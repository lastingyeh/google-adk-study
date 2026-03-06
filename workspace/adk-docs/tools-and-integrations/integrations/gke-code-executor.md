# 適用於 ADK 的 Google Cloud GKE 代碼執行器 (Code Executor) 工具

> 🔔 `更新日期：2026-03-06`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/gke-code-executor/

[`ADK 支援`: `Python v1.14.0`]

GKE 代碼執行器 (`GkeCodeExecutor`) 透過利用 Google Kubernetes Engine (GKE) 提供了一種安全且可擴展的方法來執行 LLM 生成的代碼。對於安全性、隔離性至關重要的 GKE 生產環境，您應該使用此執行器。它支援兩種執行模式：

1. **沙盒模式 (Sandbox Mode) (建議使用)：** 利用 [Agent Sandbox](https://github.com/kubernetes-sigs/agent-sandbox) 客戶端，在根據模板按需建立的沙盒實例中執行代碼。此模式透過使用 [預熱沙盒 (pre-warmed sandboxes)](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox#create_a_sandboxtemplate_and_sandboxwarmpool) 提供較低的延遲，並支援與沙盒環境更直接的互動。
2. **任務模式 (Job Mode)：** 使用帶有 gVisor 的 GKE Sandbox 環境來進行工作負載隔離。對於每個代碼執行請求，它都會動態建立一個具有強化 Pod 配置的臨時、沙盒化 Kubernetes Job。此模式是為了向後相容而提供的。

## 執行模式

### 沙盒模式 (`executor_type="sandbox"`)

這是建議使用的模式。它使用 `k8s-agent-sandbox` 客戶端程式庫與 GKE 叢集中的 Agent Sandbox 進行通訊並建立沙盒。當收到執行代碼的請求時，它會執行以下步驟：

1. 使用指定的模板建立 `SandboxClaim`。
2. 等待沙盒實例準備就緒。
3. 在索取的沙盒中執行代碼。
4. 獲取標準輸出和錯誤。
5. 刪除 `SandboxClaim`，這將進而清理沙盒實例。

此方法比任務模式更快，因為它利用了預熱沙盒並優化了 Agent Sandbox 控制器提供的啟動時間。

**主要優勢：**

除了任務模式的所有優點外，沙盒模式還提供以下功能：

- **較低延遲：** 旨在減少與建立完整 Kubernetes Job 相比的啟動時間。
- **託管環境：** 利用 Agent Sandbox 框架進行沙盒生命週期管理。

**先決條件：**

- GKE 叢集中現有的 Agent Sandbox 部署，包括沙盒控制器及其擴充功能（例如：sandbox claim controller 和 sandbox warmpool controller）、路由器、閘道器以及相關的 `SandboxTemplate` 資源（例如：`python-sandbox-template`）。
- ADK 代理建立和刪除 `SandboxClaim` 資源所需的 RBAC 權限。

### 任務模式 (`executor_type="job"`)

此模式是為了向後相容而提供的。當收到執行代碼的請求時，`GkeCodeExecutor` 會執行以下步驟：

1. **建立 ConfigMap：** 建立一個 Kubernetes ConfigMap 來存儲需要執行的 Python 代碼。
1. **建立沙盒化 Pod：** 建立一個新的 Kubernetes Job，進而建立一個具有強化安全上下文並啟用 gVisor 運行時的 Pod。來自 ConfigMap 的代碼會掛載到此 Pod 中。
1. **執行代碼：** 代碼在沙盒化的 Pod 中執行，與底層節點和其他工作負載隔離。
1. **獲取結果：** 從 Pod 的日誌中捕獲執行的標準輸出和錯誤流。
1. **清理資源：** 執行完成後，Job 和相關的 ConfigMap 會自動刪除，確保不留下任何殘留物。

**主要優勢：**

- **增強的安全性：** 代碼在具有核心級隔離的 gVisor 沙盒環境中執行。
- **臨時環境：** 每次代碼執行都在其專屬的臨時 Pod 中運行，以防止執行之間的狀態轉移。
- **資源控制：** 您可以為執行 Pod 配置 CPU 和記憶體限制，以防止資源濫用。
- **可擴展性：** 允許平行運行大量代碼執行，由 GKE 處理底層節點的調度與擴展。
- **最低限度的設置：** 依賴標準的 GKE 功能和 gVisor。

## 系統需求

必須滿足以下要求才能成功部署帶有 GKE 代碼執行器工具的 ADK 專案：

- 具有 **啟用 gVisor 的節點池** 的 GKE 叢集（任務模式的預設映像檔和典型的 Agent Sandbox 模板都需要）。
- 代理的服務帳號需要特定的 **RBAC 權限**：
  - **任務模式：** 建立、觀察和刪除 **Jobs**；管理 **ConfigMaps**；列出 **Pods** 並讀取其 **日誌**。如需任務模式完整且開箱即用的配置，請參閱 [deployment_rbac.yaml](https://github.com/google/adk-python/blob/main/contributing/samples/gke_agent_sandbox/deployment_rbac.yaml) 範例。
  - **沙盒模式：** 在部署 Agent Sandbox 的命名空間內具有建立、獲取、觀察和刪除 **SandboxClaim** 和 **Sandbox** 資源的權限。
- 安裝帶有適當額外組件的客戶端程式庫：`pip install google-adk[gke]`

## 配置參數

`GkeCodeExecutor` 可以配置以下參數：

| 參數 | 類型 | 描述 |
| ---------------------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `namespace` | `str` | 將建立執行資源（Jobs 或 SandboxClaims）的 Kubernetes 命名空間。預設為 `"default"`。 |
| `executor_type` | `Literal["job", "sandbox"]` | 指定執行模式。預設為 `"job"`。 |
| `image` | `str` | (任務模式) 用於執行 Pod 的容器映像檔。預設為 `"python:3.11-slim"`。 |
| `timeout_seconds` | `int` | (任務模式) 代碼執行的逾時時間（以秒為單位）。預設為 `300`。 |
| `cpu_requested` | `str` | (任務模式) 為執行 Pod 請求的 CPU 量。預設為 `"200m"`。 |
| `mem_requested` | `str` | (任務模式) 為執行 Pod 請求的記憶體量。預設為 `"256Mi"`。 |
| `cpu_limit` | `str` | (任務模式) 執行 Pod 可以使用的最大 CPU 量。預設為 `"500m"`。 |
| `mem_limit` | `str` | (任務模式) 執行 Pod 可以使用的最大記憶體量。預設為 `"512Mi"`。 |
| `kubeconfig_path` | `str` | 用於身份驗證的 kubeconfig 文件路徑。若未指定，則退而使用叢集內配置或預設的本地 kubeconfig。 |
| `kubeconfig_context` | `str` | 要使用的 `kubeconfig` 上下文。 |
| `sandbox_gateway_name` | `str \| None` | (沙盒模式) 要使用的沙盒閘道器名稱。選填。 |
| `sandbox_template` | `str \| None` | (沙盒模式) 要使用的 `SandboxTemplate` 名稱。預設為 `"python-sandbox-template"`。 |

## Python 使用範例

### 沙盒模式 **(建議使用)**
```python
from google.adk.agents import LlmAgent
from google.adk.code_executors import GkeCodeExecutor
from google.adk.code_executors import CodeExecutionInput
from google.adk.agents.invocation_context import InvocationContext

# 為沙盒模式初始化執行器
# 命名空間應具有 SandboxClaims 和 Sandbox 的 RBAC 權限
gke_sandbox_executor = GkeCodeExecutor(
    namespace="agent-sandbox-system",  # 通常是安裝 agent-sandbox 的地方
    executor_type="sandbox",
    sandbox_template="python-sandbox-template",
    sandbox_gateway_name="your-gateway-name", # 選填
)

# 直接執行範例：
ctx = InvocationContext()
result = gke_sandbox_executor.execute_code(ctx, CodeExecutionInput(code="print('Hello from Sandbox Mode')"))
print(result.stdout)

# 搭配代理程式的範例：
gke_sandbox_agent = LlmAgent(
    name="gke_sandbox_coding_agent",
    model="gemini-2.5-flash",
    instruction="你是一個樂於助人的 AI 代理，負責撰寫並使用沙盒執行 Python 代碼。",
    code_executor=gke_sandbox_executor,
)
```
---
### 任務模式
```python
from google.adk.agents import LlmAgent
from google.adk.code_executors import GkeCodeExecutor
from google.adk.code_executors import CodeExecutionInput
from google.adk.agents.invocation_context import InvocationContext

# 為任務模式初始化執行器
# 命名空間應具有 Jobs、ConfigMaps、Pods、Logs 的 RBAC 權限
gke_executor = GkeCodeExecutor(
    namespace="agent-ns",
    executor_type="job",
    timeout_seconds=600,
    cpu_limit="1000m",  # 1 個 CPU 核心
    mem_limit="1Gi",
)

# 直接執行範例：
ctx = InvocationContext()
result = gke_executor.execute_code(ctx, CodeExecutionInput(code="print('Hello from Job Mode')"))
print(result.stdout)

# 搭配代理程式的範例：
gke_agent = LlmAgent(
    name="gke_coding_agent",
    model="gemini-2.5-flash",
    instruction="你是一個樂於助人的 AI 代理，負責撰寫並執行 Python 代碼。",
    code_executor=gke_executor,
)
```
