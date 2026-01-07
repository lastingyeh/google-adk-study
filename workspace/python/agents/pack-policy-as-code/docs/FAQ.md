# FAQ 常見問題

本文件彙整了在使用與開發 Policy-as-Code Agent 過程中，常見的問題與解決方案。

## Q1: 為什麼在打包時，prompts 目錄下的 .md 檔案沒有包含在發行包中？

**A1:**
這通常是因為在專案的 `MANIFEST.in` 檔案中沒有正確指定要包含這些檔案。請確認 `MANIFEST.in` 中有以下內容：

  **說明**:
    - **用途**：MANIFEST.in 是 Python 包在使用 `setuptools` 打包時，用來指定非 Python 原始碼資源（例如 README、範本、靜態檔案、資料檔等）應該被包含在分發套件（source distribution，sdist）中的清單檔。當你執行 `python setup.py sdist` 或使用 `build`/`pip` 建立源碼發行包時，MANIFEST.in 控制哪些檔案會被加入到最終的 `.tar.gz` 或 `.zip` 中。
    - **具體這行的意義**：`recursive-include policy_as_code_agent/prompts *.md` 表示：遞迴地將 prompts 目錄及其所有子目錄中，所有副檔名為 `.md` 的檔案（Markdown 檔）包含到 source distribution。也就是說，包發行檔會帶上 prompts 目錄下的所有 Markdown 提示檔案，讓使用者或部署端能夠存取這些說明/範本/提示內容。
    - **為什麼常見**：很多專案會把文字說明、提示模板或範例資料放在 package 目錄下，為了確保這些不是純程式碼但又必要的資源能發佈給使用者，就要在 MANIFEST.in 裡指明包含它們。

  **建議（選用）**:
    - 若還需要包含其他類型的檔案（例如 `.json`, `.yaml`, `.txt`, 或其他資料目錄），可以新增對應規則，例如：
    - `recursive-include policy_as_code_agent/prompts *.json`
    - `include README.md`
    - `recursive-include policy_as_code_agent/static *.*`
    - 若專案使用 `package_data`（在 `setup.cfg` 或 `setup.py`）並且搭配 `setuptools_scm` 或 `include_package_data=True`，請確認這些設定與 MANIFEST.in 不衝突。
    - 可檢查 pyproject.toml / `setup.cfg`（若存在）確保打包設定一致，避免遺漏需要的資源。
