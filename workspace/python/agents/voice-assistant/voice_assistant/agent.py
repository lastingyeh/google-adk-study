"""
語音助理 Agent
完整的 VoiceAssistant 實作，包含錄音、播放與對話功能。
"""

import asyncio
import os
from typing import Optional
from google.adk.agents import Agent, LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.apps import App
from google.adk.runners import Runner
from google.genai import Client, types, errors

try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False


class VoiceAssistant:
    """
    使用 Live API 的即時語音助理。

    功能：
    - 從麥克風錄製音訊
    - 透過喇叭播放音訊
    - 雙向串流對話
    - 多種語音設定
    """

    def __init__(
        self,
        model: Optional[str] = None,
        voice_name: str = "Puck",
        sample_rate: int = 16000,
        audio_mode: bool = False,
    ):
        """
        初始化語音助理。

        Args:
            model: 要使用的 Live API 模型
            voice_name: 語音設定 (Puck, Charon, Kore, Fenrir, Aoede)
            sample_rate: 音訊取樣率 (Hz)
            audio_mode: 若為 True，使用音訊模態。若為 False，使用文字模態。
        """

        # --- 音訊設定 ---
        self.chunk_size = 1024  # 音訊緩衝區大小
        self.sample_rate = sample_rate  # 取樣率
        self.channels = 1  # 單聲道
        self.format = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None  # 16-bit PCM 格式
        self.voice_name = voice_name  # 語音名稱
        self.audio_mode = audio_mode  # 是否啟用音訊模式

        # PyAudio 實例 (延遲初始化)
        self._audio = None

        # --- 模型設定 ---
        # 決定要使用的 Live API 模型，優先使用傳入的參數，其次是環境變數，最後是預設值
        self.live_model = model or os.getenv(
            "VOICE_ASSISTANT_LIVE_MODEL", "gemini-2.0-flash-live-001"
        )

        # --- Agent 設定 ---
        # 建立 Agent，定義其模型、名稱、描述與指令
        self.agent = Agent(
            model=self.live_model,
            name="voice_assistant",
            description="即時語音助理",
            instruction="""
            你是個樂於助人的語音助理。請遵守以下準則：

            - 自然且口語化地回應
            - 為了語音互動，回應請保持簡潔（最多 2-3 句話）
            - 必要時提出澄清問題
            - 保持友善與親切的態度
            - 使用適合口語對話的非正式語言
            - 除非特別要求，否則避免冗長的解釋
            """.strip(),
            generate_content_config=types.GenerateContentConfig(
                temperature=0.8,  # 讓對話更自然
                max_output_tokens=150,  # 為了語音互動，限制輸出的 token 數量
            ),
        )

        # --- 執行與串流設定 ---
        # 根據 audio_mode 設定 live streaming 的參數
        if audio_mode:
            # 音訊模式：接收音訊回應
            self.run_config = RunConfig(
                streaming_mode=StreamingMode.BIDI,  # 雙向串流
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name
                        )
                    )
                ),
                response_modalities=["audio"],  # 指定回應模態為音訊
            )
        else:
            # 文字模式：接收文字回應 (備援)
            self.run_config = RunConfig(
                streaming_mode=StreamingMode.BIDI,
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name
                        )
                    )
                ),
                response_modalities=["text"],  # 指定回應模態為文字
            )

        # --- 認證策略 ---
        # 決定使用 Vertex AI 還是 Google AI 的認證方式
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.vertex_location = (
            os.getenv("GOOGLE_CLOUD_LOCATION")
            or os.getenv("GOOGLE_GENAI_VERTEXAI_LOCATION")
            or "us-central1"
        )
        self.use_vertex_live = bool(
            os.getenv("GOOGLE_GENAI_USE_VERTEXAI") and self.project_id
        )
        if self.use_vertex_live:
            # 確保下游函式庫能取得 location
            if not os.getenv("GOOGLE_GENAI_VERTEXAI_LOCATION"):
                os.environ["GOOGLE_GENAI_VERTEXAI_LOCATION"] = self.vertex_location
            if not os.getenv("GOOGLE_CLOUD_LOCATION"):
                os.environ["GOOGLE_CLOUD_LOCATION"] = self.vertex_location
        self._api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self._client: Optional[Client] = None
        self.text_model = os.getenv("VOICE_ASSISTANT_TEXT_MODEL", "gemini-2.5-flash")

        # --- App 與 Runner ---
        # 建立 App (Runner 在需要時延遲建立)
        self.app = App(name="voice_assistant_app", root_agent=self.agent)
        self._runner: Optional[Runner] = None

        # --- Session 管理 ---
        self._session_id: Optional[str] = None
        self._user_id = "voice_user"

    async def _fallback_generate_text(self, text: str) -> str:
        """當 Live API 串流無法使用時，改用 Responses API 作為備援。"""
        # 延遲初始化 Client
        if self._client is None:
            if self.use_vertex_live:
                # 使用 Vertex AI 端點與 ADC 憑證
                self._client = Client(
                    vertexai=True,
                    project=self.project_id,
                    location=self.vertex_location,
                )
            elif self._api_key:
                # 直接使用 API 金鑰模式 (Google hosted endpoint)
                self._client = Client(api_key=self._api_key)
            else:
                # 使用預設 Client (例如：gcloud auth application-default login)
                self._client = Client()

        # 準備使用者輸入內容
        user_content = types.Content(
            role="user", parts=[types.Part.from_text(text=text)]
        )
        model_name = self.text_model
        # 如果不是使用 Vertex AI 且模型名稱不包含 "/"，則自動加上 "models/" 前綴
        if not self.use_vertex_live and "/" not in model_name:
            model_name = f"models/{model_name}"

        try:
            # 透過非同步方式呼叫 generate_content
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model=model_name,
                contents=[user_content],
            )
        except errors.ClientError as err:
            print(f"❌ 備援模型錯誤 ({err})。請檢查 VOICE_ASSISTANT_TEXT_MODEL。")
            return "我現在無法連線到文字模型。請確認您的 API 存取權限。"

        # 解析回應並組合成單一字串
        parts: list[str] = []
        for candidate in getattr(response, "candidates", []) or []:
            content = getattr(candidate, "content", None)
            if not content or not getattr(content, "parts", None):
                continue
            for part in content.parts:
                value = getattr(part, "text", None)
                if value:
                    parts.append(value)
        return "".join(parts)

    @property
    def runner(self) -> Runner:
        """延遲初始化 Runner。"""
        if self._runner is None:
            from google.adk.sessions import InMemorySessionService

            session_service = InMemorySessionService()
            self._runner = Runner(app=self.app, session_service=session_service)
        return self._runner

    @property
    def audio(self):
        """延遲初始化 PyAudio。"""
        if not PYAUDIO_AVAILABLE:
            raise RuntimeError(
                "PyAudio 無法使用。請透過以下指令安裝：pip install pyaudio"
            )

        if self._audio is None:
            self._audio = pyaudio.PyAudio()
        return self._audio

    async def record_audio(self, duration_seconds: int = 5) -> bytes:
        """
        從麥克風錄製音訊。

        Args:
            duration_seconds: 錄音時長

        Returns:
            音訊資料 (bytes)
        """

        print(f"🎤 正在錄音 {duration_seconds} 秒...")

        # 開啟音訊串流
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
        )

        frames = []

        # 錄製指定時長的音訊
        for _ in range(0, int(self.sample_rate / self.chunk_size * duration_seconds)):
            data = stream.read(self.chunk_size)
            frames.append(data)

        # 停止並關閉串流
        stream.stop_stream()
        stream.close()

        print("✅ 錄音完成")

        return b"".join(frames)

    def play_audio(self, audio_data: bytes):
        """
        透過喇叭播放音訊。

        Args:
            audio_data: 要播放的音訊 bytes
        """

        # 開啟輸出串流
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            output=True,
        )

        # 寫入音訊資料並播放
        stream.write(audio_data)
        stream.stop_stream()
        stream.close()

    async def _ensure_session(self):
        """確保 session 已被建立。"""
        if self._session_id is None:
            session = await self.runner.session_service.create_session(
                app_name=self.app.name, user_id=self._user_id
            )
            self._session_id = session.id

    async def send_text(self, text: str) -> str:
        """
        傳送文字訊息並取得回應。

        Args:
            text: 使用者訊息

        Returns:
            Agent 的文字回應
        """

        await self._ensure_session()

        # 如果不是使用 Vertex AI，則使用備援的文字生成方法
        if not self.use_vertex_live:
            return await self._fallback_generate_text(text)

        # 建立用於 live streaming 的佇列
        queue = LiveRequestQueue()
        queue.send_content(
            types.Content(role="user", parts=[types.Part.from_text(text=text)])
        )
        queue.close()

        response_text: list[str] = []
        try:
            # 執行 live run 並處理事件
            async for event in self.runner.run_live(
                live_request_queue=queue,
                user_id=self._user_id,
                session_id=self._session_id,
                run_config=self.run_config,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_text.append(part.text)
        except Exception as exc:
            print(f"⚠️  Live session 錯誤 ({exc})；切換至備援文字回應。")
            return await self._fallback_generate_text(text)

        # 如果串流沒有回傳任何內容，則使用備援方法
        if not response_text:
            return await self._fallback_generate_text(text)

        return "".join(response_text)

    async def send_audio(self, audio_data: bytes) -> tuple[str, list[bytes]]:
        """
        傳送音訊並取得回應。

        Args:
            audio_data: 音訊 bytes

        Returns:
            一個包含 (文字回應, 音訊回應區塊) 的 tuple
        """

        await self._ensure_session()

        # 建立佇列
        queue = LiveRequestQueue()

        # 使用 send_realtime 傳送音訊
        queue.send_realtime(
            blob=types.Blob(
                data=audio_data, mime_type=f"audio/pcm;rate={self.sample_rate}"
            )
        )

        # 關閉佇列
        queue.close()

        # 收集回應
        text_response = []
        audio_response = []

        async for event in self.runner.run_live(
            live_request_queue=queue,
            user_id=self._user_id,
            session_id=self._session_id,
            run_config=self.run_config,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        text_response.append(part.text)
                    if part.inline_data:
                        audio_response.append(part.inline_data.data)

        return "".join(text_response), audio_response

    async def conversation_turn(self, user_audio: bytes):
        """
        執行一次完整的音訊對話回合。

        Args:
            user_audio: 使用者的音訊輸入
        """

        print("\n🤖 Agent 回應中...")

        # 傳送音訊並取得回應
        text_response, audio_response = await self.send_audio(user_audio)

        # 印出文字回應
        print(text_response)

        # 如果有音訊回應，則播放
        if audio_response:
            print("🔊 正在播放回應...")
            combined_audio = b"".join(audio_response)
            self.play_audio(combined_audio)

    def cleanup(self):
        """清理資源。"""
        if self._audio is not None:
            self._audio.terminate()


# 為了讓 ADK 能夠發現，匯出 root_agent
root_agent = Agent(
    model=os.getenv("VOICE_ASSISTANT_LIVE_MODEL", "gemini-2.0-flash-live-001"),
    name="voice_assistant",
    description="支援 Live API 的即時語音助理",
    instruction="""
    你是個樂於助人的語音助理。請遵守以下準則：

    - 自然且口語化地回應
    - 為了語音互動，回應請保持簡潔（最多 2-3 句話）
    - 必要時提出澄清問題
    - 保持友善與親切的態度
    - 使用適合口語對話的非正式語言
    - 除非特別要求，否則避免冗長的解釋
    """.strip(),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.8, max_output_tokens=150
    ),
)
