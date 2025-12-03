"""
重點摘要
- 核心概念：使用 Streamlit 建構的資料分析助手，整合 ADK 和程式碼執行功能。
- 關鍵技術：Streamlit, Google ADK, Pandas, AsyncIO, Multi-agent System.
- 重要結論：提供兩種模式（程式碼執行與直接對話），實現靈活的資料分析與視覺化。
- 行動項目：
    1. 初始化 Gemini Client 和 ADK Runner。
    2. 處理檔案上傳與資料預覽。
    3. 管理聊天與互動邏輯。

Data Analysis Assistant with Streamlit + ADK + Code Execution
Pure Python integration - interactive data analysis with dynamic visualization
資料分析助理：Streamlit + ADK + 程式碼執行
純 Python 整合 - 具備動態視覺化的互動式資料分析
"""

import asyncio
import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai.types import Content, Part, GenerateContentConfig
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# 匯入代理 (Import agents)
from data_analysis_agent import root_agent
from data_analysis_agent.visualization_agent import visualization_agent

# 載入環境變數 (Load environment variables)
load_dotenv()

# 設定頁面 (Configure page)
st.set_page_config(
    page_title="資料分析助理",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 初始化 Gemini 用戶端（用於舊版聊天支援）
# Initialize Gemini client (for legacy chat support)
@st.cache_resource
def get_client():
    """
    初始化並快取 Gemini 用戶端。
    Initialize and cache Gemini client.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("❌ 請設定 GOOGLE_API_KEY 環境變數")
        st.info("1. 複製 `.env.example` 到 `.env`")
        st.info("2. 從 https://makersuite.google.com/app/apikey 新增您的 Google API 金鑰")
        st.info("3. 重啟應用程式")
        st.stop()

    return genai.Client(
        api_key=api_key,
        http_options={'api_version': 'v1alpha'}
    )


# 初始化 ADK 執行器
# Initialize ADK runner
@st.cache_resource
def get_runner():
    """
    初始化並快取具備多代理系統的 ADK 執行器。
    Initialize and cache ADK runner with multi-agent system.
    """
    session_service = InMemorySessionService()
    # 建立 Runner 實例，綁定 root_agent
    return Runner(
        agent=root_agent,
        app_name="data_analysis_assistant",
        session_service=session_service,
    ), session_service


# 初始化視覺化執行器（繞過多代理路由以便直接傳遞資料）
# Initialize visualization runner (bypasses multi-agent routing for direct data passing)
@st.cache_resource
def get_visualization_runner():
    """
    初始化並快取用於直接資料傳遞的視覺化執行器。
    Initialize and cache visualization runner for direct data passing.
    """
    session_service = InMemorySessionService()
    # 建立 Runner 實例，綁定 visualization_agent
    return Runner(
        agent=visualization_agent,
        app_name="visualization_assistant",
        session_service=session_service,
    ), session_service


# 取得執行器與 Session 服務
runner, session_service = get_runner()
viz_runner, viz_session_service = get_visualization_runner()

# 初始化 Session 狀態 (Initialize session state)
if "messages" not in st.session_state:
    st.session_state.messages = []

if "dataframe" not in st.session_state:
    st.session_state.dataframe = None

if "file_name" not in st.session_state:
    st.session_state.file_name = None

if "adk_session_id" not in st.session_state:
    # 延遲建立 ADK Session ID - 將在首次使用執行器時建立
    # Create ADK session ID lazily - will be created on first runner use
    # 使用 async create_session 避免棄用警告
    async def init_adk_session():
        adk_session = await session_service.create_session(
            app_name="data_analysis_assistant",
            user_id="streamlit_user"
        )
        return adk_session.id

    st.session_state.adk_session_id = asyncio.run(init_adk_session())

if "viz_session_id" not in st.session_state:
    # 使用 async 方法建立視覺化 Session
    # Create visualization session using async method
    async def init_viz_session():
        viz_session = await viz_session_service.create_session(
            app_name="visualization_assistant",
            user_id="streamlit_user"
        )
        return viz_session.id

    st.session_state.viz_session_id = asyncio.run(init_viz_session())

if "use_code_execution" not in st.session_state:
    st.session_state.use_code_execution = False  # 預設為 False 以保持穩定性 (Default to False for stability)


# 標題 (Header)
st.title("📊 資料分析助理")
st.markdown("上傳 CSV 檔案並要求我進行分析或生成視覺化圖表！")

# 側邊欄用於檔案上傳與設定 (Sidebar for file upload and settings)
with st.sidebar:
    st.header("📁 上傳資料")
    uploaded_file = st.file_uploader(
        "選擇 CSV 檔案",
        type=["csv"],
        help="上傳要分析的 CSV 檔案",
    )

    if uploaded_file is not None:
        try:
            # 讀取 CSV 檔案
            df = pd.read_csv(uploaded_file)
            st.session_state.dataframe = df
            st.session_state.file_name = uploaded_file.name

            st.success(f"✅ 已載入: {uploaded_file.name}")

            # 顯示資料資訊 (Display data info)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("列數 (Rows)", df.shape[0])
            with col2:
                st.metric("欄數 (Columns)", df.shape[1])

            # 顯示資料預覽 (Show data preview)
            with st.expander("📋 資料預覽"):
                st.dataframe(df.head(10), width='stretch')

            # 顯示資料資訊詳情 (Show data info details)
            with st.expander("ℹ️ 資料資訊"):
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("欄位名稱與類型")
                    info_df = pd.DataFrame({
                        "欄位": df.columns,
                        "類型": [str(dtype) for dtype in df.dtypes],
                        "非空值數": df.count(),
                    })
                    st.dataframe(info_df, width='stretch')

                with col2:
                    st.subheader("基本統計")
                    st.dataframe(df.describe(), width='stretch')

            st.subheader("⚙️ 功能")
            st.session_state.use_code_execution = st.checkbox(
                "🔧 使用程式碼執行進行視覺化 (Beta)",
                value=False,
                help="啟用使用 AI 的動態視覺化生成 (BuiltInCodeExecutor) - 仍處於 Beta 階段"
            )

            # 建議分析 (Suggest analyses)
            st.markdown("---")
            st.subheader("💡 建議分析")
            suggestions = [
                "📈 分析主要欄位的見解",
                "🔗 尋找變數之間的關聯性",
                "🎯 識別離群值與異常",
                "📊 建立關鍵指標的視覺化",
            ]
            for suggestion in suggestions:
                st.write(f"• {suggestion}")

            # 清除資料按鈕 (Clear data button)
            if st.button("🗑️ 清除資料"):
                st.session_state.dataframe = None
                st.session_state.file_name = None
                st.session_state.messages = []
                st.rerun()

        except Exception as e:
            st.error(f"❌ 載入檔案錯誤: {str(e)}")

# 主聊天介面 (Main chat interface)
st.markdown("---")
st.subheader("💬 與您的資料對話")

# 顯示聊天訊息 (Display chat messages)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # 如果存在視覺化內容則顯示
        if "visualization" in message:
            if message["visualization"]["type"] == "base64_image":
                st.image(f"data:image/png;base64,{message['visualization']['data']}")
            elif message["visualization"]["type"] == "html":
                st.html(message["visualization"]["data"])

# 聊天輸入 (Chat input)
if prompt := st.chat_input(
    "詢問有關您資料的問題或請求視覺化..." if st.session_state.dataframe is not None
    else "📁 請先上傳 CSV 檔案",
    disabled=st.session_state.dataframe is None,
):
    # 新增使用者訊息 (Add user message)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # 準備資料集相關上下文 (Prepare context about dataset)
    context = ""
    df_csv = ""
    if st.session_state.dataframe is not None:
        df = st.session_state.dataframe
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()

        # 將 DataFrame 轉換為 CSV 以供程式碼執行 (Convert DataFrame to CSV for code execution)
        df_csv = df.to_csv(index=False)

        context = f"""
        **資料集資訊：**
        - 檔案：{st.session_state.file_name}
        - 形狀：{df.shape[0]} 列 × {df.shape[1]} 欄
        - 欄位：{', '.join(df.columns.tolist())}
        - 數值欄位：{', '.join(numeric_cols) if numeric_cols else '無'}
        - 分類欄位：{', '.join(categorical_cols) if categorical_cols else '無'}

        **可用於視覺化的資料：**
        使用者的資料集以 CSV 格式提供如下。請使用以下方式載入：
        ```python
        import pandas as pd
        from io import StringIO
        df = pd.read_csv(StringIO(csv_data))
        ```

        CSV 資料 (前 50 列)：
        {df.head(50).to_csv(index=False)}

        使用者可以透過要求特定的圖表類型來請求視覺化。"""
    else:
        context = "尚未上傳資料集。請先要求使用者上傳 CSV 檔案。"

    # 選擇路由：程式碼執行或直接對話 (Choose routing: code execution or direct chat)
    if st.session_state.use_code_execution:
        # 使用 ADK 多代理系統與程式碼執行 (Use ADK multi-agent system with code execution)
        with st.chat_message("assistant"):
            response_text = ""  # 在 try 區塊前初始化以避免範圍問題

            try:
                # 準備給代理的完整上下文訊息 (Prepare full context message for the agent)
                context_message = f"""{context}

User Question: {prompt}"""

                # 建立包含完整上下文的 ADK 訊息 (Create ADK message with full context)
                message = Content(
                    role="user",
                    parts=[Part.from_text(text=context_message)]
                )

                # 顯示處理狀態與詳細步驟 (Show process status with detailed steps)
                with st.status("🔍 正在處理您的請求...", expanded=False) as status:
                    try:
                        # 步驟 1: 準備 (Step 1: Prepare)
                        status.write("📋 正在準備上下文與資料...")

                        # 步驟 2: 執行 (Step 2: Execute)
                        status.write("⚙️ 正在執行分析...")

                        # 直接使用視覺化執行器以確保 CSV 資料到達代理
                        async def collect_events():
                            """收集並處理來自代理執行的所有事件。"""
                            response_parts = ""
                            has_visualization = False
                            visualization_data = []

                            # 非同步執行並收集事件
                            async for event in viz_runner.run_async(
                                user_id="streamlit_user",
                                session_id=st.session_state.viz_session_id,
                                new_message=message
                            ):
                                # 檢查事件中的內容
                                if event.content and event.content.parts:
                                    for part in event.content.parts:
                                        # 處理內嵌資料（視覺化/圖片）
                                        if hasattr(part, 'inline_data') and part.inline_data:
                                            has_visualization = True
                                            visualization_data.append(part.inline_data)
                                            response_parts += "\n📊 已生成視覺化圖表\n"

                                        # 處理可執行程式碼生成
                                        if part.executable_code:
                                            # 程式碼由視覺化代理生成
                                            pass

                                        # 處理程式碼執行結果
                                        if part.code_execution_result:
                                            # 程式碼執行成功
                                            if part.code_execution_result.outcome == "SUCCESS":
                                                pass  # 結果可能在 inline_data 中

                                        # 處理文字回應（如果已找到 inline_data 則不略過）
                                        if part.text and not part.text.isspace():
                                            response_parts += part.text

                            return response_parts, has_visualization, visualization_data

                        # 執行非同步收集 (Run async collection)
                        response_text, has_viz, viz_data = asyncio.run(collect_events())

                        # 步驟 3: 渲染 (Step 3: Render)
                        if has_viz:
                            status.write("📊 正在渲染視覺化圖表...")

                        # 完成 (Complete)
                        status.update(label="✅ 分析完成！", state="complete", expanded=False)

                    except Exception as status_error:
                        status.update(label="❌ 處理過程發生錯誤", state="error", expanded=True)
                        raise status_error

                # 顯示最終回應 (Display final response)
                if response_text:
                    st.markdown(response_text)
                else:
                    st.markdown("✓ 請求已成功處理")
                    response_text = "✓ 分析與視覺化完成"

                # 顯示任何視覺化內容 (Display any visualizations)
                if has_viz and viz_data:
                    for viz in viz_data:
                        try:
                            # 處理來自視覺化代理的 inline_data
                            if hasattr(viz, 'data'):
                                import base64
                                from io import BytesIO
                                from PIL import Image

                                # viz.data 可能是 bytes 或 base64 字串
                                if isinstance(viz.data, str):
                                    # Base64 編碼
                                    image_bytes = base64.b64decode(viz.data)
                                else:
                                    # 已經是 bytes
                                    image_bytes = viz.data

                                image = Image.open(BytesIO(image_bytes))
                                st.image(image, width='stretch')
                        except Exception as e:
                            st.warning(f"⚠️ 無法顯示視覺化: {str(e)}")

            except Exception as e:
                error_msg = f"❌ 程式碼執行發生錯誤: {str(e)}"
                with st.status("❌ 處理失敗", state="error", expanded=True):
                    st.error(error_msg)
                response_text = error_msg

            # 將回應新增至歷史記錄 (Add response to history)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text if response_text else "✓ 已處理"
            })

    else:
        # 直接使用 Gemini API 獲得更快速的回應（舊版模式）
        # Use direct Gemini API for faster response (legacy mode)
        with st.chat_message("assistant"):
            full_response = ""

            try:
                client = get_client()

                system_instruction = f"""
                你是一位專業的資料分析助理，協助使用者理解他們的資料集。

                {context}

                你的職責：
                - 協助使用者徹底了解他們的資料
                - 根據資料集的上下文進行分析
                - 提供清晰、可行的見解
                - 建議有趣的模式和關聯性
                - 保持簡潔但內容豐富
                - 使用 Markdown 格式以提高可讀性

                始終根據提供的實際資料做出回應。"""

                with st.status("💬 正在生成見解...", expanded=False) as status:
                    try:
                        status.write("📨 正在準備分析請求...")

                        response = client.models.generate_content_stream(
                            model="gemini-2.0-flash",
                            contents=[
                                Content(role="user", parts=[Part.from_text(text=prompt)])
                            ],
                            config=GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.7,
                                max_output_tokens=2048,
                            ),
                        )

                        status.write("🔍 正在分析資料...")

                        # 串流回應 (Stream response)
                        for chunk in response:
                            if chunk.text:
                                full_response += chunk.text

                        status.write("✨ 正在渲染結果...")
                        status.update(label="✅ 分析完成！", state="complete", expanded=False)

                    except Exception as status_error:
                        status.update(label="❌ 分析過程發生錯誤", state="error", expanded=True)
                        raise status_error

                # 最終訊息 (Final message)
                st.markdown(full_response)

            except Exception as e:
                error_msg = f"❌ 生成回應時發生錯誤: {str(e)}"
                with st.status("❌ 分析失敗", state="error", expanded=True):
                    st.error(error_msg)
                full_response = error_msg

            # 將回應新增至歷史記錄 (Add response to history)
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })

# 頁尾 (Footer)
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.caption("📚 由 Google Gemini 2.0 Flash 驅動")

with col2:
    st.caption("🐼 使用 Pandas 進行資料分析")

with col3:
    st.caption("🔧 ADK 程式碼執行")

with col4:
    st.caption("💬 互動式聊天")

# 在展開器中顯示實用提示 (Display helpful tips in expander)
with st.expander("💡 提示與技巧"):
    st.markdown("""
    **開始使用：**
    1. 使用側邊欄上傳 CSV 檔案
    2. 切換「使用程式碼執行進行視覺化」以獲得動態圖表
    3. 檢視資料預覽與統計數據
    4. 詢問有關您資料的問題

    **使用程式碼執行的範例問題（視覺化）：**
    - "建立各地區銷售額的長條圖"
    - "顯示價格的直方圖"
    - "繪製收入與數量的散佈圖"
    - "生成關聯性熱圖"
    - "視覺化客戶年齡的分佈"

    **用於分析的範例問題：**
    - "這份資料的關鍵見解是什麼？"
    - "顯示銷售額與利潤之間的關聯性"
    - "收入欄位中的前 5 個數值是什麼？"
    - "有任何不尋常的模式或離群值嗎？"
    - "總結此資料集的主要特徵"

    **了解模式：**
    - **程式碼執行模式**（推薦）：使用 ADK 的 BuiltInCodeExecutor 動態生成視覺化
    - **直接模式**：直接使用 Gemini API 獲得更快速的分析回應

    **程式碼執行功能：**
    - 使用 Python (matplotlib, plotly) 動態生成視覺化
    - 多代理系統：分析代理 + 視覺化代理
    - 代理推理出哪種視覺化最具洞察力
    - 資料在執行環境中以 'df' 形式可用"""
    )
