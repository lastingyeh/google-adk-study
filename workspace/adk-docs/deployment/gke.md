# 部署到 Google Kubernetes Engine (GKE)

[GKE](https://cloud.google.com/gke) 是 Google Cloud 託管的 Kubernetes 服務。它允許您使用 Kubernetes 部署和管理容器化應用程式。

要部署您的代理，您需要在 GKE 上運行 Kubernetes 叢集。您可以使用 Google Cloud Console 或 `gcloud` 命令列工具建立叢集。

在此範例中，我們將部署一個簡單的代理到 GKE。該代理將是一個使用 `Gemini 2.0 Flash` 作為 LLM 的 FastAPI 應用程式。我們可以使用環境變數 `GOOGLE_GENAI_USE_VERTEXAI` 來使用 Vertex AI 或 AI Studio 作為 LLM 提供者。

## 環境變數

按照 [設定和安裝](../get-started/installation/) 指南中的說明設定您的環境變數。您還需要安裝 `kubectl` 命令列工具。您可以在 [Google Kubernetes Engine 文件](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl) 中找到相關說明。

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id # 您的 GCP 專案 ID
export GOOGLE_CLOUD_LOCATION=us-central1 # 或者您偏好的位置
export GOOGLE_GENAI_USE_VERTEXAI=true # 如果使用 Vertex AI，請設為 true
export GOOGLE_CLOUD_PROJECT_NUMBER=$(gcloud projects describe --format json $GOOGLE_CLOUD_PROJECT | jq -r ".projectNumber")
```

如果您沒有安裝 `jq`，可以使用以下命令獲取專案編號：

```bash
gcloud projects describe $GOOGLE_CLOUD_PROJECT
```

並從輸出中複製專案編號。

```bash
export GOOGLE_CLOUD_PROJECT_NUMBER=YOUR_PROJECT_NUMBER
```

## 啟用 API 和權限

確保您已通過 Google Cloud 驗證（`gcloud auth login` 和 `gcloud config set project <your-project-id>`）。

啟用您的專案所需的 API。您可以使用 `gcloud` 命令列工具執行此操作。

```bash
gcloud services enable \
    container.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com
```

授予預設 Compute Engine 服務帳戶所需的角色，以便 `gcloud builds submit` 命令使用。

```bash
ROLES_TO_ASSIGN=(
    "roles/artifactregistry.writer"
    "roles/storage.objectViewer"
    "roles/logging.viewer"
    "roles/logging.logWriter"
)

for ROLE in "${ROLES_TO_ASSIGN[@]}"; do
    gcloud projects add-iam-policy-binding "${GOOGLE_CLOUD_PROJECT}" \
        --member="serviceAccount:${GOOGLE_CLOUD_PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
        --role="${ROLE}"
done
```

## 部署負載

當您將 ADK 代理工作流程部署到 Google Cloud GKE 時，
以下內容將上傳至服務：

- 您的 ADK 代理程式碼
- 您的 ADK 代理程式碼中宣告的任何依賴項
- 您的代理使用的 ADK API 伺服器程式碼版本

預設部署*不*包含 ADK 網頁使用者介面庫，
除非您將其指定為部署設定，例如 `adk deploy gke` 命令的 `--with_ui` 選項。

## 部署選項

您可以**使用 Kubernetes 資訊清單手動**或**使用 `adk deploy gke` 命令自動**將代理部署到 GKE。選擇最適合您工作流程的方法。

## 選項 1：使用 gcloud 和 kubectl 手動部署

### 建立 GKE 叢集

您可以使用 `gcloud` 命令列工具建立 GKE 叢集。此範例在 `us-central1` 區域建立一個名為 `adk-cluster` 的 Autopilot 叢集。

> 如果建立 GKE Standard 叢集，請確保已啟用 [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)。Workload Identity 在 Autopilot 叢集中預設啟用。

```bash
gcloud container clusters create-auto adk-cluster \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

建立叢集後，您需要使用 `kubectl` 連接到它。此命令配置 `kubectl` 以使用新叢集的憑證。

```bash
gcloud container clusters get-credentials adk-cluster \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

### 建立您的代理

我們將參考 [LLM 代理](https://google.github.io/adk-docs/agents/llm-agents/) 頁面上定義的 `capital_agent` 範例。

若要繼續，請按如下方式組織您的專案檔案：

```txt
your-project-directory/
├── capital_agent/
│   ├── __init__.py
│   └── agent.py       # 您的代理程式碼（請參閱下方的「Capital Agent 範例」）
├── main.py            # FastAPI 應用程式進入點
├── requirements.txt   # Python 依賴項
└── Dockerfile         # 容器建置說明
```

### 程式碼檔案

在 `your-project-directory/` 的根目錄中建立以下檔案（`main.py`、`requirements.txt`、`Dockerfile`、`capital_agent/agent.py`、`capital_agent/__init__.py`）。

1. 這是 `capital_agent` 目錄中的 Capital Agent 範例

   `agent.py`

    ```python title="capital_agent/agent.py"
    from google.adk.agents import LlmAgent

    # 定義工具函式
    def get_capital_city(country: str) -> str:
      """檢索給定國家的首都。"""
      # 替換為實際邏輯（例如 API 呼叫、資料庫查詢）
      capitals = {"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
      return capitals.get(country.lower(), f"Sorry, I don't know the capital of {country}.")

    # 將工具新增至代理
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent", # 您的代理名稱
        description="Answers user questions about the capital city of a given country.",
        instruction="""You are an agent that provides the capital city of a country... (previous instruction text)""",
        tools=[get_capital_city] # 直接提供函式
    )

    # ADK 將會發現 root_agent 實例
    root_agent = capital_agent
    ```

    將您的目錄標記為 python 套件

    `__init__.py`
    ```python title="capital_agent/__init__.py"
    from . import agent
    ```

2. 此檔案使用 ADK 的 `get_fast_api_app()` 設定 FastAPI 應用程式：

    `main.py`

    ```python title="main.py"
    import os

    import uvicorn
    from fastapi import FastAPI
    from google.adk.cli.fast_api import get_fast_api_app

    # 獲取 main.py 所在的目錄
    AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
    # 範例工作階段服務 URI（例如 SQLite）
    # 注意：使用 'sqlite+aiosqlite' 而非 'sqlite'，因為 DatabaseSessionService 需要非同步驅動程式
    SESSION_SERVICE_URI = "sqlite+aiosqlite:///./sessions.db"
    # 範例允許的 CORS 來源
    ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
    # 如果您打算提供網頁介面，請設定 web=True，否則設為 False
    SERVE_WEB_INTERFACE = True

    # 呼叫函式以獲取 FastAPI 應用程式實例
    # 確保代理目錄名稱 ('capital_agent') 與您的代理資料夾相符
    app: FastAPI = get_fast_api_app(
        agents_dir=AGENT_DIR,
        session_service_uri=SESSION_SERVICE_URI,
        allow_origins=ALLOWED_ORIGINS,
        web=SERVE_WEB_INTERFACE,
    )

    # 如果需要，您可以在下方新增更多 FastAPI 路由或配置
    # 範例：
    # @app.get("/hello")
    # async def read_root():
    #     return {"Hello": "World"}

    if __name__ == "__main__":
        # 使用 Cloud Run 提供的 PORT 環境變數，預設為 8080
        uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    ```

    *注意：我們指定 `agent_dir` 為 `main.py` 所在的目錄，並使用 `os.environ.get("PORT", 8080)` 以相容 Cloud Run。*

3. 列出必要的 Python 套件：
4.
    `requirements.txt`
    ```txt title="requirements.txt"
    google-adk
    # 新增您的代理需要的任何其他依賴項
    ```

5. 定義容器映像：

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

### 建置容器映像

您需要建立一個 Google Artifact Registry 存放庫來儲存您的容器映像。您可以使用 `gcloud` 命令列工具執行此操作。

```bash
gcloud artifacts repositories create adk-repo \
    --repository-format=docker \
    --location=$GOOGLE_CLOUD_LOCATION \
    --description="ADK repository"
```

使用 `gcloud` 命令列工具建置容器映像。此範例建置映像並將其標記為 `adk-repo/adk-agent:latest`。

```bash
gcloud builds submit \
    --tag $GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-repo/adk-agent:latest \
    --project=$GOOGLE_CLOUD_PROJECT \
    .
```

驗證映像是否已建置並推送到 Artifact Registry：

```bash
gcloud artifacts docker images list \
  $GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-repo \
  --project=$GOOGLE_CLOUD_PROJECT
```

### 為 Vertex AI 配置 Kubernetes 服務帳戶

如果您的代理使用 Vertex AI，您需要建立具有必要權限的 Kubernetes 服務帳戶。此範例建立一個名為 `adk-agent-sa` 的服務帳戶，並將其綁定到 `Vertex AI User` 角色。

> 如果您使用的是 AI Studio 並透過 API 金鑰存取模型，則可以跳過此步驟。

```bash
kubectl create serviceaccount adk-agent-sa
```

```bash
gcloud projects add-iam-policy-binding projects/${GOOGLE_CLOUD_PROJECT} \
    --role=roles/aiplatform.user \
    --member=principal://iam.googleapis.com/projects/${GOOGLE_CLOUD_PROJECT_NUMBER}/locations/global/workloadIdentityPools/${GOOGLE_CLOUD_PROJECT}.svc.id.goog/subject/ns/default/sa/adk-agent-sa \
    --condition=None
```

### 建立 Kubernetes 資訊清單檔案

在您的專案目錄中建立名為 `deployment.yaml` 的 Kubernetes 部署資訊清單檔案。此檔案定義如何在 GKE 上部署您的應用程式。

`deployment.yaml`
```yaml title="deployment.yaml"
cat <<  EOF > deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adk-agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: adk-agent
  template:
    metadata:
      labels:
        app: adk-agent
    spec:
      serviceAccount: adk-agent-sa
      containers:
      - name: adk-agent
        imagePullPolicy: Always
        image: $GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-repo/adk-agent:latest
        resources:
          limits:
            memory: "128Mi"
            cpu: "500m"
            ephemeral-storage: "128Mi"
          requests:
            memory: "128Mi"
            cpu: "500m"
            ephemeral-storage: "128Mi"
        ports:
        - containerPort: 8080
        env:
          - name: PORT
            value: "8080"
          - name: GOOGLE_CLOUD_PROJECT
            value: $GOOGLE_CLOUD_PROJECT
          - name: GOOGLE_CLOUD_LOCATION
            value: $GOOGLE_CLOUD_LOCATION
          - name: GOOGLE_GENAI_USE_VERTEXAI
            value: "$GOOGLE_GENAI_USE_VERTEXAI"
          # 如果使用 AI Studio，請將 GOOGLE_GENAI_USE_VERTEXAI 設為 false 並設定以下內容：
          # - name: GOOGLE_API_KEY
          #   value: $GOOGLE_API_KEY
          # 新增您的代理可能需要的任何其他必要環境變數
---
apiVersion: v1
kind: Service
metadata:
  name: adk-agent
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 8080
  selector:
    app: adk-agent
EOF
```

### 部署應用程式

使用 `kubectl` 命令列工具部署應用程式。此命令將部署和服務資訊清單檔案套用到您的 GKE 叢集。

```bash
kubectl apply -f deployment.yaml
```

片刻之後，您可以使用以下命令檢查部署狀態：

```bash
kubectl get pods -l=app=adk-agent
```

此命令列出與您的部署關聯的 Pod。您應該會看到一個狀態為 `Running` 的 Pod。

一旦 Pod 正在運行，您可以使用以下命令檢查服務的狀態：

```bash
kubectl get service adk-agent
```

如果輸出顯示 `External IP`，則表示您的服務可從網際網路存取。分配外部 IP 可能需要幾分鐘時間。

您可以使用以下命令獲取服務的外部 IP 位址：

```bash
kubectl get svc adk-agent -o=jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

## 選項 2：使用 `adk deploy gke` 自動部署

ADK 提供了一個 CLI 命令來簡化 GKE 部署。這避免了手動建置映像、編寫 Kubernetes 資訊清單或推送到 Artifact Registry 的需求。

#### 先決條件

在開始之前，請確保您已完成以下設定：

1. **一個運作中的 GKE 叢集：** 您需要在 Google Cloud 上有一個活躍的 Kubernetes 叢集。

2. **所需的 CLI：**
    * **`gcloud` CLI：** 必須安裝、驗證並配置 Google Cloud CLI 以使用您的目標專案。執行 `gcloud auth login` 和 `gcloud config set project [YOUR_PROJECT_ID]`。
    * **kubectl：** 必須安裝 Kubernetes CLI 以將應用程式部署到您的叢集。

3. **已啟用的 Google Cloud API：** 確保您的 Google Cloud 專案中已啟用以下 API：
    * Kubernetes Engine API (`container.googleapis.com`)
    * Cloud Build API (`cloudbuild.googleapis.com`)
    * Container Registry API (`containerregistry.googleapis.com`)

4. **所需的 IAM 權限：** 執行命令的使用者或 Compute Engine 預設服務帳戶至少需要以下角色：

   * **Kubernetes Engine Developer** (`roles/container.developer`)：用於與 GKE 叢集互動。

   * **Storage Object Viewer** (`roles/storage.objectViewer`)：允許 Cloud Build 從 gcloud builds submit 上傳到的 Cloud Storage 儲存桶下載原始碼。

   * **Artifact Registry Create on Push Writer** (`roles/artifactregistry.createOnPushWriter`)：允許 Cloud Build 將建置的容器映像推送到 Artifact Registry。此角色還允許在第一次推送時如果需要，在 Artifact Registry 中即時建立特殊的 gcr.io 存放庫。

   * **Logs Writer**  (`roles/logging.logWriter`)：允許 Cloud Build 將建置記錄寫入 Cloud Logging。

### `deploy gke` 命令

該命令接受代理的路徑以及指定目標 GKE 叢集的參數。

#### 語法

```bash
adk deploy gke [OPTIONS] AGENT_PATH
```

### 參數與選項

| 參數 | 描述 | 必填 |
| -------- | ------- | ------  |
| AGENT_PATH  | 您的代理根目錄的本機檔案路徑。    | 是 |
| --project | 您的 GKE 叢集所在的 Google Cloud 專案 ID。     | 是 |
| --cluster_name   | 您的 GKE 叢集名稱。    | 是 |
| --region    | 您的叢集的 Google Cloud 區域（例如 us-central1）。    | 是 |
| --with_ui   | 部署代理的後端 API 和配套的前端使用者介面。    | 否 |
| --log_level   | 設定部署過程的記錄層級。選項：debug、info、warning、error。     | 否 |


### 運作方式
當您執行 `adk deploy gke` 命令時，ADK 會自動執行以下步驟：

- 容器化：它從您的代理原始碼建置 Docker 容器映像。

- 映像推送：它標記容器映像並將其推送到您專案的 Artifact Registry。

- 資訊清單生成：它動態生成必要的 Kubernetes 資訊清單檔案（`Deployment` 和 `Service`）。

- 叢集部署：它將這些資訊清單套用到您指定的 GKE 叢集，這會觸發以下操作：

`Deployment` 指示 GKE 從 Artifact Registry 拉取容器映像並在一個或多個 Pod 中執行它。

`Service` 為您的代理建立一個穩定的網路端點。預設情況下，這是一個 LoadBalancer 服務，它提供一個公用 IP 位址以將您的代理暴露給網際網路。


### 範例用法
這裡有一個將位於 `~/agents/multi_tool_agent/` 的代理部署到名為 test 的 GKE 叢集的實際範例。

```bash
adk deploy gke \
    --project myproject \
    --cluster_name test \
    --region us-central1 \
    --with_ui \
    --log_level info \
    ~/agents/multi_tool_agent/
```

### 驗證您的部署
如果您使用了 `adk deploy gke`，請使用 `kubectl` 驗證部署：

1. 檢查 Pod：確保您的代理 Pod 處於 Running 狀態。

```bash
kubectl get pods
```
您應該會看到類似 `adk-default-service-name-xxxx-xxxx ... 1/1 Running` 的輸出（在預設命名空間中）。

2. 尋找外部 IP：獲取您的代理服務的公用 IP 位址。

```bash
kubectl get service
NAME                       TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)        AGE
adk-default-service-name   LoadBalancer   34.118.228.70   34.63.153.253   80:32581/TCP   5d20h
```

我們可以導航到外部 IP 並透過 UI 與代理互動
![alt text](https://google.github.io/adk-docs/assets/agent-gke-deployment.png)

## 測試您的代理

一旦您的代理部署到 GKE，您可以透過部署的 UI（如果已啟用）或直接使用 `curl` 等工具與其 API 端點互動。您將需要部署後提供的服務 URL。

<details>
<summary>UI 測試</summary>

### UI 測試

如果您在啟用 UI 的情況下部署了代理：

您只需在網頁瀏覽器中導航到 kubernetes 服務 URL 即可測試您的代理。

ADK 開發者 UI 允許您直接在瀏覽器中與您的代理互動、管理工作階段並查看執行詳細資訊。

要驗證您的代理是否按預期工作，您可以：

1. 從下拉選單中選擇您的代理。
2. 輸入訊息並驗證您是否收到代理的預期回應。

如果您遇到任何意外行為，請使用以下命令檢查代理的 Pod 記錄：

```bash
kubectl logs -l app=adk-agent
```
</details>

<details>
<summary>API 測試 (curl)</summary>

### API 測試 (curl)

您可以使用 `curl` 等工具與代理的 API 端點互動。這對於程式化互動或在沒有 UI 的情況下部署很有用。

#### 設定應用程式 URL

將範例 URL 替換為您已部署的 Cloud Run 服務的實際 URL。

```bash
export APP_URL=$(kubectl get service adk-agent -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
```

#### 列出可用的應用程式

驗證已部署的應用程式名稱。

```bash
curl -X GET $APP_URL/list-apps
```

*（如果需要，請根據此輸出調整以下命令中的 `app_name`。預設通常是代理目錄名稱，例如 `capital_agent`）。*

#### 建立或更新工作階段

初始化或更新特定使用者和工作階段的狀態。如果不同，請將 `capital_agent` 替換為您的實際應用程式名稱。值 `user_123` 和 `session_abc` 是範例識別碼；您可以將它們替換為您想要的使用者和工作階段 ID。

```bash
curl -X POST \
    $APP_URL/apps/capital_agent/users/user_123/sessions/session_abc \
    -H "Content-Type: application/json" \
    -d '{"preferred_language": "English", "visit_count": 5}'
```

#### 執行代理

發送提示給您的代理。將 `capital_agent` 替換為您的應用程式名稱，並根據需要調整使用者/工作階段 ID 和提示。

```bash
curl -X POST $APP_URL/run_sse \
    -H "Content-Type: application/json" \
    -d '{
    "app_name": "capital_agent",
    "user_id": "user_123",
    "session_id": "session_abc",
    "new_message": {
        "role": "user",
        "parts": [{
        "text": "What is the capital of Canada?"
        }]
    },
    "streaming": false
    }'
```

* 如果您想接收伺服器發送事件 (SSE)，請設定 `"streaming": true`。
* 回應將包含代理的執行事件，包括最終答案。
</details>


## 疑難排解

這些是將代理部署到 GKE 時可能遇到的一些常見問題：

### `Gemini 2.0 Flash` 出現 403 Permission Denied

這通常表示 Kubernetes 服務帳戶沒有存取 Vertex AI API 的必要權限。確保您已建立服務帳戶並將其綁定到 `Vertex AI User` 角色，如 [為 Vertex AI 配置 Kubernetes 服務帳戶](#configure-kubernetes-service-account-for-vertex-ai) 部分所述。如果您使用的是 AI Studio，請確保您已在部署資訊清單中設定 `GOOGLE_API_KEY` 環境變數且其有效。

### 404 或未找到回應

這通常表示您的請求有誤。檢查應用程式記錄以診斷問題。

```bash

export POD_NAME=$(kubectl get pod -l app=adk-agent -o jsonpath='{.items[0].metadata.name}')
kubectl logs $POD_NAME
```

### 嘗試寫入唯讀資料庫

您可能會看到 UI 中沒有建立工作階段 ID，且代理不回應任何訊息。這通常是由於 SQLite 資料庫是唯讀的。如果您在本地執行代理，然後建立將 SQLite 資料庫複製到容器中的容器映像，就會發生這種情況。資料庫在容器中隨後變為唯讀。

```bash
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) attempt to write a readonly database
[SQL: UPDATE app_states SET state=?, update_time=CURRENT_TIMESTAMP WHERE app_states.app_name = ?]
```

要解決此問題，您可以：

在建置容器映像之前，從本機刪除 SQLite 資料庫檔案。這將在容器啟動時建立一個新的 SQLite 資料庫。

```bash
rm -f sessions.db
```

或者（推薦），您可以將 `.dockerignore` 檔案新增至您的專案目錄，以排除將 SQLite 資料庫複製到容器映像中。

```txt title=".dockerignore"
sessions.db
```

再次建置容器映像並部署應用程式。

### 串流記錄的權限不足 `ERROR: (gcloud.builds.submit)`

當您沒有足夠的權限串流建置記錄，或者您的 VPC-SC 安全性政策限制存取預設記錄儲存桶時，可能會發生此錯誤。

要檢查建置進度，請點擊錯誤訊息中提供的連結或導航到 Google Cloud Console 中的 Cloud Build 頁面。

您還可以使用 [建置容器映像](#建置容器映像) 部分下的命令驗證映像是否已建置並推送到 Artifact Registry。

### Live Api 不支援 Gemini-2.0-Flash

當為您已部署的代理使用 ADK 開發者 UI 時，文字聊天可以工作，但語音（例如點擊麥克風按鈕）失敗。您可能會在 Pod 記錄中看到 `websockets.exceptions.ConnectionClosedError`，表示您的模型「live api 不支援」。

發生此錯誤是因為代理配置了不支援 Gemini Live API 的模型（如範例中的 `gemini-2.0-flash`）。Live API 是音訊和視訊即時雙向串流所必需的。

## 清理

要刪除 GKE 叢集和所有關聯資源，請執行：

```bash
gcloud container clusters delete adk-cluster \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

要刪除 Artifact Registry 存放庫，請執行：

```bash
gcloud artifacts repositories delete adk-repo \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

如果您不再需要該專案，也可以刪除它。這將刪除與該專案關聯的所有資源，包括 GKE 叢集、Artifact Registry 存放庫以及您建立的任何其他資源。

```bash
gcloud projects delete $GOOGLE_CLOUD_PROJECT
