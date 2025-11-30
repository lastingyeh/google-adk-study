import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx' // 匯入主要的 App 元件
import './App.css' // 匯入應用程式的全域樣式

// 使用 ReactDOM.createRoot 來建立應用的根節點
// 'document.getElementById('root')!' 表示我們確定 ID 為 'root' 的元素存在
ReactDOM.createRoot(document.getElementById('root')!).render(
  // <React.StrictMode> 是一個用於突顯應用程式中潛在問題的工具
  // 它不會渲染任何可見的 UI，只在開發模式下啟用額外的檢查與警告
  <React.StrictMode>
    {/* 渲染 App 元件 */}
    <App />
  </React.StrictMode>,
)
