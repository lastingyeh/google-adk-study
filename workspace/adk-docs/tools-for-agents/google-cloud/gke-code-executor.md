# ADK GKE 程式碼執行器 (GkeCodeExecutor)

> 🔔 `更新日期：2026-01-26`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/google-cloud/gke-code-executor/

[`ADK 支援`: `Python v1.14.0`]

GKE 程式碼執行器 (`GkeCodeExecutor`) 透過利用 GKE (Google Kubernetes Engine) Sandbox 環境（使用 gVisor 進行工作負載隔離），提供了一種安全且可擴展的方法來運行 LLM 生成的程式碼。對於每個程式碼執行請求，它會動態創建一個具有強化 Pod 配置的臨時、沙箱化 Kubernetes Job。您應該在安全性和隔離性至關重要的 GKE 生產環境中使用此執行器。

## 運作原理

當發出執行程式碼的請求時，`GkeCodeExecutor` 會執行以下步驟：

1.  **創建 ConfigMap：** 創建一個 Kubernetes ConfigMap 來存儲需要執行的 Python 程式碼。
2.  **創建沙箱化 Pod：** 創建一個新的 Kubernetes Job，進而創建一個具有強化安全上下文並啟用 gVisor 運行時的 Pod。來自 ConfigMap 的程式碼會被掛載到此 Pod 中。
3.  **執行程式碼：** 程式碼在沙箱化 Pod 內執行，與底層節點和其他工作負載隔離。
4.  **獲取結果：** 從 Pod 的日誌中擷取執行的標準輸出 (stdout) 和錯誤流 (stderr)。
5.  **清理資源：** 執行完成後，Job 和關聯的 ConfigMap 會被自動刪除，確保不留任何痕跡。

## 主要優勢

*   **增強安全性：** 程式碼在具有內核級隔離的 gVisor 沙箱環境中執行。
*   **臨時環境：** 每次程式碼執行都在其專屬的臨時 Pod 中運行，以防止執行之間的狀態轉移。
*   **資源控制：** 您可以為執行 Pod 配置 CPU 和記憶體限制，以防止資源濫用。
*   **可擴展性：** 允許您並行運行大量程式碼執行，由 GKE 處理底層節點的調度和擴展。

## 系統需求

若要使用 GKE 程式碼執行器工具成功部署您的 ADK 專案，必須滿足以下需求：

- 具有 **啟用 gVisor 的節點池** 的 GKE 叢集。
- 代理 (Agent) 的服務帳戶 (Service Account) 需要特定的 **RBAC 權限**，允許其：
    - 為每個執行請求創建、觀察和刪除 **Jobs**。
    - 管理 **ConfigMaps** 以將程式碼注入 Job 的 Pod。
    - 列出 **Pods** 並讀取其 **日誌** 以獲取執行結果。
- 安裝帶有 GKE 額外組件的客戶端函式庫：`pip install google-adk[gke]`

有關完整、開箱即用的配置，請參閱 [deployment_rbac.yaml](https://github.com/google/adk-python/blob/main/contributing/samples/gke_agent_sandbox/deployment_rbac.yaml) 範例。有關將 ADK 工作流部署到 GKE 的更多信息，請參閱 [部署到 Google Kubernetes Engine (GKE)](../../deployment/gke.md)。

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.agents import LlmAgent
from google.adk.code_executors import GkeCodeExecutor

# 初始化執行器，目標設定為其 ServiceAccount 擁有必要 RBAC 權限的命名空間。
# 此範例還設置了自定義超時和資源限制。
gke_executor = GkeCodeExecutor(
    namespace="agent-sandbox",
    timeout_seconds=600,
    cpu_limit="1000m",  # 1 CPU 核心
    mem_limit="1Gi",
)

# 代理現在對其生成的任何程式碼使用此執行器。
gke_agent = LlmAgent(
    name="gke_coding_agent",
    model="gemini-2.0-flash",
    instruction="您是一個編寫並執行 Python 程式碼的實用 AI 代理。",
    code_executor=gke_executor,
)
```

</details>

## 配置參數

`GkeCodeExecutor` 可以使用以下參數進行配置：

| 參數 | 類型 | 描述 |
| -------------------- | ------ | --------------------------------------------------------------------------------------- |
| `namespace`          | `str`  | 將在其中創建執行 Job 的 Kubernetes 命名空間。預設為 `"default"`。 |
| `image`              | `str`  | 用於執行 Pod 的容器映像檔。預設為 `"python:3.11-slim"`。 |
| `timeout_seconds`    | `int`  | 程式碼執行的超時時間（秒）。預設為 `300`。 |
| `cpu_requested`      | `str`  | 為執行 Pod 請求的 CPU 數量。預設為 `"200m"`。 |
| `mem_requested`      | `str`  | 為執行 Pod 請求的記憶體量。預設為 `"256Mi"`。 |
| `cpu_limit`          | `str`  | 執行 Pod 可以使用的最大 CPU 數量。預設為 `"500m"`。 |
| `mem_limit`          | `str`  | 執行 Pod 可以使用的最大記憶體量。預設為 `"512Mi"`。 |
| `kubeconfig_path`    | `str`  | 用於身份驗證的 kubeconfig 文件路徑。若未提供則回退到叢集內配置或預設本地 kubeconfig。 |
| `kubeconfig_context` | `str`  | 要使用的 `kubeconfig` 上下文。 |
