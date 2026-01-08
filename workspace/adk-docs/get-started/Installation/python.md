# Python 安裝指南

🔔 `更新日期：2026 年 1 月 4 日`

## 建立並啟用虛擬環境

我們建議使用 [venv](https://docs.python.org/3/library/venv.html) 建立一個虛擬 Python 環境：

`python -m venv .venv`

> **重點說明：**
> - `.venv` 是一個約定俗成的名稱，用於存放虛擬環境的相關檔案。您可以將其替換為您喜歡的任何名稱。
> - 建立虛擬環境是為了將專案的依賴套件與系統全域的 Python 環境隔離開來，避免版本衝突。

現在，您可以使用適合您作業系統和環境的指令來啟用虛擬環境：

```
# Mac / Linux
source .venv/bin/activate

# Windows CMD:
.venv\Scripts\activate.bat

# Windows PowerShell:
.venv\Scripts\Activate.ps1
```

> **重點說明：**
> - 啟用虛擬環境後，您安裝或移除的任何套件都只會影響到這個特定的環境。
> - 當您完成工作後，可以在終端機中執行 `deactivate` 指令來停用虛擬環境。

### 安裝 ADK

`pip install google-adk`

(可選) 驗證您的安裝：

`pip show google-adk`

> **重點說明：**
> - `pip` 是 Python 的套件安裝程式。`install` 指令會從 [Python Package Index (PyPI)](https://pypi.org/) 下載並安裝套件。
> - `show` 指令可以顯示已安裝套件的詳細資訊，例如版本、摘要、首頁等。

### 參考資源

- [ADK Python Repository](https://github.com/google/adk-python)
- [Python venv — 虛擬環境的建立](https://docs.python.org/3/library/venv.html)
- [pip documentation](https://pip.pypa.io/en/stable/)
- [Python Package Index (PyPI)](https://pypi.org/)