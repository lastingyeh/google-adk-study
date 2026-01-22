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

# ==========================================
# 重點摘要
# ==========================================
# - 核心概念：此模組負責建立與 Google Cloud Apigee API Hub 整合的工具集，供代理人調用外部 API。
# - 關鍵技術：
#     - APIHubToolset: Google ADK 提供的組件，用於將 API Hub 中的 API 規格動態轉換為代理人可用的工具。
#     - Secret Manager: 使用 `SecretManagerClient` 安全地從雲端獲取 API Key。
#     - OpenAPI Auth Helpers: 將獲取的 API Key 轉換為 OpenAPI 規範的驗證架構（此處使用 header 中的 x-apikey）。
# - 重要結論：透過 API Hub 與 ADK 的整合，開發者無需手動定義每個 API 的參數，即可讓 AI 代理人具備操作企業現有 API 的能力。
# - 行動項目：
#     - 確保 Google Cloud 專案中已建立名為 `cymbal-auto-apikey` 的 Secret。
#     - 確認 API Hub 中對應的 API 資源路徑（如 `members_api`, `claims_api` 等）正確無誤。
import os

from dotenv import load_dotenv
from google.adk.tools.apihub_tool.apihub_toolset import APIHubToolset
from google.adk.tools.apihub_tool.clients.secret_client import (
    SecretManagerClient,
)
from google.adk.tools.openapi_tool.auth.auth_helpers import (
    token_to_scheme_credential,
)

# 載入環境變數
load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
API_HUB_LOCATION = f"projects/{PROJECT_ID}/locations/{LOCATION}/apis"
SECRET = f"projects/{PROJECT_ID}/secrets/cymbal-auto-apikey/versions/latest"

# 獲取 Cymbal Auto APIs 的憑證
# Get the credentials for the Cymbal Auto APIs
env_apikey = os.getenv("CYMBAL_AUTO_APIKEY")
if env_apikey:
    apikey_credential_str = env_apikey
else:
    secret_manager_client = SecretManagerClient()
    apikey_credential_str = secret_manager_client.get_secret(SECRET)
auth_scheme, auth_credential = token_to_scheme_credential(
    "apikey", "header", "x-apikey", apikey_credential_str
)

# 會員管理 API
# Membership API
membership = APIHubToolset(
    name="cymbal-auto-membership-api",
    description="Member Account Management API",  # 會員帳戶管理 API
    apihub_resource_name=f"{API_HUB_LOCATION}/members_api",
    auth_scheme=auth_scheme,
    auth_credential=auth_credential,
)

# 理賠處理 API
# Claims API
claims = APIHubToolset(
    name="cymbal-auto-claims-api",
    description="Claims API",  # 理賠 API
    apihub_resource_name=f"{API_HUB_LOCATION}/claims_api",
    auth_scheme=auth_scheme,
    auth_credential=auth_credential,
)

# 道路救援 API
# Roadside API
roadsideAssistance = APIHubToolset(
    name="cymbal-auto-roadside-assistance-api",
    description="Roadside Assistance API",  # 道路救援 API
    apihub_resource_name=f"{API_HUB_LOCATION}/roadside_api",
    auth_scheme=auth_scheme,
    auth_credential=auth_credential,
)

# 獎勵優惠 API
# Rewards API
rewards = APIHubToolset(
    name="cymbal-auto-rewards-api",
    description="Rewards API",  # 獎勵 API
    apihub_resource_name=f"{API_HUB_LOCATION}/rewards_api",
    auth_scheme=auth_scheme,
    auth_credential=auth_credential,
)
