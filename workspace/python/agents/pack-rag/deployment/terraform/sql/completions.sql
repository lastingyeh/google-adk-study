-- 優化 Cloud Logging 資料與 GCS 儲存的 prompt/response 資料的 Join 操作。
-- 此查詢會提取日誌中引用的輸入與輸出訊息。
-- 注意：輸入檔案包含完整的對話歷史，因此訊息可能會多次出現。
-- Optimized join of Cloud Logging data with GCS-stored prompt/response data.
-- This query extracts both input and output messages referenced in logs.
-- Note: Input files contain full conversation history, so messages may appear multiple times.

-- 從 Cloud Logging 提取訊息引用 (掃描一次，提取輸入/輸出兩者)
-- Extract message references from Cloud Logging (scan once, extract both input/output)
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

-- Unpivot 以獲得每個訊息引用的一行資料
-- Unpivot to get one row per message reference
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

-- 與 completions 外部資料表 Join 並提取一次 api_call_id
-- Join with completions external table and extract api_call_id once
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

-- 展平 (Flatten) parts 陣列
-- Flatten the parts array
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

-- 按 trace 去除重複：每個 trace 只保留最新的日誌條目
-- (Tool calls 會建立多個具有相同 trace 但不同 timestamp 的日誌條目)
-- Deduplicate by trace: keep only the latest log entry per trace
-- (Tool calls create multiple log entries with same trace but different timestamps)
deduplicated AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY trace, message_type, role, message_idx, part_idx
      ORDER BY timestamp DESC
    ) AS row_num
  FROM flattened
)

SELECT
  -- 核心識別碼和時間戳記 (Core identifiers and timestamps)
  timestamp,
  insert_id,
  trace,
  span_id,
  api_call_id,

  -- 訊息元數據 (Message metadata)
  message_type,
  role,
  message_idx,
  part_idx,

  -- 訊息內容 (Message content)
  content,

  -- Tool/function calling
  part_type,
  tool_name,
  tool_args,
  tool_response,

  -- 額外元數據 (Additional metadata)
  uri,
  mime_type,
  data_md5_hex,

  -- 原始欄位 (Raw fields)
  labels,
  messages_ref_uri
FROM deduplicated
WHERE row_num = 1  -- 每個 trace/message/part 只保留最新的條目 (Keep only the latest entry per trace/message/part)
ORDER BY trace ASC, message_type ASC, message_idx ASC, part_idx ASC

/*
# 重點摘要
# - **核心概念**：BigQuery SQL 資料整合
# - **關鍵技術**：BigQuery SQL (CTEs, UNNEST, Window Functions)
# - **重要結論**：此 SQL 查詢將 Cloud Logging 中的日誌記錄與 GCS 外部資料表中的詳細對話內容進行關聯 (Join)，並展平 (Flatten) 巢狀的 JSON 結構，以便進行分析。
# - **行動項目**：無
*/
