import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
} from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Loader2,
  Activity,
  Info,
  Search,
  TextSearch,
  Brain,
  Pen,
  ChevronDown,
  ChevronUp,
  Link,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';

/**
 * 已處理事件類型
 * 記錄研究流程中的每個步驟
 */
export interface ProcessedEvent {
  title: string; // 事件標題
  data: unknown; // 事件資料
}

/**
 * 活動時間軸組件的屬性定義
 * @property processedEvents - 已處理的事件陣列
 * @property isLoading - 是否正在載入
 * @property websiteCount - 搜尋的網站數量
 */
interface ActivityTimelineProps {
  processedEvents: ProcessedEvent[];
  isLoading: boolean;
  websiteCount: number;
}

/**
 * 活動時間軸組件
 * 顯示 AI 研究流程的時間軸，包括搜尋、分析和生成報告的各個階段
 */
export function ActivityTimeline({
  processedEvents,
  isLoading,
  websiteCount,
}: ActivityTimelineProps) {
  const [isTimelineCollapsed, setIsTimelineCollapsed] =
    useState<boolean>(false);

  /**
   * 格式化事件資料以便顯示
   * 處理不同類型的資料（函數呼叫、回應、文字、來源等）
   */
  const formatEventData = (data: unknown): string => {
    // 處理新的結構化資料類型
    // Handle new structured data types
    if (typeof data === 'object' && data !== null && 'type' in data) {
      const typedData = data as {
        type: string;
        name?: string;
        args?: unknown;
        response?: unknown;
        content?: unknown;
      };
      switch (typedData.type) {
        case 'functionCall':
          return `呼叫函數: ${typedData.name}\n參數: ${JSON.stringify(
            typedData.args,
            null,
            2
          )}`;
        case 'functionResponse':
          return `函數 ${typedData.name} 回應:\n${JSON.stringify(
            typedData.response,
            null,
            2
          )}`;
        case 'text':
          return String(typedData.content);
        case 'sources': {
          const sources = typedData.content as Record<
            string,
            { title: string; url: string }
          >;
          if (Object.keys(sources).length === 0) {
            return '未找到來源。';
          }
          return Object.values(sources)
            .map((source) => `[${source.title || '無標題來源'}](${source.url})`)
            .join(', ');
        }
        default:
          return JSON.stringify(data, null, 2);
      }
    }

    // Existing logic for backward compatibility
    if (typeof data === 'string') {
      // Try to parse as JSON first
      try {
        const parsed = JSON.parse(data);
        return JSON.stringify(parsed, null, 2);
      } catch {
        // If not JSON, return as string (could be markdown)
        return data;
      }
    } else if (Array.isArray(data)) {
      return data.join(', ');
    } else if (typeof data === 'object' && data !== null) {
      return JSON.stringify(data, null, 2);
    }
    return String(data);
  };

  /**
   * 判斷資料是否為 JSON 格式
   * 用於決定如何渲染事件資料
   */
  const isJsonData = (data: unknown): boolean => {
    // 處理新的結構化資料類型
    // Handle new structured data types
    if (typeof data === 'object' && data !== null && 'type' in data) {
      const typedData = data as { type: string };
      if (typedData.type === 'sources') {
        return false; // 讓 ReactMarkdown 處理這個
      }
      return (
        typedData.type === 'functionCall' ||
        typedData.type === 'functionResponse'
      );
    }

    // 既有逻輯
    // Existing logic
    if (typeof data === 'string') {
      try {
        JSON.parse(data);
        return true;
      } catch {
        return false;
      }
    }
    return typeof data === 'object' && data !== null;
  };

  /**
   * 根據事件標題取得相對應的圖示
   * 不同類型的事件顯示不同的圖示和顏色
   */
  const getEventIcon = (title: string, index: number) => {
    if (index === 0 && isLoading && processedEvents.length === 0) {
      return <Loader2 className='h-4 w-4 text-neutral-400 animate-spin' />;
    }
    if (title.toLowerCase().includes('function call')) {
      return <Activity className='h-4 w-4 text-blue-400' />;
    } else if (title.toLowerCase().includes('function response')) {
      return <Activity className='h-4 w-4 text-green-400' />;
    } else if (
      title.toLowerCase().includes('generating') ||
      title.toLowerCase().includes('生成')
    ) {
      return <TextSearch className='h-4 w-4 text-neutral-400' />;
    } else if (
      title.toLowerCase().includes('thinking') ||
      title.toLowerCase().includes('思考')
    ) {
      return <Loader2 className='h-4 w-4 text-neutral-400 animate-spin' />;
    } else if (
      title.toLowerCase().includes('reflection') ||
      title.toLowerCase().includes('反思')
    ) {
      return <Brain className='h-4 w-4 text-neutral-400' />;
    } else if (
      title.toLowerCase().includes('research') ||
      title.toLowerCase().includes('研究')
    ) {
      return <Search className='h-4 w-4 text-neutral-400' />;
    } else if (
      title.toLowerCase().includes('finalizing') ||
      title.toLowerCase().includes('完成')
    ) {
      return <Pen className='h-4 w-4 text-neutral-400' />;
    } else if (
      title.toLowerCase().includes('retrieved sources') ||
      title.toLowerCase().includes('檢索來源')
    ) {
      return <Link className='h-4 w-4 text-yellow-400' />;
    }
    return <Activity className='h-4 w-4 text-neutral-400' />;
  };

  // 當加載完成且有事件時，自動收縮時間軸
  useEffect(() => {
    if (!isLoading && processedEvents.length !== 0) {
      setIsTimelineCollapsed(true);
    }
  }, [isLoading, processedEvents]);
  return (
    <Card
      className={`border-none rounded-lg bg-neutral-700 ${
        isTimelineCollapsed ? 'h-10 py-2' : 'max-h-96 py-2'
      }`}
    >
      <CardHeader className='py-0'>
        <CardDescription className='flex items-center justify-between'>
          <div
            className='flex items-center justify-start text-sm w-full cursor-pointer gap-2 text-neutral-100'
            onClick={() => setIsTimelineCollapsed(!isTimelineCollapsed)}
          >
            <span>研究</span>
            {websiteCount > 0 && (
              <span className='text-xs bg-neutral-600 px-2 py-0.5 rounded-full'>
                {websiteCount} 個網站
              </span>
            )}
            {isTimelineCollapsed ? (
              <ChevronDown className='h-4 w-4 mr-2' />
            ) : (
              <ChevronUp className='h-4 w-4 mr-2' />
            )}
          </div>
        </CardDescription>
      </CardHeader>
      {!isTimelineCollapsed && (
        <ScrollArea className='max-h-80 overflow-y-auto'>
          <CardContent>
            {isLoading && processedEvents.length === 0 && (
              <div className='relative pl-8 pb-4'>
                <div className='absolute left-3 top-3.5 h-full w-0.5 bg-neutral-800' />
                <div className='absolute left-0.5 top-2 h-5 w-5 rounded-full bg-neutral-800 flex items-center justify-center ring-4 ring-neutral-900'>
                  <Loader2 className='h-3 w-3 text-neutral-400 animate-spin' />
                </div>
                <div>
                  <p className='text-sm text-neutral-300 font-medium'>
                    思考中...
                  </p>
                </div>
              </div>
            )}
            {processedEvents.length > 0 ? (
              <div className='space-y-0'>
                {processedEvents.map((eventItem, index) => (
                  <div key={index} className='relative pl-8 pb-4'>
                    {index < processedEvents.length - 1 ||
                    (isLoading && index === processedEvents.length - 1) ? (
                      <div className='absolute left-3 top-3.5 h-full w-0.5 bg-neutral-600' />
                    ) : null}
                    <div className='absolute left-0.5 top-2 h-6 w-6 rounded-full bg-neutral-600 flex items-center justify-center ring-4 ring-neutral-700'>
                      {getEventIcon(eventItem.title, index)}
                    </div>
                    <div>
                      <p className='text-sm text-neutral-200 font-medium mb-0.5'>
                        {eventItem.title}
                      </p>
                      <div className='text-xs text-neutral-300 leading-relaxed'>
                        {isJsonData(eventItem.data) ? (
                          <pre className='bg-neutral-800 p-2 rounded text-xs overflow-x-auto whitespace-pre-wrap'>
                            {formatEventData(eventItem.data)}
                          </pre>
                        ) : (
                          <ReactMarkdown
                            components={{
                              p: ({ children }) => <span>{children}</span>,
                              a: ({ href, children }) => (
                                <a
                                  href={href}
                                  target='_blank'
                                  rel='noopener noreferrer'
                                  className='text-blue-400 hover:text-blue-300 underline'
                                >
                                  {children}
                                </a>
                              ),
                              code: ({ children }) => (
                                <code className='bg-neutral-800 px-1 py-0.5 rounded text-xs'>
                                  {children}
                                </code>
                              ),
                            }}
                          >
                            {formatEventData(eventItem.data)}
                          </ReactMarkdown>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && processedEvents.length > 0 && (
                  <div className='relative pl-8 pb-4'>
                    <div className='absolute left-0.5 top-2 h-5 w-5 rounded-full bg-neutral-600 flex items-center justify-center ring-4 ring-neutral-700'>
                      <Loader2 className='h-3 w-3 text-neutral-400 animate-spin' />
                    </div>
                    <div>
                      <p className='text-sm text-neutral-300 font-medium'>
                        思考中...
                      </p>
                    </div>
                  </div>
                )}
              </div>
            ) : !isLoading ? ( // 只有在未加載且無事件時才顯示「無活動」
              // Only show "No activity" if not loading and no events
              <div className='flex flex-col items-center justify-center h-full text-neutral-500 pt-10'>
                <Info className='h-6 w-6 mb-3' />
                <p className='text-sm'>無活動可顯示。</p>
                <p className='text-xs text-neutral-600 mt-1'>
                  時間軸將在處理過程中更新。
                </p>
              </div>
            ) : null}
          </CardContent>
        </ScrollArea>
      )}
    </Card>
  );
}
