"""
用於 Live API 音訊處理的音訊工具集

處理 Live API 的音訊播放、錄製與格式轉換。
"""

import io
import wave
from typing import Optional, Tuple
import numpy as np

try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    pyaudio = None


class AudioConfig:
    """Live API 的音訊設定常數。"""

    # Live API 預期使用 16-bit PCM, 16kHz, 單聲道
    SAMPLE_RATE = 16000  # 取樣率
    CHANNELS = 1  # 聲道數
    SAMPLE_WIDTH = 2  # 16-bit = 2 bytes
    FORMAT = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None  # 音訊格式
    CHUNK_SIZE = 1024  # 緩衝區大小

    # 麥克風錄音用
    DEFAULT_RECORD_SECONDS = 5  # 預設錄音秒數


class AudioPlayer:
    """播放從 Live API 接收到的音訊。"""

    def __init__(self):
        """初始化音訊播放器。"""
        if not PYAUDIO_AVAILABLE:
            raise RuntimeError(
                "PyAudio 未安裝。請使用：pip install pyaudio\n"
                "詳細的平台安裝說明請見 AUDIO_SETUP.md。"
            )
        self.audio = pyaudio.PyAudio()

    def play_pcm_bytes(self, audio_data: bytes) -> None:
        """
        播放原始 PCM 音訊資料。

        Args:
            audio_data: 原始 PCM bytes (16-bit, 16kHz, mono)
        """
        if not audio_data:
            return

        # 開啟輸出串流
        stream = self.audio.open(
            format=AudioConfig.FORMAT,
            channels=AudioConfig.CHANNELS,
            rate=AudioConfig.SAMPLE_RATE,
            output=True,
            frames_per_buffer=AudioConfig.CHUNK_SIZE,
        )

        try:
            # 分塊播放音訊
            for i in range(
                0, len(audio_data), AudioConfig.CHUNK_SIZE * AudioConfig.SAMPLE_WIDTH
            ):
                chunk = audio_data[
                    i : i + AudioConfig.CHUNK_SIZE * AudioConfig.SAMPLE_WIDTH
                ]
                stream.write(chunk)
        finally:
            stream.stop_stream()
            stream.close()

    def play_wav_bytes(self, wav_data: bytes) -> None:
        """
        從 bytes 播放 WAV 檔案。

        Args:
            wav_data: 完整的 WAV 檔案 (bytes)
        """
        # 解析 WAV 檔案
        wav_io = io.BytesIO(wav_data)
        with wave.open(wav_io, "rb") as wav_file:
            # 讀取音訊資料
            audio_data = wav_file.readframes(wav_file.getnframes())

            # 使用 WAV 檔案的參數開啟輸出串流
            stream = self.audio.open(
                format=self.audio.get_format_from_width(wav_file.getsampwidth()),
                channels=wav_file.getnchannels(),
                rate=wav_file.getframerate(),
                output=True,
            )

            try:
                stream.write(audio_data)
            finally:
                stream.stop_stream()
                stream.close()

    def save_to_wav(self, audio_data: bytes, filename: str) -> None:
        """
        將原始 PCM 音訊儲存為 WAV 檔案。

        Args:
            audio_data: 原始 PCM bytes
            filename: 輸出的 WAV 檔名
        """
        with wave.open(filename, "wb") as wav_file:
            wav_file.setnchannels(AudioConfig.CHANNELS)
            wav_file.setsampwidth(AudioConfig.SAMPLE_WIDTH)
            wav_file.setframerate(AudioConfig.SAMPLE_RATE)
            wav_file.writeframes(audio_data)

    def close(self):
        """關閉音訊資源。"""
        if hasattr(self, "audio") and self.audio:
            self.audio.terminate()

    def __enter__(self):
        """Context manager 進入點。"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 離開點。"""
        self.close()


class AudioRecorder:
    """從麥克風錄製音訊以供 Live API 使用。"""

    def __init__(self):
        """初始化錄音機。"""
        if not PYAUDIO_AVAILABLE:
            raise RuntimeError(
                "PyAudio 未安裝。請使用：pip install pyaudio\n"
                "詳細的平台安裝說明請見 AUDIO_SETUP.md。"
            )
        self.audio = pyaudio.PyAudio()

    def record_audio(
        self,
        duration_seconds: int = AudioConfig.DEFAULT_RECORD_SECONDS,
        show_progress: bool = True,
    ) -> bytes:
        """
        從麥克風錄製音訊。

        Args:
            duration_seconds: 錄音時長 (秒)
            show_progress: 是否顯示錄音進度

        Returns:
            原始 PCM 音訊 bytes (16-bit, 16kHz, mono)
        """
        if show_progress:
            print(f"🎤 正在錄音 {duration_seconds} 秒...")

        # 開啟輸入串流
        stream = self.audio.open(
            format=AudioConfig.FORMAT,
            channels=AudioConfig.CHANNELS,
            rate=AudioConfig.SAMPLE_RATE,
            input=True,
            frames_per_buffer=AudioConfig.CHUNK_SIZE,
        )

        frames = []
        num_chunks = int(
            AudioConfig.SAMPLE_RATE / AudioConfig.CHUNK_SIZE * duration_seconds
        )

        try:
            for i in range(num_chunks):
                data = stream.read(AudioConfig.CHUNK_SIZE)
                frames.append(data)

                # 更新進度條
                if show_progress and i % 10 == 0:
                    progress = (i / num_chunks) * 100
                    print(f"\r🎤 錄音中：{progress:.0f}%", end="", flush=True)

            if show_progress:
                print("\r🎤 錄音完成！     ")
        finally:
            stream.stop_stream()
            stream.close()

        return b"".join(frames)

    def close(self):
        """關閉音訊資源。"""
        if hasattr(self, "audio") and self.audio:
            self.audio.terminate()

    def __enter__(self):
        """Context manager 進入點。"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 離開點。"""
        self.close()


def check_audio_available() -> Tuple[bool, Optional[str]]:
    """
    檢查音訊功能是否可用。

    Returns:
        一個包含 (是否可用, 錯誤訊息) 的 tuple
    """
    if not PYAUDIO_AVAILABLE:
        return False, (
            "PyAudio 未安裝。\n"
            "請使用：pip install pyaudio\n"
            "詳細的平台安裝說明請見 AUDIO_SETUP.md。"
        )

    # 嘗試初始化 PyAudio
    try:
        audio = pyaudio.PyAudio()

        # 檢查輸入與輸出裝置
        has_input = False
        has_output = False

        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info["maxInputChannels"] > 0:
                has_input = True
            if device_info["maxOutputChannels"] > 0:
                has_output = True

        audio.terminate()

        if not has_input:
            return False, "未偵測到麥克風。請連接麥克風。"

        if not has_output:
            return (
                False,
                "未偵測到音訊輸出裝置。請連接喇叭或耳機。",
            )

        return True, None

    except Exception as e:
        return False, f"音訊初始化失敗：{str(e)}"


def print_audio_devices():
    """印出可用的音訊裝置以供除錯。"""
    if not PYAUDIO_AVAILABLE:
        print("❌ PyAudio 未安裝")
        return

    try:
        audio = pyaudio.PyAudio()

        print("\n" + "=" * 70)
        print("可用的音訊裝置")
        print("=" * 70)

        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            print(f"\n裝置 {i}: {device_info['name']}")
            print(f"  最大輸入聲道: {device_info['maxInputChannels']}")
            print(f"  最大輸出聲道: {device_info['maxOutputChannels']}")
            print(f"  預設取樣率: {device_info['defaultSampleRate']}")

        print("\n" + "=" * 70)

        audio.terminate()

    except Exception as e:
        print(f"❌ 列出音訊裝置時發生錯誤：{e}")


def pcm_to_numpy(pcm_data: bytes) -> np.ndarray:
    """
    將 PCM bytes 轉換為 numpy 陣列。

    Args:
        pcm_data: 原始 PCM bytes (16-bit)

    Returns:
        音訊樣本的 Numpy 陣列
    """
    return np.frombuffer(pcm_data, dtype=np.int16)


def numpy_to_pcm(audio_array: np.ndarray) -> bytes:
    """
    將 numpy 陣列轉換為 PCM bytes。

    Args:
        audio_array: 音訊樣本的 Numpy 陣列

    Returns:
        原始 PCM bytes (16-bit)
    """
    return audio_array.astype(np.int16).tobytes()


def adjust_volume(audio_data: bytes, volume_factor: float) -> bytes:
    """
    調整音量。

    Args:
        audio_data: 原始 PCM bytes
        volume_factor: 音量乘數 (1.0 = 原始音量, 2.0 = 兩倍, 0.5 = 一半)

    Returns:
        調整後的 PCM bytes
    """
    audio_array = pcm_to_numpy(audio_data)
    # 透過 np.clip 避免音量超出 16-bit 整數範圍
    adjusted = np.clip(audio_array * volume_factor, -32768, 32767)
    return numpy_to_pcm(adjusted)


if __name__ == "__main__":
    # 測試音訊可用性
    available, error = check_audio_available()

    if available:
        print("✅ 音訊功能可用！")
        print_audio_devices()
    else:
        print(f"❌ 音訊不可用：{error}")
