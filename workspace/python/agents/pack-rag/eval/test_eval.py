# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
RAG 代理評估測試

重點摘要:
- **核心概念**: RAG 代理自動化評估
- **關鍵技術**: Pytest, AgentEvaluator, 異步測試
- **重要結論**: 透過 AgentEvaluator 自動執行對話測試案例，驗證 RAG 代理的基本能力
- **行動項目**:
  - <div style='text-align: left;'> 確認 `data/conversation.test.json` 測試資料集存在且格式正確</div>
"""

import pathlib

import dotenv
import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """
    載入環境變數。

    此 fixture 會在測試 session 開始時自動執行，負責載入 .env 檔案中的設定。
    這對於需要 API 金鑰或其他環境配置的測試至關重要。
    """
    # 使用 dotenv 載入 .env 檔案內容到環境變數中
    dotenv.load_dotenv()


@pytest.mark.asyncio
async def test_eval_full_conversation():
    """
    測試代理在少數範例上的基本能力。

    此測試使用 ADK 的 AgentEvaluator 來評估 'rag' 代理模組。
    它會讀取指定的測試資料集，並執行評估流程。

    流程圖:
    <div style='text-align: left;'>
    ```mermaid
    sequenceDiagram
        participant TestFunction as 測試函數
        participant AgentEvaluator as AgentEvaluator
        participant TestData as 測試資料(conversation.test.json)

        TestFunction->>TestData: 解析資料路徑
        TestFunction->>AgentEvaluator: 呼叫 evaluate (agent_module="rag")
        AgentEvaluator->>TestData: 讀取測試案例
        Note over AgentEvaluator: 執行代理評估 (num_runs=1)
        AgentEvaluator-->>TestFunction: 返回評估結果
    ```
    </div>
    """
    # 使用 AgentEvaluator 進行評估
    # agent_module="rag": 指定要評估的代理模組為 RAG
    # eval_dataset_file_path_or_dir: 指定測試資料的路徑 (data/conversation.test.json)
    # num_runs=1: 設定每個案例的執行次數為 1
    await AgentEvaluator.evaluate(
        agent_module="rag",
        eval_dataset_file_path_or_dir=str(
            pathlib.Path(__file__).parent / "data/conversation.test.json"
        ),
        num_runs=1,
    )
