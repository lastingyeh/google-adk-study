import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import Session, InMemorySessionService
from google.adk.events import Event, EventActions
from google.genai import types


# 設定日誌記錄
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CustomerServiceMonitor:
    """具備全面事件監控的客戶服務代理程式。

    功能：
    - 追蹤所有互動的事件
    - 記錄工具呼叫
    - 處理上報
    - 收集指標
    - 提供詳細報告
    """

    def __init__(self):
        """初始化客戶服務監控系統。"""

        # 事件日誌儲存
        self.events: List[Dict[str, Any]] = []

        # 建立具備事件追蹤功能的工具

        def check_order_status(order_id: str) -> Dict[str, Any]:
            """
            檢查訂單狀態。

            Args:
                order_id: 訂單識別碼 (例如：'ORD-001')

            Returns:
                包含狀態、報告與訂單詳情的字典
            """
            self._log_tool_call('check_order_status', {'order_id': order_id})

            # 模擬訂單查詢
            order_statuses = {
                'ORD-001': '已出貨',
                'ORD-002': '處理中',
                'ORD-003': '已送達'
            }

            status = order_statuses.get(order_id, 'not_found')

            if status == 'not_found':
                return {
                    'status': 'error',
                    'report': f'找不到訂單 {order_id}',
                    'order_id': order_id,
                    'order_status': None
                }

            return {
                'status': 'success',
                'report': f'訂單 {order_id} 狀態：{status}',
                'order_id': order_id,
                'order_status': status
            }

        def process_refund(order_id: str, amount: float) -> Dict[str, Any]:
            """
            處理退款請求。

            Args:
                order_id: 訂單識別碼
                amount: 退款金額

            Returns:
                包含狀態、報告與退款詳情的字典
            """
            self._log_tool_call('process_refund', {
                'order_id': order_id,
                'amount': amount
            })

            # 金額超過 100 時上報
            if amount > 100:
                return {
                    'status': 'requires_approval',
                    'report': f'上報：${amount} 的退款超過批准門檻',
                    'order_id': order_id,
                    'amount': amount,
                    'requires_approval': True
                }

            return {
                'status': 'success',
                'report': f'訂單 {order_id} 的 ${amount} 退款已批准',
                'order_id': order_id,
                'amount': amount,
                'approved': True
            }

        def check_inventory(product_id: str) -> Dict[str, Any]:
            """
            檢查產品庫存。

            Args:
                product_id: 產品識別碼 (例如：'PROD-A')

            Returns:
                包含狀態、報告與庫存詳情的字典
            """
            self._log_tool_call('check_inventory', {'product_id': product_id})

            # 模擬庫存檢查
            inventory_levels = {
                'PROD-A': 150,
                'PROD-B': 5,
                'PROD-C': 0
            }

            inventory = inventory_levels.get(product_id, 0)

            return {
                'status': 'success',
                'report': f'產品 {product_id} 庫存：{inventory} 件',
                'product_id': product_id,
                'inventory': inventory,
                'in_stock': inventory > 0
            }

        # 客戶服務代理程式
        self.agent = Agent(
            model='gemini-2.0-flash-exp',
            name='customer_service',
            description='具備事件追蹤的客戶服務代理程式',
            instruction="""
            您是一位客戶服務代理，協助客戶處理：
            - 訂單狀態查詢
            - 退款請求
            - 庫存檢查
            - 一般問題

            指南：
            1. 始終保持禮貌與樂於助人
            2. 使用工具以獲取準確資訊
            3. 對於超過 100 美元的退款，說明需要主管批准
            4. 追蹤所有互動
            5. 記錄重要決策

            可用工具：
            - check_order_status: 依訂單 ID 取得訂單狀態
            - process_refund: 處理退款 (若超過 100 美元則上報)
            - check_inventory: 依產品 ID 檢查產品可用性

            務必呼叫適當的工具以獲取準確資訊。
            """.strip(),
            tools=[
                check_order_status,
                process_refund,
                check_inventory
            ],
            generate_content_config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=1024
            )
        )

        # 建立具備 session 服務的 runner
        session_service = InMemorySessionService()
        self.runner = Runner(
            app_name="observability_agent",
            agent=self.agent,
            session_service=session_service
        )
        self.session_service = session_service

    def _log_tool_call(self, tool_name: str, args: Dict[str, Any]):
        """記錄工具調用。"""
        self.events.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'tool_call',
            'tool': tool_name,
            'arguments': args
        })
        logger.info(f"工具已呼叫：{tool_name}，參數：{args}")

    def _log_agent_event(self, event_type: str, data: Dict[str, Any]):
        """記錄代理程式事件。"""
        self.events.append({
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'data': data
        })
        logger.info(f"代理程式事件：{event_type} - {data}")

    async def handle_customer_query(
        self,
        customer_id: str,
        query: str
    ) -> Any:
        """
        處理客戶查詢並進行完整的事件追蹤。

        Args:
            customer_id: 客戶識別碼
            query: 客戶查詢

        Returns:
            代理程式的回應
        """

        print(f"\n{'='*70}")
        print(f"客戶：{customer_id}")
        print(f"查詢：{query}")
        print(f"{'='*70}\n")

        # 記錄查詢事件
        self._log_agent_event('customer_query', {
            'customer_id': customer_id,
            'query': query
        })

        # 建立帶有客戶上下文的 session
        session = await self.session_service.create_session(
            app_name="observability_agent",
            user_id=customer_id
        )

        # 設定 session 狀態
        session.state['customer_id'] = customer_id
        session.state['query_time'] = datetime.now().isoformat()
        session.state['query_count'] = session.state.get('query_count', 0) + 1

        # 使用正確的 run_async 簽章執行代理程式
        result_event = None
        async for event in self.runner.run_async(
            user_id=customer_id,
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text=query)])
        ):
            result_event = event
            if event.turn_complete:
                break

        # 使用最終事件作為結果
        result = result_event if result_event else None

        # 記錄回應
        response_text = ""
        if result and result.content and result.content.parts:
            response_text = result.content.parts[0].text

        self._log_agent_event('agent_response', {
            'customer_id': customer_id,
            'response': response_text
        })

        # 檢查是否需要上報
        if 'ESCALATE' in response_text or 'requires approval' in response_text.lower():
            self._log_agent_event('escalation', {
                'customer_id': customer_id,
                'reason': response_text
            })
            print("🚨 已上報至主管\n")

        print(f"🤖 代理程式回應：\n{response_text}\n")
        print(f"{'='*70}\n")

        return result

    def get_event_summary(self) -> str:
        """產生事件摘要報告。"""

        total_events = len(self.events)

        event_types: Dict[str, int] = {}
        for event in self.events:
            event_type = event['type']
            event_types[event_type] = event_types.get(event_type, 0) + 1

        tool_calls = [e for e in self.events if e['type'] == 'tool_call']
        escalations = [e for e in self.events if e['type'] == 'escalation']

        summary = f"""
        事件摘要報告
        {'='*70}

        總事件數：{total_events}

        事件類型：
        """

        for event_type, count in event_types.items():
            summary += f"  - {event_type}: {count}\n"

        summary += f"\n工具呼叫次數：{len(tool_calls)}\n"

        if tool_calls:
            summary += "  使用的工具：\n"
            tool_usage: Dict[str, int] = {}
            for call in tool_calls:
                tool = call['tool']
                tool_usage[tool] = tool_usage.get(tool, 0) + 1

            for tool, count in tool_usage.items():
                summary += f"    - {tool}: {count} 次呼叫\n"

        summary += f"\n上報次數：{len(escalations)}\n"

        if escalations:
            summary += "  上報原因：\n"
            for esc in escalations:
                summary += f"    - {esc['data']['reason']}\n"

        summary += f"\n{'='*70}"

        return summary

    def get_detailed_timeline(self) -> str:
        """取得詳細的事件時間軸。"""

        timeline = f"\n詳細事件時間軸\n{'='*70}\n"

        for i, event in enumerate(self.events, 1):
            timeline += f"\n[{i}] {event['timestamp']}\n"
            timeline += f"    類型：{event['type']}\n"

            if event['type'] == 'tool_call':
                timeline += f"    工具：{event['tool']}\n"
                timeline += f"    參數：{event['arguments']}\n"
            elif event['type'] in ['customer_query', 'agent_response', 'escalation']:
                for key, value in event['data'].items():
                    # 截斷過長的值
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:97] + "..."
                    timeline += f"    {key}: {value_str}\n"

        timeline += f"\n{'='*70}\n"

        return timeline


# 可觀測性輔助類別

class EventLogger:
    """用於結構化記錄的自訂事件記錄器。"""

    def __init__(self):
        self.logger = logging.getLogger('agent_events')
        self.logger.setLevel(logging.INFO)

    def log_event(self, event: Event):
        """使用結構化資料記錄事件。"""
        event_data = {
            'invocation_id': event.invocation_id,
            'author': event.author,
            'content': event.content.parts[0].text if event.content and event.content.parts else None,
            'actions': {
                'state_delta': event.actions.state_delta if event.actions else None,
                'escalate': event.actions.escalate if event.actions else None,
                'transfer_to_agent': event.actions.transfer_to_agent if event.actions else None
            }
        }
        self.logger.info(f"事件：{event_data}")


@dataclass
class AgentMetrics:
    """代理程式效能指標。"""
    invocation_count: int = 0
    total_latency: float = 0.0
    tool_call_count: int = 0
    error_count: int = 0
    escalation_count: int = 0


class MetricsCollector:
    """收集代理程式指標以進行監控。"""

    def __init__(self):
        self.metrics: Dict[str, AgentMetrics] = {}

    def track_invocation(
        self,
        agent_name: str,
        latency: float,
        tool_calls: int = 0,
        had_error: bool = False,
        escalated: bool = False
    ):
        """追蹤代理程式調用指標。"""

        if agent_name not in self.metrics:
            self.metrics[agent_name] = AgentMetrics()

        m = self.metrics[agent_name]
        m.invocation_count += 1
        m.total_latency += latency
        m.tool_call_count += tool_calls

        if had_error:
            m.error_count += 1
        if escalated:
            m.escalation_count += 1

    def get_summary(self, agent_name: str) -> Dict[str, Any]:
        """取得代理程式的指標摘要。"""

        if agent_name not in self.metrics:
            return {}

        m = self.metrics[agent_name]

        return {
            'invocations': m.invocation_count,
            'avg_latency': m.total_latency / m.invocation_count if m.invocation_count > 0 else 0,
            'total_tool_calls': m.tool_call_count,
            'error_rate': m.error_count / m.invocation_count if m.invocation_count > 0 else 0,
            'escalation_rate': m.escalation_count / m.invocation_count if m.invocation_count > 0 else 0
        }


class EventAlerter:
    """針對特定事件模式發出警報。"""

    def __init__(self):
        self.rules: List[tuple[Callable[[Event], bool], Callable[[Event], None]]] = []

    def add_rule(
        self,
        condition: Callable[[Event], bool],
        alert_fn: Callable[[Event], None]
    ):
        """新增警報規則。"""
        self.rules.append((condition, alert_fn))

    def check_event(self, event: Event):
        """根據所有規則檢查事件。"""
        for condition, alert_fn in self.rules:
            if condition(event):
                alert_fn(event)


async def main():
    """示範的主要進入點。"""

    print("\n" + "="*70)
    print("教學 18：事件與可觀測性示範")
    print("="*70)

    monitor = CustomerServiceMonitor()

    # 客戶 1：訂單狀態查詢
    await monitor.handle_customer_query(
        customer_id='CUST-001',
        query='我的訂單 ORD-001 的狀態是什麼？'
    )

    await asyncio.sleep(1)

    # 客戶 2：退款請求 (小額)
    await monitor.handle_customer_query(
        customer_id='CUST-002',
        query='我想要為訂單 ORD-002 申請 50 美元的退款'
    )

    await asyncio.sleep(1)

    # 客戶 3：退款請求 (大額 - 觸發上報)
    await monitor.handle_customer_query(
        customer_id='CUST-003',
        query='我需要為訂單 ORD-003 申請 150 美元的退款'
    )

    await asyncio.sleep(1)

    # 客戶 4：庫存檢查
    await monitor.handle_customer_query(
        customer_id='CUST-004',
        query='產品 PROD-B 有庫存嗎？'
    )

    # 產生報告
    print("\n" + monitor.get_event_summary())
    print(monitor.get_detailed_timeline())


# 建立實例並匯出 root_agent 以供 ADK 發現
_monitor_instance = None

def get_monitor():
    """取得或建立 CustomerServiceMonitor 實例。"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = CustomerServiceMonitor()
    return _monitor_instance

# 匯出 root_agent 以供 ADK 發現
root_agent = get_monitor().agent


if __name__ == '__main__':
    asyncio.run(main())
