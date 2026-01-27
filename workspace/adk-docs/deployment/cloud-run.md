# 部署到 Cloud Run

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/deploy/cloud-run/

[Cloud Run](https://cloud.google.com/run)
是一個全託管平台，讓您可以直接在 Google 的可擴展基礎架構上運行您的程式碼。

要部署您的代理，您可以使用 `adk deploy cloud_run` 指令 _(Python 推薦使用)_，或者透過 Cloud Run 使用 `gcloud run deploy` 指令。

## 代理範例

對於每個指令，我們將參考 [LLM 代理](../agents/llm-agents.md) 頁面上定義的 `Capital Agent` 範例。我們假設它位於一個目錄中 (例如：`capital_agent`)。

繼續之前，請確認您的代理程式碼配置如下：

<details>
<summary>配置說明</summary>

> Python

1. 代理程式碼位於您的代理目錄中名為 `agent.py` 的檔案內。
2. 您的代理變數名為 `root_agent`。
3. `__init__.py` 位於您的代理目錄中，並包含 `from . import agent`。
4. 您的 `requirements.txt` 檔案存在於代理目錄中。

> Go

 1. 您的應用程式進入點 (main 套件和 main() 函式) 位於單個 Go 檔案中。使用 `main.go` 是一個強烈建議的慣例。
 2. 您的代理實例被傳遞給啟動器配置，通常使用 `agent.NewSingleLoader` (yourAgent)。`adkgo` 工具使用此啟動器以正確的服務啟動您的代理。
 3. 您的 go.mod 和 go.sum 檔案存在於您的專案目錄中以管理相依性。

 請參閱下一節以獲取更多詳細資訊。您也可以在 Github 儲存庫中找到 [範例應用程式](https://github.com/google/adk-docs/tree/main/examples/go/cloud-run)。

> Java

1. 代理程式碼位於您的代理目錄中名為 `CapitalAgent.java` 的檔案內。
2. 您的代理變數是全域的，並遵循 `public static final BaseAgent ROOT_AGENT` 格式。
3. 您的代理定義存在於靜態類別方法中。

請參閱下一節以獲取更多詳細資訊。您也可以在 Github 儲存庫中找到
[範例應用程式](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run)。

</details>

## 環境變數

按照 [設定與安裝](../get-started/installation/) 指南中的說明設定您的環境變數。

``` shell
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1 # 或者您偏好的位置
export GOOGLE_GENAI_USE_VERTEXAI=True
```

_(將 `your-project-id` 替換為您的實際 GCP 專案 ID)_

或者，您也可以使用來自 AI Studio 的 API 金鑰

```shell
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1 # 或者您偏好的位置
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY=your-api-key
```

*(將 `your-project-id` 替換為您的實際 GCP 專案 ID，並將 `your-api-key` 替換為您來自 AI Studio 的實際 API 金鑰)*

## 先決條件

1. 您應該擁有一個 Google Cloud 專案。您需要知道您的：
    - 專案名稱 (即 "my-project")
    - 專案位置 (即 "us-central1")
    - 服務帳戶 (即 "1234567890-compute@developer.gserviceaccount.com")
    - GOOGLE_API_KEY

## Secret (密鑰)

請確保您已建立一個可由您的服務帳戶讀取的 Secret。

### GOOGLE_API_KEY Secret 項目

您可以手動建立 Secret 或使用 CLI：

```shell
echo "<<put your GOOGLE_API_KEY here>>" | gcloud secrets create GOOGLE_API_KEY --project=my-project --data-file=-
```

### 讀取權限
您應該給予您的服務帳戶適當的權限以讀取此 Secret。

```shell
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY --member="serviceAccount:1234567890-compute@developer.gserviceaccount.com" --role="roles/secretmanager.secretAccessor" --project=my-project
```

## 部署負載 (Deployment payload)

當您將 ADK 代理工作流程部署到 Google Cloud Run 時，
以下內容將上傳到服務：

- 您的 ADK 代理程式碼
- 您的 ADK 代理程式碼中宣告的任何相依性
- 您的代理使用的 ADK API 伺服器程式碼版本

預設部署 *不* 包含 ADK 網頁使用者介面函式庫，
除非您將其指定為部署設定，例如 `adk deploy cloud_run` 指令的 `--with_ui` 選項。

## 部署指令

<details>
<summary>Python - adk CLI</summary>

###  adk CLI

`adk deploy cloud_run` 指令將您的代理程式碼部署到 Google Cloud Run。

確保您已通過 Google Cloud 驗證 (`gcloud auth login` 和 `gcloud config set project <your-project-id>`)。

#### 設定環境變數

可選但建議：設定環境變數可以讓部署指令更簡潔。

```shell
# 設定您的 Google Cloud 專案 ID
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

# 設定您想要的 Google Cloud 位置
export GOOGLE_CLOUD_LOCATION="us-central1" # 範例位置

# 設定您的代理程式碼目錄的路徑
export AGENT_PATH="./capital_agent" # 假設 capital_agent 位於目前目錄

# 設定您的 Cloud Run 服務名稱 (可選)
export SERVICE_NAME="capital-agent-service"

# 設定應用程式名稱 (可選)
export APP_NAME="capital-agent-app"
```

#### 指令用法

##### 最小指令

```shell
adk deploy cloud_run \
--project=$GOOGLE_CLOUD_PROJECT \
--region=$GOOGLE_CLOUD_LOCATION \
$AGENT_PATH
```

##### 帶有可選旗標的完整指令

```shell
adk deploy cloud_run \
--project=$GOOGLE_CLOUD_PROJECT \
--region=$GOOGLE_CLOUD_LOCATION \
--service_name=$SERVICE_NAME \
--app_name=$APP_NAME \
--with_ui \
$AGENT_PATH
```

##### 引數

* `AGENT_PATH`: (必填) 位置引數，指定包含您的代理原始碼的目錄路徑 (例如範例中的 `$AGENT_PATH`，或 `capital_agent/`)。此目錄必須至少包含一個 `__init__.py` 和您的主要代理檔案 (例如 `agent.py`)。

##### 選項

* `--project TEXT`: (必填) 您的 Google Cloud 專案 ID (例如 `$GOOGLE_CLOUD_PROJECT`)。
* `--region TEXT`: (必填) 部署的 Google Cloud 位置 (例如 `$GOOGLE_CLOUD_LOCATION`, `us-central1`)。
* `--service_name TEXT`: (可選) Cloud Run 服務的名稱 (例如 `$SERVICE_NAME`)。預設為 `adk-default-service-name`。
* `--app_name TEXT`: (可選) ADK API 伺服器的應用程式名稱 (例如 `$APP_NAME`)。預設為由 `AGENT_PATH` 指定的目錄名稱 (例如，如果 `AGENT_PATH` 是 `./capital_agent`，則為 `capital_agent`)。
* `--agent_engine_id TEXT`: (可選) 如果您透過 Vertex AI Agent Engine 使用託管工作階段服務，請在此提供其資源 ID。
* `--port INTEGER`: (可選) ADK API 伺服器在容器內監聽的連接埠號。預設為 8000。
* `--with_ui`: (可選) 如果包含此項，將在代理 API 伺服器旁邊部署 ADK 開發者 UI。預設情況下，僅部署 API 伺服器。
* `--temp_folder TEXT`: (可選) 指定用於儲存部署過程中產生的中間檔案的目錄。預設為系統暫存目錄中的時間戳記資料夾。 *(注意：除非排除故障問題，否則通常不需要此選項)。*
* `--help`: 顯示說明訊息並退出。

##### 經過驗證的存取
在部署過程中，您可能會收到提示：`Allow unauthenticated invocations to [your-service-name] (y/N)?` (允許未經身份驗證的呼叫到 [your-service-name] (y/N)？)。

* 輸入 `y` 以允許在不進行身份驗證的情況下公開存取您的代理 API 端點。
* 輸入 `N` (或按 Enter 鍵使用預設值) 以要求身份驗證 (例如，使用「測試您的代理」一節中顯示的身份驗證權杖)。

成功執行後，該指令將您的代理部署到 Cloud Run 並提供已部署服務的 URL。

</details>

<details>
<summary>Python - gcloud CLI</summary>

### gcloud CLI for Python

或者，您可以使用帶有 `Dockerfile` 的標準 `gcloud run deploy` 指令進行部署。與 `adk` 指令相比，此方法需要更多的手動設定，但提供了靈活性，特別是如果您想將代理嵌入到自訂 [FastAPI](https://fastapi.tiangolo.com/) 應用程式中。

確保您已通過 Google Cloud 驗證 (`gcloud auth login` 和 `gcloud config set project <your-project-id>`)。

#### 專案結構

按如下方式組織您的專案檔案：

```text
your-project-directory/
├── capital_agent/
│   ├── __init__.py
│   └── agent.py       # 您的代理程式碼 (請參閱「代理範例」分頁)
├── main.py            # FastAPI 應用程式進入點
├── requirements.txt   # Python 相依性
└── Dockerfile         # 容器建置說明
```

在 `your-project-directory/` 的根目錄中建立以下檔案 (`main.py`, `requirements.txt`, `Dockerfile`)。

#### 程式碼檔案

1. 此檔案使用 ADK 中的 `get_fast_api_app()` 設定 FastAPI 應用程式：

   `main.py`
    ```python title="main.py"
    import os

    import uvicorn
    from fastapi import FastAPI
    from google.adk.cli.fast_api import get_fast_api_app

    # Get the directory where main.py is located
    # 取得 main.py 所在的目錄
    AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
    # Example session service URI (e.g., SQLite)
    # Note: Use 'sqlite+aiosqlite' instead of 'sqlite' because DatabaseSessionService requires an async driver
    # 範例工作階段服務 URI (例如 SQLite)
    # 注意：使用 'sqlite+aiosqlite' 而非 'sqlite'，因為 DatabaseSessionService 需要非同步驅動程式
    SESSION_SERVICE_URI = "sqlite+aiosqlite:///./sessions.db"
    # Example allowed origins for CORS
    # CORS 的範例允許來源
    ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
    # Set web=True if you intend to serve a web interface, False otherwise
    # 如果您打算提供網頁介面，請設定 web=True，否則設定 False
    SERVE_WEB_INTERFACE = True

    # Call the function to get the FastAPI app instance
    # Ensure the agent directory name ('capital_agent') matches your agent folder
    # 呼叫函式以取得 FastAPI 應用程式實例
    # 確保代理目錄名稱 ('capital_agent') 與您的代理資料夾相符
    app: FastAPI = get_fast_api_app(
        agents_dir=AGENT_DIR,
        session_service_uri=SESSION_SERVICE_URI,
        allow_origins=ALLOWED_ORIGINS,
        web=SERVE_WEB_INTERFACE,
    )

    # You can add more FastAPI routes or configurations below if needed
    # Example:
    # @app.get("/hello")
    # async def read_root():
    #     return {"Hello": "World"}
    # 如果需要，您可以在下方新增更多 FastAPI 路由或配置
    # 範例：
    # @app.get("/hello")
    # async def read_root():
    #     return {"Hello": "World"}

    if __name__ == "__main__":
        # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
        # 使用 Cloud Run 提供的 PORT 環境變數，預設為 8080
        uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    ```

    *注意：我們將 `agent_dir` 指定為 `main.py` 所在的目錄，並使用 `os.environ.get("PORT", 8080)` 以相容 Cloud Run。*

2. 列出必要的 Python 套件：

    `requirements.txt`
    ```txt title="requirements.txt"
    google-adk
    # Add any other dependencies your agent needs
    # 新增您的代理需要的任何其他相依性
    ```

3. 定義容器映像：

    `Dockerfile`
    ```dockerfile title="Dockerfile"
    FROM python:3.13-slim
    WORKDIR /app

    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    RUN adduser --disabled-password --gecos "" myuser && \
        chown -R myuser:myuser /app

    COPY . .

    USER myuser

    ENV PATH="/home/myuser/.local/bin:$PATH"

    CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
    ```

#### 定義多個代理

您可以透過在 `your-project-directory/` 的根目錄中建立個別資料夾，在同一個 Cloud Run 實例中定義和部署多個代理。每個資料夾代表一個代理，且必須在其配置中定義 `root_agent`。

範例結構：

```text
your-project-directory/
├── capital_agent/
│   ├── __init__.py
│   └── agent.py       # contains `root_agent` definition (包含 `root_agent` 定義)
├── population_agent/
│   ├── __init__.py
│   └── agent.py       # contains `root_agent` definition (包含 `root_agent` 定義)
└── ...
```

#### 使用 `gcloud` 部署

在終端機中導航到 `your-project-directory`。

```shell
gcloud run deploy capital-agent-service \
--source . \
--region $GOOGLE_CLOUD_LOCATION \
--project $GOOGLE_CLOUD_PROJECT \
--allow-unauthenticated \
--set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI"
# Add any other necessary environment variables your agent might need
# 新增您的代理可能需要的任何其他必要環境變數
```

* `capital-agent-service`: 您想要給予 Cloud Run 服務的名稱。
* `--source .`: 告訴 gcloud 從目前目錄中的 Dockerfile 建置容器映像。
* `--region`: 指定部署區域。
* `--project`: 指定 GCP 專案。
* `--allow-unauthenticated`: 允許公開存取服務。對於私人服務，請移除此旗標。
* `--set-env-vars`: 將必要的環境變數傳遞給執行中的容器。確保包含 ADK 和您的代理所需的所有變數 (如果不使用應用程式預設憑證，則如 API 金鑰)。

`gcloud` 將建置 Docker 映像，將其推送到 Google Artifact Registry，並部署到 Cloud Run。完成後，它將輸出您已部署服務的 URL。

有關部署選項的完整清單，請參閱 [`gcloud run deploy` 參考文件](https://cloud.google.com/sdk/gcloud/reference/run/deploy)。

</details>

<details>
<summary>Go - adkgo CLI</summary>


### adk CLI

adkgo 指令位於 google/adk-go 儲存庫的 cmd/adkgo 下。使用之前，您需要從 adk-go 儲存庫的根目錄建置它：

`go build ./cmd/adkgo`

adkgo deploy cloudrun 指令自動化您的應用程式部署。您不需要提供自己的 Dockerfile。

#### 代理程式碼結構

當使用 adkgo 工具時，您的 main.go 檔案必須使用啟動器框架。這是因為該工具編譯您的程式碼，然後以特定的命令列引數 (如 web, api, a2a) 運行產生的可執行檔以啟動所需的服務。啟動器旨在正確解析這些引數。

您的 main.go 應該如下所示：

```go title="main.go"
package main

import (
    "context"
    "fmt"
    "log"
    "os"
    "strings"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/cmd/launcher"
    "google.golang.org/adk/cmd/launcher/full"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/functiontool"
    "google.golang.org/genai"
)

type getCapitalCityArgs struct {
    Country string `json:"country" jsonschema:"The country for which to find the capital city."`
}

func getCapitalCity(ctx tool.Context, args getCapitalCityArgs) (string, error) {
    capitals := map[string]string{
        "united states": "Washington, D.C.",
        "canada":        "Ottawa",
        "france":        "Paris",
        "japan":         "Tokyo",
    }
    capital, ok := capitals[strings.ToLower(args.Country)]
    if !ok {
        return "", fmt.Errorf("couldn't find the capital for %s", args.Country)
    }

    return capital, nil
}

func main() {
    ctx := context.Background()

    model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{
        APIKey: os.Getenv("GOOGLE_API_KEY"),
    })
    if err != nil {
        log.Fatalf("Failed to create model: %v", err)
    }

    capitalTool, err := functiontool.New(
        functiontool.Config{
            Name:        "get_capital_city",
            Description: "Retrieves the capital city for a given country.",
        },
        getCapitalCity,
    )
    if err != nil {
        log.Fatalf("Failed to create function tool: %v", err)
    }

    geoAgent, err := llmagent.New(llmagent.Config{
        Name:        "capital_agent",
        Model:       model,
        Description: "Agent to find the capital city of a country.",
        Instruction: "I can answer your questions about the capital city of a country.",
        Tools:       []tool.Tool{capitalTool},
    })
    if err != nil {
        log.Fatalf("Failed to create agent: %v", err)
    }

    config := &launcher.Config{
        AgentLoader: agent.NewSingleLoader(geoAgent),
    }

    l := full.NewLauncher()
    err = l.Execute(ctx, config, os.Args[1:])
    if err != nil {
        log.Fatalf("run failed: %v\n\n%s", err, l.CommandLineSyntax())
    }
}
```

#### 運作方式

1. adkgo 工具將您的 main.go 編譯為 Linux 的靜態連結二進位檔。
2. 它產生一個 Dockerfile，將此二進位檔複製到一個最小容器中。
3. 它使用 gcloud 建置並將此容器部署到 Cloud Run。
4. 部署後，它啟動一個本地代理，安全地連接到您的新服務。

確保您已通過 Google Cloud 驗證 (`gcloud auth login` 和 `gcloud config set project <your-project-id>`)。

#### 設定環境變數

可選但建議：設定環境變數可以讓部署指令更簡潔。

```
# Set your Google Cloud Project ID
# 設定您的 Google Cloud 專案 ID
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

# Set your desired Google Cloud Location
# 設定您想要的 Google Cloud 位置
export GOOGLE_CLOUD_LOCATION="us-central1"

# Set the path to your agent's main Go file
# 設定您的代理主要 Go 檔案的路徑
export AGENT_PATH="./examples/go/cloud-run/main.go"

# Set a name for your Cloud Run service
# 設定您的 Cloud Run 服務名稱
export SERVICE_NAME="capital-agent-service"
```

#### 指令用法

```
./adkgo deploy cloudrun \
    -p $GOOGLE_CLOUD_PROJECT \
    -r $GOOGLE_CLOUD_LOCATION \
    -s $SERVICE_NAME \
    --proxy_port=8081 \
    --server_port=8080 \
    -e $AGENT_PATH \
    --a2a --api --webui
```

##### 必填

* `-p, --project_name`: 您的 Google Cloud 專案 ID (例如 $GOOGLE_CLOUD_PROJECT)。
* `-r, --region`: 部署的 Google Cloud 位置 (例如 $GOOGLE_CLOUD_LOCATION, us-central1)。
* `-s, --service_name`: Cloud Run 服務的名稱 (例如 $SERVICE_NAME)。
* `-e, --entry_point_path`: 包含您代理原始碼的主要 Go 檔案路徑 (例如 $AGENT_PATH)。

##### 可選

* `--proxy_port`: 驗證代理監聽的本地連接埠。預設為 8081。
* `--server_port`: 伺服器在 Cloud Run 容器內監聽的連接埠號。預設為 8080。
* `--a2a`: 如果包含此項，則啟用 Agent2Agent 通訊。預設啟用。
* `--a2a_agent_url`: 公開代理卡中廣告的 A2A 代理卡 URL。此旗標僅在與 --a2a 旗標一起使用時有效。
* `--api`: 如果包含此項，則部署 ADK API 伺服器。預設啟用。
* `--webui`: 如果包含此項，則在代理 API 伺服器旁邊部署 ADK 開發者 UI。預設啟用。
* `--temp_dir`: 建置成品的暫存目錄。預設為 os.TempDir()。
* `--help`: 顯示說明訊息並退出。

##### 經過驗證的存取

服務預設使用 --no-allow-unauthenticated 部署。

成功執行後，該指令將您的代理部署到 Cloud Run，並提供一個本地 URL 以透過代理存取服務。
</details>

<details>
<summary>Java - gcloud CLI</summary>


### gcloud CLI for Java

您可以使用標準 `gcloud run deploy` 指令與 `Dockerfile` 部署 Java 代理。這是目前將 Java 代理部署到 Google Cloud Run 的推薦方式。

確保您已通過 Google Cloud [驗證](https://cloud.google.com/docs/authentication/gcloud)。
具體來說，在終端機中執行指令 `gcloud auth login` 和 `gcloud config set project <your-project-id>`。

#### 專案結構

按如下方式組織您的專案檔案：

```txt
your-project-directory/
├── src/
│   └── main/
│       └── java/
│             └── agents/
│                 ├── capitalagent/
│                     └── CapitalAgent.java    # Your agent code (您的代理程式碼)
├── pom.xml                                    # Java adk and adk-dev dependencies (Java adk 和 adk-dev 相依性)
└── Dockerfile                                 # Container build instructions (容器建置說明)
```

在您的專案目錄根目錄中建立 `pom.xml` 和 `Dockerfile`。您的代理程式碼檔案 (`CapitalAgent.java`) 位於如上所示的目錄中。

#### 程式碼檔案

1. 這是我們的代理定義。這與 [LLM 代理](../agents/llm-agents.md) 中的程式碼相同，但有兩個注意事項：

     * 代理現在初始化為 **全域公開靜態常數變數 (global public static final variable)**。

     * 代理的定義可以在靜態方法中公開，也可以在宣告期間內聯。

    請參閱 [examples](https://github.com/google/adk-docs/blob/main/examples/java/cloud-run/src/main/java/agents/capitalagent/CapitalAgent.java) 儲存庫中的 `CapitalAgent` 範例程式碼。

2. 將以下相依性和外掛程式新增至 pom.xml 檔案。

    ```xml title="pom.xml"
    <dependencies>
        <dependency>
            <groupId>com.google.adk</groupId>
            <artifactId>google-adk</artifactId>
            <version>0.1.0</version>
        </dependency>
        <dependency>
            <groupId>com.google.adk</groupId>
            <artifactId>google-adk-dev</artifactId>
            <version>0.1.0</version>
        </dependency>
    </dependencies>

    <plugin>
        <groupId>org.codehaus.mojo</groupId>
        <artifactId>exec-maven-plugin</artifactId>
        <version>3.2.0</version>
        <configuration>
        <mainClass>com.google.adk.web.AdkWebServer</mainClass>
        <classpathScope>compile</classpathScope>
        </configuration>
    </plugin>
    ```

3.  定義容器映像：

    ```dockerfile title="Dockerfile"
    # Use an official Maven image with a JDK. Choose a version appropriate for your project.
    FROM maven:3.8-openjdk-17 AS builder

    WORKDIR /app

    COPY pom.xml .
    RUN mvn dependency:go-offline -B

    COPY src ./src

    # Expose the port your application will listen on.
    # Cloud Run will set the PORT environment variable, which your app should use.
    EXPOSE 8080

    # The command to run your application.
    # Use a shell so ${PORT} expands and quote exec.args so agent source-dir is passed correctly.
    ENTRYPOINT ["sh", "-c", "mvn compile exec:java \
        -Dexec.mainClass=com.google.adk.web.AdkWebServer \
        -Dexec.classpathScope=compile \
        -Dexec.args='--server.port=${PORT:-8080} --adk.agents.source-dir=target'"]
    ```

#### 使用 `gcloud` 部署

在終端機中導航到 `your-project-directory`。

```shell
gcloud run deploy capital-agent-service \
--source . \
--region $GOOGLE_CLOUD_LOCATION \
--project $GOOGLE_CLOUD_PROJECT \
--allow-unauthenticated \
--set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI"
# Add any other necessary environment variables your agent might need
# 新增您的代理可能需要的任何其他必要環境變數
```

* `capital-agent-service`: 您想要給予 Cloud Run 服務的名稱。
* `--source .`: 告訴 gcloud 從目前目錄中的 Dockerfile 建置容器映像。
* `--region`: 指定部署區域。
* `--project`: 指定 GCP 專案。
* `--allow-unauthenticated`: 允許公開存取服務。對於私人服務，請移除此旗標。
* `--set-env-vars`: 將必要的環境變數傳遞給執行中的容器。確保包含 ADK 和您的代理所需的所有變數 (如果不使用應用程式預設憑證，則如 API 金鑰)。

`gcloud` 將建置 Docker 映像，將其推送到 Google Artifact Registry，並部署到 Cloud Run。完成後，它將輸出您已部署服務的 URL。

有關部署選項的完整清單，請參閱 [`gcloud run deploy` 參考文件](https://cloud.google.com/sdk/gcloud/reference/run/deploy)。
</details>

## 測試您的代理

一旦您的代理部署到 Cloud Run，您可以透過已部署的 UI (如果已啟用) 與其互動，或者使用像 `curl` 這樣的工具直接與其 API 端點互動。您將需要部署後提供的服務 URL。

<details>
<summary>UI 測試</summary>

### UI 測試

如果您在啟用 UI 的情況下部署了代理：

*   **adk CLI:** 您在部署期間包含了 `--webui` 旗標。
*   **gcloud CLI:** 您在 `main.py` 中設定了 `SERVE_WEB_INTERFACE = True`。

您可以透過在瀏覽器中導航到部署後提供的 Cloud Run 服務 URL 來簡單地測試您的代理。

```
# Example URL format
# 範例 URL 格式
# https://your-service-name-abc123xyz.a.run.app
```

ADK 開發者 UI 允許您直接在瀏覽器中與您的代理互動、管理工作階段並檢視執行詳細資訊。

要驗證您的代理是否按預期運作，您可以：

1. 從下拉選單中選擇您的代理。
2. 輸入訊息並驗證您是否收到來自代理的預期回應。

如果您遇到任何非預期的行為，請檢查 [Cloud Run](https://console.cloud.google.com/run) 主控台記錄檔。

</details>

<details>
<summary>API 測試 (curl)</summary>


### API 測試 (curl)

您可以使用像 `curl` 這樣的工具與代理的 API 端點互動。這對於程式化互動或如果您在沒有 UI 的情況下部署非常有用。

您將需要部署後提供的服務 URL，如果您的服務未設定為允許未經身份驗證的存取，則可能需要身份驗證權杖。

#### 設定應用程式 URL

將範例 URL 替換為您已部署的 Cloud Run 服務的實際 URL。

```shell
export APP_URL="YOUR_CLOUD_RUN_SERVICE_URL"
# Example: export APP_URL="https://adk-default-service-name-abc123xyz.a.run.app"
# 範例：export APP_URL="https://adk-default-service-name-abc123xyz.a.run.app"
```

#### 取得身份驗證權杖 (如果需要)

如果您的服務需要身份驗證 (即，您未使用 `gcloud` 的 `--allow-unauthenticated` 或在 `adk` 提示中回答 'N')，請取得身份驗證權杖。

```
export TOKEN=$(gcloud auth print-identity-token)
```

*如果您的服務允許未經身份驗證的存取，您可以從下面的 `curl` 指令中省略 `-H "Authorization: Bearer $TOKEN"` 標頭。*

#### 列出可用的應用程式

驗證已部署的應用程式名稱。

```shell
curl -X GET -H "Authorization: Bearer $TOKEN" $APP_URL/list-apps
```

*(如果需要，請根據此輸出調整以下指令中的 `app_name`。預設通常是代理目錄名稱，例如 `capital_agent`)*。

#### 建立或更新工作階段

初始化或更新特定使用者和工作階段的狀態。如果不同，請將 `capital_agent` 替換為您的實際應用程式名稱。值 `user_123` 和 `session_abc` 是範例識別碼；您可以將它們替換為您想要的使用者和工作階段 ID。

```shell
curl -X POST -H "Authorization: Bearer $TOKEN" \
    $APP_URL/apps/capital_agent/users/user_123/sessions/session_abc \
    -H "Content-Type: application/json" \
    -d '{"preferred_language": "English", "visit_count": 5}'
```

#### 執行代理

發送提示給您的代理。將 `capital_agent` 替換為您的應用程式名稱，並根據需要調整使用者/工作階段 ID 和提示。

```shell
curl -X POST -H "Authorization: Bearer $TOKEN" \
    $APP_URL/run_sse \
    -H "Content-Type: application/json" \
    -d '{
    "app_name": "capital_agent",
    "user_id": "user_123",
    "session_id": "session_abc",
    "new_message": {
        "role": "user",
        "parts": [{
        "text": "加拿大的首都是什麼？"
        }]
        },
        "streaming": false
    }'
```

* 如果您想接收伺服器發送事件 (SSE)，請設定 `"streaming": true`。
* 回應將包含代理的執行事件，包括最終答案。
</details>
