/**
 * A registry to map attached worklets by their audio-context
 * any module using `audioContext.audioWorklet.addModule(` should register the worklet here
 * 依據 AudioContext 映射已附加的 Worklet 的註冊表
 * 任何使用 `audioContext.audioWorklet.addModule(` 的模組都應在此註冊 Worklet
 */
export type WorkletGraph = {
  node?: AudioWorkletNode; // The AudioWorkletNode instance // AudioWorkletNode 實例
  handlers: Array<(this: MessagePort, ev: MessageEvent) => any>; // Event handlers for the worklet // Worklet 的事件處理程序
};

// Map to store registered worklets for each AudioContext
// 用於儲存每個 AudioContext 的已註冊 Worklet 的 Map
export const registeredWorklets: Map<
  AudioContext,
  Record<string, WorkletGraph>
> = new Map();

/**
 * Creates a Blob URL from worklet source code string.
 * 從 Worklet 原始碼字串建立 Blob URL。
 * This allows loading AudioWorklets from strings/variables instead of external files.
 * 這允許從字串/變數載入 AudioWorklets，而不是從外部檔案。
 *
 * @param workletName The name of the AudioWorkletProcessor to register
 *                    要註冊的 AudioWorkletProcessor 名稱
 * @param workletSrc The source code of the AudioWorkletProcessor class
 *                   AudioWorkletProcessor 類別的原始碼
 * @returns A Blob URL representing the worklet script
 *          代表 Worklet 腳本的 Blob URL
 */
export const createWorketFromSrc = (
  workletName: string,
  workletSrc: string,
) => {
  const script = new Blob(
    [`registerProcessor("${workletName}", ${workletSrc})`],
    {
      type: "application/javascript",
    },
  );

  return URL.createObjectURL(script);
};
