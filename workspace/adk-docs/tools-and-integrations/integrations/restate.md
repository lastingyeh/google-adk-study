# ADK 的 Restate 外掛程式

> 🔔 `更新日期：2026-03-09`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/restate/

[`ADK 支援`: `Python`]

[Restate](https://restate.dev) 是一個持續性的執行引擎，可將 ADK 代理轉變為天生具備彈性且強大的系統。它提供持久化會話（sessions）、人工作業審核的暫停/恢復、具彈性的多代理編排、安全版本控制，以及對每次執行的全面觀測與控制。所有的 LLM 調用和工具執行都會被記錄（journaled），因此如果發生任何故障，您的代理可以從上次中斷的地方準確恢復。

## 使用場景

Restate 外掛程式賦予您的代理以下能力：

- **持續性執行 (Durable execution)**：永不遺失進度。如果您的代理崩潰，它會自動重試並從上次中斷的地點準確恢復。
- **人機協作的暫停/恢復 (Pause/resume for human-in-the-loop)**：暫停執行數天或數週直到人工核准，然後從中斷處恢復。
- **持續性狀態 (Durable state)**：代理記憶和對話歷史記錄透過內建的會話管理，在重啟後依然存在。
- **觀測性與任務控制 (Observability & Task control)**：查看代理執行的確切操作，並隨時終止、暫停及恢復代理執行。
- **具彈性的多代理編排 (Resilient multi-agent orchestration)**：跨多個代理運行具備平行執行能力的彈性工作流。
- **安全版本控制 (Safe versioning)**：透過不可變部署（immutable deployments）部署新版本，而不影響正在進行的執行任務。

## 前置作業

- Python 3.12+
- [Gemini API 金鑰](https://aistudio.google.com/app/api-keys)

若要執行下方的範例，您還需要：

- [uv](https://docs.astral.sh/uv/) (Python 套件管理器)
- [Docker](https://docs.docker.com/get-docker/) (或用於 Restate 伺服器的 [Brew/npm/binary](https://docs.restate.dev/develop/local_dev#running-restate-server--cli-locally))

## 安裝

安裝 Python 版的 Restate SDK：

```bash
# 使用 pip 安裝支援序列化功能的 restate-sdk
pip install "restate-sdk[serde]"
```

## 與代理搭配使用

按照以下步驟運行持續性代理，並在 Restate UI 中檢查其執行日誌（journal）：

1. **複製 [restate-google-adk-example 儲存庫](https://github.com/restatedev/restate-google-adk-example) 並導航至範例目錄**

   ```bash
   # 複製專案儲存庫
   git clone https://github.com/restatedev/restate-google-adk-example.git
   # 切換到 hello-world 範例目錄
   cd restate-google-adk-example/examples/hello-world
   ```
2. **匯出您的 Gemini API 金鑰**

   ```bash
   # 設定 Google API 金鑰環境變數
   export GOOGLE_API_KEY=your-api-key
   ```

3. **啟動天氣代理 (weather agent)**

   ```bash
   # 使用 uv 執行當前目錄的專案
   uv run .
   ```

4. **在另一個終端機啟動 Restate**

   ```bash
   # 使用 Docker 啟動 Restate 伺服器
   docker run --name restate --rm -p 8080:8080 -p 9070:9070 -d \
     --add-host host.docker.internal:host-gateway \
     docker.restate.dev/restatedev/restate:latest
   ```

   其他安裝方式：[Brew, npm, 二進制檔下載](https://docs.restate.dev/develop/local_dev#running-restate-server--cli-locally)

5. **註冊代理**

   打開 Restate UI (`localhost:9070`) 並註冊您的代理部署（例如：`http://host.docker.internal:9080`）：

   ![restate-registration](https://google.github.io/adk-docs/integrations/assets/restate-registration.png)

   > [!TIP] 安全版本控制
   Restate 將每次部署註冊為不可變快照。當您部署新版本時，正在進行的執行任務會在原始部署上完成，而新的請求則會路由到最新版本。了解更多關於 [版本感知的路由 (version-aware routing)](https://docs.restate.dev/services/versioning)。

6. **向代理發送請求**

   在 Restate UI 中，選擇 **WeatherAgent**，開啟 **Playground**，然後發送請求：

   ![restate-request](https://google.github.io/adk-docs/integrations/assets/restate-request.png)

   > [!TIP]持續性會話與重試
   此請求會經過 Restate，Restate 會在轉發給您的代理之前將其持久化。每個會話（此處為 `session-1`）都是隔離的、有狀態的且持續性的。如果代理在執行中途崩潰，Restate 會自動重試並從最後一個記錄的步驟恢復，不會遺失進度。

7. **檢查執行日誌**

   點擊 **Invocations** 頁籤，然後點擊您的調用以查看執行日誌（execution journal）：

   ![restate-journal](https://google.github.io/adk-docs/integrations/assets/restate-journal.png)

   > [!TIP]對代理執行的全面控制
   每一次 LLM 調用和工具執行都會記錄在日誌中。從 UI 介面，您可以暫停、恢復、從任何中間步驟重新啟動，或終止執行。查看 **State** 頁籤以檢查代理當前的會話數據。

## 能力 (Capabilities)

Restate 外掛程式為您的 ADK 代理提供以下能力：

| 能力                     | 描述                                                                                          |
| ------------------------ | --------------------------------------------------------------------------------------------- |
| 持續性工具執行             | 使用 `restate_object_context().run_typed()` 包裝工具邏輯，使其能夠自動重試與恢復              |
| 人工參與 (Human-in-the-loop) | 使用 `restate_object_context().awakeable()` 暫停執行，直到收到外部信號（例如：人工核准）       |
| 持久化會話               | `RestateSessionService()` 可持久化儲存代理記憶與對話狀態                                      |
| 持續性 LLM 調用            | `RestatePlugin()` 記錄 LLM 調用並具備自動重試功能                                            |
| 多代理通訊               | 使用 `restate_object_context().service_call()` 進行持續性的跨代理 HTTP 調用                     |
| 平行執行                 | 使用 `restate.gather()` 同時執行工具與代理，以進行確定性的恢復                                |

## 額外資源

- [Restate ADK 範例儲存庫](https://github.com/restatedev/restate-google-adk-example) - 可運行的範例，包含具備人工核准的理賠處理
- [Restate ADK 教學](https://docs.restate.dev/tour/google-adk) - 使用 Restate 和 ADK 開發代理的逐步導覽
- [Restate AI 文件](https://docs.restate.dev/ai) - 持續性 AI 代理模式的完整參考
- [PyPI 上的 Restate SDK](https://pypi.org/project/restate-sdk/) - Python 套件
