# 為什麼要評估代理 (Agents)
🔔 `更新日期：2026-01-19`

[`ADK 支援`: `Python`]


在傳統軟體開發中，單元測試和整合測試讓我們確信程式碼能按預期運作，並在變更過程中保持穩定。這些測試提供明確的「通過/失敗」訊號，指引後續開發。然而，大型語言模型 (LLM) 代理引入了一定程度的變異性，使得傳統的測試方法顯得不足。

由於模型具有機率性質，確定性的「通過/失敗」斷言通常不適用於評估代理性能。相反，我們需要對最終輸出和代理的「軌跡 (trajectory)」——即達成解決方案所採取的步驟序列——進行定性評估。這包括評估代理決策的品質、其推理過程以及最終結果。

這套設定看起來可能需要很多額外工作，但自動化評估的投資很快就會得到回報。如果您打算超越原型階段，這是一項強烈建議的最佳實踐。

![intro_components.png](https://google.github.io/adk-docs/assets/evaluate_agent.png)

## 為代理評估做準備

在自動化代理評估之前，請定義明確的目標和成功標準：

* **定義成功：** 對於您的代理來說，什麼樣的結果才算成功？
* **識別關鍵任務：** 您的代理必須完成哪些核心任務？
* **選擇相關指標：** 您將追蹤哪些指標來衡量性能？

這些考量將引導評估場景的建立，並實現對真實部署中代理行為的有效監控。

## 評估什麼？

為了彌合概念驗證與生產級 AI 代理之間的差距，一個穩健且自動化的評估框架至關重要。與評估生成式模型（主要關注最終輸出）不同，代理評估需要更深入地了解決策過程。代理評估可以分解為兩個部分：

1. **評估軌跡與工具使用：** 分析代理為達成解決方案而採取的步驟，包括其工具選擇、策略以及方法的效率。
2. **評估最終回應：** 評估代理最終輸出的品質、相關性和正確性。

軌跡(trajectory)僅僅是代理在回覆使用者之前採取的步驟列表。我們可以將其與我們預期代理應採取的步驟列表進行比較。

### 評估軌跡與工具使用

在回覆使用者之前，代理通常會執行一系列動作，我們稱之為「軌跡(trajectory)」。它可能會將使用者輸入與工作階段歷史記錄進行比較以消除術語歧義，或者查閱政策文件、搜尋知識庫或調用 API 來儲存工單。我們稱之為動作的「軌跡」。評估代理的性能需要將其實際軌跡與預期（或理想）的軌跡進行比較。這種比較可以揭示代理過程中的錯誤和低效率。預期軌跡代表「地面實況 (ground truth)」——即我們預期代理應採取的步驟列表。

例如：

```python
# 軌跡評估將會比較
# 預期步驟 = ["確定意圖", "使用工具", "審查結果", "報告生成"]
expected_steps = ["determine_intent", "use_tool", "review_results", "report_generation"]
# 實際步驟 = ["確定意圖", "使用工具", "審查結果", "報告生成"]
actual_steps = ["determine_intent", "use_tool", "review_results", "report_generation"]
```

ADK 提供基於地面實況和基於量表 (rubric) 的工具使用評估指標。要為您的代理特定需求和目標選擇適當的指標，請參閱我們的[建議](#關於標準的建議)。

## 評估如何與 ADK 協作

ADK 提供兩種方法，根據預定義的資料集和評估標準來評估代理性能。雖然概念上相似，但它們在可處理的資料量上有所不同，這通常決定了每種方法的適用場景。

### 第一種方法：使用測試檔案，參考更多說明 [EvalSet 架構說明](#評估集-evalset-架構說明)

此方法涉及建立個別的測試檔案，每個檔案代表單一、簡單的代理-模型互動（一個工作階段）。這在主動開發代理期間最為有效，可作為一種單元測試。這些測試旨在快速執行，並應專注於簡單的工作階段複雜度。每個測試檔案包含一個工作階段，其中可能包含多個輪次 (turns)。一個輪次代表使用者與代理之間的單次互動。每個輪次包括：

-   `使用者內容 (User Content)`：使用者發出的查詢。
-   `預期的中間工具使用軌跡 (Expected Intermediate Tool Use Trajectory)`：我們期望代理為正確回應使用者查詢而進行的工具調用。
-   `預期的中間代理回應 (Expected Intermediate Agent Responses)`：這些是代理（或子代理）在產生最終答案的過程中產生的自然語言回應。這些中間回應通常是多代理系統的產物，其中您的根代理依賴子代理來達成目標。這些中間回應對終端使用者來說可能感興趣，也可能不感興趣，但對於系統的開發者/擁有者而言，它們至關重要，因為它們讓您確信代理經過了正確的路徑來產生最終回應。
-   `最終回應 (Final Response)`：來自代理的預期最終回應。

您可以為檔案命名為任何名稱，例如 `evaluation.test.json`。框架僅檢查 `.test.json` 字尾，檔案名稱的前半部分不受限制。測試檔案由正式的 Pydantic 資料模型支援。兩個關鍵的架構檔案是 [Eval Set](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py) 和 [Eval Case](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py)。
以下是一個包含幾個範例的測試檔案：

*(注意：包含註解是為了說明目的，應將其移除以使 JSON 有效。)*

```json
// 請注意，為了使此文件易於閱讀，已移除某些欄位。
{
  "eval_set_id": "home_automation_agent_light_on_off_set",
  "name": "",
  "description": "這是一個用於單元測試代理 `x` 行為的評估集",
  "eval_cases": [
    {
      "eval_id": "eval_case_id",
      "conversation": [
        {
          "invocation_id": "b7982664-0ab6-47cc-ab13-326656afdf75", // 調用的唯一識別碼。
          "user_content": { // 使用者在此次調用中提供的內容。即查詢。
            "parts": [
              {
                "text": "關掉臥室的 device_2。"
              }
            ],
            "role": "user"
          },
          "final_response": { // 來自代理的最終回應，作為基準參考。
            "parts": [
              {
                "text": "我已將 device_2 狀態設置為關閉。"
              }
            ],
            "role": "model"
          },
          "intermediate_data": {
            "tool_uses": [ // 按時間順序排列的工具使用軌跡。
              {
                "args": {
                  "location": "Bedroom",
                  "device_id": "device_2",
                  "status": "OFF"
                },
                "name": "set_device_info"
              }
            ],
            "intermediate_responses": [] // 任何中間子代理回應。
          }
        }
      ],
      "session_input": { // 初始工作階段輸入。
        "app_name": "home_automation_agent",
        "user_id": "test_user",
        "state": {}
      }
    }
  ]
}
```

#### 如何遷移不支援 Pydantic 架構的測試檔案？

注意：如果您的測試檔案不符合 [EvalSet](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py) 架構檔案，那麼本節與您相關。

請使用 `AgentEvaluator.migrate_eval_data_to_new_schema` 將您現有的 `*.test.json` 檔案遷移到支援 Pydantic 的架構。

該公用程式採用您目前的測試資料檔案和一個選用的初始工作階段檔案，並產生一個包含新格式序列化資料的單一輸出 JSON 檔案。鑑於新架構更具凝聚力，舊的測試資料檔案和初始工作階段檔案都可以忽略（或移除）。

### 第二種方法：使用評估集 (Evalset) 檔案

評估集方法利用一個稱為「評估集」的專用資料集來評估代理-模型互動。與測試檔案類似，評估集包含互動範例。然而，一個評估集可以包含多個、可能很長的工作階段，使其成為模擬複雜、多輪對話的理想選擇。由於能夠表示複雜的工作階段，評估集非常適合整合測試。由於其規模龐大，這些測試通常比單元測試執行頻率更低。

一個評估集檔案包含多個「評估 (evals)」，每個代表一個獨立的工作階段。每個評估由一個或多個「輪次」組成，包括使用者查詢、預期工具使用、預期的中間代理回應和參考回應。這些欄位與測試檔案方法中的含義相同。或者，一個評估可以定義一個*對話場景*，用於[動態模擬](./user-sim.md)使用者與代理的互動。每個評估都由一個唯一名稱識別。此外，每個評估都包含一個相關聯的初始工作階段狀態。

手動建立評估集可能很複雜，因此提供了 UI 工具來幫助擷取相關的工作階段，並輕鬆將其轉換為評估集中的評估。請在下方進一步了解如何使用 Web UI 進行評估。以下是一個包含兩個工作階段的評估集範例。評估集檔案由正式的 Pydantic 資料模型支援。兩個關鍵的架構檔案是 [Eval Set](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py) 和 [Eval Case](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py)。

> [!WARNING]
    此評估集評估方法需要使用付費服務：[Vertex Gen AI Evaluation Service API](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/evaluation)。

*(注意：包含註解是為了說明目的，應將其移除以使 JSON 有效。)*

```json
// 請注意，為了使此文件易於閱讀，已移除某些欄位。
{
  "eval_set_id": "eval_set_example_with_multiple_sessions",
  "name": "具有多個工作階段的評估集",
  "description": "此評估集是一個範例，顯示一個評估集可以擁有多個工作階段。",
  "eval_cases": [
    {
      "eval_id": "session_01",
      "conversation": [
        {
          "invocation_id": "e-0067f6c4-ac27-4f24-81d7-3ab994c28768",
          "user_content": {
            "parts": [
              {
                "text": "你能做什麼？"
              }
            ],
            "role": "user"
          },
          "final_response": {
            "parts": [
              {
                "text": "我可以擲不同大小的骰子並檢查數字是否為質數。"
              }
            ],
            "role": null
          },
          "intermediate_data": {
            "tool_uses": [],
            "intermediate_responses": []
          }
        }
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user",
        "state": {}
      }
    },
    {
      "eval_id": "session_02",
      "conversation": [
        {
          "invocation_id": "e-92d34c6d-0a1b-452a-ba90-33af2838647a",
          "user_content": {
            "parts": [
              {
                "text": "擲一個 19 面的骰子"
              }
            ],
            "role": "user"
          },
          "final_response": {
            "parts": [
              {
                "text": "我擲出了 17。"
              }
            ],
            "role": null
          },
          "intermediate_data": {
            "tool_uses": [],
            "intermediate_responses": []
          }
        },
        {
          "invocation_id": "e-bf8549a1-2a61-4ecc-a4ee-4efbbf25a8ea",
          "user_content": {
            "parts": [
              {
                "text": "擲兩次 10 面骰子，然後檢查 9 是否為質數"
              }
            ],
            "role": "user"
          },
          "final_response": {
            "parts": [
              {
                "text": "我從骰子中得到了 4 和 7，而 9 不是質數。\n"
              }
            ],
            "role": null
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "id": "adk-1a3f5a01-1782-4530-949f-07cf53fc6f05",
                "args": {
                  "sides": 10
                },
                "name": "roll_die"
              },
              {
                "id": "adk-52fc3269-caaf-41c3-833d-511e454c7058",
                "args": {
                  "sides": 10
                },
                "name": "roll_die"
              },
              {
                "id": "adk-5274768e-9ec5-4915-b6cf-f5d7f0387056",
                "args": {
                  "nums": [
                    9
                  ]
                },
                "name": "check_prime"
              }
            ],
            "intermediate_responses": [
              [
                "data_processing_agent",
                [
                  {
                    "text": "我已經擲了兩次 10 面骰子。第一次是 5，第二次是 3。\n"
                  }
                ]
              ]
            ]
          }
        }
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user",
        "state": {}
      }
    }
  ]
}
```

#### 如何遷移不支援 Pydantic 架構的評估集檔案？

注意：如果您的評估集檔案不符合 [EvalSet](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py) 架構檔案，那麼本節與您相關。

根據評估集資料的維護者，有兩條路徑：

1.  **由 ADK UI 維護的評估集資料：** 如果您使用 ADK UI 來維護評估集資料，則*不需要採取任何行動*。

2.  **手動開發和維護並在 ADK 評估 CLI 中使用的評估集資料：** 遷移工具正在開發中，在那之前，ADK 評估 CLI 命令將繼續支援舊格式的資料。

### 評估標準

ADK 提供多種內建標準來評估代理性能，範圍從工具軌跡比對到基於 LLM 的回應品質評估。有關可用標準的詳細列表以及何時使用它們的指引，請參閱[評估標準](./criteria.md)。

以下是所有可用標準的摘要：

*   **tool_trajectory_avg_score**：工具調用軌跡的精確比對。
*   **response_match_score**：與參考回應的 ROUGE-1 相似度。
*   **final_response_match_v2**：由 LLM 評判的與參考回應的語義比對。
*   **rubric_based_final_response_quality_v1**：由 LLM 根據自定義量表評判的最終回應品質。
*   **rubric_based_tool_use_quality_v1**：由 LLM 根據自定義量表評判的工具使用品質。
*   **hallucinations_v1**：由 LLM 評判的代理回應相對於上下文的實證性 (groundedness)。
*   **safety_v1**：代理回應的安全性/無害性。

如果未提供評估標準，則使用以下預設配置：

* `tool_trajectory_avg_score`：預設為 1.0，要求工具使用軌跡 100% 匹配。
* `response_match_score`：預設為 0.8，允許代理的自然語言回應有很小的誤差範圍。

以下是一個指定自定義評估標準的 `test_config.json` 檔案範例：

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.8
  }
}
```

#### 關於標準的建議

根據您的評估目標選擇標準：

*   **在 CI/CD 管道或回歸測試中啟用測試：** 使用 `tool_trajectory_avg_score` 和 `response_match_score`。這些標準快速、可預測，且適用於頻繁的自動檢查。
*   **評估可信的參考回應：** 使用 `final_response_match_v2` 來評估語義等價性。這種基於 LLM 的檢查比精確比對更靈活，且能更好地捕捉代理的回應是否與參考回應表達相同的意思。
*   **在沒有參考回應的情況下評估回應品質：** 使用 `rubric_based_final_response_quality_v1`。當您沒有可信的參考時，這很有用，但您可以定義好回應的屬性（例如：「回應簡潔」、「回應語氣有幫助」）。
*   **評估工具使用的正確性：** 使用 `rubric_based_tool_use_quality_v1`。這讓您可以藉由檢查來驗證代理的推理過程，例如檢查是否調用了特定工具，或者工具是否按正確順序調用（例如：「工具 A 必須在工具 B 之前調用」）。
*   **檢查回應是否植基於上下文：** 使用 `hallucinations_v1` 來檢測代理是否提出了與其可用資訊（例如：工具輸出）不符或矛盾的主張。
*   **檢查有害內容：** 使用 `safety_v1` 確保代理回應安全且不違反安全政策。

此外，需要預期代理工具使用和/或回應資訊的標準，不支援與[使用者模擬](./user-sim.md)結合使用。
目前，僅 `hallucinations_v1` 和 `safety_v1` 標準支援此類評估。

### 使用者模擬

在評估對話代理時，使用一組固定的使用者提示並不總是切實可行，因為對話可能會以意想不到的方式進行。
例如，如果代理需要使用者提供兩個數值來執行任務，它可能會一次要求一個數值，或同時要求兩個數值。
為了釋決這個問題，ADK 允許您在特定的*對話場景*中測試代理的行為，其中的使用者提示是由 AI 模型動態生成的。
有關如何設定使用者模擬評估的詳細資訊，請參閱[使用者模擬](./user-sim.md)。

## 如何使用 ADK 執行評估

身為開發者，您可以透過以下方式使用 ADK 評估您的代理：

1. **基於 Web 的 UI (`adk web`)：** 透過網頁界面互動式地評估代理。
2. **程式化方式 (`pytest`)**：使用 `pytest` 和測試檔案將評估整合到您的測試管道中。
3. **命令列界面 (`adk eval`)：** 直接從命令列在現有的評估集檔案上執行評估。

### 1. `adk web` - 透過 Web UI 執行評估

Web UI 提供了一種互動式方式來評估代理、產生評估資料集並詳細檢查代理行為。

#### 步驟 1：建立並儲存測試案例

1. 執行以下命令啟動 Web 伺服器：`adk web <代理檔案夾路徑>`
2. 在網頁界面中，選擇一個代理並與其互動以建立一個工作階段。
3. 導航到界面右側的 **Eval** 分頁。
4. 建立新的評估集或選擇現有的評估集。
5. 點擊 **"Add current session"** 將對話儲存為新的評估案例。

#### 步驟 2：檢視並編輯您的測試案例

案例儲存後，您可以點擊列表中的 ID 來檢查它。要進行更改，請點擊 **Edit current eval case** 圖示（鉛筆）。此互動式檢視讓您可以：

* **修改**代理的文本回應以完善測試場景。
* 從對話中**刪除**個別代理訊息。
* 如果不再需要，**刪除**整個評估案例。

![adk-eval-case.gif](https://google.github.io/adk-docs/assets/adk-eval-case.gif)

#### 步驟 3：使用自定義指標執行評估

1. 從您的評估集中選擇一個或多個測試案例。
2. 點擊 **Run Evaluation**。將出現 **EVALUATION METRIC** 對話框。
3. 在對話框中，使用滑桿配置以下項目的閾值：
    * **Tool trajectory avg score (工具軌跡平均分數)**
    * **Response match score (回應比對分數)**
4. 點擊 **Start** 以使用您的自定義標準執行評估。評估歷史將記錄每次執行所使用的指標。

![adk-eval-config.gif](https://google.github.io/adk-docs/assets/adk-eval-config.gif)

#### 步驟 4：分析結果

執行完成後，您可以分析結果：

* **分析執行失敗原因**：點擊任何 **Pass (通過)** 或 **Fail (失敗)** 結果。對於失敗，您可以將滑鼠懸停在 `Fail` 標籤上，查看**實際 vs. 預期輸出**的並排比較以及導致失敗的分數。

### 使用追蹤檢視 (Trace View) 進行除錯

ADK Web UI 包含一個強大的 **Trace** 分頁，用於對代理行為進行除錯。此功能適用於任何代理工作階段，而不僅僅是在評估期間。

**Trace** 分頁提供了一種詳細且互動的方式來檢查代理的執行流程。追蹤會自動按使用者訊息分組，方便追蹤事件鏈。

每一行追蹤都是互動式的：

* **懸停**在追蹤行上會突顯聊天視窗中對應的訊息。
* **點擊**追蹤行會開啟一個包含四個分頁的詳細檢查面板：
    * **Event (事件)**：原始事件資料。
    * **Request (請求)**：發送給模型的請求。
    * **Response (回應)**：從模型接收到的回應。
    * **Graph (圖表)**：工具調用和代理邏輯流的視覺化表示。

![adk-trace1.gif](https://google.github.io/adk-docs/assets/adk-trace1.gif)

![adk-trace2.gif](https://google.github.io/adk-docs/assets/adk-trace2.gif)

追蹤檢視中的藍色行表示該互動產生了事件。點擊這些藍色行將開啟底部的事件細節面板，提供對代理執行流程的更深入見解。

### 2. `pytest` - 以程式方式執行測試

您還可以使用 **`pytest`** 作為整合測試的一部分來執行測試檔案。

#### 範例命令

```shell
pytest tests/integration/
```

#### 範例測試程式碼

以下是一個執行單一測試檔案的 `pytest` 測試案例範例：

```py
from google.adk.evaluation.agent_evaluator import AgentEvaluator
import pytest

@pytest.mark.asyncio
async def test_with_single_test_file():
    """透過工作階段檔案測試代理的基本能力。"""
    await AgentEvaluator.evaluate(
        # 代理模組名稱
        agent_module="home_automation_agent",
        # 評估資料集檔案路徑或目錄
        eval_dataset_file_path_or_dir="tests/integration/fixture/home_automation_agent/simple_test.test.json",
    )
```

這種方法讓您可以將代理評估整合到 CI/CD 管道或更大的測試套件中。如果您想為測試指定初始工作階段狀態，可以將工作階段詳細資訊儲存在檔案中，並將其傳遞給 `AgentEvaluator.evaluate` 方法。

### 3\. `adk eval` - 透過 CLI 執行評估

您還可以透過命令列界面 (CLI) 執行評估集檔案的評估。這與 UI 上的評估相同，但有助於自動化，即您可以將此命令作為常規建置產生和驗證過程的一部分。

以下是命令：

```shell
adk eval \
    <AGENT_MODULE_FILE_PATH> \
    <EVAL_SET_FILE_PATH> \
    [--config_file_path=<PATH_TO_TEST_JSON_CONFIG_FILE>] \
    [--print_detailed_results]
```

例如：

```shell
adk eval \
    samples_for_testing/hello_world \
    samples_for_testing/hello_world/hello_world_eval_set_001.evalset.json
```

以下是各個命令列引數的詳細說明：

* `AGENT_MODULE_FILE_PATH`：指向包含名為 "agent" 模組之 `__init__.py` 檔案的路徑。"agent" 模組包含一個 `root_agent`。
* `EVAL_SET_FILE_PATH`：評估檔案的路徑。您可以指定一個或多個評估集檔案路徑。對於每個檔案，預設將執行所有評估。如果您只想執行評估集中的特定評估，請先建立一個以逗號分隔的評估名稱列表，然後將其作為字尾添加到評估集檔案名稱中，並以冒號 `:` 分隔。
* 例如：`sample_eval_set_file.json:eval_1,eval_2,eval_3`
  `這將僅執行 sample_eval_set_file.json 中的 eval_1、eval_2 和 eval_3`
* `CONFIG_FILE_PATH`：配置檔案的路徑。
* `PRINT_DETAILED_RESULTS`：在主控台上列印詳細結果。

## 更多說明

### 評估集 (EvalSet) 架構說明

| 欄位名稱                                   | 說明                                 | 用法                                       | 備註                                   |
| :----------------------------------------- | :----------------------------------- | :----------------------------------------- | :------------------------------------- |
| `eval_set_id`                              | 評估集的唯一識別碼。                 | 用於區分不同的評估集。                     | 應保持唯一性。                         |
| `name`                                     | 評估集的名稱。                       | 提供一個人類可讀的名稱。                   |                                        |
| `description`                              | 評估集的詳細描述。                   | 說明此評估集的目的和內容。                 |                                        |
| `eval_cases`                               | 包含多個評估案例的陣列。             | 每個評估案例代表一個獨立的工作階段。       |                                        |
| `eval_cases.eval_id`                       | 評估案例的唯一識別碼。               | 用於識別單一的評估工作階段。               |                                        |
| `eval_cases.conversation`                  | 包含對話輪次的陣列。                 | 記錄使用者與代理之間的多輪互動。           |                                        |
| `conversation.invocation_id`               | 該輪對話的唯一識別碼。               | 用於追蹤單次呼叫。                         |                                        |
| `conversation.user_content`                | 使用者輸入的內容。                   | 包含使用者在此輪對話中提供的查詢。         |                                        |
| `conversation.final_response`              | 代理的最終預期回應。                 | 作為評估代理回應正確性的基準參考。         |                                        |
| `conversation.intermediate_data`           | 代理在產生最終回應前的中間步驟資料。 | 包含工具使用軌跡和中間代理回應。           | 對於除錯和評估代理的決策過程至關重要。 |
| `intermediate_data.tool_uses`              | 按時間順序排列的工具使用軌跡。       | 記錄代理呼叫了哪些工具、參數為何。         |                                        |
| `intermediate_data.intermediate_responses` | 中間子代理的回應。                   | 在多代理系統中，記錄子代理產生的回應。     |                                        |
| `eval_cases.session_input`                 | 初始工作階段輸入。                   | 定義代理開始此工作階段時的初始狀態。       |                                        |
| `session_input.app_name`                   | 代理應用程式的名稱。                 |                                            |                                        |
| `session_input.user_id`                    | 使用者的識別碼。                     |                                            |                                        |
| `session_input.state`                      | 工作階段的狀態物件。                 | 可以包含任何需要在工作階段之間保持的資料。 |                                        |