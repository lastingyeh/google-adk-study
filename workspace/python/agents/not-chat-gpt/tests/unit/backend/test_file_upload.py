import pytest
import os
from google.genai import types

class TestFileUpload:
    """測試文檔上傳與內容查詢功能"""
    
    def test_file_upload_and_content_query(self, genai_client, model_name):
        """測試上傳文檔並查詢其內容"""
        # 1. 確保測試文檔存在
        fixtures_path = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures")
        sample_doc_path = os.path.join(fixtures_path, "sample_doc.txt")
        
        if not os.path.exists(sample_doc_path):
            pytest.skip(f"測試文檔不存在: {sample_doc_path}")
        
        # 2. 上傳測試文檔
        test_file = genai_client.files.upload(
            file=sample_doc_path,
            config=types.UploadFileConfig(display_name="Test Document")
        )
        print(f"✅ 文檔已上傳: {test_file.name}")
        print(f"   URI: {test_file.uri}")
        print(f"   MIME類型: {test_file.mime_type}")
        
        try:
            # 3. 使用上傳的文檔進行查詢
            response = genai_client.models.generate_content(
                model=model_name,
                contents=[
                    types.Part.from_uri(
                        file_uri=test_file.uri,
                        mime_type=test_file.mime_type
                    ),
                    "這份文檔的主要內容是什麼？請用繁體中文回答。"
                ]
            )
            
            # 4. 驗證回應
            assert response.text is not None, "回應不應為空"
            assert len(response.text) > 0, "回應長度應大於 0"
            print(f"✅ 查詢成功")
            print(f"   回應: {response.text[:200]}...")
            
        finally:
            # 5. 清理：刪除測試文檔
            try:
                genai_client.files.delete(name=test_file.name)
                print("✅ 測試文檔已刪除")
            except Exception as e:
                print(f"⚠️  清理警告: {e}")
    
    def test_file_list_and_get(self, genai_client):
        """測試列出和獲取文檔資訊"""
        fixtures_path = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures")
        sample_doc_path = os.path.join(fixtures_path, "sample_doc.txt")
        
        if not os.path.exists(sample_doc_path):
            pytest.skip(f"測試文檔不存在: {sample_doc_path}")
        
        # 上傳文檔
        test_file = genai_client.files.upload(
            file=sample_doc_path,
            config=types.UploadFileConfig(display_name="List Test Document")
        )
        
        try:
            # 列出所有文檔
            files_list = list(genai_client.files.list())
            assert len(files_list) > 0, "應該至少有一個文檔"
            print(f"✅ 文檔列表: {len(files_list)} 個文檔")
            
            # 獲取特定文檔資訊
            retrieved_file = genai_client.files.get(name=test_file.name)
            assert retrieved_file.name == test_file.name
            assert retrieved_file.display_name == "List Test Document"
            print(f"✅ 文檔資訊獲取成功")
            
        finally:
            genai_client.files.delete(name=test_file.name)
            print("✅ 測試文檔已刪除")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])