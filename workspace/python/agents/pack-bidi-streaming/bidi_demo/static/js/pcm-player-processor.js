/**
 * PCM 播放處理器 (PCM Player Processor)
 * 這是一個音訊工作處理緒 (Audio Worklet Processor)，負責儲存從主線程傳送的 PCM 音訊數據
 * 到環形緩衝區 (Ring Buffer) 並進行播放。
 */
class PCMPlayerProcessor extends AudioWorkletProcessor {
  constructor() {
    super();

    // 初始化緩衝區
    // 取樣率 24kHz x 180 秒，確保有足夠的緩存空間
    this.bufferSize = 24000 * 180;
    this.buffer = new Float32Array(this.bufferSize);
    this.writeIndex = 0; // 寫入索引
    this.readIndex = 0;  // 讀取索引

    // 處理來自主線程的訊息
    this.port.onmessage = (event) => {
      // 當收到 'endOfAudio' 指令時重置緩衝區
      if (event.data.command === 'endOfAudio') {
        this.readIndex = this.writeIndex; // 清空緩衝區
        console.log("收到 endOfAudio，正在清空緩衝區。");
        return;
      }

      // 將傳入的 ArrayBuffer 解碼為 Int16Array
      const int16Samples = new Int16Array(event.data);

      // 將音訊數據加入緩衝區
      this._enqueue(int16Samples);
    };
  }

  /**
   * 將傳入的 Int16 數據推入環形緩衝區
   * @param {Int16Array} int16Samples - 16-bit PCM 樣本
   */
  _enqueue(int16Samples) {
    for (let i = 0; i < int16Samples.length; i++) {
      // 將 16-bit 整數轉換為範圍 [-1, 1] 的浮點數
      const floatVal = int16Samples[i] / 32768;

      // 存入環形緩衝區（目前僅處理單聲道）
      this.buffer[this.writeIndex] = floatVal;
      this.writeIndex = (this.writeIndex + 1) % this.bufferSize;

      // 溢位處理：如果寫入追上讀取，則強行移動讀取索引（覆蓋舊數據）
      if (this.writeIndex === this.readIndex) {
        this.readIndex = (this.readIndex + 1) % this.bufferSize;
      }
    }
  }

  /**
   * 音訊處理核心函數，系統會定期呼叫（通常每次 128 個樣本）
   * 從環形緩衝區填充輸出緩衝區
   */
  process(inputs, outputs, parameters) {
    // 獲取輸出串流
    const output = outputs[0];
    const framesPerBlock = output[0].length;

    for (let frame = 0; frame < framesPerBlock; frame++) {
      // 將樣本寫入輸出緩衝區
      output[0][frame] = this.buffer[this.readIndex]; // 左聲道
      if (output.length > 1) {
        output[1][frame] = this.buffer[this.readIndex]; // 右聲道 (複製單聲道)
      }

      // 向前移動讀取索引，除非緩衝區已空
      if (this.readIndex != this.writeIndex) {
        this.readIndex = (this.readIndex + 1) % this.bufferSize;
      }
    }

    // 回傳 true 以維持處理器運行
    return true;
  }
}

// 註冊處理器
registerProcessor('pcm-player-processor', PCMPlayerProcessor);

/**
 * 重點摘要
 * - **核心概念**：實作環形緩衝區來管理即時音訊串流的播放。
 * - **關鍵技術**：AudioWorkletProcessor、環形緩衝區 (Ring Buffer)、Float32 數據轉換。
 * - **重要結論**：透過環形緩衝區有效地緩衝異步到達的音訊包，並確保在 `process` 函數中能夠穩定地輸出音訊流。
 */
