/**
 * @fileoverview
 * 這個檔案定義了 `LiveAPIContext`，它提供了一個 React Context，
 * 用於在整個應用程式中共享與即時 API 互動的狀態和函式。
 */

// 從 'react' 函式庫中匯入必要的功能
import { createContext, FC, ReactNode, useContext } from 'react';
// 從自訂的 use-live-api 鉤子 (hook) 中匯入主要的鉤子函式和其回傳值的型別
import { useLiveAPI, UseLiveAPIResults } from '../hooks/use-live-api';

/**
 * 建立 LiveAPIContext。
 * 這是一個 React Context 物件，將用於在元件樹中向下傳遞 API 的狀態和函式。
 * 它的初始值為 undefined，因為提供者 (Provider) 將會提供實際的值。
 * @type {React.Context<UseLiveAPIResults | undefined>}
 */
const LiveAPIContext = createContext<UseLiveAPIResults | undefined>(undefined);

/**
 * 定義 LiveAPIProvider 元件的 props 型別。
 */
export type LiveAPIProviderProps = {
  /** 子元件，React 會自動傳入 */
  children: ReactNode;
  /** API 的 URL，此為可選屬性 */
  url?: string;
  /** 使用者 ID，此為可選屬性 */
  userId?: string;
};

/**
 * LiveAPIProvider 元件。
 * 這是一個函式元件 (Functional Component)，它會將其子元件包裹在 Context Provider 中。
 * 它會初始化 useLiveAPI 鉤子，並將其結果作為 context 的值提供給所有後代元件。
 * @param {LiveAPIProviderProps} props - 元件的 props。
 * @returns {JSX.Element}
 */
export const LiveAPIProvider: FC<LiveAPIProviderProps> = ({
  url,
  userId,
  children,
}) => {
  // 呼叫 useLiveAPI 鉤子，傳入 url 和 userId，以取得與 API 互動所需的所有狀態和函式
  const liveAPI = useLiveAPI({ url, userId });

  // 回傳 Context Provider，並將 useLiveAPI 的回傳值作為 value 傳遞下去
  // 這樣，任何被 <LiveAPIProvider> 包裹的子元件都能夠存取到 liveAPI 的值
  return (
    <LiveAPIContext.Provider value={liveAPI}>
      {children}
    </LiveAPIContext.Provider>
  );
};

/**
 * useLiveAPIContext 自訂鉤子。
 * 這是一個輔助鉤子，讓後代元件可以輕易地存取 LiveAPIContext 的值。
 * 它簡化了 `useContext(LiveAPIContext)` 的使用方式。
 * @throws {Error} 如果在 LiveAPIProvider 的範圍之外使用此鉤子，將會拋出錯誤。
 * @returns {UseLiveAPIResults} 從 context 中取得的 API 狀態和函式。
 */
export const useLiveAPIContext = () => {
  // 使用 React 的 useContext 鉤子來讀取 context 的目前值
  const context = useContext(LiveAPIContext);
  // 進行檢查，確保此鉤子是在 LiveAPIProvider 內部被呼叫
  if (!context) {
    throw new Error('useLiveAPIContext 必須在 LiveAPIProvider 內部使用');
  }
  // 回傳 context 的值
  return context;
};
