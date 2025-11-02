import feffery_antd_components as fac
import callbacks.core_pages_c.data_source_c as data_source_c

from configs.database_config import source_db

db_configs = ['test']

def render():
    """ 子页面: 数据源管理界面 """
    
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
                {'title': '状态', 'dataIndex': 'status', 'key': 'status'},
                {'title': '操作', 'dataIndex': 'action', 'key': 'action'},
            ],
            data=[
                {
                    'key': str(i),
                    'name': f'数据源_{i}',
                    'type': 'PostgreSQL' if i % 2 == 0 else 'MySQL',
                    'host': '192.168.1.100',
                    'port': '5432' if i % 2 == 0 else '3306',
                    'status': '已连接',
                    'action': '编辑 | 删除'
                } for i in range(1, len(db_configs) + 1)
            ] if db_configs else [],
            bordered=True,
            size='middle'
        ),
        
        # 添加数据源弹框
        fac.AntdModal(
            id='datasource-modal',
            title='添加数据源',
            visible=False,
            children=fac.AntdForm([
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
