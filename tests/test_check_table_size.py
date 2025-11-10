"""
执行 core/sql/metadata/check_table_size.sql 的小脚本/测试：
- 默认在 web-dev 环境下运行
- 自动选择第一个 PostgreSQL 数据源（也可通过命令行参数 --ds 指定）
- dt 默认取今天（YYYY-MM-DD），可通过 --dt 指定
- 输出结果中字段包含：dt、table_schema、table_name、table_size、indexes_size、total_size
- 额外打印按 total_size 排序的 Top10（基于 pg_size_pretty 文本解析成字节排序）

用法：
  conda run -n web-dev python tests/test_check_table_size.py
  conda run -n web-dev python tests/test_check_table_size.py --ds my_pg --dt 2025-11-09
"""


from __future__ import annotations

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import re
import sys
import argparse
import pathlib
from datetime import date
from typing import Optional, List, Dict

import pandas as pd

from utils.execute_query import run_dataframe
from configs.database_config import DataSourceModel
from models.data_assets import AssetDB, CheckTableSize


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
SQL_PATH = PROJECT_ROOT / "core" / "sql" / "metadata" / "check_table_size.sql"


def _render_sql(dt: str) -> str:
    """将模板SQL中的 {{ dt }} 渲染为命名参数 :dt"""
    raw = SQL_PATH.read_text(encoding="utf-8")
    return re.sub(r"\{\{\s*dt\s*\}\}", ":dt", raw)


def _parse_pretty_size_to_bytes(text: str) -> float:
    """将 pg_size_pretty 的输出解析为字节数便于排序，例如 '123 MB', '9 kB', '42 bytes'"""
    if not text:
        return 0.0
    try:
        m = re.match(r"^(\d+(?:\.\d+)?)\s*([A-Za-z]+)\s*$", text)
        if not m:
            return float(text)
        value = float(m.group(1))
        unit = m.group(2).lower()
        unit_map = {
            "b": 1,
            "byte": 1,
            "bytes": 1,
            "kb": 1024,
            "mb": 1024 ** 2,
            "gb": 1024 ** 3,
            "tb": 1024 ** 4,
            "pb": 1024 ** 5,
            "eb": 1024 ** 6,
        }
        return value * unit_map.get(unit, 1)
    except Exception:
        return 0.0


def _pick_first_pg_datasource() -> Optional[str]:
    try:
        for ds in DataSourceModel.select():
            if getattr(ds, "type", None) == "postgresql":
                return ds.name
        return None
    except Exception:
        return None


def _get_datasource_db_name(datasource_name: str) -> Optional[str]:
    """根据数据源名，获取其 database 字段作为 data_source_db 标识"""
    try:
        ds = DataSourceModel.get(DataSourceModel.name == datasource_name)
        return getattr(ds, "database", None)
    except Exception:
        return None


def _write_check_table_size(
    df: pd.DataFrame,
    dt: str,
    datasource_name: str,
    data_source_db: Optional[str],
) -> int:
    """使用 Peewee 模型 CheckTableSize 写入，并在写入前按 dt 清空当天数据，避免重复"""
    if df.empty:
        return 0

    records: List[Dict[str, str]] = df.to_dict(orient="records")
    payloads: List[Dict[str, str]] = []
    for row in records:
        payloads.append({
            "dt": dt,
            "datasource": datasource_name,
            "data_source_db": data_source_db or "",
            "table_schema": row.get("table_schema", "public"),
            "table_name": row.get("table_name", ""),
            "table_size": row.get("table_size", ""),
            "indexes_size": row.get("indexes_size", ""),
            "total_size": row.get("total_size", ""),
        })

    inserted = 0
    try:
        AssetDB.connect(reuse_if_open=True)
        with AssetDB.atomic():
            # 按 dt + datasource 清空，避免一天同数据源的数据重复
            CheckTableSize.delete().where(
                (CheckTableSize.dt == dt) & (CheckTableSize.datasource == datasource_name)
            ).execute()
            if payloads:
                CheckTableSize.insert_many(payloads).execute()
                inserted = len(payloads)
    except Exception as e:
        print(f"写入 CheckTableSize 失败: {e}")
    finally:
        try:
            AssetDB.close()
        except Exception:
            pass

    return inserted


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run check_table_size.sql against a datasource")
    parser.add_argument("--ds", type=str, default=None, help="Datasource name (PostgreSQL)")
    parser.add_argument("--dt", type=str, default=date.today().isoformat(), help="Date (YYYY-MM-DD)")
    parser.add_argument("--no-write", action="store_true", help="仅查询不写入本地快照表(check_table_size)")

    args = parser.parse_args(argv)

    if not SQL_PATH.exists():
        print(f"SQL文件不存在: {SQL_PATH}")
        return 2

    datasource = args.ds or _pick_first_pg_datasource()
    if not datasource:
        print("未找到PostgreSQL数据源，请在数据库配置中添加后重试（configs.database_config.DataSourceModel）")
        return 3
    data_source_db = _get_datasource_db_name(datasource)
    if not data_source_db:
        print("警告：未能获取数据源的 database 字段，将以空字符串写入 data_source_db")

    try:
        sql = _render_sql(args.dt)
        df: pd.DataFrame = run_dataframe(datasource, sql, params={"dt": args.dt})
        print("df columns:", df.columns)
    except Exception as e:
        print(f"执行失败: {e}")
        return 4

    expected_cols = {"dt", "table_schema", "table_name", "table_size", "indexes_size", "total_size"}
    if not expected_cols.issubset(set(df.columns)):
        print(f"返回列缺失，期望包含: {expected_cols}，实际: {list(df.columns)}")
        return 5

    print(f"查询成功：共 {len(df)} 条记录（dt={args.dt}, ds={datasource}）")

    # 写入本地 SQLite（Peewee模型：CheckTableSize），包含 data_source_db 字段，并按 dt+datasource 清空
    if not args.no_write:
        inserted = _write_check_table_size(df, args.dt, datasource, data_source_db)
        print(f"已写入 CheckTableSize：{inserted} 条（按 dt+datasource 清空后写入，data_source_db={data_source_db}）")

    # Top10 by total_size (descending)
    if not df.empty:
        df_sorted = df.copy()
        df_sorted["__total_bytes__"] = df_sorted["total_size"].map(_parse_pretty_size_to_bytes)
        df_sorted = df_sorted.sort_values("__total_bytes__", ascending=False).head(10)
        print("\nTop10（按 total_size）：")
        print(df_sorted[["table_schema", "table_name", "table_size", "indexes_size", "total_size"]].to_string(index=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())

#     conn = sqlite3.connect(ASSET_DB_PATH.as_posix())
#     cur = conn.cursor()
#     tables = cur.execute("""SELECT 
#     name
# FROM 
#     sqlite_schema
# WHERE 
#     type ='table' AND 
#     name NOT LIKE 'sqlite_%';""")
#     print(tables.fetchall())

#     tables = cur.execute("""DROP TABLE IF EXISTS checktablesize;""")
#     conn.commit()