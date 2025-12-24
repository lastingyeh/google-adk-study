"""
ADK 教學 19：Artifacts與檔案管理

此代理程式展示了用於文件處理工作流程的全面Artifacts儲存、版本控制和檢索功能。

功能：
- 文件文字提取與儲存
- 帶有Artifacts版本控制的摘要功能
- 多語言翻譯
- 結合所有Artifacts生成最終報告
- 用於對話式存取的內建Artifacts載入工具
"""

from typing import Dict, Any, Optional
from google.adk.agents import Agent
from google.adk.tools.load_artifacts_tool import load_artifacts_tool
from google.adk.tools.tool_context import ToolContext
from google.genai import types


async def extract_text_tool(document_content: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    將文件文字提取並儲存為Artifacts。

    此工具接收原始文件內容，進行處理，並將提取的文字
    儲存為版本化的Artifacts以供將來參考。

    Args:
        document_content: 要處理和儲存的原始文件文字。

    Returns:
        包含狀態、報告和提取文字資訊的字典。
    """
    try:
        # 基本的文字提取（在實際應用中，這可能涉及
        # PDF 解析、OCR 或其他文件處理）
        extracted_text = document_content.strip()

        # 驗證提取的內容
        if not extracted_text:
            return {
                'status': 'error',
                'error': '文件中找不到文字內容',
                'report': '從文件中提取文字失敗'
            }

        # 創建Artifacts部分
        text_part = types.Part.from_text(text=extracted_text)

        # 另存為Artifacts
        version = await tool_context.save_artifact(
            filename='document_extracted.txt',
            artifact=text_part
        )

        return {
            'status': 'success',
            'report': f'成功提取 {len(extracted_text)} 個字元的文字並儲存為版本 {version}',
            'data': {
                'filename': 'document_extracted.txt',
                'version': version,
                'content': extracted_text,
                'word_count': len(extracted_text.split()),
                'character_count': len(extracted_text)
            }
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'提取文件文字失敗：{str(e)}'
        }


async def summarize_document_tool(document_text: Optional[str], tool_context: ToolContext) -> Dict[str, Any]:
    """
    生成文件摘要並將其儲存為Artifacts。

    為提供的文件文字創建簡潔的摘要，並將其儲存為
    版本化的Artifacts。如果未提供文字，則嘗試載入
    最近提取的文件。

    Args:
        document_text: 要摘要的文字（可選 - 若未提供則從Artifacts中載入）。
        tool_context: 用於Artifacts操作的工具上下文。

    Returns:
        包含狀態、報告和摘要資訊的字典。
    """
    try:
        # 如果未提供文字，嘗試載入提取的文件
        if not document_text:
            artifact = await tool_context.load_artifact('document_extracted.txt')
            if artifact and artifact.text:
                document_text = artifact.text
            else:
                return {
                    'status': 'error',
                    'error': '未提供文件文字',
                    'report': '請提供文件文字或確保提取的文字可用'
                }

        # 基本的摘要功能（在實務中，這會使用大型語言模型）
        words = document_text.split()
        if len(words) <= 50:
            summary = document_text
        else:
            summary = ' '.join(words[:50]) + '...'

        # 創建Artifacts部分
        summary_part = types.Part.from_text(text=summary)

        # 另存為Artifacts
        version = await tool_context.save_artifact(
            filename='document_summary.txt',
            artifact=summary_part
        )

        return {
            'status': 'success',
            'report': f'已生成摘要（{len(summary)} 個字元）並儲存為版本 {version}',
            'data': {
                'filename': 'document_summary.txt',
                'version': version,
                'content': summary,
                'original_length': len(document_text),
                'summary_length': len(summary)
            }
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'生成文件摘要失敗：{str(e)}'
        }


async def translate_document_tool(text: str, target_language: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    將文件文字翻譯成目標語言並儲存為Artifacts。

    Args:
        text: 要翻譯的文字。
        target_language: 目標語言（例如：'Spanish', 'French', 'German'）。
        tool_context: 用於Artifacts操作的工具上下文。

    Returns:
        包含狀態、報告和翻譯資訊的字典。
    """
    try:
        if not text:
            return {
                'status': 'error',
                'error': '未提供用於翻譯的文字',
                'report': '請提供要翻譯的文字'
            }

        # 基本的翻譯模擬（在實務中，這會使用翻譯 API）
        # 為示範目的，我們僅將文字標記為「已翻譯」
        translated_text = f"[翻譯至 {target_language}] {text}"

        # 創建Artifacts部分
        translation_part = types.Part.from_text(text=translated_text)

        # 另存為Artifacts
        filename = f'document_{target_language.lower()}.txt'
        version = await tool_context.save_artifact(
            filename=filename,
            artifact=translation_part
        )

        return {
            'status': 'success',
            'report': f'已將 {len(text)} 個字元翻譯成 {target_language} 並儲存為版本 {version}',
            'data': {
                'filename': filename,
                'version': version,
                'content': translated_text,
                'source_language': 'English',
                'target_language': target_language
            }
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'翻譯文件失敗：{str(e)}'
        }


async def create_final_report_tool(tool_context: ToolContext) -> Dict[str, Any]:
    """
    創建一份結合所有文件Artifacts的綜合最終報告。

    生成一份最終報告，該報告引用並結合所有已處理的
    文件Artifacts，成為一份單一的綜合文件。

    Args:
        tool_context: 用於Artifacts操作的工具上下文。

    Returns:
        包含狀態、報告和最終報告資訊的字典。
    """
    try:
        # 載入所有Artifacts
        all_artifacts = await tool_context.list_artifacts()

        # 建立報告內容
        report_content = """# 文件處理最終報告

## 處理摘要

本報告結合了當前會話中的所有文件處理Artifacts。

## 已處理的Artifacts

"""

        artifacts_list = []
        for filename in all_artifacts:
            if filename.startswith('document_') and not filename.endswith('FINAL_REPORT.md'):
                artifact = await tool_context.load_artifact(filename)
                if artifact:
                    report_content += f"- {filename}: {len(artifact.text)} 個字元\n"
                    artifacts_list.append(filename)

        report_content += """
## 建議

所有文件處理已成功完成。Artifacts均已版本化並
可供將來參考。

## 後續步驟

- 檢閱個別Artifacts以獲取詳細內容
- 如有需要，生成額外的翻譯
- 封存或匯出最終結果
"""

        # 創建Artifacts部分
        report_part = types.Part.from_text(text=report_content)

        # 另存為Artifacts
        version = await tool_context.save_artifact(
            filename='document_FINAL_REPORT.md',
            artifact=report_part
        )

        return {
            'status': 'success',
            'report': f'已生成結合 {len(artifacts_list)} 個Artifacts的綜合最終報告（版本 {version}）',
            'data': {
                'filename': 'document_FINAL_REPORT.md',
                'version': version,
                'content': report_content,
                'artifacts_combined': artifacts_list
            }
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'創建最終報告失敗：{str(e)}'
        }


async def list_artifacts_tool(tool_context: ToolContext) -> Dict[str, Any]:
    """
    列出當前會話中所有可用的Artifacts。

    Args:
        tool_context: 用於Artifacts操作的工具上下文。

    Returns:
        包含狀態、報告和可用Artifacts列表的字典。
    """
    try:
        # 從Artifacts服務中載入所有Artifacts
        artifacts = await tool_context.list_artifacts()

        return {
            'status': 'success',
            'report': f'找到 {len(artifacts)} 個Artifacts',
            'data': {
                'artifacts': artifacts,
                'count': len(artifacts)
            }
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'列出Artifacts失敗：{str(e)}'
        }


async def load_artifact_tool(filename: str, tool_context: ToolContext, version: Optional[int] = None) -> Dict[str, Any]:
    """
    按檔名和可選的版本號載入特定Artifact。

    Args:
        filename: 要載入的Artifact名稱。
        tool_context: 用於Artifact操作的工具上下文。
        version: 要載入的特定版本（可選 - 若未指定則載入最新版本）。

    Returns:
        包含狀態、報告和Artifact內容的字典。
    """
    try:
        if not filename:
            return {
                'status': 'error',
                'error': '未提供檔名',
                'report': '請指定要載入的Artifact檔名'
            }

        # 從Artifacts服務中載入Artifacts
        artifact = await tool_context.load_artifact(filename, version=version)

        if not artifact:
            return {
                'status': 'error',
                'error': f'找不到Artifacts {filename}',
                'report': f'找不到Artifacts {filename}' + (f' 版本 {version}' if version else '')
            }

        return {
            'status': 'success',
            'report': f'已載入Artifacts {filename}' + (f' 版本 {version}' if version else ' (最新)'),
            'data': {
                'filename': filename,
                'version': version,
                'content': artifact.text if artifact.text else '[二進位內容]'
            }
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'載入Artifacts {filename} 失敗：{str(e)}'
        }


def main():
    """直接執行代理程式的主要進入點。"""
    import asyncio
    from google.adk.runners import Runner
    from google.adk.artifacts import InMemoryArtifactService
    from google.adk.sessions import InMemorySessionService

    async def run_agent():
        # 設定Artifacts服務
        artifact_service = InMemoryArtifactService()

        # 創建支援Artifacts的 runner
        runner = Runner(
            agent=root_agent,
            session_service=InMemorySessionService(),
            artifact_service=artifact_service
        )

        print("🤖 Artifacts代理程式已就緒！")
        print("📄 此代理程式可以處理文件並將其儲存為Artifacts。")
        print("💡 試試看：'處理此文件：[貼上一些文字]'")

        # 在實際的 CLI 中，您會在這裡處理使用者輸入
        # 目前，僅顯示代理程式已設定
        print(f"代理程式：{root_agent.name}")
        print(f"工具：{len(root_agent.tools)} 個可用")
        print("Artifacts服務：已設定 ✓")

    asyncio.run(run_agent())


if __name__ == "__main__":
    main()


# 根據 ADK 要求匯出 root_agent
root_agent = Agent(
    name="artifact_agent",
    model="gemini-1.5-flash",
    description="具備全面Artifacts儲存和版本控制功能的文件處理代理程式",
    instruction="""
    您是一個具備Artifacts儲存功能的進階文件處理代理程式。

        您的主要功能：
        1. 提取並儲存文件文字為Artifacts
        2. 生成摘要並將其儲存為版本化的Artifacts
        3. 將內容翻譯成多種語言
        4. 創建結合所有已處理Artifacts的綜合報告
        5. 列出並檢索先前儲存的Artifacts

        處理文件時：
        - 始終將提取的文字儲存為 'document_extracted.txt'
        - 將摘要儲存為 'document_summary.txt' 並進行版本控制
        - 將翻譯儲存為 'document_LANGUAGE.txt'（其中 LANGUAGE 是目標語言）
        - 將最終報告創建為 'document_FINAL_REPORT.md'

        當使用者詢問先前處理過的文件時，請使用 load_artifacts 工具。
        透過在新Artifacts中引用先前版本來維護Artifacts的來源。

        可用工具：
        - save_artifact: 儲存檔案並自動進行版本控制
        - load_artifact: 檢索特定Artifacts版本
        - list_artifacts: 顯示所有可用的Artifacts
        - load_artifacts_tool: 用於對話式Artifacts存取的內建工具
        """,
    tools=[
        extract_text_tool,
        summarize_document_tool,
        translate_document_tool,
        create_final_report_tool,
        list_artifacts_tool,
        load_artifact_tool,
        load_artifacts_tool,  # 用於對話式存取的 ADK 內建工具
    ],
)
