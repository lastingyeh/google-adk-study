import "./logger.scss";

import { Part } from "@google/generative-ai";
import cn from "classnames";
import { ReactNode } from "react";
import { useLoggerStore } from "../../utils/store-logger";
import {
  ClientContentMessage,
  isClientContentMessage,
  isInterrupted,
  isModelTurn,
  isServerContenteMessage,
  isToolCallCancellationMessage,
  isToolCallMessage,
  isToolResponseMessage,
  isTurnComplete,
  ModelTurn,
  ServerContentMessage,
  StreamingLog,
  ToolCallCancellationMessage,
  ToolCallMessage,
  ToolResponseMessage,
} from "../../multimodal-live-types";

// Helper to format date object to time string
// 格式化日期物件為時間字串的輔助函數
const formatTime = (d: Date) => d.toLocaleTimeString().slice(0, -3);

// Component to render a single log entry
// 渲染單個日誌條目的組件
const LogEntry = ({
  log,
  MessageComponent,
}: {
  log: StreamingLog;
  MessageComponent: ({
    message,
  }: {
    message: StreamingLog["message"];
  }) => ReactNode;
}): JSX.Element => (
  <li
    className={cn(
      `plain-log`,
      `source-${log.type.slice(0, log.type.indexOf("."))}`,
      {
        receive: log.type.includes("receive"),
        send: log.type.includes("send"),
      },
    )}
  >
    <span className="timestamp">{formatTime(log.date)}</span>
    <span className="source">{log.type}</span>
    <span className="message">
      <MessageComponent message={log.message} />
    </span>
    {log.count && <span className="count">{log.count}</span>}
  </li>
);

// Render simple text message
// 渲染純文字訊息
const PlainTextMessage = ({
  message,
}: {
  message: StreamingLog["message"];
}) => <span>{message as string}</span>;

type Message = { message: StreamingLog["message"] };

// Render any other message type as JSON
// 將任何其他訊息類型渲染為 JSON
const AnyMessage = ({ message }: Message) => (
  <pre>{JSON.stringify(message, null, "  ")}</pre>
);

// Render content part (text or inline data)
// 渲染內容部分 (文字或內聯數據)
const RenderPart = ({ part }: { part: Part }) =>
  part.text && part.text.length ? (
    <p className="part part-text">{part.text}</p>
  ) : (
    <div className="part part-inlinedata">
      <h5>Inline Data: {part.inlineData?.mimeType}</h5>
    </div>
  );

// Render client content log
// 渲染客戶端內容日誌
const ClientContentLog = ({ message }: Message) => {
  const { turns, turnComplete } = (message as ClientContentMessage)
    .clientContent;
  return (
    <div className="rich-log client-content user">
      <h4 className="roler-user">User (使用者)</h4>
      {turns.map((turn, i) => (
        <div key={`message-turn-${i}`}>
          {turn.parts
            .filter((part) => !(part.text && part.text === "\n"))
            .map((part, j) => (
              <RenderPart part={part} key={`message-turh-${i}-part-${j}`} />
            ))}
        </div>
      ))}
      {!turnComplete ? <span>turnComplete: false</span> : ""}
    </div>
  );
};

// Render tool call log
// 渲染工具調用日誌
const ToolCallLog = ({ message }: Message) => {
  const { toolCall } = message as ToolCallMessage;
  return (
    <div className={cn("rich-log tool-call")}>
      <h4 className="role-tool">Tool Call (工具調用)</h4>
      {toolCall.functionCalls.map((fc) => (
        <div key={fc.id} className="part part-functioncall">
          <h5>Function: {fc.name}</h5>
          <div className="function-details">
            <div><strong>ID:</strong> {fc.id}</div>
            <div><strong>Args:</strong></div>
            <pre>{JSON.stringify(fc.args, null, 2)}</pre>
          </div>
        </div>
      ))}
    </div>
  );
};

// Render tool call cancellation log
// 渲染工具調用取消日誌
const ToolCallCancellationLog = ({ message }: Message): JSX.Element => (
  <div className={cn("rich-log tool-call-cancellation")}>
    <span>
      {" "}
      ids:{" "}
      {(message as ToolCallCancellationMessage).toolCallCancellation.ids.map(
        (id) => (
          <span className="inline-code" key={`cancel-${id}`}>
            "{id}"
          </span>
        ),
      )}
    </span>
  </div>
);

// Render tool response log
// 渲染工具回應日誌
const ToolResponseLog = ({ message }: Message): JSX.Element => (
  <div className={cn("rich-log tool-response")}>
    {(message as ToolResponseMessage).toolResponse.functionResponses.map(
      (fc) => (
        <div key={`tool-response-${fc.id}`} className="part">
          <h5>Function Response: {fc.id}</h5>
          <pre>{JSON.stringify(fc.response, null, "  ")}</pre>
        </div>
      ),
    )}
  </div>
);

// Render model turn log
// 渲染模型輪次日誌
const ModelTurnLog = ({ message }: Message): JSX.Element => {
  const serverContent = (message as ServerContentMessage).serverContent;
  const { modelTurn } = serverContent as ModelTurn;
  const { parts } = modelTurn;

  return (
    <div className="rich-log model-turn model">
      <h4 className="role-model">Model (模型)</h4>
      {parts
        .filter((part) => !(part.text && part.text === "\n"))
        .map((part, j) => (
          <RenderPart part={part} key={`model-turn-part-${j}`} />
        ))}
    </div>
  );
};

// Helper to create a plain text log component
// 建立純文字日誌組件的輔助函數
const CustomPlainTextLog = (msg: string) => () => (
  <PlainTextMessage message={msg} />
);

export type LoggerFilterType = "conversations" | "tools" | "none";

export type LoggerProps = {
  filter: LoggerFilterType;
};

// Define filter functions for different log types
// 為不同的日誌類型定義過濾函數
const filters: Record<LoggerFilterType, (log: StreamingLog) => boolean> = {
  tools: (log: StreamingLog) =>
    isToolCallMessage(log.message) ||
    isToolResponseMessage(log.message) ||
    isToolCallCancellationMessage(log.message),
  conversations: (log: StreamingLog) =>
    isClientContentMessage(log.message) || isServerContenteMessage(log.message),
  none: () => true,
};

// Determine the component to render based on the log message type
// 根據日誌訊息類型決定要渲染的組件
const component = (log: StreamingLog) => {
  if (typeof log.message === "string") {
    return PlainTextMessage;
  }
  if (isClientContentMessage(log.message)) {
    return ClientContentLog;
  }
  if (isToolCallMessage(log.message)) {
    return ToolCallLog;
  }
  if (isToolCallCancellationMessage(log.message)) {
    return ToolCallCancellationLog;
  }
  if (isToolResponseMessage(log.message)) {
    return ToolResponseLog;
  }
  if (isServerContenteMessage(log.message)) {
    const { serverContent } = log.message;
    if (isInterrupted(serverContent)) {
      return CustomPlainTextLog("interrupted");
    }
    if (isTurnComplete(serverContent)) {
      return CustomPlainTextLog("turnComplete");
    }
    if (isModelTurn(serverContent)) {
      return ModelTurnLog;
    }
  }
  return AnyMessage;
};

/**
 * Logger component to display streaming logs
 * 用於顯示串流日誌的 Logger 組件
 */
export default function Logger({ filter = "none" }: LoggerProps) {
  const { logs } = useLoggerStore();

  const filterFn = filters[filter];

  return (
    <div className="logger">
      <ul className="logger-list">
        {logs.filter(filterFn).map((log, key) => {
          return (
            <LogEntry MessageComponent={component(log)} log={log} key={key} />
          );
        })}
      </ul>
    </div>
  );
}
