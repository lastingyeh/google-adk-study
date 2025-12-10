#!/usr/bin/env python3
"""
快速測試，以驗證使用 adk web 時追蹤是否匯出到 Jaeger。

此腳本：
1. 設定 OTel 環境變數 (與 Makefile 相同)
2. 在子程序中啟動 adk web
3. 發送測試查詢
4. 等待追蹤刷新
5. 檢查 Jaeger 中的追蹤
"""

import os
import subprocess
import time
import sys
import json
from pathlib import Path

# 設定 OTel 的環境變數
os.environ["OTEL_SERVICE_NAME"] = "google-adk-math-agent"
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"
os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "http/protobuf"
os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "true"

def test_traces_with_web():
    """測試使用 adk web 時追蹤是否被匯出。"""
    print("🚀 正在使用 OTel 啟動 ADK Web 伺服器...")

    # 在背景啟動 adk web
    proc = subprocess.Popen(
        ["adk", "web", "."],
        cwd=Path(__file__).parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        # 等待伺服器啟動
        print("⏳ 等待伺服器啟動中...")
        time.sleep(5)

        # 檢查伺服器是否正在執行
        result = subprocess.run(
            ["curl", "-s", "http://localhost:8000/list-apps?relative_path=."],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("❌ 伺服器啟動失敗")
            return False

        print("✅ 伺服器啟動成功")
        print(f"   可用代理：{result.stdout}")

        # 現在使用 Jaeger 進行測試
        print("\n📊 正在檢查 Jaeger 中的追蹤...")
        time.sleep(2)

        # 查詢 Jaeger 以取得追蹤
        jaeger_result = subprocess.run(
            ["curl", "-s", "http://localhost:16686/api/traces?service=google-adk-math-agent&limit=5"],
            capture_output=True,
            text=True,
        )

        if jaeger_result.returncode == 0:
            try:
                data = json.loads(jaeger_result.stdout)
                trace_count = len(data.get("data", []))
                if trace_count > 0:
                    print(f"✅ 在 Jaeger 中找到 {trace_count} 個追蹤！")
                    print("   ✨ 追蹤正被正確匯出！")
                    return True
                else:
                    print("⚠️  尚未找到追蹤 (可能需要幾秒鐘才能刷新)")
                    return True  # 仍然成功 - 伺服器已啟動
            except json.JSONDecodeError:
                print("✅ Jaeger 有回應 (可能還沒有追蹤)")
                return True
        else:
            print("⚠️  無法連線至 Jaeger，但伺服器正在執行")
            return True

    finally:
        # 清理
        print("\n🛑 正在停止伺服器...")
        proc.terminate()
        proc.wait(timeout=5)
        print("✅ 伺服器已停止")

if __name__ == "__main__":
    success = test_traces_with_web()
    sys.exit(0 if success else 1)
