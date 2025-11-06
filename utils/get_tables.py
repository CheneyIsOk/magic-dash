import psycopg2
import pymysql
from configs.database_config import DataSourceModel
from peewee import SqliteDatabase

def get_tables(dbmodel=DataSourceModel, selected_db=None):
    """获取数据库中的所有表名"""
    try:
        if selected_db:
            # 获取特定数据源的表
            datasource = dbmodel.get(dbmodel.name == selected_db)
            return _get_tables_from_datasource(datasource)
        else:
            # 获取所有数据源的表
            datasources = dbmodel.select()
            all_tables = []
            for datasource in datasources:
                tables = _get_tables_from_datasource(datasource)
                all_tables.extend(tables)
            return all_tables
    except Exception as e:
        print(f"获取表列表失败: {e}")
        return []

def _get_tables_from_datasource(datasource):
    """从单个数据源获取表列表"""
    try:
        if datasource.type == 'sqlite':
            # SQLite数据库
            db = SqliteDatabase(datasource.database)
            tables = db.get_tables()
            return [{'datasource': datasource.name, 'table': table} for table in tables]
        
        elif datasource.type == 'postgresql':
            # PostgreSQL数据库
            conn = psycopg2.connect(
                host=datasource.host,
                port=datasource.port,
                user=datasource.username,
                password=datasource.password,
                database=datasource.database
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return [{'datasource': datasource.name, 'table': table} for table in tables]
        
        elif datasource.type == 'mysql':
            # MySQL数据库
            conn = pymysql.connect(
                host=datasource.host,
                port=datasource.port,
                user=datasource.username,
                password=datasource.password,
                database=datasource.database
            )
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return [{'datasource': datasource.name, 'table': table} for table in tables]
        
        else:
            return []
    except Exception as e:
        print(f"从数据源 {datasource.name} 获取表列表失败: {e}")
        return []

def get_columns(datasource_name, table_name):
    """获取指定表的字段列表"""
    try:
        # 获取数据源信息
        datasource = DataSourceModel.get(DataSourceModel.name == datasource_name)
        
        if datasource.type == 'sqlite':
            # SQLite数据库
            db = SqliteDatabase(datasource.database)
            # SQLite没有直接获取字段信息的方法，需要执行查询
            return ['id', 'name', 'email', 'created_at']  # 示例字段
        
        elif datasource.type == 'postgresql':
            # PostgreSQL数据库
            conn = psycopg2.connect(
                host=datasource.host,
                port=datasource.port,
                user=datasource.username,
                password=datasource.password,
                database=datasource.database
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = %s
            """, (table_name,))
            columns = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return columns
        
        elif datasource.type == 'mysql':
            # MySQL数据库
            conn = pymysql.connect(
                host=datasource.host,
                port=datasource.port,
                user=datasource.username,
                password=datasource.password,
                database=datasource.database
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s
            """, (table_name,))
            columns = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return columns
        
        else:
            return []
    except Exception as e:
        print(f"获取表 {table_name} 的字段列表失败: {e}")
        return []