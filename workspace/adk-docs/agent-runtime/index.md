# 代理運行時 (Agent Runtime)
🔔 `更新日期：2026-01-22`

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

ADK 提供多種在開發期間運行和測試代理的方法。請選擇最適合您開發工作流程的方法。

## 運行代理的方法

- **開發者介面 (Dev UI)**

    ---

    使用 `adk web` 啟動基於瀏覽器的介面，以便與您的代理進行互動。

    → [使用網頁介面](web-interface.md)

- **命令列 (Command Line)**

    ---

    使用 `adk run` 直接在終端機中與您的代理進行互動。

    → [使用命令列](command-line.md)

- **API 伺服器 (API Server)**

    ---

    使用 `adk api_server` 透過 RESTful API 公開您的代理。

    → [使用 API 伺服器](api-server.md)

## 技術參考

如需有關運行時配置和行為的更深入資訊，請參閱以下頁面：

- **[事件迴圈 (Event Loop)](event-loop.md)**：了解驅動 ADK 的核心事件迴圈，包括 yield/pause/resume 週期。
- **[恢復代理 (Resume Agents)](resume.md)**：了解如何從先前的狀態恢復代理執行。
- **[運行配置 (Runtime Config)](runconfig.md)**：使用 RunConfig 配置運行時行為。
