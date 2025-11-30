import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite 設定檔的官方文件：https://vitejs.dev/config/
export default defineConfig({
  // 'plugins' 是一個陣列，用於設定 Vite 要使用的插件
  // '@vitejs/plugin-react' 讓 Vite 能夠理解和處理 React JSX 語法
  plugins: [react()],

  // 'server' 物件用於設定 Vite 開發伺服器的行為
  server: {
    // 'port' 指定開發伺服器運行的埠號
    port: 5173,

    // 'host: true' 會將主機設定為 0.0.0.0，允許從區域網路中的其他裝置存取
    host: true,

    // 'proxy' 用於設定 API 請求代理，解決開發時的跨域問題
    proxy: {
      // 當前端程式碼中有名為 '/api/copilotkit' 的請求時
      '/api/copilotkit': {
        // 將該請求轉發到 'http://localhost:8000'
        target: 'http://localhost:8000',

        // 'changeOrigin: true' 會修改請求標頭中的 Origin 欄位，
        // 使其與目標 URL 的來源相符，這對於某些後端伺服器的安全檢查是必要的
        changeOrigin: true,
      },
    },
  },
})
