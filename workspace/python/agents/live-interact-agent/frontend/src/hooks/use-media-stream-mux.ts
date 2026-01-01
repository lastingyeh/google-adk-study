/**
 * Type definition for the result of using a media stream hook.
 * 使用媒體串流 Hook 的結果類型定義。
 */
export type UseMediaStreamResult = {
  type: "webcam" | "screen"; // The type of media stream (webcam or screen share) // 媒體串流類型 (網路攝影機或螢幕分享)
  start: () => Promise<MediaStream>; // Function to start the stream // 啟動串流的函數
  stop: () => void; // Function to stop the stream // 停止串流的函數
  isStreaming: boolean; // Whether the stream is currently active // 串流目前是否處於活動狀態
  stream: MediaStream | null; // The actual MediaStream object // 實際的 MediaStream 物件
};
