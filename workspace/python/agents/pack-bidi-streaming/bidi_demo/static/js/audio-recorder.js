/**
 * 音訊錄製器工作線程 (Audio Recorder Worklet)
 * 負責擷取麥克風輸入並轉換為 16-bit PCM 格式傳送至伺服器
 */

let micStream;

/**
 * 啟動音訊錄製 Worklet
 * @param {Function} audioRecorderHandler - 處理 PCM 數據的回調函數
 */
export async function startAudioRecorderWorklet(audioRecorderHandler) {
  // 建立音訊上下文，取樣率設定為 16000 Hz (語音辨識常用的規格)
  const audioRecorderContext = new AudioContext({ sampleRate: 16000 });
  console.log("AudioContext sample rate:", audioRecorderContext.sampleRate);

  // 載入錄製處理器模組 (pcm-recorder-processor.js)
  const workletURL = new URL("./pcm-recorder-processor.js", import.meta.url);
  await audioRecorderContext.audioWorklet.addModule(workletURL);

  // 請求麥克風存取權限
  micStream = await navigator.mediaDevices.getUserMedia({
    audio: { channelCount: 1 }, // 使用單聲道
  });

  // 建立媒體流來源
  const source = audioRecorderContext.createMediaStreamSource(micStream);

  // 建立使用 PCMProcessor 的 AudioWorkletNode
  const audioRecorderNode = new AudioWorkletNode(
    audioRecorderContext,
    "pcm-recorder-processor"
  );

  // 將麥克風來源連接到工作線程節點
  source.connect(audioRecorderNode);

  // 監聽來自 Worklet 的訊息 (Float32 數據)
  audioRecorderNode.port.onmessage = (event) => {
    // 將 Float32 樣本轉換為 16-bit PCM
    const pcmData = convertFloat32ToPCM(event.data);

    // 將 PCM 數據傳送給處理器 (發送到伺服器)
    audioRecorderHandler(pcmData);
  };

  return [audioRecorderNode, audioRecorderContext, micStream];
}

/**
 * 停止麥克風串流
 * @param {MediaStream} micStream - 要停止的麥克風串流
 */
export function stopMicrophone(micStream) {
  micStream.getTracks().forEach((track) => track.stop());
  console.log("stopMicrophone(): Microphone stopped.");
}

/**
 * 將 Float32 樣本轉換為 16-bit PCM (Int16)
 * @param {Float32Array} inputData - 浮點數音訊數據
 * @returns {ArrayBuffer} 16-bit PCM 數據
 */
function convertFloat32ToPCM(inputData) {
  // 建立相同長度的 Int16Array
  const pcm16 = new Int16Array(inputData.length);
  for (let i = 0; i < inputData.length; i++) {
    // 將浮點值 [-1, 1] 縮放至 16-bit PCM 範圍 [-32768, 32767]
    // 乘上 0x7fff (32767)
    pcm16[i] = inputData[i] * 0x7fff;
  }
  // 回傳底層的 ArrayBuffer
  return pcm16.buffer;
}

/**
 * 重點摘要
 * - **核心概念**：實現網頁端的麥克風擷取，並將其轉換為伺服器所需的 16-bit PCM 格式。
 * - **關鍵技術**：getUserMedia、AudioWorklet、PCM 數據轉換。
 * - **重要結論**：取樣率固定為 16kHz 以符合大多數語音辨識 (ASR) 引擎的需求，並在 Worker 中進行轉換以維持效能。
 */
