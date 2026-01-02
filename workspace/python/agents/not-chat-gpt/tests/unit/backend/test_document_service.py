import pytest
from google import genai
from backend.services.document_service import DocumentService
import os
from pathlib import Path

class TestDocumentService:
    """測試文檔管理服務"""
    
    @pytest.fixture
    def genai_client(self):
        """建立 Gemini 客戶端"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")
        return genai.Client(api_key=api_key)
    
    @pytest.fixture
    def doc_service(self, genai_client):
        """建立 DocumentService (使用記憶體資料庫)"""
        return DocumentService(genai_client, database_url="sqlite:///:memory:")
    
    def test_upload_document(self, doc_service):
        """測試文檔上傳功能"""
        # 確保測試文檔存在
        test_file = Path("tests/fixtures/sample_doc.txt")
        if not test_file.exists():
            pytest.skip("測試文檔不存在")
        
        # 上傳文檔
        result = doc_service.upload_document(
            file_path=str(test_file),
            display_name="Test Document"
        )
        
        # 驗證結果
        assert "id" in result, "應返回文檔 ID"
        assert "name" in result, "應返回文檔名稱"
        assert result["name"] == "Test Document"
        assert "uri" in result, "應返回文檔 URI"
        
        print(f"\n✅ 文檔上傳成功:")
        print(f"   ID: {result['id']}")
        print(f"   URI: {result['uri']}")
        
        # 清理
        try:
            doc_service.delete_document(result["id"])
        except:
            pass
    
    def test_list_documents(self, doc_service):
        """測試文檔列表功能"""
        test_file = Path("tests/fixtures/sample_doc.txt")
        if not test_file.exists():
            pytest.skip("測試文檔不存在")
        
        # 上傳文檔
        result = doc_service.upload_document(str(test_file), "List Test Doc")
        doc_id = result["id"]
        
        try:
            # 列出文檔
            docs = doc_service.list_documents()
            assert len(docs) >= 1, "應至少有一個文檔"
            
            # 驗證文檔存在於列表中
            doc_names = [d["name"] for d in docs]
            assert "List Test Doc" in doc_names
            
            print(f"\n✅ 文檔列表: {len(docs)} 個文檔")
            
        finally:
            # 清理
            doc_service.delete_document(doc_id)
    
    def test_get_document(self, doc_service):
        """測試獲取單一文檔資訊"""
        test_file = Path("tests/fixtures/sample_doc.txt")
        if not test_file.exists():
            pytest.skip("測試文檔不存在")
        
        # 上傳文檔
        result = doc_service.upload_document(str(test_file), "Get Test Doc")
        doc_id = result["id"]
        
        try:
            # 獲取文檔資訊
            doc_info = doc_service.get_document(doc_id)
            
            assert doc_info is not None, "應返回文檔資訊"
            assert doc_info["id"] == doc_id
            assert doc_info["name"] == "Get Test Doc"
            
            print(f"\n✅ 文檔資訊獲取成功:")
            print(f"   名稱: {doc_info['name']}")
            print(f"   大小: {doc_info['size']} bytes")
            
        finally:
            # 清理
            doc_service.delete_document(doc_id)
    
    def test_delete_document(self, doc_service):
        """測試文檔刪除功能"""
        test_file = Path("tests/fixtures/sample_doc.txt")
        if not test_file.exists():
            pytest.skip("測試文檔不存在")
        
        # 上傳文檔
        result = doc_service.upload_document(str(test_file), "Delete Test Doc")
        doc_id = result["id"]
        
        # 刪除文檔
        doc_service.delete_document(doc_id)
        
        # 驗證文檔已刪除
        doc_info = doc_service.get_document(doc_id)
        assert doc_info is None, "文檔應已被刪除"
        
        print("\n✅ 文檔刪除成功")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])