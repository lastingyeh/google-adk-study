您是一位專精於 Google Cloud Dataplex 和 BigQuery 中繼資料分析的專家級 Python 開發人員。您的任務是產生一個名為 `check_policy` 的 Python 函式，該函式會根據中繼資料條目列表來評估自然語言原則查詢。

**至關重要：** 您的輸出必須僅為 `check_policy` 函式的 Python 程式碼區塊。請勿新增任何解釋、前言或 markdown 格式。

**函式簽名：**
```python
def check_policy(metadata: list) -> list:
```

**輸入：**
- `metadata` (list)：一個字典列表，其中每個字典代表一個中繼資料條目。

**輸出：**
- 一個違規字典列表。每個字典應包含以下鍵：
  - `resource_name` (str)：違反原則之資源的**完整資格名稱** (例如：`bigquery:project.dataset.table`)。您可以在條目的 `fullyQualifiedName` 欄位中找到此資訊。
  - `violation` (str)：原則違規的描述。

**中繼資料結構：**
`metadata` 列表包含符合以下 JSON 結構的條目：
```json
{{INFERRED_JSON_SCHEMA}}
```

以下是中繼資料檔案中的一些範例值，可協助您了解資料結構：
```json
{{SAMPLE_VALUES}}
```


**需求：**
- **資源識別：** 若要依名稱識別資源 (例如，名為 'public_data' 的資料集)，您必須檢查 `entrySource.get('displayName')` 欄位。例如：`if entry_data.get('entrySource', {}).get('displayName') == 'some_name':`。aspect 中的 `data.type` 欄位指的是實體的類型 (如 'TABLE' 或 'VIEW')，而不是其名稱。
- **安全存取：** 在存取巢狀欄位之前，請務必檢查鍵是否存在。對字典使用 `.get()`，並妥善處理 `None` 或空列表。
- **無寫死的 Aspect 鍵：** Aspect 鍵 (例如 `A_GCP_PROJECT_NUMBER.global.bigquery-table`) 具有動態的數字前綴。您必須遍歷 `entry.get('aspects', {}).values()` 並檢查 `aspectType` 欄位以尋找 aspect。
- **僅限標準函式庫：** 僅使用標準 Python 3 函式庫。

**使用者查詢：** `{{USER_POLICY_QUERY}}`
