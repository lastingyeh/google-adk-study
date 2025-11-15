#!/usr/bin/env python3
"""針對 Vertex AI 文字 API 連線能力的快速煙霧測試。"""

import os
import sys
from google.genai import Client, types

# 從環境變數中獲取專案 ID
project = os.environ['GOOGLE_CLOUD_PROJECT']
# 從環境變數中獲取地區，預設為 'us-central1'
location = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
# 從環境變數中獲取模型名稱，預設為 'gemini-2.5-flash'
model = os.environ.get('VOICE_ASSISTANT_TEXT_MODEL', 'gemini-2.5-flash')

try:
    # 初始化 Vertex AI 客戶端
    client = Client(vertexai=True, project=project, location=location)
    # 產生內容以測試 API 連線
    response = client.models.generate_content(
        model=model,
        contents=[types.Content(role='user', parts=[types.Part.from_text(text='ping')])]
    )
except Exception as exc:
    # 如果測試失敗，輸出錯誤訊息並退出
    print(f'   ❌ Live 煙霧測試失敗：{exc}')
    sys.exit(1)

text = ''
# 從回應中提取生成的文字
for candidate in getattr(response, 'candidates', []) or []:
    content = getattr(candidate, 'content', None)
    if not content:
        continue
    for part in getattr(content, 'parts', []) or []:
        value = getattr(part, 'text', None)
        if value:
            text += value
    if text:
        break

# 輸出成功訊息
print('   ✅ Vertex 文字 API 可連線。')
if text:
    # 顯示部分回應內容
    preview = text.replace('\n', ' ')[:120]
    print(f'   ↪ 回應範例：{preview}')
