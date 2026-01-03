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
客戶服務 Agent 評估測試模組
本檔案使用 Google ADK 的 AgentEvaluator 來驗證 Agent 的對話表現。
"""

import os

import pytest
from customer_service.config import Config
from dotenv import find_dotenv, load_dotenv
from google.adk.evaluation.agent_evaluator import AgentEvaluator

# 設定 pytest 插件，支援非同步測試
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """
    載入環境變數與設定
    - scope="session": 在整個測試會話中只執行一次
    - autouse=True: 自動應用於所有測試函數
    """
    load_dotenv(find_dotenv(".env"))
    c = Config()


@pytest.mark.asyncio
async def test_eval_simple():
    """
    簡單對話測試
    測試目標：驗證 Agent 處理基本請求的能力。
    使用資料：eval_data/simple.test.json
    重點說明：
    - AgentEvaluator.evaluate: 調用 ADK 評估器。
    - "customer_service": 指定要評估的 Agent 名稱。
    - num_runs=1: 執行次數，通常用於確保結果的穩定性。
    """
    await AgentEvaluator.evaluate(
        "customer_service",
        os.path.join(os.path.dirname(__file__), "eval_data/simple.test.json"),
        num_runs=1,
    )


@pytest.mark.asyncio
async def test_eval_full_conversation():
    """
    完整對話流程測試
    測試目標：驗證 Agent 在多輪對話中的上下文維持與邏輯判斷。
    使用資料：eval_data/full_conversation.test.json
    重點說明：
    - 這裡會載入更複雜的情境，檢查 Agent 是否能根據歷史對話提供正確回覆。
    """
    await AgentEvaluator.evaluate(
        "customer_service",
        os.path.join(
            os.path.dirname(__file__), "eval_data/full_conversation.test.json"
        ),
        num_runs=1,
    )
