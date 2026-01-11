# 快取分析研究助理

本範例展示了 ADK 上下文快取功能，並以一個全面性的研究助理代理人來測試 Gemini 2.0 Flash 與 2.5 Flash 的上下文快取能力。此範例展示了 ADK 明確快取（explicit caching）與 Google 內建隱式快取（implicit caching）之間的差異。

## 主要特色

- **應用程式層級快取設定**：於應用程式層級設定上下文快取
- **大型上下文指令**：系統指令超過 4200 個 token，以觸發上下文快取門檻
- **完整工具組**：內建 7 種專業研究與分析工具
- **多模型支援**：相容於所有 Gemini 模型，自動調整實驗類型
- **效能指標**：詳細追蹤 token 使用情形，包括 `cached_content_token_count`

## 快取設定

```python
ContextCacheConfig(
     min_tokens=4096,
        ttl_seconds=600,  # 研究會話快取 10 分鐘
        cache_intervals=3,  # 最多呼叫 3 次後快取失效
```

## 使用方式

### 執行快取實驗

`run_cache_experiments.py` 腳本可比較不同模型間的快取效能：

```bash
# 測試任一 Gemini 模型，腳本會自動判斷實驗類型
python run_cache_experiments.py <model_name> --output results.json

# 範例：
python run_cache_experiments.py gemini-2.0-flash-001 --output gemini_2_0_results.json
python run_cache_experiments.py gemini-2.5-flash --output gemini_2_5_results.json
python run_cache_experiments.py gemini-1.5-flash --output gemini_1_5_results.json

# 執行多次以取得平均結果
python run_cache_experiments.py <model_name> --repeat 3 --output averaged_results.json
```

### 直接使用代理人

```bash
# 直接執行代理人
adk run /cache_analysis/agent.py

# 使用網頁介面進行除錯
adk /cache_analysis
```

## 實驗類型

腳本會根據模型名稱自動決定實驗類型：

### 含有 "2.5" 的模型（如 gemini-2.5-flash）
- **明確快取**：同時啟用 ADK 明確快取與 Google 內建隱式快取
- **僅隱式快取**：僅使用 Google 內建隱式快取
- **評估項目**：比較明確快取對於內建隱式快取的額外效益

### 其他模型（如 gemini-2.0-flash-001, gemini-1.5-flash）
- **有快取**：啟用 ADK 明確上下文快取
- **無快取**：不啟用快取（作為基準比較）
- **評估項目**：比較有無快取下的效能提升

## 內建工具

1. **analyze_data_patterns** - 資料集的統計分析與模式辨識
2. **research_literature** - 學術與專業文獻研究並附引用
3. **generate_test_scenarios** - 全面性測試案例產生與驗證策略
4. **benchmark_performance** - 系統效能測量與瓶頸分析
5. **optimize_system_performance** - 效能最佳化建議與策略
6. **analyze_security_vulnerabilities** - 資安風險評估與弱點分析
7. **design_scalability_architecture** - 可擴展系統架構設計與規劃

## 預期結果

### 效能與成本權衡

**注意**：本範例使用工具密集型代理人，效能表現可能與純文字型代理人不同。

### 效能提升
- **純文字代理人**：啟用快取後通常可降低 30-70% 延遲
- **工具密集型代理人**：因快取建立有額外負擔，延遲可能較高，但仍有成本優勢
- **Gemini 2.5 Flash**：可比較 ADK 明確快取與 Google 內建隱式快取

### 成本節省
- **輸入 Token 成本**：快取內容僅需原本 25% 成本（節省 75%）
- **一般節省**：多輪對話下可節省 30-60% 輸入成本
- **工具密集型工作負載**：成本節省通常大於延遲增加的影響

### Token 指標
- **快取內容 Token 數**：非零值代表快取命中
- **快取命中率**：快取提供的 token 比例與新計算的比例

## 疑難排解

### 快取 Token 為零
若 `cached_content_token_count` 一直為 0：
- 確認模型名稱完全正確（如 `gemini-2.0-flash-001`）
- 檢查快取設定的 `min_tokens` 門檻是否達到
- 確認已使用正確的應用程式層級設定

### Session 錯誤
若出現 "Session not found" 錯誤：
- 確認建立 session 時有使用 `runner.app_name`
- 檢查 InMemoryRunner 初始化時 App 與 Agent 物件的使用方式

## 技術實作

本範例展示：
- **現代應用架構**：依循 ADK 最佳實踐，於應用程式層級設定快取
- **整合測試**：全面驗證快取功能
- **效能分析**：詳細收集指標並比較效能
- **錯誤處理**：健全的 session 管理與快取失效處理

## 相關文件

本範例主要搭配 `[adk-docs] context` [caching](../../../adk-docs/context/caching.md) 文件使用，展示如何在 ADK 中設定與測試內容快取功能，並分析其效能與成本效益。 如需更多資訊，請參閱該文件。