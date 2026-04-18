# ADK 的 Vertex AI Search 工具

> 🔔 `更新日期：2026-03-09`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/vertex-ai-search/

[`ADK 支援`: `Python v0.1.0`]

`vertex_ai_search_tool` 使用 Google Cloud Vertex AI Search，讓代理程式（agent）能夠在您私有的、已配置的資料儲存庫（例如內部文件、公司政策、知識庫）中進行搜尋。這個內建工具需要您在配置期間提供特定的資料儲存庫 ID。有關該工具的進一步細節，請參閱 [瞭解 Vertex AI Search 落地 (grounding)](../../grounding/grounding/vertex_ai_search_grounding.md)。

> [!WARNING] 警告：每個代理程式僅限單一工具
此工具在代理程式實例中只能***單獨使用***。
有關此限制及其解決辦法的更多資訊，請參閱 [ADK 工具的限制](../../custom-tools/limitations.md#每個代理一個工具的限制)。

```py
import asyncio

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.tools import VertexAiSearchTool

# 請替換為您的 Vertex AI Search 資料儲存庫路徑，以及對應的區域（例如 us-central1 或 global）。
# 格式：projects/<PROJECT_ID>/locations/<REGION>/collections/default_collection/dataStores/<DATASTORE_ID>
DATASTORE_PATH = "DATASTORE_PATH_HERE"

# 常數設定
APP_NAME_VSEARCH = "vertex_search_app"
USER_ID_VSEARCH = "user_vsearch_1"
SESSION_ID_VSEARCH = "session_vsearch_1"
AGENT_NAME_VSEARCH = "doc_qa_agent"
GEMINI_2_FLASH = "gemini-2.0-flash"

# 工具實例化
# 您必須在此處提供您的資料儲存庫路徑。
vertex_search_tool = VertexAiSearchTool(data_store_id=DATASTORE_PATH)

# 代理程式定義
doc_qa_agent = LlmAgent(
    name=AGENT_NAME_VSEARCH,
    model=GEMINI_2_FLASH, # 需要使用 Gemini 模型
    tools=[vertex_search_tool],
    instruction=f"""你是一個得力的助手，負責根據文件儲存庫中的資訊回答問題：{DATASTORE_PATH}。
    在回答之前，請使用搜尋工具查找相關資訊。
    如果答案不在文件中，請說明您找不到該資訊。
    """,
    description="使用特定的 Vertex AI Search 資料儲存庫回答問題。",
)

# 會話與執行器設定
session_service_vsearch = InMemorySessionService()
runner_vsearch = Runner(
    agent=doc_qa_agent, app_name=APP_NAME_VSEARCH, session_service=session_service_vsearch
)
session_vsearch = session_service_vsearch.create_session(
    app_name=APP_NAME_VSEARCH, user_id=USER_ID_VSEARCH, session_id=SESSION_ID_VSEARCH
)

# 代理程式互動函式
async def call_vsearch_agent_async(query):
    print("\n--- 正在執行 Vertex AI Search 代理程式 ---")
    print(f"查詢內容: {query}")
    if "DATASTORE_PATH_HERE" in DATASTORE_PATH:
        print("跳過執行：請將 DATASTORE_PATH_HERE 替換為您實際的資料儲存庫路徑。")
        print("-" * 30)
        return

    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "未收到回應。"
    try:
        async for event in runner_vsearch.run_async(
            user_id=USER_ID_VSEARCH, session_id=SESSION_ID_VSEARCH, new_message=content
        ):
            # 就像 Google 搜尋一樣，結果通常會嵌入在模型的回答中。
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text = event.content.parts[0].text.strip()
                print(f"代理程式回應: {final_response_text}")
                # 您可以檢查 event.grounding_metadata 以獲取來源引用
                if event.grounding_metadata:
                    print(f"  (找到落地元數據，包含 {len(event.grounding_metadata.grounding_attributions)} 個引用)")

    except Exception as e:
        print(f"發生錯誤: {e}")
        print("請確保您的資料儲存庫 ID 正確，且服務帳戶具有相應權限。")
    print("-" * 30)

# --- 執行範例 ---
async def run_vsearch_example():
    # 請替換為與您的資料儲存庫內容相關的問題
    await call_vsearch_agent_async("總結關於第二季度戰略文件的主要觀點。")
    await call_vsearch_agent_async("實驗室 X 提到了哪些安全程序？")

# 執行範例
# await run_vsearch_example()

# 由於多個 await 可能導致 Colab 的 asyncio 問題，因此在本地運行
try:
    asyncio.run(run_vsearch_example())
except RuntimeError as e:
    if "cannot be called from a running event loop" in str(e):
        print("在執行中的事件迴圈（如 Colab/Jupyter）中跳過執行。請在本地執行。")
    else:
        raise e
```
