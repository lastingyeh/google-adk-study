#!/bin/bash
# ============================================================================
# setup-vertex-ai.sh
#
# Configures the commerce agent to use Vertex AI authentication exclusively
# 將商務代理人設定為專門使用 Vertex AI 驗證
# Unsets any conflicting Gemini API keys
# 取消設定任何衝突的 Gemini API 金鑰
# ============================================================================

set -e

echo "🔐 Vertex AI Authentication Setup (Vertex AI 驗證設定)"
echo "================================="
echo ""

# Check if credentials file exists (檢查憑證檔案是否存在)
if [ ! -f "./credentials/commerce-agent-key.json" ]; then
    echo "❌ Error: Service account key not found at ./credentials/commerce-agent-key.json (錯誤：未在 ./credentials/commerce-agent-key.json 找到服務帳戶金鑰)"
    echo ""
    echo "To set up a service account key, run: (若要設定服務帳戶金鑰，請執行：)"
    echo "  See: log/20250124_173000_vertex_ai_setup_guide.md"
    exit 1
fi

echo "✅ Service account key found (已找到服務帳戶金鑰)"
echo ""

# Get project ID from credentials file (從憑證檔案取得專案 ID)
PROJECT_ID=$(jq -r '.project_id' ./credentials/commerce-agent-key.json)
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "null" ]; then
    echo "❌ Error: Could not read project_id from credentials file (錯誤：無法從憑證檔案讀取 project_id)"
    exit 1
fi

echo "✅ Project ID: $PROJECT_ID"
echo ""

# Unset Gemini API key if it exists (如果存在 Gemini API 金鑰，則取消設定)
if [ ! -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  Unsetting GOOGLE_API_KEY to avoid conflicts... (正在取消設定 GOOGLE_API_KEY 以避免衝突...)"
    unset GOOGLE_API_KEY
    echo "✅ GOOGLE_API_KEY unset (GOOGLE_API_KEY 已取消設定)"
    echo ""
fi

if [ ! -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Unsetting GEMINI_API_KEY to avoid conflicts... (正在取消設定 GEMINI_API_KEY 以避免衝突...)"
    unset GEMINI_API_KEY
    echo "✅ GEMINI_API_KEY unset (GEMINI_API_KEY 已取消設定)"
    echo ""
fi

# Set Vertex AI credentials (設定 Vertex AI 憑證)
export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials/commerce-agent-key.json"

echo "✅ Environment variables set for Vertex AI: (已為 Vertex AI 設定環境變數：)"
echo "   GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT"
echo "   GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS"
echo ""

# Verify credentials work (驗證憑證是否運作)
echo "🔍 Verifying credentials... (正在驗證憑證...)"
python3 << 'VERIFY_CREDS'
import os
import json
import sys

project = os.getenv('GOOGLE_CLOUD_PROJECT')
creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

if not project or not creds_path:
    print("❌ Environment variables not set (環境變數未設定)")
    sys.exit(1)

if not os.path.exists(creds_path):
    print(f"❌ Credentials file not found (憑證檔案未找到): {creds_path}")
    sys.exit(1)

try:
    with open(creds_path, 'r') as f:
        creds = json.load(f)

    if creds.get('project_id') != project:
        print(f"⚠️  Project ID mismatch (專案 ID 不符): {project} vs {creds.get('project_id')}")

    print(f"✅ Credentials verified (憑證已驗證):")
    print(f"   Service Account (服務帳戶): {creds.get('client_email')}")
    print(f"   Type (類型): {creds.get('type')}")
    print(f"   Project (專案): {creds.get('project_id')}")

except Exception as e:
    print(f"❌ Error reading credentials (讀取憑證時發生錯誤): {e}")
    sys.exit(1)
VERIFY_CREDS

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Credential verification failed (憑證驗證失敗)"
    exit 1
fi

echo ""
echo "✅ Vertex AI Setup Complete! (Vertex AI 設定完成！)"
echo ""
echo "To make these settings permanent, add to your ~/.zshrc: (若要使這些設定永久生效，請新增至您的 ~/.zshrc：)"
echo ""
echo "  export GOOGLE_CLOUD_PROJECT=\"$PROJECT_ID\""
echo "  export GOOGLE_APPLICATION_CREDENTIALS=\"$(pwd)/credentials/commerce-agent-key.json\""
echo ""
echo "Then run: source ~/.zshrc (然後執行：source ~/.zshrc)"
echo ""
echo "Ready to start the agent: (準備啟動代理人：)"
echo "  make dev"
echo ""
