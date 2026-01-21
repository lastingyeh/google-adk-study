# 供 ADK 代理程式使用的 Claude 模型
🔔 `更新日期：2026-01-21`

[`ADK 支援`: `Java v0.2.0`]

您可以使用 ADK 的 `Claude` 包裝類別，透過 Anthropic API 金鑰或從 Vertex AI 後端，將 Anthropic 的 Claude 模型直接整合到您的 Java ADK 應用程式中。您也可以透過 Google Cloud Vertex AI 服務存取 Anthropic 模型。如需更多資訊，請參閱 [Vertex AI 上的第三方模型（例如 Anthropic Claude）](./vertex.md#vertex-ai-上的-anthropic-claude) 章節。您也可以透過適用於 Python 的 [LiteLLM](./litellm.md) 程式庫使用 Anthropic 模型。

## 開始使用

以下程式碼範例顯示了在您的代理程式中使用 Gemini 模型的基本實作：

```java
public static LlmAgent createAgent() {

  // 使用 AnthropicOkHttpClient 建立 Anthropic 客戶端
  AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
      .apiKey("ANTHROPIC_API_KEY")
      .build();

  // 初始化 Claude 模型
  Claude claudeModel = new Claude(
      "claude-3-7-sonnet-latest", anthropicClient
  );

  // 建立並回傳 LlmAgent
  return LlmAgent.builder()
      .name("claude_direct_agent")
      .model(claudeModel)
      .instruction("You are a helpful AI assistant powered by Anthropic Claude.")
      .build();
}
```

## 先決條件

1.  **依賴項目：**
    *   **Anthropic SDK 類別（間接依賴）：** Java ADK 的 `com.google.adk.models.Claude` 包裝類別依賴於 Anthropic 官方 Java SDK 的類別。這些通常作為 *間接依賴（transitive dependencies）* 包含在內。如需更多資訊，請參閱 [Anthropic Java SDK](https://github.com/anthropics/anthropic-sdk-java)。

2.  **Anthropic API 金鑰：**
    *   從 Anthropic 獲取 API 金鑰。請使用秘密管理器（secret manager）安全地管理此金鑰。

## 範例實作

實例化 `com.google.adk.models.Claude`，提供所需的 Claude 模型名稱和配置了 API 金鑰的 `AnthropicOkHttpClient`。然後，將 `Claude` 實例傳遞給您的 `LlmAgent`，如下列範例所示：

```java
import com.anthropic.client.AnthropicClient;
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Claude;
import com.anthropic.client.okhttp.AnthropicOkHttpClient; // 來自 Anthropic 的 SDK

public class DirectAnthropicAgent {

  private static final String CLAUDE_MODEL_ID = "claude-3-7-sonnet-latest"; // 或您偏好的 Claude 模型

  public static LlmAgent createAgent() {

    // 建議從安全的設定檔載入敏感金鑰
    AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
        .apiKey("ANTHROPIC_API_KEY")
        .build();

    // 建立 Claude 模型實例
    Claude claudeModel = new Claude(
        CLAUDE_MODEL_ID,
        anthropicClient
    );

    // 建立並回傳代理程式
    return LlmAgent.builder()
        .name("claude_direct_agent")
        .model(claudeModel)
        .instruction("You are a helpful AI assistant powered by Anthropic Claude.")
        // ... 其他 LlmAgent 配置
        .build();
  }

  public static void main(String[] args) {
    try {
      // 獲取代理程式
      LlmAgent agent = createAgent();
      System.out.println("成功建立直接 Anthropic 代理程式：" + agent.name());
    } catch (IllegalStateException e) {
      // 捕捉並顯示錯誤
      System.err.println("建立代理程式時出錯：" + e.getMessage());
    }
  }
}
```
