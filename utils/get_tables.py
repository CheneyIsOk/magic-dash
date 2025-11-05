from re import M
from peewee import SqliteDatabase, PostgresqlDatabase, MySQLDatabase, Model



def get_tables(dbmodel: Model, selected_db='all'):
    """根据数据源模型获取所有数据源的表信息"""

    if selected_db != 'all' and selected_db != None: 
        data_sources = dbmodel.select().where(dbmodel.name == selected_db)
    else:
        data_sources = dbmodel.select()

    records= []
    all_tables= []
    for ds in data_sources:
        records.append({
            'name': ds.name,
            'type': ds.type,
            'host': ds.host,
            'port': ds.port,
            'username': ds.username,
            'password': ds.password,
            'database': ds.database
        })
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
            all_tables.extend(tables)
            print(f"数据源 '{ds.name}' ({ds.type}) 下的表: {tables}")
            db_conn.close()
        except Exception as e:
            print(f"连接数据源 '{ds.name}' 时出错: {e}")
    return all_tables
