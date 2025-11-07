import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from configs.database_config import DataSourceModel, source_db
from utils.get_tables import get_tables

# 测试数据库连接
def test_datasource_connection():
    source_db.connect(reuse_if_open=True)
    query = DataSourceModel.select()
    assert query is not None, "数据库连接失败"
    assert len(query) > 0, "数据库中没有数据源"
    for ds in query:
        print("res:", ds.name, ds.host, ds.port)
    source_db.close()


# 查看数据库有多少表
def test_database_tables():
    # 使用统一的SQLAlchemy连接池接口，逐个数据源获取表名
    source_db.connect(reuse_if_open=True)
    try:
        data_sources = list(DataSourceModel.select())
        assert data_sources is not None, "未能读取数据源列表"
        if not data_sources:
            print("数据源列表为空，跳过表枚举测试")
            return

        for ds in data_sources:
            tables = get_tables(DataSourceModel, ds.name)
            print(f"数据源 '{ds.name}' 的表:", tables)
            assert tables is not None, f"获取数据源 {ds.name} 的表失败"
            # 表数量可能为0，允许通过；仅验证流程不报错
    finally:
        source_db.close()


# 获取data_source_tbl表中所有记录的数据库信息
def get_data_source_records():
    # 连接数据源管理库
    source_db.connect(reuse_if_open=True)

    try:
        # 查询所有数据源记录
        data_sources = DataSourceModel.select()

        records = []
        for ds in data_sources:
            record = {
                'name': ds.name,
                'type': ds.type,
                'host': ds.host,
                'port': ds.port,
                'username': ds.username,
                'password': ds.password,
                'database': ds.database
            }
            records.append(record)

            # 通过统一接口获取该数据源的表
            try:
                tables = get_tables(DataSourceModel, ds.name)
                print(f"数据源 '{ds.name}' ({ds.type}) 下的表:")
                for t in tables:
                    print(f"  - {t['table']}")
            except Exception as e:
                print(f"枚举数据源 '{ds.name}' 的表时出错: {e}")

        return records
    except Exception as e:
        print(f"查询数据源信息时出错: {e}")
        return []
    finally:
        # 关闭数据库连接
        source_db.close()

if __name__ == '__main__':
    # test_datasource_connection()
    # test_database_tables()

    # 获取所有数据源记录
    print("\n获取所有数据源记录:")
    records = get_data_source_records()
    