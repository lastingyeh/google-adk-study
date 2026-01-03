# Terraform 基礎架構說明

此目錄包含用於部署客戶服務 Agent 的基礎架構程式碼（Infrastructure as Code）。

### 目錄結構重點：

- **根目錄 (`terraform/`)**: 包含核心資源定義。
  - `apis.tf`: 啟用所需的 Google Cloud API（如 Vertex AI, Cloud Build）。
  - `storage.tf`: 建立用於存儲 Agent 打包檔案的 Cloud Storage Bucket。
  - `iam.tf` & `service_accounts.tf`: 定義 Agent 運作所需的權限與服務帳戶。
  - `build_triggers.tf`: 設定 Cloud Build 觸發器以實現自動化部署。
  - `github.tf`: 處理與 GitHub 儲存庫的連結。
  - `variables.tf`: 定義輸入參數（如專案 ID、區域）。

- **環境目錄 (`dev/`)**: 針對開發環境的特定設定。
  - 繼承了根目錄的大部分邏輯，但允許針對開發環境進行微調。

- **變數檔案 (`vars/env.tfvars`)**:
  - 存放實際的參數值（如 `project_id = "your-project"`）。**注意：請勿將敏感資訊提交至版本控制。**

### 部署建議：
建議使用根目錄下的 `deploy.py` 進行應用程式層級的部署，而使用此處的 Terraform 檔案進行雲端基礎資源的初始化。
