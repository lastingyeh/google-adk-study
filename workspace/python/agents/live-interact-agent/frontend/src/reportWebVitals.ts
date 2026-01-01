import { ReportHandler } from "web-vitals";

/**
 * Function to measure and report web vitals performance metrics.
 * 用於測量和報告 Web Vitals 效能指標的函數。
 *
 * @param onPerfEntry - Optional callback function to handle performance entries.
 *                      可選的回調函數，用於處理效能條目。
 */
const reportWebVitals = (onPerfEntry?: ReportHandler) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    // Dynamically import web-vitals library to reduce initial bundle size
    // 動態導入 web-vitals 庫以減少初始打包大小
    import("web-vitals").then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry); // Cumulative Layout Shift (累計版面配置轉移)
      getFID(onPerfEntry); // First Input Delay (首次輸入延遲)
      getFCP(onPerfEntry); // First Contentful Paint (首次內容繪製)
      getLCP(onPerfEntry); // Largest Contentful Paint (最大內容繪製)
      getTTFB(onPerfEntry); // Time to First Byte (首字節時間)
    });
  }
};

export default reportWebVitals;
