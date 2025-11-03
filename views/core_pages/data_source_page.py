import feffery_antd_components as fac
from dash import html
import callbacks.core_pages_c.data_source_c as data_source_c

from configs.database_config import DataSourceModel


def load_datasource_data():
    """ 从数据库加载数据源数据 """
    try:
        # 从数据库加载所有数据源
        query = DataSourceModel.select()
        data_sources = []
        
        for idx, ds in enumerate(query):
            data_sources.append({
                'key': str(idx + 1),
                'name': ds.name,
                'type': 'PostgreSQL' if ds.type == 'postgresql' else 'MySQL',
                'host': ds.host,
                'port': str(ds.port),
                'username': ds.username,
                'status': '已连接',
                'action': fac.AntdSpace([
                    fac.AntdButton('编辑', type='primary', size='small', id={'type': 'edit-btn', 'index': ds.name}),
                    fac.AntdButton('删除', type='primary', danger=True, size='small', id={'type': 'delete-btn', 'index': ds.name})
                ])
            })
        
        return data_sources
    except Exception as e:
        print(f"加载数据源列表失败: {e}")
        return []

def render():
    """ 子页面: 数据源管理界面 """
    # 加载数据源数据
    datasource_data = load_datasource_data()
    
    return fac.AntdSpace([
        fac.AntdRow([
            fac.AntdCol(
                fac.AntdButton('添加数据源', type='primary', icon=fac.AntdIcon(icon='antd-database'), id='add-datasource-btn'),
                span=24
            )
        ], style={'marginBottom': '16px'}),

        fac.AntdTable(
            id='datasource-table',
            columns=[
                {'title': '数据源名称', 'dataIndex': 'name', 'key': 'name'},
                {'title': '数据库类型', 'dataIndex': 'type', 'key': 'type'},
                {'title': '主机地址', 'dataIndex': 'host', 'key': 'host'},
                {'title': '端口', 'dataIndex': 'port', 'key': 'port'},
                {'title': '用户名', 'dataIndex': 'username', 'key': 'username'},
                {'title': '状态', 'dataIndex': 'status', 'key': 'status'},
                {'title': '操作', 'dataIndex': 'action', 'key': 'action'},
            ],
            data=datasource_data,
            bordered=True,
            size='middle',
            pagination={'pageSize': 10},
        ),
        
        # 添加数据源弹框
        fac.AntdModal(
            id='datasource-modal',
            title='添加数据源',
            visible=False,
            children=fac.AntdForm([
                html.Div(id='editing-datasource', style={'display': 'none'}),  # 隐藏状态变量，用于跟踪编辑模式
                fac.AntdFormItem(
                    fac.AntdInput(id='datasource-name', placeholder='请输入数据源名称'),
                    label='数据源名称',
                    required=True
                ),
                fac.AntdFormItem(
                    fac.AntdSelect(
                        id='datasource-type',
                        options=[
                            {'label': 'PostgreSQL', 'value': 'postgresql'},
                            {'label': 'MySQL', 'value': 'mysql'},
                        ],
                        placeholder='请选择数据库类型'
                    ),
                    label='数据库类型',
                    required=True
                ),
                fac.AntdFormItem(
                    fac.AntdInput(id='datasource-host', placeholder='请输入主机地址'),
                    label='主机地址',
                    required=True
                ),
                fac.AntdFormItem(
                    fac.AntdInputNumber(id='datasource-port', placeholder='请输入端口', style={'width': '100%'}),
                    label='端口',
                    required=True
                ),
                fac.AntdFormItem(
                    fac.AntdInput(id='datasource-database', placeholder='请输入数据库名'),
                    label='数据库名',
                    required=True
                ),
                fac.AntdFormItem(
                    fac.AntdInput(id='datasource-username', placeholder='请输入用户名'),
                    label='用户名',
                    required=True
                ),
                fac.AntdFormItem(
                    fac.AntdInput(id='datasource-password', placeholder='请输入密码', mode='password'),
                    label='密码',
                    required=True
                ),
                fac.AntdFormItem(
                    fac.AntdSpace([
                        fac.AntdRow([
                            fac.AntdCol(
                                fac.AntdButton('测试连接', type='primary', id='test-datasource-btn'),
                            ),
                            fac.AntdCol(
                                fac.AntdButton('保存连接', type='primary', id='save-datasource-btn'),
                            ),
                        ], gutter=20),
                    ], addSplitLine=True),
                    wrapperCol={'offset': 6}
                ),
                fac.AntdText(id='datasource-status', children='', style={}),
            ], labelCol={'span': 6}, wrapperCol={'span': 18}),
            okText='确定',
            cancelText='取消'
        )
    ], direction='vertical', size='large', style={'width': '100%'})
