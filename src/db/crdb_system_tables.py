
GET_TABLE_COLUMNS = """
SELECT 
    a.attname AS column_name,
    pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
    a.attnotnull AS not_null
FROM pg_catalog.pg_attribute a
INNER JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
INNER JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
WHERE c.relname = %s
  AND n.nspname = %s
  AND a.attnum > 0
  AND NOT a.attisdropped
ORDER BY a.attnum;
"""
GET_PRIMARY_KEY_COLUMNS = """
SELECT a.attname AS column_name
FROM pg_catalog.pg_constraint con
INNER JOIN pg_catalog.pg_class rel ON rel.oid = con.conrelid
INNER JOIN pg_catalog.pg_namespace nsp ON nsp.oid = rel.relnamespace
INNER JOIN pg_catalog.pg_attribute a ON a.attrelid = rel.oid AND a.attnum = ANY(con.conkey)
WHERE con.contype = 'p'
  AND nsp.nspname = %s
  AND rel.relname = %s
ORDER BY array_position(con.conkey, a.attnum);
"""
GET_COLUMN_DEFAULTS = """
SELECT
    a.attname AS column_name,
    pg_catalog.pg_get_expr(d.adbin, d.adrelid) AS default_expr
FROM pg_catalog.pg_attribute a
INNER JOIN pg_catalog.pg_class c ON c.oid = a.attrelid
INNER JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
INNER JOIN pg_catalog.pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
WHERE n.nspname = %s
  AND c.relname = %s
  AND a.attnum > 0
  AND NOT a.attisdropped
ORDER BY a.attnum;
"""
GET_UNIQUE_CONSTRAINTS = """
SELECT
    con.conname AS constraint_name,
    a.attname  AS column_name
FROM pg_catalog.pg_constraint con
INNER JOIN pg_catalog.pg_class rel
    ON rel.oid = con.conrelid
INNER JOIN pg_catalog.pg_namespace nsp
    ON nsp.oid = rel.relnamespace
INNER JOIN pg_catalog.pg_attribute a
    ON a.attrelid = rel.oid
   AND a.attnum = ANY(con.conkey)
WHERE con.contype = 'u'
  AND nsp.nspname = %s
  AND rel.relname = %s
ORDER BY con.conname, array_position(con.conkey, a.attnum);
"""
GET_TABLE_INDEXES = """
SELECT
    idx.relname AS index_name,
    ix.indisprimary AS is_primary,
    ix.indisunique  AS is_unique,
    pg_catalog.pg_get_indexdef(ix.indexrelid) AS index_def
FROM pg_catalog.pg_index ix
INNER JOIN pg_catalog.pg_class tbl
    ON tbl.oid = ix.indrelid
INNER JOIN pg_catalog.pg_namespace nsp
    ON nsp.oid = tbl.relnamespace
INNER JOIN pg_catalog.pg_class idx
    ON idx.oid = ix.indexrelid
WHERE nsp.nspname = %s
  AND tbl.relname = %s
ORDER BY ix.indisprimary DESC, ix.indisunique DESC, idx.relname;
"""
GET_FOREIGN_KEYS = """
SELECT
    con.conname AS fk_name,
    src_col.attname AS column_name,
    ref_nsp.nspname AS ref_schema,
    ref_rel.relname AS ref_table,
    ref_col.attname AS ref_column
FROM pg_catalog.pg_constraint con
INNER JOIN pg_catalog.pg_class src_rel
    ON src_rel.oid = con.conrelid
INNER JOIN pg_catalog.pg_namespace src_nsp
    ON src_nsp.oid = src_rel.relnamespace
INNER JOIN pg_catalog.pg_class ref_rel
    ON ref_rel.oid = con.confrelid
INNER JOIN pg_catalog.pg_namespace ref_nsp
    ON ref_nsp.oid = ref_rel.relnamespace
INNER JOIN pg_catalog.pg_attribute src_col
    ON src_col.attrelid = src_rel.oid
   AND src_col.attnum = ANY(con.conkey)
INNER JOIN pg_catalog.pg_attribute ref_col
    ON ref_col.attrelid = ref_rel.oid
   AND ref_col.attnum = ANY(con.confkey)
WHERE con.contype = 'f'
  AND src_nsp.nspname = %s
  AND src_rel.relname = %s
ORDER BY con.conname;
"""
LIST_DATABASES = "SHOW DATABASES;"

LIST_SCHEMAS = """
SELECT n.nspname AS schema_name
FROM pg_catalog.pg_namespace n
WHERE n.nspname NOT LIKE 'pg_%'
  AND n.nspname <> 'information_schema'
  AND n.nspname <> 'crdb_internal'
ORDER BY n.nspname;
"""

LIST_TABLES_BY_SCHEMA = """
SELECT n.nspname AS schema_name,
       c.relname AS table_name
FROM pg_catalog.pg_class c
INNER JOIN pg_catalog.pg_namespace n
  ON n.oid = c.relnamespace
WHERE c.relkind = 'r'
  AND n.nspname = %s
ORDER BY c.relname;
"""

LIST_VIEWS_BY_SCHEMA = """
SELECT n.nspname AS schema_name,
       c.relname AS view_name
FROM pg_catalog.pg_class c
INNER JOIN pg_catalog.pg_namespace n
  ON n.oid = c.relnamespace
WHERE c.relkind = 'v'
  AND n.nspname = %s
ORDER BY c.relname;
"""

LIST_INDEXES_BY_SCHEMA = """
SELECT
  ns.nspname  AS schema_name,
  t.relname   AS table_name,
  i.relname   AS index_name
FROM pg_catalog.pg_index ix
INNER JOIN pg_catalog.pg_class t
  ON t.oid = ix.indrelid
INNER JOIN pg_catalog.pg_class i
  ON i.oid = ix.indexrelid
INNER JOIN pg_catalog.pg_namespace ns
  ON ns.oid = t.relnamespace
WHERE ns.nspname = %s
ORDER BY t.relname, i.relname;
"""

LIST_FUNCTIONS_BY_SCHEMA = """
SELECT
  n.nspname AS schema_name,
  p.proname AS routine_name
FROM pg_catalog.pg_proc p
INNER JOIN pg_catalog.pg_namespace n
  ON n.oid = p.pronamespace
WHERE n.nspname = %s
ORDER BY p.proname;
"""

LIST_SEQUENCES_BY_SCHEMA = """
SELECT n.nspname AS schema_name,
       c.relname AS sequence_name
FROM pg_catalog.pg_class c
INNER JOIN pg_catalog.pg_namespace n
  ON n.oid = c.relnamespace
WHERE c.relkind = 'S'
  AND n.nspname = %s
ORDER BY c.relname;
"""

LIST_TYPES_BY_SCHEMA = """
SELECT n.nspname AS schema_name,
       t.typname AS type_name
FROM pg_catalog.pg_type t
INNER JOIN pg_catalog.pg_namespace n
  ON n.oid = t.typnamespace
WHERE n.nspname = %s
ORDER BY t.typname;
"""