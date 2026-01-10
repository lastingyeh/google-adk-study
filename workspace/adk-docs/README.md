# Google ADK 文件學習指南

🔔 `更新日期：2026 年 1 月 10 日`

---
🪧 `以官方文件 (Google ADK Docs) 為基礎的學習資源`

✍️ `作者：Lastingyeh`

歡迎來到 Google ADK 官方文件學習指南！本指南旨在協助您快速了解和掌握 Google ADK（Application Development Kit）的核心概念與功能。無論您是初學者還是經驗豐富的開發者，都能在此找到適合您的資源和建議。

### 版本發行 (Release Notes)

您可以在各支援語言的程式碼儲存庫中找到發行說明。有關 ADK 發行版本的詳細資訊，請參閱以下位置：

- [ADK Python 發行說明](https://github.com/google/adk-python/releases) (v1.21.0)
- [ADK TypeScript 發行說明](https://github.com/google/adk-js/releases) (v0.2.1)
- [ADK Go 發行說明](https://github.com/google/adk-go/releases) (v0.3.0)
- [ADK Java 發行說明](https://github.com/google/adk-java/releases) (v0.5.0)

### 快速入門 (Get started)

ADK 文件提供了多種程式語言的快速入門指南，可協助您在幾分鐘內建立您的第一個 ADK 代理程式。請選擇最適合您的語言：

| 語言           | 描述                                               | 快速入門連結                                       | 安裝指南                                             |
| :------------- | :------------------------------------------------- | :------------------------------------------------- | :--------------------------------------------------- |
| **Python**     | 在幾分鐘內建立您的第一個 Python ADK 代理程式。     | [開始使用 Python](./get-started/python.md)         | [安裝說明](./get-started/Installation/python.md)     |
| **Go**         | 在幾分鐘內建立您的第一個 Go ADK 代理程式。         | [開始使用 Go](./get-started/go.md)                 | [安裝說明](./get-started/Installation/go.md)         |
| **Java**       | 在幾分鐘內建立您的第一個 Java ADK 代理程式。       | [開始使用 Java](./get-started/java.md)             | [安裝說明](./get-started/Installation/java.md)       |
| **TypeScript** | 在幾分鐘內建立您的第一個 TypeScript ADK 代理程式。 | [開始使用 TypeScript](./get-started/typescript.md) | [安裝說明](./get-started/Installation/typescript.md) |

### 會話與記憶 (Sessions & Memory)

| 標頭                                                         | 描述                                                     | 連結                                          |
| :----------------------------------------------------------- | :------------------------------------------------------- | :-------------------------------------------- |
| [對話上下文簡介](./sessions&memory/sessions.md)              | 簡介 `Session`、`State` 與 `Memory` 如何管理對話上下文。 | [連結](./sessions&memory/sessions.md)         |
| [會話 (Session) 概觀](./sessions&memory/session/overview.md) | 深入探討 `Session` 如何追蹤個別對話。                    | [連結](./sessions&memory/session/overview.md) |
| [會話倒回 (Rewind)](./sessions&memory/session/rewind.md)     | 說明如何將會話還原到之前的狀態。                         | [連結](./sessions&memory/session/rewind.md)   |
| [State](./sessions&memory/state.md)                          | 解釋 `State` 如何作為 `Session` 的暫存記事本。           | [連結](./sessions&memory/state.md)            |
| [記憶 (Memory)](./sessions&memory/memory.md)                 | 介紹如何利用 `MemoryService` 實現長期知識。              | [連結](./sessions&memory/memory.md)           |
| [Vertex AI 快速模式](./sessions&memory/express-mode.md)      | 說明如何使用 Vertex AI 會話與記憶的快速模式。            | [連結](./sessions&memory/express-mode.md)     |

### 代理執行 (Agent Runtime)

| 標頭                                                 | 描述                                                                                   | 連結                                  |
| :--------------------------------------------------- | :------------------------------------------------------------------------------------- | :------------------------------------ |
| [Runtime 總覽](./agent-runtime/index.md)             | 介紹 ADK Runtime 的核心概念，包括事件迴圈 (Event Loop) 以及各關鍵元件如何協同運作。    | [連結](./agent-runtime/index.md)      |
| [執行設定 (RunConfig)](./agent-runtime/runconfig.md) | 解釋如何使用 RunConfig 來定義代理的執行時行為，例如串流模式、語音設定和 LLM 呼叫限制。 | [連結](./agent-runtime/runconfig.md)  |
| [API 伺服器](./agent-runtime/api-server.md)          | 說明如何使用 ADK API 伺服器在本地環境中測試和除錯您的代理，並提供詳細的 API 端點參考。 | [連結](./agent-runtime/api-server.md) |
| [恢復中斷的代理](./agent-runtime/resume.md)          | 指導如何設定與使用恢復功能，讓因故中斷的代理工作流能從上次中斷的地方繼續執行。         | [連結](./agent-runtime/resume.md)     |

### 部署 (Deployment)

| 標頭                                                      | 描述                                                                              | 連結                                       |
| :-------------------------------------------------------- | :-------------------------------------------------------------------------------- | :----------------------------------------- |
| [部署總覽](./deployment/deploy.md)                        | 介紹如何將您的代理部署到各種環境，例如 Vertex AI Agent Engine、Cloud Run 或 GKE。 | [連結](./deployment/deploy.md)             |
| [部署至 Agent Engine](./deployment/agent-engine/index.md) | 說明如何將代理部署到 Google Cloud 上全託管、可自動擴展的 Agent Engine。           | [連結](./deployment/agent-engine/index.md) |
| [部署至 Cloud Run](./deployment/cloud-run.md)             | 指導您如何將代理以容器化應用程式的形式部署到 Cloud Run。                          | [連結](./deployment/cloud-run.md)          |
| [部署至 GKE](./deployment/gke.md)                         | 提供在 GKE 上部署代理的詳細步驟，適合需要更多控制權的場景。                       | [連結](./deployment/gke.md)                |




### 參考資源

- [Google ADK Docs](https://google.github.io/adk-docs/)
- [[code wiki] adk-python](https://codewiki.google/github.com/google/adk-python)
- [[code wiki] agent-starter-pack](https://codewiki.google/github.com/googlecloudplatform/agent-starter-pack)
- [Google AI Studio](https://aistudio.google.com/)
- [Gemini Live API](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api)

### 免責聲明

本文件僅為個人學習與教育目的而創建。其內容是基於個人在學習 Google ADK 過程中的理解與整理，並非 Google 的官方觀點或文件。所有資訊請以 Google 官方發布為準。
