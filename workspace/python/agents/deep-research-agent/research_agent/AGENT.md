## 深度研究代理 (Deep Research Agent) 實作

### 本模組提供 Google 深度研究代理 (Deep Research Agent) 的高階介面，
該代理能自主規劃、執行並整合多步驟的研究任務。

深度研究代理 (Deep Research Agent) 的工作流程：
- 規劃研究策略
- 在網路上搜尋資訊
- 閱讀並分析來源
- 迭代以填補知識缺口
- 產出包含引用的綜合報告

### 工作流程圖：
```mermaid
    graph TD
        Start[開始研究任務] --> Plan[規劃研究策略]
        Plan --> Search[搜尋網路資訊]
        Search --> Analyze[閱讀並分析來源]
        Analyze --> Check{是否有知識缺口?}
        Check -- 是 --> Iterate[迭代填補缺口]
        Iterate --> Search
        Check -- 否 --> Report[產出綜合報告]
        Report --> End[結束]
```

## Streaming

### 深度研究代理 (Deep Research Agent) 串流工具

本模組提供即時串流功能，用於研究任務期間的進度更新。

串流與重連流程：
```mermaid
graph TD
    Start[開始串流] --> Stream[接收事件]
    Stream --> Success{是否完成?}
    Success -- 是 --> End[結束]
    Success -- 否 --> Error{發生錯誤?}
    Error -- 是 --> RetryCheck{重試次數 < 最大值?}
    RetryCheck -- 是 --> Wait[等待延遲]
    Wait --> Resume[使用 Last-Event-ID 恢復串流]
    Resume --> Stream
    RetryCheck -- 否 --> Fail[報告錯誤並結束]
```