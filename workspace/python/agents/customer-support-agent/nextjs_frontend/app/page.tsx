"use client";

import { useState, useEffect } from "react";
import { CopilotKit, useCopilotReadable, useCopilotAction } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import { ThemeToggle } from "@/components/ThemeToggle";
import { ProductCard } from "@/components/ProductCard";
import { FeatureShowcase } from "@/components/FeatureShowcase";
import { Markdown } from "@copilotkit/react-ui";

/**
 * ChatInterface 元件具備進階功能：
 * 1. 生成式 UI (Generative UI) - 根據 Agent 回應渲染產品卡片
 * 2. 人機協作 (Human-in-the-Loop) - 使用者批准退款
 * 3. 共享狀態 (Shared State) - Agent 可讀取的使用者情境
 */
function ChatInterface() {
  // 功能 3：共享狀態 - Agent 可讀取的使用者情境
  const [userData] = useState({
    name: "John Doe",
    email: "john@example.com",
    accountType: "Premium",
    orders: ["ORD-12345", "ORD-67890"],
    memberSince: "2023-01-15",
  });

  // 功能 1：生成式 UI - 用於渲染的產品資料狀態
  const [currentProduct, setCurrentProduct] = useState<{
    name: string;
    price: number;
    image: string;
    rating: number;
    inStock: boolean;
  } | null>(null);

  // 讓 Agent 可讀取使用者資料
  useCopilotReadable({
    description: "當前使用者的帳戶資訊和訂單歷史",
    value: userData,
  });

  // 功能 1：生成式 UI - Agent 可以呼叫的前端動作，用於渲染產品卡片
  // 使用 available: "remote" 表示此動作僅可由後端 Agent 呼叫
  useCopilotAction({
    name: "render_product_card",
    available: "remote",
    description: "在聊天介面中渲染帶有產品詳情的產品卡片",
    parameters: [
      { name: "name", type: "string", description: "產品名稱", required: true },
      { name: "price", type: "number", description: "產品價格 (美元)", required: true },
      { name: "image", type: "string", description: "產品圖片 URL", required: true },
      { name: "rating", type: "number", description: "產品評分 (0-5)", required: true },
      { name: "inStock", type: "boolean", description: "產品庫存狀態", required: true },
    ],
    handler: async ({ name, price, image, rating, inStock }) => {
      // 更新狀態以顯示產品卡片
      setCurrentProduct({ name, price, image, rating, inStock });

      // 回傳成功訊息給 Agent
      return `已成功為 ${name} 顯示產品卡片`;
    },
    render: ({ args, status }) => {
      // 處理中顯示載入狀態
      if (status !== "complete") {
        return (
          <div className="p-4 border rounded-lg animate-pulse bg-card">
            <div className="h-48 bg-muted rounded mb-4"></div>
            <div className="h-4 bg-muted rounded w-3/4 mb-2"></div>
            <div className="h-4 bg-muted rounded w-1/2"></div>
          </div>
        );
      }

      // 完成時渲染實際的 ProductCard 元件
      return (
        <div className="my-4">
          <ProductCard
            name={args.name}
            price={args.price}
            image={args.image}
            rating={args.rating}
            inStock={args.inStock}
          />
        </div>
      );
    },
  });

  // 功能 2：人機協作 - 退款批准
  // 管理批准對話框的狀態
  const [refundRequest, setRefundRequest] = useState<{
    order_id: string;
    amount: number;
    reason: string;
  } | null>(null);

  // 僅限前端的動作，使用 available: "remote" 顯示批准對話框
  useCopilotAction({
    name: "process_refund",
    available: "remote",
    description: "經使用者批准後處理退款",
    parameters: [
      { name: "order_id", type: "string", description: "要退款的訂單 ID", required: true },
      { name: "amount", type: "number", description: "退款金額", required: true },
      { name: "reason", type: "string", description: "退款原因", required: true },
    ],
    handler: async ({ order_id, amount, reason }) => {
      console.log("🔍 HITL handler 被呼叫，參數：", { order_id, amount, reason });

      // 儲存退款請求以顯示在對話框中
      setRefundRequest({ order_id, amount, reason });

      // 回傳一個 promise，當使用者批准/取消時解決
      return new Promise((resolve) => {
        // 我們將在對話框按鈕中解決這個 promise
        (window as any).__refundPromiseResolve = resolve;
      });
    },
    render: ({ args, status }) => {
      console.log("🔍 HITL render - 狀態：", status, "參數：", args);

      if (status !== "complete") {
        // 等待使用者決定時顯示載入狀態
        return (
          <div className="p-5 border-2 border-yellow-300 dark:border-yellow-700 rounded-xl bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 space-y-3 shadow-lg">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-yellow-500 rounded-full flex items-center justify-center animate-pulse">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h4 className="font-bold text-lg text-yellow-900 dark:text-yellow-100">等待您的批准</h4>
                <p className="text-sm text-yellow-700 dark:text-yellow-300">請檢閱上方的模態對話框</p>
              </div>
            </div>
            <div className="pl-13 space-y-1">
              <div className="flex items-center gap-2 text-sm text-yellow-800 dark:text-yellow-200">
                <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                <span>訂單：<strong>{args.order_id}</strong></span>
              </div>
              <div className="flex items-center gap-2 text-sm text-yellow-800 dark:text-yellow-200">
                <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" style={{ animationDelay: "0.2s" }}></div>
                <span>金額：<strong>${args.amount}</strong></span>
              </div>
            </div>
          </div>
        );
      }

      return (
        <div className="p-4 border-2 border-green-300 dark:border-green-700 rounded-lg bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 flex items-center gap-3 shadow-md">
          <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div>
            <p className="font-semibold text-green-900 dark:text-green-100">決定已記錄</p>
            <p className="text-sm text-green-700 dark:text-green-300">正在處理您的選擇...</p>
          </div>
        </div>
      );
    },
  });

  // 當 refundRequest 設定時渲染批准對話框
  const handleRefundApproval = async (approved: boolean) => {
    console.log("🔍 使用者決定：", approved ? "批准" : "取消");

    const resolve = (window as any).__refundPromiseResolve;
    if (resolve && refundRequest) {
      if (approved) {
        // 呼叫後端 API 實際處理退款
        try {
          const response = await fetch("http://localhost:8000/api/copilotkit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              action: "process_refund_backend",
              params: refundRequest,
            }),
          });
          const result = await response.json();
          resolve({
            approved: true,
            message: `訂單 ${refundRequest.order_id} 退款處理成功`,
          });
        } catch (error) {
          resolve({
            approved: true,
            message: `訂單 ${refundRequest.order_id} 退款已批准 - $${refundRequest.amount}`,
          });
        }
      } else {
        resolve({
          approved: false,
          message: "使用者取消退款",
        });
      }
    }

    setRefundRequest(null);
    delete (window as any).__refundPromiseResolve;
  };

  // 模態框的鍵盤支援 (ESC 取消，Enter 批准)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (refundRequest) {
        if (e.key === "Escape") {
          e.preventDefault();
          handleRefundApproval(false);
        } else if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          handleRefundApproval(true);
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [refundRequest]);  return (
    <div className="flex flex-col min-h-screen">
      {/* HITL 批准對話框 - 增強使用者體驗的模態框 */}
      {refundRequest && (
        <div
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4 animate-in fade-in duration-200"
          onClick={(e) => {
            // 如果點擊背景則關閉模態框
            if (e.target === e.currentTarget) {
              handleRefundApproval(false);
            }
          }}
        >
          <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-2xl p-8 max-w-md w-full shadow-2xl animate-in zoom-in-95 duration-200">
            {/* 標頭與圖示 */}
            <div className="flex items-start gap-4 mb-6">
              <div className="flex-shrink-0 w-14 h-14 bg-yellow-400 dark:bg-yellow-500 rounded-full flex items-center justify-center shadow-lg">
                <svg className="w-8 h-8 text-gray-900 dark:text-gray-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-1">需要退款批准</h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">請仔細檢閱下方詳情</p>
              </div>
            </div>

            {/* 退款詳情卡片 */}
            <div className="space-y-3 bg-gray-50 dark:bg-gray-800 rounded-lg p-5 mb-6 border border-gray-200 dark:border-gray-700">
              <div className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                <span className="text-sm font-medium text-gray-600 dark:text-gray-400">訂單 ID</span>
                <span className="text-sm font-mono font-semibold text-gray-900 dark:text-gray-100 bg-gray-100 dark:bg-gray-700 px-3 py-1.5 rounded-md">
                  {refundRequest.order_id}
                </span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                <span className="text-sm font-medium text-gray-600 dark:text-gray-400">退款金額</span>
                <span className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  ${refundRequest.amount.toFixed(2)}
                </span>
              </div>
              <div className="pt-2">
                <span className="text-sm font-medium text-gray-600 dark:text-gray-400 block mb-2">原因</span>
                <div className="text-sm text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-900 rounded-md p-3 border border-gray-200 dark:border-gray-700">
                  {refundRequest.reason}
                </div>
              </div>
            </div>

            {/* 警告訊息 */}
            <div className="flex items-start gap-3 mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-500 rounded-r-lg shadow-sm">
              <svg className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <p className="text-sm text-yellow-900 dark:text-yellow-100 font-medium">
                此動作無法復原。批准後將立即處理退款。
              </p>
            </div>

            {/* 動作按鈕 */}
            <div className="flex gap-4">
              <button
                onClick={() => handleRefundApproval(false)}
                className="flex-1 px-6 py-3.5 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-gray-100 rounded-xl font-bold transition-all duration-200 hover:scale-105 active:scale-95 flex items-center justify-center gap-2 shadow-md"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                </svg>
                取消
              </button>
              <button
                onClick={() => handleRefundApproval(true)}
                className="flex-1 px-6 py-3.5 bg-green-600 hover:bg-green-700 dark:bg-green-600 dark:hover:bg-green-500 text-white rounded-xl font-bold transition-all duration-200 hover:scale-105 active:scale-95 flex items-center justify-center gap-2 shadow-lg"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                </svg>
                批准退款
              </button>
            </div>

            {/* ESC 提示 */}
            <p className="text-xs text-center text-gray-500 dark:text-gray-400 mt-5">
              按 <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded text-xs font-mono text-gray-900 dark:text-gray-100 shadow-sm">ESC</kbd> 取消
            </p>
          </div>
        </div>
      )}

      {/* 頁首 */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-md">
                <svg
                  className="w-5 h-5 text-primary-foreground"
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
              </div>
              <div>
                <h1 className="text-lg font-semibold">客戶支援助理</h1>
                <p className="text-xs text-muted-foreground">
                  AI 驅動協助 • 已登入為 {userData.name}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <a
                href="/advanced"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
                進階功能
              </a>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      {/* 主要內容 - 聊天 */}
      <main className="flex-1">
        <div className="container mx-auto px-4 py-6 h-[600px]">
          <div className="h-full border rounded-lg bg-card">
            <CopilotChat
              instructions="你是一位友善且專業的客戶支援代理人。請樂於助人、有同理心，並提供清晰、可行的解決方案。你可以存取使用者的帳戶資訊。"
              labels={{
                title: "支援聊天",
                initial:
                  "👋 您好！我是您的 AI 支援助理。\n\n" +
                  "**試試這些範例提示：**\n\n" +
                  "🎨 **生成式 UI (Generative UI)**\n" +
                  "• \"Show me product PROD-001\" (顯示產品 PROD-001)\n" +
                  "• \"Display product PROD-002\" (顯示產品 PROD-002)\n\n" +
                  "🔐 **人機協作 (Human-in-the-Loop)**\n" +
                  "• \"I want a refund for order ORD-12345\" (我想為訂單 ORD-12345 退款)\n" +
                  "• \"Process a refund for my purchase\" (為我的購買處理退款)\n\n" +
                  "👤 **共享狀態 (Shared State)**\n" +
                  "• \"What's my account status?\" (我的帳戶狀態是什麼？)\n" +
                  "• \"Show me my recent orders\" (顯示我最近的訂單)\n\n" +
                  "📦 **一般支援**\n" +
                  "• \"What is your refund policy?\" (你的退款政策是什麼？)\n" +
                  "• \"Track my order ORD-67890\" (追蹤我的訂單 ORD-67890)\n" +
                  "• \"I need help with a billing issue\" (我需要協助解決帳單問題)\n\n" +
                  "💡 *向下捲動查看所有功能的互動式示範！*",
              }}
              className="h-full"
            />
          </div>
        </div>
      </main>

      {/* 功能展示 */}
      <FeatureShowcase userData={userData} />
    </div>
  );
}

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <CopilotKit runtimeUrl="/api/copilotkit" agent="customer_support_agent">
        <ChatInterface />
      </CopilotKit>
    </div>
  );
}

// 重點摘要
// - **核心概念**：首頁元件，整合了 CopilotKit 的聊天介面和進階功能。
// - **關鍵技術**：Next.js, CopilotKit (useCopilotReadable, useCopilotAction, CopilotChat), React Hooks (useState, useEffect)。
// - **重要結論**：
//   - 使用 `useCopilotReadable` 提供共享狀態給 Agent。
//   - 使用 `useCopilotAction` 定義生成式 UI (`render_product_card`) 和人機協作 (`process_refund`) 動作。
//   - 實作了退款批准的模態對話框。
//   - 整合了 `ProductCard` 和 `FeatureShowcase` 元件。
// - **行動項目**：無。
