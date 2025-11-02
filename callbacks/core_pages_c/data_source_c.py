from sqlalchemy import create_engine
from dash import Input, Output, State, callback


@callback(
    Output('datasource-modal', 'visible'),
    Input('add-datasource-btn', 'nClicks'),
    prevent_initial_call=True
)
def toggle_datasource_modal(n_clicks):
    """ 点击添加数据源按钮，切换数据源弹窗显示状态 """
    return True


@callback(
    [
        Output('datasource-status', 'children'),
        Output('datasource-status', 'style'),
    ],
    Input('test-datasource-btn', 'nClicks'),
    [
        State('datasource-name', 'value'),
        State('datasource-type', 'value'),
        State('datasource-host', 'value'),
        State('datasource-port', 'value'),
        State('datasource-database', 'value'),
        State('datasource-username', 'value'),
        State('datasource-password', 'value'),
    ],
    prevent_initial_call=True
)
def validate_datasource_connection(n_clicks, datasource_name, datasource_type, datasource_host, datasource_port, datasource_database, datasource_username, datasource_password):
    """ 点击测试连接按钮，检测数据库连接状态 """
    if not all([datasource_name, datasource_type, datasource_host, datasource_port, datasource_database, datasource_username, datasource_password]):
        return '请填写完整的数据库连接信息', {'color': 'red'}
    
    # 根据数据库类型构建连接字符串
    if datasource_type == 'postgresql':
        conn_str = f"postgresql://{datasource_username}:{datasource_password}@{datasource_host}:{datasource_port}/{datasource_database}"
    elif datasource_type == 'mysql':
        conn_str = f"mysql+pymysql://{datasource_username}:{datasource_password}@{datasource_host}:{datasource_port}/{datasource_database}"
    else:
        return f"不支持的数据库类型: {datasource_type}", {'color': 'red'}
    
    try:
        engine = create_engine(conn_str)
        with engine.connect() as conn:
            print("连接成功！")
            return "数据库连接成功", {'color': 'green'}
    except Exception as e:
        print(f"连接失败：{e}")
        return f"数据库连接失败: {str(e)}", {'color': 'red'}


# @callback(
#     Output('datasource-table', 'children'),
#     Input('save-datasource-btn', 'nClicks'),
#     [
#         State('datasource-name', 'value'),
#         State('datasource-type', 'value'),
#         State('datasource-host', 'value'),
#         State('datasource-port', 'value'),
#         State('datasource-database', 'value'),
#         State('datasource-username', 'value'),
#         State('datasource-password', 'value'),
#     ],
#     prevent_initial_call=True
# )
# def save_datasource_connection(n_clicks, datasource_name, datasource_type, datasource_host, datasource_port, datasource_database, datasource_username, datasource_password):
#     """ 点击保存按钮，保存数据库连接信息 """
#     if not all([datasource_name, datasource_type, datasource_host, datasource_port, datasource_database, datasource_username, datasource_password]):
#         return '请填写完整的数据库连接信息', {'color': 'red'}
    
#     try:
#         engine = create_engine(conn_str)
#         with engine.connect() as conn:
#             print("连接成功！")
#             return "数据库连接成功", {'color': 'green'}
#     except Exception as e:
#         print(f"连接失败：{e}")
#         return f"数据库连接失败: {str(e)}", {'color': 'red'}