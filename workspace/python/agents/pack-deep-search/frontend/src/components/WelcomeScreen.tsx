import { Button } from '@/components/ui/button';
import { InputForm } from '@/components/InputForm';

/**
 * 歡迎畫面組件的屬性定義
 * @property handleSubmit - 處理用戶提交查詢的函數
 * @property isLoading - 載入狀態標記
 * @property onCancel - 取消操作的回調函數
 */
interface WelcomeScreenProps {
  handleSubmit: (query: string) => void;
  isLoading: boolean;
  onCancel: () => void;
}

/**
 * 歡迎畫面組件 - 顯示應用程式首頁和輸入表單
 * 此組件在用戶尚未開始對話時顯示，提供初始的查詢輸入界面
 */
export function WelcomeScreen({
  handleSubmit,
  isLoading,
  onCancel,
}: WelcomeScreenProps) {
  return (
    // 此容器填滿父層提供的空間，並將內容（卡片）置中顯示
    // 適用於分割視圖中的左側面板等佈局
    <div className='flex-1 flex flex-col items-center justify-center p-4 overflow-hidden relative'>
      {/* 「卡片」容器 */}
      {/* 此 div 包含卡片的所有樣式：背景、模糊效果、內距、邊框、陰影和懸停效果 */}
      <div
        className='w-full max-w-2xl z-10
                      bg-neutral-900/50 backdrop-blur-md
                      p-8 rounded-2xl border border-neutral-700
                      shadow-2xl shadow-black/60
                      transition-all duration-300 hover:border-neutral-600'
      >
        {/* 卡片標題區塊 */}
        <div className='text-center space-y-4'>
          <h1 className='text-4xl font-bold text-white flex items-center justify-center gap-3'>
            ✨ 深度搜尋 - ADK 🚀
          </h1>
          <p className='text-lg text-neutral-300 max-w-md mx-auto'>
            將您的問題轉化為全面的報告！
          </p>
        </div>

        {/* 卡片的輸入表單區塊 */}
        <div className='mt-8'>
          <InputForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
            context='homepage'
          />
          {isLoading && (
            <div className='mt-4 flex justify-center'>
              <Button
                variant='outline'
                onClick={onCancel}
                className='text-red-400 hover:text-red-300 hover:bg-red-900/20 border-red-700/50' // 增強的取消按鈕樣式
              >
                取消
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
