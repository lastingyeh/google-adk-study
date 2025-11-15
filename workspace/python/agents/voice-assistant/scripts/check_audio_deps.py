#!/usr/bin/env python3
"""檢查音訊相關的依賴套件是否可用。"""

import importlib.util
import sys

# 檢查 'pyaudio' 和 'numpy' 是否已安裝
missing = [m for m in ('pyaudio', 'numpy') if importlib.util.find_spec(m) is None]

# 如果有任何缺少的套件
if missing:
    # 輸出錯誤訊息，列出缺少的套件
    print('   ❌ 缺少音訊套件：' + ', '.join(missing))
    # 提供安裝指令
    print('   👉 請使用此指令安裝：pip install pyaudio numpy')
    # 提供平台特定說明的參考文件
    print('   👉 請參閱 AUDIO_SETUP.md 以獲取平台特定的安裝說明')
    # 退出程式，返回錯誤碼 1
    sys.exit(1)

# 如果所有依賴都已安裝，輸出成功訊息
print('   ✅ 音訊依賴套件皆已安裝。')
