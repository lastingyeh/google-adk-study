# 教學 15：音訊設定指南

本指南將協助您為 Live API 音訊示範設定音訊功能。

## 快速檢查

在安裝之前，請先確認是否需要音訊功能：

```bash
# 檢查音訊工具是否可用
make check_audio
```

## 需求

- **Python 3.8+**
- **PyAudio** 用於音訊 I/O
- **麥克風** (用於互動式示範)
- **喇叭/耳機** (用於音訊播放)

## 特定平台的安裝方式

### macOS

#### 選項 1：使用 Homebrew (建議)

```bash
# 安裝 portaudio (PyAudio 的依賴套件)
brew install portaudio

# 安裝 PyAudio
pip install pyaudio

# 驗證安裝
python -c "import pyaudio; print('✅ PyAudio 安裝成功！')"
```

#### 選項 2：預先建置的 Wheels

```bash
# 安裝預先建置的 PyAudio wheel
pip install pyaudio

# 如果上述指令失敗，請嘗試：
pip install --upgrade pip
pip install pyaudio
```

#### macOS 疑難排解

**問題**：`fatal error: 'portaudio.h' file not found`

```bash
# 解決方案：先安裝 portaudio
brew install portaudio

# 然後使用明確的路徑重新安裝 PyAudio
pip install --global-option="build_ext" \
  --global-option="-I/opt/homebrew/include" \
  --global-option="-L/opt/homebrew/lib" \
  pyaudio
```

**問題**：麥克風權限遭拒

```bash
# macOS 需要麥克風權限
# 前往：系統偏好設定 → 安全性與隱私權 → 隱私權 → 麥克風
# 為「終端機」或您的 Python IDE 啟用麥克風存取權限
```

### Linux (Ubuntu/Debian)

```bash
# 安裝系統依賴套件
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio

# 安裝 PyAudio
pip install pyaudio

# 驗證安裝
python -c "import pyaudio; print('✅ PyAudio 安裝成功！')"
```

#### 替代方案：從原始碼建置

```bash
# 安裝建置依賴套件
sudo apt-get install -y python3-dev portaudio19-dev

# 安裝 PyAudio
pip install pyaudio
```

#### Linux 疑難排解

**問題**：未偵測到音訊裝置

```bash
# 檢查音訊裝置
aplay -l   # 列出播放裝置
arecord -l # 列出錄音裝置

# 如果缺少 ALSA 工具，請安裝
sudo apt-get install alsa-utils

# 測試麥克風
arecord -d 5 test.wav  # 錄製 5 秒
aplay test.wav         # 播放
```

**問題**：音訊裝置權限遭拒

```bash
# 將使用者加入 audio 群組
sudo usermod -a -G audio $USER

# 登出再重新登入以使變更生效
```

### Windows

#### 選項 1：預先建置的 Wheels (最簡單)

```powershell
# 從預先建置的 wheel 安裝 PyAudio
pip install pyaudio

# 如果上述指令失敗，請嘗試非官方的二進位檔：
# 從此處下載：https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# 然後執行：pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl
```

#### 選項 2：使用 pipwin

```powershell
# 安裝 pipwin
pip install pipwin

# 使用 pipwin 安裝 PyAudio
pipwin install pyaudio
```

#### Windows 疑難排解

**問題**：需要 Microsoft Visual C++ 14.0

```powershell
# 安裝 Visual Studio Build Tools
# 從此處下載：https://visualstudio.microsoft.com/downloads/
# 選擇「使用 C++ 的桌面開發」

# 或使用預先建置的 wheels (選項 1)
```

**問題**：未偵測到麥克風

```powershell
# 檢查 Windows 聲音設定
# 設定 → 系統 → 音效 → 輸入
# 確保麥克風已啟用並設定為預設裝置
```

## 驗證安裝

安裝 PyAudio 後：

```bash
# 檢查音訊裝置
make check_audio

# 或手動執行：
python -m voice_assistant.audio_utils
```

預期輸出：
```
✅ 音訊功能可用！

======================================================================
可用的音訊裝置
======================================================================

裝置 0：內建麥克風
  最大輸入聲道：2
  最大輸出聲道：0
  預設取樣率：48000.0

裝置 1：內建輸出
  最大輸入聲道：0
  最大輸出聲道：2
  預設取樣率：48000.0
```

## 測試音訊

### 測試音訊播放

```bash
# 執行帶有音訊輸出的基本示範
make basic_demo_audio
```

此指令將會：
1. 傳送文字訊息給代理人
2. 接收音訊回應
3. 透過喇叭播放音訊
4. 將音訊儲存為 `response.wav`

### 測試完整的互動式音訊

```bash
# 執行互動式示範 (麥克風 + 喇叭)
make audio_demo
```

此指令將會：
1. 從您的麥克風錄音 (5 秒)
2. 將音訊傳送至 Live API
3. 接收音訊回應
4. 透過喇叭播放回應

## 常見問題

### "PyAudio 未安裝"

```bash
# 遵循上述特定平台的安裝步驟
pip install pyaudio
```

### "未偵測到麥克風"

**macOS**：檢查「系統偏好設定」→「安全性與隱私權」→「麥克風」

**Linux**：
```bash
arecord -l  # 列出錄音裝置
# 如果清單是空的，請檢查硬體連接
```

**Windows**：設定 → 系統 → 音效 → 輸入

### "未偵測到音訊輸出"

確保喇叭/耳機：
- 已連接
- 已開啟電源
- 已設定為預設音訊輸出裝置
- 未靜音

### 音訊品質問題

Live API 期望特定的音訊格式：
- **格式**：16-bit PCM
- **取樣率**：16kHz
- **聲道**：單聲道 (1 channel)

如果音訊品質不佳：

```bash
# 檢查您的裝置是否支援 16kHz
python -c "
import pyaudio
p = pyaudio.PyAudio()
info = p.get_default_input_device_info()
print(f'預設取樣率：{info[\"defaultSampleRate\"]}')
p.terminate()
"
```

大多數裝置都支援 16kHz，但如有需要，音訊工具會重新取樣。

## 替代方案：純文字模式

如果音訊設定太複雜，請使用純文字示範：

```bash
# 帶有文字回應的基本示範 (無音訊)
make basic_demo_text

# 或一般的示範 (文字對話)
make demo
```

## Docker/容器環境

在容器中使用音訊需要特殊設定：

### 在 macOS/Linux 上的 Docker

```dockerfile
# 在您的 Dockerfile 中加入：
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    alsa-utils \
    && pip install pyaudio

# 執行時需有音訊裝置存取權限：
docker run --device /dev/snd:/dev/snd your-image
```

### 在 Windows 上使用 WSL2 的 Docker

WSL2 的音訊支援有限。請考慮：
- 直接在 Windows 上執行示範
- 使用純文字模式
- 連接到具有音訊功能的遠端機器

## CI/CD 環境

在沒有音訊硬體的情況下進行測試：

```python
# 在測試中模擬音訊
from unittest.mock import patch

with patch('voice_assistant.audio_utils.PYAUDIO_AVAILABLE', False):
    # 以純文字模式執行測試
    pass
```

或使用純文字示範：

```bash
# 在 CI 管線中
make basic_demo_text  # 不需要音訊
```

## 尋求協助

如果您遇到問題：

1. **檢查音訊裝置**：`make check_audio`
2. **測試麥克風**：使用系統聲音設定
3. **驗證 PyAudio**：`python -c "import pyaudio; print(pyaudio.__version__)"`
4. **查閱文件**：[PyAudio 文件](https://people.csail.mit.edu/hubert/pyaudio/)
5. **使用文字模式**：退回使用純文字示範

## 後續步驟

音訊功能正常運作後：

```bash
# 1. 測試基本音訊播放
make basic_demo_audio

# 2. 嘗試互動式對話
make audio_demo

# 3. 探索進階功能
make advanced_demo
```

## 額外資源

- **PyAudio 文件**：https://people.csail.mit.edu/hubert/pyaudio/
- **PortAudio**：http://www.portaudio.com/
- **Live API 文件**：https://ai.google.dev/gemini-api/docs/live
- **教學 15**：[完整文件](../../../notes/google-adk-training-hub/adk_training/15-live_api_audio.md)
