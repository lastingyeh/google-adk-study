-- ============================================================================
-- Completions 視圖 SQL 查詢
-- ============================================================================
-- 此 SQL 查詢建立一個 BigQuery 視圖，結合 Cloud Logging 和 GCS 中的資料：
--
-- 主要功能：
-- 1. 從 Cloud Logging 提取 GenAI 遙測日誌中的訊息引用
-- 2. 與儲存在 GCS 中的 prompt/response 實際內容進行 JOIN
-- 3. 將巢狀的訊息結構扁平化，便於分析
-- 4. 去除重複的追蹤記錄（保留最新的）
-- 5. 提取工具呼叫資訊（tool name, arguments, response）
--
-- 資料流程：
-- log_refs → unpivoted_refs → joined_data → flattened → deduplicated → 最終結果
--
-- 注意：輸入檔案包含完整的對話歷史記錄，因此訊息可能會出現多次
-- ============================================================================

-- 優化 Cloud Logging 資料與儲存在 GCS 中的 prompt/response 資料的 JOIN 操作。
-- 此查詢會提取日誌中引用的輸入和輸出訊息。
-- 注意：輸入檔案包含完整的對話歷史記錄，因此訊息可能會出現多次。

-- 從 Cloud Logging 中提取訊息引用 (掃描一次，同時提取輸入/輸出)
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

-- Unpivot 操作，為每個訊息引用產生一列
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

-- 與 completions 外部資料表 JOIN，並提取一次 api_call_id
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

-- 將 parts 陣列扁平化
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
-- (工具呼叫會產生多個具有相同 trace 但時間戳不同的日誌條目)
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
  -- 核心識別碼與時間戳
  timestamp,
  insert_id,
  trace,
  span_id,
  api_call_id,

  -- 訊息元資料
  message_type,
  role,
  message_idx,
  part_idx,

  -- 訊息內容
  content,

  -- 工具/函式呼叫
  part_type,
  tool_name,
  tool_args,
  tool_response,

  -- 額外元資料
  uri,
  mime_type,
  data_md5_hex,

  -- 原始欄位
  labels,
  messages_ref_uri
FROM deduplicated
WHERE row_num = 1  -- 每個 trace/message/part 只保留最新的條目
ORDER BY trace ASC, message_type ASC, message_idx ASC, part_idx ASC
