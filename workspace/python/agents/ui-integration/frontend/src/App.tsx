import { useState, useRef, useEffect } from "react";
import "./App.css";

// 定義訊息物件的介面
interface Message {
  role: "user" | "assistant"; // 角色可以是使用者或助理
  content: string; // 訊息內容
}

function App() {
  // 使用 useState 管理聊天訊息陣列
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "嗨！我由 Google ADK 與 Gemini 2.0 Flash 驅動。請問有什麼可以幫您的？",
    },
  ]);
  // 管理使用者輸入框的狀態
  const [input, setInput] = useState("");
  // 管理是否正在等待後端回應的狀態
  const [isLoading, setIsLoading] = useState(false);
  // 建立一個 ref 來指向訊息列表的末端，用於自動滾動
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 使用 useEffect 在每次訊息更新時，自動滾動到最新的訊息
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 定義發送訊息的非同步函式
  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault(); // 防止表單提交時頁面重新載入
    if (!input.trim() || isLoading) return; // 如果輸入為空或正在加載，則不執行

    // 建立使用者訊息物件
    const userMessage: Message = { role: "user", content: input };
    // 將使用者訊息添加到訊息列表中
    setMessages((prev) => [...prev, userMessage]);
    setInput(""); // 清空輸入框
    setIsLoading(true); // 設定為加載中狀態

    try {
      // 使用 fetch API 向後端發送 POST 請求
      const response = await fetch("http://localhost:8000/api/copilotkit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          threadId: "tutorial29-thread", // 固定的執行緒 ID
          runId: `run-${Date.now()}`, // 唯一的運行 ID
          // 將所有訊息對應到後端要求的格式
          messages: [...messages, userMessage].map((m, i) => ({
            id: `msg-${Date.now()}-${i}`,
            role: m.role,
            content: m.content,
          })),
          state: {},
          tools: [],
          context: [],
          forwardedProps: {},
        }),
      });

      // 如果回應不成功，拋出錯誤
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // 處理 SSE (Server-Sent Events) 串流回應
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break; // 如果串流結束，則跳出迴圈

          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");

          // 逐行處理串流數據
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const jsonData = JSON.parse(line.slice(6));
                // 如果是文字訊息內容
                if (jsonData.type === "TEXT_MESSAGE_CONTENT") {
                  fullContent += jsonData.delta;
                  // 即時更新 UI 上的助理訊息
                  setMessages((prev) => {
                    const newMessages = [...prev];
                    const lastMsg = newMessages[newMessages.length - 1];
                    if (lastMsg && lastMsg.role === "assistant") {
                      // 更新最後一條助理訊息
                      lastMsg.content = fullContent;
                    } else {
                      // 新增一條助理訊息
                      newMessages.push({ role: "assistant", content: fullContent });
                    }
                    return newMessages;
                  });
                }
              } catch (e) {
                // 忽略無效的 JSON
              }
            }
          }
        }
      }

      // 確保在串流結束後，如果最後一條訊息不是助理的，則新增一條完整的助理訊息
      if (fullContent && messages[messages.length - 1]?.role !== "assistant") {
        const assistantMessage: Message = {
          role: "assistant",
          content: fullContent,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error("錯誤:", error);
      // 如果發生錯誤，顯示錯誤訊息
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "錯誤：無法取得回應" },
      ]);
    } finally {
      setIsLoading(false); // 結束加載狀態
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* 頁首 */}
      <header className="bg-white border-b border-gray-200 shadow-sm" role="banner">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div
                className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center text-2xl shadow-lg"
                aria-hidden="true"
              >
                🚀
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">ADK 快速入門</h1>
                <p className="text-sm text-gray-600">Gemini 2.0 Flash</p>
              </div>
            </div>
            <div className="flex items-center gap-2" role="status" aria-live="polite">
              <div
                className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"
                aria-hidden="true"
              ></div>
              <span className="text-sm font-medium text-emerald-700">已連線</span>
            </div>
          </div>
        </div>
      </header>

      {/* 聊天訊息 */}
      <main
        className="flex-1 overflow-y-auto"
        role="main"
        aria-label="聊天對話"
      >
        <div className="max-w-4xl mx-auto px-6 py-8">
          {messages.length === 1 && (
            <div
              className="text-center py-12"
              role="status"
              aria-label="歡迎訊息"
            >
              <div className="text-6xl mb-4" aria-hidden="true">💬</div>
              <p className="text-lg font-semibold text-gray-700 mb-2">
                開始對話
              </p>
              <p className="text-sm text-gray-600">
                試試看："什麼是 Google ADK？" 或 "解釋一下 AI 代理"
              </p>
            </div>
          )}

          <div
            role="log"
            aria-live="polite"
            aria-atomic="false"
            aria-label="聊天訊息"
          >
            {messages.map((message, index) => (
              <article
                key={index}
                className={`flex gap-3 mb-6 items-start animate-in slide-in-from-bottom-2 duration-300 ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
                role="article"
                aria-label={`${message.role === "user" ? "您的訊息" : "助理訊息"}`}
              >
                {message.role === "assistant" && (
                  <div
                    className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center flex-shrink-0 text-lg shadow-md"
                    aria-hidden="true"
                  >
                    🤖
                  </div>
                )}

                <div
                  className={`max-w-[75%] px-4 py-3 rounded-2xl leading-relaxed break-words ${
                    message.role === "user"
                      ? "bg-blue-600 text-white shadow-lg shadow-blue-600/30 rounded-br-sm"
                      : "bg-white text-gray-900 shadow-md border border-gray-100 rounded-bl-sm"
                  }`}
                  role="region"
                  aria-label={message.role === "user" ? "您的訊息" : "助理回應"}
                >
                  {message.content}
                </div>

                {message.role === "user" && (
                  <div
                    className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0 text-lg text-white shadow-md"
                    aria-hidden="true"
                  >
                    👤
                  </div>
                )}
              </article>
            ))}
          </div>

          {isLoading && (
            <div
              className="flex gap-3 items-start animate-in slide-in-from-bottom-2 duration-300"
              role="status"
              aria-live="polite"
              aria-label="助理正在輸入"
            >
              <div
                className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center flex-shrink-0 text-lg shadow-md"
                aria-hidden="true"
              >
                🤖
              </div>
              <div className="px-4 py-3 rounded-2xl rounded-bl-sm bg-white shadow-md border border-gray-100">
                <div className="flex gap-1" aria-label="載入中">
                  <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: "0s" }}></div>
                  <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                  <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: "0.4s" }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} aria-hidden="true" />
        </div>
      </main>

      {/* 輸入表單 */}
      <footer className="bg-white border-t border-gray-200 shadow-lg" role="contentinfo">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <form
            onSubmit={sendMessage}
            className="flex gap-3"
            aria-label="訊息輸入表單"
          >
            <div className="flex-1 relative">
              <label htmlFor="message-input" className="sr-only">
                輸入您的訊息
              </label>
              <input
                id="message-input"
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="輸入您的訊息..."
                disabled={isLoading}
                autoFocus
                autoComplete="off"
                aria-label="訊息輸入框"
                aria-describedby="message-hint"
                aria-invalid="false"
                className="w-full px-5 py-3 pr-12 border-2 border-gray-300 rounded-full text-base outline-none transition-all bg-white text-gray-900 placeholder-gray-500 focus:border-blue-600 focus:ring-4 focus:ring-blue-600/20 disabled:bg-gray-100 disabled:text-gray-500 disabled:cursor-not-allowed"
              />
              {input.length > 0 && (
                <div
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-sm text-gray-500 pointer-events-none"
                  aria-live="polite"
                  aria-atomic="true"
                >
                  <span className="sr-only">字數統計： </span>
                  {input.length}
                </div>
              )}
            </div>
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              aria-label={isLoading ? "正在發送訊息" : "發送訊息"}
              aria-busy={isLoading}
              className="px-6 py-3 bg-blue-600 text-white rounded-full font-semibold transition-all flex items-center gap-2 shadow-lg shadow-blue-600/30 hover:bg-blue-700 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-blue-600/40 focus:outline-none focus:ring-4 focus:ring-blue-600/20 disabled:bg-gray-300 disabled:text-gray-600 disabled:cursor-not-allowed disabled:shadow-none disabled:translate-y-0"
            >
              {isLoading ? (
                <>
                  <span>傳送中</span>
                  <span className="animate-spin" aria-hidden="true">⏳</span>
                </>
              ) : (
                <>
                  <span>傳送</span>
                  <span aria-hidden="true">🚀</span>
                </>
              )}
            </button>
          </form>
          <p
            id="message-hint"
            className="text-center text-xs text-gray-500 mt-3"
            role="contentinfo"
          >
            由 Google ADK 驅動 • 教學 29 快速入門
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
