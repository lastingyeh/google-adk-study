/**
 * ============================================================
 * AudioPlayerNode 完整範例
 * ============================================================
 * 展示如何使用 Web Audio API 的 AudioWorklet 來播放
 * 從 AI 代理接收的 PCM 音訊數據
 */

import { startAudioPlayerWorklet } from "./audio-player.js";

// ============================================================
// 1. 全域變數：音訊播放器節點與上下文
// ============================================================

let audioPlayerNode;      // **AudioWorkletNode**: 處理 PCM 音訊數據的工作節點
let audioPlayerContext;   // **AudioContext**: Web Audio API 的音訊上下文

// ============================================================
// 2. 初始化音訊播放器 (需要用戶手勢觸發)
// ============================================================

/**
 * **重點**: 啟動音訊播放器
 *
 * Web Audio API 需要用戶手勢(點擊、按鍵等)才能啟動
 * 這是瀏覽器的安全機制,防止網站自動播放音訊
 */
async function initializeAudioPlayer() {
  try {
    // **啟動 AudioWorklet**: 載入並初始化音訊處理器
    const [node, ctx] = await startAudioPlayerWorklet();

    // **儲存引用**: 供後續使用
    audioPlayerNode = node;
    audioPlayerContext = ctx;

    console.log("✅ Audio player initialized:", {
      sampleRate: ctx.sampleRate,      // 採樣率 (通常是 48000 Hz)
      state: ctx.state,                 // 音訊上下文狀態 (running/suspended)
      destination: ctx.destination      // 音訊輸出目標 (揚聲器)
    });

    return true;
  } catch (error) {
    console.error("❌ Failed to initialize audio player:", error);
    return false;
  }
}

// **用戶手勢觸發**: 按鈕點擊事件
document.getElementById("startAudioButton")?.addEventListener("click", async () => {
  const success = await initializeAudioPlayer();
  if (success) {
    document.getElementById("startAudioButton").disabled = true;
    console.log("🎵 Audio mode enabled - ready to play audio from agent");
  }
});

// ============================================================
// 3. 從 WebSocket 接收並播放音訊
// ============================================================

/**
 * **WebSocket 訊息處理器**
 *
 * 接收 AI 代理回傳的 ADK Event,從中提取音訊數據並播放
 */
websocket.onmessage = function (event) {
  const adkEvent = JSON.parse(event.data);

  // **檢查是否包含內容部分**
  if (adkEvent.content && adkEvent.content.parts) {
    const parts = adkEvent.content.parts;

    for (const part of parts) {
      // ============================================================
      // **核心邏輯**: 處理 inlineData 中的音訊
      // ============================================================

      if (part.inlineData) {
        // **提取屬性**:
        const mimeType = part.inlineData.mimeType;  // 音訊格式 (例如: "audio/pcm")
        const data = part.inlineData.data;          // Base64 編碼的音訊數據

        // **格式檢查**: 僅處理 PCM 格式音訊
        // PCM (Pulse Code Modulation) 是未壓縮的原始音訊格式
        // 其他格式如 MP3、AAC 需要不同的解碼器
        if (mimeType && mimeType.startsWith("audio/pcm")) {

          // **安全檢查**: 確保播放器已初始化
          if (audioPlayerNode) {

            // **關鍵步驟**: Base64 → ArrayBuffer → 播放
            // 1. 將 Base64 字串解碼為 ArrayBuffer
            const audioBuffer = base64ToArray(data);

            // 2. 透過 AudioWorklet 的 MessagePort 發送音訊數據
            //    AudioWorklet 在獨立的執行緒中處理音訊,不會阻塞 UI
            audioPlayerNode.port.postMessage(audioBuffer);

            console.log("🔊 Playing audio chunk:", {
              mimeType: mimeType,
              originalSize: data.length,           // Base64 字串長度
              decodedSize: audioBuffer.byteLength, // 實際位元組數
              format: "PCM 16-bit mono"            // 音訊格式
            });

          } else {
            console.warn("⚠️ Audio player not initialized - skipping audio playback");
          }
        } else {
          console.warn("⚠️ Unsupported audio format:", mimeType);
        }
      }

      // 處理其他類型的內容 (例如文字)
      if (part.text) {
        console.log("💭 Text:", part.text);
      }
    }
  }
};

// ============================================================
// 4. 音訊結束信號處理
// ============================================================

/**
 * **重點**: 通知 AudioWorklet 音訊串流已結束
 *
 * 當收到 turnComplete 或 interrupted 事件時,
 * 需要告訴播放器停止等待更多音訊數據
 */
function signalEndOfAudio() {
  if (audioPlayerNode) {
    // **發送控制訊息**: 告知 AudioWorklet 處理完緩衝區中的音訊後停止
    audioPlayerNode.port.postMessage({
      command: "endOfAudio"
    });

    console.log("⏹️ End of audio signal sent");
  }
}

// **使用範例**: 對話輪結束時
websocket.onmessage = function (event) {
  const adkEvent = JSON.parse(event.data);

  // **對話輪完成**: 音訊播放完畢
  if (adkEvent.turnComplete === true) {
    signalEndOfAudio();
  }

  // **被中斷**: 停止當前音訊播放
  if (adkEvent.interrupted === true) {
    signalEndOfAudio();
    console.log("⏸️ Audio playback interrupted by user");
  }
};

// ============================================================
// 5. Base64 解碼工具函數
// ============================================================

/**
 * **Base64 → ArrayBuffer 轉換器**
 *
 * @param {string} base64 - Base64 或 Base64URL 編碼的字串
 * @returns {ArrayBuffer} - 解碼後的二進位音訊數據
 *
 * **支援兩種 Base64 格式**:
 * - Standard Base64: 使用 +、/ 和 = 字元
 * - Base64URL: 使用 -、_ (URL 安全,無 padding)
 */
function base64ToArray(base64) {
  // **步驟 1**: 標準化為 Standard Base64
  // Base64URL → Standard Base64
  let standardBase64 = base64
    .replace(/-/g, '+')  // URL 安全字元 - 轉換為 +
    .replace(/_/g, '/'); // URL 安全字元 _ 轉換為 /

  // **步驟 2**: 補齊 padding (=)
  // Base64 編碼長度必須是 4 的倍數
  while (standardBase64.length % 4) {
    standardBase64 += '=';
  }

  // **步驟 3**: 使用瀏覽器原生 API 解碼
  // atob() 將 Base64 字串解碼為二進位字串
  const binaryString = window.atob(standardBase64);

  // **步驟 4**: 二進位字串 → Uint8Array
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }

  // **步驟 5**: 返回 ArrayBuffer
  // Web Audio API 需要 ArrayBuffer 格式
  return bytes.buffer;
}

// ============================================================
// 6. 錯誤處理與狀態管理
// ============================================================

/**
 * **音訊播放器狀態檢查**
 */
function checkAudioPlayerStatus() {
  if (!audioPlayerContext) {
    return {
      initialized: false,
      message: "Audio player not initialized"
    };
  }

  return {
    initialized: true,
    state: audioPlayerContext.state,           // running/suspended/closed
    sampleRate: audioPlayerContext.sampleRate, // 採樣率
    currentTime: audioPlayerContext.currentTime, // 當前時間 (秒)
    baseLatency: audioPlayerContext.baseLatency  // 基礎延遲 (秒)
  };
}

/**
 * **恢復音訊上下文** (如果被暫停)
 *
 * 某些瀏覽器可能會自動暫停音訊上下文以節省資源
 */
async function resumeAudioContext() {
  if (audioPlayerContext && audioPlayerContext.state === 'suspended') {
    await audioPlayerContext.resume();
    console.log("▶️ Audio context resumed");
  }
}

// **使用範例**: 在播放音訊前檢查狀態
async function playAudioSafely(base64Data) {
  // 1. 檢查播放器狀態
  const status = checkAudioPlayerStatus();
  if (!status.initialized) {
    console.error("❌", status.message);
    return false;
  }

  // 2. 恢復音訊上下文 (如果需要)
  await resumeAudioContext();

  // 3. 播放音訊
  const audioBuffer = base64ToArray(base64Data);
  audioPlayerNode.port.postMessage(audioBuffer);

  return true;
}

// ============================================================
// 7. 清理資源
// ============================================================

/**
 * **重點**: 正確清理音訊資源
 *
 * 當頁面卸載或不再需要音訊功能時,應該清理資源
 */
function cleanupAudioPlayer() {
  // **停止播放**: 發送結束信號
  if (audioPlayerNode) {
    audioPlayerNode.port.postMessage({ command: "endOfAudio" });
  }

  // **關閉音訊上下文**: 釋放系統資源
  if (audioPlayerContext && audioPlayerContext.state !== 'closed') {
    audioPlayerContext.close();
    console.log("🔇 Audio context closed");
  }

  // **清空引用**
  audioPlayerNode = null;
  audioPlayerContext = null;
}

// **頁面卸載時清理**
window.addEventListener('beforeunload', cleanupAudioPlayer);

// ============================================================
// 8. 除錯工具
// ============================================================

/**
 * **音訊數據分析器** (用於除錯)
 */
function analyzeAudioData(base64Data) {
  const buffer = base64ToArray(base64Data);
  const dataView = new DataView(buffer);
  const samples = buffer.byteLength / 2; // 假設 16-bit PCM

  console.log("🔍 Audio Data Analysis:", {
    base64Length: base64Data.length,
    bufferSize: buffer.byteLength,
    sampleCount: samples,
    durationMs: (samples / 16000 * 1000).toFixed(2), // 假設 16kHz 採樣率
    firstSample: dataView.getInt16(0, true),         // 第一個樣本值
    lastSample: dataView.getInt16(buffer.byteLength - 2, true) // 最後一個樣本值
  });
}

// **使用範例**:
// analyzeAudioData(part.inlineData.data);

export {
  initializeAudioPlayer,
  playAudioSafely,
  signalEndOfAudio,
  checkAudioPlayerStatus,
  resumeAudioContext,
  cleanupAudioPlayer,
  analyzeAudioData
};