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

"""
### 翻譯內容
# 版權所有 2026 Google LLC
#
# 根據 Apache 許可證 2.0 版（"許可證"）獲得許可；
# 除非遵守許可證，否則您不得使用此檔案。
# 您可以在以下網址獲得許可證副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據許可證分發的軟體
# 是按「現狀」分發的，不附帶任何明示或暗示的保證或條件。
# 請參閱許可證以瞭解管理許可證下的權限和限制的特定語言。

### 重點摘要
- **核心概念**：初始化 `a2a_human_in_loop` 套件。
- **關鍵技術**：使用 Python 的相對導入（Relative Import）機制。
- **重要結論**：該檔案作為套件進入點，確保 `agent` 模組可被外部存取。
- **行動項目**：無。
"""

# 從當前目錄導入 agent 模組
from . import agent
