# Copyright 2026 Google LLC
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

import os
import tempfile

from google.adk import Agent
from google.adk.tools.computer_use.computer_use_toolset import ComputerUseToolset

from .playwright import PlaywrightComputer

# ---------- 瀏覽器使用者設定資料資料夾（profile）設定 ----------
# 為瀏覽器指定一個固定的 user data 目錄，這可用於保留 cookie、登入狀態、擴充套件等。
profile_name = "browser_profile_for_adk"
# 使用系統暫存目錄作為基底路徑，避免硬編碼絕對路徑，並在不同平台上具備可移植性。
profile_path = os.path.join(tempfile.gettempdir(), profile_name)
# 若路徑不存在則建立，exist_ok=True 以避免在已存在時拋出例外。
os.makedirs(profile_path, exist_ok=True)

# ---------- 建立可操作的電腦/瀏覽器實例 ----------
# 使用自訂的 PlaywrightComputer，並將 user_data_dir 指向剛建立的設定資料夾。
# screen_size 可調整為測試或使用需求所需的分辨率。
computer_with_profile = PlaywrightComputer(
    screen_size=(1280, 936),
    user_data_dir=profile_path,
)

# ---------- 建立 Agent 並注入 ComputerUse 工具集 ----------
# Agent 會使用指定的模型與工具集來執行「操作電腦/瀏覽器」相關的任務。
root_agent = Agent(
    model="gemini-2.5-computer-use-preview-10-2025",
    name="hello_world_agent",
    description=("可在電腦上操作瀏覽器以完成使用者任務的電腦使用代理"),
    instruction="""你是一個電腦使用代理。""",
    # 將 ComputerUseToolset 加入 tools，並傳入先前建立的 computer 實例。
    tools=[ComputerUseToolset(computer=computer_with_profile)],
)

if __name__ == "__main__":
    # 提示使用者已成功建立代理以及使用中的瀏覽器設定資料夾路徑。
    print("已建立代理：hello_world_agent")
    print("描述：電腦使用代理，可操作瀏覽器完成使用者任務。")
    print(f"瀏覽器使用者設定資料夾：{profile_path}")
    print("說明：代理已初始化並包含 ComputerUseToolset。")
    # 說明如何啟動互動（具體方法依 ADK 文件與程式流程而定）
    print(
        "要啟動互動，請依照 ADK 文件呼叫適當方法，例如 root_agent.run(task) 或 root_agent.listen()。"
    )
