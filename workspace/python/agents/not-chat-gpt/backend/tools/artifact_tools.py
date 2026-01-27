import os

from typing import Dict, Any
from google.genai import types
from google.adk.tools.tool_context import ToolContext

async def save_artifact(
    file_name: str,
    file_data: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """儲存檔案為 Artifact。目前僅支援文字形式檔案，如 .md 和 .txt。
    如果檔案名稱以 "user:" 為前綴，例如 "user:profile.md" ，
    則該工件僅與 app_name 和 user_id 關聯。
    可以在應用程式內屬於該使用者的任何會話中存取或更新它。
    
    Args:
        file_name: 檔案名稱 (包含副檔名)
        file_data: 檔案內容 (字串形式)
        tool_context: 工具上下文
        
    Returns:
        包含儲存結果的字典
    """
    # file_mime_type = _get_mime_type(file_name)
    artifact = types.Part.from_text(text=file_data)
    version = await tool_context.save_artifact(file_name, artifact)
    return {
        "status": "success",
        "file_name": file_name,
        "version": version,
        "message": f"已成功儲存檔案 '{file_name}' 為 Artifact，版本: {version}"
    }

async def load_artifact(
    file_name: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """載入 Artifact 檔案內容。
    
    Args:
        file_name: 檔案名稱
        tool_context: 工具上下文
        
    Returns:
        包含檔案內容的字典
    """
    file_data = await tool_context.load_artifact(file_name)
    return {
        "status": "success",
        "file_name": file_name,
        "file_data": file_data,
        "message": f"已成功載入 Artifact 檔案 '{file_name}'"
    }

async def list_artifacts(
    tool_context: ToolContext
) -> Dict[str, Any]:
    """列出所有 Artifact 檔案名稱。
    
    Args:
        tool_context: 工具上下文
        
    Returns:
        包含檔案名稱列表的字典
    """
    filenames = await tool_context.list_artifacts()
    return {
        "status": "success",
        "files": filenames,
        "message": f"已成功列出 {len(filenames)} 個 Artifact 檔案"
    }

def _get_mime_type(file_name: str) -> str:
    """Determines the MIME type based on the file extension."""
    extension = os.path.splitext(file_name)[1].lower()
    if extension == ".md":
        return "text/markdown"
    elif extension == ".txt":
        return "text/plain"
    else:
        raise ValueError(f"Unsupported file type: {extension}. Only .md and .txt are supported.")

ARTIFACT_TOOLS = [save_artifact, load_artifact, list_artifacts]
