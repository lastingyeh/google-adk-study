import { useState } from "react";
import { ProductCard } from "./ProductCard";

interface FeatureShowcaseProps {
  userData: {
    name: string;
    email: string;
    accountType: string;
    orders: string[];
    memberSince: string;
  };
}

export function FeatureShowcase({ userData }: FeatureShowcaseProps) {
  const [activeTab, setActiveTab] = useState<"generative" | "hitl" | "state">("generative");

  return (
    <div className="border-t bg-muted/30">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <h2 className="text-2xl font-bold mb-2">進階功能展示</h2>
          <p className="text-muted-foreground">
            探索由 Google ADK 驅動的這個 AI 助理的功能
          </p>
        </div>

        {/* 功能分頁 */}
        <div className="flex gap-2 mb-6 flex-wrap">
          <button
            onClick={() => setActiveTab("generative")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === "generative"
                ? "bg-primary text-primary-foreground"
                : "bg-background border hover:bg-accent"
            }`}
          >
            🎨 生成式 UI (Generative UI)
          </button>
          <button
            onClick={() => setActiveTab("hitl")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === "hitl"
                ? "bg-primary text-primary-foreground"
                : "bg-background border hover:bg-accent"
            }`}
          >
            🔐 人機協作 (Human-in-the-Loop)
          </button>
          <button
            onClick={() => setActiveTab("state")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === "state"
                ? "bg-primary text-primary-foreground"
                : "bg-background border hover:bg-accent"
            }`}
          >
            👤 共享狀態 (Shared State)
          </button>
        </div>

        {/* 功能內容 */}
        <div className="bg-background rounded-lg border p-6">
          {activeTab === "generative" && (
            <div>
              <h3 className="text-xl font-semibold mb-3">生成式 UI (Generative UI)</h3>
              <p className="text-muted-foreground mb-4">
                Agent 可以在聊天中直接渲染豐富的互動式 React 元件。
                試著問：<strong>"Show me product PROD-001" (顯示產品 PROD-001)</strong>
              </p>
              <div className="grid md:grid-cols-2 gap-4">
                <ProductCard
                  name="Widget Pro"
                  price={99.99}
                  image="https://placehold.co/400x400/6366f1/fff.png"
                  rating={4.5}
                  inStock={true}
                />
                <ProductCard
                  name="Gadget Plus"
                  price={149.99}
                  image="https://placehold.co/400x400/8b5cf6/fff.png"
                  rating={4.8}
                  inStock={true}
                />
              </div>
              <div className="mt-4 p-4 bg-muted rounded-lg">
                <p className="text-sm font-mono">
                  <strong>運作方式：</strong> 當 Agent 呼叫{" "}
                  <code className="bg-background px-1 rounded">create_product_card()</code> 時，
                  前端接收結構化資料並將其渲染為 React 元件，而不是純文字。
                </p>
              </div>
            </div>
          )}

          {activeTab === "hitl" && (
            <div>
              <h3 className="text-xl font-semibold mb-3">人機協作 (Human-in-the-Loop, HITL)</h3>
              <p className="text-muted-foreground mb-4">
                敏感操作執行前需要明確的使用者批准。試著問：{" "}
                <strong>"I want a refund for order ORD-12345" (我想為訂單 ORD-12345 退款)</strong>
              </p>
              <div className="space-y-4">
                <div className="border rounded-lg p-4 bg-card">
                  <h4 className="font-semibold mb-2">🔔 需要退款批准</h4>
                  <div className="space-y-2 text-sm">
                    <p>
                      <strong>訂單 ID：</strong> ORD-12345
                    </p>
                    <p>
                      <strong>金額：</strong> $99.99
                    </p>
                    <p>
                      <strong>原因：</strong> 產品瑕疵
                    </p>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <button className="px-4 py-2 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-lg text-sm">
                      ❌ 取消
                    </button>
                    <button className="px-4 py-2 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-lg text-sm">
                      ✅ 批准
                    </button>
                  </div>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm font-mono">
                    <strong>運作方式：</strong> 當 Agent 嘗試處理退款時，它會暫停並顯示確認對話框。Agent 只有在您批准後才會繼續。您也可以取消操作。
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === "state" && (
            <div>
              <h3 className="text-xl font-semibold mb-3">共享狀態 (Shared State)</h3>
              <p className="text-muted-foreground mb-4">
                Agent 無需詢問即可即時存取您的使用者情境。試試：{" "}
                <strong>"What's my account status?" (我的帳戶狀態是什麼？)</strong>
              </p>
              <div className="space-y-4">
                <div className="border rounded-lg p-4 bg-card">
                  <h4 className="font-semibold mb-3">您的帳戶資訊</h4>
                  <div className="grid gap-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">姓名：</span>
                      <span className="font-medium">{userData.name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">電子郵件：</span>
                      <span className="font-medium">{userData.email}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">帳戶類型：</span>
                      <span className="font-medium bg-primary/10 text-primary px-2 py-1 rounded">
                        {userData.accountType}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">最近訂單：</span>
                      <span className="font-medium">{userData.orders.join(", ")}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">加入時間：</span>
                      <span className="font-medium">{userData.memberSince}</span>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm font-mono">
                    <strong>運作方式：</strong> 前端使用{" "}
                    <code className="bg-background px-1 rounded">useCopilotReadable()</code> 與 Agent 分享此資料。
                    Agent 可以在回應中引用它，而無需詢問您問題。
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="mt-6 text-center">
          <a
            href="/advanced"
            className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
          >
            檢視實作細節 →
          </a>
        </div>
      </div>
    </div>
  );
}

// 重點摘要
// - **核心概念**：首頁底部的功能展示元件，讓使用者可以快速預覽三個進階功能。
// - **關鍵技術**：React Components, State Management (useState), Conditional Rendering.
// - **重要結論**：使用分頁切換不同功能的說明和靜態範例。
// - **行動項目**：無。
