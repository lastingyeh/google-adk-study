import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "客戶支援聊天",
  description: "由 Google ADK 驅動的 AI 客戶支援",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-TW">
      {/* suppressHydrationWarning 防止 React 記錄瀏覽器擴充功能
          或其他僅限客戶端的修改 (例如 cz-shortcut-listen) 所注入的屬性
          造成的不符合。這是安全的，因為 body 元素的內容完全是
          客戶端渲染的包裝內容，我們不依賴這些屬性進行渲染邏輯。 */}
      <body className={inter.className} suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}

// 重點摘要
// - **核心概念**：Next.js 應用程式的根佈局 (Root Layout)。
// - **關鍵技術**：Next.js App Router, Metadata API, Google Fonts。
// - **重要結論**：設定了全域樣式、字體 (Inter) 和 metadata。
// - **行動項目**：無。
