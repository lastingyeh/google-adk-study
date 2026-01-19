# 評估標準 (Evaluation Criteria)
🔔 `更新日期：2026-01-19`

[`ADK 支援`: `Python`]

本頁面概述了 ADK 提供的評估標準，用於衡量代理 (agent) 的效能，包括工具使用軌跡、回應品質和安全性。

| 準則 (Criterion)                         | 描述                                                | 基於參考 (Reference-Based) | 需要量表 (Requires Rubrics) | LLM 作為裁判 (LLM-as-a-Judge) | 支援 [使用者模擬 (User Simulation)](./user-sim.md) |
| :--------------------------------------- | :-------------------------------------------------- | :------------------------- | :-------------------------- | :---------------------------- | :------------------------------------------------- |
| `tool_trajectory_avg_score`              | 工具呼叫軌跡的精確匹配                              | 是                         | 否                          | 否                            | 否                                                 |
| `response_match_score`                   | 與參考回應的 ROUGE-1 相似度                         | 是                         | 否                          | 否                            | 否                                                 |
| `final_response_match_v2`                | LLM 判定與參考回應的語義匹配                        | 是                         | 否                          | 是                            | 否                                                 |
| `rubric_based_final_response_quality_v1` | LLM 根據自定義量表判定的最終回應品質                | 否                         | 是                          | 是                            | 是                                                 |
| `rubric_based_tool_use_quality_v1`       | LLM 根據自定義量表判定的工具使用品質                | 否                         | 是                          | 是                            | 是                                                 |
| `hallucinations_v1`                      | LLM 判定代理回應相對於上下文的基礎性 (groundedness) | 否                         | 否                          | 是                            | 是                                                 |
| `safety_v1`                              | 代理回應的安全/無害性                               | 否                         | 否                          | 是                            | 是                                                 |
| `per_turn_user_simulator_quality_v1`     | LLM 判定的使用者模擬器品質                          | 否                         | 否                          | 是                            | 是                                                 |

## tool_trajectory_avg_score

此準則將代理呼叫的工具序列與預期呼叫列表進行比較，並根據以下匹配類型之一計算平均分數：`EXACT` (精確)、`IN_ORDER` (按順序) 或 `ANY_ORDER` (任一順序)。

#### 何時使用此準則？

此準則適用於代理的正確性取決於工具呼叫的情況。根據對工具呼叫遵循程度的嚴格要求，您可以從三種匹配類型中選擇一種：`EXACT`、`IN_ORDER` 和 `ANY_ORDER`。

此指標對於以下方面特別有價值：

*   **回歸測試 (Regression testing)：** 確保代理更新不會無意中改變既有測試案例的工具呼叫行為。
*   **流程驗證 (Workflow validation)：** 驗證代理是否正確遵循需要以特定順序進行特定 API 呼叫的預定義流程。
*   **高精度任務 (High-precision tasks)：** 評估工具參數或呼叫順序的微小偏差可能導致顯著不同或不正確結果的任務。

當您需要強制執行特定的工具執行路徑，並將任何偏差（無論是工具名稱、參數還是順序）視為失敗時，請使用 `EXACT` 匹配。

當您想要確保某些關鍵工具呼叫按特定順序發生，但允許在兩者之間發生其他工具呼叫時，請使用 `IN_ORDER` 匹配。此選項有助於確保某些關鍵動作或工具呼叫按一定順序發生，同時也為其他工具呼叫的發生留出了一些空間。

當您想要確保發生某些關鍵工具呼叫，但不在乎它們的順序，並允許在兩者之間發生其他工具呼叫時，請使用 `ANY_ORDER` 匹配。此準則對於涉及相同概念的多個工具呼叫的情況很有幫助，例如您的代理發出了 5 個搜尋查詢。您並不真正關心搜尋查詢發出的順序，只要它們發生即可。

#### 詳細資訊

對於每次被評估的呼叫，此準則都會使用三種匹配類型之一，將代理產生的工具呼叫列表與預期的工具呼叫列表進行比較。如果工具呼叫根據選定的匹配類型相匹配，則該次呼叫將獲得 1.0 分，否則分數為 0.0。最終值是評估案例中所有呼叫的這些分數的平均值。

可以使用以下匹配類型之一進行比較：

*   **`EXACT`**: 要求實際和預期的工具呼叫之間完美匹配，沒有額外或缺失的工具呼叫。
*   **`IN_ORDER`**: 要求預期列表中的所有工具呼叫都出現在實際列表中且順序相同，但允許中間出現其他工具呼叫。
*   **`ANY_ORDER`**: 要求預期列表中的所有工具呼叫都以任何順序出現在實際列表中，並允許中間出現其他工具呼叫。

#### 如何使用此準則？

預設情況下，`tool_trajectory_avg_score` 使用 `EXACT` 匹配類型。您可以在 `EvalConfig` 的 `criteria` 字典下為 `EXACT` 匹配類型指定閾值 (threshold)。該值應為 0.0 到 1.0 之間的浮點數，代表評估案例通過所需的最低可接受分數。如果您希望所有呼叫中的工具軌跡都精確匹配，則應將閾值設置為 1.0。

`EXACT` 匹配的 `EvalConfig` 範例項目：

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0 // 設置 tool_trajectory_avg_score 的閾值為 1.0
  }
}
```

或者您可以明確指定 `match_type`：

```json
{
  "criteria": {
    "tool_trajectory_avg_score": {
      "threshold": 1.0, // 設置最低通過閾值
      "match_type": "EXACT" // 指定匹配類型為 EXACT (精確匹配)
    }
  }
}
```

如果您想使用 `IN_ORDER` 或 `ANY_ORDER` 匹配類型，可以透過 `match_type` 欄位連同閾值一起指定。

`IN_ORDER` 匹配的 `EvalConfig` 範例項目：

```json
{
  "criteria": {
    "tool_trajectory_avg_score": {
      "threshold": 1.0, // 設置最低通過閾值
      "match_type": "IN_ORDER" // 指定匹配類型為 IN_ORDER (按順序匹配)
    }
  }
}
```

`ANY_ORDER` 匹配的 `EvalConfig` 範例項目：

```json
{
  "criteria": {
    "tool_trajectory_avg_score": {
      "threshold": 1.0, // 設置最低通過閾值
      "match_type": "ANY_ORDER" // 指定匹配類型為 ANY_ORDER (任一順序匹配)
    }
  }
}
```

#### 輸出及如何解讀

輸出是 0.0 到 1.0 之間的分數，其中 1.0 表示所有呼叫的實際與預期工具軌跡完美匹配，0.0 表示所有呼叫完全不匹配。分數越高越好。低於 1.0 的分數表示至少有一次呼叫中，代理的工具呼叫軌跡偏離了預期軌跡。

## response_match_score

此準則使用 ROUGE-1 評估代理的最終回應是否與黃金/預期最終回應相匹配。

### 何時使用此準則？

當您需要對代理輸出在內容重疊方面與預期輸出的匹配程度進行定量衡量時，請使用此準則。

### 詳細資訊

ROUGE-1 專門測量系統生成的文本（候選摘要）與參考文本之間的單詞 (unigrams) 重疊。它本質上檢查參考文本中有多少單個單詞出現在候選文本中。要了解更多資訊，請參閱 [ROUGE-1](https://github.com/google-research/google-research/tree/master/rouge) 的詳細資訊。

### 如何使用此準則？

您可以在 `EvalConfig` 的 `criteria` 字典下指定此準則的閾值。該值應為 0.0 到 1.0 之間的浮點數，代表評估案例通過所需的最低可接受分數。

`EvalConfig` 範例項目：

```json
{
  "criteria": {
    "response_match_score": 0.8 // 設置 response_match_score 的閾值為 0.8
  }
}
```

### 輸出及如何解讀

此準則的值範圍為 [0,1]，越接近 1 的值越理想。

## final_response_match_v2

此準則使用 LLM 作為裁判，評估代理的最終回應是否與黃金/預期 (golden/expected) 最終回應相匹配。

### 何時使用此準則？

當您需要根據參考評估代理最終回應的正確性，但要求在答案呈現方式上具有靈活性時，請使用此準則。它適用於不同的措辭或格式都可以接受，只要核心含義和資訊與參考相符的情況。此準則是評估問答、摘要或其他生成式任務的理想選擇，在這些任務中，語義等效性比精確的詞彙重疊更重要，使其成為比 `response_match_score` 更進階的替代方案。

### 詳細資訊

此準則使用大型語言模型 (LLM) 作為裁判，判斷代理的最終回應在語義上是否等同於提供的參考回應。它被設計為比詞彙匹配指標（如 `response_match_score`）更靈活，因為它關注代理的回應是否包含正確的資訊，同時容忍格式、措辭或包含額外正確細節的差異。

對於每次呼叫，準則都會提示裁判 LLM 將代理的回應與參考相比評定為「有效 (valid)」或「無效 (invalid)」。為了確保穩健性，此過程會重複多次（可透過 `num_samples` 配置），並由多數票決定該次呼叫是獲得 1.0 分（有效）還是 0.0 分（無效）。最終準則分數是整個評估案例中被視為有效的呼叫比例。

### 如何使用此準則？

此準則使用 `LlmAsAJudgeCriterion`，允許您配置評估閾值、裁判模型和每次呼叫的樣本數。

`EvalConfig` 範例項目：

```json
{
  "criteria": {
    "final_response_match_v2": {
      "threshold": 0.8, // 設置評估閾值
      "judge_model_options": {
            "judge_model": "gemini-2.5-flash", // 指定裁判模型
            "num_samples": 5 // 每次評估的樣本數量
          }
        }
    }
  }
}
```

### 輸出及如何解讀

此準則返回 0.0 到 1.0 之間的分數。1.0 分表示 LLM 裁判認為代理在所有呼叫中的最終回應都是有效的，而接近 0.0 的分數表示與參考回應相比，許多回應被判定為無效。值越高越好。

## rubric_based_final_response_quality_v1

此準則使用 LLM 作為裁判，根據使用者定義的一組量表 (rubrics) 評估代理最終回應的品質。

### 何時使用此準則？

當您需要評估超出簡單正確性或與參考語義等效的回應品質維度時，請使用此準則。它非常適合評估細微的屬性，如語氣、風格、幫助程度，或是否遵守量表中定義的特定對話指南。當不存在單一參考回應，或品質取決於多個主觀因素時，此準則特別有用。

### 詳細資訊

此準則提供了一種靈活的方法，根據您定義為量表的特定標準來評估回應品質。例如，您可以定義量表來檢查回應是否簡潔、是否正確推斷了使用者意圖，或者是否避免了專業術語。

該準則使用 LLM 作為裁判，針對每個量表評估代理的最終回應，並為每個量表產生「是」(1.0) 或「否」(0.0) 的判定。與其他基於 LLM 的指標一樣，它會對每個呼叫多次取樣裁判模型，並使用多數票決定該呼叫中每個量表的分數。一次呼叫的總分是其量表分數的平均值。評估案例的最終準則分數是所有呼叫中這些總分的平均值。

### 如何使用此準則？

此準則使用 `RubricsBasedCriterion`，需要在 `EvalConfig` 中提供量表列表。每個量表都應定義唯一的 ID 及其內容。

`EvalConfig` 範例項目：

```json
{
  "criteria": {
    "rubric_based_final_response_quality_v1": {
      "threshold": 0.8, // 設置評估閾值
      "judge_model_options": {
        "judge_model": "gemini-2.5-flash", // 指定裁判模型
        "num_samples": 5 // 樣本數量
      },
      "rubrics": [
        {
          "rubric_id": "conciseness",
          "rubric_content": {
            "text_property": "代理的回應直接且精要。" // 定義簡潔性量表內容
          }
        },
        {
          "rubric_id": "intent_inference",
          "rubric_content": {
            "text_property": "代理的回應準確地從模糊的查詢中推斷出使用者的潛在目標。" // 定義意圖推斷量表內容
          }
        }
      ]
    }
  }
}
```

### 輸出及如何解讀

準則輸出 0.0 到 1.0 之間的總分，其中 1.0 表示代理的回應在所有呼叫中都滿足了所有量表，而 0.0 表示沒有滿足任何量表。結果還包括每次呼叫的詳細個別量表分數。值越高越好。

## rubric_based_tool_use_quality_v1

此準則使用 LLM 作為裁判，根據使用者定義的一組量表評估代理工具使用的品質。

### 何時使用此準則？

當您需要評估代理「如何」使用工具，而不僅僅是最終回應是否正確時，請使用此準則。它非常適合評估代理是否選擇了正確的工具、是否使用了正確的參數，或者是否遵循了特定的工具呼叫序列。這對於驗證代理的推理過程、偵錯工具使用錯誤以及確保遵守規定的工作流程非常有用，特別是在多個工具使用路徑都可能導致相似最終答案，但只有一個路徑被認為是正確的情況下。

### 詳細資訊

此準則提供了一種靈活的方法，根據您定義為量表的特定規則來評估工具使用情況。例如，您可以定義量表來檢查是否呼叫了特定工具、其參數是否正確，或者工具是否按特定順序呼叫。

該準則使用 LLM 作為裁判，針對每個量表評估代理的工具呼叫和回應，並為每個量表產生「是」(1.0) 或「否」(0.0) 的判定。與其他基於 LLM 的指標一樣，它會對每個呼叫多次取樣裁判模型，並使用多數票決定該呼叫中每個量表的分數。一次呼叫的總分是其量表分數的平均值。評估案例的最終準則分數是所有呼叫中這些總分的平均值。

### 如何使用此準則？

此準則使用 `RubricsBasedCriterion`，需要在 `EvalConfig` 中提供量表列表。每個量表都應定義唯一的 ID 及其內容，描述要評估的工具使用的特定方面。

`EvalConfig` 範例項目：

```json
{
  "criteria": {
    "rubric_based_tool_use_quality_v1": {
      "threshold": 1.0, // 設置評估閾值
      "judge_model_options": {
        "judge_model": "gemini-2.5-flash", // 指定裁判模型
        "num_samples": 5 // 樣本數量
      },
      "rubrics": [
        {
          "rubric_id": "geocoding_called",
          "rubric_content": {
            "text_property": "代理在呼叫 GetWeather 工具之前先呼叫了 GeoCoding 工具。" // 檢查工具呼叫順序
          }
        },
        {
          "rubric_id": "getweather_called",
          "rubric_content": {
            "text_property": "代理使用從使用者位置衍生的坐標呼叫 GetWeather 工具。" // 檢查工具參數
          }
        }
      ]
    }
  }
}
```

### 輸出及如何解讀

準則輸出 0.0 到 1.0 之間的總分，其中 1.0 表示代理的工具使用在所有呼叫中都滿足了所有量表，而 0.0 表示沒有滿足任何量表。結果還包括每次呼叫的詳細個別量表分數。值越高越好。

## hallucinations_v1

此準則評估模型回應是否包含任何虛假、矛盾或不受支援的主張。

### 何時使用此準則？

使用此準則可確保代理的回應基於提供的上下文（例如，工具輸出、使用者查詢、指令）且不包含幻覺。

### 詳細資訊

此準則根據包含開發者指令、使用者提示、工具定義以及工具呼叫及其結果的上下文，評估模型回應是否包含任何虛假、矛盾或不受支援的主張。它使用 LLM 作為裁判，並遵循兩步過程：

1.  **分段器 (Segmenter)**：將代理回應分割成單個句子。
2.  **句子驗證器 (Sentence Validator)**：針對提供的上下文評估每個分段句子的基礎性。每個句子都被標記為 `supported` (受支援)、`unsupported` (不受支援)、`contradictory` (矛盾)、`disputed` (有爭議) 或 `not_applicable` (不適用)。

該指標計算準確度分數：標記為 `supported` 或 `not_applicable` 的句子百分比。預設情況下，僅評估最終回應。如果在準則中將 `evaluate_intermediate_nl_responses` 設置為 true，則代理的中間自然語言回應也會被評估。

### 如何使用此準則？

此準則使用 `HallucinationsCriterion`，允許您配置評估閾值、裁判模型、每次呼叫的樣本數以及是否評估中間自然語言回應。

`EvalConfig` 範例項目：

```json
{
  "criteria": {
    "hallucinations_v1": {
      "threshold": 0.8, // 設置準確度閾值
      "judge_model_options": {
            "judge_model": "gemini-2.5-flash", // 指定裁判模型
          },
      "evaluate_intermediate_nl_responses": true // 是否評估中間回應
    }
  }
}

```

### 輸出及如何解讀

此準則返回 0.0 到 1.0 之間的分數。1.0 分表示代理回應中的所有句子都基於上下文，而接近 0.0 的分數表示許多句子是虛假、矛盾或不受支援的。值越高越好。

## safety_v1

此準則評估代理回應的安全性（無害性）。

### 何時使用此準則？

當您需要確保代理回應符合安全準則且不產生有害或不適當的內容時，應使用此準則。對於面向使用者的應用程式或任何將回應安全性視為優先事項的系統，這點至關重要。

### 詳細資訊

此準則評估代理的回應是否包含任何有害內容，例如仇恨言論、騷擾或危險資訊。與 ADK 內建實現的其他指標不同，`safety_v1` 將評估委託給 Vertex AI General AI Eval SDK。

### 如何使用此準則？

使用此準則需要一個 Google Cloud 專案。您必須設置 `GOOGLE_CLOUD_PROJECT` 和 `GOOGLE_CLOUD_LOCATION` 環境變數（通常在代理目錄的 `.env` 檔案中），以便 Vertex AI SDK 正常運作。

您可以在 `EvalConfig` 的 `criteria` 字典下指定此準則的閾值。該值應為 0.0 到 1.0 之間的浮點數，代表回應被視為通過的最低安全分數。

`EvalConfig` 範例項目：

```json
{
  "criteria": {
    "safety_v1": 0.8 // 設置最低安全分數閾值
  }
}
```

### 輸出及如何解讀

此準則返回 0.0 到 1.0 之間的分數。接近 1.0 的分數表示回應是安全的，而接近 0.0 的分數表示存在潛在的安全問題。

## per_turn_user_simulator_quality_v1

此準則評估使用者模擬器是否忠於對話計劃。

#### 何時使用此準則？

當您需要在多輪對話中評估使用者模擬器時，請使用此準則。它旨在評估模擬器是否遵循 `ConversationScenario` 中定義的對話計劃。

#### 詳細資訊

此準則判斷使用者模擬器在多輪對話中是否遵循定義的 `ConversationScenario`。

對於第一輪，此準則檢查使用者模擬器的回應是否與 `ConversationScenario` 中的 `starting_prompt` 相符。對於後續輪次，它使用 LLM 作為裁判，評估使用者回應是否遵循 `ConversationScenario` 中的 `conversation_plan`。

#### 如何使用此準則？

此準則允許您配置評估閾值、裁判模型和每次呼叫的樣本數。該準則還允許您指定 `stop_signal` (停止訊號)，用於向 LLM 裁判發訊號表示對話已完成。為了獲得最佳效果，請在 `LlmBackedUserSimulator` 中使用停止訊號。

`EvalConfig` 範例項目：

```json
{
  "criteria": {
    "per_turn_user_simulator_quality_v1": {
      "threshold": 1.0, // 設置評估閾值
      "judge_model_options": {
        "judge_model": "gemini-2.5-flash", // 指定裁判模型
        "num_samples": 5 // 樣本數量
      },
      "stop_signal": "</finished>" // 對話結束標籤
    }
  }
}
```

#### 輸出及如何解讀

該準則返回 0.0 到 1.0 之間的分數，代表使用者模擬器的回應被判定為符合對話情境的輪次比例。1.0 分表示模擬器在所有輪次中的表現均符合預期，而接近 0.0 的分數表示模擬器在許多輪次中偏離了計劃。值越高越好。

---
## 評估標準總覽
### 評估指標總覽（含決策指南）

#### 一、快速決策指南（先選方法，再看細節）

| 問題 / 情境                                  | 建議評估指標                           |
| -------------------------------------------- | -------------------------------------- |
| 是否需要**完全可重現、無主觀判斷**？         | tool_trajectory_avg_score              |
| 是否要**比較工具呼叫流程是否正確**？         | tool_trajectory_avg_score              |
| 是否只關心**文字內容重疊比例**？             | response_match_score                   |
| 是否重視**語義正確性，而非字詞是否一樣**？   | final_response_match_v2                |
| 是否要評估**語氣、風格、整體品質**？         | rubric_based_final_response_quality_v1 |
| 是否要檢查**工具選擇／參數／順序是否合理**？ | rubric_based_tool_use_quality_v1       |
| 是否擔心模型**憑空編造（幻覺）**？           | hallucinations_v1                      |
| 是否需要**安全與合規檢核**？                 | safety_v1                              |
| 是否在測試**多輪對話的使用者模擬器**？       | per_turn_user_simulator_quality_v1     |

> 建議實務做法：
> - **回歸測試 / CI**：先用「比對型評估」
> - **功能正確性 + 品質**：比對型 + LLM 評估並行
> - **對外或高風險場景**：務必加上 hallucinations_v1 + safety_v1

---

#### 二、比對型評估（Comparison-based Evals）

| 評估指標                      | 何時用                         | 核心資訊                                        | 配置                     | 輸出         |
| ----------------------------- | ------------------------------ | ----------------------------------------------- | ------------------------ | ------------ |
| **tool_trajectory_avg_score** | 回歸測試／流程驗證／高精度任務 | 工具呼叫序列比對<br/>EXACT／IN_ORDER／ANY_ORDER | threshold<br/>match_type | 0.0–1.0 分數 |
| **response_match_score**      | 定量內容重疊                   | ROUGE-1<br/>unigram overlap                     | threshold                | 0.0–1.0 分數 |

---

#### 三、LLM 評估（LLM / Judge-based Evals）

| 評估指標                                   | 何時用                   | 核心資訊                                   | 配置                                                            | 輸出             |
| ------------------------------------------ | ------------------------ | ------------------------------------------ | --------------------------------------------------------------- | ---------------- |
| **final_response_match_v2**                | 語義等效性高於詞彙重疊   | LLM 作為裁判<br/>多次取樣提升穩健性        | threshold<br/>judge_model<br/>num_samples                       | 0.0–1.0 分數     |
| **rubric_based_final_response_quality_v1** | 語氣／風格／主觀品質評估 | LLM＋自訂 rubrics 量表                     | rubrics<br/>threshold<br/>judge_model<br/>num_samples           | 0.0–1.0 總分     |
| **rubric_based_tool_use_quality_v1**       | 工具選擇／順序／參數偵錯 | LLM 評估工具使用方式                       | rubrics<br/>threshold<br/>judge_model<br/>num_samples           | 0.0–1.0 總分     |
| **hallucinations_v1**                      | 上下文依據檢核           | 分段＋句子驗證<br/>supported / unsupported | threshold<br/>judge_model                                       | 0.0–1.0 準確度   |
| **safety_v1**                              | 安全準則檢核             | Vertex AI General AI Eval SDK              | GCP env<br/>threshold                                           | 0.0–1.0 安全分數 |
| **per_turn_user_simulator_quality_v1**     | 多輪對話一致性           | 遵循 ConversationScenario                  | threshold<br/>judge_model<br/>num_samples<br/>stop_signal（可） | 0.0–1.0 符合比例 |

---

#### 四、常見組合建議（實務）

- **CI / Regression Pipeline**
  tool_trajectory_avg_score + response_match_score

- **功能正確性驗證（LLM App）**
  final_response_match_v2 + hallucinations_v1

- **品質導向（對外回應、客服、助理）**
  rubric_based_final_response_quality_v1 + safety_v1

- **Agent / Tool-heavy 系統**
  rubric_based_tool_use_quality_v1 + tool_trajectory_avg_score
