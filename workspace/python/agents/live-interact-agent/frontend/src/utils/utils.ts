export type GetAudioContextOptions = AudioContextOptions & {
  id?: string;
};

const map: Map<string, AudioContext> = new Map();

/**
 * Retrieves or creates an AudioContext.
 * 檢索或建立 AudioContext。
 * Handles browser autoplay policies by waiting for user interaction if necessary.
 * 如有必要，透過等待使用者互動來處理瀏覽器自動播放策略。
 */
export const audioContext: (
  options?: GetAudioContextOptions,
) => Promise<AudioContext> = (() => {
  const didInteract = new Promise((res) => {
    window.addEventListener("pointerdown", res, { once: true });
    window.addEventListener("keydown", res, { once: true });
  });

  return async (options?: GetAudioContextOptions) => {
    try {
      // Try to play a silent sound to unlock audio
      // 嘗試播放靜音以解鎖音訊
      const a = new Audio();
      a.src =
        "data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA";
      await a.play();
      if (options?.id && map.has(options.id)) {
        const ctx = map.get(options.id);
        if (ctx) {
          return ctx;
        }
      }
      const ctx = new AudioContext(options);
      if (options?.id) {
        map.set(options.id, ctx);
      }
      return ctx;
    } catch (e) {
      // If play failed (likely due to autoplay policy), wait for interaction
      // 如果播放失敗 (可能是由於自動播放策略)，等待互動
      await didInteract;
      if (options?.id && map.has(options.id)) {
        const ctx = map.get(options.id);
        if (ctx) {
          return ctx;
        }
      }
      const ctx = new AudioContext(options);
      if (options?.id) {
        map.set(options.id, ctx);
      }
      return ctx;
    }
  };
})();

/**
 * Converts a Blob to JSON.
 * 將 Blob 轉換為 JSON。
 */
export const blobToJSON = (blob: Blob) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (reader.result) {
        const json = JSON.parse(reader.result as string);
        resolve(json);
      } else {
        reject("oops");
      }
    };
    reader.readAsText(blob);
  });

/**
 * Cleans a Base64 string to ensure it's valid standard Base64.
 * 清理 Base64 字串以確保它是有效的標準 Base64。
 * Handles URL-safe characters and padding.
 * 處理 URL 安全字符和填充。
 */
function cleanBase64String(base64: string): string {
  // Convert URL-safe base64 to standard base64
  // 將 URL 安全的 base64 轉換為標準 base64
  let cleaned = base64
    .replace(/-/g, '+')  // Replace - with + // 將 - 替換為 +
    .replace(/_/g, '/')  // Replace _ with / // 將 _ 替換為 /
    .replace(/[^A-Za-z0-9+/=]/g, ''); // Remove any other invalid characters // 移除任何其他無效字符

  // Ensure proper padding (base64 strings must be multiples of 4)
  // 確保適當的填充 (base64 字串長度必須是 4 的倍數)
  return cleaned + '='.repeat((4 - cleaned.length % 4) % 4);
}

/**
 * Converts a Base64 string to an ArrayBuffer.
 * 將 Base64 字串轉換為 ArrayBuffer。
 */
export function base64ToArrayBuffer(base64: string) {
  const cleanedBase64 = cleanBase64String(base64);

  try {
    var binaryString = atob(cleanedBase64);
    var bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  } catch (error) {
    console.error('Failed to decode base64 audio data:', error);
    console.error('Original base64 length:', base64.length);
    console.error('Cleaned base64 length:', cleanedBase64.length);
    console.error('First 100 chars:', base64.substring(0, 100));
    // Return empty buffer on error
    // 發生錯誤時返回空緩衝區
    return new ArrayBuffer(0);
  }
}
