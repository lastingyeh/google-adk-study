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

import os

from google.adk.tools.apihub_tool import apihub_toolset
from google.adk.tools.apihub_tool.clients import secret_client
from google.adk.tools.base_toolset import BaseToolset


class StubAPIHubToolset(BaseToolset):
    def __init__(self, *, name: str, description: str = "", **_kwargs):
        super().__init__()
        self.name = name
        self.description = description

    async def get_tools(self, readonly_context=None):
        return []


def _get_apikey_credential() -> str:
    env_apikey = os.getenv("CYMBAL_AUTO_APIKEY")
    if env_apikey:
        return env_apikey
    return "test-apikey"


apihub_toolset.APIHubToolset = StubAPIHubToolset
secret_client.SecretManagerClient.get_secret = (
    lambda self, name: _get_apikey_credential()
)
