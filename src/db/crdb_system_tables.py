# Consultas basadas en pg_catalog

LIST_TABLES = """
SELECT n.nspname AS schema_name, c.relname AS object_name
FROM pg_catalog.pg_class c
JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r'           -- r = ordinary table
  AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'crdb_internal')
ORDER BY n.nspname, c.relname;
"""

LIST_VIEWS = """
SELECT n.nspname AS schema_name, c.relname AS object_name
FROM pg_catalog.pg_class c
JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'v'           -- v = view
  AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'crdb_internal')
ORDER BY n.nspname, c.relname;
"""
GET_TABLE_COLUMNS = """
SELECT 
    a.attname AS column_name,
    pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
    a.attnotnull AS not_null
FROM pg_catalog.pg_attribute a
JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
WHERE c.relname = %s
  AND n.nspname = %s
  AND a.attnum > 0
  AND NOT a.attisdropped
ORDER BY a.attnum;
"""
