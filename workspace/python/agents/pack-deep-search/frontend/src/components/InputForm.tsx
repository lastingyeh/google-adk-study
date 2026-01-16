import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, Send } from 'lucide-react';

/**
 * 輸入表單組件的屬性定義
 * @property onSubmit - 提交查詢時的回調函數
 * @property isLoading - 載入狀態標記
 * @property context - 使用場景，'homepage' 或 'chat'，用於調整提示文字
 */
interface InputFormProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
  context?: 'homepage' | 'chat'; // Add new context prop
}

/**
 * 輸入表單組件 - 提供用戶輸入查詢的界面
 * 支持多行文字輸入，Enter 鍵提交，Shift+Enter 換行
 */
export function InputForm({
  onSubmit,
  isLoading,
  context = 'homepage',
}: InputFormProps) {
  const [inputValue, setInputValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 組件載入時自動聚焦到輸入框
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  // 處理表單提交
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onSubmit(inputValue.trim());
      setInputValue('');
    }
  };

  // 處理鍵盤按下事件：Enter 提交，Shift+Enter 換行
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // 根據使用場景顯示不同的提示文字
  const placeholderText =
    context === 'chat'
      ? '回應 Agent、優化計畫，或輸入「看起來不錯」...'
      : '問我任何問題... 例如：關於最新 Google I/O 的報告';

  return (
    <form onSubmit={handleSubmit} className='flex flex-col gap-2'>
      <div className='flex items-end space-x-2'>
        <Textarea
          ref={textareaRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholderText}
          rows={1}
          className='flex-1 resize-none pr-10 min-h-[40px]'
        />
        <Button
          type='submit'
          size='icon'
          disabled={isLoading || !inputValue.trim()}
        >
          {isLoading ? (
            <Loader2 className='h-4 w-4 animate-spin' />
          ) : (
            <Send className='h-4 w-4' />
          )}
        </Button>
      </div>
    </form>
  );
}
