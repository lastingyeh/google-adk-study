# AI 代理的安全性與防護

> 🔔 `更新日期：2026-01-30`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/safety/

[`ADK 支援`: `Python` | `TypeScript` | `Go` | `Java`]

隨著 AI 代理的能力不斷增長，確保其安全、可靠地運行並符合您的品牌價值觀至關重要。失控的代理可能會帶來風險，包括執行不一致或有害的操作（如數據洩露），以及生成可能影響品牌聲譽的不當內容。**風險來源包括模糊的指令、模型幻覺、惡意使用者的越獄（jailbreaks）與提示詞注入（prompt injections），以及透過工具使用進行的間接提示詞注入。**

[Google Cloud Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/overview) 提供了一種多層次的方法來降低這些風險，使您能夠構建強大*且*值得信賴的代理。它提供了多種機制來建立嚴格的邊界，確保代理僅執行您明確允許的操作：

1. **身份與授權**：透過定義代理和使用者認證，控制代理以**誰的身份**行動。
2. **篩選輸入與輸出的護欄（Guardrails）：** 精確控制您的模型和工具呼叫。

    * *工具內護欄（In-Tool Guardrails）：* 以防禦性思維設計工具，使用開發者設定的工具上下文（tool context）來強制執行策略（例如，僅允許對特定資料表進行查詢）。
    * *內置 Gemini 安全功能：* 如果使用 Gemini 模型，可受益於內容過濾器以阻擋有害輸出，並透過系統指令引導模型的行為和安全準則。
    * *回呼（Callbacks）與插件（Plugins）：* 在執行前或執行後驗證模型和工具呼叫，根據代理狀態或外部策略檢查參數。
    * *使用 Gemini 作為安全護欄：* 實施額外的安全層，使用配置了回呼的廉價且快速的模型（如 Gemini Flash Lite）來篩選輸入和輸出。

3. **沙盒化程式碼執行：** 透過沙盒化環境，防止模型生成的程式碼導致安全性問題。
4. **評估與追蹤**：使用評估工具評估代理最終輸出的質量、相關性和正確性。使用追蹤功能來獲取代理操作的可視化資訊，以分析代理達成解決方案所採取的步驟，包括其工具選擇、策略以及方法的效率。
5. **網路控制與 VPC-SC：** 將代理活動限制在安全周界（如 VPC Service Controls）內，以防止數據洩露並限制潛在的影響範圍。

## 安全與防護風險

在實施安全措施之前，請針對代理的能力、領域和部署背景進行專門的徹底風險評估。

**風險*來源*** 包括：

* 模糊的代理指令
* 來自惡意使用者的提示詞注入和越獄嘗試
* 透過工具使用進行的間接提示詞注入

**風險類別** 包括：

* **失控與目標腐敗**
    * 追求非預期或代理目標，導致有害結果（「獎勵破解」）
    * 誤解複雜或模糊的指令
* **產生有害內容，包括品牌安全**
    * 產生毒性、仇恨、偏見、性暗示、歧視或非法內容
    * 品牌安全風險，例如使用違背品牌價值觀的語言或進行離題對話
* **不安全的操作**
    * 執行損壞系統的命令
    * 進行未經授權的採購或金融交易
    * 洩露敏感個人資料 (PII)
    * 數據洩露

## 最佳實踐

### 身份與授權

從安全角度來看，*工具* 用於在外部系統執行操作的身份是一個關鍵的設計考量。同一個代理中的不同工具可以配置不同的策略，因此在討論代理配置時需要格外小心。

#### 代理身份驗證 (Agent-Auth)

**工具使用代理自身的身份（例如服務帳號）與外部系統進行交互。** 代理身份必須在外部系統的存取策略中得到明確授權，例如將代理的服務帳號新增到資料庫的 IAM 策略中以獲取讀取權限。此類策略將代理限制在僅能執行開發者預期可行的操作：透過對資源授予唯讀權限，無論模型如何決定，工具都將被禁止執行寫入操作。

這種方法易於實現，且**適用於所有使用者共享相同存取層級的代理。** 如果並非所有使用者都具有相同的存取權限，則單靠這種方法無法提供足夠的保護，必須與下方的其他技術相結合。在工具實現中，請確保建立日誌以維持操作與使用者之間的歸屬關係，因為所有代理的操作都會顯示為來自代理本身。

#### 使用者身份驗證 (User Auth)

工具使用 **「控制使用者」的身份**（例如在 Web 應用程式中與前端互動的人員）與外部系統互動。在 ADK 中，這通常使用 OAuth 實現：代理與前端互動以獲取 OAuth 令牌，然後工具在執行外部操作時使用該令牌：如果控制使用者有權自行執行該操作，外部系統將授權該操作。

使用者身份驗證的優點是代理僅執行使用者本身可以執行的操作。這大大降低了惡意使用者濫用代理以獲取額外數據存取權限的風險。然而，大多數常見的委派實現都有一組固定的委派權限（即 OAuth 範圍）。通常，這些範圍比代理實際要求的存取權限更廣，因此需要下方的技術來進一步限制代理的操作。

### 篩選輸入與輸出的護欄 (Guardrails)

#### 工具內護欄 (In-tool guardrails)

工具可以在設計時考慮到安全性：我們可以建立僅公開我們希望模型採取的動作而無其他的工具。透過限制我們提供給代理的動作範圍，我們可以確定性地消除我們永遠不希望代理採取的惡意動作類別。

工具內護欄是一種建立通用且可重複使用的工具的方法，這些工具公開了開發者可用於在每個工具實例化時設定限制的確定性控制項。

這種方法依賴於工具接收兩種類型的輸入：由模型設定的**參數（arguments）**，以及可由代理開發者確定性設定的 [**`工具上下文 (Tool Context)`**](../custom-tools/index.md#工具上下文-tool-context)。我們可以依靠確定性設定的資訊來驗證模型的行為是否符合預期。

例如，查詢工具可以設計為預期從工具上下文中讀取策略。

<details>
<summary>範例說明</summary>

> Python

```python
# 概念範例：設定用於工具上下文的策略數據
# 在實際的 ADK 應用中，這可能會在 InvocationContext.session.state 中設定
# 或在工具初始化期間傳遞，然後透過 ToolContext 檢索。

policy = {} # 假設策略是一個字典
policy['select_only'] = True
policy['tables'] = ['mytable1', 'mytable2']

# 概念性：將策略存儲在工具稍後可以透過 ToolContext 存取的地方。
# 這一行在實際操作中可能看起來有所不同。
# 例如，存儲在 session 狀態中：
invocation_context.session.state["query_tool_policy"] = policy

# 或者可能在工具初始化期間傳遞：
query_tool = QueryTool(policy=policy)
# 在本範例中，我們假設它被存儲在可存取的地方。
```

> typescript

```typescript
// 概念範例：設定用於工具上下文的策略數據
// 在實際的 ADK 應用中，這可能會在 InvocationContext.session.state 中設定
// 或在工具初始化期間傳遞，然後透過 ToolContext 檢索。

const policy: {[key: string]: any} = {}; // 假設策略是一個物件
policy['select_only'] = true;
policy['tables'] = ['mytable1', 'mytable2'];

// 概念性：將策略存儲在工具稍後可以透過 ToolContext 存取的地方。
// 這一行在實際操作中可能看起來有所不同。
// 例如，存儲在 session 狀態中：
invocationContext.session.state["query_tool_policy"] = policy;

// 或者可能在工具初始化期間傳遞：
const queryTool = new QueryTool({policy: policy});
// 在本範例中，我們假設它被存儲在可存取的地方。
```

> go

```go
// 概念範例：設定用於工具上下文的策略數據
// 在實際的 ADK 應用中，這可以使用 session 狀態服務來設定。
// `ctx` 是一個在回呼或自定義代理中可用的 `agent.Context`。

policy := map[string]interface{}{
	"select_only": true,
	"tables":      []string{"mytable1", "mytable2"},
}

// 概念性：將策略存儲在工具稍後可以透過 ToolContext 存取的地方。
// 這一行在實際操作中可能看起來有所不同。
// 例如，存儲在 session 狀態中：
if err := ctx.Session().State().Set("query_tool_policy", policy); err != nil {
    // 處理錯誤，例如記錄它。
}

// 或者可能在工具初始化期間傳遞：
// queryTool := NewQueryTool(policy)
// 在本範例中，我們假設它被存儲在可存取的地方。
```

> java

```java
// 概念範例：設定用於工具上下文的策略數據
// 在實際的 ADK 應用中，這可能會在 InvocationContext.session.state 中設定
// 或在工具初始化期間傳遞，然後透過 ToolContext 檢索。

policy = new HashMap<String, Object>(); // 假設策略是一個 Map
policy.put("select_only", true);
policy.put("tables", new ArrayList<>("mytable1", "mytable2"));

// 概念性：將策略存儲在工具稍後可以透過 ToolContext 存取的地方。
// 這一行在實際操作中可能看起來有所不同。
// 例如，存儲在 session 狀態中：
invocationContext.session().state().put("query_tool_policy", policy);

// 或者可能在工具初始化期間傳遞：
query_tool = QueryTool(policy);
// 在本範例中，我們假設它被存儲在可存取的地方。
```

</details>

在工具執行期間，[**`工具上下文 (Tool Context)`**](../custom-tools/index.md#工具上下文-tool-context) 將被傳遞給工具：

<details>
<summary>範例說明</summary>

> Python

```python
def query(query: str, tool_context: ToolContext) -> str | dict:
  # 假設從上下文中檢索「策略」，例如透過 session 狀態：
  # policy = tool_context.invocation_context.session.state.get('query_tool_policy', {})

  # --- 佔位符策略執行 (Placeholder Policy Enforcement) ---
  policy = tool_context.invocation_context.session.state.get('query_tool_policy', {}) # 範例檢索
  actual_tables = explainQuery(query) # 假設的函數呼叫

  if not set(actual_tables).issubset(set(policy.get('tables', []))):
    # 為模型回傳錯誤訊息
    allowed = ", ".join(policy.get('tables', ['(None defined)']))
    return f"錯誤：查詢目標為未經授權的資料表。允許的資料表：{allowed}"

  if policy.get('select_only', False):
       if not query.strip().upper().startswith("SELECT"):
           return "錯誤：策略限制查詢僅限於 SELECT 語句。"
  # --- 策略執行結束 ---

  print(f"正在執行經過驗證的查詢（假設）：{query}")
  return {"status": "success", "results": [...]} # 範例成功回傳
```

> typescript

```typescript
function query(query: string, toolContext: ToolContext): string | object {
    // 假設從上下文中檢索「策略」，例如透過 session 狀態：
    const policy = toolContext.state.get('query_tool_policy', {}) as {[key: string]: any};

    // --- 佔位符策略執行 (Placeholder Policy Enforcement) ---
    const actual_tables = explainQuery(query); // 假設的函數呼叫

    const policyTables = new Set(policy['tables'] || []);
    const isSubset = actual_tables.every(table => policyTables.has(table));

    if (!isSubset) {
        // 為模型回傳錯誤訊息
        const allowed = (policy['tables'] || ['(None defined)']).join(', ');
        return `錯誤：查詢目標為未經授權的資料表。允許的資料表：{allowed}`;
    }

    if (policy['select_only']) {
        if (!query.trim().toUpperCase().startsWith("SELECT")) {
            return "錯誤：策略限制查詢僅限於 SELECT 語句。";
        }
    }
    // --- 策略執行結束 ---

    console.log(`正在執行經過驗證的查詢（假設）：{query}`);
    return { "status": "success", "results": [] }; // 範例成功回傳
}
```

> go

```go
import (
	"fmt"
	"strings"

	"google.golang.org/adk/tool"
)

func query(query string, toolContext *tool.Context) (any, error) {
	// 假設從上下文中檢索「策略」，例如透過 session 狀態：
	policyAny, err := toolContext.State().Get("query_tool_policy")
	if err != nil {
		return nil, fmt.Errorf("無法檢索策略：%w", err)
	}    	policy, _ := policyAny.(map[string]interface{})
	actualTables := explainQuery(query) // 假設的函數呼叫

	// --- 佔位符策略執行 (Placeholder Policy Enforcement) ---
	if tables, ok := policy["tables"].([]string); ok {
		if !isSubset(actualTables, tables) {
			// 回傳錯誤以信號失敗
			allowed := strings.Join(tables, ", ")
			if allowed == "" {
				allowed = "(None defined)"
			}
			return nil, fmt.Errorf("查詢目標為未經授權的資料表。允許的資料表：%s", allowed)
		}
	}

	if selectOnly, _ := policy["select_only"].(bool); selectOnly {
		if !strings.HasPrefix(strings.ToUpper(strings.TrimSpace(query)), "SELECT") {
			return nil, fmt.Errorf("策略限制查詢僅限於 SELECT 語句")
		}
	}
	// --- 策略執行結束 ---

	fmt.Printf("正在執行經過驗證的查詢（假設）：%s\n", query)
	return map[string]interface{}{"status": "success", "results": []string{"..."}}, nil
}

// 輔助函數，檢查 a 是否為 b 的子集
func isSubset(a, b []string) bool {
	set := make(map[string]bool)
	for _, item := range b {
		set[item] = true
	}
	for _, item := range a {
		if _, found := set[item]; !found {
			return false
		}
	}
	return true
}
```

> java

```java

import com.google.adk.tools.ToolContext;
import java.util.*;

class ToolContextQuery {

  public Object query(String query, ToolContext toolContext) {

    // 假設從上下文中檢索「策略」，例如透過 session 狀態：
    Map<String, Object> queryToolPolicy =
        toolContext.invocationContext.session().state().getOrDefault("query_tool_policy", null);
    List<String> actualTables = explainQuery(query);

    // --- 佔位符策略執行 (Placeholder Policy Enforcement) ---
    if (!queryToolPolicy.get("tables").containsAll(actualTables)) {
      List<String> allowedPolicyTables =
          (List<String>) queryToolPolicy.getOrDefault("tables", new ArrayList<String>());

      String allowedTablesString =
          allowedPolicyTables.isEmpty() ? "(None defined)" : String.join(", ", allowedPolicyTables);

      return String.format(
          "錯誤：查詢目標為未經授權的資料表。允許的資料表：%s", allowedTablesString);
    }

    if (!queryToolPolicy.get("select_only")) {
      if (!query.trim().toUpperCase().startswith("SELECT")) {
        return "錯誤：策略限制查詢僅限於 SELECT 語句。";
      }
    }
    // --- 策略執行結束 ---

    System.out.printf("正在執行經過驗證的查詢（假設） %s:", query);
    Map<String, Object> successResult = new HashMap<>();
    successResult.put("status", "success");
    successResult.put("results", Arrays.asList("result_item1", "result_item2"));
    return successResult;
  }
}
```

</details>

#### 內置 Gemini 安全功能

Gemini 模型帶有內置的安全機制，可用於提高內容和品牌安全。

* **內容安全過濾器**： [內容過濾器](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/configure-safety-attributes) 可以幫助阻擋有害內容的輸出。它們獨立於 Gemini 模型運行，作為針對試圖越獄模型的威脅者的多層防禦的一部分。Vertex AI 上的 Gemini 模型使用兩種類型的內容過濾器：
* **不可配置的安全過濾器** 會自動阻擋包含违禁內容的輸出，例如兒童性虐待內容 (CSAM) 和個人識別資訊 (PII)。
* **可配置的內容過濾器** 允許您根據概率和嚴重程度分數，在四個傷害類別（仇恨言論、騷擾、性暗示和危險內容）中定義阻擋閾值。這些過濾器預設為關閉，但您可以根據需要進行配置。
* **安全系統指令**： Vertex AI 中 Gemini 模型的 [系統指令](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/safety-system-instructions) 為模型提供了關於如何表現以及生成何種類型內容的直接引導。透過提供特定的指令，您可以主動引導模型遠離生成不良內容，以滿足您組織的獨特需求。您可以編寫系統指令來定義內容安全準則（例如禁止和敏感主題以及免責聲明語言），以及品牌安全準則，以確保模型的輸出符合您品牌的聲音、語調、價值觀和目標受眾。

雖然這些措施在內容安全方面非常強大，但您還需要額外的檢查來減少代理失控、不安全操作和品牌安全風險。

#### 安全護欄的回呼與插件

回呼提供了一種簡單且特定於代理的方法，用於為工具和模型的 I/O 新增預先驗證，而插件則為跨多個代理實施通用安全策略提供了可重複使用的解決方案。

當無法修改工具以新增護欄時，可以使用 [**`工具前置回呼 (Before Tool Callback)`**](../callbacks/types-of-callbacks.md#before-tool-callback) 函數來新增呼叫的預先驗證。回呼可以存取代理的狀態、要求的工具和參數。這種方法非常通用，甚至可以用於建立可重複使用工具策略的通用程式庫。然而，如果實施護欄所需的資訊在參數中不直接可見，它可能不適用於所有工具。

<details>
<summary>範例說明</summary>

> Python

```python
# 假設的回呼函數
def validate_tool_params(
    callback_context: CallbackContext, # 正確的上下文類型
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext
    ) -> Optional[Dict]: # before_tool_callback 的正確回傳類型

  print(f"工具觸發回呼：{tool.name}，參數：{args}")

  # 範例驗證：檢查狀態中要求的使用者 ID 是否與參數匹配
  expected_user_id = callback_context.state.get("session_user_id")
  actual_user_id_in_args = args.get("user_id_param") # 假設工具接受 'user_id_param'

  if actual_user_id_in_args != expected_user_id:
      print("驗證失敗：使用者 ID 不匹配！")
      # 回傳一個字典以防止工具執行並提供回饋
      return {"error": f"工具呼叫被封鎖：使用者 ID 不匹配。"}

  # 如果驗證通過，回傳 None 以允許工具呼叫繼續進行
  print("回呼驗證通過。")
  return None

# 假設的代理設置
root_agent = LlmAgent( # 使用特定的代理類型
    model='gemini-2.0-flash',
    name='root_agent',
    instruction="...",
    before_tool_callback=validate_tool_params, # 分配回呼
    tools = [
      # ... 工具函數或工具實例列表 ...
      # 例如 query_tool_instance
    ]
)
```

> typescript

```typescript
// 假設的回呼函數
function validateToolParams(
    {tool, args, context}: {
        tool: BaseTool,
        args: {[key: string]: any},
        context: ToolContext
    }
): {[key: string]: any} | undefined {
    console.log(`工具觸發回呼：${tool.name}，參數：${JSON.stringify(args)}`);

    // 範例驗證：檢查狀態中要求的使用者 ID 是否與參數匹配
    const expectedUserId = context.state.get("session_user_id");
    const actualUserIdInArgs = args["user_id_param"]; // 假設工具接受 'user_id_param'

    if (actualUserIdInArgs !== expectedUserId) {
        console.log("驗證失敗：使用者 ID 不匹配！");
        // 回傳一個字典以防止工具執行並提供回饋
        return {"error": `工具呼叫被封鎖：使用者 ID 不匹配。`};
    }

    // 如果驗證通過，回傳 undefined 以允許工具呼叫繼續進行
    console.log("回呼驗證通過。");
    return undefined;
}

// 假設的代理設置
const rootAgent = new LlmAgent({
    model: 'gemini-2.5-flash',
    name: 'root_agent',
    instruction: "...",
    beforeToolCallback: validateToolParams, // 分配回呼
    tools: [
      // ... 工具函數或工具實例列表 ...
      // 例如 queryToolInstance
    ]
});
```

> go

```go
import (
	"fmt"
	"reflect"

	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/tool"
)

// 假設的回呼函數
func validateToolParams(
	ctx tool.Context,
	t tool.Tool,
	args map[string]any,
) (map[string]any, error) {
	fmt.Printf("工具觸發回呼：%s，參數：%v\n", t.Name(), args)

	// 範例驗證：檢查狀態中要求的使用者 ID 是否與參數匹配
	expectedUserIDVal, err := ctx.State().Get("session_user_id")
	if err != nil {
		// 這是一個意外的失敗，回傳錯誤。
		return nil, fmt.Errorf("內部錯誤：狀態中找不到 session_user_id：%w", err)
	}
	expectedUserID, ok := expectedUserIDVal.(string)
	if !ok {
		return nil, fmt.Errorf("內部錯誤：狀態中的 session_user_id 不是字串，得到 %T", expectedUserIDVal)
	}

	actualUserIDInArgs, exists := args["user_id_param"]
	if !exists {
		// 處理 user_id_param 不在參數中的情況
		fmt.Println("驗證失敗：參數中缺失 user_id_param！")
		return map[string]any{"error": "工具呼叫被封鎖：參數中缺失 user_id_param。"}, nil
	}

	actualUserID, ok := actualUserIDInArgs.(string)
	if !ok {
		// 處理 user_id_param 不是字串的情況
		fmt.Println("驗證失敗：user_id_param 不是字串！")
		return map[string]any{"error": "工具呼叫被封鎖：user_id_param 不是字串。"}, nil
	}

	if actualUserID != expectedUserID {
		fmt.Println("驗證失敗：使用者 ID 不匹配！")
		// 回傳一個 map 以防止工具執行並向模型提供回饋。
		// 這不是 Go 錯誤，而是給代理的訊息。
		return map[string]any{"error": "工具呼叫被封鎖：使用者 ID 不匹配。"}, nil
	}
	// 如果驗證通過，回傳 nil, nil 以允許工具呼叫繼續進行
	fmt.Println("回呼驗證通過。")
	return nil, nil
}

// 假設的代理設置
// rootAgent, err := llmagent.New(llmagent.Config{
// 	Model: "gemini-2.0-flash",
// 	Name: "root_agent",
// 	Instruction: "...",
// 	BeforeToolCallbacks: []llmagent.BeforeToolCallback{validateToolParams},
// 	Tools: []tool.Tool{queryToolInstance},
// })
```

> java

```java
// 假設的回呼函數
public Optional<Map<String, Object>> validateToolParams(
  CallbackContext callbackContext,
  Tool baseTool,
  Map<String, Object> input,
  ToolContext toolContext) {

System.out.printf("工具觸發回呼：%s，參數：%s", baseTool.name(), input);

// 範例驗證：檢查狀態中要求的使用者 ID 是否與輸入參數匹配
Object expectedUserId = callbackContext.state().get("session_user_id");
Object actualUserIdInput = input.get("user_id_param"); // 假設工具接受 'user_id_param'

if (!actualUserIdInput.equals(expectedUserId)) {
  System.out.println("驗證失敗：使用者 ID 不匹配！");
  // 回傳以防止工具執行並提供回饋
  return Optional.of(Map.of("error", "工具呼叫被封鎖：使用者 ID 不匹配。"));
}

// 如果驗證通過，回傳以允許工具呼叫繼續進行
System.out.println("回呼驗證通過。");
return Optional.empty();
}

// 假設的代理設置
public void runAgent() {
LlmAgent agent =
    LlmAgent.builder()
        .model("gemini-2.0-flash")
        .name("AgentWithBeforeToolCallback")
        .instruction("...")
        .beforeToolCallback(this::validateToolParams) // 分配回呼
        .tools(anyToolToUse) // 定義要使用的工具
        .build();
}
```

</details>

然而，在為代理應用程式新增安全護欄時，建議使用插件來實施不特定於單個代理的策略。插件被設計為自包含且模組化的，允許您針對特定的安全策略建立單獨的插件，並在執行器（runner）級別全局應用。這意味著一個安全插件可以配置一次，並應用於使用該執行器的每個代理，從而確保整個應用程式中一致的安全護欄，而無需重複程式碼。

一些範例包括：

* **Gemini 作為裁判 (Judge) 插件**：此插件使用 Gemini Flash Lite 來評估使用者輸入、工具輸入和輸出，以及代理的響應是否合適，並進行提示詞注入和越獄檢測。該插件將 Gemini 配置為安全過濾器，以降低內容安全、品牌安全和代理失控的風險。插件配置為將使用者輸入、工具輸入和輸出以及模型輸出傳遞給 Gemini Flash Lite，由其決定對代理的輸入是安全還是不安全。如果 Gemini 決定輸入不安全，代理將回傳預定的響應：「抱歉，我無法提供協助。我還能幫您處理其他事情嗎？」。

* **Model Armor 插件**：一種查詢 Model Armor API 的插件，用於在代理執行的指定點檢查潛在的內容安全違規。與 _Gemini 作為裁判_ 插件類似，如果 Model Armor 發現有害內容匹配，它將向使用者回傳預定的響應。

* **PII 個人識別資訊遮蔽 (Redaction) 插件**：一種專門為 [工具前置回呼](../plugins/index.md#工具回呼) 設計的插件，專門用於在工具處理或發送到外部服務之前，對個人識別資訊進行脫敏處理。

### 沙盒化程式碼執行

程式碼執行是一個具有額外安全意義的特殊工具：必須使用沙盒化來防止模型生成的程式碼損害本地環境，從而可能導致安全性問題。

Google 和 ADK 提供了多種安全執行程式碼的選項。[Vertex Gemini Enterprise API 程式碼執行功能](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/code-execution-api) 使代理能夠透過啟用 tool_execution 工具來利用伺服器端的沙盒化程式碼執行。對於執行數據分析的程式碼，您可以使用 ADK 中的 [程式碼執行器 (Code Executor)](../tools-for-agents/gemini-api/code-execution.md) 工具來呼叫 [Vertex 程式碼解釋器 (Code Interpreter) 擴充功能](https://cloud.google.com/vertex-ai/generative-ai/docs/extensions/code-interpreter)。

如果這些選項都不能滿足您的需求，您可以使用 ADK 提供的構建塊構建自己的程式碼執行器。我們建議建立密閉的執行環境：不允許網路連接和 API 呼叫，以避免不受控制的數據洩露；並在執行過程中完全清理數據，以避免跨使用者的洩露疑慮。

### 評估

請參閱[評估代理](../evaluation/index.md)。

### VPC-SC 周界與網路控制

如果您在 VPC-SC 周界內執行代理，這將保證所有 API 呼叫僅操作周界內的資源，從而降低數據洩露的機率。

然而，身份和周界僅提供對代理操作的粗略控制。工具使用護欄減輕了此類限制，並賦予代理開發者更多權力來精確控制允許執行哪些操作。

### 其他安全風險

#### 務必在 UI 中轉義模型產生的內容

當代理輸出在瀏覽器中視覺化時，必須小心：如果 UI 中沒有正確轉義 HTML 或 JS 內容，模型回傳的文字可能會被執行，從而導致數據洩露。例如，間接提示詞注入可以欺騙模型包含一個 img 標籤，從而欺騙瀏覽器將會話內容發送到第三方網站；或構造 URL，如果點擊這些 URL，則會將數據發送到外部網站。對此類內容進行適當的轉義必須確保模型生成的文字不會被瀏覽器解釋為程式碼。
