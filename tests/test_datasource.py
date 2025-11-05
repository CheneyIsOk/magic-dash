import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from configs.database_config import DataSourceModel, source_db
from peewee import SqliteDatabase, PostgresqlDatabase, MySQLDatabase

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
    tables = source_db.get_tables()
    print("数据库中的表:", tables)
    assert tables is not None, "获取数据库表失败"
    assert len(tables) > 0, "数据库中没有表"


# 获取data_source_tbl表中所有记录的数据库信息
def get_data_source_records():
    # 连接数据库
    source_db.connect(reuse_if_open=True)
    
    try:
        # 查询所有数据源记录
        data_sources = DataSourceModel.select()
        
        # 遍历并打印每条记录的详细信息
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
            
            # 连接record对应的数据库并获取其下数据库表
            try:
                # 根据数据源类型创建相应的数据库连接
                if ds.type.lower() == 'sqlite':
                    # SQLite数据库
                    db_conn = SqliteDatabase(ds.database)
                elif ds.type.lower() == 'postgresql':
                    # PostgreSQL数据库
                    db_conn = PostgresqlDatabase(
                        ds.database,
                        host=ds.host,
                        port=ds.port,
                        user=ds.username,
                        password=ds.password
                    )
                elif ds.type.lower() == 'mysql':
                    # MySQL数据库
                    db_conn = MySQLDatabase(
                        ds.database,
                        host=ds.host,
                        port=ds.port,
                        user=ds.username,
                        passwd=ds.password
                    )
                else:
                    print(f"不支持的数据库类型: {ds.type}")
                    continue
                
                # 连接数据库并获取表列表
                db_conn.connect()
                tables = db_conn.get_tables()
                print(f"数据源 '{ds.name}' ({ds.type}) 下的表:")
                for table in tables:
                    print(f"  - {table}")
                db_conn.close()
                
            except Exception as e:
                print(f"连接数据源 '{ds.name}' 时出错: {e}")
            
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
    