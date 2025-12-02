import { useState, useRef, useEffect } from "react";
import { Line, Bar, Scatter } from "react-chartjs-2";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import rehypeRaw from "rehype-raw";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import "./App.css";
import "highlight.js/styles/github-dark.css";

// 註冊 Chart.js 元件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface Message {
  role: "user" | "assistant";
  content: string;
  chartData?: ChartData;
}

interface ChartData {
  chart_type: string;
  data: {
    labels: string[];
    values: number[];
  };
  options: {
    x_label: string;
    y_label: string;
    title: string;
  };
  status?: string;
  report?: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "嗨！我是您的**數據分析助手**，由 Google ADK 與 Gemini 2.0 Flash 驅動。📊\n\n上傳 CSV 檔案或請我分析數據！",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [currentChart, setCurrentChart] = useState<ChartData | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 從 Agent 回應中提取圖表數據
  const extractChartData = (content: string): ChartData | null => {
    try {
      // 在回應中尋找包含 chart_type 的 JSON 物件
      const jsonMatch = content.match(/\{[^{}]*"chart_type"[^{}]*"data"[^{}]*\}/s);
      if (jsonMatch) {
        const chartData = JSON.parse(jsonMatch[0]);
        if (chartData.chart_type && chartData.data) {
          return chartData;
        }
      }
    } catch (e) {
      console.error("無法提取圖表數據：", e);
    }
    return null;
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/copilotkit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          threadId: "data-analysis-thread",
          runId: `run-${Date.now()}`,
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

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // 處理 SSE 串流回應
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";
      let toolResults: Record<string, any> = {};

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const jsonData = JSON.parse(line.slice(6));
                console.log("📡 收到事件：", jsonData.type, jsonData);

                // 處理文字內容串流
                if (jsonData.type === "TEXT_MESSAGE_CONTENT") {
                  fullContent += jsonData.delta;
                  // 即時更新訊息
                  setMessages((prev) => {
                    const newMessages = [...prev];
                    const lastMsg = newMessages[newMessages.length - 1];
                    if (lastMsg && lastMsg.role === "assistant") {
                      lastMsg.content = fullContent;
                    } else {
                      newMessages.push({ role: "assistant", content: fullContent });
                    }
                    return newMessages;
                  });
                }

                // 處理工具調用結果（圖表數據存在於此！）
                if (jsonData.type === "TOOL_CALL_RESULT") {
                  console.log(" 收到 TOOL_CALL_RESULT 事件！");
                  console.log("   完整事件物件：", JSON.stringify(jsonData, null, 2));
                  console.log("   內容類型：", typeof jsonData.content);
                  console.log("   內容值：", jsonData.content);

                  try {
                    // 解析工具結果內容
                    const resultContent = typeof jsonData.content === 'string'
                      ? JSON.parse(jsonData.content)
                      : jsonData.content;

                    console.log("   解析後內容：", resultContent);
                    console.log("   是否有 chart_type？", !!resultContent.chart_type);

                    toolResults[jsonData.tool_call_id] = resultContent;

                    // 檢查這是否為圖表建立結果
                    if (resultContent && resultContent.chart_type) {
                      console.log("✅ 發現圖表數據！");
                      console.log("   圖表類型：", resultContent.chart_type);
                      console.log("   圖表數據：", resultContent);

                      setCurrentChart(resultContent);
                      console.log("   已設定 currentChart 狀態");

                      setMessages((prev) => {
                        const newMessages = [...prev];
                        const lastMsg = newMessages[newMessages.length - 1];
                        console.log("   最後訊息角色：", lastMsg?.role);
                        if (lastMsg && lastMsg.role === "assistant") {
                          lastMsg.chartData = resultContent;
                          console.log("   已將 chartData 附加到訊息");
                        }
                        return newMessages;
                      });
                    } else {
                      console.log("❌ 結果中未發現 chart_type");
                      console.log("   結果鍵值：", Object.keys(resultContent));
                    }
                  } catch (e) {
                    console.error("❌ 解析工具結果錯誤：", e);
                    console.error("   原始內容：", jsonData.content);
                  }
                }
              } catch (e) {
                // 跳過無效 JSON
              }
            }
          }
        }
      }

      // 備案：如果在工具結果中未找到圖表，則從文字內容中提取
      if (!currentChart) {
        const chartData = extractChartData(fullContent);
        if (chartData) {
          console.log("📊 從文字提取圖表數據（備案）：", chartData);
          setCurrentChart(chartData);
          setMessages((prev) => {
            const newMessages = [...prev];
            const lastMsg = newMessages[newMessages.length - 1];
            if (lastMsg && lastMsg.role === "assistant") {
              lastMsg.chartData = chartData;
            }
            return newMessages;
          });
        }
      }

      // 確保加入最後訊息（如果在串流中尚未加入）
      if (fullContent && messages[messages.length - 1]?.role !== "assistant") {
        const assistantMessage: Message = {
          role: "assistant",
          content: fullContent,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error("錯誤：", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "錯誤：無法從伺服器獲得回應" },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    if (!file.name.endsWith('.csv')) {
      alert('請上傳 CSV 檔案');
      return;
    }

    setUploadedFile(file);
    setIsLoading(true);

    try {
      const csvText = await file.text();

      // 將 CSV 數據發送給 Agent
      const uploadMessage = `請載入此 CSV 數據進行分析：\n\n檔案：${file.name}\n數據：\n${csvText}`;

      const userMessage: Message = { role: "user", content: `已上傳：${file.name}` };
      setMessages((prev) => [...prev, userMessage]);

      const response = await fetch("http://localhost:8000/api/copilotkit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          threadId: "data-analysis-thread",
          runId: `run-${Date.now()}`,
          messages: [...messages, { role: "user", content: uploadMessage }].map((m, i) => ({
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

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // 處理回應，類似 sendMessage
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";
      let chartDataFromTool: ChartData | null = null;

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const jsonData = JSON.parse(line.slice(6));
                console.log("📡 收到事件：", jsonData.type, jsonData);

                // 處理文字內容串流
                if (jsonData.type === "TEXT_MESSAGE_CONTENT") {
                  fullContent += jsonData.delta;
                  setMessages((prev) => {
                    const newMessages = [...prev];
                    const lastMsg = newMessages[newMessages.length - 1];
                    if (lastMsg && lastMsg.role === "assistant") {
                      lastMsg.content = fullContent;
                    } else {
                      newMessages.push({ role: "assistant", content: fullContent });
                    }
                    return newMessages;
                  });
                }

                // 處理工具結果（圖表數據）
                if (jsonData.type === "TOOL_CALL_RESULT") {
                  console.log("📊 上傳：收到 TOOL_CALL_RESULT：", jsonData);
                  try {
                    const resultContent = typeof jsonData.content === 'string'
                      ? JSON.parse(jsonData.content)
                      : jsonData.content;

                    if (resultContent && resultContent.chart_type) {
                      console.log("📈 上傳：發現圖表數據：", resultContent);
                      chartDataFromTool = resultContent;
                      setCurrentChart(resultContent);
                    }
                  } catch (e) {
                    console.error("解析上傳工具結果錯誤：", e);
                  }
                }
              } catch (e) {
                // 跳過無效 JSON
              }
            }
          }
        }
      }

      if (fullContent && messages[messages.length - 1]?.role !== "assistant") {
        const assistantMessage: Message = {
          role: "assistant",
          content: fullContent,
          chartData: chartDataFromTool || undefined,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      }

    } catch (error) {
      console.error("上傳錯誤：", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `上傳 ${file.name} 時發生錯誤：${error}` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    const csvFile = files.find(file => file.name.endsWith('.csv'));

    if (csvFile) {
      handleFileUpload(csvFile);
    } else {
      alert('請拖放 CSV 檔案');
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const renderChart = (chartData: ChartData) => {
    const data = {
      labels: chartData.data.labels,
      datasets: [
        {
          label: chartData.options.y_label,
          data: chartData.data.values,
          backgroundColor: chartData.chart_type === 'line'
            ? 'rgba(37, 99, 235, 0.1)'
            : 'rgba(37, 99, 235, 0.8)',
          borderColor: 'rgba(37, 99, 235, 1)',
          borderWidth: 2,
          tension: chartData.chart_type === 'line' ? 0.4 : 0,
          pointBackgroundColor: 'rgba(37, 99, 235, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(37, 99, 235, 1)',
        },
      ],
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top' as const,
          labels: {
            color: '#1f2937',
            font: {
              size: 12,
              weight: 'bold' as const,
            },
          },
        },
        title: {
          display: true,
          text: chartData.options.title,
          color: '#111827',
          font: {
            size: 16,
            weight: 'bold' as const,
          },
        },
      },
      scales: {
        x: {
          title: {
            display: true,
            text: chartData.options.x_label,
            color: '#4b5563',
            font: {
              size: 12,
              weight: 'bold' as const,
            },
          },
          ticks: {
            color: '#6b7280',
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)',
          },
        },
        y: {
          title: {
            display: true,
            text: chartData.options.y_label,
            color: '#4b5563',
            font: {
              size: 12,
              weight: 'bold' as const,
            },
          },
          ticks: {
            color: '#6b7280',
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)',
          },
        },
      },
    };

    switch (chartData.chart_type) {
      case 'line':
        return <Line data={data} options={options} />;
      case 'bar':
        return <Bar data={data} options={options} />;
      case 'scatter':
        return <Scatter data={data} options={options} />;
      default:
        return <Line data={data} options={options} />;
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-blue-50 overflow-hidden">
      {/* 標頭 */}
      <header className="bg-white/90 backdrop-blur-sm border-b border-gray-200 shadow-sm sticky top-0 z-10 flex-shrink-0" role="banner">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div
                className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center text-2xl shadow-lg"
                aria-hidden="true"
              >
                📊
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">數據分析儀表板</h1>
                <p className="text-sm text-gray-600">由 Gemini 2.0 Flash 驅動</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {uploadedFile && (
                <div className="text-sm text-gray-600 bg-green-50 px-3 py-1 rounded-full border border-green-200">
                  📄 {uploadedFile.name}
                </div>
              )}
              <div className="flex items-center gap-2" role="status" aria-live="polite">
                <div
                  className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"
                  aria-hidden="true"
                ></div>
                <span className="text-sm font-medium text-emerald-700">已連線</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 flex max-w-full mx-auto w-full relative">
        {/* 主要聊天區域 */}
        <main className={`flex-1 flex flex-col transition-all duration-300 ${(currentChart || uploadedFile) ? 'mr-96' : ''}`} style={{maxWidth: '100%'}} role="main">
          {/* 檔案上傳區域 */}
          <div className="p-6 border-b border-gray-200 bg-white/50">
            <div
              className={`relative border-2 border-dashed rounded-xl p-6 text-center transition-all duration-200 ${
                isDragOver
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-300 hover:border-blue-400 hover:bg-blue-50/50"
              }`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFileUpload(file);
                }}
                className="hidden"
              />
              <div className="text-4xl mb-2">📁</div>
              <p className="text-lg font-semibold text-gray-700 mb-1">
                拖放 CSV 檔案至此或{" "}
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="text-blue-600 hover:text-blue-700 underline"
                >
                  瀏覽
                </button>
              </p>
              <p className="text-sm text-gray-500">
                支援用於數據分析和視覺化的 CSV 檔案
              </p>
            </div>
          </div>

          {/* 聊天訊息 */}
          <div className="flex-1 overflow-y-auto" aria-label="聊天對話">
            <div className="px-6 py-4 max-w-5xl mx-auto">
              {messages.length === 1 && (
                <div
                  className="text-center py-12"
                  role="status"
                  aria-label="歡迎訊息"
                >
                  <div className="text-6xl mb-4" aria-hidden="true">📈</div>
                  <p className="text-xl font-semibold text-gray-700 mb-2">
                    準備好分析您的數據
                  </p>
                  <p className="text-gray-600 mb-4">
                    上傳 CSV 檔案或請我分析數據趨勢
                  </p>
                  <div className="flex flex-wrap gap-2 justify-center">
                    <button
                      onClick={() => setInput("分析銷售趨勢")}
                      className="px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition-colors"
                    >
                      "分析銷售趨勢"
                    </button>
                    <button
                      onClick={() => setInput("顯示相關性分析")}
                      className="px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-sm hover:bg-purple-200 transition-colors"
                    >
                      "顯示相關性分析"
                    </button>
                    <button
                      onClick={() => setInput("建立折線圖")}
                      className="px-4 py-2 bg-green-100 text-green-700 rounded-full text-sm hover:bg-green-200 transition-colors"
                    >
                      "建立折線圖"
                    </button>
                  </div>
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
                    className={`flex gap-4 mb-6 items-start animate-in slide-in-from-bottom-2 duration-300 ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                    role="article"
                    aria-label={`${message.role === "user" ? "您的訊息" : "助手訊息"}`}
                  >
                    {message.role === "assistant" && (
                      <div
                        className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center flex-shrink-0 text-lg shadow-lg"
                        aria-hidden="true"
                      >
                        🤖
                      </div>
                    )}

                    <div
                      className={`max-w-[75%] px-5 py-4 rounded-2xl leading-relaxed shadow-lg ${
                        message.role === "user"
                          ? "bg-gradient-to-r from-blue-700 to-blue-800 text-white rounded-br-md"
                          : "bg-white text-gray-900 border-2 border-gray-200 rounded-bl-md"
                      }`}
                      role="region"
                      aria-label={message.role === "user" ? "您的訊息內容" : "助手回應內容"}
                    >
                      <div className={`prose prose-sm max-w-none ${
                        message.role === "user"
                          ? "prose-invert"
                          : "prose-gray prose-headings:text-gray-900 prose-p:text-gray-800 prose-strong:text-gray-900 prose-code:text-blue-700 prose-pre:bg-gray-100"
                      }`}>
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          rehypePlugins={[rehypeHighlight, rehypeRaw]}
                        >
                          {message.content}
                        </ReactMarkdown>
                      </div>

                      {/* 為帶有圖表數據的訊息顯示內嵌圖表 */}
                      {message.chartData && (
                        <div className="mt-4 bg-gray-50 rounded-lg p-4 border-2 border-gray-200">
                          <div className="h-64">
                            {renderChart(message.chartData)}
                          </div>
                        </div>
                      )}
                    </div>

                    {message.role === "user" && (
                      <div
                        className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center flex-shrink-0 text-lg text-white shadow-lg"
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
                  className="flex gap-4 items-start animate-in slide-in-from-bottom-2 duration-300"
                  role="status"
                  aria-live="polite"
                  aria-label="助手正在輸入"
                >
                  <div
                    className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center flex-shrink-0 text-lg shadow-lg"
                    aria-hidden="true"
                  >
                    🤖
                  </div>
                  <div className="px-5 py-4 rounded-2xl rounded-bl-md bg-white shadow-lg border border-gray-100">
                    <div className="flex gap-1" aria-label="載入中">
                      <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: "0s" }}></div>
                      <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                      <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: "0.4s" }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} aria-hidden="true" />
            </div>
          </div>

          {/* 輸入表單 */}
          <footer className="bg-white/90 backdrop-blur-sm border-t border-gray-200 shadow-lg" role="contentinfo">
            <div className="px-6 py-4">
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
                    placeholder="詢問關於數據分析的問題..."
                    disabled={isLoading}
                    autoFocus
                    autoComplete="off"
                    aria-label="訊息輸入"
                    aria-describedby="message-hint"
                    aria-invalid="false"
                    className="w-full px-6 py-4 pr-12 border-2 border-gray-300 rounded-2xl text-base outline-none transition-all bg-white text-gray-900 placeholder-gray-500 focus:border-blue-600 focus:ring-4 focus:ring-blue-600/20 disabled:bg-gray-100 disabled:text-gray-500 disabled:cursor-not-allowed shadow-sm"
                  />
                  {input.length > 0 && (
                    <div
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-sm text-gray-500 pointer-events-none"
                      aria-live="polite"
                      aria-atomic="true"
                    >
                      <span className="sr-only">字數： </span>
                      {input.length}
                    </div>
                  )}
                </div>
                <button
                  type="submit"
                  disabled={isLoading || !input.trim()}
                  aria-label={isLoading ? "正在發送訊息，請稍候" : "發送訊息"}
                  aria-busy={isLoading}
                  className="px-8 py-4 bg-gradient-to-r from-blue-700 to-blue-800 text-white rounded-2xl font-bold transition-all flex items-center gap-2 shadow-lg hover:from-blue-800 hover:to-blue-900 hover:-translate-y-0.5 hover:shadow-xl focus:outline-none focus:ring-4 focus:ring-blue-600/30 disabled:bg-gray-400 disabled:text-white disabled:cursor-not-allowed disabled:shadow-none disabled:translate-y-0 disabled:opacity-60"
                >
                  {isLoading ? (
                    <>
                      <span>發送中</span>
                      <span className="animate-spin" aria-hidden="true">⏳</span>
                    </>
                  ) : (
                    <>
                      <span>發送</span>
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
                Powered by Google ADK • Tutorial 31 Data Analysis Dashboard
              </p>
            </div>
          </footer>
        </main>

        {/* 側邊欄（圖表和數據）- 固定位置 */}
        {(currentChart || uploadedFile) && (
          <aside
            className="fixed right-0 top-0 w-96 h-screen bg-white border-l-2 border-gray-300 flex flex-col shadow-2xl z-20 animate-in slide-in-from-right duration-300"
            role="complementary"
            aria-label="視覺化面板"
          >
            {/* 固定標頭 */}
            <div className="flex-shrink-0 p-6 border-b-2 border-gray-300 bg-gradient-to-r from-gray-50 to-blue-50">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  📊 視覺化
                </h2>
                <button
                  onClick={() => setCurrentChart(null)}
                  className="text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded-lg p-2 transition-colors"
                  aria-label="關閉視覺化面板"
                  title="關閉面板"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* 可滾動內容 */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6" style={{maxHeight: 'calc(100vh - 88px)'}}>
              {currentChart && (
                <div className="space-y-4">
                  {/* 圖表容器 */}
                  <div className="bg-gradient-to-br from-white to-gray-50 rounded-xl p-6 border-2 border-gray-300 shadow-lg">
                    <div className="h-80">
                      {renderChart(currentChart)}
                    </div>
                  </div>

                  {/* 圖表元數據 */}
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-5 border-2 border-blue-200 shadow-sm space-y-3">
                    <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wide mb-3 flex items-center gap-2">
                      <span className="text-blue-600">📋</span> 圖表詳情
                    </h3>
                    <div className="space-y-2.5">
                      <div className="flex items-start justify-between gap-2">
                        <span className="text-sm font-medium text-gray-600">類型：</span>
                        <span className="text-sm font-bold text-gray-900 capitalize">{currentChart.chart_type}</span>
                      </div>
                      <div className="flex items-start justify-between gap-2">
                        <span className="text-sm font-medium text-gray-600">X 軸：</span>
                        <span className="text-sm font-semibold text-gray-800 text-right">{currentChart.options.x_label}</span>
                      </div>
                      <div className="flex items-start justify-between gap-2">
                        <span className="text-sm font-medium text-gray-600">Y 軸：</span>
                        <span className="text-sm font-semibold text-gray-800 text-right">{currentChart.options.y_label}</span>
                      </div>
                      <div className="flex items-start justify-between gap-2 pt-2 border-t border-blue-200">
                        <span className="text-sm font-medium text-gray-600">數據點：</span>
                        <span className="text-sm font-bold text-blue-700">{currentChart.data.labels.length}</span>
                      </div>
                    </div>
                  </div>

                  {/* 圖表狀態 */}
                  {currentChart.report && (
                    <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                      <p className="text-sm text-green-800 leading-relaxed">
                        <span className="font-semibold">✓</span> {currentChart.report}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {uploadedFile && (
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-5 border-2 border-blue-300 shadow-sm">
                  <h3 className="font-bold text-blue-900 mb-3 flex items-center gap-2 text-sm uppercase tracking-wide">
                    <span>📄</span> 已上傳檔案
                  </h3>
                  <div className="space-y-2">
                    <p className="text-sm text-blue-900 font-semibold break-all">{uploadedFile.name}</p>
                    <div className="flex items-center gap-3 text-xs text-blue-700">
                      <span className="font-medium bg-blue-200 px-2 py-1 rounded">
                        {(uploadedFile.size / 1024).toFixed(1)} KB
                      </span>
                      <span className="font-medium bg-blue-200 px-2 py-1 rounded">
                        CSV 格式
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}

export default App;

// #### 重點摘要 (程式碼除外)
// - **核心概念**：React 主應用程式元件，整合了聊天介面、檔案上傳與即時圖表視覺化。
// - **關鍵技術**：React (Hooks), Chart.js, Tailwind CSS, AG-UI Protocol (Server-Sent Events), Markdown 渲染。
// - **重要結論**：
//   - 透過 `fetch` 與 SSE 處理即時聊天串流。
//   - 解析 `TOOL_CALL_RESULT` 事件以提取圖表數據並更新 UI。
//   - 實作了拖放檔案上傳功能，並將 CSV 內容傳送給後端。
//   - 使用固定側邊欄顯示圖表和檔案資訊，提供更好的使用者體驗。
// - **行動項目**：確認後端 API URL 正確指向 `http://localhost:8000/api/copilotkit`。
