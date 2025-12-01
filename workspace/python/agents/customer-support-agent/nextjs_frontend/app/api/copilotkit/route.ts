/**
 * CopilotKit API Route
 *
 * 此路由作為 CopilotKit 的 GraphQL 前端與 ADK 代理人後端的 REST API 之間的代理。
 */

import { NextRequest } from "next/server";
import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";

// 從環境變數獲取後端 URL
const backendUrl = process.env.NEXT_PUBLIC_AGENT_URL || "http://localhost:8000";

// 建立一個 CopilotRuntime 實例，配置指向 ADK 後端 (AG-UI 端點) 的 HttpAgent。
// 這符合 CopilotKit 部落格中推薦的 ADK + AG-UI 整合模式。
const serviceAdapter = new ExperimentalEmptyAdapter();

const runtime = new CopilotRuntime({
  agents: {
    customer_support_agent: new HttpAgent({ url: `${backendUrl}/api/copilotkit` }),
  },
});

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};

// 重點摘要
// - **核心概念**：Next.js API 路由，作為 CopilotKit 前端與後端 ADK Agent 的橋樑。
// - **關鍵技術**：Next.js App Router, CopilotKit Runtime, AG-UI Client。
// - **重要結論**：使用 `ExperimentalEmptyAdapter` 和 `HttpAgent` 來整合 AG-UI 協定，將請求轉發至後端。
// - **行動項目**：無。
