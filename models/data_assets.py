from __future__ import annotations

import pathlib
from typing import Optional

from peewee import (
    SqliteDatabase,
    Model,
    AutoField,
    CharField,
    TextField,
)

PROJECT_ROOT = pathlib.Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "database" / "data_asset.db"

AssetDB = SqliteDatabase(DB_PATH.as_posix())


class BaseModel(Model):
    class Meta:
        database = AssetDB


class CheckTableSize(BaseModel):
    """
        表每日大小检查结果
        check_table_size.sql 的查询结果（用于分析和页面读取）
    """
    class Meta:
        table_name = "check_table_size"

    id = AutoField()
    dt = CharField(index=True)  # YYYY-MM-DD
    data_source = CharField(index=True)
    data_source_db = CharField(null=True)  # 数据库归属（DataSourceModel.database）
    table_schema = CharField(default="public")
    table_name = CharField()
    table_size = CharField()  # pretty size text
    indexes_size = CharField()  # pretty size text
    total_size = CharField()  # pretty size text


def ensure_schema() -> None:
    AssetDB.connect(reuse_if_open=True)
    AssetDB.create_tables([CheckTableSize])  # 确保表结构；新增模型时需要更新这里
    AssetDB.close()


# 自动确保表结构
try:
    ensure_schema()
except Exception as e:
    # 启动时确保不抛出异常，失败则在使用时重试
    print(f"初始化数据资产库失败: {e}")