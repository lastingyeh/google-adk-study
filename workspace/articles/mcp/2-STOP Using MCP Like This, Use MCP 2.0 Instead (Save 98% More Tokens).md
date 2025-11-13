## 一、為什麼要用「Code Execution + MCP」？

### 1. 問題一：工具定義把 Context 撐爆

當一個 Agent 連到很多 MCP servers（Google Drive、Salesforce、各種內部系統…），傳統做法是：

* 把所有 tools 的定義（名稱、參數 schema、說明）全部塞到模型的 context 裡
* 模型用「直接呼叫工具」的方式運作（例如：`gdrive.getDocument`、`salesforce.updateRecord`）

當工具多到幾百、幾千個時：

* 工具定義本身就可能佔掉數十萬 tokens
* 還沒開始處理你的需求，context 已經被吃光一半了 ([Anthropic][1])

### 2. 問題二：中間結果也一直佔 tokens

典型流程像這樣：

1. 呼叫 `gdrive.getDocument(documentId: "abc123")` → 把完整逐字稿塞回模型 context
2. 模型再呼叫 `salesforce.updateRecord(...)`，需要把整份逐字稿再貼一次進參數裡

所以：

* 同一份 2 小時會議逐字稿，可能在 context 裡出現兩次以上
* 大文件甚至會超過 context 限制，流程直接壞掉 ([Anthropic][1])

---

## 二、解法總圖：把 MCP 工具包裝成「程式碼 API」

核心 Idea（這篇文章的重點）：

> 不是讓模型「直接呼叫 MCP 工具」，而是讓模型「寫程式」去呼叫 MCP API。([Anthropic][1])

做法是：

1. 每個 MCP tool 對應成一個程式檔：像 `servers/google-drive/getDocument.ts`
2. Agent 在「程式碼執行環境」裡，自行：

   * 探索檔案系統（列出有哪些工具）
   * `import` 它需要的工具
   * 寫 code 串接多個工具、處理資料
3. 只有「必要的摘要結果」才回傳給模型，減少 token 消耗

文章中的範例，把所有 server 長得像這樣的檔案樹：([Anthropic][1])

```text
servers
├── google-drive
│   ├── getDocument.ts
│   └── index.ts
├── salesforce
│   ├── updateRecord.ts
│   └── index.ts
└── ...
```

---

## 三、實作步驟：手把手設計一個「MCP + Code Execution」架構

以下用 TypeScript 當示範（文章也是用 TS）。

### 步驟 0：準備一個 `callMCPTool` 共用方法

這隻 function 是你自己的 MCP client，用來對 MCP server 發送請求：

```ts
// client.ts
export async function callMCPTool<TResponse>(
  toolName: string,
  input: unknown
): Promise<TResponse> {
  // 這裡會依照 MCP 規範，透過 WebSocket / stdio / HTTP 等方式，
  // 把 toolName + input 發送給對應的 MCP server，並解析回應。

  // 假裝的實作：
  const res = await fetch("http://localhost:4000/mcp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tool: toolName, input }),
  });

  if (!res.ok) throw new Error(`MCP tool error: ${res.statusText}`);

  return (await res.json()) as TResponse;
}
```

> 真實實作要依 MCP 規格與你使用的 SDK 來寫，這裡只示意「由你掌控 MCP 呼叫，而不是讓模型直接呼叫」。

---

### 步驟 1：把每個 MCP 工具包裝成 TypeScript 函式

以 Google Drive 的 `getDocument` 為例（對應 MCP 上某個工具 `google_drive__get_document`）：([Anthropic][1])

```ts
// ./servers/google-drive/getDocument.ts
import { callMCPTool } from "../../client";

export interface GetDocumentInput {
  documentId: string;
}

export interface GetDocumentResponse {
  content: string;
}

export async function getDocument(
  input: GetDocumentInput
): Promise<GetDocumentResponse> {
  return callMCPTool<GetDocumentResponse>("google_drive__get_document", input);
}
```

Salesforce 也一樣，包裝成程式碼 API，例如 `updateRecord.ts`。

---

### 步驟 2：讓 Agent 在程式碼中組合這些工具

文章中的「下載 Google Drive 逐字稿 → 寫入 Salesforce」範例，用程式碼就很直覺：([Anthropic][1])

```ts
// ./workflows/gdrive-to-salesforce.ts
import * as gdrive from "../servers/google-drive/getDocument";
import * as salesforce from "../servers/salesforce/updateRecord";

async function syncMeetingNotes() {
  const transcript = (await gdrive.getDocument({ documentId: "abc123" }))
    .content;

  await salesforce.updateRecord({
    objectType: "SalesMeeting",
    recordId: "00Q5f000001abcXYZ",
    data: { Notes: transcript },
  });
}

syncMeetingNotes().catch(console.error);
```

**關鍵差異：**

* 模型只需要閱讀這段 TypeScript 程式碼（幾百～幾千 tokens）
* 真正的 2 小時逐字稿內容，只在 code execution 環境裡流動，不必全部塞到模型 context 裡頭

文章估算：這種改寫可以把 token 消耗從 150,000 減到 2,000 左右，省掉 98% 以上的成本 ([Anthropic][1])

---

### 步驟 3：讓模型自己「探索」工具（Progressive Disclosure）

以前：

* 一次把所有 tools 的定義丟給模型：名稱 + 描述 + 參數 schema…

現在：

* 模型透過「檔案系統」慢慢探索：

  1. 先 `ls ./servers` 看有哪些 server（`google-drive`, `salesforce`, …）
  2. 再打開 `./servers/salesforce/updateRecord.ts` 之類的檔案，理解介面
  3. 只 import 它需要的那幾支工具 ([Anthropic][1])

進階版作法（文章裡有提）：
在 MCP server 端實作一個 `search_tools` 工具，支援：

* 關鍵字搜尋（例如 `"salesforce"`）
* `detail_level` 參數：只要名稱、名稱+描述、還是連 schema 整個回傳 ([Anthropic][1])

這樣模型只拿到**它當下需要**的部分定義，context 更省。

---

## 四、進階技巧：怎麼讓 Agent 又省 Context 又好用？

### 1. 在程式裡先整理資料，再回傳給模型

假設你要處理 10,000 筆訂單的試算表：([Anthropic][1])

傳統作法：

* `TOOL CALL: gdrive.getSheet` → 把 10,000 列全部塞進 context
* 模型在自然語言回合裡「憑印象」過濾 pending 訂單

Code execution 作法：

```ts
const allRows = await gdrive.getSheet({ sheetId: "abc123" });

const pendingOrders = allRows.filter((row) => row["Status"] === "pending");

console.log(`Found ${pendingOrders.length} pending orders`);
console.log(pendingOrders.slice(0, 5)); // 只顯示前 5 筆給模型看
```

好處：

* 10,000 筆資料只在程式裡處理
* 模型只看到你 `console.log` 的摘要與前幾筆樣本
  → context 使用量從「整張表」縮成「幾行 log + 統計數字」

---

### 2. 用程式語言的控制流程：loop / if / error handling

文章舉例：
你想讓 Agent 等待 Slack channel 出現「deployment complete」訊息，如果沒看到就每 5 秒再查一次：([Anthropic][1])

```ts
let found = false;

while (!found) {
  const messages = await slack.getChannelHistory({ channel: "C123456" });

  found = messages.some((m) => m.text.includes("deployment complete"));

  if (!found) {
    await new Promise((r) => setTimeout(r, 5000));
  }
}

console.log("Deployment notification received");
```

用 code execution 的好處：

* 這個 `while` loop 完全在執行環境裡跑，不需要模型一直輪詢「我要不要再查一次？」。
* 減少模型 round-trip，也縮短「time to first token」。

---

### 3. 隱私與敏感資料保護（PII Tokenization）

這邊是我覺得對金融業很實用的一段。

文章的做法是：

* 讓 MCP client 在**程式碼層**攔截資料，主動把 PII（Email, Phone, Name…）tokenize 成 `[EMAIL_1]` 之類的 placeholder ([Anthropic][1])

流程示意：

```ts
const sheet = await gdrive.getSheet({ sheetId: "abc123" });

for (const row of sheet.rows) {
  await salesforce.updateRecord({
    objectType: "Lead",
    recordId: row.salesforceId,
    data: {
      Email: row.email,
      Phone: row.phone,
      Name: row.name,
    },
  });
}
console.log(`Updated ${sheet.rows.length} leads`);
```

在 Agent 看到的世界裡，如果你 `console.log(sheet.rows)`，會被 MCP client 改寫成像：([Anthropic][1])

```ts
[
  { salesforceId: "00Q...", email: "[EMAIL_1]", phone: "[PHONE_1]", name: "[NAME_1]" },
  { salesforceId: "00Q...", email: "[EMAIL_2]", phone: "[PHONE_2]", name: "[NAME_2]" },
  ...
]
```

但在真正傳給 Salesforce 的時候，MCP client 會再把 placeholders 還原成真實的值。

**重點：**

* 真實的 Email / Phone / Name **從來沒進模型 context**，只在你的安全執行環境與下游系統間流動。
* 你可以在 MCP client 實作「資料流向白名單」，明確定義：哪些欄位可以流向哪個系統。

---

### 4. 狀態持久化與「技能（Skills）」的概念

因為程式碼可以操作檔案系統，你可以讓 Agent：

1. 把中間結果寫到檔案
2. 下次執行再讀回來，繼續之前沒做完的工作 ([Anthropic][1])

例如，把 Salesforce leads 匯出成 CSV：

```ts
const leads = await salesforce.query({
  query: "SELECT Id, Email FROM Lead LIMIT 1000",
});

const csvData = leads.map((l) => `${l.Id},${l.Email}`).join("\n");

await fs.writeFile("./workspace/leads.csv", csvData);

// 之後其他任務可以再讀這個檔
const saved = await fs.readFile("./workspace/leads.csv", "utf-8");
```

進一步，你可以把常用邏輯抽成「技能」：

```ts
// ./skills/save-sheet-as-csv.ts
import * as gdrive from "../servers/google-drive";
import fs from "fs/promises";

export async function saveSheetAsCsv(sheetId: string) {
  const data = await gdrive.getSheet({ sheetId });
  const csv = data.map((row) => row.join(",")).join("\n");
  await fs.writeFile(`./workspace/sheet-${sheetId}.csv`, csv);
  return `./workspace/sheet-${sheetId}.csv`;
}
```

之後任何任務都可以：

```ts
import { saveSheetAsCsv } from "./skills/save-sheet-as-csv";

const csvPath = await saveSheetAsCsv("abc123");
```

文章把這個概念和「Skills」連在一起：

* 每個 skill 是一個資料夾 + `SKILL.md` 說明
* Model 可以學會重複使用這些技能，變成越來越強的 agent ([Anthropic][1])

---

## 五、什麼時候適合用「Code Execution + MCP」？

**適合情境：**

* 你的 Agent 已經連接「很多」 MCP servers（內外部系統、SaaS、DB…）
* 任務會處理大量資料（報表、log、交易資料、客戶清單…）
* 對隱私與資料流向有高要求（金融、醫療、公部門）
* 需要複雜控制流程：輪詢、重試、錯誤處理、多步驟 pipeline

**需要考慮的成本：** ([Anthropic][1])

* 必須建立一個**安全的程式碼執行環境**：

  * sandbox（容器 / VM）
  * resource limit（CPU / Memory / 執行時間）
  * 監控與審計（避免惡意程式碼）
* 相較「直接讓模型呼叫工具」，基礎設施與維運複雜一些

---

## 六、延伸教學大綱建議

### Lesson 1：MCP 與工具爆炸問題

* MCP 是什麼？為什麼大家開始標準化工具介面？
* Demo：用圖解說明「工具定義塞滿 context」「中間結果來回 copy」的痛點
* 小練習：估算現在系統上工具定義的 token 數量

### Lesson 2：把 MCP 工具包裝成程式碼 API

* 建立 `callMCPTool` 函式
* 手動包裝 1–2 個工具成 TS 函式
* Demo：用 code 執行環境跑一個「從 A 系統讀 → 寫到 B 系統」的範例

### Lesson 3：Progressive Disclosure & Tool Discovery

* 檔案樹設計：`servers/<server-name>/<tool>.ts`
* 讓 Agent 用 `ls / cat` 探索工具定義
* 設計 `search_tools` MCP 工具：支援關鍵字 + detail 等級

### Lesson 4：Context-efficient 資料處理

* 用 code 做 filter / aggregation / join，最後只 log 摘要
* 案例：10,000 筆交易資料 → 只回報 top 10 risk cases 與統計數字

### Lesson 5：隱私與資料流向控制

* 在 MCP client 實作 PII tokenization & de-tokenization
* 畫出資料流向圖：哪些欄位可以流向哪個 server
* 金融業／內控／稽核觀點切入：如何解釋這個架構

### Lesson 6：State & Skills

* 讓 Agent 把中間結果存成檔案
* 把常用流程抽成 `skills/` 資料夾
* 幫每個 skill 寫 `SKILL.md`，讓模型更好理解如何使用
