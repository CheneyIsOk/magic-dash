from __future__ import annotations

import os
import sqlite3
from typing import List

from configs.database_config import DataSourceModel, source_db
from utils.db_pool import get_engine_by_name, invalidate_engine
from utils.get_tables import get_tables
from server import cache


def setup_module(module):
    """测试前准备：创建sqlite测试数据库与数据源记录"""
    db_path = os.path.join(os.path.dirname(__file__), "tmp_test.db")
    # 创建sqlite物理文件并建表
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS foo(id INTEGER PRIMARY KEY, name TEXT)")
    conn.commit()
    conn.close()

    # 写入数据源记录
    with source_db.atomic():
        # 若已存在则更新，否则创建
        ds = DataSourceModel.select().where(DataSourceModel.name == "test_sqlite").first()
        if ds:
            ds.type = "sqlite"
            ds.database = db_path
            ds.host = ""
            ds.port = 0
            ds.username = ""
            ds.password = ""
            ds.save()
        else:
            DataSourceModel.create(
                name="test_sqlite",
                type="sqlite",
                host="",
                port=0,
                database=db_path,
                username="",
                password="",
            )


def teardown_module(module):
    """测试后清理：删除测试数据源与sqlite文件"""
    with source_db.atomic():
        DataSourceModel.delete().where(DataSourceModel.name == "test_sqlite").execute()
    db_path = os.path.join(os.path.dirname(__file__), "tmp_test.db")
    try:
        os.remove(db_path)
    except Exception:
        pass


def test_engine_pool_and_invalidation():
    """验证连接池创建与失效逻辑"""
    engine1 = get_engine_by_name("test_sqlite")
    assert engine1.dialect.name == "sqlite"

    # 再次获取应复用缓存
    engine2 = get_engine_by_name("test_sqlite")
    assert engine1 is engine2

    # 失效后重新获取应产生新对象
    invalidate_engine("test_sqlite")
    engine3 = get_engine_by_name("test_sqlite")
    assert engine3 is not engine1


def test_get_tables_and_cache_clear():
    """验证表名获取与缓存清理效果"""
    tables1: List[dict] = get_tables(selected_db="test_sqlite")
    names1 = {t["table"] for t in tables1}
    assert "foo" in names1

    # 添加新表后，未清理缓存前可能仍返回旧结果
    db_path = os.path.join(os.path.dirname(__file__), "tmp_test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS bar(id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

    tables2: List[dict] = get_tables(selected_db="test_sqlite")
    names2 = {t["table"] for t in tables2}
    # 若缓存命中，bar可能不在结果中
    # 清理缓存后应能获取到bar
    cache.clear()
    tables3: List[dict] = get_tables(selected_db="test_sqlite")
    names3 = {t["table"] for t in tables3}
    assert "bar" in names3