from __future__ import annotations

from typing import Any, Dict, Optional, List

import pandas as pd
from sqlalchemy import text

from utils.db_pool import get_connection


def run_sql(datasource_name: str, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """执行SQL并返回字典列表（基于连接池的上下文管理）

    参数:
    - datasource_name: 数据源名称（DataSourceModel.name）
    - sql: 需要执行的SQL文本
    - params: 可选的参数字典，用于绑定到SQL

    返回:
    - List[Dict[str, Any]]: 查询结果的字典列表
    """
    with get_connection(datasource_name) as conn:
        result = conn.execute(text(sql), params or {})
        return [dict(row) for row in result.mappings().all()]


def run_dataframe(datasource_name: str, sql: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """执行SQL并返回DataFrame（基于连接池的上下文管理）

    参数:
    - datasource_name: 数据源名称（DataSourceModel.name）
    - sql: 需要执行的SQL文本
    - params: 可选的参数字典，用于绑定到SQL

    返回:
    - pandas.DataFrame: 查询结果的DataFrame
    """
    with get_connection(datasource_name) as conn:
        return pd.read_sql(text(sql), conn, params=params)
