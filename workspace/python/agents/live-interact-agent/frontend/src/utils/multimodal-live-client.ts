import { Content, GenerativeContentBlob, Part } from "@google/generative-ai";
import { EventEmitter } from "eventemitter3";
import { difference } from "lodash";
import {
  isInterrupted,
  isModelTurn,
  isServerContenteMessage,
  isSetupCompleteMessage,
  isToolCallCancellationMessage,
  isToolCallMessage,
  isTurnComplete,
  isAdkEvent,
  isInputTranscription,
  isOutputTranscription,
  LiveIncomingMessage,
  ModelTurn,
  ServerContent,
  StreamingLog,
  ToolCall,
  ToolCallCancellation,
  ToolResponseMessage,
  type LiveConfig,
  type AdkEvent,
} from "../multimodal-live-types";
import { blobToJSON, base64ToArrayBuffer } from "./utils";

/**
 * the events that this client will emit
 * 此客戶端將發出的事件
 */
interface MultimodalLiveClientEventTypes {
  open: () => void;
  log: (log: StreamingLog) => void;
  close: (event: CloseEvent) => void;
  audio: (data: ArrayBuffer) => void;
  content: (data: ServerContent) => void;
  interrupted: () => void;
  setupcomplete: () => void;
  status: (status: string) => void;
  turncomplete: () => void;
  toolcall: (toolCall: ToolCall) => void;
  toolcallcancellation: (toolcallCancellation: ToolCallCancellation) => void;
  // ADK events
  // ADK 事件
  inputtranscription: (text: string) => void;
  outputtranscription: (text: string) => void;
  adkevent: (event: AdkEvent) => void;
}

export type MultimodalLiveAPIClientConnection = {
  url?: string;
  runId?: string;
  userId?: string;
};

/**
 * A event-emitting class that manages the connection to the websocket and emits
 * events to the rest of the application.
 * If you dont want to use react you can still use this.
 * 一個事件發射類別，用於管理 WebSocket 連接並向應用程式的其他部分發出事件。
 * 如果您不想使用 React，仍然可以使用此類別。
 */
export class MultimodalLiveClient extends EventEmitter<MultimodalLiveClientEventTypes> {
  public ws: WebSocket | null = null;
  protected config: LiveConfig | null = null;
  public url: string = "";
  private runId: string;
  private userId?: string;
  private firstContentSent: boolean = false;
  private audioChunksSent: number = 0;
  private lastAudioSendTime: number = 0;
  private readonly INITIAL_SEND_INTERVAL_MS = 300; // Start slow: 300ms between chunks // 初始發送間隔：300ms
  private readonly NORMAL_SEND_INTERVAL_MS = 125; // Normal rate: 125ms (8 chunks/sec) // 正常速率：125ms (每秒 8 個區塊)
  private readonly RAMPUP_CHUNKS = 10; // Number of chunks to send at reduced rate // 以降低速率發送的區塊數量

  constructor({ url, userId, runId }: MultimodalLiveAPIClientConnection) {
    super();
    const defaultWsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;
    url = url || defaultWsUrl;
    this.url = new URL("ws", url).href;
    this.userId = userId;
    this.runId = runId || crypto.randomUUID(); // Ensure runId is always a string by providing default // 確保 runId 始終為字串
    this.send = this.send.bind(this);
  }

  get currentRunId(): string {
    return this.runId;
  }

  log(type: string, message: StreamingLog["message"]) {
    const log: StreamingLog = {
      date: new Date(),
      type,
      message,
    };
    this.emit("log", log);
  }

  connect(newRunId?: string): Promise<boolean> {
    const ws = new WebSocket(this.url);

    // Update runId if provided
    // 如果提供了 newRunId，則更新 runId
    if (newRunId) {
      this.runId = newRunId;
    }

    // Reset connection state
    // 重置連接狀態
    this.firstContentSent = false;
    this.audioChunksSent = 0;
    this.lastAudioSendTime = 0;

    ws.addEventListener("message", async (evt: MessageEvent) => {
      if (evt.data instanceof Blob) {
        this.receive(evt.data);
      } else if (typeof evt.data === "string") {
        try {
          const jsonData = JSON.parse(evt.data);

          // Handle different message types from backend
          // 處理來自後端的不同訊息類型
          if (jsonData.setupComplete) {
            this.emit("setupcomplete");
            this.log("server.setupComplete", "Session ready");
          } else if (jsonData.serverContent) {
            // Handle serverContent messages
            // 處理伺服器內容訊息
            this.receive(new Blob([JSON.stringify(jsonData)], {type: 'application/json'}));
          } else if (jsonData.toolCall) {
            // Handle tool calls
            // 處理工具調用
            this.receive(new Blob([JSON.stringify(jsonData)], {type: 'application/json'}));
          } else if (jsonData.status) {
            this.log("server.status", jsonData.status);
            console.log("Status:", jsonData.status);
          } else if (jsonData.error) {
            this.log("server.error", jsonData.error);
            console.error("Server error:", jsonData.error);
          } else {
            // Try to process as a regular message
            // 嘗試作為普通訊息處理
            this.receive(new Blob([JSON.stringify(jsonData)], {type: 'application/json'}));
          }
        } catch (error) {
          console.error("Error parsing message:", error);
        }
      } else {
        console.log("Unhandled message type:", evt);
      }
    });

    return new Promise((resolve, reject) => {
      const onError = (ev: Event) => {
        this.disconnect(ws);
        const message = `Could not connect to "${this.url}"`;
        this.log(`server.${ev.type}`, message);
        reject(new Error(message));
      };
      ws.addEventListener("error", onError);
      ws.addEventListener("open", (ev: Event) => {
        this.log(`client.${ev.type}`, `connected to socket`);
        this.emit("open");

        this.ws = ws;
        // Send initial setup message with user_id for backend
        // 發送帶有 user_id 的初始設置訊息給後端
        const setupMessage = {
          user_id: this.userId || "default_user",
          setup: {
            run_id: this.runId,
            user_id: this.userId || "default_user",
          },
        };
        this._sendDirect(setupMessage);
        ws.removeEventListener("error", onError);
        ws.addEventListener("close", (ev: CloseEvent) => {
          console.log(ev);
          this.disconnect(ws);
          let reason = ev.reason || "";
          if (reason.toLowerCase().includes("error")) {
            const prelude = "ERROR]";
            const preludeIndex = reason.indexOf(prelude);
            if (preludeIndex > 0) {
              reason = reason.slice(
                preludeIndex + prelude.length + 1,
                Infinity,
              );
            }
          }
          this.log(
            `server.${ev.type}`,
            `disconnected ${reason ? `with reason: ${reason}` : ``}`,
          );
          this.emit("close", ev);
        });
        resolve(true);
      });
    });
  }

  disconnect(ws?: WebSocket) {
    // could be that this is an old websocket and there's already a new instance
    // only close it if its still the correct reference
    // 可能是舊的 WebSocket，且已經有新的實例
    // 只有在引用正確時才關閉它
    if ((!ws || this.ws === ws) && this.ws) {
      this.ws.close();
      this.ws = null;
      this.log("client.close", `Disconnected`);
      return true;
    }
    return false;
  }

  protected async receive(blob: Blob) {
    const response = (await blobToJSON(blob)) as LiveIncomingMessage;
    console.log("Parsed response:", response);

    if (isToolCallMessage(response)) {
      this.log("server.toolCall", response);
      this.emit("toolcall", response.toolCall);
      return;
    }
    if (isToolCallCancellationMessage(response)) {
      this.log("receive.toolCallCancellation", response);
      this.emit("toolcallcancellation", response.toolCallCancellation);
      return;
    }

    if (isSetupCompleteMessage(response)) {
      this.log("server.send", "setupComplete");
      this.emit("setupcomplete");
      return;
    }

    // this json also might be `contentUpdate { interrupted: true }`
    // or contentUpdate { end_of_turn: true }
    // 此 JSON 也可能是 `contentUpdate { interrupted: true }`
    // 或 contentUpdate { end_of_turn: true }
    if (isServerContenteMessage(response)) {
      const { serverContent } = response;
      if (isInterrupted(serverContent)) {
        this.log("receive.serverContent", "interrupted");
        this.emit("interrupted");
        return;
      }
      if (isTurnComplete(serverContent)) {
        this.log("server.send", "turnComplete");
        this.emit("turncomplete");
        //plausible there's more to the message, continue
        // 訊息中可能還有更多內容，繼續
      }

      if (isModelTurn(serverContent)) {
        let parts: Part[] = serverContent.modelTurn.parts;

        // when its audio that is returned for modelTurn (check both camelCase and snake_case)
        // 當返回的是音訊內容時 (檢查駝峰式和蛇形命名)
        const audioParts = parts.filter(
          (p: any) => {
            const inlineData = p.inlineData || p.inline_data;
            const mimeType = inlineData?.mimeType || inlineData?.mime_type;
            return inlineData && mimeType && mimeType.startsWith("audio/pcm");
          }
        );
        const base64s = audioParts.map((p: any) => {
          const inlineData = p.inlineData || p.inline_data;
          return inlineData?.data;
        });

        // strip the audio parts out of the modelTurn
        // 從 modelTurn 中移除音訊部分
        const otherParts = difference(parts, audioParts);
        // console.log("otherParts", otherParts);

        base64s.forEach((b64) => {
          if (b64) {
            const data = base64ToArrayBuffer(b64);
            this.emit("audio", data);
            this.log(`server.audio`, `buffer (${data.byteLength})`);
          }
        });
        if (!otherParts.length) {
          return;
        }

        parts = otherParts;

        const content: ModelTurn = { modelTurn: { parts } };
        this.emit("content", content);
        this.log(`server.content`, response);
      }
    } else if (isAdkEvent(response)) {
      // Handle ADK events
      // 處理 ADK 事件
      this.emit("adkevent", response);

      // Handle specific ADK event types
      // 處理特定 ADK 事件類型
      if (isInputTranscription(response)) {
        this.emit("inputtranscription", response.input_transcription!.text);
      }

      if (isOutputTranscription(response)) {
        this.emit("outputtranscription", response.output_transcription!.text);
      }

      // Handle ADK content (text responses from agent)
      // 處理 ADK 內容 (代理的文字回應)
      if (response.content && response.content.parts) {
        const parts = response.content.parts;

        // Extract function calls for tool call logging
        // 提取用於工具調用日誌記錄的函數調用
        const functionCallParts = parts.filter((p: any) => p.function_call);

        // Log function calls as tool calls for the console
        // 在控制台中將函數調用記錄為工具調用
        if (functionCallParts.length > 0) {
          const functionCalls = functionCallParts.map((p: any) => ({
            id: p.function_call.id,
            name: p.function_call.name,
            args: p.function_call.args || {}
          }));

          const toolCallMessage = {
            toolCall: {
              functionCalls: functionCalls
            }
          };

          this.log("server.toolCall", toolCallMessage);
          this.emit("toolcall", toolCallMessage.toolCall);
        }

        // Extract audio parts for playing (check both camelCase and snake_case)
        // 提取用於播放的音訊部分 (檢查駝峰式和蛇形命名)
        const audioParts = parts.filter(
          (p: any) => {
            const inlineData = p.inlineData || p.inline_data;
            const mimeType = inlineData?.mimeType || inlineData?.mime_type;
            return inlineData && mimeType && mimeType.startsWith("audio/");
          }
        );

        // Play audio if present
        // 如果存在則播放音訊
        audioParts.forEach((audioPart: any) => {
          const inlineData = audioPart.inlineData || audioPart.inline_data;
          if (inlineData && inlineData.data) {
            const audioData = base64ToArrayBuffer(inlineData.data);

            // Only emit audio if we have a valid buffer with data
            // 僅在有有效數據緩衝區時發出音訊
            if (audioData.byteLength > 0) {
              this.emit("audio", audioData);
              this.log(`server.audio`, `buffer (${audioData.byteLength}) - ${inlineData.mime_type || inlineData.mimeType}`);
            } else {
              this.log(`server.audio`, `invalid audio buffer - skipped`);
            }
          }
        });

        // Send content for other parts (text, etc.) - exclude function calls and audio
        // 發送其他部分的內容 (文字等) - 排除函數調用和音訊
        const nonAudioNonFunctionParts = parts.filter(
          (p: any) => {
            const inlineData = p.inlineData || p.inline_data;
            const mimeType = inlineData?.mimeType || inlineData?.mime_type;
            const hasAudio = inlineData && mimeType && mimeType.startsWith("audio/");
            const hasFunctionCall = p.function_call;
            return !hasAudio && !hasFunctionCall;
          }
        );

        if (nonAudioNonFunctionParts.length > 0) {
          const content: ModelTurn = { modelTurn: { parts: nonAudioNonFunctionParts } };
          this.emit("content", content);
          this.log("server.content", `content with ${nonAudioNonFunctionParts.length} non-audio, non-function parts`);
        }
      }

      // Handle turn complete
      // 處理輪次完成
      if (response.turn_complete) {
        this.emit("turncomplete");
        this.log("server.turncomplete", "ADK turn complete");
      }

      // Handle interruption
      // 處理中斷
      if (response.interrupted) {
        this.emit("interrupted");
        this.log("server.interrupted", "ADK interrupted");
      }
    } else {
      // Ignore webpack dev server HMR messages
      // 忽略 webpack 開發伺服器 HMR 訊息
      const hmrTypes = ["liveReload", "reconnect", "overlay", "hash", "ok", "warnings", "errors", "invalid", "still-ok", "hot"];
      if (typeof (response as any).type === "string" && hmrTypes.includes((response as any).type)) {
        return;
      }
      console.log("received unmatched message", response);
      this.log("received unmatched message", response);
    }
  }

  /**
   * send realtimeInput, this is base64 chunks of "audio/pcm" and/or "image/jpg"
   * 發送即時輸入，這是 "audio/pcm" 和/或 "image/jpg" 的 base64 區塊
   */
  sendRealtimeInput(chunks: GenerativeContentBlob[]) {
    // Don't send if WebSocket is not open - this prevents flooding the queue
    // during connection setup
    // 如果 WebSocket 未開啟則不發送 - 這可防止在連接設置期間淹沒隊列
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      return;
    }

    let hasAudio = false;
    let hasVideo = false;
    for (let i = 0; i < chunks.length; i++) {
      const ch = chunks[i];
      if (ch.mimeType.includes("audio")) {
        hasAudio = true;
      }
      if (ch.mimeType.includes("image")) {
        hasVideo = true;
      }
      if (hasAudio && hasVideo) {
        break;
      }
    }

    // Throttle audio chunks during initial connection phase
    // 在初始連接階段限制音訊區塊
    if (hasAudio && !hasVideo) {
      const now = Date.now();

      // Calculate required interval based on how many chunks we've sent
      // 根據我們發送的區塊數量計算所需的間隔
      const requiredInterval = this.audioChunksSent < this.RAMPUP_CHUNKS
        ? this.INITIAL_SEND_INTERVAL_MS
        : this.NORMAL_SEND_INTERVAL_MS;

      // If not enough time has passed since last send, drop this chunk
      // 如果自上次發送以來經過的時間不足，則丟棄此區塊
      if (this.lastAudioSendTime > 0 && (now - this.lastAudioSendTime) < requiredInterval) {
        return;
      }

      this.lastAudioSendTime = now;
      this.audioChunksSent++;
    }

    const message =
      hasAudio && hasVideo
        ? "audio + video"
        : hasAudio
          ? "audio"
          : hasVideo
            ? "video"
            : "unknown";

    // Convert to LiveRequest format for backend
    // 轉換為後端的 LiveRequest 格式
    for (const chunk of chunks) {
      let data: any = {
        blob: {
          mimeType: chunk.mimeType,
          data: chunk.data,
        },
      };

      // For remote mode: wrap first content in {user_id, live_request} format
      // 對於遠端模式：將第一個內容包裝在 {user_id, live_request} 格式中
      if (!this.firstContentSent) {
        data = {
          user_id: this.userId || "default_user",
          live_request: data,
        };
        this.firstContentSent = true;
      }

      this._sendDirect(data);
    }
    this.log(`client.realtimeInput`, message);
  }

  /**
   *  send a response to a function call and provide the id of the functions you are responding to
   *  發送對函數調用的回應，並提供您正在回應的函數 ID
   */
  sendToolResponse(toolResponse: ToolResponseMessage["toolResponse"]) {
    const message: ToolResponseMessage = {
      toolResponse,
    };

    this._sendDirect(message);
    this.log(`client.toolResponse`, message);
  }

  /**
   * send normal content parts such as { text }
   * 發送普通內容部分，例如 { text }
   */
  send(parts: Part | Part[], _turnComplete: boolean = true) {
    parts = Array.isArray(parts) ? parts : [parts];
    const content: Content = {
      role: "user",
      parts,
    };

    // Convert to LiveRequest format for backend
    // 轉換為後端的 LiveRequest 格式
    let data: any = {
      content: content,
    };

    // For remote mode: wrap first content in {user_id, live_request} format
    // 對於遠端模式：將第一個內容包裝在 {user_id, live_request} 格式中
    if (!this.firstContentSent) {
      data = {
        user_id: this.userId || "default_user",
        live_request: data,
      };
      this.firstContentSent = true;
    }

    this._sendDirect(data);
    this.log(`client.send`, `content with ${parts.length} parts`);
  }

  /**
   *  used internally to send all messages
   *  don't use directly unless trying to send an unsupported message type
   *  內部使用，用於發送所有訊息
   *  除非嘗試發送不支援的訊息類型，否則請勿直接使用
   */
  _sendDirect(request: object) {
    if (!this.ws) {
      throw new Error("WebSocket is not connected (WebSocket 未連接)");
    }
    const str = JSON.stringify(request);
    this.ws.send(str);
  }
}
