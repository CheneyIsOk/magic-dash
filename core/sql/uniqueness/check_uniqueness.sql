-- 检查字段唯一性
SELECT 
  COUNT(*) AS row_cnt,
  COUNT(distinct {{ column }}) AS distinct_cnt
FROM {{ table }};
