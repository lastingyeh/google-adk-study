import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

// Create the React root element
// 建立 React 根元素
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

// Render the App component
// 渲染 App 組件
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
// 如果您想開始測量應用程式的效能，請傳遞一個函數
// 來記錄結果 (例如：reportWebVitals(console.log))
// 或發送到分析端點。了解更多：https://bit.ly/CRA-vitals
reportWebVitals();
