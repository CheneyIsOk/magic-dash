from typing import Literal
import pathlib
from peewee import SqliteDatabase, CharField, IntegerField, Model


DATA_SOURCE_DB = "data_source.db"
DATA_SOURCE_TABLE_NAME = "data_source"

source_db_path = pathlib.Path(__file__).parent.parent / "database" / DATA_SOURCE_DB
source_db = SqliteDatabase(source_db_path)


class DataSourceModel(Model):
    """ 保存的数据源表模型 """
    name = CharField(max_length=128, unique=True)
    type = CharField(max_length=32)
    host = CharField(max_length=128)
    port = IntegerField()
    username = CharField(max_length=128)
    password = CharField(max_length=128)
    database = CharField(max_length=128)

    class Meta:
        database = source_db
        table_name = DATA_SOURCE_TABLE_NAME

# 确保数据库表存在
source_db.connect()
if not source_db.table_exists(DATA_SOURCE_TABLE_NAME):
    source_db.create_tables([DataSourceModel])
source_db.close()


class DatabaseConfig:
    """数据库配置参数"""

    # 应用基础数据库类型
    # 当使用postgresql类型时，请使用`pip install psycopg2-binary`安装必要依赖
    # 当使用mysql类型时，请使用`pip install pymysql`安装必要依赖
    database_type: Literal["sqlite", "postgresql", "mysql"] = "sqlite"

    # 当database_type为'postgresql'时，对应的数据库连接配置参数，使用时请根据实际情况修改
    postgresql_config = {
        "host": "127.0.0.1",
        "port": 5432,
        "user": "root",
        "password": "admin123",
        "database": "magic_dash_pro",
    }

    # 当database_type为'mysql'时，对应的数据库连接配置参数，使用时请根据实际情况修改
    mysql_config = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "admin123",
        "database": "magic_dash_pro",
    }
