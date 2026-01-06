# config.py
import os

"""Policy-as-Code Agent 的設定變數（設定檔）"""

# Google Cloud 專案設定
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# 記憶體庫（Memory Bank）設定
ENABLE_MEMORY_BANK = os.getenv("ENABLE_MEMORY_BANK", "True").lower() == "true"
FIRESTORE_DATABASE = os.getenv("FIRESTORE_DATABASE", "(default)")
FIRESTORE_COLLECTION_POLICIES = os.getenv("FIRESTORE_COLLECTION_POLICIES", "policies")
FIRESTORE_COLLECTION_EXECUTIONS = os.getenv(
    "FIRESTORE_COLLECTION_EXECUTIONS", "policy_executions"
)
CORE_POLICIES_DOC_REF = os.getenv(
    "CORE_POLICIES_DOC_REF", "configurations/core_policies"
)
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-004")

# LLM（大型語言模型）設定
GEMINI_MODEL_PRO = os.getenv("GEMINI_MODEL_PRO", "gemini-2.5-pro")
GEMINI_MODEL_FLASH = os.getenv("GEMINI_MODEL_FLASH", "gemini-2.5-flash")

# 提示詞（Prompt）檔案設定
PROMPT_CODE_GENERATION_FILE = os.getenv(
    "PROMPT_CODE_GENERATION_FILE", "code_generation.md"
)
PROMPT_REMEDIATION_FILE = os.getenv("PROMPT_REMEDIATION_FILE", "remediation.md")
PROMPT_INSTRUCTION_FILE = os.getenv("PROMPT_INSTRUCTION_FILE", "instructions.md")

# MCP（Dataplex MCP 伺服器）設定
DATAPLEX_MCP_SERVER_URL = os.getenv("DATAPLEX_MCP_SERVER_URL")

# 執行緒（Threading）設定
MAX_REMEDIATION_WORKERS = int(os.getenv("MAX_REMEDIATION_WORKERS", 10))

# 預設核心政策（Default Core Policies）
DEFAULT_CORE_POLICIES = [
    "analytics_dataset 與 finance_dataset 中的所有資料表必須進行分割區（partitioned）設計。",
    "所有資料表不得包含 byte 或 boolean 資料型態的欄位。",
    "所有資料表必須包含 'data_owner' 標籤。",
    "資料表名稱必須使用蛇形命名法（snake_case）。",
    "對於 marketing_dataset 中名稱包含 'performance' 的每個資料表，sales_dataset 中必須存在名稱包含 'summary' 的資料表，且 marketing_dataset 中所有資料表的欄位名稱皆須使用蛇形命名法（snake_case）。",
]
