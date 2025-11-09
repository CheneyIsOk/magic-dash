-- 检查当前各表大小（包括数据、索引、总大小）
SELECT
    {{ dt }} as dt,
    table_schema,
    table_name,
    pg_size_pretty(table_size) AS table_size,
    pg_size_pretty(indexes_size) AS indexes_size,
    pg_size_pretty(total_size) AS total_size
FROM (
    SELECT
        table_schema,
        table_name,
        pg_table_size(table_name) AS table_size,
        pg_indexes_size(table_name) AS indexes_size,
        pg_total_relation_size(table_name) AS total_size
    FROM (
        SELECT 
            table_schema,
            table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    ) AS all_tables
    ORDER BY table_schema, total_size DESC
) AS pretty_sizes