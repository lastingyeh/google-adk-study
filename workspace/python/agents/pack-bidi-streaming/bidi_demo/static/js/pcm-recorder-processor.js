/**
 * PCM 錄製處理器 (PCM Recorder Processor)
 * 負責從麥克風輸入中擷取原始音訊樣本並傳送至主線程。
 */
class PCMProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
  }

  /**
   * 音訊處理核心函數
   * @param {Array} inputs - 輸入音訊數據
   * @param {Array} outputs - 輸出音訊數據
   * @param {Object} parameters - 音訊參數
   */
  process(inputs, outputs, parameters) {
    // 檢查是否有有效的輸入數據
    if (inputs.length > 0 && inputs[0].length > 0) {
      // 使用第一個聲道 (單聲道)
      const inputChannel = inputs[0][0];

      // 複製緩衝區數據，以避免 Web Audio API 重複使用記憶體造成的數據競爭問題
      const inputCopy = new Float32Array(inputChannel);

      // 將擷取到的樣本發送到主線程進行轉換與傳輸
      this.port.postMessage(inputCopy);
    }

    // 回傳 true 以維持處理器運行
    return true;
  }
}

// 註冊處理器
registerProcessor("pcm-recorder-processor", PCMProcessor);

/**
 * 重點摘要
 * - **核心概念**：在音訊線程中即時擷取麥克風樣本。
 * - **關鍵技術**：AudioWorkletProcessor、記憶體複製 (Buffer Copy)、線程間通訊 (PostMessage)。
 * - **重要結論**：使用獨立線程進行音訊擷取，確保錄音的高穩定性與低延遲。
 */
