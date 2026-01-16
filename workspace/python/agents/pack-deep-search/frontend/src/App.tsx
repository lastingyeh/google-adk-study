import { useState, useRef, useCallback, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { WelcomeScreen } from '@/components/WelcomeScreen';
import { ChatMessagesView } from '@/components/ChatMessagesView';

// 顯示資料類型定義
// 更新 DisplayData 為字串類型
type DisplayData = string | null;

/**
 * 帶有 Agent 資訊的訊息界面
 * @property type - 訊息類型：'human' 表示用戶訊息，'ai' 表示 AI 回應
 * @property content - 訊息內容
 * @property id - 唯一識別碼
 * @property agent - 當前處理訊息的 Agent 名稱
 * @property finalReportWithCitations - 是否為帶有引用的最終報告
 */
interface MessageWithAgent {
  type: 'human' | 'ai';
  content: string;
  id: string;
  agent?: string;
  finalReportWithCitations?: boolean;
}

/**
 * 已處理的事件類型
 * 用於活動時間軸中顯示研究流程的各個階段
 */
interface ProcessedEvent {
  title: string; // 事件標題
  data: unknown; // 事件資料
}

/**
 * 主應用程式組件
 * 管理整個應用的狀態，包括用戶對話、後端連接、SSE 事件處理等
 */
export default function App() {
  // 使用者與工作階段狀態
  const [userId, setUserId] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [appName, setAppName] = useState<string | null>(null);

  // 訊息與顯示狀態
  const [messages, setMessages] = useState<MessageWithAgent[]>([]);
  const [displayData, setDisplayData] = useState<DisplayData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // 事件追蹤狀態
  const [messageEvents, setMessageEvents] = useState<
    Map<string, ProcessedEvent[]>
  >(new Map());
  const [websiteCount, setWebsiteCount] = useState<number>(0);

  // 後端連接狀態
  const [isBackendReady, setIsBackendReady] = useState(false);
  const [isCheckingBackend, setIsCheckingBackend] = useState(true);

  // Ref 用於追蹤當前 Agent 和累積文字
  const currentAgentRef = useRef('');
  const accumulatedTextRef = useRef('');
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  /**
   * 指數退縮重試機制
   * 用於處理網路請求失敗，自動重試並逗步增加重試間隔
   * @param fn - 要執行的異步函數
   * @param maxRetries - 最大重試次數（預設 10 次）
   * @param maxDuration - 最大重試時間（預設 2 分鐘）
   */
  const retryWithBackoff = async <T,>(
    fn: () => Promise<T>,
    maxRetries: number = 10,
    maxDuration: number = 120000 // 2 分鐘
  ): Promise<T> => {
    const startTime = Date.now();
    let lastError: Error;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      if (Date.now() - startTime > maxDuration) {
        throw new Error(`Retry timeout after ${maxDuration}ms`);
      }

      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;
        const delay = Math.min(1000 * Math.pow(2, attempt), 5000); // 指數退縮，最大 5 秒
        console.log(
          `第 ${attempt + 1} 次嘗試失敗，${delay}ms 後重試...`,
          error
        );
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }

    throw lastError!;
  };

  /**
   * 建立新的工作階段
   * 使用 UUID 生成唯一的工作階段 ID，並向後端 API 發送建立請求
   */
  const createSession = async (): Promise<{
    userId: string;
    sessionId: string;
    appName: string;
  }> => {
    const generatedSessionId = uuidv4();
    const response = await fetch(
      `/api/apps/app/users/u_999/sessions/${generatedSessionId}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(
        `建立工作階段失敗: ${response.status} ${response.statusText}`
      );
    }

    const data = await response.json();
    return {
      userId: data.userId,
      sessionId: data.id,
      appName: data.appName,
    };
  };

  /**
   * 檢查後端服務健康狀態
   * 透過請求 /api/docs 端點來驗證後端是否就緒
   */
  const checkBackendHealth = async (): Promise<boolean> => {
    try {
      // 使用 docs 端點或根端點檢查後端是否就緒
      const response = await fetch('/api/docs', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      return response.ok;
    } catch (error) {
      console.log('後端尚未就緒:', error);
      return false;
    }
  };

  /**
   * 從 SSE (Server-Sent Events) 資料中提取文字和元資料
   * 解析從後端來的事件串流，提取文字內容、Agent 資訊、函數呼叫等
   */
  // Function to extract text and metadata from SSE data
  const extractDataFromSSE = (data: string) => {
    try {
      const parsed = JSON.parse(data);
      console.log('[SSE PARSED EVENT]:', JSON.stringify(parsed, null, 2)); // DEBUG: Log parsed event

      let textParts: string[] = [];
      let agent = '';
      let finalReportWithCitations = undefined;
      let functionCall = null;
      let functionResponse = null;
      let sources = null;

      // Check if content.parts exists and has text
      if (parsed.content && parsed.content.parts) {
        textParts = parsed.content.parts
          .filter(
            (part: {
              text?: string;
              functionCall?: unknown;
              functionResponse?: unknown;
            }) => part.text
          )
          .map((part: { text: string }) => part.text);

        // Check for function calls
        const functionCallPart = parsed.content.parts.find(
          (part: { functionCall?: unknown }) => part.functionCall
        );
        if (functionCallPart) {
          functionCall = functionCallPart.functionCall;
        }

        // Check for function responses
        const functionResponsePart = parsed.content.parts.find(
          (part: { functionResponse?: unknown }) => part.functionResponse
        );
        if (functionResponsePart) {
          functionResponse = functionResponsePart.functionResponse;
        }
      }

      // Extract agent information
      if (parsed.author) {
        agent = parsed.author;
        console.log('[SSE EXTRACT] Agent:', agent); // DEBUG: Log agent
      }

      if (
        parsed.actions &&
        parsed.actions.stateDelta &&
        parsed.actions.stateDelta.final_report_with_citations
      ) {
        finalReportWithCitations =
          parsed.actions.stateDelta.final_report_with_citations;
      }

      // Extract website count from research agents
      let sourceCount = 0;
      if (
        parsed.author === 'section_researcher' ||
        parsed.author === 'enhanced_search_executor'
      ) {
        console.log(
          '[SSE EXTRACT] Relevant agent for source count:',
          parsed.author
        ); // DEBUG
        if (parsed.actions?.stateDelta?.url_to_short_id) {
          console.log(
            '[SSE EXTRACT] url_to_short_id found:',
            parsed.actions.stateDelta.url_to_short_id
          ); // DEBUG
          sourceCount = Object.keys(
            parsed.actions.stateDelta.url_to_short_id
          ).length;
          console.log('[SSE EXTRACT] Calculated sourceCount:', sourceCount); // DEBUG
        } else {
          console.log(
            '[SSE EXTRACT] url_to_short_id NOT found for agent:',
            parsed.author
          ); // DEBUG
        }
      }

      // Extract sources if available
      if (parsed.actions?.stateDelta?.sources) {
        sources = parsed.actions.stateDelta.sources;
        console.log('[SSE EXTRACT] Sources found:', sources); // DEBUG
      }

      return {
        textParts,
        agent,
        finalReportWithCitations,
        functionCall,
        functionResponse,
        sourceCount,
        sources,
      };
    } catch (error) {
      // Log the error and a truncated version of the problematic data for easier debugging.
      const truncatedData =
        data.length > 200 ? data.substring(0, 200) + '...' : data;
      console.error(
        'Error parsing SSE data. Raw data (truncated): "',
        truncatedData,
        '". Error details:',
        error
      );
      return {
        textParts: [],
        agent: '',
        finalReportWithCitations: undefined,
        functionCall: null,
        functionResponse: null,
        sourceCount: 0,
        sources: null,
      };
    }
  };

  /**
   * 根據 Agent 名稱取得相對應的顯示標題
   * 各個 Agent 代表不同的研究階段
   */
  // Define getEventTitle here or ensure it's in scope from where it's used
  const getEventTitle = (agentName: string): string => {
    switch (agentName) {
      case 'plan_generator':
        return '規劃研究策略';
      case 'section_planner':
        return '結構化報告大綱';
      case 'section_researcher':
        return '初步網路研究';
      case 'research_evaluator':
        return '評估研究品質';
      case 'EscalationChecker':
        return '品質評估';
      case 'enhanced_search_executor':
        return '增強網路研究';
      case 'research_pipeline':
        return '執行研究流程';
      case 'iterative_refinement_loop':
        return '優化研究結果';
      case 'interactive_planner_agent':
      case 'root_agent':
        return '互動式規劃';
      default:
        return `處理中 (${agentName || '未知 Agent'})`;
    }
  };

  /**
   * 處理 SSE 事件資料
   * 解析並處理從後端來的事件，更新訊息、時間軸事件和網站計數
   * @param jsonData - JSON 格式的事件資料
   * @param aiMessageId - AI 訊息的唯一 ID
   */
  const processSseEventData = (jsonData: string, aiMessageId: string) => {
    const {
      textParts,
      agent,
      finalReportWithCitations,
      functionCall,
      functionResponse,
      sourceCount,
      sources,
    } = extractDataFromSSE(jsonData);

    if (sourceCount > 0) {
      console.log(
        '[SSE HANDLER] Updating websiteCount. Current sourceCount:',
        sourceCount
      );
      setWebsiteCount((prev) => Math.max(prev, sourceCount));
    }

    if (agent && agent !== currentAgentRef.current) {
      currentAgentRef.current = agent;
    }

    if (functionCall) {
      const functionCallTitle = `Function Call: ${functionCall.name}`;
      console.log(
        '[SSE HANDLER] Adding Function Call timeline event:',
        functionCallTitle
      );
      setMessageEvents((prev) =>
        new Map(prev).set(aiMessageId, [
          ...(prev.get(aiMessageId) || []),
          {
            title: functionCallTitle,
            data: {
              type: 'functionCall',
              name: functionCall.name,
              args: functionCall.args,
              id: functionCall.id,
            },
          },
        ])
      );
    }

    if (functionResponse) {
      const functionResponseTitle = `Function Response: ${functionResponse.name}`;
      console.log(
        '[SSE HANDLER] Adding Function Response timeline event:',
        functionResponseTitle
      );
      setMessageEvents((prev) =>
        new Map(prev).set(aiMessageId, [
          ...(prev.get(aiMessageId) || []),
          {
            title: functionResponseTitle,
            data: {
              type: 'functionResponse',
              name: functionResponse.name,
              response: functionResponse.response,
              id: functionResponse.id,
            },
          },
        ])
      );
    }

    if (textParts.length > 0 && agent !== 'report_composer_with_citations') {
      if (agent !== 'interactive_planner_agent') {
        const eventTitle = getEventTitle(agent);
        console.log(
          '[SSE HANDLER] Adding Text timeline event for agent:',
          agent,
          'Title:',
          eventTitle,
          'Data:',
          textParts.join(' ')
        );
        setMessageEvents((prev) =>
          new Map(prev).set(aiMessageId, [
            ...(prev.get(aiMessageId) || []),
            {
              title: eventTitle,
              data: { type: 'text', content: textParts.join(' ') },
            },
          ])
        );
      } else {
        // interactive_planner_agent text updates the main AI message
        for (const text of textParts) {
          accumulatedTextRef.current += text + ' ';
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === aiMessageId
                ? {
                    ...msg,
                    content: accumulatedTextRef.current.trim(),
                    agent: currentAgentRef.current || msg.agent,
                  }
                : msg
            )
          );
          setDisplayData(accumulatedTextRef.current.trim());
        }
      }
    }

    if (sources) {
      console.log(
        '[SSE HANDLER] Adding Retrieved Sources timeline event:',
        sources
      );
      setMessageEvents((prev) =>
        new Map(prev).set(aiMessageId, [
          ...(prev.get(aiMessageId) || []),
          {
            title: 'Retrieved Sources',
            data: { type: 'sources', content: sources },
          },
        ])
      );
    }

    if (
      agent === 'report_composer_with_citations' &&
      finalReportWithCitations
    ) {
      const finalReportMessageId = Date.now().toString() + '_final';
      setMessages((prev) => [
        ...prev,
        {
          type: 'ai',
          content: finalReportWithCitations as string,
          id: finalReportMessageId,
          agent: currentAgentRef.current,
          finalReportWithCitations: true,
        },
      ]);
      setDisplayData(finalReportWithCitations as string);
    }
  };

  /**
   * 處理用戶提交的查詢
   * 建立工作階段（如需）、傳送訊息到後端、並處理 SSE 回應
   */
  const handleSubmit = useCallback(
    async (query: string) => {
      if (!query.trim()) return;

      setIsLoading(true);
      try {
        // 如果不存在則建立工作階段
        let currentUserId = userId;
        let currentSessionId = sessionId;
        let currentAppName = appName;

        if (!currentSessionId || !currentUserId || !currentAppName) {
          console.log('建立新工作階段...');
          const sessionData = await retryWithBackoff(createSession);
          currentUserId = sessionData.userId;
          currentSessionId = sessionData.sessionId;
          currentAppName = sessionData.appName;

          setUserId(currentUserId);
          setSessionId(currentSessionId);
          setAppName(currentAppName);
          console.log('工作階段建立成功:', {
            currentUserId,
            currentSessionId,
            currentAppName,
          });
        }

        // 將用戶訊息加入聊天
        const userMessageId = Date.now().toString();
        setMessages((prev) => [
          ...prev,
          { type: 'human', content: query, id: userMessageId },
        ]);

        // 建立 AI 訊息占位符
        const aiMessageId = Date.now().toString() + '_ai';
        currentAgentRef.current = ''; // 重置當前 Agent
        accumulatedTextRef.current = ''; // 重置累積文字

        setMessages((prev) => [
          ...prev,
          {
            type: 'ai',
            content: '',
            id: aiMessageId,
            agent: '',
          },
        ]);

        // 使用重試逻輯傳送訊息
        const sendMessage = async () => {
          const response = await fetch('/api/run_sse', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              appName: currentAppName,
              userId: currentUserId,
              sessionId: currentSessionId,
              newMessage: {
                parts: [{ text: query }],
                role: 'user',
              },
              streaming: false,
            }),
          });

          if (!response.ok) {
            throw new Error(
              `傳送訊息失敗: ${response.status} ${response.statusText}`
            );
          }

          return response;
        };

        const response = await retryWithBackoff(sendMessage);

        // 處理 SSE 串流
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let lineBuffer = '';
        let eventDataBuffer = '';

        if (reader) {
          while (true) {
            const { done, value } = await reader.read();

            if (value) {
              lineBuffer += decoder.decode(value, { stream: true });
            }

            let eolIndex;
            // 處理緩衝區中所有完整的行，或如果 'done' 則處理剩餘緩衝區
            while (
              (eolIndex = lineBuffer.indexOf('\n')) >= 0 ||
              (done && lineBuffer.length > 0)
            ) {
              let line: string;
              if (eolIndex >= 0) {
                line = lineBuffer.substring(0, eolIndex);
                lineBuffer = lineBuffer.substring(eolIndex + 1);
              } else {
                // Only if done and lineBuffer has content without a trailing newline
                line = lineBuffer;
                lineBuffer = '';
              }

              if (line.trim() === '') {
                // 空行：分派事件
                if (eventDataBuffer.length > 0) {
                  // 在解析前移除尾部換行符
                  const jsonDataToParse = eventDataBuffer.endsWith('\n')
                    ? eventDataBuffer.slice(0, -1)
                    : eventDataBuffer;
                  console.log(
                    '[SSE DISPATCH EVENT]:',
                    jsonDataToParse.substring(0, 200) + '...'
                  ); // DEBUG
                  processSseEventData(jsonDataToParse, aiMessageId);
                  eventDataBuffer = ''; // 重置以便下一個事件
                }
              } else if (line.startsWith('data:')) {
                eventDataBuffer += line.substring(5).trimStart() + '\n'; // 根據規範為多行資料加入換行符
              } else if (line.startsWith(':')) {
                // 註釋行，忽略
              } // 其他 SSE 欄位（event、id、retry）如需可在此處理
            }

            if (done) {
              // If the loop exited due to 'done', and there's still data in eventDataBuffer
              // (e.g., stream ended after data lines but before an empty line delimiter)
              if (eventDataBuffer.length > 0) {
                const jsonDataToParse = eventDataBuffer.endsWith('\n')
                  ? eventDataBuffer.slice(0, -1)
                  : eventDataBuffer;
                console.log(
                  '[SSE DISPATCH FINAL EVENT]:',
                  jsonDataToParse.substring(0, 200) + '...'
                ); // DEBUG
                processSseEventData(jsonDataToParse, aiMessageId);
                eventDataBuffer = ''; // Clear buffer
              }
              break; // Exit the while(true) loop
            }
          }
        }

        setIsLoading(false);
      } catch (error) {
        console.error('錯誤:', error);
        // 使用錯誤訊息更新 AI 訊息占位符
        const aiMessageId = Date.now().toString() + '_ai_error';
        setMessages((prev) => [
          ...prev,
          {
            type: 'ai',
            content: `抱歉，處理您的請求時發生錯誤: ${
              error instanceof Error ? error.message : '未知錯誤'
            }`,
            id: aiMessageId,
          },
        ]);
        setIsLoading(false);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [userId, sessionId, appName]
  );

  // 當訊息更新時，自動滾動到底部
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector(
        '[data-radix-scroll-area-viewport]'
      );
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  }, [messages]);

  // 應用程式載入時檢查後端就緒狀態
  useEffect(() => {
    const checkBackend = async () => {
      setIsCheckingBackend(true);

      // 使用重試逻輯檢查後端是否就緒
      const maxAttempts = 60; // 2 分鐘，每次間隔 2 秒
      let attempts = 0;

      while (attempts < maxAttempts) {
        const isReady = await checkBackendHealth();
        if (isReady) {
          setIsBackendReady(true);
          setIsCheckingBackend(false);
          return;
        }

        attempts++;
        await new Promise((resolve) => setTimeout(resolve, 2000)); // 每次檢查間隔 2 秒
      }

      // 如果執行到這裡，表示後端在時限內未能啟動
      setIsCheckingBackend(false);
      console.error('後端在 2 分鐘內未能啟動');
    };

    checkBackend();
  }, []);

  /**
   * 處理取消操作
   * 清空訊息和狀態，並重新載入頁面
   */
  const handleCancel = useCallback(() => {
    setMessages([]);
    setDisplayData(null);
    setMessageEvents(new Map());
    setWebsiteCount(0);
    window.location.reload();
  }, []);

  /**
   * 後端載入畫面組件
   * 當後端尚未就緒時顯示的載入畫面
   */
  const BackendLoadingScreen = () => (
    <div className='flex-1 flex flex-col items-center justify-center p-4 overflow-hidden relative'>
      <div
        className='w-full max-w-2xl z-10
                      bg-neutral-900/50 backdrop-blur-md
                      p-8 rounded-2xl border border-neutral-700
                      shadow-2xl shadow-black/60'
      >
        <div className='text-center space-y-6'>
          <h1 className='text-4xl font-bold text-white flex items-center justify-center gap-3'>
            ✨ 深度搜尋 - ADK 🚀
          </h1>

          <div className='flex flex-col items-center space-y-4'>
            {/* 旋轉動畫 */}
            <div className='relative'>
              <div className='w-16 h-16 border-4 border-neutral-600 border-t-blue-500 rounded-full animate-spin'></div>
              <div
                className='absolute inset-0 w-16 h-16 border-4 border-transparent border-r-purple-500 rounded-full animate-spin'
                style={{
                  animationDirection: 'reverse',
                  animationDuration: '1.5s',
                }}
              ></div>
            </div>

            <div className='space-y-2'>
              <p className='text-xl text-neutral-300'>等待後端就緒中...</p>
              <p className='text-sm text-neutral-400'>
                首次啟動可能需要一些時間
              </p>
            </div>

            {/* 動畫點點 */}
            <div className='flex space-x-1'>
              <div
                className='w-2 h-2 bg-blue-500 rounded-full animate-bounce'
                style={{ animationDelay: '0ms' }}
              ></div>
              <div
                className='w-2 h-2 bg-purple-500 rounded-full animate-bounce'
                style={{ animationDelay: '150ms' }}
              ></div>
              <div
                className='w-2 h-2 bg-pink-500 rounded-full animate-bounce'
                style={{ animationDelay: '300ms' }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className='flex h-screen bg-neutral-800 text-neutral-100 font-sans antialiased'>
      <main className='flex-1 flex flex-col overflow-hidden w-full'>
        <div
          className={`flex-1 overflow-y-auto ${
            messages.length === 0 || isCheckingBackend ? 'flex' : ''
          }`}
        >
          {isCheckingBackend ? (
            <BackendLoadingScreen />
          ) : !isBackendReady ? (
            <div className='flex-1 flex flex-col items-center justify-center p-4'>
              <div className='text-center space-y-4'>
                <h2 className='text-2xl font-bold text-red-400'>後端不可用</h2>
                <p className='text-neutral-300'>
                  無法連接到 localhost:8000 的後端服務
                </p>
                <button
                  onClick={() => window.location.reload()}
                  className='px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors'
                >
                  重試
                </button>
              </div>
            </div>
          ) : messages.length === 0 ? (
            <WelcomeScreen
              handleSubmit={handleSubmit}
              isLoading={isLoading}
              onCancel={handleCancel}
            />
          ) : (
            <ChatMessagesView
              messages={messages}
              isLoading={isLoading}
              scrollAreaRef={scrollAreaRef}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              displayData={displayData}
              messageEvents={messageEvents}
              websiteCount={websiteCount}
            />
          )}
        </div>
      </main>
    </div>
  );
}
