"""
最佳實踐代理 - 生產就緒模式 (Best Practices Agent - Production-Ready Patterns)

展示：
- 使用 Pydantic 進行輸入驗證 (Input validation)
- 綜合錯誤處理 (Comprehensive error handling)
- 斷路器模式 (Circuit breaker pattern)
- 具指數退避的重試邏輯 (Retry logic with exponential backoff)
- 效能最佳化 (Performance optimization) (快取、批次處理)
- 監控與健康指標 (Monitoring and health metrics)
"""

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Dict, Any, List, Optional
from enum import Enum
import time
import random
import logging

# 設定日誌記錄 (Configure logging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# 模型與驗證 (MODELS & VALIDATION)
# ============================================================================

class CircuitState(Enum):
    """斷路器狀態 (Circuit breaker states)。"""
    CLOSED = "closed"       # 關閉 (正常運作)
    OPEN = "open"           # 開啟 (阻斷請求)
    HALF_OPEN = "half_open" # 半開啟 (嘗試恢復)


class InputRequest(BaseModel):
    """
    經過驗證的輸入請求 (Validated input request)。
    使用 Pydantic 確保資料符合預期格式與安全規範。
    """

    email: Optional[EmailStr] = Field(None, description="要驗證的電子郵件地址")
    text: str = Field(..., min_length=1, max_length=10000, description="文字內容")
    priority: str = Field("normal", description="優先順序層級")

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        """驗證優先順序值 (Validate priority values)。"""
        valid = ["low", "normal", "high", "urgent"]
        if v not in valid:
            raise ValueError(f"優先順序必須是以下之一：{', '.join(valid)}")
        return v

    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        """
        驗證文字內容是否包含危險模式 (Validate text content for dangerous patterns)。
        防止 SQL 注入與 XSS 攻擊。
        """
        dangerous = ['DROP TABLE', 'DELETE FROM', '; --', '<SCRIPT>']
        v_upper = v.upper()

        for pattern in dangerous:
            if pattern in v_upper:
                raise ValueError(f"偵測到潛在危險模式：{pattern}")

        return v


# ============================================================================
# 斷路器模式 (CIRCUIT BREAKER PATTERN)
# ============================================================================

class CircuitBreaker:
    """
    外部依賴的斷路器 (Circuit breaker for external dependencies)。

    透過暫時阻斷對故障服務的請求，防止連鎖故障 (Cascading failures)。
    具有三種狀態：關閉 (CLOSED)、開啟 (OPEN)、半開啟 (HALF_OPEN)。
    """

    def __init__(self, failure_threshold: int = 3, timeout_seconds: int = 30):
        self.failure_threshold = failure_threshold # 觸發斷路器的失敗次數閾值
        self.timeout = timeout_seconds             # 斷路器開啟後的冷卻時間
        self.failures = 0                          # 當前連續失敗次數
        self.last_failure_time = None              # 上次失敗時間
        self.state = CircuitState.CLOSED           # 初始狀態為關閉 (正常)
        self.success_count = 0                     # 半開啟狀態下的成功次數

    def call(self, func, *args, **kwargs):
        """執行受斷路器保護的函數 (Execute function with circuit breaker protection)。"""

        # 檢查斷路器是否開啟
        if self.state == CircuitState.OPEN:
            # 如果超過冷卻時間，嘗試進入半開啟狀態
            if time.time() - self.last_failure_time > self.timeout:
                logger.info("斷路器進入 HALF_OPEN 狀態")
                self.state = CircuitState.HALF_OPEN
            else:
                # 仍在冷卻時間內，直接拋出異常，不執行實際函數
                raise Exception(f"斷路器為 OPEN 狀態。請於 {int(self.timeout - (time.time() - self.last_failure_time))} 秒後重試")

        try:
            # 執行實際函數
            result = func(*args, **kwargs)

            # 成功 - 重置或關閉斷路器
            if self.state == CircuitState.HALF_OPEN:
                logger.info("呼叫成功後斷路器關閉")
                self.state = CircuitState.CLOSED
                self.failures = 0
                self.success_count = 0

            return result

        except Exception:
            # 發生異常，增加失敗計數
            self.failures += 1
            self.last_failure_time = time.time()

            # 如果失敗次數達到閾值，開啟斷路器
            if self.failures >= self.failure_threshold:
                logger.warning(f"在 {self.failures} 次失敗後斷路器開啟")
                self.state = CircuitState.OPEN

            raise


# 全域斷路器實例 (Global circuit breaker instance)
external_service_breaker = CircuitBreaker(failure_threshold=3, timeout_seconds=30)


# ============================================================================
# 效能最佳化 (PERFORMANCE OPTIMIZATION)
# ============================================================================

class CachedDataStore:
    """具 TTL 的時間基礎快取 (Time-based cache with TTL)。"""

    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}  # 儲存結構: {key: (value, timestamp)}
        self.ttl = ttl_seconds
        self.hits = 0    # 命中次數
        self.misses = 0  # 未命中次數

    def get(self, key: str) -> Optional[Any]:
        """如果未過期則取得快取值 (Get cached value if not expired)。"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            # 檢查是否在 TTL 有效期內
            if time.time() - timestamp < self.ttl:
                self.hits += 1
                return value
            del self.cache[key] # 已過期，刪除

        self.misses += 1
        return None

    def set(self, key: str, value: Any):
        """儲存值與當前時間戳 (Store value with current timestamp)。"""
        self.cache[key] = (value, time.time())

    def stats(self) -> Dict[str, Any]:
        """取得快取統計資料 (Get cache statistics)。"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'size': len(self.cache)
        }


# 全域快取實例 (Global cache instance)
data_cache = CachedDataStore(ttl_seconds=300)


# ============================================================================
# 指標與監控 (METRICS & MONITORING)
# ============================================================================

class MetricsCollector:
    """收集與追蹤系統指標 (Collect and track system metrics)。"""

    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_latency = 0.0
        self.start_time = time.time()

    def record_request(self, latency: float, error: bool = False):
        """記錄請求指標 (Record request metrics)。"""
        self.request_count += 1
        self.total_latency += latency
        if error:
            self.error_count += 1

    def get_metrics(self) -> Dict[str, Any]:
        """取得當前指標 (Get current metrics)。"""
        uptime = time.time() - self.start_time
        avg_latency = self.total_latency / self.request_count if self.request_count > 0 else 0
        error_rate = (self.error_count / self.request_count * 100) if self.request_count > 0 else 0

        return {
            'uptime_seconds': round(uptime, 2),
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': f"{error_rate:.2f}%",
            'avg_latency_ms': round(avg_latency * 1000, 2),
            'requests_per_second': round(self.request_count / uptime, 2) if uptime > 0 else 0
        }

    def health_check(self) -> Dict[str, Any]:
        """執行健康檢查 (Perform health check)。"""
        metrics = self.get_metrics()

        # 判斷健康狀態
        error_rate = float(metrics['error_rate'].rstrip('%'))

        if error_rate > 50:
            status = "unhealthy" # 不健康
        elif error_rate > 10:
            status = "degraded"  # 降級
        else:
            status = "healthy"   # 健康

        return {
            'status': status,
            'circuit_breaker_state': external_service_breaker.state.value,
            'cache_stats': data_cache.stats(),
            'metrics': metrics
        }


# 全域指標收集器 (Global metrics collector)
metrics = MetricsCollector()


# ============================================================================
# 工具 (TOOLS)
# ============================================================================

def validate_input_tool(
    email: str,
    text: str,
    priority: str = "normal",
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    透過綜合檢查驗證使用者輸入 (Validate user input with comprehensive checks)。

    展示：
    - Pydantic 驗證
    - 輸入淨化 (Input sanitization)
    - 安全性最佳實踐

    Args:
        email: 要驗證的電子郵件地址
        text: 要驗證的文字內容
        priority: 優先順序層級 (low, normal, high, urgent)
        tool_context: ADK 工具上下文

    Returns:
        Dict: 驗證結果
    """
    start_time = time.time()

    try:
        # 使用 Pydantic 進行驗證
        request = InputRequest(
            email=email if email else None,
            text=text,
            priority=priority
        )

        latency = time.time() - start_time
        metrics.record_request(latency, error=False)

        return {
            'status': 'success',
            'report': f'✅ 輸入驗證通過 email={email}, priority={priority}',
            'validated_data': {
                'email': request.email,
                'text_length': len(request.text),
                'priority': request.priority
            },
            'validation_time_ms': round(latency * 1000, 2)
        }

    except ValueError as e:
        latency = time.time() - start_time
        metrics.record_request(latency, error=True)

        return {
            'status': 'error',
            'error': str(e),
            'report': f'❌ 驗證失敗：{str(e)}',
            'validation_time_ms': round(latency * 1000, 2)
        }

    except Exception as e:
        latency = time.time() - start_time
        metrics.record_request(latency, error=True)
        logger.error(f"意外的驗證錯誤：{e}")

        return {
            'status': 'error',
            'error': '內部驗證錯誤',
            'report': '❌ 驗證期間發生意外錯誤',
            'validation_time_ms': round(latency * 1000, 2)
        }


def retry_with_backoff_tool(
    operation: str,
    max_retries: int = 3,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    執行具有重試邏輯和指數退避的操作 (Execute operation with retry logic and exponential backoff)。

    展示：
    - 錯誤處理
    - 重試模式
    - 指數退避 (Exponential backoff)

    Args:
        operation: 要執行的操作
        max_retries: 最大重試次數
        tool_context: ADK 工具上下文

    Returns:
        Dict: 執行結果
    """
    start_time = time.time()

    def simulated_operation():
        """模擬可能失敗的操作 (Simulate an operation that might fail)。"""
        # 30% 機率失敗
        if random.random() < 0.3:
            raise Exception("模擬的暫時性錯誤 (Simulated transient error)")
        return {"result": f"成功處理：{operation}"}

    attempts = []

    for attempt in range(max_retries):
        try:
            logger.info(f"嘗試 {attempt + 1} / {max_retries}")
            result = simulated_operation()

            latency = time.time() - start_time
            metrics.record_request(latency, error=False)

            return {
                'status': 'success',
                'report': f'✅ 操作在嘗試 {attempt + 1} 次後成功',
                'result': result,
                'attempts': attempt + 1,
                'total_time_ms': round(latency * 1000, 2)
            }

        except Exception as e:
            attempts.append({
                'attempt': attempt + 1,
                'error': str(e),
                'timestamp': time.time()
            })

            if attempt < max_retries - 1:
                backoff_time = 2 ** attempt  # 指數退避：1s, 2s, 4s
                logger.warning(f"嘗試 {attempt + 1} 失敗，將在 {backoff_time} 秒後重試")
                time.sleep(backoff_time)
            else:
                latency = time.time() - start_time
                metrics.record_request(latency, error=True)

                return {
                    'status': 'error',
                    'error': f'操作在 {max_retries} 次嘗試後失敗',
                    'report': f'❌ 所有 {max_retries} 次重試嘗試均失敗',
                    'attempts': attempts,
                    'total_time_ms': round(latency * 1000, 2)
                }

    latency = time.time() - start_time
    metrics.record_request(latency, error=True)

    return {
        'status': 'error',
        'error': '超過最大重試次數',
        'report': '❌ 操作失敗',
        'total_time_ms': round(latency * 1000, 2)
    }


def circuit_breaker_call_tool(
    service_name: str,
    simulate_failure: bool = False,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    使用斷路器保護呼叫外部服務 (Call external service with circuit breaker protection)。

    展示：
    - 斷路器模式
    - 優雅降級 (Graceful degradation)
    - 故障隔離 (Failure isolation)

    Args:
        service_name: 要呼叫的服務名稱
        simulate_failure: 是否模擬失敗
        tool_context: ADK 工具上下文

    Returns:
        Dict: 呼叫結果
    """
    start_time = time.time()

    def external_service_call():
        """模擬外部服務呼叫 (Simulate external service call)。"""
        if simulate_failure:
            raise Exception(f"服務 {service_name} 無法使用")
        return {"data": f"來自 {service_name} 的回應"}

    try:
        # 透過斷路器執行呼叫
        result = external_service_breaker.call(external_service_call)

        latency = time.time() - start_time
        metrics.record_request(latency, error=False)

        return {
            'status': 'success',
            'report': f'✅ 成功呼叫 {service_name}',
            'result': result,
            'circuit_state': external_service_breaker.state.value,
            'latency_ms': round(latency * 1000, 2)
        }

    except Exception as e:
        latency = time.time() - start_time
        metrics.record_request(latency, error=True)

        return {
            'status': 'error',
            'error': str(e),
            'report': f'❌ 呼叫 {service_name} 失敗：{str(e)}',
            'circuit_state': external_service_breaker.state.value,
            'failures': external_service_breaker.failures,
            'latency_ms': round(latency * 1000, 2)
        }


def cache_operation_tool(
    key: str,
    value: Optional[str] = None,
    operation: str = "get",
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    執行快取操作以進行效能最佳化 (Perform caching operations for performance optimization)。

    展示：
    - 快取策略
    - TTL 管理
    - 快取統計

    Args:
        key: 快取鍵
        value: 要快取的值 (用於 set 操作)
        operation: 要執行的操作 (get, set, stats)
        tool_context: ADK 工具上下文

    Returns:
        Dict: 操作結果
    """
    start_time = time.time()

    try:
        if operation == "set":
            if value is None:
                return {
                    'status': 'error',
                    'error': 'set 操作需要值',
                    'report': '❌ 無法在沒有值的情況下設定快取'
                }

            data_cache.set(key, value)

            return {
                'status': 'success',
                'report': f'✅ 已快取鍵的值：{key}',
                'operation': 'set',
                'key': key
            }

        elif operation == "get":
            cached_value = data_cache.get(key)

            if cached_value is not None:
                return {
                    'status': 'success',
                    'report': f'✅ 快取命中 (HIT) 鍵：{key}',
                    'operation': 'get',
                    'key': key,
                    'value': cached_value,
                    'cache_hit': True
                }
            else:
                return {
                    'status': 'success',
                    'report': f'ℹ️  快取未命中 (MISS) 鍵：{key}',
                    'operation': 'get',
                    'key': key,
                    'cache_hit': False
                }

        elif operation == "stats":
            stats = data_cache.stats()

            return {
                'status': 'success',
                'report': '✅ 已取得快取統計',
                'operation': 'stats',
                'statistics': stats
            }

        else:
            return {
                'status': 'error',
                'error': f'未知操作：{operation}',
                'report': '❌ 無效操作。請使用：get, set, 或 stats'
            }

    except Exception as e:
        latency = time.time() - start_time
        metrics.record_request(latency, error=True)
        logger.error(f"快取操作錯誤：{e}")

        return {
            'status': 'error',
            'error': str(e),
            'report': f'❌ 快取操作失敗：{str(e)}'
        }


def batch_process_tool(
    items: List[str],
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    批次處理多個項目以提升效率 (Batch process multiple items for efficiency)。

    展示：
    - 批次處理 (Batch processing)
    - 效能最佳化
    - 資源效率

    Args:
        items: 要處理的項目列表
        tool_context: ADK 工具上下文

    Returns:
        Dict: 批次處理結果
    """
    start_time = time.time()

    try:
        if not items or len(items) == 0:
            return {
                'status': 'error',
                'error': '未提供項目',
                'report': '❌ 無法批次處理空列表'
            }

        # 批次處理項目
        results = []
        for i, item in enumerate(items):
            results.append({
                'index': i,
                'item': item,
                'processed': f"已處理 (PROCESSED)-{item}",
                'timestamp': time.time()
            })

        latency = time.time() - start_time
        metrics.record_request(latency, error=False)

        # 計算效率增益
        sequential_time_estimate = len(items) * 0.1  # 假設每個項目需 100ms
        time_saved = sequential_time_estimate - latency

        return {
            'status': 'success',
            'report': f'✅ 於 {round(latency * 1000, 2)}ms 內批次處理了 {len(items)} 個項目',
            'items_processed': len(items),
            'results': results,
            'processing_time_ms': round(latency * 1000, 2),
            'estimated_sequential_time_ms': round(sequential_time_estimate * 1000, 2),
            'time_saved_ms': round(time_saved * 1000, 2) if time_saved > 0 else 0,
            'efficiency_gain': f"{round(time_saved / sequential_time_estimate * 100, 1)}%" if sequential_time_estimate > 0 else "0%"
        }

    except Exception as e:
        latency = time.time() - start_time
        metrics.record_request(latency, error=True)
        logger.error(f"批次處理錯誤：{e}")

        return {
            'status': 'error',
            'error': str(e),
            'report': f'❌ 批次處理失敗：{str(e)}'
        }


def health_check_tool(
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    執行綜合健康檢查 (Perform comprehensive health check)。

    展示：
    - 健康監控
    - 系統指標
    - 可觀測性模式

    Args:
        tool_context: ADK 工具上下文

    Returns:
        Dict: 健康狀態
    """
    try:
        health = metrics.health_check()

        return {
            'status': 'success',
            'report': f'✅ 系統健康：{health["status"].upper()}',
            'health': health
        }

    except Exception as e:
        logger.error(f"健康檢查錯誤：{e}")

        return {
            'status': 'error',
            'error': str(e),
            'report': f'❌ 健康檢查失敗：{str(e)}'
        }


def get_metrics_tool(
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    取得當前系統指標 (Get current system metrics)。

    展示：
    - 指標收集
    - 效能監控
    - 可觀測性

    Args:
        tool_context: ADK 工具上下文

    Returns:
        Dict: 系統指標
    """
    try:
        system_metrics = metrics.get_metrics()

        return {
            'status': 'success',
            'report': f'✅ 已取得系統指標 ({system_metrics["total_requests"]} 次請求)',
            'metrics': system_metrics
        }

    except Exception as e:
        logger.error(f"指標取得錯誤：{e}")

        return {
            'status': 'error',
            'error': str(e),
            'report': f'❌ 取得指標失敗：{str(e)}'
        }


# ============================================================================
# 代理設定 (AGENT CONFIGURATION)
# ============================================================================

root_agent = Agent(
    name="best_practices_agent",
    model="gemini-2.5-flash",
    description="展示安全性、效能、可靠性和可觀測性最佳實踐的生產就緒代理",
    instruction="""
    你是一個生產就緒代理 (Production-ready agent)，展示建置穩健、安全且高效系統的最佳實踐。

    ## 你的能力 (Your Capabilities)

    你擁有展示以下功能的工具：

    **安全性與驗證 (Security & Validation):**
    - 具綜合檢查的輸入驗證
    - XSS 與 SQL 注入防護
    - 電子郵件驗證

    **可靠性與韌性 (Reliability & Resilience):**
    - 具指數退避的重試邏輯
    - 外部服務的斷路器模式
    - 優雅的錯誤處理

    **效能最佳化 (Performance Optimization):**
    - 具 TTL 的快取機制
    - 提升效率的批次處理
    - 回應時間最佳化

    **可觀測性與監控 (Observability & Monitoring):**
    - 健康檢查
    - 系統指標收集
    - 效能統計

    ## 如何使用你的工具 (How to Use Your Tools)

    1. **validate_input_tool**: 透過安全性檢查驗證使用者輸入
    2. **retry_with_backoff_tool**: 執行具重試邏輯的操作
    3. **circuit_breaker_call_tool**: 安全地呼叫外部服務
    4. **cache_operation_tool**: 為了效能快取資料
    5. **batch_process_tool**: 高效地處理多個項目
    6. **health_check_tool**: 檢查系統健康狀態
    7. **get_metrics_tool**: 取得效能指標

    ## 指導方針 (Guidelines)

    - 處理前務必驗證輸入
    - 優雅地處理錯誤並提供有用的訊息
    - 為了效能在適當時候使用快取
    - 監控系統健康並報告問題
    - 在你的回應中展示生產模式
    - 解釋你正在應用的最佳實踐

    ## 互動範例 (Example Interactions)

    User: "Validate this email: user@example.com"
    → 使用 validate_input_tool 展示安全性驗證

    User: "Process order with retry logic"
    → 使用 retry_with_backoff_tool 展示韌性模式

    User: "Call external service"
    → 使用 circuit_breaker_call_tool 展示故障保護

    User: "Show system health"
    → 使用 health_check_tool 顯示監控能力
    """.strip(),
    tools=[
        validate_input_tool,
        retry_with_backoff_tool,
        circuit_breaker_call_tool,
        cache_operation_tool,
        batch_process_tool,
        health_check_tool,
        get_metrics_tool,
    ]
)


def main():
    """執行代理的主要進入點 (Main entry point for running the agent)。"""
    print("🚀 最佳實踐代理 - 生產就緒模式 (Production-Ready Patterns)")
    print("=" * 60)
    print("\n此代理展示：")
    print("  ✅ 輸入驗證與安全性")
    print("  ✅ 錯誤處理與重試邏輯")
    print("  ✅ 斷路器模式")
    print("  ✅ 效能最佳化")
    print("  ✅ 監控與可觀測性")
    print("\n" + "=" * 60)
    print("\n執行 'adk web' 以與代理互動")
    print("或使用 'make dev' 進入開發模式\n")


if __name__ == "__main__":
    main()

# 重點摘要 (Code Summary)
# - **核心概念**：實現了一個具備生產級特性的代理，包含安全性、可靠性、效能和監控模組。
# - **關鍵技術**：Pydantic (驗證), Circuit Breaker (斷路器), Cache with TTL (快取), Metrics Collection (指標收集), ADK Tools (工具整合)。
# - **重要結論**：透過模組化工具設計，代理能夠在保持高可靠性的同時，提供高效且安全的服務。
# - **行動項目**：整合至實際應用前，需根據具體業務需求調整斷路器閾值與快取 TTL 設定。
