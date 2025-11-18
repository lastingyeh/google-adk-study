from setuptools import setup, find_packages

setup(
    name="tutorial20",
    version="0.1.0",
    packages=find_packages(include=["tutorial20", "tutorial20.*", "customer_support", "customer_support.*"]),
    install_requires=["google-adk>=1.15.1"],
    description="教學 20：YAML 設定 - 宣告式代理人設定",
    python_requires=">=3.9",
)

# 重點摘要
# - **核心概念**：Python 套件安裝設定腳本。
# - **關鍵技術**：setuptools, find_packages。
# - **重要結論**：使用 `setuptools` 封裝專案，定義了套件名稱、版本、包含的模組 (`customer_support`) 以及依賴項 (`google-adk`)。
# - **行動項目**：使用 `pip install -e .` 安裝專案為可編輯模式。
