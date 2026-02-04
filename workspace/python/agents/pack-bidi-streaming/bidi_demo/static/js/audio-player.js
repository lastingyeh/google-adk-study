/**
 * 音訊播放器工作線程 (Audio Player Worklet)
 * 負責初始化音訊上下文並載入 PCM 播放處理器
 */

export async function startAudioPlayerWorklet() {
    // 1. 建立音訊上下文 (AudioContext)
    // 設定取樣率為 24000 Hz，這通常是高品質語音合成的標準
    const audioContext = new AudioContext({
        sampleRate: 24000
    });

    // 2. 載入自定義處理器代碼 (pcm-player-processor.js)
    // 使用 import.meta.url 確保路徑相對於目前檔案
    const workletURL = new URL('./pcm-player-processor.js', import.meta.url);
    await audioContext.audioWorklet.addModule(workletURL);

    // 3. 建立音訊工作節點 (AudioWorkletNode)
    // 使用已註冊的 'pcm-player-processor' 名稱
    const audioPlayerNode = new AudioWorkletNode(audioContext, 'pcm-player-processor');

    // 4. 連接到音訊輸出設備 (通常是喇叭)
    audioPlayerNode.connect(audioContext.destination);

    // 回傳節點與上下文，以便主線程透過 audioPlayerNode.port 發送音訊數據
    return [audioPlayerNode, audioContext];
}

/**
 * 重點摘要
 * - **核心概念**：初始化網頁端音訊播放環境，使用 AudioWorklet 實現低延遲播放。
 * - **關鍵技術**：Web Audio API、AudioWorklet、PCM 處理。
 * - **重要結論**：透過獨立的 Worklet 線程處理音訊，可以避免主線程 UI 操作造成的音訊卡頓。
 */
