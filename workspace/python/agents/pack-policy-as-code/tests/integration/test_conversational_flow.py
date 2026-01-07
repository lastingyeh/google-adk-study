"""Policy-as-code 代理的對話流程整合測試。"""

import pytest
from google.adk.agents import Agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from policy_as_code_agent import agent as agent_module

# --- Mock 工具 ---


def mock_find_policy_in_memory(query: str, source: str, **kwargs) -> dict:
    """模擬尋找策略。"""
    return {"status": "not_found", "message": "No policy found (mock)."}


def mock_generate_policy_code_from_gcs(query: str, gcs_uri: str) -> dict:
    """模擬生成策略程式碼。"""
    return {
        "status": "success",
        "policy_code": "def check_policy(metadata):\n    return []",
    }


def mock_save_policy_to_memory(
    natural_language_query: str, policy_code: str, source: str, **kwargs
) -> dict:
    """模擬儲存策略。"""
    return {"status": "success", "policy_id": "mock_id", "version": 1}


def mock_run_policy_from_gcs(policy_code: str, gcs_uri: str, **kwargs) -> dict:
    """模擬執行策略。"""
    return {
        "status": "success",
        "report": {
            "violations_found": True,
            "violations": [{"violation": "Mock violation"}],
            "message": "Mock run complete.",
        },
    }


# 建立帶有模擬工具的測試代理的輔助函數
def create_test_agent() -> Agent:
    # 我們需要保留原始工具名稱，以便 LLM 知道根據說明呼叫什麼。

    # 建立原始工具名稱到模擬函數的對映
    mocks = {
        "find_policy_in_memory": mock_find_policy_in_memory,
        "generate_policy_code_from_gcs": mock_generate_policy_code_from_gcs,
        "save_policy_to_memory": mock_save_policy_to_memory,
        "run_policy_from_gcs": mock_run_policy_from_gcs,
    }

    new_tools = []
    for tool in agent_module.root_agent.tools:
        tool_name = getattr(tool, "__name__", None)
        if tool_name and tool_name in mocks:
            # 使用模擬，但確保它具有正確的名稱和 docstring
            # (ADK 可能使用 docstrings 進行工具定義)
            mock = mocks[tool_name]
            mock.__name__ = tool_name
            mock.__doc__ = tool.__doc__  # 從原始複製 docstring
            new_tools.append(mock)  # type: ignore[arg-type]
        else:
            new_tools.append(tool)  # type: ignore[arg-type]

    return Agent(
        name="test_policy_agent",
        model="gemini-2.5-flash",
        description=agent_module.root_agent.description,
        instruction=agent_module.root_agent.instruction,
        tools=new_tools,  # type: ignore[arg-type]
    )


@pytest.fixture
def runner() -> Runner:
    return Runner(
        app_name="test-conversation",
        agent=create_test_agent(),
        session_service=InMemorySessionService(),
        artifact_service=InMemoryArtifactService(),
    )


@pytest.mark.asyncio
async def test_conversational_policy_creation(runner: Runner) -> None:
    """
    測試多輪對話，使用者要求從 GCS 建立策略，
    且代理遵循正確的步驟 (尋找 -> 生成 -> 儲存 -> 執行)。
    """
    user_id = "test-user"
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id=user_id
    )
    session_id = session.id

    # 第一輪：使用者問候 / 意圖
    # 預期代理詢問來源。
    response_text = await send_message(
        runner, user_id, session_id, "I want to check if table descriptions exist."
    )
    # 我們無法嚴格斷言確切的文字，但我們可以檢查它是否提到了 "GCS" 或 "Dataplex"
    # 或者如果尚未呼叫工具 (因為我們尚未提供來源)。
    # 但模型可能會急切地假設來源或使用未知來源呼叫 'find'。
    # 如果需要，讓我們列印它以進行除錯，或檢查流程。

    # 第二輪：使用者提供來源
    response_text = await send_message(runner, user_id, session_id, "Use GCS.")

    # 代理現在應該嘗試尋找策略。我們的模擬返回 "not_found"。
    # 然後它應該詢問 GCS URI (因為它需要它來生成)。

    # 第三輪：使用者提供 URI
    response_text = await send_message(
        runner, user_id, session_id, "gs://my-bucket/metadata.jsonl"
    )

    # 現在代理應該：
    # 1. 呼叫 generate_policy_code_from_gcs
    # 2. 呼叫 save_policy_to_memory
    # 3. 呼叫 run_policy_from_gcs
    # 4. 報告結果。

    assert (
        "Mock violation" in response_text or "violations found" in response_text.lower()
    ), f"Agent response did not contain expected mock result. Got: {response_text}"


async def send_message(runner: Runner, user_id: str, session_id: str, text: str) -> str:
    """發送訊息並取得最終文字回應的輔助函數。"""
    input_content = types.UserContent(text)
    response_parts = []

    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=input_content
    ):
        if event.content:
            for part in event.content.parts:  # type: ignore[union-attr]
                if part.text:
                    response_parts.append(part.text)

    return "".join(response_parts)
