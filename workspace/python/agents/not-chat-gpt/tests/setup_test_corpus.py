from google import genai
from google.genai import types
from pathlib import Path
from dotenv import load_dotenv
import os

# 載入環境變數
load_dotenv()

# 初始化 DocumentService
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment")

def setup_test_corpus():
    """設定測試用的文檔 corpus"""
    client = genai.Client(api_key=api_key)
    
    # 測試文檔路徑
    fixtures_dir = Path(__file__).parent / "fixtures"
    test_docs = [
        fixtures_dir / "company_policy.txt",
        fixtures_dir / "employee_handbook.txt",
        fixtures_dir / "project_guidelines.txt",
    ]
    
    uploaded_files = []
    
    print("📤 開始上傳測試文檔...")
    
    for doc_path in test_docs:
        if not doc_path.exists():
            print(f"⚠️  文檔不存在: {doc_path}")
            continue
        
        try:
            # 上傳文檔
            uploaded_file = client.files.upload(
                file=str(doc_path),
                config=types.UploadFileConfig(
                    display_name=doc_path.name
                )
            )
            
            uploaded_files.append({
                "name": uploaded_file.name,
                "display_name": uploaded_file.display_name,
                "uri": uploaded_file.uri,
            })
            
            print(f"✅ 已上傳: {uploaded_file.display_name}")
            print(f"   ID: {uploaded_file.name}")
            
        except Exception as e:
            print(f"❌ 上傳失敗 {doc_path.name}: {e}")
    
    print(f"\n📊 總共上傳 {len(uploaded_files)} 個文檔")
    return uploaded_files

def cleanup_test_corpus():
    """清理測試文檔"""
    client = genai.Client(api_key=api_key)
    
    print("🧹 清理測試文檔...")
    
    # 列出所有文檔
    files = list(client.files.list())
    
    for file in files:
        try:
            client.files.delete(name=file.name)
            print(f"🗑️  已刪除: {file.display_name}")
        except Exception as e:
            print(f"⚠️  刪除失敗 {file.display_name}: {e}")
    
    print("✅ 清理完成")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        cleanup_test_corpus()
    else:
        setup_test_corpus()