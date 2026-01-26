# 會話資料庫架構遷移 (Session database schema migration)

> 🔔 `更新日期：2026-01-26`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/sessions/session/migrate/

[`ADK 支援`: `Python v1.22.1`]

如果您正在使用 `DatabaseSessionService` 並升級至 ADK Python 版本 v1.22.0 或更高版本，您應該將資料庫遷移至新的會話資料庫架構（session database schema）。從 ADK Python 版本 v1.22.0 開始，`DatabaseSessionService` 的資料庫架構已從 `v0`（基於 pickle 的序列化）更新為 `v1`（使用基於 JSON 的序列化）。先前的 `v0` 會話架構資料庫將繼續與 ADK Python v1.22.0 及更高版本配合使用，但在未來的版本中可能需要 `v1` 架構。


## 遷移會話資料庫 (Migrate session database)

系統提供了一個遷移腳本以簡化遷移過程。該腳本會從您現有的資料庫中讀取數據，將其轉換為新格式，並將其寫入新資料庫。您可以使用 ADK 命令列介面 (CLI) 的 `migrate session` 命令執行遷移，如下列範例所示：

> [!WARNING] 需要：ADK Python v1.22.1 或更高版本
此程序需要 ADK Python v1.22.1，因為它包含遷移命令列介面功能以及支援會話資料庫架構更改的錯誤修正。

<details>
<summary>範例說明</summary>

> SQLite

```bash
# 使用 ADK CLI 遷移會話資料庫
adk migrate session \
  --source_db_url=sqlite:///source.db \
  --dest_db_url=sqlite:///dest.db
```

> PostgreSQL

```bash
# 從 v0 遷移至 v1 的 PostgreSQL 範例
adk migrate session \
  --source_db_url=postgresql://localhost:5432/v0 \
  --dest_db_url=postgresql://localhost:5432/v1
```

</details>

執行遷移後，請更新您的 `DatabaseSessionService` 配置，以使用您為 `dest_db_url` 指定的新資料庫 URL。
