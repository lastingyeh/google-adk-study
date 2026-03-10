# 代理的可觀察性

> 🔔 `更新日期：2026-03-09`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/observability/

代理的可觀察性（Observability）透過分析系統的外部遙測資料和結構化日誌，實現對系統內部狀態的測量，包括推理追蹤（reasoning traces）、工具調用（tool calls）以及潛在的模型輸出。在構建代理時，您可能需要這些功能來協助偵錯並診斷其執行中的行為。對於具有任何顯著複雜程度的代理而言，基本的輸入和輸出監控通常是不夠的。

代理開發套件 (ADK) 提供可配置的 [記錄 (logging)](observability/logging.md) 功能，用於監控和偵錯代理。然而，您可能需要考慮更進階的 [可觀察性 ADK 整合 (observability ADK Integrations)](../tools-and-integrations/index.md#可觀測性) 來進行監控和分析。

用於可觀察性的 ADK 整合

有關 ADK 的預建可觀察性函式庫列表，請參閱 [工具與整合 (Tools and Integrations)](../tools-and-integrations/index.md#可觀測性)。
