# Apigee AI Gateway for ADK agents

> 🔔 `更新日期：2026-01-23`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/agents/models/apigee/

[`ADK 支援`: `Python v1.18.0` | `Java v0.4.0`]

[Apigee](https://docs.cloud.google.com/apigee/docs/api-platform/get-started/what-apigee)
提供強大的 [AI 閘道器](https://cloud.google.com/solutions/apigee-ai)，
改變您管理與治理生成式 AI 模型流量的方式。透過 Apigee 代理公開您的 AI 模型端點（例如 Vertex AI 或 Gemini API），您立即就能獲得企業級的功能：

- **模型安全：** 實作如 Model Armor 之類的安全性原則來防禦威脅。

- **流量治理：** 強制執行速率限制與權杖限制，以管理成本並防止濫用。

- **效能：** 使用語義快取（Semantic Caching）與進階模型路由，改善回應時間與效率。

- **監控與可見性：** 針對您的所有 AI 請求提供詳盡的監控、分析與稽核。

> [!NOTE]
`ApigeeLLM` 封裝目前設計用於 Vertex AI 和 Gemini API (generateContent)。我們正持續擴展對其他模型與介面的支援。

## 範例實作

透過實例化 `ApigeeLlm` 封裝物件並將其傳遞給 `LlmAgent` 或其他代理類型，將 Apigee 的治理整合到您的代理工作流程中。

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.agents import LlmAgent
from google.adk.models.apigee_llm import ApigeeLlm

# 實例化 ApigeeLlm 封裝
model = ApigeeLlm(
    # 指定指向您模型的 Apigee 路由。如需更多資訊，請參閱 ApigeeLlm 說明文件 (https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_apigeellm)。
    model="apigee/gemini-2.5-flash",
    # 您部署的 Apigee 代理的代理 URL，包含基礎路徑
    proxy_url=f"https://{APIGEE_PROXY_URL}",
    # 傳遞必要的驗證/授權標頭（例如 API 金鑰）
    custom_headers={"foo": "bar"}
)

# 將設定好的模型封裝傳遞給您的 LlmAgent
agent = LlmAgent(
    model=model,
    name="my_governed_agent",
    instruction="You are a helpful assistant powered by Gemini and governed by Apigee.",
    # ... 其他代理參數
)
```

> Java

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.ApigeeLlm;
import com.google.common.collect.ImmutableMap;

// 建立 ApigeeLlm 實例
ApigeeLlm apigeeLlm =
        ApigeeLlm.builder()
            .modelName("apigee/gemini-2.5-flash") // 指定指向您模型的 Apigee 路由。如需更多資訊，請參閱 ApigeeLlm 說明文件
            .proxyUrl(APIGEE_PROXY_URL) // 您部署的 Apigee 代理的代理 URL，包含基礎路徑
            .customHeaders(ImmutableMap.of("foo", "bar")) // 傳遞必要的驗證/授權標頭（例如 API 金鑰）
            .build();

// 將設定好的模型封裝傳遞給您的 LlmAgent
LlmAgent agent =
    LlmAgent.builder()
        .model(apigeeLlm)
        .name("my_governed_agent")
        .description("my_governed_agent")
        .instruction("You are a helpful assistant powered by Gemini and governed by Apigee.")
        // 接下來將會新增工具
        .build();
```

</details>

在此配置下，您代理的每一次 API 呼叫都會先經過 Apigee。在請求安全地轉發到基礎 AI 模型端點之前，所有必要的原則（安全性、速率限制、記錄）都會在此執行。有關使用 Apigee 代理的完整程式碼範例，請參閱 [Hello World Apigee LLM](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_apigeellm)。

## 下一步

- [Pack Auto Insurance Agent 參考範例](../../python/agents/pack-auto-insurance-agent/)