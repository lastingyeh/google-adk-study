import { useEffect, useRef, useState } from "react";
import { useLiveAPIContext } from "../../contexts/LiveAPIContext";
import cn from "classnames";
import "./transcription-preview.scss";

export type TranscriptionPreviewProps = {
  open: boolean;
};

/**
 * Component to display real-time input and output transcriptions.
 * 用於顯示即時輸入和輸出轉錄的組件。
 */
export default function TranscriptionPreview({ open }: TranscriptionPreviewProps) {
  const { client } = useLiveAPIContext();
  const [inputTexts, setInputTexts] = useState<string[]>([]);
  const [outputTexts, setOutputTexts] = useState<string[]>([]);
  const inputRef = useRef<HTMLDivElement>(null);
  const outputRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Handler for new input transcriptions
    // 新輸入轉錄的處理程序
    const handleInputTranscription = (text: string) => {
      setInputTexts((prev) => [...prev, text]);
      // Auto-scroll to bottom
      // 自動滾動到底部
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.scrollTop = inputRef.current.scrollHeight;
        }
      }, 0);
    };

    // Handler for new output transcriptions
    // 新輸出轉錄的處理程序
    const handleOutputTranscription = (text: string) => {
      setOutputTexts((prev) => [...prev, text]);
      // Auto-scroll to bottom
      // 自動滾動到底部
      setTimeout(() => {
        if (outputRef.current) {
          outputRef.current.scrollTop = outputRef.current.scrollHeight;
        }
      }, 0);
    };

    client.on("inputtranscription", handleInputTranscription);
    client.on("outputtranscription", handleOutputTranscription);

    return () => {
      client.off("inputtranscription", handleInputTranscription);
      client.off("outputtranscription", handleOutputTranscription);
    };
  }, [client]);

  return (
    <div className={cn("transcription-preview", { open })}>
      {/* Input Transcription Section */}
      {/* 輸入轉錄區域 */}
      <div className="transcription-section input-section">
        <div className="transcription-header">
          <span className="material-symbols-outlined">mic</span>
          <h3>Input (輸入)</h3>
        </div>
        <div className="transcription-content" ref={inputRef}>
          {inputTexts.length > 0 ? (
            <>
              {inputTexts.map((text, index) => (
                <p key={index} className={index === inputTexts.length - 1 ? "current" : "previous"}>
                  {text}
                </p>
              ))}
            </>
          ) : (
            <p className="placeholder">Listening... (聆聽中...)</p>
          )}
        </div>
      </div>

      {/* Output Transcription Section */}
      {/* 輸出轉錄區域 */}
      <div className="transcription-section output-section">
        <div className="transcription-header">
          <span className="material-symbols-outlined">volume_up</span>
          <h3>Output (輸出)</h3>
        </div>
        <div className="transcription-content" ref={outputRef}>
          {outputTexts.length > 0 ? (
            <>
              {outputTexts.map((text, index) => (
                <p key={index} className={index === outputTexts.length - 1 ? "current" : "previous"}>
                  {text}
                </p>
              ))}
            </>
          ) : (
            <p className="placeholder">Waiting for response... (等待回應...)</p>
          )}
        </div>
      </div>
    </div>
  );
}
