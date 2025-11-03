from sqlalchemy import create_engine
from dash import Input, Output, State, callback, ALL, callback_context
from configs.database_config import DataSourceModel, source_db


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
    Input('test-connection-btn', 'nClicks'),
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


@callback(
    [
        Output('datasource-table', 'data'),
        Output('datasource-modal', 'visible', allow_duplicate=True),
        Output('datasource-status', 'children', allow_duplicate=True),
        Output('datasource-status', 'style', allow_duplicate=True),
    ],
    Input('save-datasource-btn', 'nClicks'),
    [
        State('datasource-name', 'value'),
        State('datasource-type', 'value'),
        State('datasource-host', 'value'),
        State('datasource-port', 'value'),
        State('datasource-database', 'value'),
        State('datasource-username', 'value'),
        State('datasource-password', 'value'),
        State('datasource-table', 'data'),
        State('editing-datasource', 'children'),  # 获取编辑模式状态
    ],
    prevent_initial_call=True
)
def save_datasource_connection(n_clicks, datasource_name, datasource_type, datasource_host, datasource_port, 
                              datasource_database, datasource_username, datasource_password, current_data, editing_datasource):
    """ 点击保存按钮，保存数据库连接信息到data_source.db """
    if not all([datasource_name, datasource_type, datasource_host, datasource_port, datasource_database, datasource_username, datasource_password]):
        return current_data, True, '请填写完整的数据库连接信息', {'color': 'red'}
    
    # 根据数据库类型构建连接字符串
    if datasource_type == 'postgresql':
        conn_str = f"postgresql://{datasource_username}:{datasource_password}@{datasource_host}:{datasource_port}/{datasource_database}"
    elif datasource_type == 'mysql':
        conn_str = f"mysql+pymysql://{datasource_username}:{datasource_password}@{datasource_host}:{datasource_port}/{datasource_database}"
    else:
        return current_data, True, f"不支持的数据库类型: {datasource_type}", {'color': 'red'}
    
    try:
        # 测试连接
        engine = create_engine(conn_str)
        with engine.connect() as conn:
            pass
        
        # 保存到data_source.db
        try:
            with source_db.atomic():
                # 检查是否是编辑模式
                is_editing = editing_datasource and editing_datasource != ''
                
                if is_editing:
                    # 编辑模式 - 更新现有记录
                    existing = DataSourceModel.select().where(DataSourceModel.name == editing_datasource).first()
                    if existing:
                        # 如果名称改变了，需要检查新名称是否已存在
                        if editing_datasource != datasource_name:
                            name_exists = DataSourceModel.select().where(DataSourceModel.name == datasource_name).first()
                            if name_exists:
                                return current_data, True, f"数据源名称 '{datasource_name}' 已存在", {'color': 'red'}
                        
                        # 更新记录
                        existing.name = datasource_name
                        existing.type = datasource_type
                        existing.host = datasource_host
                        existing.port = datasource_port
                        existing.database = datasource_database
                        existing.username = datasource_username
                        existing.password = datasource_password
                        existing.save()
                else:
                    # 新增模式 - 检查是否已存在同名数据源
                    existing = DataSourceModel.select().where(DataSourceModel.name == datasource_name).first()
                    if existing:
                        return current_data, True, f"数据源名称 '{datasource_name}' 已存在", {'color': 'red'}
                    
                    # 创建新数据源记录
                    DataSourceModel.create(
                        name=datasource_name,
                        type=datasource_type,
                        host=datasource_host,
                        port=datasource_port,
                        database=datasource_database,
                        username=datasource_username,
                        password=datasource_password
                    )
                
                # 重新加载表格数据
                from views.core_pages.data_source_page import load_datasource_data
                updated_data = load_datasource_data()
                
                return updated_data, False, '数据源保存成功！', {'color': 'green'}
                
        except Exception as e:
            print(f"保存数据源失败: {e}")
            return current_data, True, f"保存数据源失败: {str(e)}", {'color': 'red'}
            
    except Exception as e:
        print(f"连接失败：{e}")
        return current_data, True, f"数据库连接失败: {str(e)}", {'color': 'red'}


@callback(
    Output('datasource-table', 'data', allow_duplicate=True),
    Input({'type': 'delete-btn', 'index': ALL}, 'nClicks'),
    State('datasource-table', 'data'),
    prevent_initial_call=True
)
def delete_datasource(n_clicks_list, current_data):
    """ 删除数据源 """
    if not any(n_clicks_list):
        return current_data
    
    # 获取触发删除的按钮ID
    ctx = callback_context
    if not ctx.triggered:
        return current_data
    
    # 从按钮ID中提取数据源名称
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    import json
    button_data = json.loads(button_id.replace("'", '"'))
    datasource_name = button_data['index']
    
    try:
        # 从数据库删除数据源
        with source_db.atomic():
            DataSourceModel.delete().where(DataSourceModel.name == datasource_name).execute()
        
        # 重新加载表格数据
        from views.core_pages.data_source_page import load_datasource_data
        updated_data = load_datasource_data()
        
        return updated_data
        
    except Exception as e:
        print(f"删除数据源失败: {e}")
        return current_data


@callback(
    [
        Output('datasource-modal', 'visible', allow_duplicate=True),
        Output('datasource-name', 'value'),
        Output('datasource-type', 'value'),
        Output('datasource-host', 'value'),
        Output('datasource-port', 'value'),
        Output('datasource-database', 'value'),
        Output('datasource-username', 'value'),
        Output('datasource-password', 'value'),
        Output('editing-datasource', 'children'),
        Output('datasource-modal', 'title'),
    ],
    Input({'type': 'edit-btn', 'index': ALL}, 'nClicks'),
    prevent_initial_call=True
)
def edit_datasource(n_clicks_list):
    """ 编辑数据源 - 打开模态框并填充数据 """
    if not any(n_clicks_list):
        return [False] + [''] * 8 + ['', '添加数据源']
    
    # 获取触发编辑的按钮ID
    ctx = callback_context
    if not ctx.triggered:
        return [False] + [''] * 8 + ['', '添加数据源']
    
    # 从按钮ID中提取数据源名称
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    import json
    button_data = json.loads(button_id.replace("'", '"'))
    datasource_name = button_data['index']
    
    try:
        # 从数据库获取数据源信息
        datasource = DataSourceModel.select().where(DataSourceModel.name == datasource_name).first()
        if datasource:
            return [
                True,  # 打开模态框
                datasource.name,
                datasource.type,
                datasource.host,
                datasource.port,
                datasource.database,
                datasource.username,
                datasource.password,
                datasource.name,  # 设置编辑模式
                '编辑数据源'  # 修改标题
            ]
        else:
            return [False] + [''] * 8 + ['', '添加数据源']
            
    except Exception as e:
        print(f"加载数据源信息失败: {e}")
        return [False] + [''] * 8 + ['', '添加数据源']


@callback(
    [
        Output('datasource-name', 'value', allow_duplicate=True),
        Output('datasource-type', 'value', allow_duplicate=True),
        Output('datasource-host', 'value', allow_duplicate=True),
        Output('datasource-port', 'value', allow_duplicate=True),
        Output('datasource-database', 'value', allow_duplicate=True),
        Output('datasource-username', 'value', allow_duplicate=True),
        Output('datasource-password', 'value', allow_duplicate=True),
        Output('editing-datasource', 'children', allow_duplicate=True),
        Output('datasource-modal', 'title', allow_duplicate=True),
    ],
    Input('add-datasource-btn', 'nClicks'),
    prevent_initial_call=True
)
def reset_modal_fields(n_clicks):
    """ 重置模态框字段 - 当点击添加按钮时 """
    if n_clicks:
        return [''] * 7 + ['', '添加数据源']
    return [''] * 7 + ['', '添加数据源']
