-- 目的：優化 Cloud Logging 資料與儲存在 GCS 中的提示/回應資料的 JOIN 操作。
-- 說明：此查詢會從 Cloud Logging 中擷取 AI 模型互動的日誌，並與 GCS 上儲存的完整對話內容進行關聯。
--      它能解析出結構化的對話資料，包含輸入(input)、輸出(output)、工具調用(tool calls)等。
-- 注意：輸入檔案包含完整的對話歷史記錄，因此訊息可能會出現多次。

-- 步驟1: 從 Cloud Logging 提取訊息參考
-- 建立一個名為 log_refs 的 CTE (Common Table Expression)。
-- 掃描日誌一次，同時提取輸入(input_ref)和輸出(output_ref)的 GCS 路徑參考。
WITH log_refs AS (
  SELECT
    insert_id,
    timestamp,
    labels,
    trace,
    span_id,
    JSON_VALUE(labels, '$.\"gen_ai.input.messages_ref\"') AS input_ref,
    JSON_VALUE(labels, '$.\"gen_ai.output.messages_ref\"') AS output_ref
  FROM `${project_id}.${logs_link_id}._AllLogs`
  WHERE JSON_VALUE(labels, '$.\"gen_ai.input.messages_ref\"') IS NOT NULL
     OR JSON_VALUE(labels, '$.\"gen_ai.output.messages_ref\"') IS NOT NULL
),

-- 步驟2: Unpivot 資料，為每個訊息參考產生一列
-- 建立 unpivoted_refs CTE，將上一步的 input_ref 和 output_ref 欄位轉換為單一的 messages_ref_uri 欄位。
-- 並增加 'message_type' 欄位來標示是 'input' 還是 'output'。
unpivoted_refs AS (
  SELECT
    insert_id,
    timestamp,
    labels,
    trace,
    span_id,
    input_ref AS messages_ref_uri,
    'input' AS message_type
  FROM log_refs
  WHERE input_ref IS NOT NULL

  UNION ALL

  SELECT
    insert_id,
    timestamp,
    labels,
    trace,
    span_id,
    output_ref AS messages_ref_uri,
    'output' AS message_type
  FROM log_refs
  WHERE output_ref IS NOT NULL
),

-- 步驟3: 與 GCS 外部資料表 JOIN 以取得詳細內容
-- 建立 joined_data CTE，將日誌參考與儲存在 GCS 的詳細訊息內容（透過 BigQuery 外部資料表存取）進行 JOIN。
-- JOIN 條件是 GCS 檔案路徑 (_FILE_NAME)。
-- 同時，從檔案路徑中提取 api_call_id。
joined_data AS (
  SELECT
    lr.insert_id,
    lr.timestamp,
    lr.labels,
    lr.trace,
    lr.span_id,
    lr.messages_ref_uri,
    lr.message_type,
    SPLIT(REGEXP_EXTRACT(lr.messages_ref_uri, r'/([^/]+)\.jsonl'), '_')[OFFSET(0)] AS api_call_id,
    c.role,
    c.parts,
    c.index AS message_idx
  FROM unpivoted_refs lr
  JOIN `${project_id}.${dataset_id}.${completions_external_table}` c
    ON lr.messages_ref_uri = c._FILE_NAME
),

-- 步驟4: 展開 parts 陣列
-- 建立 flattened CTE，使用 CROSS JOIN UNNEST 將 'parts' 陣列中的每個元素展開成獨立的列。
-- 'parts' 陣列包含了訊息的各個部分，例如文字內容、工具調用請求等。
flattened AS (
  SELECT
    insert_id,
    timestamp,
    labels,
    trace,
    span_id,
    messages_ref_uri,
    message_type,
    api_call_id,
    role,
    message_idx,
    part_idx,
    part.type AS part_type,
    part.content,
    part.uri,
    part.mime_type,
    TO_HEX(MD5(part.data)) AS data_md5_hex,
    part.id AS tool_id,
    part.name AS tool_name,
    part.arguments AS tool_args,
    part.response AS tool_response
  FROM joined_data
  CROSS JOIN UNNEST(parts) AS part WITH OFFSET AS part_idx
),

-- 步驟5: 根據 trace 進行資料去重
-- 建立 deduplicated CTE。由於工具調用等操作可能會在同一個 trace 中產生多筆日誌，
-- 這裡使用 ROW_NUMBER() 視窗函數，根據時間戳(timestamp)排序，保留每個訊息部分最新的那筆記錄。
deduplicated AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY trace, message_type, role, message_idx, part_idx
      ORDER BY timestamp DESC
    ) AS row_num
  FROM flattened
)

-- 最終選取與排序
SELECT
  -- 核心識別碼與時間戳
  timestamp,
  insert_id,
  trace,
  span_id,
  api_call_id,

  -- 訊息元數據
  message_type,
  role,
  message_idx,
  part_idx,

  -- 訊息內容
  content,

  -- 工具/函數調用相關欄位
  part_type,
  tool_name,
  tool_args,
  tool_response,

  -- 額外元數據
  uri,
  mime_type,
  data_md5_hex,

  -- 原始欄位，方便追溯
  labels,
  messages_ref_uri
FROM deduplicated
WHERE row_num = 1  -- 只保留每個追蹤/訊息/部分的最新條目
ORDER BY trace ASC, message_type ASC, message_idx ASC, part_idx ASC -- 按照對話順序排序
