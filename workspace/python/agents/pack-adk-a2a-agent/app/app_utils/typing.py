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
import uuid
from typing import (
    Literal,
)

from google.adk.events.event import Event
from google.genai.types import Content
from pydantic import (
    BaseModel,
    Field,
)


class Request(BaseModel):
    """表示帶有可選配置的聊天請求輸入。"""

    message: Content
    events: list[Event]
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    model_config = {"extra": "allow"}


class Feedback(BaseModel):
    """表示對話的回饋。"""

    score: int | float
    text: str | None = ""
    log_type: Literal["feedback"] = "feedback"
    service_name: Literal["pack-adk-a2a-agent"] = "pack-adk-a2a-agent"
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
