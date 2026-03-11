-- 優化後的 Cloud Logging 數據與存儲在 GCS 的提示 (Prompt)/回覆 (Response) 數據關聯查詢。
-- 此查詢會提取日誌中引用的輸入與輸出訊息。
-- 注意：輸入檔案包含完整的對話歷史，因此訊息可能會出現多次。

-- 從 Cloud Logging 提取訊息引用資訊 (掃描一次，同時提取輸入與輸出)
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

-- 轉置 (Unpivot) 數據，使每個訊息引用佔用一行
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

-- 與回覆結果 (Completions) 外部資料表關聯，並提取 api_call_id
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

-- 展開 parts 陣列 (Flatten)
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

-- 依據追蹤識別碼 (Trace) 進行去重：每個追蹤僅保留最新的日誌項目
-- (工具調用會產生多個具有相同 trace 但不同時間戳記的日誌項目)
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
  -- 核心識別碼與時間戳記
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

  -- 工具/函式調用 (Function Calling)
  part_type,
  tool_name,
  tool_args,
  tool_response,

  -- 額外元數據
  uri,
  mime_type,
  data_md5_hex,

  -- 原始欄位
  labels,
  messages_ref_uri
FROM deduplicated
WHERE row_num = 1  -- 僅保留每個 trace/message/part 的最新條目
ORDER BY trace ASC, message_type ASC, message_idx ASC, part_idx ASC
