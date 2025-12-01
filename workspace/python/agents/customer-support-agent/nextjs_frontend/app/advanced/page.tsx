"use client";

import Link from "next/link";
import { ProductCard } from "@/components/ProductCard";

/**
 * 進階功能示範頁面 (Advanced Features Demo Page)
 *
 * 此頁面展示了教學 30 中可用的三個進階功能：
 * 1. 生成式 UI (Generative UI) - 根據 Agent 回應渲染 React 元件
 * 2. 人機協作 (Human-in-the-Loop) - 敏感操作需使用者批准
 * 3. 共享狀態 (Shared State) - 與 Agent 情境同步應用程式狀態
 */
export default function AdvancedFeaturesPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-12">
        {/* 頁首 */}
        <div className="mb-8">
          <Link
            href="/"
            className="text-sm text-muted-foreground hover:text-foreground mb-4 inline-block"
          >
            ← 返回聊天
          </Link>
          <h1 className="text-4xl font-bold mb-2">進階功能</h1>
          <p className="text-lg text-muted-foreground">
            探索能增強客戶支援體驗的強大功能
          </p>
        </div>

        {/* 功能網格 */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {/* 功能 1：生成式 UI */}
          <div className="border rounded-lg p-6 bg-card">
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-primary"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
                />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold mb-2">生成式 UI (Generative UI)</h2>
            <p className="text-muted-foreground mb-4">
              Agent 可以在聊天中直接渲染豐富的互動式 React 元件。
            </p>
            <div className="space-y-2 text-sm">
              <div className="flex items-start gap-2">
                <span className="text-primary">✓</span>
                <span>包含圖片的產品卡片</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-primary">✓</span>
                <span>動態資料視覺化</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-primary">✓</span>
                <span>互動式元件</span>
              </div>
            </div>
          </div>

          {/* 功能 2：人機協作 */}
          <div className="border rounded-lg p-6 bg-card">
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-primary"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold mb-2">人機協作 (Human-in-the-Loop)</h2>
            <p className="text-muted-foreground mb-4">
              關鍵動作執行前需要使用者批准。
            </p>
            <div className="space-y-2 text-sm">
              <div className="flex items-start gap-2">
                <span className="text-primary">✓</span>
                <span>退款批准</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-primary">✓</span>
                <span>資料修改</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-primary">✓</span>
                <span>敏感操作</span>
              </div>
            </div>
          </div>

          {/* 功能 3：共享狀態 */}
          <div className="border rounded-lg p-6 bg-card">
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-primary"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
                />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold mb-2">共享狀態 (Shared State)</h2>
            <p className="text-muted-foreground mb-4">
              Agent 可即時存取應用程式和使用者情境。
            </p>
            <div className="space-y-2 text-sm">
              <div className="flex items-start gap-2">
                <span className="text-primary">✓</span>
                <span>使用者帳戶資料</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-primary">✓</span>
                <span>訂單歷史</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-primary">✓</span>
                <span>工作階段偏好設定</span>
              </div>
            </div>
          </div>
        </div>

        {/* 示範區塊 */}
        <div className="space-y-8">
          {/* 功能 1 示範 */}
          <div className="border rounded-lg p-8 bg-card">
            <h3 className="text-2xl font-semibold mb-4">1. 生成式 UI 範例</h3>
            <p className="text-muted-foreground mb-6">
              當 Agent 呼叫 <code className="px-2 py-1 bg-muted rounded">create_product_card()</code> 時，
              前端會渲染一個豐富的產品卡片元件：
            </p>
            <div className="flex justify-center">
              <ProductCard
                name="Widget Pro"
                price={99.99}
                image="https://placehold.co/400x400/6366f1/fff.png"
                rating={4.5}
                inStock={true}
              />
            </div>
            <div className="mt-6 p-4 bg-muted rounded-lg">
              <p className="text-sm font-semibold mb-2">試著問：</p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>"Show me product PROD-001" (顯示產品 PROD-001)</li>
                <li>"What products do you have available?" (你們有哪些產品？)</li>
                <li>"Tell me about the Widget Pro" (告訴我關於 Widget Pro 的資訊)</li>
              </ul>
            </div>
          </div>

          {/* 功能 2 示範 */}
          <div className="border rounded-lg p-8 bg-card">
            <h3 className="text-2xl font-semibold mb-4">2. 人機協作範例</h3>
            <p className="text-muted-foreground mb-6">
              當 Agent 嘗試退款時，您會看到一個確認對話框：
            </p>
            <div className="p-6 border-2 border-dashed rounded-lg bg-background">
              <div className="text-center">
                <div className="text-4xl mb-4">🔔</div>
                <h4 className="text-lg font-semibold mb-2">需要退款批准</h4>
                <div className="text-sm text-muted-foreground space-y-1 mb-4">
                  <p>訂單 ID：ORD-12345</p>
                  <p>金額：$99.99</p>
                  <p>原因：產品瑕疵</p>
                </div>
                <div className="flex gap-2 justify-center">
                  <button className="px-4 py-2 bg-primary text-primary-foreground rounded-md">
                    批准
                  </button>
                  <button className="px-4 py-2 bg-muted text-muted-foreground rounded-md">
                    拒絕
                  </button>
                </div>
              </div>
            </div>
            <div className="mt-6 p-4 bg-muted rounded-lg">
              <p className="text-sm font-semibold mb-2">試著問：</p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>"I want a refund for order ORD-12345" (我想為訂單 ORD-12345 退款)</li>
                <li>"Process a refund of $99.99 for my order" (為我的訂單處理 $99.99 的退款)</li>
                <li>"Can you refund my purchase?" (你能為我的購買退款嗎？)</li>
              </ul>
            </div>
          </div>

          {/* 功能 3 示範 */}
          <div className="border rounded-lg p-8 bg-card">
            <h3 className="text-2xl font-semibold mb-4">3. 共享狀態範例</h3>
            <p className="text-muted-foreground mb-6">
              Agent 無需詢問即可存取您的帳戶資訊：
            </p>
            <div className="p-6 border rounded-lg bg-background">
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="font-semibold">姓名：</span>
                  <span className="text-muted-foreground">John Doe</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-semibold">電子郵件：</span>
                  <span className="text-muted-foreground">john@example.com</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-semibold">帳戶類型：</span>
                  <span className="text-primary font-semibold">Premium</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-semibold">訂單：</span>
                  <span className="text-muted-foreground">ORD-12345, ORD-67890</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-semibold">加入時間：</span>
                  <span className="text-muted-foreground">2023 年 1 月 15 日</span>
                </div>
              </div>
            </div>
            <div className="mt-6 p-4 bg-muted rounded-lg">
              <p className="text-sm font-semibold mb-2">試著問：</p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>"What's my account status?" (我的帳戶狀態是什麼？)</li>
                <li>"Show me my recent orders" (顯示我最近的訂單)</li>
                <li>"When did I join?" (我什麼時候加入的？)</li>
              </ul>
            </div>
          </div>
        </div>

        {/* 實作指南 */}
        <div className="mt-12 border rounded-lg p-8 bg-card">
          <h3 className="text-2xl font-semibold mb-4">實作細節</h3>
          <div className="space-y-6">
            <div>
              <h4 className="font-semibold mb-2">後端 (agent/agent.py)</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• <code>create_product_card()</code> - 回傳結構化產品資料</li>
                <li>• <code>process_refund()</code> - 處理退款邏輯</li>
                <li>• Agent 指令包含所有功能的引導</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">前端 (app/page.tsx)</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• <code>useCopilotAction()</code> - 註冊生成式 UI 和 HITL 的動作</li>
                <li>• <code>useCopilotReadable()</code> - 與 Agent 分享狀態</li>
                <li>• <code>ProductCard</code> 元件 - 豐富的 UI 渲染</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">元件 (components/)</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• <code>ProductCard.tsx</code> - 可重複使用的產品顯示元件</li>
                <li>• <code>ThemeToggle.tsx</code> - 深色/淺色模式切換器</li>
              </ul>
            </div>
          </div>
        </div>

        {/* 返回聊天按鈕 */}
        <div className="mt-8 text-center">
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
            在聊天中嘗試進階功能
          </Link>
        </div>
      </div>
    </div>
  );
}

// 重點摘要
// - **核心概念**：進階功能展示頁面，介紹生成式 UI、人機協作和共享狀態。
// - **關鍵技術**：Next.js, React Components, Tailwind CSS。
// - **重要結論**：
//   - 使用卡片佈局展示每個功能的說明和優點。
//   - 提供互動式範例 (如 ProductCard, 退款對話框 mockup)。
//   - 列出實作細節，幫助開發者理解前後端整合方式。
// - **行動項目**：無。
