"""
Policy Navigator 展示的簡單結果格式化器。
"""

from typing import List, Any


def format_answer(question: str, answer: str, citations: List[Any], store_name: str) -> str:
    """格式化搜尋結果以供顯示。"""
    dept = store_name.replace("policy-navigator-", "").upper()

    result = f"\n[{dept}] {question}\n"
    result += "─" * 70 + "\n"
    result += f"✓ 找到 {len(citations)} 個來源\n\n"
    result += f"{answer}\n"

    if citations:
        result += "來源 (Sources):\n"
        for i, cite in enumerate(citations[:3], 1):
            # 從引用字典或物件中擷取文字
            if isinstance(cite, dict):
                text = cite.get("text", str(cite)[:100])
            else:
                text = str(cite)[:100]

            # 清理文字
            text = text.replace("...", "").strip()[:100]
            result += f"  {i}. {text}...\n"

    result += "─" * 70 + "\n"

    return result
