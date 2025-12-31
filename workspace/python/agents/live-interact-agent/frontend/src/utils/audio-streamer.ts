import {
  createWorketFromSrc,
  registeredWorklets,
} from "./audioworklet-registry";

/**
 * AudioStreamer class handles streaming audio playback.
 * AudioStreamer 類別處理串流音訊播放。
 * It manages an audio queue, processes PCM16 data, and schedules playback.
 * 它管理音訊隊列，處理 PCM16 數據，並排程播放。
 */
export class AudioStreamer {
  public audioQueue: Float32Array[] = [];
  private isPlaying: boolean = false;
  private sampleRate: number = 24000;
  private bufferSize: number = 7680;
  private processingBuffer: Float32Array = new Float32Array(0);
  private scheduledTime: number = 0;
  public gainNode: GainNode;
  public source: AudioBufferSourceNode;
  private isStreamComplete: boolean = false;
  private checkInterval: number | null = null;
  private initialBufferTime: number = 0.1; //0.1 // 100ms initial buffer // 100ms 初始緩衝區
  private endOfQueueAudioSource: AudioBufferSourceNode | null = null;

  public onComplete = () => {};

  constructor(public context: AudioContext) {
    this.gainNode = this.context.createGain();
    this.source = this.context.createBufferSource();
    this.gainNode.connect(this.context.destination);
    this.addPCM16 = this.addPCM16.bind(this);
  }

  /**
   * Adds an audio worklet to the context.
   * 將音訊 worklet 添加到上下文。
   */
  async addWorklet<T extends (d: any) => void>(
    workletName: string,
    workletSrc: string,
    handler: T,
  ): Promise<this> {
    let workletsRecord = registeredWorklets.get(this.context);
    if (workletsRecord && workletsRecord[workletName]) {
      // The worklet already exists on this context
      // add the new handler to it
      // 該 worklet 已存在於此上下文中
      // 將新的處理程序添加到其中
      workletsRecord[workletName].handlers.push(handler);
      return Promise.resolve(this);
      //throw new Error(`Worklet ${workletName} already exists on context`);
    }

    if (!workletsRecord) {
      registeredWorklets.set(this.context, {});
      workletsRecord = registeredWorklets.get(this.context)!;
    }

    // Create new record to fill in as becomes available
    // 建立新記錄以在可用時填入
    workletsRecord[workletName] = { handlers: [handler] };

    const src = createWorketFromSrc(workletName, workletSrc);
    await this.context.audioWorklet.addModule(src);
    const worklet = new AudioWorkletNode(this.context, workletName);

    // Add the node into the map
    // 將節點加入到映射中
    workletsRecord[workletName].node = worklet;

    return this;
  }

  /**
   * Adds PCM16 audio data to the processing buffer.
   * 將 PCM16 音訊數據添加到處理緩衝區。
   */
  addPCM16(chunk: Uint8Array) {
    const float32Array = new Float32Array(chunk.length / 2);
    const dataView = new DataView(chunk.buffer);

    for (let i = 0; i < chunk.length / 2; i++) {
      try {
        const int16 = dataView.getInt16(i * 2, true);
        float32Array[i] = int16 / 32768;
      } catch (e) {
        console.error(e);
        // console.log(
        //   `dataView.length: ${dataView.byteLength},  i * 2: ${i * 2}`,
        // );
      }
    }

    const newBuffer = new Float32Array(
      this.processingBuffer.length + float32Array.length,
    );
    newBuffer.set(this.processingBuffer);
    newBuffer.set(float32Array, this.processingBuffer.length);
    this.processingBuffer = newBuffer;

    // Push full buffers to the queue
    // 將完整的緩衝區推送到隊列
    while (this.processingBuffer.length >= this.bufferSize) {
      const buffer = this.processingBuffer.slice(0, this.bufferSize);
      this.audioQueue.push(buffer);
      this.processingBuffer = this.processingBuffer.slice(this.bufferSize);
    }

    if (!this.isPlaying) {
      this.isPlaying = true;
      // Initialize scheduledTime only when we start playing
      // 僅在開始播放時初始化 scheduledTime
      this.scheduledTime = this.context.currentTime + this.initialBufferTime;
      this.scheduleNextBuffer();
    }
  }

  private createAudioBuffer(audioData: Float32Array): AudioBuffer {
    const audioBuffer = this.context.createBuffer(
      1,
      audioData.length,
      this.sampleRate,
    );
    audioBuffer.getChannelData(0).set(audioData);
    return audioBuffer;
  }

  private scheduleNextBuffer() {
    const SCHEDULE_AHEAD_TIME = 0.2;

    while (
      this.audioQueue.length > 0 &&
      this.scheduledTime < this.context.currentTime + SCHEDULE_AHEAD_TIME
    ) {
      const audioData = this.audioQueue.shift()!;
      const audioBuffer = this.createAudioBuffer(audioData);
      const source = this.context.createBufferSource();

      if (this.audioQueue.length === 0) {
        if (this.endOfQueueAudioSource) {
          this.endOfQueueAudioSource.onended = null;
        }
        this.endOfQueueAudioSource = source;
        source.onended = () => {
          if (
            !this.audioQueue.length &&
            this.endOfQueueAudioSource === source
          ) {
            this.endOfQueueAudioSource = null;
            this.onComplete();
          }
        };
      }

      source.buffer = audioBuffer;
      source.connect(this.gainNode);

      const worklets = registeredWorklets.get(this.context);

      if (worklets) {
        Object.entries(worklets).forEach(([, graph]) => {
          const { node, handlers } = graph;
          if (node) {
            source.connect(node);
            node.port.onmessage = function (ev: MessageEvent) {
              handlers.forEach((handler) => {
                handler.call(node.port, ev);
              });
            };
            node.connect(this.context.destination);
          }
        });
      }

      // i added this trying to fix clicks
      // this.gainNode.gain.setValueAtTime(0, 0);
      // this.gainNode.gain.linearRampToValueAtTime(1, 1);

      // Ensure we never schedule in the past
      // 確保我們永遠不會排程過去的時間
      const startTime = Math.max(this.scheduledTime, this.context.currentTime);
      source.start(startTime);

      this.scheduledTime = startTime + audioBuffer.duration;
    }

    if (this.audioQueue.length === 0 && this.processingBuffer.length === 0) {
      if (this.isStreamComplete) {
        this.isPlaying = false;
        if (this.checkInterval) {
          clearInterval(this.checkInterval);
          this.checkInterval = null;
        }
      } else {
        if (!this.checkInterval) {
          this.checkInterval = window.setInterval(() => {
            if (
              this.audioQueue.length > 0 ||
              this.processingBuffer.length >= this.bufferSize
            ) {
              this.scheduleNextBuffer();
            }
          }, 100) as unknown as number;
        }
      }
    } else {
      const nextCheckTime =
        (this.scheduledTime - this.context.currentTime) * 1000;
      setTimeout(
        () => this.scheduleNextBuffer(),
        Math.max(0, nextCheckTime - 50),
      );
    }
  }

  /**
   * Stops audio playback and resets state.
   * 停止音訊播放並重置狀態。
   */
  stop() {
    this.isPlaying = false;
    this.isStreamComplete = true;
    this.audioQueue = [];
    this.processingBuffer = new Float32Array(0);
    this.scheduledTime = this.context.currentTime;

    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }

    this.gainNode.gain.linearRampToValueAtTime(
      0,
      this.context.currentTime + 0.1,
    );

    setTimeout(() => {
      this.gainNode.disconnect();
      this.gainNode = this.context.createGain();
      this.gainNode.connect(this.context.destination);
    }, 200);
  }

  /**
   * Resumes the audio context if suspended.
   * 如果暫停，則恢復音訊上下文。
   */
  async resume() {
    if (this.context.state === "suspended") {
      await this.context.resume();
    }
    this.isStreamComplete = false;
    this.scheduledTime = this.context.currentTime + this.initialBufferTime;
    this.gainNode.gain.setValueAtTime(1, this.context.currentTime);
  }

  /**
   * Marks the stream as complete.
   * 將串流標記為已完成。
   */
  complete() {
    this.isStreamComplete = true;
    if (this.processingBuffer.length > 0) {
      this.audioQueue.push(this.processingBuffer);
      this.processingBuffer = new Float32Array(0);
      if (this.isPlaying) {
        this.scheduleNextBuffer();
      }
    } else {
      this.onComplete();
    }
  }
}

// // Usage example:
// // 使用範例：
// const audioStreamer = new AudioStreamer();
//
// // In your streaming code:
// // 在您的串流程式碼中：
// function handleChunk(chunk: Uint8Array) {
//   audioStreamer.handleChunk(chunk);
// }
//
// // To start playing (call this in response to a user interaction)
// // 開始播放 (回應使用者互動時呼叫此函數)
// await audioStreamer.resume();
//
// // To stop playing
// // 停止播放
// // audioStreamer.stop();
