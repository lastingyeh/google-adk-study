<div style="text-align: center;">
  <div class="centered-logo-text-group">
    <img src="https://google.github.io/adk-docs/assets/agent-development-kit.png" alt="Agent Development Kit Logo" width="100">
    <h1>Agent Development Kit</h1>
  </div>
</div>

> 🔔 `更新日期：2026-01-23`
>
> 🔗 `資料來源：https://google.github.io/adk-docs/`

Agent Development Kit (ADK) 是一個靈活且模組化的架構，用於**開發和部署 AI 代理 (AI agents)**。雖然針對 Gemini 和 Google 生態系統進行了優化，但 ADK 是**模型無關 (model-agnostic)**、**部署無關 (deployment-agnostic)**，並且是為了**與其他框架的相容性**而構建的。ADK 旨在讓代理開發感覺更像軟體開發，使開發人員更輕鬆地創建、部署和編排代理架構，涵蓋從簡單任務到複雜工作流的範圍。

---

### 快速入門

| 語言 | 安裝指令 / 依賴 | 文件連結 |
|---|---|---|
| Python | `pip install google-adk` | [開始使用 (Python)](./get-started/python.md) |
| TypeScript | `npm install @google/adk` | [開始使用 (TypeScript)](./get-started/typescript.md) |
| Go | `go get google.golang.org/adk` | [開始使用 (Go)](./get-started/go.md) |
| Java | [參考](#Java-依賴) | [開始使用 (Java)](./get-started/java.md) |

---

## 了解更多

[觀看「Agent Development Kit 簡介」！](https://www.youtube.com/watch?v=zgrOwow_uTQ)

| 功能 | 重點 | 參考連結 |
|---|---|---|
| 靈活的編排 (Flexible Orchestration) | 使用工作流代理（`Sequential`、`Parallel`、`Loop`）或 LLM 驅動動態路由（`LlmAgent`） | [了解代理](agents/index.md) |
| 多代理架構 (Multi-Agent Architecture) | 層次化組合專業代理以實現模組化與擴展性 | [探索多代理系統](agents/multi-agents.md) |
| 豐富的工具生態系統 (Rich Tool Ecosystem) | 預建工具、客製函式與第三方整合；代理亦可作為工具 | [瀏覽工具](tools/index.md) |
| 部署就緒 (Deployment Ready) | 容器化並可於本地、Vertex AI、Cloud Run 等部署 | [部署代理](deploy/index.md) |
| 內建評估 (Built-in Evaluation) | 使用預定義測試案例評估回應質量與執行軌跡 | [評估代理](evaluate/index.md) |
| 構建安全可靠的代理 (Building Safe and Secure Agents) | 在設計中實施安全模式與最佳實踐 | [安全與防護](safety/index.md) |

---
### 更多參考
#### Java 依賴
`pom.xml` 中加入以下依賴：
```xml
<dependency>
    <groupId>com.google.adk</groupId>
    <artifactId>google-adk</artifactId>
    <version>0.5.0</version>
</dependency>
```
---
`build.gradle` 中加入以下依賴：
```groovy
dependencies {
    implementation 'com.google.adk:google-adk:0.5.0'
}
```