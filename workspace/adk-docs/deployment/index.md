# 部署您的 Agent

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/deploy/

一旦您使用 ADK 構建並測試了您的 Agent，下一步就是將其部署，以便在生產環境中存取、查詢和使用，或與其他應用程式整合。部署將您的 Agent 從本機開發機器移動到可擴展且可靠的環境中。

<img src="https://google.github.io/adk-docs/assets/deploy-agent.png" alt="部署您的 Agent">

## 部署選項

根據您對生產就緒性或自定義靈活性的需求，您的 ADK Agent 可以部署到各種不同的環境中：
| 部署選項 | 說明 | 相關連結 |
|---|---|---|
| Vertex AI Agent Engine | Google Cloud 上完全託管的自動擴展服務，專為部署、管理和擴展使用 ADK 等框架構建的 AI Agent 而設計。 | [了解更多](./agent-engine/index.md) |
| Cloud Run | Google Cloud 上的託管自動擴展運算平台，使您能夠以基於容器的應用程式形式運行您的 Agent。 | [了解更多](./cloud-run.md) |
| Google Kubernetes Engine (GKE) | Google Cloud 的託管 Kubernetes 服務，適合需要更多部署控制或運行開放模型的情境。 | [了解更多](./gke.md) |
| 其他容器友好基礎設施 | 可手動將 Agent 打包到容器映像，並在 Docker、Podman 或其他支援容器的環境中運行。適合離線或無 Google Cloud 連線需求。 | 無 |

請按照 [將您的 Agent 部署到 Cloud Run](./cloud-run.md#deployment-commands) 的說明進行操作。
在 gcloud CLI 的「部署指令 (Deployment Commands)」部分，您將找到 FastAPI 進入點和 Dockerfile 的範例。
