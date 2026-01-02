# Phase 2: 工具整合與 UI

## Week 3: 工具整合

### 步驟 1: Google Search Grounding

#### 1.1 建立 Google Search Tool

**backend/tools/google_search.py**:

```python
"""Google Search Grounding Tool

提供即時網路搜尋功能，整合 Google Search Grounding API。
支援引用來源追蹤與顯示。
"""
from google import genai
from google.genai import types
import logging

logger = logging.getLogger(__name__)

def create_google_search_tool() -> types.Tool:
    """建立 Google Search Tool
    
    Returns:
        types.Tool: Google Search Tool 配置
    """
    return types.Tool(google_search={})

def extract_grounding_chunks(response) -> list[dict]:
    """提取 Grounding Chunks（引用來源）
    
    Args:
        response: Gemini API 回應物件
        
    Returns:
        list[dict]: 引用來源列表，包含標題、URL、摘要
    """
    chunks = []
    
    # 檢查是否有 grounding metadata
    if not hasattr(response, 'candidates') or not response.candidates:
        return chunks
    
    candidate = response.candidates[0]
    if not hasattr(candidate, 'grounding_metadata'):
        return chunks
    
    metadata = candidate.grounding_metadata
    if not hasattr(metadata, 'grounding_chunks'):
        return chunks
    
    # 提取每個 chunk 的資訊
    for chunk in metadata.grounding_chunks:
        chunk_info = {
            'title': getattr(chunk.web, 'title', 'Unknown'),
            'url': getattr(chunk.web, 'uri', ''),
            'snippet': ''  # Google Search 通常不提供摘要
        }
        chunks.append(chunk_info)
    
    return chunks

def format_citations(chunks: list[dict]) -> str:
    """格式化引用來源為 Markdown
    
    Args:
        chunks: 引用來源列表
        
    Returns:
        str: Markdown 格式的引用來源
    """
    if not chunks:
        return ""
    
    citations = ["\n\n📚 **參考來源**:\n"]
    for i, chunk in enumerate(chunks, 1):
        citations.append(f"{i}. [{chunk['title']}]({chunk['url']})")
    
    return "\n".join(citations)
```

#### 1.2 整合到對話 Agent

**backend/agents/tool_aware_agent.py**:

```python
"""具有工具整合的對話 Agent"""
from google import genai
from google.genai import types
from backend.tools.google_search import create_google_search_tool, extract_grounding_chunks
from backend.config.mode_config import ModeConfig
import logging

logger = logging.getLogger(__name__)

def create_tool_aware_agent(
    client: genai.Client,
    thinking_mode: bool = False,
    enable_google_search: bool = True
) -> types.GenerateContentConfig:
    """建立具有工具能力的 Agent
    
    Args:
        client: Gemini Client
        thinking_mode: 是否啟用思考模式
        enable_google_search: 是否啟用 Google Search
        
    Returns:
        types.GenerateContentConfig: Agent 配置
    """
    # 基礎配置
    mode_config = ModeConfig.get_thinking_config() if thinking_mode else ModeConfig.get_standard_config()
    
    # 添加工具
    tools = []
    if enable_google_search:
        tools.append(create_google_search_tool())
    
    config = types.GenerateContentConfig(
        temperature=mode_config['temperature'],
        top_p=mode_config['top_p'],
        top_k=mode_config.get('top_k'),
        thinking_config=mode_config.get('thinking_config'),
        tools=tools if tools else None,
        system_instruction="""你是 NotChatGPT，一個智慧對話助理。

當需要即時資訊時，使用 Google Search 工具查詢。
回答時請：
1. 提供準確、有幫助的資訊
2. 引用來源時標註出處
3. 保持回答簡潔清晰
"""
    )
    
    return config

def generate_with_tools(
    client: genai.Client,
    message: str,
    thinking_mode: bool = False,
    enable_google_search: bool = True,
    conversation_history: list = None
) -> dict:
    """使用工具生成回應
    
    Returns:
        dict: {
            'text': str,  # 回應內容
            'citations': list[dict],  # 引用來源
            'tool_used': bool  # 是否使用了工具
        }
    """
    config = create_tool_aware_agent(client, thinking_mode, enable_google_search)
    
    # 準備訊息
    messages = conversation_history or []
    messages.append(types.Content(role='user', parts=[types.Part(text=message)]))
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=messages,
            config=config
        )
        
        # 提取引用來源
        citations = extract_grounding_chunks(response)
        
        # 檢查是否使用了工具
        tool_used = len(citations) > 0
        
        return {
            'text': response.text,
            'citations': citations,
            'tool_used': tool_used
        }
        
    except Exception as e:
        logger.error(f"生成回應失敗: {e}")
        raise
```

#### 1.3 測試 Google Search 功能

**tests/unit/backend/test_google_search.py**:

```python
import pytest
from google import genai
from dotenv import load_dotenv
import os
from backend.tools.google_search import create_google_search_tool, extract_grounding_chunks, format_citations
from backend.agents.tool_aware_agent import create_tool_aware_agent, generate_with_tools

class TestGoogleSearchTool:
    """測試 Google Search Tool"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """設定測試環境"""
        load_dotenv()
        self.client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        yield
        self.client = None
    
    def test_create_google_search_tool(self):
        """測試建立 Google Search Tool"""
        tool = create_google_search_tool()
        assert tool is not None
        print("✅ Google Search Tool 建立成功")
    
    def test_google_search_query(self):
        """測試 Google Search 查詢（需要即時資訊的問題）"""
        result = generate_with_tools(
            self.client,
            "今天台北的天氣如何？",
            enable_google_search=True
        )
        
        assert result['text'], "回應不應為空"
        assert result['tool_used'], "應該使用了 Google Search"
        print(f"✅ 回應: {result['text'][:100]}...")
        
        if result['citations']:
            print(f"📚 找到 {len(result['citations'])} 個引用來源")
            for i, cite in enumerate(result['citations'][:3], 1):
                print(f"  {i}. {cite['title']}: {cite['url']}")
    
    def test_no_search_for_general_question(self):
        """測試一般問題不應觸發搜尋"""
        result = generate_with_tools(
            self.client,
            "什麼是 Python？",
            enable_google_search=True
        )
        
        assert result['text'], "回應不應為空"
        print(f"✅ 回應: {result['text'][:100]}...")
        print(f"🔧 工具使用: {result['tool_used']}")
    
    def test_format_citations(self):
        """測試引用來源格式化"""
        chunks = [
            {'title': 'Example 1', 'url': 'https://example.com/1', 'snippet': ''},
            {'title': 'Example 2', 'url': 'https://example.com/2', 'snippet': ''}
        ]
        
        formatted = format_citations(chunks)
        assert '📚 **參考來源**' in formatted
        assert '[Example 1](https://example.com/1)' in formatted
        print("✅ 引用來源格式化測試通過")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**執行測試**:

```bash
# 執行 Google Search 測試
python -m pytest tests/unit/backend/test_google_search.py -v

# 執行單一測試
python -m pytest tests/unit/backend/test_google_search.py::TestGoogleSearchTool::test_google_search_query -v
```

**參考**: Day 7 (grounding-agent) - Google Search Grounding

---

### 步驟 2: Code Execution Tool

#### 2.1 建立 Code Executor

**backend/tools/code_executor.py**:

```python
"""Code Execution Tool

提供程式碼執行功能，支援 Python 程式碼安全執行。
"""
from google import genai
from google.genai import types
import logging

logger = logging.getLogger(__name__)

def create_code_execution_tool() -> types.Tool:
    """建立 Code Execution Tool
    
    Returns:
        types.Tool: Code Execution Tool 配置
    """
    return types.Tool(code_execution={})

def format_code_result(response) -> dict:
    """格式化程式碼執行結果
    
    Args:
        response: Gemini API 回應物件
        
    Returns:
        dict: {
            'has_code': bool,  # 是否包含程式碼執行
            'code_blocks': list[str],  # 程式碼區塊
            'outputs': list[str]  # 執行結果
        }
    """
    result = {
        'has_code': False,
        'code_blocks': [],
        'outputs': []
    }
    
    if not hasattr(response, 'candidates') or not response.candidates:
        return result
    
    candidate = response.candidates[0]
    if not hasattr(candidate, 'content') or not candidate.content:
        return result
    
    # 遍歷所有 parts，尋找 executable_code 和 code_execution_result
    for part in candidate.content.parts:
        if hasattr(part, 'executable_code'):
            result['has_code'] = True
            result['code_blocks'].append(part.executable_code.code)
        
        if hasattr(part, 'code_execution_result'):
            result['outputs'].append(part.code_execution_result.output)
    
    return result
```

#### 2.2 整合 Code Execution

**更新 backend/agents/tool_aware_agent.py**:

```python
# 在檔案開頭添加
from backend.tools.code_executor import create_code_execution_tool, format_code_result

# 修改 create_tool_aware_agent 函式
def create_tool_aware_agent(
    client: genai.Client,
    thinking_mode: bool = False,
    enable_google_search: bool = True,
    enable_code_execution: bool = True  # 新增參數
) -> types.GenerateContentConfig:
    """建立具有工具能力的 Agent"""
    # ... 前面的程式碼 ...
    
    # 添加工具
    tools = []
    if enable_google_search:
        tools.append(create_google_search_tool())
    if enable_code_execution:
        tools.append(create_code_execution_tool())
    
    # ... 後面的程式碼 ...
```

#### 2.3 測試 Code Execution

**tests/unit/backend/test_code_execution.py**:

```python
import pytest
from google import genai
from dotenv import load_dotenv
import os
from backend.tools.code_executor import create_code_execution_tool, format_code_result
from backend.agents.tool_aware_agent import generate_with_tools

class TestCodeExecutionTool:
    """測試 Code Execution Tool"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        load_dotenv()
        self.client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        yield
        self.client = None
    
    def test_create_code_execution_tool(self):
        """測試建立 Code Execution Tool"""
        tool = create_code_execution_tool()
        assert tool is not None
        print("✅ Code Execution Tool 建立成功")
    
    def test_simple_calculation(self):
        """測試簡單數學計算"""
        response = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents="計算 123 * 456 的結果",
            config={'tools': [create_code_execution_tool()]}
        )
        
        result = format_code_result(response)
        assert result['has_code'], "應該執行了程式碼"
        print(f"✅ 程式碼: {result['code_blocks'][0] if result['code_blocks'] else 'N/A'}")
        print(f"✅ 結果: {result['outputs'][0] if result['outputs'] else 'N/A'}")
    
    def test_data_analysis(self):
        """測試資料分析任務"""
        response = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents="計算 [1, 2, 3, 4, 5] 的平均值和標準差",
            config={'tools': [create_code_execution_tool()]}
        )
        
        result = format_code_result(response)
        if result['has_code']:
            print(f"✅ 執行的程式碼:\n{result['code_blocks'][0]}")
            print(f"✅ 執行結果:\n{result['outputs'][0]}")
        else:
            print("ℹ️ Agent 選擇直接回答而非執行程式碼")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**執行測試**:

```bash
python -m pytest tests/unit/backend/test_code_execution.py -v
```

**參考**: Day 21 (code-calculator) - Code Execution

---

### 步驟 3: 多工具協同測試

#### 3.1 整合測試

**tests/integration/test_multi_tool.py**:

```python
"""測試多工具協同使用"""
import pytest
from google import genai
from dotenv import load_dotenv
import os
from backend.agents.tool_aware_agent import generate_with_tools

class TestMultiToolIntegration:
    """測試多工具整合"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        load_dotenv()
        self.client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        yield
        self.client = None
    
    def test_search_and_calculate(self):
        """測試搜尋 + 計算（例如：查詢股價並計算報酬率）"""
        result = generate_with_tools(
            self.client,
            "如果我在 2024 年初買入台積電股票 100 股，現在值多少錢？",
            enable_google_search=True,
            enable_code_execution=True
        )
        
        print(f"✅ 回應: {result['text']}")
        if result['citations']:
            print(f"📚 引用來源: {len(result['citations'])} 個")
    
    def test_tool_selection_accuracy(self):
        """測試工具選擇準確率"""
        test_cases = [
            ("今天天氣如何？", "google_search"),
            ("計算 100 的平方根", "code_execution"),
            ("什麼是 Python？", "none"),  # 不應使用工具
        ]
        
        results = []
        for question, expected_tool in test_cases:
            result = generate_with_tools(
                self.client,
                question,
                enable_google_search=True,
                enable_code_execution=True
            )
            
            actual_tool = "none"
            if result.get('tool_used'):
                if result.get('citations'):
                    actual_tool = "google_search"
                else:
                    actual_tool = "code_execution"
            
            is_correct = actual_tool == expected_tool
            results.append(is_correct)
            
            print(f"{'✅' if is_correct else '❌'} {question}")
            print(f"   預期: {expected_tool}, 實際: {actual_tool}")
        
        accuracy = sum(results) / len(results) * 100
        print(f"\n🎯 工具選擇準確率: {accuracy:.1f}%")
        
        # 要求準確率 > 66% (3個測試至少對2個)
        assert accuracy >= 66, f"準確率過低: {accuracy:.1f}%"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**執行整合測試**:

```bash
python -m pytest tests/integration/test_multi_tool.py -v
```

---

## Week 4: Web UI 建構

### 步驟 4: React + Vite 專案設定

#### 4.1 建立 Frontend 專案

```bash
# 在專案根目錄執行
cd /path/to/not-chat-gpt

# 使用 Vite 建立 React TypeScript 專案
npm create vite@latest frontend -- --template react-ts

# 進入 frontend 目錄
cd frontend

# 安裝基礎依賴
npm install

# 安裝額外套件
npm install --save \
  @ag-ui/core \
  react-markdown \
  remark-gfm \
  rehype-highlight \
  axios \
  zustand

# 安裝開發依賴
npm install --save-dev \
  @types/react-markdown \
  tailwindcss \
  postcss \
  autoprefixer
```

#### 4.2 設定 Tailwind CSS

```bash
# 初始化 Tailwind
npx tailwindcss init -p
```

**frontend/tailwind.config.js**:

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**frontend/src/index.css**:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 自訂樣式 */
.message-markdown {
  @apply prose prose-sm max-w-none;
}

.message-markdown pre {
  @apply bg-gray-800 text-gray-100 rounded-lg p-4 overflow-x-auto;
}

.message-markdown code {
  @apply bg-gray-100 text-red-600 px-1 rounded;
}
```

#### 4.3 設定 Vite Proxy（串接後端 API）

**frontend/vite.config.ts**:

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

#### 4.4 測試環境設定

```bash
# 啟動開發伺服器
npm run dev

# 預期輸出
# VITE v5.x.x  ready in xxx ms
# ➜  Local:   http://localhost:3000/
```

**參考**: Day 24 (shopping-assistant-ui) - Frontend Setup

---

### 步驟 5: 基礎 UI 架構

#### 5.1 建立 API 服務層

**frontend/src/services/api.ts**:

```typescript
/**
 * API 服務層
 * 負責與後端 API 通訊
 */

export interface ChatMessage {
  role: 'user' | 'model';
  content: string;
  timestamp: Date;
  citations?: Citation[];
}

export interface Citation {
  title: string;
  url: string;
  snippet?: string;
}

export interface ChatRequest {
  message: string;
  thinking_mode: boolean;
  session_id?: string;
}

export interface ChatResponse {
  text: string;
  citations?: Citation[];
  tool_used?: boolean;
}

/**
 * 發送聊天訊息（SSE 串流）
 */
export async function* streamChat(request: ChatRequest): AsyncGenerator<string> {
  const response = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error('Response body is null');
  }

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') {
          return;
        }
        yield data;
      }
    }
  }
}

/**
 * 取得對話列表
 */
export async function getConversations(): Promise<any[]> {
  const response = await fetch('/api/conversations');
  if (!response.ok) {
    throw new Error('Failed to fetch conversations');
  }
  return response.json();
}

/**
 * 建立新對話
 */
export async function createConversation(name: string): Promise<string> {
  const response = await fetch('/api/conversations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  });
  if (!response.ok) {
    throw new Error('Failed to create conversation');
  }
  const data = await response.json();
  return data.session_id;
}

/**
 * 上傳文檔
 */
export async function uploadDocument(file: File): Promise<string> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/api/documents/upload', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Failed to upload document');
  }

  const data = await response.json();
  return data.file_id;
}

/**
 * 取得文檔列表
 */
export async function getDocuments(): Promise<any[]> {
  const response = await fetch('/api/documents');
  if (!response.ok) {
    throw new Error('Failed to fetch documents');
  }
  return response.json();
}

/**
 * 刪除文檔
 */
export async function deleteDocument(fileId: string): Promise<void> {
  const response = await fetch(`/api/documents/${fileId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete document');
  }
}
```

#### 5.2 建立狀態管理（Zustand）

**frontend/src/store/chatStore.ts**:

```typescript
/**
 * Chat 狀態管理
 * 使用 Zustand 管理全域狀態
 */
import { create } from 'zustand';
import type { ChatMessage } from '../services/api';

interface ChatState {
  // 狀態
  messages: ChatMessage[];
  currentSessionId: string | null;
  thinkingMode: boolean;
  isStreaming: boolean;
  
  // Actions
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
  setSessionId: (id: string) => void;
  toggleThinkingMode: () => void;
  setStreaming: (streaming: boolean) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  // 初始狀態
  messages: [],
  currentSessionId: null,
  thinkingMode: false,
  isStreaming: false,
  
  // Actions
  addMessage: (message) => 
    set((state) => ({ messages: [...state.messages, message] })),
  
  clearMessages: () => 
    set({ messages: [] }),
  
  setSessionId: (id) => 
    set({ currentSessionId: id }),
  
  toggleThinkingMode: () => 
    set((state) => ({ thinkingMode: !state.thinkingMode })),
  
  setStreaming: (streaming) => 
    set({ isStreaming: streaming }),
}));
```

#### 5.3 建立主要元件

**frontend/src/components/ConversationView.tsx**:

```typescript
/**
 * 主要對話介面
 */
import React, { useState } from 'react';
import { useChatStore } from '../store/chatStore';
import { streamChat } from '../services/api';
import MessageList from './MessageList';
import InputBox from './InputBox';
import ModeSelector from './ModeSelector';

export default function ConversationView() {
  const { messages, addMessage, thinkingMode, currentSessionId, setStreaming } = useChatStore();
  const [currentResponse, setCurrentResponse] = useState('');

  const handleSendMessage = async (text: string) => {
    // 添加使用者訊息
    addMessage({
      role: 'user',
      content: text,
      timestamp: new Date(),
    });

    // 開始串流
    setStreaming(true);
    setCurrentResponse('');

    try {
      for await (const chunk of streamChat({
        message: text,
        thinking_mode: thinkingMode,
        session_id: currentSessionId || undefined,
      })) {
        setCurrentResponse((prev) => prev + chunk);
      }

      // 串流結束，添加完整回應
      addMessage({
        role: 'model',
        content: currentResponse,
        timestamp: new Date(),
      });
      setCurrentResponse('');
    } catch (error) {
      console.error('Error streaming chat:', error);
    } finally {
      setStreaming(false);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      {/* 頂部工具列 */}
      <div className="flex items-center justify-between p-4 border-b">
        <h1 className="text-xl font-bold">NotChatGPT</h1>
        <ModeSelector />
      </div>

      {/* 訊息列表 */}
      <div className="flex-1 overflow-y-auto">
        <MessageList messages={messages} currentResponse={currentResponse} />
      </div>

      {/* 輸入框 */}
      <div className="border-t">
        <InputBox onSend={handleSendMessage} />
      </div>
    </div>
  );
}
```

**frontend/src/components/MessageList.tsx**:

```typescript
/**
 * 訊息列表元件
 */
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import type { ChatMessage } from '../services/api';

interface Props {
  messages: ChatMessage[];
  currentResponse?: string;
}

export default function MessageList({ messages, currentResponse }: Props) {
  return (
    <div className="max-w-3xl mx-auto p-4 space-y-4">
      {messages.map((msg, idx) => (
        <div
          key={idx}
          className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-2xl p-4 rounded-lg ${
              msg.role === 'user'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-900'
            }`}
          >
            <ReactMarkdown
              className="message-markdown"
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
            >
              {msg.content}
            </ReactMarkdown>
            
            {/* 引用來源 */}
            {msg.citations && msg.citations.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-300">
                <p className="text-sm font-semibold mb-1">📚 參考來源:</p>
                {msg.citations.map((cite, i) => (
                  <a
                    key={i}
                    href={cite.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-sm text-blue-600 hover:underline"
                  >
                    {i + 1}. {cite.title}
                  </a>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}

      {/* 串流中的回應 */}
      {currentResponse && (
        <div className="flex justify-start">
          <div className="max-w-2xl p-4 rounded-lg bg-gray-100 text-gray-900">
            <ReactMarkdown
              className="message-markdown"
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
            >
              {currentResponse}
            </ReactMarkdown>
            <span className="inline-block w-2 h-4 bg-gray-900 animate-pulse ml-1"></span>
          </div>
        </div>
      )}
    </div>
  );
}
```

**frontend/src/components/InputBox.tsx**:

```typescript
/**
 * 輸入框元件
 */
import React, { useState } from 'react';
import { useChatStore } from '../store/chatStore';

interface Props {
  onSend: (text: string) => void;
}

export default function InputBox({ onSend }: Props) {
  const [input, setInput] = useState('');
  const { isStreaming } = useChatStore();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    
    onSend(input);
    setInput('');
  };

  return (
    <form onSubmit={handleSubmit} className="p-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="輸入訊息..."
          disabled={isStreaming}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          disabled={isStreaming || !input.trim()}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          {isStreaming ? '傳送中...' : '送出'}
        </button>
      </div>
    </form>
  );
}
```

**frontend/src/components/ModeSelector.tsx**:

```typescript
/**
 * 思考模式切換元件
 */
import React from 'react';
import { useChatStore } from '../store/chatStore';

export default function ModeSelector() {
  const { thinkingMode, toggleThinkingMode } = useChatStore();

  return (
    <button
      onClick={toggleThinkingMode}
      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
        thinkingMode
          ? 'bg-purple-500 text-white'
          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
      }`}
    >
      {thinkingMode ? '💭 思考模式' : '💬 標準模式'}
    </button>
  );
}
```

#### 5.4 更新主程式

**frontend/src/App.tsx**:

```typescript
import ConversationView from './components/ConversationView';

function App() {
  return <ConversationView />;
}

export default App;
```

#### 5.5 測試前端

```bash
# 啟動後端（終端 1）
cd backend
python -m backend.main

# 啟動前端（終端 2）
cd frontend
npm run dev

# 開啟瀏覽器
# http://localhost:3000
```

**功能測試清單**:

- [ ] 可以輸入並送出訊息
- [ ] 訊息以串流方式顯示
- [ ] 可以切換思考模式
- [ ] Markdown 正確渲染
- [ ] 程式碼區塊有語法高亮

---

### 步驟 6: 對話管理與文檔管理

#### 6.1 更新後端 API

**backend/api/routes.py** (完整版):

```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
from google import genai
import os
from dotenv import load_dotenv

from backend.agents.streaming_agent import stream_response
from backend.services.session_service import SessionService
from backend.services.document_service import DocumentService

load_dotenv()

app = FastAPI(title="NotChatGPT API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 服務初始化
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
session_service = SessionService()
document_service = DocumentService(client)

class ChatRequest(BaseModel):
    message: str
    thinking_mode: bool = False
    session_id: Optional[str] = None

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """SSE 串流端點"""
    async def generate():
        async for chunk in stream_response(
            message=request.message,
            thinking_mode=request.thinking_mode,
            enable_safety=True
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

@app.get("/api/conversations")
async def get_conversations():
    """取得對話列表"""
    conversations = session_service.list_sessions()
    return conversations

@app.post("/api/conversations")
async def create_conversation(name: str = "New Chat"):
    """建立新對話"""
    session_id = session_service.create_session(name)
    return {"session_id": session_id}

@app.delete("/api/conversations/{session_id}")
async def delete_conversation(session_id: str):
    """刪除對話"""
    # 實作刪除邏輯
    return {"message": "Conversation deleted"}

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """上傳文檔"""
    try:
        file_id = await document_service.upload_file(file)
        return {"file_id": file_id, "name": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents")
async def get_documents():
    """取得文檔列表"""
    documents = await document_service.list_files()
    return documents

@app.delete("/api/documents/{file_id}")
async def delete_document(file_id: str):
    """刪除文檔"""
    try:
        await document_service.delete_file(file_id)
        return {"message": "Document deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "NotChatGPT API is running"}
```

#### 6.2 建立對話管理 UI

**frontend/src/components/ConversationList.tsx**:

```typescript
/**
 * 對話列表側邊欄
 */
import React, { useEffect, useState } from 'react';
import { getConversations, createConversation } from '../services/api';

interface Conversation {
  id: string;
  name: string;
  updated_at: string;
}

export default function ConversationList() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const data = await getConversations();
      setConversations(data);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewConversation = async () => {
    try {
      await createConversation('New Chat');
      loadConversations();
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  return (
    <div className="w-64 bg-gray-50 border-r h-screen p-4">
      <button
        onClick={handleNewConversation}
        className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 mb-4"
      >
        + 新對話
      </button>

      <div className="space-y-2">
        {loading ? (
          <p className="text-gray-500 text-sm">載入中...</p>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className="p-3 bg-white rounded-lg hover:bg-gray-100 cursor-pointer"
            >
              <p className="font-medium truncate">{conv.name}</p>
              <p className="text-xs text-gray-500">{new Date(conv.updated_at).toLocaleDateString()}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
```

#### 6.3 建立文檔管理 UI

**frontend/src/components/DocumentPanel.tsx**:

```typescript
/**
 * 文檔管理面板
 */
import React, { useEffect, useState } from 'react';
import { getDocuments, uploadDocument, deleteDocument } from '../services/api';

interface Document {
  id: string;
  name: string;
  size: number;
  uploaded_at: string;
}

export default function DocumentPanel() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const data = await getDocuments();
      setDocuments(data);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await uploadDocument(file);
      loadDocuments();
    } catch (error) {
      console.error('Failed to upload document:', error);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('確定要刪除此文檔？')) return;

    try {
      await deleteDocument(id);
      loadDocuments();
    } catch (error) {
      console.error('Failed to delete document:', error);
    }
  };

  return (
    <div className="w-80 bg-gray-50 border-l h-screen p-4">
      <h2 className="text-lg font-bold mb-4">📚 文檔管理</h2>

      {/* 上傳按鈕 */}
      <label className="block w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-center cursor-pointer mb-4">
        {uploading ? '上傳中...' : '+ 上傳文檔'}
        <input
          type="file"
          onChange={handleUpload}
          disabled={uploading}
          className="hidden"
          accept=".pdf,.doc,.docx,.txt,.md"
        />
      </label>

      {/* 文檔列表 */}
      <div className="space-y-2">
        {documents.map((doc) => (
          <div key={doc.id} className="p-3 bg-white rounded-lg">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <p className="font-medium truncate">{doc.name}</p>
                <p className="text-xs text-gray-500">
                  {(doc.size / 1024).toFixed(1)} KB
                </p>
              </div>
              <button
                onClick={() => handleDelete(doc.id)}
                className="text-red-500 hover:text-red-700 text-sm"
              >
                刪除
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

#### 6.4 整合到主介面

**frontend/src/App.tsx** (更新):

```typescript
import ConversationList from './components/ConversationList';
import ConversationView from './components/ConversationView';
import DocumentPanel from './components/DocumentPanel';

function App() {
  return (
    <div className="flex h-screen">
      <ConversationList />
      <ConversationView />
      <DocumentPanel />
    </div>
  );
}

export default App;
```

---

## Phase 2 檢查點

### 功能完成度

- [ ] Google Search Tool 整合完成
- [ ] Code Execution Tool 整合完成
- [ ] 多工具協同測試通過
- [ ] React + Vite 專案建立完成
- [ ] 基礎 UI 元件實作完成
- [ ] SSE 串流顯示正常
- [ ] 思考模式切換功能正常
- [ ] 對話管理功能完成
- [ ] 文檔管理功能完成
- [ ] 前後端整合測試通過

### 品質指標

- [ ] 工具選擇準確率 > 85%
- [ ] 串流回應順暢度 > 95%
- [ ] UI 響應時間 < 100ms
- [ ] API 回應時間 < 3s（不含 LLM）
- [ ] 前端測試覆蓋率 > 60%
- [ ] 後端測試覆蓋率 > 70%

### 使用者體驗

- [ ] UI/UX 直觀易用
- [ ] 錯誤處理完善
- [ ] 載入狀態清晰
- [ ] 響應式設計良好
- [ ] 無明顯效能問題

---

## 下一步：Phase 3

Phase 2 完成後，即可進入 Phase 3：

- 進階評估與監控（AgentEvaluator 整合）
- 多租戶與權限管理
- 進階 RAG 功能（Hybrid Search, Reranking）
- 企業整合（SSO, API Key Management）
- 生產環境部署（Docker, Kubernetes）
