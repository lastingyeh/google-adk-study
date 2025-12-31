import { useRef, useState } from "react";
import "./App.scss";
import { LiveAPIProvider } from "./contexts/LiveAPIContext";
import SidePanel from "./components/side-panel/SidePanel";
import cn from "classnames";

// In development mode (frontend on :8501), connect to backend on :8000
// 在開發模式下 (前端運行於 :8501)，連接到後端的 :8000 端口
const isDevelopment = window.location.port === '8501';
const defaultHost = isDevelopment ? `${window.location.hostname}:8000` : window.location.host;
const defaultUri = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${defaultHost}/`;

function App() {
  // Video element reference
  // 視訊元素的參考
  const videoRef = useRef<HTMLVideoElement>(null);
  // State for the video stream
  // 視訊串流的狀態
  const [videoStream, setVideoStream] = useState<MediaStream | null>(null);
  // State for the WebSocket server URL
  // WebSocket 伺服器 URL 的狀態
  const [serverUrl, setServerUrl] = useState<string>(defaultUri);
  // State for the user ID
  // 使用者 ID 的狀態
  const [userId, setUserId] = useState<string>("user1");

  return (
    <div className="App">
      {/* Provider for the Live API context */}
      {/* Live API 上下文的提供者 */}
      <LiveAPIProvider url={serverUrl} userId={userId}>
        <div className="streaming-console">
          {/* Side panel component containing controls */}
          {/* 包含控制項的側邊面板組件 */}
          <SidePanel
            videoRef={videoRef}
            supportsVideo={true}
            onVideoStreamChange={setVideoStream}
            serverUrl={serverUrl}
            userId={userId}
            onServerUrlChange={setServerUrl}
            onUserIdChange={setUserId}
          />
          <main>
            <div className="main-app-area">
              {/* Video element to display the stream */}
              {/* 用於顯示串流的視訊元素 */}
              <video
                className={cn("stream", {
                  hidden: !videoRef.current || !videoStream,
                })}
                ref={videoRef}
                autoPlay
                playsInline
              />
            </div>
          </main>
        </div>
      </LiveAPIProvider>
    </div>
  );
}

export default App;
