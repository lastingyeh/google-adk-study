import cn from "classnames";
import { memo, ReactNode, RefObject, useEffect, useRef, useState } from "react";
import { RiSidebarFoldLine, RiSidebarUnfoldLine } from "react-icons/ri";
import Select from "react-select";
import { useLiveAPIContext } from "../../contexts/LiveAPIContext";
import { useLoggerStore } from "../../utils/store-logger";
import { UseMediaStreamResult } from "../../hooks/use-media-stream-mux";
import { useScreenCapture } from "../../hooks/use-screen-capture";
import { useWebcam } from "../../hooks/use-webcam";
import { AudioRecorder } from "../../utils/audio-recorder";
import AudioPulse from "../audio-pulse/AudioPulse";
import Logger, { LoggerFilterType } from "../logger/Logger";
import TranscriptionPreview from "../transcription-preview/TranscriptionPreview";
import "./side-panel.scss";

// Options for filtering logs
// 日誌過濾選項
const filterOptions = [
  { value: "conversations", label: "Conversations (對話)" },
  { value: "tools", label: "Tool Use (工具使用)" },
  { value: "none", label: "All (全部)" },
];

export type SidePanelProps = {
  videoRef?: RefObject<HTMLVideoElement>;
  children?: ReactNode;
  supportsVideo?: boolean;
  onVideoStreamChange?: (stream: MediaStream | null) => void;
  serverUrl?: string;
  userId?: string;
  onServerUrlChange?: (url: string) => void;
  onUserIdChange?: (userId: string) => void;
};

type MediaStreamButtonProps = {
  isStreaming: boolean;
  onIcon: string;
  offIcon: string;
  start: () => Promise<any>;
  stop: () => any;
};

// Button component for media streams (webcam/screen share)
// 媒體串流 (網路攝影機/螢幕分享) 的按鈕組件
const MediaStreamButton = memo(
  ({ isStreaming, onIcon, offIcon, start, stop }: MediaStreamButtonProps) =>
    isStreaming ? (
      <button className={cn("action-button", { active: isStreaming })} onClick={stop}>
        <span className="material-symbols-outlined">{onIcon}</span>
      </button>
    ) : (
      <button className="action-button" onClick={start}>
        <span className="material-symbols-outlined">{offIcon}</span>
      </button>
    ),
);

/**
 * SidePanel component containing controls, logs, and settings.
 * 包含控制項、日誌和設定的側邊面板組件。
 */
function SidePanel({
  videoRef,
  children,
  onVideoStreamChange = () => {},
  supportsVideo = true,
  serverUrl = "ws://localhost:8000/",
  userId = "user1",
  onServerUrlChange = () => {},
  onUserIdChange = () => {},
}: SidePanelProps) {
  const { connected, client, connect, disconnect, volume } = useLiveAPIContext();
  const [open, setOpen] = useState(true);
  const [connectionExpanded, setConnectionExpanded] = useState(false);

  // Auto-collapse connection settings when panel is closed
  // 當面板關閉時自動折疊連接設定
  useEffect(() => {
    if (!open && connectionExpanded) {
      setConnectionExpanded(false);
    }
  }, [open, connectionExpanded]);
  const loggerRef = useRef<HTMLDivElement>(null);
  const loggerLastHeightRef = useRef<number>(-1);
  const { log, logs } = useLoggerStore();

  const [textInput, setTextInput] = useState("");
  const [selectedOption, setSelectedOption] = useState<{
    value: string;
    label: string;
  } | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Control states
  // 控制狀態
  const videoStreams = [useWebcam(), useScreenCapture()];
  const [activeVideoStream, setActiveVideoStream] = useState<MediaStream | null>(null);
  const [webcam, screenCapture] = videoStreams;
  const [inVolume, setInVolume] = useState(0);
  const [audioRecorder] = useState(() => new AudioRecorder());
  const [muted, setMuted] = useState(false);
  const renderCanvasRef = useRef<HTMLCanvasElement>(null);
  const connectButtonRef = useRef<HTMLButtonElement>(null);

  // Feedback state (local to SidePanel)
  // 反饋狀態 (SidePanel 區域變數)
  const [feedbackScore, setFeedbackScore] = useState<number>(10);
  const [feedbackText, setFeedbackText] = useState<string>("");
  const [sendFeedback, setShowFeedback] = useState(false);

  // Focus connect button when disconnected
  // 斷開連接時聚焦連接按鈕
  useEffect(() => {
    if (!connected && connectButtonRef.current) {
      connectButtonRef.current.focus();
    }
  }, [connected]);

  // Update CSS variable for volume
  // 更新音量的 CSS 變數
  useEffect(() => {
    document.documentElement.style.setProperty(
      "--volume",
      `${Math.max(5, Math.min(inVolume * 200, 8))}px`,
    );
  }, [inVolume]);

  // Handle audio recording and streaming
  // 處理音訊錄製和串流
  useEffect(() => {
    const onData = (base64: string) => {
      client.sendRealtimeInput([
        {
          mimeType: "audio/pcm;rate=16000",
          data: base64,
        },
      ]);
    };
    if (connected && !muted && audioRecorder) {
      audioRecorder.on("data", onData).on("volume", setInVolume).start();
    } else {
      audioRecorder.stop();
    }
    return () => {
      audioRecorder.off("data", onData).off("volume", setInVolume);
    };
  }, [connected, client, muted, audioRecorder]);

  // Handle video streaming
  // 處理視訊串流
  useEffect(() => {
    if (videoRef && videoRef.current) {
      videoRef.current.srcObject = activeVideoStream;
    }

    let timeoutId = -1;

    function sendVideoFrame() {
      const video = videoRef && videoRef.current;
      const canvas = renderCanvasRef.current;

      if (!video || !canvas) {
        return;
      }

      const ctx = canvas.getContext("2d")!;
      canvas.width = video.videoWidth * 0.25;
      canvas.height = video.videoHeight * 0.25;
      if (canvas.width + canvas.height > 0) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const base64 = canvas.toDataURL("image/jpeg", 1.0);
        const data = base64.slice(base64.indexOf(",") + 1, Infinity);
        client.sendRealtimeInput([{ mimeType: "image/jpeg", data }]);
      }
      if (connected) {
        timeoutId = window.setTimeout(sendVideoFrame, 1000 / 0.5);
      }
    }
    if (connected && activeVideoStream !== null) {
      requestAnimationFrame(sendVideoFrame);
    }
    return () => {
      clearTimeout(timeoutId);
    };
  }, [connected, activeVideoStream, client, videoRef]);

  // Handler for swapping from one video-stream to the next
  // 切換視訊串流的處理程序
  const changeStreams = (next?: UseMediaStreamResult) => async () => {
    if (next) {
      const mediaStream = await next.start();
      setActiveVideoStream(mediaStream);
      onVideoStreamChange(mediaStream);
    } else {
      setActiveVideoStream(null);
      onVideoStreamChange(null);
    }

    videoStreams.filter((msr) => msr !== next).forEach((msr) => msr.stop());
  };

  // Submit feedback to the server
  // 提交反饋到伺服器
  const submitFeedback = async () => {
    const feedbackUrl = new URL('feedback', serverUrl.replace('ws', 'http')).href;

    try {
      const response = await fetch(feedbackUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          score: feedbackScore,
          text: feedbackText,
          run_id: client.currentRunId,
          user_id: userId,
          log_type: "feedback"
        })
      });
      if (!response.ok) {
        throw new Error(`Failed to submit feedback: Server returned status ${response.status} ${response.statusText}`);
      }

      // Clear feedback after successful submission
      // 成功提交後清除反饋
      setFeedbackScore(10);
      setFeedbackText("");
      setShowFeedback(false);
      alert("Feedback submitted successfully! (反饋提交成功！)");
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert(`Failed to submit feedback: ${error} (提交反饋失敗)`);
    }
  };

  // Scroll the log to the bottom when new logs come in
  // 當新日誌進來時滾動到底部
  useEffect(() => {
    if (loggerRef.current) {
      const el = loggerRef.current;
      const scrollHeight = el.scrollHeight;
      if (scrollHeight !== loggerLastHeightRef.current) {
        el.scrollTop = scrollHeight;
        loggerLastHeightRef.current = scrollHeight;
      }
    }
  }, [logs]);

  // Listen for log events and store them
  // 監聽日誌事件並存儲它們
  useEffect(() => {
    client.on("log", log);
    return () => {
      client.off("log", log);
    };
  }, [client, log]);

  // Handle text input submission
  // 處理文字輸入提交
  const handleSubmit = () => {
    client.send([{ text: textInput }]);

    setTextInput("");
    if (inputRef.current) {
      inputRef.current.innerText = "";
    }
  };

  return (
    <div className={`console-container ${open ? "open" : ""}`}>
      <header className="console-header">
        <h2>Console (控制台)</h2>
        {open ? (
          <button className="toggle-button" onClick={() => setOpen(!open)}>
            <RiSidebarFoldLine color="#b4b8bb" />
          </button>
        ) : (
          <button className="toggle-button" onClick={() => setOpen(!open)}>
            <RiSidebarUnfoldLine color="#b4b8bb" />
          </button>
        )}
      </header>
      <div className="console-content">
        <div className="side-panel">
          <canvas style={{ display: "none" }} ref={renderCanvasRef} />

      {/* Connection Settings Section */}
      {/* 連接設定部分 */}
      <section className="connection-settings">
        <button
          className="connection-expander"
          onClick={() => setConnectionExpanded(!connectionExpanded)}
        >
          Connection Settings (連接設定)
          <span>{connectionExpanded ? '▼' : '▶'}</span>
        </button>
        {connectionExpanded && open && (
          <div className="connection-content">
            <div className="setting-group">
              <label htmlFor="server-url">Server URL (伺服器 URL)</label>
              <input
                id="server-url"
                type="text"
                value={serverUrl}
                onChange={(e) => onServerUrlChange(e.target.value)}
                placeholder="ws://localhost:8000/"
                className="setting-input"
              />
            </div>
            <div className="setting-group">
              <label htmlFor="user-id">User ID (使用者 ID)</label>
              <input
                id="user-id"
                type="text"
                value={userId}
                onChange={(e) => onUserIdChange(e.target.value)}
                placeholder="user123"
                className="setting-input"
              />
            </div>
            <button
              onClick={() => setShowFeedback(!sendFeedback)}
              className="feedback-button"
            >
              {sendFeedback ? 'Hide Feedback (隱藏反饋)' : 'Send Feedback (發送反饋)'}
            </button>
          </div>
        )}
      </section>

      {/* Control Tray - All buttons moved here */}
      {/* 控制托盤 - 所有按鈕移至此處 */}
      <section className="control-tray">
        <nav className={cn("actions-nav", { disabled: !connected })}>
          <button
            ref={connectButtonRef}
            className={cn("action-button connect-toggle", { connected })}
            onClick={connected ? disconnect : connect}
          >
            <span className="material-symbols-outlined filled">
              {connected ? "pause" : "play_arrow"}
            </span>
          </button>

          <button
            className={cn("action-button mic-button", { active: !muted })}
            onClick={() => setMuted(!muted)}
          >
            {!muted ? (
              <span className="material-symbols-outlined filled">mic</span>
            ) : (
              <span className="material-symbols-outlined filled">mic_off</span>
            )}
          </button>

          <div className="action-button no-action outlined">
            <AudioPulse volume={volume} active={connected} hover={false} />
          </div>

          {supportsVideo && (
            <>
              <MediaStreamButton
                isStreaming={screenCapture.isStreaming}
                start={changeStreams(screenCapture)}
                stop={changeStreams()}
                onIcon="cancel_presentation"
                offIcon="present_to_all"
              />
              <MediaStreamButton
                isStreaming={webcam.isStreaming}
                start={changeStreams(webcam)}
                stop={changeStreams()}
                onIcon="videocam_off"
                offIcon="videocam"
              />
            </>
          )}
          {children}
        </nav>

        <div className="connection-status">
          <span className={cn("text-indicator", { connected })}>
            {connected ? "Streaming (串流中)" : "Disconnected (已斷開)"}
          </span>
        </div>
      </section>

      <section className="indicators">
        <Select
          className="react-select"
          classNamePrefix="react-select"
          styles={{
            control: (baseStyles) => ({
              ...baseStyles,
              background: "var(--Neutral-15)",
              color: "var(--Neutral-90)",
              minHeight: "33px",
              maxHeight: "33px",
              border: 0,
            }),
            option: (styles, { isFocused, isSelected }) => ({
              ...styles,
              backgroundColor: isFocused
                ? "var(--Neutral-30)"
                : isSelected
                  ? "var(--Neutral-20)"
                  : undefined,
            }),
          }}
          defaultValue={selectedOption}
          options={filterOptions}
          onChange={(e) => {
            setSelectedOption(e);
          }}
        />
        <div className={cn("streaming-indicator", { connected })}>
          {connected
            ? `🔵${open ? " Streaming" : ""}`
            : `⏸️${open ? " Paused" : ""}`}
        </div>
      </section>
      <div className="side-panel-container" ref={loggerRef}>
        <Logger
          filter={(selectedOption?.value as LoggerFilterType) || "none"}
        />
      </div>
      <div className={cn("input-container", { disabled: !connected })}>
        <div className="input-content">
          <textarea
            className="input-area"
            ref={inputRef}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                e.stopPropagation();
                handleSubmit();
              }
            }}
            onChange={(e) => setTextInput(e.target.value)}
            value={textInput}
          ></textarea>
          <span
            className={cn("input-content-placeholder", {
              hidden: textInput.length,
            })}
          >
            Type&nbsp;something... (輸入些什麼...)
          </span>

          <button
            className="send-button material-symbols-outlined filled"
            onClick={handleSubmit}
          >
            send
          </button>
        </div>
      </div>

      {/* Audio Pulse Bottom Section */}
      {/* 底部音訊脈衝部分 */}
      <section className="audio-pulse-bottom">
        <div className="pulse-container">
          <AudioPulse volume={volume} active={connected} hover={false} />
          <span className="pulse-label">
            {connected ? (volume > 0 ? "AI Speaking... (AI 說話中...)" : "AI Ready (AI 準備就緒)") : "Not connected (未連接)"}
          </span>
        </div>
      </section>

      {/* Feedback Overlay Section */}
      {/* 反饋覆蓋層部分 */}
      {sendFeedback && (
        <div className="feedback-section" style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          padding: '20px',
          background: 'rgba(255, 255, 255, 0.95)',
          boxShadow: '0 0 10px rgba(0,0,0,0.2)',
          borderRadius: '8px',
          zIndex: 1001,
          minWidth: '300px'
        }}>
          <h3>Provide Feedback (提供反饋)</h3>
          <div>
            <label htmlFor="feedback-score">Score (評分 0-10): </label>
            <input
              id="feedback-score"
              type="number"
              min="0"
              max="10"
              value={feedbackScore}
              onChange={(e) => setFeedbackScore(Number(e.target.value))}
              style={{margin: '0 10px'}}
            />
          </div>
          <div style={{marginTop: '10px'}}>
            <label htmlFor="feedback-text">Comments (評論): </label>
            <textarea
              id="feedback-text"
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              style={{
                width: '100%',
                height: '60px',
                margin: '5px 0'
              }}
            />
          </div>
          <button
            onClick={submitFeedback}
            style={{
              padding: '5px 10px',
              marginTop: '5px',
              cursor: 'pointer'
            }}
          >
            Submit Feedback (提交反饋)
          </button>
        </div>
      )}
        </div>
        <TranscriptionPreview open={open} />
      </div>
    </div>
  );
}

export default memo(SidePanel);
