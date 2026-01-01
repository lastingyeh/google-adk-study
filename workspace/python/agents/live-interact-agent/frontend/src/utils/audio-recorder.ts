import { audioContext } from "./utils";
import AudioRecordingWorklet from "./worklets/audio-processing";
import VolMeterWorket from "./worklets/vol-meter";

import { createWorketFromSrc } from "./audioworklet-registry";
import EventEmitter from "eventemitter3";

// Helper function to convert ArrayBuffer to Base64 string
// 將 ArrayBuffer 轉換為 Base64 字串的輔助函數
function arrayBufferToBase64(buffer: ArrayBuffer) {
  var binary = "";
  var bytes = new Uint8Array(buffer);
  var len = bytes.byteLength;
  for (var i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

/**
 * AudioRecorder class handles microphone input and audio processing.
 * AudioRecorder 類別處理麥克風輸入和音訊處理。
 * It uses AudioWorklets to process audio data and calculate volume levels.
 * 它使用 AudioWorklets 來處理音訊數據並計算音量級別。
 */
export class AudioRecorder extends EventEmitter {
  stream: MediaStream | undefined;
  audioContext: AudioContext | undefined;
  source: MediaStreamAudioSourceNode | undefined;
  recording: boolean = false;
  recordingWorklet: AudioWorkletNode | undefined;
  vuWorklet: AudioWorkletNode | undefined;

  private starting: Promise<void> | null = null;

  constructor(public sampleRate = 16000) {
    super();
  }

  /**
   * Starts recording audio from the user's microphone.
   * 開始錄製使用者麥克風的音訊。
   */
  async start() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error("Could not request user media (無法請求使用者媒體)");
    }

    this.starting = new Promise(async (resolve) => {
      // Request microphone access
      // 請求麥克風權限
      this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.audioContext = await audioContext({ sampleRate: this.sampleRate });
      this.source = this.audioContext.createMediaStreamSource(this.stream);

      // Load and connect the audio recording worklet
      // 載入並連接音訊錄製 worklet
      const workletName = "audio-recorder-worklet";
      const src = createWorketFromSrc(workletName, AudioRecordingWorklet);

      await this.audioContext.audioWorklet.addModule(src);
      this.recordingWorklet = new AudioWorkletNode(
        this.audioContext,
        workletName,
      );

      this.recordingWorklet.port.onmessage = async (ev: MessageEvent) => {
        // Worklet processes recording floats and messages converted buffer
        // Worklet 處理錄製的浮點數並傳送轉換後的緩衝區
        const arrayBuffer = ev.data.data.int16arrayBuffer;

        if (arrayBuffer) {
          const arrayBufferString = arrayBufferToBase64(arrayBuffer);
          this.emit("data", arrayBufferString);
        }
      };
      this.source.connect(this.recordingWorklet);

      // Load and connect the volume meter worklet
      // 載入並連接音量計 worklet
      const vuWorkletName = "vu-meter";
      await this.audioContext.audioWorklet.addModule(
        createWorketFromSrc(vuWorkletName, VolMeterWorket),
      );
      this.vuWorklet = new AudioWorkletNode(this.audioContext, vuWorkletName);
      this.vuWorklet.port.onmessage = (ev: MessageEvent) => {
        this.emit("volume", ev.data.volume);
      };

      this.source.connect(this.vuWorklet);
      this.recording = true;
      resolve();
      this.starting = null;
    });
  }

  /**
   * Stops recording and releases resources.
   * 停止錄製並釋放資源。
   */
  stop() {
    // Its plausible that stop would be called before start completes
    // such as if the websocket immediately hangs up
    // 在 start 完成之前呼叫 stop 是可能的，例如 WebSocket 立即掛斷
    const handleStop = () => {
      this.source?.disconnect();
      this.stream?.getTracks().forEach((track) => track.stop());
      this.stream = undefined;
      this.recordingWorklet = undefined;
      this.vuWorklet = undefined;
    };
    if (this.starting) {
      this.starting.then(handleStop);
      return;
    }
    handleStop();
  }
}
