-- 检查列空值比例
SELECT 
  COUNT(*) AS row_cnt,
  SUM(CASE WHEN {{ column }} IS NULL THEN 1 ELSE 0 END) AS null_cnt
FROM {{ table }};
