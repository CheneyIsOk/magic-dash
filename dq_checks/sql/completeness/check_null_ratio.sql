-- 检查列空值比例
SELECT 
  CASE 
    WHEN COUNT(*) = 0 THEN 0 
    ELSE SUM(CASE WHEN {{ column }} IS NULL THEN 1 ELSE 0 END) / COUNT(*)
  END AS null_ratio 
FROM {{ table }};
