"""
ADK 教學 24: 進階可觀測性與監控

此 Agent 展示了全面的可觀測性模式，包括：
- SaveFilesAsArtifactsPlugin 用於自動儲存檔案
- MetricsCollectorPlugin 用於請求/回應追蹤
- AlertingPlugin 用於錯誤檢測和警報
- PerformanceProfilerPlugin 用於詳細效能分析
- ProductionMonitoringSystem 用於完整的監控解決方案

功能特性：
- 基於外掛程式的架構，用於模組化可觀測性
- 即時指標收集和報告
- 錯誤檢測和警報
- 效能分析和剖析
- 生產就緒的監控模式
"""

import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from google.adk.agents import Agent
from google.adk.plugins import BasePlugin
from google.adk.events import Event
from google.genai import types


@dataclass
class RequestMetrics:
    """單一請求的指標。"""
    request_id: str
    agent_name: str
    start_time: float
    end_time: Optional[float] = None
    latency: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    token_count: int = 0
    tool_calls: int = 0


@dataclass
class AggregateMetrics:
    """跨請求的聚合指標。"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency: float = 0.0
    total_tokens: int = 0
    total_tool_calls: int = 0
    requests: List[RequestMetrics] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """計算成功率。"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests

    @property
    def avg_latency(self) -> float:
        """計算平均延遲。"""
        if self.total_requests == 0:
            return 0.0
        return self.total_latency / self.total_requests

    @property
    def avg_tokens(self) -> float:
        """計算平均 Token 數。"""
        if self.total_requests == 0:
            return 0.0
        return self.total_tokens / self.total_requests


class MetricsCollectorPlugin(BasePlugin):
    """用於收集請求指標的外掛程式。"""

    def __init__(self, name: str = 'metrics_collector_plugin'):
        """初始化指標收集器。"""
        super().__init__(name)
        self.metrics = AggregateMetrics()
        self.current_requests: Dict[str, RequestMetrics] = {}

    async def on_event_callback(self, *, invocation_context, event: Event) -> Optional[Event]:
        """處理 Agent 事件以進行指標收集。"""
        # 追蹤事件 (為教學簡化實作)
        if hasattr(event, 'event_type'):
            if event.event_type == 'request_start':
                request_id = str(time.time())
                metrics = RequestMetrics(
                    request_id=request_id,
                    agent_name='observability_plugins_agent',
                    start_time=time.time()
                )
                self.current_requests[request_id] = metrics
                print(f"📊 [METRICS] 請求開始於 {datetime.now().strftime('%H:%M:%S')}")

            elif event.event_type == 'request_complete':
                if self.current_requests:
                    request_id = list(self.current_requests.keys())[0]
                    metrics = self.current_requests[request_id]
                    metrics.end_time = time.time()
                    metrics.latency = metrics.end_time - metrics.start_time

                    # 更新聚合物件
                    self.metrics.total_requests += 1
                    self.metrics.successful_requests += 1
                    self.metrics.total_latency += metrics.latency
                    self.metrics.requests.append(metrics)

                    print(f"✅ [METRICS] 請求完成: {metrics.latency:.2f}s")
                    del self.current_requests[request_id]
        return event

    def get_summary(self) -> str:
        """獲取指標摘要。"""
        m = self.metrics

        summary = f"""
        METRICS SUMMARY (指標摘要)
        {'='*70}

        Total Requests (總請求數):       {m.total_requests}
        Successful (成功):               {m.successful_requests}
        Failed (失敗):                   {m.failed_requests}
        Success Rate (成功率):           {m.success_rate*100:.1f}%

        Average Latency (平均延遲):      {m.avg_latency:.2f}s
        Average Tokens (平均 Token):     {m.avg_tokens:.0f}
        Total Tool Calls (總工具呼叫):   {m.total_tool_calls}

        {'='*70}
        """.strip()

        return summary


class AlertingPlugin(BasePlugin):
    """用於異常警報的外掛程式。"""

    def __init__(self, name: str = 'alerting_plugin', latency_threshold: float = 5.0, error_threshold: int = 3):
        """
        初始化警報外掛程式。

        Args:
            name: 外掛程式名稱
            latency_threshold: 如果延遲超過此值則發出警報 (秒)
            error_threshold: 如果連續錯誤超過此值則發出警報
        """
        super().__init__(name)
        self.latency_threshold = latency_threshold
        self.error_threshold = error_threshold
        self.consecutive_errors = 0

    async def on_event_callback(self, *, invocation_context, event: Event) -> Optional[Event]:
        """處理 Agent 事件以進行警報。"""
        if hasattr(event, 'event_type'):
            if event.event_type == 'request_complete':
                # 成功時重置錯誤計數器
                self.consecutive_errors = 0

            elif event.event_type == 'request_error':
                self.consecutive_errors += 1
                print("🚨 [ALERT] 檢測到錯誤")

                if self.consecutive_errors >= self.error_threshold:
                    print(f"🚨🚨 [CRITICAL ALERT] 連續 {self.consecutive_errors} 次錯誤!")
        return event


class PerformanceProfilerPlugin(BasePlugin):
    """用於詳細效能分析的外掛程式。"""

    def __init__(self, name: str = 'performance_profiler_plugin'):
        """初始化分析器。"""
        super().__init__(name)
        self.profiles: List[Dict] = []
        self.current_profile: Optional[Dict] = None

    async def on_event_callback(self, *, invocation_context, event: Event) -> Optional[Event]:
        """處理 Agent 事件以進行分析。"""
        if hasattr(event, 'event_type'):
            if event.event_type == 'tool_call_start':
                self.current_profile = {
                    'tool': getattr(event, 'tool_name', 'unknown'),
                    'start_time': time.time()
                }
                print("⚙️ [PROFILER] 工具呼叫開始")

            elif event.event_type == 'tool_call_complete':
                if self.current_profile:
                    self.current_profile['end_time'] = time.time()
                    self.current_profile['duration'] = (
                        self.current_profile['end_time'] - self.current_profile['start_time']
                    )
                    self.profiles.append(self.current_profile)
                    print(f"✅ [PROFILER] 工具呼叫完成: {self.current_profile['duration']:.2f}s")
                    self.current_profile = None
        return event

    def get_profile_summary(self) -> str:
        """獲取分析摘要。"""
        if not self.profiles:
            return "未收集到分析資料"

        summary = f"\nPERFORMANCE PROFILE (效能分析)\n{'='*70}\n\n"

        tool_stats = {}

        for profile in self.profiles:
            if 'duration' not in profile:
                continue

            tool = profile['tool']

            if tool not in tool_stats:
                tool_stats[tool] = {
                    'calls': 0,
                    'total_duration': 0.0,
                    'min_duration': float('inf'),
                    'max_duration': 0.0
                }

            stats = tool_stats[tool]
            stats['calls'] += 1
            stats['total_duration'] += profile['duration']
            stats['min_duration'] = min(stats['min_duration'], profile['duration'])
            stats['max_duration'] = max(stats['max_duration'], profile['duration'])

        for tool, stats in tool_stats.items():
            avg_duration = stats['total_duration'] / stats['calls']

            summary += f"Tool (工具): {tool}\n"
            summary += f"  Calls (呼叫次數):        {stats['calls']}\n"
            summary += f"  Avg Duration (平均耗時): {avg_duration:.3f}s\n"
            summary += f"  Min Duration (最小耗時): {stats['min_duration']:.3f}s\n"
            summary += f"  Max Duration (最大耗時): {stats['max_duration']:.3f}s\n\n"

        summary += f"{'='*70}\n"

        return summary


# 建立包含所有外掛程式的可觀測性 Agent
root_agent = Agent(
    model='gemini-2.5-flash',
    name='observability_plugins_agent',
    description="""具有全面可觀測性的生產助理，包括指標收集、警報和效能分析，用於企業監控。""",
    instruction="""
    您是一位生產助理，負責協助客戶解決有關 AI 和技術的疑問。

    關鍵行為：
    - 提供準確、有幫助的回覆
    - 保持回覆簡潔但資訊豐富
    - 使用清晰、簡單的語言
    - 保持主題相關並專注

    您的回覆正受到品質、效能和可靠性的監控。
    請始終保持樂於助人且準確。
    """.strip(),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.5,
        max_output_tokens=1024
    )
)


def main():
    """
    示範主要進入點。

    此函式演示如何將可觀測性 Agent 與 ADK 網頁介面一起使用。
    實際的監控外掛程式是在 Runner 層級註冊的 (請參見測試中的範例)。
    """
    print("🚀 教學 24: 進階可觀測性與監控")
    print("=" * 70)
    print("\n📊 可觀測性 Agent 功能:")
    print("  • SaveFilesAsArtifactsPlugin - 自動儲存檔案")
    print("  • MetricsCollectorPlugin - 請求/回應指標")
    print("  • AlertingPlugin - 錯誤檢測和警報")
    print("  • PerformanceProfilerPlugin - 詳細效能分析")
    print("\n💡 查看 Agent 運作:")
    print("  1. 執行: adk web")
    print("  2. 打開 http://localhost:8000")
    print("  3. 從下拉選單中選擇 'observability_plugins_agent'")
    print("  4. 嘗試各種提示並觀察控制台指標")
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()

# 重點摘要
# - **核心概念**: 可觀測性 Agent 實作
# - **關鍵技術**: Google ADK, BasePlugin, Metrics Collection, Alerting, Profiling
# - **行動項目**: 執行此腳本以啟動監控 Agent

