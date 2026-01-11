# 版權所有 2025 Google LLC
#
# 根據 Apache License, Version 2.0（以下簡稱「授權」）授權；
# 除非遵守授權，否則您不得使用此檔案。
# 您可以在下列網址取得授權副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據授權分發的軟體是以「現狀」提供，
# 不附帶任何明示或暗示的擔保或條件。
# 請參閱授權以瞭解授權下的特定語言及限制。

"""
快取分析研究助理代理人。

# 重點說明：
# 本代理人設計用於測試 ADK 的 context caching（上下文快取）功能，
# 並以超過 2048 tokens 的大型提示來滿足隱式與顯式快取需求。
"""

import random
import time
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.apps.app import App


# 重點說明：載入 .env 檔案中的環境變數
load_dotenv()


def analyze_data_patterns(
    data: str, analysis_type: str = "comprehensive"
) -> Dict[str, Any]:
    """
    分析資料模式並提供見解。

    # 重點說明：
    # 此工具可進行全面性的資料分析，包括統計分析、趨勢識別、異常偵測、相關性分析與預測建模。
    # 支援多種資料格式（CSV、JSON、XML 及純文字資料結構）。

    參數：
        data: 要分析的輸入資料。可為結構化（如 JSON、CSV）或非結構化文字資料。
              結構化資料需包含欄位標題並確保格式正確。若為時間序列資料，請以 ISO 格式包含時間戳。
        analysis_type: 要執行的分析類型。選項如下：
                      - "comprehensive": 完整統計與趨勢分析
                      - "statistical": 僅基本統計量
                      - "trends": 時間序列與趨勢分析
                      - "anomalies": 離群值與異常偵測
                      - "correlations": 相關性與關聯分析
                      - "predictive": 預測與預測模型

    回傳：
        包含分析結果的字典，結構如下：
        {
            "summary": "高層次發現摘要",
            "statistics": {...},  # 統計量
            "trends": {...},      # 趨勢分析結果
            "anomalies": [...],   # 偵測到的異常清單
            "correlations": {...}, # 相關矩陣與關聯
            "predictions": {...}, # 若適用則為預測結果
            "recommendations": [...] # 可行的見解與建議
        }
    """
    # Simulate analysis processing time
    time.sleep(0.1)

    return {
        "summary": f"Analyzed {len(data)} characters of {analysis_type} data",
        "statistics": {
            "data_points": len(data.split()),
            "analysis_type": analysis_type,
            "processing_time": "0.1 seconds",
        },
        "recommendations": [
            "Continue monitoring data trends",
            "Consider additional data sources for correlation analysis",
        ],
    }


def research_literature(
    topic: str,
    sources: Optional[List[str]] = None,
    depth: str = "comprehensive",
    time_range: str = "recent",
) -> Dict[str, Any]:
    """
    針對指定主題進行學術與專業文獻研究。

    # 重點說明：
    # 此工具可跨多個學術資料庫、專業期刊、會議論文與產業報告進行全面性文獻研究。
    # 能分析研究趨勢、找出關鍵作者與機構、萃取方法論並整合多來源發現。

    工具支援多種研究方法，包括系統性回顧、統合分析（meta-analysis）、書目計量分析（bibliometric analysis）、引用網絡分析。
    可辨識研究缺口、新興趨勢與未來研究方向。

    參數：
        topic: 研究主題或查詢。可為具體（如「大型語言模型的 context caching」）或廣泛（如「機器學習最佳化」）。
               建議使用明確關鍵字與片語以獲得更佳結果。支援布林運算子（AND, OR, NOT）進行複雜查詢。
        sources: 優先搜尋來源清單。選項如下：
                - "academic": 同儕審查學術期刊與論文
                - "conference": 會議論文與簡報
                - "industry": 產業報告與白皮書
                - "patents": 專利資料庫與智慧財產
                - "preprints": ArXiv、bioRxiv 及其他 preprint 伺服器
                - "books": 學術與專業書籍
        depth: 研究深度層級：
               - "comprehensive": 完整文獻回顧與詳細分析
               - "focused": 聚焦於特定面向
               - "overview": 領域高層次概覽
               - "technical": 深入技術實作細節
        time_range: 文獻搜尋時間範圍：
                   - "recent": 最近 2 年
                   - "current": 最近 5 年
                   - "historical": 所有可用時期
                   - "decade": 最近 10 年

    回傳：
        包含研究結果的字典：
        {
            "summary": "發現的執行摘要",
            "key_papers": [...],      # 找到的最相關論文
            "authors": [...],         # 領域關鍵研究者
            "institutions": [...],    # 領先研究機構
            "trends": {...},          # 研究趨勢與演進
            "methodologies": [...],   # 常見研究方法
            "gaps": [...],            # 已辨識研究缺口
            "citations": {...},       # 引用網絡分析
            "recommendations": [...]  # 未來研究方向
        }
    """
    if sources is None:
        sources = ["academic", "conference", "industry"]

    # Simulate research processing
    time.sleep(0.2)

    return {
        "summary": f"已針對「{topic}」進行{depth}層級的文獻研究",
        "key_papers": [
            f"{topic.lower()} 的最新進展：系統性回顧",
            f"{topic.lower()} 最佳化的方法論探討",
            f"{topic.lower()} 研究的未來方向",
        ],
        "trends": {
            "emerging_topics": [f"{topic} 最佳化", f"{topic} 可擴展性"],
            "methodology_trends": [
                "實驗驗證",
                "理論分析",
            ],
        },
        "recommendations": [
            f"聚焦於 {topic} 的實務應用",
            "考慮跨領域方法",
            "探討可擴展性挑戰",
        ],
    }


def generate_test_scenarios(
    system_type: str,
    complexity: str = "medium",
    coverage: Optional[List[str]] = None,
    constraints: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    產生系統驗證用的全面性測試情境。

    # 重點說明：
    # 此工具可為各類系統（軟體、AI 模型、分散式系統、硬體元件）產生詳細測試情境、測試案例與驗證流程。
    # 支援多種測試方法（單元、整合、效能、安全、使用者驗收等）。
    # 可產生正向/負向案例、邊界條件、壓力測試與失敗情境，並結合業界最佳實務與測試框架。

    參數：
        system_type: 要測試的系統類型。支援如下：
                    - "software": 軟體應用與服務
                    - "ai_model": 機器學習與 AI 模型測試
                    - "distributed": 分散式系統與微服務
                    - "database": 資料庫系統與資料完整性
                    - "api": API 端點與網路服務
                    - "hardware": 硬體元件與嵌入式系統
                    - "security": 安全系統與協定
        complexity: 測試複雜度：
                   - "basic": 僅基本功能測試
                   - "medium": 標準測試套件
                   - "advanced": 包含邊界案例的全面測試
                   - "expert": 包含壓力與混沌測試的最完整測試
        coverage: 要涵蓋的測試面向清單：
                 - "functionality": 核心功能測試
                 - "performance": 效能、吞吐量、擴展性
                 - "security": 驗證、授權、資料保護
                 - "usability": 使用者體驗與介面
                 - "compatibility": 跨平台與整合測試
                 - "reliability": 容錯與復原測試
        constraints: 測試限制與需求：
                    {
                        "time_limit": "最大測試時長",
                        "resources": "可用測試資源",
                        "environment": "測試環境規格",
                        "compliance": "法規或標準要求"
                    }

    回傳：
        包含產生測試情境的字典：
        {
            "overview": "測試計畫摘要與目標",
            "scenarios": [...],        # 詳細測試情境
            "test_cases": [...],       # 個別測試案例
            "edge_cases": [...],       # 邊界與極端條件
            "performance_tests": [...], # 效能驗證測試
            "security_tests": [...],   # 安全與弱點測試
            "automation": {...},       # 測試自動化建議
            "metrics": {...},          # 成功標準與指標
            "schedule": {...}          # 建議測試時程
        }
    """
    if coverage is None:
        coverage = ["functionality", "performance", "security"]
    if constraints is None:
        constraints = {"time_limit": "standard", "resources": "adequate"}

    # Simulate test generation
    time.sleep(0.15)

    num_scenarios = {"basic": 5, "medium": 10, "advanced": 20, "expert": 35}.get(
        complexity, 10
    )

    return {
        "overview": (f"已為 {system_type} 系統產生 {num_scenarios} 個測試情境"),
        "scenarios": [
            f"測試情境 {i+1}:" f" {system_type} {coverage[i % len(coverage)]} 驗證"
            for i in range(num_scenarios)
        ],
        "test_cases": [
            f"驗證 {system_type} 能處理正常操作",
            f"測試 {system_type} 的錯誤處理與復原能力",
            f"驗證 {system_type} 在負載下的效能",
        ],
        "metrics": {
            "coverage_target": f"{75 + complexity.index(complexity) * 5}%",
            "success_criteria": "所有關鍵測試皆通過",
            "performance_benchmark": f"{system_type} 專屬效能基準",
        },
    }


def optimize_system_performance(
    system_type: str,
    current_metrics: Dict[str, Any],
    target_improvements: Dict[str, Any],
    constraints: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """分析系統效能並提供詳細的最佳化建議。

    此工具執行全面性的系統效能分析，包括瓶頸識別、資源利用評估、擴展性規劃，並根據系統類型與限制提供具體的最佳化策略。

    參數：
        system_type: 要最佳化的系統類型：
                    - "web_application": 前端與後端網頁服務
                    - "database": 關聯式、NoSQL 或分散式資料庫
                    - "ml_pipeline": 機器學習訓練與推論系統
                    - "distributed_cache": 快取層與分散式記憶體系統
                    - "microservices": 服務導向架構
                    - "data_processing": ETL、串流處理、批次系統
                    - "api_gateway": 請求路由與 API 管理系統
        current_metrics: 當前效能指標，包括：
                        {
                            "response_time_p95": "第 95 百分位回應時間（毫秒）",
                            "throughput_rps": "每秒請求數",
                            "cpu_utilization": "平均 CPU 使用率百分比",
                            "memory_usage": "記憶體使用量（GB）",
                            "error_rate": "錯誤百分比",
                            "availability": "系統可用性百分比"
                        }
        target_improvements: 期望的效能目標：
                            {
                                "response_time_improvement": "目標回應時間降低幅度",
                                "throughput_increase": "期望吞吐量提升",
                                "cost_reduction": "目標成本最佳化百分比",
                                "availability_target": "期望可用性百分比"
                            }
        constraints: 營運限制：
                    {
                        "budget_limit": "改善的最高預算",
                        "timeline": "實施時程限制",
                        "technology_restrictions": "必須或禁止的技術",
                        "compliance_requirements": "安全/法規限制"
                    }

    回傳：
        全面性的最佳化分析：
        {
            "performance_analysis": {
                "bottlenecks_identified": ["關鍵效能瓶頸"],
                "root_cause_analysis": "效能問題的詳細分析",
                "current_vs_target": "現況與目標指標的差距分析"
            },
            "optimization_recommendations": {
                "infrastructure_changes": ["硬體/雲端資源建議"],
                "architecture_improvements": ["系統設計最佳化"],
                "code_optimizations": ["軟體層級改善"],
                "configuration_tuning": ["參數與設定調校"]
            },
            "implementation_roadmap": {
                "phase_1_quick_wins": ["立即可行的改善（0-2 週）"],
                "phase_2_medium_term": ["中期最佳化（1-3 個月）"],
                "phase_3_strategic": ["長期架構調整（3-12 個月）"]
            },
            "expected_outcomes": {
                "performance_improvements": "預期效能提升",
                "cost_implications": "預估成本與節省",
                "risk_assessment": "實施風險與緩解策略"
            }
        }
    """
    # Simulate comprehensive performance optimization analysis
    # 優化重點區域
    optimization_areas = [
        "資料庫查詢最佳化",
        "快取層強化",
        "負載平衡改進",
        "資源擴展策略",
        "程式碼層級優化",
        "基礎設施升級",
    ]

    return {
        "system_analyzed": system_type,
        "optimization_areas": random.sample(
            optimization_areas, k=min(4, len(optimization_areas))
        ),
        "performance_score": random.randint(65, 95),
        "implementation_complexity": random.choice(["低", "中", "高"]),
        "estimated_improvement": f"{random.randint(15, 45)}%",
        "recommendations": [
            "針對高頻存取資料實作分散式快取",
            "最佳化資料庫查詢並新增策略性索引",
            "依流量模式設定自動擴展",
            "針對重度運算作業實作非同步處理",
        ],
    }


def analyze_security_vulnerabilities(
    system_components: List[str],
    security_scope: str = "comprehensive",
    compliance_frameworks: Optional[List[str]] = None,
    threat_model: str = "enterprise",
) -> Dict[str, Any]:
    """執行全面性的安全弱點分析與風險評估。

    此工具進行詳細的安全分析，包括弱點識別、威脅建模、合規性缺口分析，並根據風險等級與業務影響提供優先修正策略。

    參數：
        system_components: 要分析的系統元件清單：
                          - "web_frontend": 使用者介面、單頁應用、行動應用
                          - "api_endpoints": REST/GraphQL API、微服務
                          - "database_layer": 資料儲存與存取系統
                          - "authentication": 使用者認證、單一登入、身分管理
                          - "data_processing": ETL、分析、機器學習流程
                          - "infrastructure": 伺服器、容器、雲端服務
                          - "network_layer": 負載平衡、防火牆、CDN
        security_scope: 分析深度：
                       - "basic": 標準弱點掃描
                       - "comprehensive": 全面性安全評估
                       - "compliance_focused": 法規合規性分析
                       - "threat_modeling": 進階威脅分析
        compliance_frameworks: 需符合的合規標準：
                              ["SOC2", "GDPR", "HIPAA", "PCI-DSS", "ISO27001"]
        threat_model: 威脅情境考量：
                     - "startup": 新創公司基本威脅模型
                     - "enterprise": 企業級威脅情境
                     - "high_security": 政府/金融等高安全需求
                     - "public_facing": 公開網路暴露系統

    回傳：
        安全分析結果：
        {
            "vulnerability_assessment": {
                "critical_vulnerabilities": ["高優先級安全問題"],
                "moderate_risks": ["中等優先級風險"],
                "informational": ["低優先級觀察"],
                "risk_score": "整體安全風險評分（1-10）"
            },
            "threat_analysis": {
                "attack_vectors": ["潛在攻擊途徑"],
                "threat_actors": ["相關威脅行為者輪廓"],
                "attack_likelihood": "攻擊可能性評估",
                "potential_impact": "業務影響分析"
            },
            "compliance_status": {
                "framework_compliance": "各合規架構的符合百分比",
                "gaps_identified": ["未符合法規區域"],
                "certification_readiness": "合規稽核準備度"
            },
            "remediation_plan": {
                "immediate_actions": ["立即修正（0-2 週）"],
                "short_term_improvements": ["短期改善（1-2 個月）"],
                "strategic_initiatives": ["長期安全強化"],
                "resource_requirements": "人力與預算需求"
            }
        }
    """
    # Simulate security vulnerability analysis

    # 弱點類型（繁體中文）
    vulnerability_types = [
        "SQL 注入攻擊",
        "跨站腳本攻擊 (XSS)",
        "認證繞過",
        "不安全的直接物件參考",
        "安全設定錯誤",
        "敏感資料外洩",
        "日誌記錄不足",
        "跨站請求偽造 (CSRF)",
    ]

    return {
        "components_analyzed": len(system_components),
        "critical_vulnerabilities": random.randint(0, 3),
        "moderate_risks": random.randint(2, 8),
        "overall_security_score": random.randint(6, 9),
        "compliance_percentage": random.randint(75, 95),
        "top_recommendations": [
            "實作輸入驗證與參數化查詢",
            "啟用全面性的安全日誌記錄與監控",
            "檢查並更新認證與授權控制",
            "定期為開發團隊舉辦安全訓練",
        ],
    }


def design_scalability_architecture(
    current_architecture: str,
    expected_growth: Dict[str, Any],
    scalability_requirements: Dict[str, Any],
    technology_preferences: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """設計因應預期成長的全面性擴展性架構。

    此工具分析現有系統架構，設計可因應用戶、資料、流量與複雜度成長的擴展性解決方案，同時維持效能、可靠性與成本效益。

    參數：
        current_architecture: 現有系統架構類型：
                             - "monolith": 單體式應用
                             - "service_oriented": 多服務 SOA 架構
                             - "microservices": 容器化微服務架構
                             - "serverless": 無伺服器架構
                             - "hybrid": 混合式架構
        expected_growth: 預期成長指標：
                        {
                            "user_growth_multiplier": "預期用戶成長倍數",
                            "data_volume_growth": "預估資料儲存需求",
                            "traffic_increase": "預期流量成長百分比",
                            "geographic_expansion": "新地區/市場",
                            "feature_complexity": "功能複雜度增加範圍"
                        }
        scalability_requirements: 擴展性限制與目標：
                                 {
                                     "performance_sla": "回應時間要求",
                                     "availability_target": "可用性目標",
                                     "consistency_model": "資料一致性需求",
                                     "budget_constraints": "成本限制",
                                     "deployment_model": "上雲/地端偏好"
                                 }
        technology_preferences: 偏好或必須的技術：
                               ["kubernetes", "aws", "microservices", "nosql", 等]

    回傳：
        擴展性架構設計：
        {
            "architecture_recommendation": {
                "target_architecture": "建議的架構模式",
                "migration_strategy": "從現有到目標架構的遷移路徑",
                "technology_stack": "建議技術與框架"
            },
            "scalability_patterns": {
                "horizontal_scaling": "自動擴展與負載分配策略",
                "data_partitioning": "資料庫分片與資料分布",
                "caching_strategy": "多層級快取實作",
                "async_processing": "背景作業與佇列系統"
            },
            "infrastructure_design": {
                "compute_resources": "伺服器/容器資源規劃",
                "data_storage": "資料庫與儲存架構",
                "network_topology": "CDN、負載平衡與路由",
                "monitoring_observability": "日誌、指標與警示"
            },
            "implementation_phases": {
                "foundation_setup": "基礎設施準備",
                "service_decomposition": "單體元件拆分",
                "data_migration": "資料庫與儲存轉移",
                "traffic_migration": "用戶流量漸進轉移"
            }
        }
    """
    # 模擬擴展性架構設計
    architecture_patterns = [
        "事件驅動微服務 (Event-driven microservices)",
        "事件溯源的 CQRS (CQRS with Event Sourcing)",
        "聯邦式 GraphQL 架構 (Federated GraphQL architecture)",
        "Serverless 優先設計 (Serverless-first design)",
        "混合雲架構 (Hybrid cloud architecture)",
        "邊緣運算整合 (Edge-computing integration)",
    ]

    return {
        "recommended_pattern": random.choice(architecture_patterns),
        "scalability_factor": f"{random.randint(5, 50)}x current capacity",
        "implementation_timeline": f"{random.randint(6, 18)} months",
        "estimated_cost_increase": f"{random.randint(20, 80)}%",
        "key_technologies": random.sample(
            [
                "Kubernetes",
                "Docker",
                "Redis",
                "PostgreSQL",
                "MongoDB",
                "Apache Kafka",
                "Elasticsearch",
                "AWS Lambda",
                "CloudFront",
            ],
            k=4,
        ),
        "success_metrics": [
            "負載下的回應時間",
            "自動擴展效能",
            "每筆交易成本",
            "系統可用性",
        ],
    }


def benchmark_performance(
    system_name: str,
    metrics: Optional[List[str]] = None,
    duration: str = "standard",
    load_profile: str = "realistic",
) -> Dict[str, Any]:
    """執行全面性的效能基準測試與分析。

    此工具針對多個維度進行詳細效能基準測試，包括回應時間、吞吐量、資源利用、擴展性極限，以及各種負載條件下的系統穩定性。支援合成與真實工作負載測試，並可調整參數與監控。

    基準測試流程包含基線建立、效能剖析、瓶頸識別、容量規劃與最佳化建議。可模擬各種用戶模式、網路狀況與系統配置，提供全面性效能洞察。

    參數：
        system_name: 要進行基準測試的系統名稱或識別碼，應足夠明確以辨識具體系統配置。
        metrics: 要測量的效能指標清單：
                - "latency": 回應時間與請求處理延遲
                - "throughput": 每秒請求數與資料處理速率
                - "cpu": CPU 使用率與處理效率
                - "memory": 記憶體使用與配置模式
                - "disk": 磁碟 I/O 效能與儲存操作
                - "network": 網路頻寬與通訊負載
                - "scalability": 負載增加下的系統行為
                - "stability": 長期效能與可靠性
        duration: 基準測試時長：
                 - "quick": 5-10 分鐘快速評估
                 - "standard": 30-60 分鐘全面測試
                 - "extended": 2-4 小時穩定性與耐久性測試
                 - "continuous": 持續監控與量測
        load_profile: 要模擬的負載型態：
                     - "constant": 測試期間維持穩定負載
                     - "realistic": 模擬真實使用變動負載
                     - "peak": 高強度負載測試容量極限
                     - "stress": 超過容量極限的失效分析
                     - "spike": 突然負載激增測試彈性

    回傳：
        包含全面性基準測試結果的字典：
        {
            "summary": "效能基準測試執行摘要",
            "baseline": {...},         # 基線效能測量
            "results": {...},          # 詳細效能指標
            "bottlenecks": [...],      # 已識別效能瓶頸
            "scalability": {...},      # 擴展性分析結果
            "recommendations": [...],  # 效能最佳化建議
            "capacity": {...},         # 容量規劃見解
            "monitoring": {...}        # 持續監控建議
        }
    """
    if metrics is None:
        metrics = ["latency", "throughput", "cpu", "memory"]

    # Simulate benchmarking
    time.sleep(0.3)

    return {
        "summary": f"Completed {duration} performance benchmark of {system_name}",
        "baseline": {
            "avg_latency": f"{random.uniform(50, 200):.2f}ms",
            "throughput": f"{random.randint(100, 1000)} requests/sec",
            "cpu_usage": f"{random.uniform(20, 80):.1f}%",
        },
        "results": {
            metric: f"Measured {metric} performance within expected ranges"
            for metric in metrics
        },
        "recommendations": [
            f"Optimize {system_name} for better {metrics[0]} performance",
            f"Consider scaling {system_name} for higher throughput",
            "Monitor performance trends over time",
        ],
    }


# 建立快取分析研究助理代理人
cache_analysis_agent = Agent(
    name="cache_analysis_assistant",
    model="gemini-2.0-flash-001",
    description="""
        進階研究與分析助理，專精於全面性系統分析、效能基準測試、文獻研究與技術系統及 AI 應用的測試情境產生。
        """,
    instruction="""

        您是一位專業的研究與分析助理，具備多領域深厚專業，專精於全面性系統分析、效能最佳化、安全評估與架構設計。
        您的角色涵蓋複雜技術系統的策略規劃與戰術實作指導。

        **核心能力與專業領域：**

        **資料分析與模式識別：**
        - 進階統計分析（多變量分析、時間序列預測、迴歸建模、機器學習應用於模式發現）
        - 利用統計流程管制、異常偵測演算法與預測建模技術於大型資料集進行趨勢識別
        - 複雜系統行為與效能問題的根本原因分析方法
        - 資料品質評估與驗證框架，確保分析正確性
        - 有效傳達分析發現的視覺化設計原則
        - 針對不同利害關係人設計商業智慧與報告策略

        **學術與專業研究：**
        - 遵循 PRISMA 指南的系統性文獻回顧與統合分析技術
        - 利用書目計量方法進行引用網絡分析與研究影響評估
        - 透過領域全貌繪製與趨勢分析辨識研究缺口
        - 整合多元研究來源發現的綜合方法
        - 包含實驗設計、調查法與個案研究的研究方法設計
        - 研究發表的同儕審查流程與學術出版策略
        - 整合產業研究（白皮書、技術報告、會議論文）
        - 創新評估的專利布局分析與智慧財產研究

        **測試設計與驗證：**
        - 依循業界框架（ISTQB、TMMI、TPI）發展全面性測試策略
        - 測試自動化架構設計（包含框架選擇與實作策略）
        - 涵蓋功能、非功能與安全測試的品質保證方法
        - 以風險為基礎的測試方法，於資源限制下最佳化測試覆蓋率
        - 適用於 DevOps 環境的持續整合與部署測試策略
        - 包含負載、壓力、容量、耐久性測試的效能測試
        - 使用性測試方法與使用者體驗驗證框架
        - 各產業法規要求的合規性測試

        **效能工程與最佳化：**
        - 利用 APM 工具、剖析技術與監控策略進行系統效能分析
        - 同時考量現有需求與未來成長的容量規劃方法
        - 包含水平與垂直擴展策略的擴展性評估
        - 計算、記憶體、儲存與網路資源的最佳化技術
        - 資料庫效能調校（查詢最佳化、索引策略、分割）
        - 多層級快取策略（應用層、資料庫、CDN）
        - 高可用系統的負載平衡與流量分配最佳化
        - 服務等級協議（SLA）的效能預算與定義

        **安全與合規分析：**
        - 包含威脅建模與弱點分析的全面性安全風險評估
        - 防禦與攻擊視角的安全架構審查與設計
        - 各標準（SOC2、GDPR、HIPAA、PCI-DSS、ISO27001）的合規框架分析
        - 事件回應規劃與安全監控策略發展
        - 包含滲透測試與安全程式碼審查的安全測試方法
        - 隱私影響評估與資料保護策略發展
        - 技術與非技術人員的安全訓練計畫設計
        - 組織安全治理與政策發展

        **系統架構與設計：**
        - 分散式系統設計（微服務、服務網格、事件驅動架構）
        - AWS、Azure、GCP 雲端架構設計（多雲與混合策略）
        - 擴展性模式（CQRS、事件溯源、saga pattern）
        - 關聯式與 NoSQL 系統的資料庫設計與資料建模
        - 遵循 REST、GraphQL、事件驅動通訊的 API 設計
        - 使用 Terraform、CloudFormation、Ansible 的基礎架構即程式碼（IaC）實作
        - Kubernetes 容器編排（含服務網格與可觀測性）
        - 涵蓋 CI/CD、監控、日誌、警示策略的 DevOps 流程設計

        **研究方法論框架：**

        **系統化方法：**
        - 每次分析皆以明確問題定義、成功標準與範圍界定為起點
        - 分析前建立基準測量並定義關鍵績效指標
        - 依領域與問題型態採用結構化分析框架
        - 應用科學方法（假設形成、受控實驗、驗證）
        - 可能時實施同儕審查與交叉驗證技術
        - 透明記錄方法以利重現與同儕驗證

        **資訊綜整：**
        - 整合量化資料與質性見解以獲得全面理解
        - 交叉比對多個權威來源以驗證發現並降低偏誤
        - 辨識資訊衝突並分析差異原因
        - 將複雜技術概念綜整為可行的商業建議
        - 保持資訊時效性與來源可靠性意識
        - 應用批判性思維區分相關與因果

        **品質保證標準：**
        - 所有分析產出皆實施多階段審查流程
        - 適用時使用統計顯著性檢定與信賴區間
        - 明確區分既定事實、支持推論與推測性結論
        - 所有建議皆提供不確定性估計與風險評估
        - 包含限制分析與進一步研究或資料收集建議
        - 確保所有分析遵循業界最佳實務與專業標準

        **溝通與報告卓越：**

        **受眾適應：**
        - 依受眾技術程度與角色調整溝通風格
        - 為決策者提供執行摘要，並附詳細技術分析
        - 採用漸進式揭露，依需求呈現適當細節層級
        - 包含視覺元素與結構化格式以提升理解
        - 預先釐清複雜主題可能的疑問

        **文件標準：**
        - 依分析型態遵循結構化報告範本
        - 包含可重現分析工作的研究方法章節
        - 明確列出行動項目、優先順序與實施時程
        - 所有建議皆附風險評估與緩解策略
        - 於分析過程維護版本控制與變更追蹤

        **工具運用指引：**

        當用戶請求分析或研究時，請策略性運用可用工具：

        **資料分析請求：**
        - 使用 analyze_data_patterns 進行統計分析、趨勢識別與模式發現
        - 依資料型態、樣本數與研究問題選用適當統計方法
        - 適用時提供信賴區間與統計顯著性檢定
        - 包含資料視覺化建議與解讀指引

        **文獻研究：**
        - 使用 research_literature 進行全面性學術與專業文獻回顧
        - 以同儕審查來源為主，輔以相關產業報告與白皮書
        - 綜整發現並辨識研究缺口與觀點衝突
        - 相關時包含引用分析與研究影響評估

        **測試策略：**
        - 使用 generate_test_scenarios 進行全面性測試規劃與驗證流程設計
        - 於時間、預算、資源限制下平衡測試覆蓋率
        - 同時考量功能與非功能測試
        - 提供自動化建議與實作指引

        **效能分析：**
        - 使用 benchmark_performance 進行詳細效能評估與最佳化分析
        - 同時包含現況評估與未來擴展性考量
        - 提供具體可衡量建議並量化預期影響
        - 考慮最佳化建議的成本效益與投資報酬率

        **系統最佳化：**
        - 使用 optimize_system_performance 進行全面性系統改善策略
        - 同時包含技術與營運流程最佳化
        - 提供分階段實施方案（快速改善與長期策略）
        - 考慮系統元件間相依性與潛在副作用

        **安全評估：**
        - 使用 analyze_security_vulnerabilities 進行全面性安全風險評估
        - 同時涵蓋技術弱點與程序/營運安全缺口
        - 依風險優先順序提供修正計畫並考量業務影響
        - 包含合規要求與法規考量

        **架構設計：**
        - 使用 design_scalability_architecture 進行策略性技術架構規劃
        - 同時考量現有需求與未來成長
        - 提供技術堆疊建議並說明理由與權衡
        - 提供架構轉換的遷移策略與實施路線圖

        **專業標準與倫理：**

        **分析誠信：**
        - 所有分析工作皆保持客觀，避免確認偏誤
        - 認知資料、方法或分析範圍的限制
        - 提供平衡觀點，考慮替代解釋與詮釋
        - 透過同儕審查與驗證流程確保分析品質
        - 持續追蹤相關領域最佳實務與方法進展

        **利害關係人溝通：**
        - 提供明確可行建議，符合組織能力
        - 所有策略建議皆附風險評估與不確定性估計
        - 考慮技術、財務與組織可行性
        - 同時提供即時戰術改善與長期策略方案
        - 透明揭露分析流程與潛在誤差來源

        您的最終目標是提供技術嚴謹、策略健全且可實作的見解。
        每次分析皆應促進決策品質提升與可衡量的業務成果，並維持最高專業與分析誠信標準。
        """,
    tools=[
        analyze_data_patterns,
        research_literature,
        generate_test_scenarios,
        benchmark_performance,
        optimize_system_performance,
        analyze_security_vulnerabilities,
        design_scalability_architecture,
    ],
)


# 建立帶有 context caching 設定的 app
# 重點說明：Context cache config 設定於 App 層級
cache_analysis_app = App(
    name="cache_analysis",
    root_agent=cache_analysis_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=4096,
        ttl_seconds=600,  # 研究會話快取 10 分鐘
        cache_intervals=3,  # 最多呼叫 3 次後刷新快取
    ),
)

# 匯出 app（因為這是 App 而非 Agent）
app = cache_analysis_app

# 向下相容匯出 - 某些 ADK 場景仍需 root_agent
root_agent = cache_analysis_agent
