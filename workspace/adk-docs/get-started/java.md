# ADK for Java 快速入門

> 更新日期：2026 年 1 月 4 日

本指南將引導您快速上手使用適用於 Java 的 Agent Development Kit (ADK)。在開始之前，請確保您已安裝以下軟體：

*   Java 17 或更高版本
*   Maven 3.9 或更高版本

## 建立 Agent 專案

首先，建立一個包含以下檔案和目錄結構的 Agent 專案：

```
my_agent/
    src/main/java/com/example/agent/
                        HelloTimeAgent.java # 主要的 Agent 程式碼
                        AgentCliRunner.java # 命令列介面
    pom.xml                                 # 專案設定檔
    .env                                    # 存放 API 金鑰或專案 ID
```

您可以使用以下指令快速建立此專案結構：

**MacOS / Linux**

```bash
mkdir -p my_agent/src/main/java/com/example/agent && \
    touch my_agent/src/main/java/com/example/agent/HelloTimeAgent.java && \
    touch my_agent/src/main/java/com/example/agent/AgentCliRunner.java && \
    touch my_agent/pom.xml my_agent/.env
```

**Windows**

```console
mkdir my_agent\src\main\java\com\example\agent
type nul > my_agent\src\main\java\com\example\agent\HelloTimeAgent.java
type nul > my_agent\src\main\java\com\example\agent\AgentCliRunner.java
type nul > my_agent\pom.xml
type nul > my_agent\.env
```

### 定義 Agent 程式碼

接著，為您的基本 Agent 建立程式碼，其中包含一個名為 `getCurrentTime()` 的 ADK [函式工具 (Function Tool)](https://google.github.io/adk-docs/tools-custom/function-tools/) 的簡單實作。將以下程式碼新增到您的 `HelloTimeAgent.java` 檔案中：

```java title="my_agent/src/main/java/com/example/agent/HelloTimeAgent.java"
package com.example.agent;

import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;

import java.util.Map;

public class HelloTimeAgent {

    public static BaseAgent ROOT_AGENT = initAgent();

    private static BaseAgent initAgent() {
        return LlmAgent.builder()
            .name("hello-time-agent")
            .description("告知指定城市的目前時間") // 註解：Agent 的功能描述
            .instruction("""
                你是一個樂於助人的助理，負責告知某個城市的目前時間。
                請使用 'getCurrentTime' 工具來達成此目的。
                """) // 註解：給予 Agent 的指令
            .model("gemini-2.5-flash")
            .tools(FunctionTool.create(HelloTimeAgent.class, "getCurrentTime"))
            .build();
    }

    /** 模擬工具實作 */
    @Schema(description = "取得指定城市的目前時間") // 註解：工具的用途描述
    public static Map<String, String> getCurrentTime(
        @Schema(name = "city", description = "要取得時間的城市名稱") String city) { // 註解：工具參數的描述
        return Map.of(
            "city", city,
            "forecast", "現在時間是上午 10:30。" // 註解：模擬的回應
        );
    }
}
```

> **重點說明：**
> *   `LlmAgent.builder()`：這是建立基於大型語言模型 (LLM) 的 Agent 的主要建構器。
> *   `instruction`: 這是給予 Agent 的指令，告訴它其角色和目標。
> *   `tools`: 這裡註冊了 `getCurrentTime` 函式作為 Agent 可以使用的工具。這使得 Agent 能夠呼叫您的 Java 程式碼來執行特定任務。
> *   `@Schema`: 這個註解用來向 LLM 描述函式和其參數的用途，讓模型知道在何時以及如何使用這個工具。

> [!IMPORTANT]：Gemini 3 相容性問題**
>
> ADK Java v0.3.0 及更低版本與 [Gemini 3 Pro Preview](https://ai.google.dev/gemini-api/docs/models#gemini-3-pro) 不相容，因為函式呼叫的思維簽章 (thought signature) 有所變更。請改用 Gemini 2.5 或更低版本的模型。

### 設定專案與依賴項目

您的 ADK Agent 專案需要在 `pom.xml` 專案檔中加入以下依賴項：

```xml title="my_agent/pom.xml (部分)"
<dependencies>
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>adk-core</artifactId>
        <version>0.5.0</version>
    </dependency>
</dependencies>
```

以下是一個完整的 `pom.xml` 設定範例，您可以直接使用：

`my_agent/pom.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example.agent</groupId>
    <artifactId>adk-agents</artifactId>
    <version>1.0-SNAPSHOT</version>

    <!-- 指定您將使用的 Java 版本 -->
    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <!-- ADK 核心依賴 -->
        <dependency>
            <groupId>com.google.adk</groupId>
            <artifactId>google-adk</artifactId>
            <version>0.5.0</version>
        </dependency>
        <!-- 用於偵錯 Agent 的 ADK 開發 Web UI -->
        <dependency>
            <groupId>com.google.adk</groupId>
            <artifactId>google-adk-dev</artifactId>
            <version>0.5.0</version>
        </dependency>
    </dependencies>

</project>
```

### 設定您的 API 金鑰

本專案使用 Gemini API，因此需要一組 API 金鑰。如果您還沒有，可以在 Google AI Studio 的 [API 金鑰](https://aistudio.google.com/app/apikey) 頁面建立一組金鑰。

在終端機視窗中，將您的 API 金鑰寫入專案的 `.env` 檔案以設定環境變數：

**MacOS / Linux**

```bash title="更新: my_agent/.env"
echo 'export GOOGLE_API_KEY="YOUR_API_KEY"' > .env
```

**Windows**

```console title="更新: my_agent/env.bat"
echo 'set GOOGLE_API_KEY="YOUR_API_KEY"' > env.bat
```

> **提示：** ADK 支援多種生成式 AI 模型。若要了解如何在 ADK Agent 中設定其他模型，請參閱[模型與驗證](https://google.github.io/adk-docs/agents/models/)。

### 建立 Agent 命令列介面

建立一個 `AgentCliRunner.java` 類別，讓您可以從命令列執行 `HelloTimeAgent` 並與之互動。此程式碼展示了如何建立一個 `RunConfig` 物件來執行 Agent，以及一個 `Session` 物件來與執行中的 Agent 互動。

`my_agent/src/main/java/com/example/agent/AgentCliRunner.java`
```java
package com.example.agent;

import com.google.adk.agents.RunConfig;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import java.util.Scanner;

import static java.nio.charset.StandardCharsets.UTF_8;

public class AgentCliRunner {

    public static void main(String[] args) {
        RunConfig runConfig = RunConfig.builder().build();
        InMemoryRunner runner = new InMemoryRunner(HelloTimeAgent.ROOT_AGENT);

        Session session = runner
                .sessionService()
                .createSession(runner.appName(), "user1234")
                .blockingGet();

        try (Scanner scanner = new Scanner(System.in, UTF_8)) {
            while (true) {
                System.out.print("\nYou > ");
                String userInput = scanner.nextLine();
                if ("quit".equalsIgnoreCase(userInput)) {
                    break;
                }

                Content userMsg = Content.fromParts(Part.fromText(userInput));
                Flowable<Event> events = runner.runAsync(session.userId(), session.id(), userMsg, runConfig);

                System.out.print("\nAgent > ");
                events.blockingForEach(event -> {
                    if (event.finalResponse()) {
                        System.out.println(event.stringifyContent());
                    }
                });
            }
        }
    }
}
```

## 執行您的 Agent

您可以使用您定義的互動式命令列介面 `AgentCliRunner` 類別，或使用 ADK 提供的 `AdkWebServer` 類別來執行您的 ADK Agent。這兩種方式都可以讓您測試並與您的 Agent 互動。

### 使用命令列介面執行

使用以下 Maven 指令，透過 `AgentCliRunner` 類別執行您的 Agent：

```console
# 記得載入金鑰與設定: source .env 或 env.bat
mvn compile exec:java -Dexec.mainClass="com.example.agent.AgentCliRunner"
```

![adk-run.png](https://google.github.io/adk-docs/assets/adk-run.png)

### 使用 Web 介面執行

使用以下 Maven 指令，透過 ADK Web 介面執行您的 Agent：

```
記得載入金鑰與設定: source .env 或 env.bat
mvn compile exec:java \
    -Dexec.mainClass="com.google.adk.web.AdkWebServer" \
    -Dexec.args="--adk.agents.source-dir=target --server.port=8000"
```

此指令會啟動一個帶有聊天介面的 Web 伺服器。您可以透過 (http://localhost:8000) 存取此介面。在左上角選擇您的 Agent，然後輸入您的請求。

![adk-web-dev-ui-chat.png](https://google.github.io/adk-docs/assets/adk-web-dev-ui-chat.png)

> [!WARNING]ADK Web 僅供開發使用**
>
> ADK Web ***不適用於生產環境部署***。您應該僅在開發和偵錯階段使用 ADK Web。


### 參考資源

*   [Gemini 3 Pro Preview](https://ai.google.dev/gemini-api/docs/models#gemini-3-pro)
*   [Google AI Studio API 金鑰](https://aistudio.google.com/app/apikey)
*   [ADK 模型與驗證](https://google.github.io/adk-docs/agents/models/)
*   [函式工具 (Function Tool)](https://google.github.io/adk-docs/tools-custom/function-tools/)