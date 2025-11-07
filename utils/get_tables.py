from __future__ import annotations

from typing import Optional, List, Dict

from sqlalchemy import inspect
from server import cache
from configs.database_config import DataSourceModel
from utils.db_pool import get_engine_by_name

@cache.memoize(timeout=300)
def get_tables(dbmodel: type = DataSourceModel, selected_db: Optional[str] = None) -> List[Dict[str, str]]:
    """
    获取数据库中的所有表名（基于SQLAlchemy inspector）

    - 当提供 selected_db 时，仅返回该数据源的表
    - 否则遍历全部数据源，返回累积列表
    """
    try:
        if selected_db:
            datasource = dbmodel.get(dbmodel.name == selected_db)
            return _get_tables_from_datasource(datasource)
        else:
            datasources = dbmodel.select()
            all_tables: List[Dict[str, str]] = []
            for datasource in datasources:
                tables = _get_tables_from_datasource(datasource)
                all_tables.extend(tables)
            return all_tables
    except Exception as e:
        print(f"获取表列表失败: {e}")
        return []

def _get_tables_from_datasource(datasource: DataSourceModel) -> List[Dict[str, str]]:
    """从单个数据源获取表列表（统一使用SQLAlchemy inspector）"""
    try:
        engine = get_engine_by_name(datasource.name)
        inspector = inspect(engine)
        dialect = engine.dialect.name

        if dialect == "postgresql":
            tables = inspector.get_table_names(schema="public")
        else:
            # mysql/sqlite 等默认schema
            tables = inspector.get_table_names()

        return [{"datasource": datasource.name, "table": table} for table in tables]
    except Exception as e:
        print(f"从数据源 {datasource.name} 获取表列表失败: {e}")
        return []

@cache.memoize(timeout=300)
def get_columns(datasource_name: str, table_name: str) -> List[str]:
    """获取指定表的字段列表（统一使用SQLAlchemy inspector）"""
    try:
        engine = get_engine_by_name(datasource_name)
        inspector = inspect(engine)
        dialect = engine.dialect.name

        if dialect == "postgresql":
            cols = inspector.get_columns(table_name, schema="public")
        else:
            cols = inspector.get_columns(table_name)

        return [c["name"] for c in cols]
    except Exception as e:
        print(f"获取表 {table_name} 的字段列表失败: {e}")
        return []