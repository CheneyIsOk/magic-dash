from __future__ import annotations

from functools import lru_cache
from contextlib import contextmanager
from typing import Iterator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, Connection

from configs.database_config import DataSourceModel


def _build_conn_uri(ds: DataSourceModel) -> str:
    """根据数据源配置构建SQLAlchemy连接URI"""
    if ds.type == "sqlite":
        # sqlite 使用文件路径
        return f"sqlite:///{ds.database}"
    elif ds.type == "postgresql":
        return (
            f"postgresql+psycopg2://{ds.username}:{ds.password}"
            f"@{ds.host}:{ds.port}/{ds.database}"
        )
    elif ds.type == "mysql":
        return (
            f"mysql+pymysql://{ds.username}:{ds.password}"
            f"@{ds.host}:{ds.port}/{ds.database}"
        )
    else:
        raise ValueError(f"不支持的数据库类型: {ds.type}")


@lru_cache(maxsize=64)
def get_engine_by_name(datasource_name: str) -> Engine:
    """按数据源名称获取（或创建并缓存）SQLAlchemy Engine"""
    ds = DataSourceModel.get(DataSourceModel.name == datasource_name)
    uri = _build_conn_uri(ds)
    return create_engine(
        uri,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=1800,
        future=True,
    )


@contextmanager
def get_connection(datasource_name: str) -> Iterator[Connection]:
    """提供连接上下文，确保归还连接到池"""
    engine = get_engine_by_name(datasource_name)
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()


def invalidate_engine(datasource_name: Optional[str] = None) -> None:
    """失效缓存的Engine

    - 若传入特定名称，当前实现直接清空全部缓存（lru_cache不支持精确键清除），
      同时这也能避免连接配置变更后缓存与实际不一致的问题。
    """
    # 未来如需精细化清除，可改为自维护dict缓存
    try:
        get_engine_by_name.cache_clear()
    except Exception as e:
        print(f"清理连接池缓存失败: {e}")