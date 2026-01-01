from langchain_core.prompts import (
    PromptTemplate,
)

# --- 重點說明 ---
# 1. 目的：此程式碼定義了一個 LangChain 的提示模板 (PromptTemplate)，用於將一系列文件（docs）格式化為單一的字串。
# 2. 模板語言：使用 Jinja2 模板格式 (`template_format="jinja2"`)，這允許使用迴圈、條件判斷等邏輯。
# 3. 運作方式：
#    - `{% for doc in docs %}`：這是一個迴圈，會遍歷傳入的 `docs` 列表中的每一個文件物件 `doc`。
#    - `<Document {{ loop.index0 }}>...</Document {{ loop.index0 }}>`：為每個文件內容加上 XML/HTML 風格的標籤，並使用 `loop.index0` (從 0 開始的索引) 來編號。
#    - `{{ doc.page_content | safe }}`：將每個文件的 `page_content` 屬性內容插入到模板中。`| safe` 過濾器是為了防止 Jinja2 自動跳脫內容中的特殊字元，確保原始內容（例如包含 HTML 標籤的內容）能被完整呈現。
# 4. 用途：這個 `format_docs` 模板通常在 RAG (Retrieval-Augmented Generation) 應用中，將檢索到的多個文件內容整理成一個清晰的上下文區塊，然後提供給大型語言模型進行後續處理。

format_docs = PromptTemplate.from_template(
    """## 提供的上下文：
    {% for doc in docs%}
    <文件 {{ loop.index0 }}>
    {{ doc.page_content | safe }}
    </文件 {{ loop.index0 }}>
    {% endfor %}
    """,
    template_format="jinja2",
)
