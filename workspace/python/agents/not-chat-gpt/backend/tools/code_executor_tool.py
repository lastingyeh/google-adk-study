import os
from google.adk.agents import Agent
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools.agent_tool import AgentTool

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3-flash-preview")

code_executor_agent = Agent(
    model=MODEL_NAME,
    name='code_executor_agent',
    instruction='你可以編寫並執行 Python 程式碼。',
    code_executor=BuiltInCodeExecutor()  # ← 新功能
)

CODE_EXECUTOR_AGENT_TOOL = AgentTool(code_executor_agent)
