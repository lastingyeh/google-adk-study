[<< 上一篇：SRE Copilot Agent 設計](./10_sre-copilot-agent.md) | [返回目錄](./README.md)
***

## 1️⃣ 架構全圖

```mermaid
flowchart LR
    %% ========= 上層：業務系統與使用者 =========
    subgraph CHANNELS[業務系統 / 使用者]
        APP[業務系統 / 服務]
        USER[使用者 / 客戶]
        SRE[SRE / On-call 工程師]
    end

    USER --> APP

    %% ========= Observability 層 =========
    subgraph OBS[Observability 層]
        direction TB
        MET["Metrics\n(Prometheus)"]
        LOG["Logs\n(Loki / ELK)"]
        TRC["Tracing\n(Jaeger / OpenTelemetry)"]
        ALT[Alertmanager]

        APP --> MET
        APP --> LOG
        APP --> TRC
        MET --> ALT
    end

    %% ========= Kafka / Streaming 層 =========
    subgraph KAFKA[Kafka / Streaming 層]
        direction TB
        EXP[Exporter / Bridge]
        KFK[(Kafka Cluster)]
        STR["Streaming Jobs\n(Kafka Streams / Flink)"]

        MET --> EXP
        LOG --> EXP
        ALT --> EXP

        EXP --> KFK
        KFK --> STR
        STR --> KFK
    end

    %% ========= ADK Agent / A2A 層 =========
    subgraph ADK_LAYER[ADK Agent Mesh 層]
        direction TB

        subgraph ADK_RT[Google ADK Agent Runtime]
            direction LR
            M[Monitoring Agent]
            T[Incident Triage Agent]
            R[Runbook / Knowledge Agent]
            E[Execution Agent]
            C[SRE Copilot Agent]
        end

        A2A["A2A Protocol\n(Agent-to-Agent)"]
    end

    %% ADK 與 Kafka / Observability 的關係
    KFK --> M
    M --> T

    %% Triage 直接透過 MCP 查 Observability
    subgraph MCP_OBS["MCP Tools\n(Observability Adapter)"]
        direction TB
        M_MET[metrics_query_tool]
        M_LOG[log_query_tool]
        M_TRC[trace_query_tool]
    end

    T --> M_MET
    T --> M_LOG
    T --> M_TRC

    %% A2A Mesh 連線
    M --> A2A
    T --> A2A
    R --> A2A
    E --> A2A
    C --> A2A

    %% Triage 與其他 Agent 協作
    T --> R
    T --> E
    T --> C

    %% ========= 人機互動 / 通報層 =========
    subgraph COLLAB[協作 / 通報]
        direction TB
        CHAT["ChatOps\n(Slack / Teams)"]
        PAGE["On-call\n(PagerDuty / Opsgenie)"]
    end

    C --> CHAT
    C --> PAGE
    SRE --> CHAT
```

## 重點說明

1. **左上**是既有的業務系統與使用者（APP、USER），
   下方是既有的 **Observability 堆疊**（Prometheus、Loki、Jaeger、Alertmanager）。

2. Observability 資料經過 **Exporter / Bridge** 匯入 **Kafka**，
   由 **Streaming Job（Kafka Streams / Flink）** 進行降噪與聚合，
   形成比較乾淨的「事件流」。

3. **Google ADK Agent Mesh 層**：

   * 多個 Agent（Monitoring / Triage / Runbook / Execution / SRE Copilot）
   * 都跑在 ADK Runtime 上。
   * 彼此透過 **A2A Protocol** 來做 **Agent-to-Agent 任務協作**。

4. **Monitoring Agent** 從 Kafka 訂閱事件，做第一層判斷後交給 **Incident Triage Agent**。

5. **Incident Triage Agent** 是決策中樞：

   * 一方面透過 MCP Tools 直接查 **Observability**（metrics/logs/traces），
   * 一方面透過 A2A 找 **Runbook Agent** 要知識、
   * 再透過 A2A 呼叫 **Execution Agent** 做自動修復，
   * 同時把結果與建議送到 **SRE Copilot Agent**。

6. **SRE Copilot Agent** 最後透過 **ChatOps / On-call 系統** 把事件摘要與決策建議呈現給 **SRE 值班工程師**，形成完整的人機協作閉環。
