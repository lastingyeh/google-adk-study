-- 在 BigQuery 中建立資料表
CREATE TABLE IF NOT EXISTS your_project_id.your_dataset_id.products (
    Title STRING,
    Description STRING,
    Attributes STRING,
    Brand STRING
);
-- 注意事項：
-- - 將 your_project_id 替換為您的 Google Cloud 專案 ID。
-- - 將 your_dataset_id 替換為您的 BigQuery 資料集名稱。

-- 將資料插入資料表
INSERT INTO your_project_id.your_dataset_id.products (Title, Description, Attributes,Brand)
VALUES
    ('兒童慢跑鞋','為活潑好動的孩子設計的舒適、具支撐性的跑鞋。透氣的網布鞋面能讓雙腳保持涼爽，耐用的外底則提供絕佳的抓地力。''尺寸：10 號幼童，顏色：藍/綠','BSOAgentTestBrand'),
    ('發光運動鞋','有趣又時尚的發光運動鞋，孩子們會愛不釋手。具支撐性且舒適，適合整天玩樂。','尺寸：13 號幼童，顏色：銀色','BSOAgentTestBrand'),
    ('學校鞋','多功能且舒適的鞋子，非常適合在學校日常穿著。結構耐用，設計具支撐性。''尺寸：12 號學齡前，顏色：黑色','BSOAgentTestBrand');
-- 注意事項：
-- - 確保專案和資料集 ID 與 CREATE TABLE 陳述式中使用的 ID 相符。