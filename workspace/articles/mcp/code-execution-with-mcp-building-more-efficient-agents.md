# 使用 MCP 執行程式碼：建構更有效率的 AI Agents (Code execution with MCP: Building more efficient agents)

## **本文翻譯參考來源**：[連結](https://www.anthropic.com/engineering/code-execution-with-mcp)

**發布日期：** 2025年11月4日

直接的工具呼叫會為每個定義與結果消耗上下文。Agents (代理) 透過編寫程式碼來呼叫工具，可以更好地擴展。本文將介紹如何透過 MCP 實現這一點。

[模型上下文協議 (The Model Context Protocol, MCP)](https://modelcontextprotocol.io/) 是一個將 AI agents 連接到外部系統的開放標準。傳統上，將 agents 連接到工具和資料需要為每個配對進行客製化整合，這會造成碎片化和重複性工作，使得擴展真正互聯的系統變得困難。MCP 提供了一個通用協議——開發者在他們的 agent 中實作一次 MCP，就能解鎖整個整合生態系統。

自 2024 年 11 月推出 MCP 以來，其採用速度非常快：社群已經建立了數千個 [MCP 伺服器](https://github.com/modelcontextprotocol/servers)，所有主要程式語言都提供了 [SDK](https://modelcontextprotocol.io/docs/sdk)，且業界已將 MCP 作為連接 agents 與工具和資料的實際標準。

今日，開發者們經常建構能夠存取數十個 MCP 伺服器上數百甚至數千個工具的 agents。然而，隨著連接工具數量的增長，預先載入所有工具定義並將中間結果傳遞到上下文視窗中，會減慢 agents 的速度並增加成本。

在這篇文章中，我們將探討程式碼執行如何使 agents 更有效地與 MCP 伺服器互動，處理更多工具的同時使用更少的 token。

## 過多的工具 Token 消耗降低了 Agents 的效率 (Excessive token consumption from tools makes agents less efficient)

隨著 MCP 使用規模的擴大，有兩種常見模式會增加 agent 的成本和延遲：

- 工具定義使上下文視窗超載；
- 中間工具結果消耗額外的 token。

### 1. 工具定義使上下文視窗超載 (1. Tool definitions overload the context window)

大多數 MCP 客戶端會直接將所有工具定義預先載入到上下文中，並使用直接的工具呼叫語法將它們暴露給模型。這些工具定義可能如下所示：

```
gdrive.getDocument
 說明：從 Google Drive 檢索文件
 參數：
            documentId (必要, 字串): 要檢索的文件的 ID
            fields (可選, 字串): 要返回的特定欄位
 返回：包含標題、內文、元數據、權限等的文件物件。
```

```
salesforce.updateRecord
說明：更新 Salesforce 中的一筆紀錄
參數：
           objectType (必要, 字串): Salesforce 物件的類型 (潛在客戶、聯絡人、帳戶等)
           recordId (必要, 字串): 要更新的紀錄的 ID
           data (必要, 物件): 要更新的欄位及其新值
 返回：包含確認訊息的已更新紀錄物件。
```

工具描述佔用了更多的上下文視窗空間，增加了回應時間和成本。在 agents 連接到數千個工具的情況下，它們在讀取請求之前需要處理數十萬個 token。

### 2. 中間工具結果消耗額外的 Token (2. Intermediate tool results consume additional tokens)

大多數 MCP 客戶端允許模型直接呼叫 MCP 工具。例如，您可能會要求您的 agent：「從 Google Drive 下載我的會議記錄，並將其附加到 Salesforce 的潛在客戶中。」

模型將進行如下呼叫：

```
// 工具呼叫：gdrive.getDocument(documentId: "abc123")
TOOL CALL: gdrive.getDocument(documentId: "abc123")
    // → 返回 "討論了第四季度的目標...\n[完整的會議記錄文本]"
    → returns "Discussed Q4 goals...\n[full transcript text]"
       // (載入到模型上下文中)
       (loaded into model context)

// 工具呼叫：salesforce.updateRecord(...)
TOOL CALL: salesforce.updateRecord(
        objectType: "SalesMeeting",
        recordId: "00Q5f000001abcXYZ",
          data: { "Notes": "討論了第四季度的目標...\n[完整的會議記錄文本再次寫入]" }
    )
    // (模型需要再次將整個會議記錄寫入上下文)
    (model needs to write entire transcript into context again)
```

每個中間結果都必須通過模型。在這個例子中，完整的通話記錄流經了兩次。對於一個 2 小時的銷售會議，這可能意味著要額外處理 50,000 個 token。更大的文件甚至可能超出上下文視窗的限制，從而中斷工作流程。

對於大型文件或複雜的資料結構，模型在工具呼叫之間複製資料時更容易出錯。

![MCP 客戶端與 MCP 伺服器和 LLM 的協作方式示意圖](https://www.anthropic.com/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2F9ecf165020005c09a22a9472cee6309555485619-1920x1080.png&w=3840&q=75)

MCP 客戶端將工具定義載入到模型的上下文視窗中，並協調一個訊息循環，其中每個工具呼叫和結果都在操作之間通過模型。

## 使用 MCP 進行程式碼執行可提高上下文效率 (Code execution with MCP improves context efficiency)

隨著程式碼執行環境在 agents 中變得越來越普遍，一個解決方案是將 MCP 伺服器呈現為程式碼 API，而不是直接的工具呼叫。這樣，agent 就可以編寫程式碼與 MCP 伺服器互動。這種方法解決了兩個挑戰：agents 可以只載入它們需要的工具，並在將結果傳回模型之前在執行環境中處理資料。

實現這一點有多種方法。一種方法是從已連接的 MCP 伺服器生成所有可用工具的檔案樹。以下是使用 TypeScript 的一個實作範例：

```
servers
├── google-drive
│   ├── getDocument.ts
│   ├── ... (其他工具)
│   └── index.ts
├── salesforce
│   ├── updateRecord.ts
│   ├── ... (其他工具)
│   └── index.ts
└── ... (其他伺服器)
```

然後每個工具對應一個檔案，內容類似於：

```typescript
// 檔案路徑: ./servers/google-drive/getDocument.ts

// 導入 MCP 工具呼叫函式
import { callMCPTool } from "../../../client.js";

// 定義 getDocument 函式的輸入介面
interface GetDocumentInput {
  documentId: string; // 文件 ID
}

// 定義 getDocument 函式的回應介面
interface GetDocumentResponse {
  content: string; // 文件內容
}

/* 從 Google Drive 讀取文件 */
export async function getDocument(input: GetDocumentInput): Promise<GetDocumentResponse> {
  // 呼叫 MCP 工具 'google_drive__get_document' 並返回結果
  return callMCPTool<GetDocumentResponse>('google_drive__get_document', input);
}
```

我們上面提到的 Google Drive 到 Salesforce 的範例就變成了以下程式碼：

```typescript
// 從 Google Docs 讀取會議記錄並新增到 Salesforce 潛在客戶

// 導入 Google Drive 和 Salesforce 的工具模組
import * as gdrive from './servers/google-drive';
import * as salesforce from './servers/salesforce';

// 從 Google Drive 取得文件內容
const transcript = (await gdrive.getDocument({ documentId: 'abc123' })).content;
// 將文件內容更新到 Salesforce 的紀錄中
await salesforce.updateRecord({
  objectType: 'SalesMeeting',
  recordId: '00Q5f000001abcXYZ',
  data: { Notes: transcript }
});
```

agent 透過探索檔案系統來發現工具：列出 `./servers/` 目錄以找到可用的伺服器（如 `google-drive` 和 `salesforce`），然後讀取它需要的特定工具檔案（如 `getDocument.ts` 和 `updateRecord.ts`）以了解每個工具的介面。這讓 agent 只需載入當前任務所需的定義。這將 token 使用量從 150,000 個 token 減少到 2,000 個 token——節省了 98.7% 的時間和成本。

Cloudflare [發表了類似的發現](https://blog.cloudflare.com/code-mode/)，將使用 MCP 的程式碼執行稱為「程式碼模式 (Code Mode)」。核心見解是相同的：LLM 擅長編寫程式碼，開發者應該利用這一優勢來建構能更有效地與 MCP 伺服器互動的 agents。

## 使用 MCP 進行程式碼執行的好處 (Benefits of code execution with MCP)

使用 MCP 進行程式碼執行使 agents 能夠透過按需載入工具、在資料到達模型前進行過濾以及在單一步驟中執行複雜邏輯，從而更有效地利用上下文。這種方法在安全性和狀態管理方面也有好處。

### 漸進式揭露 (Progressive disclosure)

模型非常擅長導覽檔案系統。將工具呈現為檔案系統上的程式碼，允許模型按需讀取工具定義，而不是一次性全部讀取。

或者，可以在伺服器上新增一個 `search_tools` 工具來尋找相關的定義。例如，在使用上面假設的 Salesforce 伺服器時，agent 搜尋 "salesforce" 並只載入當前任務所需的工具。在 `search_tools` 工具中包含一個細節級別參數，允許 agent 選擇所需的細節級別（例如僅名稱、名稱和描述，或包含結構的完整定義），這也有助於 agent 節省上下文並有效地找到工具。

### 上下文高效的工具結果 (Context efficient tool results)

在處理大型資料集時，agents 可以在返回結果之前在程式碼中進行過濾和轉換。考慮獲取一個包含 10,000 列的試算表：

```typescript
// 不使用程式碼執行 - 所有列都流經上下文
TOOL CALL: gdrive.getSheet(sheetId: 'abc123')
        → 在上下文中返回 10,000 列以手動過濾

// 使用程式碼執行 - 在執行環境中過濾
// 取得所有列的資料
const allRows = await gdrive.getSheet({ sheetId: 'abc123' });
// 過濾出狀態為 'pending' 的訂單
const pendingOrders = allRows.filter(row =>
  row["Status"] === 'pending'
);
// 顯示找到的待處理訂單數量
console.log(`找到 ${pendingOrders.length} 個待處理訂單`);
// 僅顯示前 5 筆待處理訂單以供審查
console.log(pendingOrders.slice(0, 5));
```

agent 只看到五列而不是 10,000 列。類似的模式適用於匯總、跨多個資料來源的連接或提取特定欄位——所有這些都不會使上下文視窗膨脹。

#### 更強大且上下文高效的控制流程 (More powerful and context-efficient control flow)

迴圈、條件判斷和錯誤處理可以使用熟悉的程式碼模式來完成，而不是鏈接單個工具呼叫。例如，如果您需要在 Slack 中收到部署通知，agent 可以編寫：

```typescript
// 初始化 found 變數為 false
let found = false;
// 當尚未找到目標訊息時，持續執行迴圈
while (!found) {
  // 從 Slack 頻道獲取歷史訊息
  const messages = await slack.getChannelHistory({ channel: 'C123456' });
  // 檢查是否有訊息包含 'deployment complete'
  found = messages.some(m => m.text.includes('deployment complete'));
  // 如果未找到，則等待 5 秒後再試
  if (!found) await new Promise(r => setTimeout(r, 5000));
}
// 找到目標訊息後，輸出通知
console.log('已收到部署通知');
```

這種方法比透過 agent 迴圈交替進行 MCP 工具呼叫和睡眠命令更有效率。

此外，能夠寫出一個被執行的條件樹也可以節省「首個 token 時間」的延遲：agent 不必等待模型評估 if 語句，而是讓程式碼執行環境來完成。

### 隱私保護操作 (Privacy-preserving operations)

當 agents 使用 MCP 進行程式碼執行時，中間結果預設保留在執行環境中。這樣，agent 只看到您明確記錄或返回的內容，這意味著您不希望與模型共享的資料可以在您的工作流程中流動，而無需進入模型的上下文。

對於更敏感的工作負載，agent 工具鏈可以自動對敏感資料進行權杖化 (tokenize)。例如，假設您需要將客戶聯絡資訊從試算表導入到 Salesforce。agent 編寫：

```typescript
// 從 Google Drive 取得試算表資料
const sheet = await gdrive.getSheet({ sheetId: 'abc123' });
// 遍歷試算表中的每一列
for (const row of sheet.rows) {
  // 將每一列的資料更新到 Salesforce 的潛在客戶紀錄中
  await salesforce.updateRecord({
    objectType: 'Lead',
    recordId: row.salesforceId,
    data: {
      Email: row.email,
      Phone: row.phone,
      Name: row.name
    }
  });
}
// 顯示已更新的潛在客戶數量
console.log(`已更新 ${sheet.rows.length} 個潛在客戶`);
```

MCP 客戶端在資料到達模型之前攔截並對個人可識別資訊 (PII) 進行權杖化：

```json
// 如果 agent 記錄了 sheet.rows，它會看到：
[
  { "salesforceId": "00Q...", "email": "[EMAIL_1]", "phone": "[PHONE_1]", "name": "[NAME_1]" },
  { "salesforceId": "00Q...", "email": "[EMAIL_2]", "phone": "[PHONE_2]", "name": "[NAME_2]" },
  ...
]
```

然後，當資料在另一個 MCP 工具呼叫中共享時，它會透過 MCP 客戶端中的查詢來取消權杖化。真實的電子郵件地址、電話號碼和姓名從 Google Sheets 流向 Salesforce，但從未通過模型。這可以防止 agent 意外記錄或處理敏感資料。您還可以使用它來定義確定性的安全規則，選擇資料可以流向何處。

### 狀態持久化與技能 (State persistence and skills)

具有檔案系統存取權限的程式碼執行允許 agents 在操作之間保持狀態。Agents 可以將中間結果寫入檔案，使它們能夠恢復工作並追蹤進度：

```typescript
// 從 Salesforce 查詢潛在客戶資料
const leads = await salesforce.query({
  query: 'SELECT Id, Email FROM Lead LIMIT 1000'
});
// 將查詢結果轉換為 CSV 格式
const csvData = leads.map(l => `${l.Id},${l.Email}`).join('\n');
// 將 CSV 資料寫入檔案
await fs.writeFile('./workspace/leads.csv', csvData);

// 稍後的執行從中斷處繼續
// 從檔案中讀取先前儲存的資料
const saved = await fs.readFile('./workspace/leads.csv', 'utf-8');
```

Agents 還可以將自己的程式碼持久化為可重用的函式。一旦 agent 為某個任務開發了可行的程式碼，它可以將該實作保存以備將來使用：

```typescript
// 在 ./skills/save-sheet-as-csv.ts 中

// 導入 Google Drive 工具模組
import * as gdrive from './servers/google-drive';
// 導出一個將試算表另存為 CSV 的函式
export async function saveSheetAsCsv(sheetId: string) {
  // 取得試算表資料
  const data = await gdrive.getSheet({ sheetId });
  // 將資料轉換為 CSV 格式
  const csv = data.map(row => row.join(',')).join('\n');
  // 將 CSV 資料寫入檔案
  await fs.writeFile(`./workspace/sheet-${sheetId}.csv`, csv);
  // 返回檔案路徑
  return `./workspace/sheet-${sheetId}.csv`;
}

// 稍後，在任何 agent 執行中：
// 導入先前儲存的技能
import { saveSheetAsCsv } from './skills/save-sheet-as-csv';
// 呼叫技能函式並取得 CSV 檔案路徑
const csvPath = await saveSheetAsCsv('abc123');
```

這與 [技能 (Skills)](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) 的概念密切相關，即為模型提供可重用的指令、腳本和資源的資料夾，以提高在專門任務上的表現。在這些已保存的函式中新增一個 `SKILL.md` 檔案，可以創建一個模型可以參考和使用的結構化技能。隨著時間的推移，這使您的 agent 能夠建立一個更高級別能力的工具箱，發展出使其工作最有效所需的支持架構。

請注意，程式碼執行本身也帶來了複雜性。執行由 agent 生成的程式碼需要一個安全的執行環境，並配備適當的[沙盒 (sandboxing)](https://www.anthropic.com/engineering/claude-code-sandboxing)、資源限制和監控。這些基礎設施要求增加了直接工具呼叫所能避免的營運開銷和安全考量。程式碼執行的好處——減少 token 成本、降低延遲和改進工具組合——應與這些實作成本進行權衡。

## 總結 (Summary)

MCP 為 agents 連接到眾多工具和系統提供了一個基礎協議。然而，一旦連接的伺服器過多，工具定義和結果可能會消耗過多的 token，從而降低 agent 的效率。

儘管這裡的許多問題感覺很新穎——上下文管理、工具組合、狀態持久化——但它們在軟體工程中都有已知的解決方案。程式碼執行將這些已建立的模式應用於 agents，讓它們使用熟悉的程式設計結構更有效地與 MCP 伺服器互動。如果您實作了這種方法，我們鼓勵您與 [MCP 社群](https://modelcontextprotocol.io/community/communication)分享您的發現。

### 致謝 (Acknowledgments)

本文由 Adam Jones 和 Conor Kelly 撰寫。感謝 Jeremy Fox、Jerome Swannack、Stuart Ritchie、Molly Vorwerck、Matt Samuels 和 Maggie Vo 對本文草稿的回饋。

## 相關資源 (Related Resources)

- 模型上下文協議 (The Model Context Protocol, MCP)：[https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
- MCP 伺服器 (MCP servers)：[https://github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)
- 軟體開發套件 (SDKs)：[https://modelcontextprotocol.io/docs/sdk](https://modelcontextprotocol.io/docs/sdk)
- Cloudflare 的發現 (Cloudflare published similar findings)：[https://blog.cloudflare.com/code-mode/](https://blog.cloudflare.com/code-mode/)
- 技能 (Skills)：[https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- 沙盒 (sandboxing)：[https://www.anthropic.com/engineering/claude-code-sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)
- MCP 社群 (MCP community)：[https://modelcontextprotocol.io/community/communication](https://modelcontextprotocol.io/community/communication)
- theailanguage 頻道：[I Just Made Google ADK 10x Faster with Anthropic’s New Programmatic Tool Calling (MCP Demo)](https://www.youtube.com/watch?v=ewGEbeWzWI0&list=TLGGxAYCU_zHTtQxNDEyMjAyNQ)
- theailanguage Github 範例：[version_7_programmatic_tool_execution](https://github.com/theailanguage/adk_samples/tree/main/version_7_programmatic_tool_execution)