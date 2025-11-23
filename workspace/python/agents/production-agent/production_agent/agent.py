"""
展示部署策略的生產環境部署代理 (Production deployment agent)。

此代理展示了生產環境部署的最佳實踐，包括：
- FastAPI 伺服器整合
- 環境設定
- 健康檢查 (Health checks)
- 監控模式 (Monitoring patterns)
"""

from google.adk.agents import Agent
from google.genai import types


def check_deployment_status() -> dict:
    """
    檢查部署狀態與健康狀況。

    Returns:
        Dict: 包含部署狀態資訊的字典
    """
    # 回傳模擬的健康檢查與狀態報告
    return {
        "status": "success",
        "report": "Deployment health check successful", # 部署健康檢查成功
        "deployment_type": "production",
        "features": [
            "FastAPI server",        # FastAPI 伺服器
            "Cloud Run deployment",  # Cloud Run 部署
            "Agent Engine deployment", # Agent Engine 部署
            "GKE deployment",        # GKE 部署
            "Health checks",         # 健康檢查
            "Monitoring"             # 監控
        ]
    }


def get_deployment_options() -> dict:
    """
    取得可用的部署選項。

    Returns:
        Dict: 包含部署選項與描述的字典
    """
    # 定義並回傳各種部署環境的詳細資訊
    return {
        "status": "success",
        "report": "Available deployment options retrieved", # 已取得可用的部署選項
        "options": {
            "local_api_server": {
                "command": "adk api_server",
                "description": "Start local FastAPI server for development", # 啟動用於開發的本地 FastAPI 伺服器
                "features": ["Hot reload", "API docs", "CORS enabled"] # 熱重載、API 文件、啟用 CORS
            },
            "cloud_run": {
                "command": "adk deploy cloud_run",
                "description": "Deploy to serverless Cloud Run", # 部署至無伺服器 Cloud Run
                "features": ["Auto-scaling", "Managed infrastructure", "Pay per use"] # 自動擴展、託管基礎設施、按使用量付費
            },
            "agent_engine": {
                "command": "adk deploy agent_engine",
                "description": "Deploy to Vertex AI Agent Engine", # 部署至 Vertex AI Agent Engine
                "features": ["Managed agents", "Built-in monitoring", "Version control"] # 託管代理、內建監控、版本控制
            },
            "gke": {
                "command": "adk deploy gke",
                "description": "Deploy to Google Kubernetes Engine", # 部署至 Google Kubernetes Engine
                "features": ["Full control", "Custom scaling", "Advanced networking"] # 完全控制、自定義擴展、進階網路功能
            }
        }
    }


def get_best_practices() -> dict:
    """
    取得生產環境部署最佳實踐。

    Returns:
        Dict: 包含生產環境部署最佳實踐的字典
    """
    # 提供安全性、監控、可擴展性和可靠性的建議
    return {
        "status": "success",
        "report": "Production best practices retrieved", # 已取得生產環境最佳實踐
        "best_practices": {
            "security": [ # 安全性
                "Use Google Secret Manager for secrets", # 使用 Google Secret Manager 管理機密
                "Never commit API keys or credentials", # 絕不提交 API 金鑰或憑證
                "Enable CORS with specific origins only", # 僅對特定來源啟用 CORS
                "Implement rate limiting" # 實作速率限制
            ],
            "monitoring": [ # 監控
                "Implement health check endpoints", # 實作健康檢查端點
                "Use structured logging (JSON format)", # 使用結構化日誌 (JSON 格式)
                "Enable Cloud Trace for observability", # 啟用 Cloud Trace 進行可觀測性
                "Track error rates and response times" # 追蹤錯誤率和回應時間
            ],
            "scalability": [ # 可擴展性
                "Configure auto-scaling appropriately", # 適當設定自動擴展
                "Set min and max instance counts", # 設定最小和最大實例數
                "Optimize memory and CPU limits", # 最佳化記憶體和 CPU 限制
                "Use connection pooling" # 使用連線池
            ],
            "reliability": [ # 可靠性
                "Implement graceful shutdown", # 實作優雅關機 (Graceful shutdown)
                "Add readiness and liveness probes", # 新增就緒 (readiness) 和存活 (liveness) 探針
                "Use circuit breakers for external calls", # 對外部呼叫使用斷路器 (Circuit breakers)
                "Configure retries with exponential backoff" # 設定指數退避 (Exponential backoff) 重試機制
            ]
        }
    }


# 建立生產環境部署代理
root_agent = Agent(
    name="production_deployment_agent",
    model="gemini-2.0-flash",
    description="生產環境部署專家，為 ADK 代理提供部署策略、最佳實踐和基礎設施模式的指導。",
    instruction="""
    你是 ADK 代理生產環境部署的專家。你協助使用者了解：

    1. **部署選項 (Deployment Options)**：
    - 使用 FastAPI 的本地 API 伺服器 (Local API server)
    - 使用 Cloud Run 的無伺服器部署 (Serverless deployment)
    - 使用 Agent Engine 的託管部署 (Managed deployment)
    - 使用 GKE 的自定義 Kubernetes 部署 (Custom Kubernetes deployment)

    2. **最佳實踐 (Best Practices)**：
    - 安全性 (Security)：密鑰管理、驗證、跨來源資源共用 (CORS)
    - 監控 (Monitoring)：健康檢查、日誌記錄、追蹤
    - 可擴展性 (Scalability)：自動擴展、資源限制
    - 可靠性 (Reliability)：錯誤處理、重試機制、故障轉移

    3. **指令 (Commands)**：
    - `adk api_server`：啟動本地 FastAPI 伺服器
    - `adk deploy cloud_run`：部署至 Cloud Run
    - `adk deploy agent_engine`：部署至 Agent Engine
    - `adk deploy gke`：部署至 GKE

    當使用者詢問關於部署的問題時：
    - 根據他們的需求推薦最合適的部署選項
    - 提供具體的指令和設定範例
    - 強調重要的考量因素（成本、複雜度、可擴展性）
    - 分享相關的最佳實踐

    請務實，提供可運作的範例，並專注於生產就緒 (production-ready) 的模式。
    """.strip(),
    tools=[
        check_deployment_status,
        get_deployment_options,
        get_best_practices
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.5,
        max_output_tokens=2048
    )
)

"""
重點摘要:
- **核心概念**: 生產環境部署代理，用於指導使用者進行正確的部署決策
- **關鍵技術**:
    - Google ADK Agent 框架
    - Gemini 2.0 Flash 模型
    - 工具整合 (Tools integration)
- **重要結論**:
    - 提供了三種主要工具：檢查狀態、獲取部署選項、獲取最佳實踐
    - 涵蓋了本地開發到雲端部署 (Cloud Run, GKE, Agent Engine) 的完整路徑
    - 強調了安全性、監控、可擴展性和可靠性的重要性
- **行動項目**:
    - 使用者可透過此代理查詢特定情境下的部署建議
    - 代理可提供具體的 `adk` 指令來執行部署
"""
