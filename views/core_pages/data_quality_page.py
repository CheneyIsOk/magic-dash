""" 
数据质量检查页面
① 数据源选择区（选择数据库连接）
② 表与字段选择区（下拉选择表、可多选字段）
③ 规则与参数配置区（选择规则模板 + 输入参数）
④ 执行与结果展示区（开始按钮 + 结果展示面板）
"""

import feffery_antd_components as fac
from dash import html, dcc
from configs.database_config import DataSourceModel

import callbacks.core_pages_c.data_quality_c

def render():
    """ 子页面: 数据质量检查界面 """
    return fac.AntdSpace([
        fac.AntdBreadcrumb(items=[{"title": "数据质量"}, {"title": "数据质检"}]),

        fac.AntdRow([
            # 数据源选择区
            fac.AntdCol(
                fac.AntdCard(
                    title='数据源选择',
                    children=[
                        fac.AntdFormItem(
                            fac.AntdSelect(
                                id='dq-datasource-select',
                                placeholder='请选择数据源',
                                options=[],
                                style={'width': 120}
                            ),
                            label='数据源'
                        )
                    ],
                    style={'height': '100%'}
                ),
                span=6
            ),
            # 表与字段选择区
            fac.AntdCol(
                fac.AntdCard(
                    title='表与字段选择',
                    children=[
                        fac.AntdFormItem(
                            fac.AntdSelect(
                                id='dq-table-select',
                                placeholder='请选择表',
                                options=[],
                                style={'width': 120}
                            ),
                            label='表名'
                        ),
                        fac.AntdFormItem(
                            fac.AntdSelect(
                                id='dq-column-select',
                                placeholder='请选择字段（可多选）',
                                options=[],
                                mode='multiple',
                                style={'width': 120}
                            ),
                            label='字段'
                        )
                    ],
                    style={'height': '100%'}
                ),
                span=6
            ),
            # 规则与参数配置区
            fac.AntdCol(
                fac.AntdCard(
                    title='检查规则与参数配置',
                    children=[
                        fac.AntdFormItem(
                            fac.AntdSelect(
                                id='dq-check-type',
                                placeholder='请选择检查类型',
                                options=[
                                    {'label': '完整性', 'value': 'completeness'},
                                    {'label': '唯一性', 'value': 'uniqueness'},
                                    {'label': '准确性', 'value': 'accuracy'},
                                    {'label': '一致性', 'value': 'consistency'},
                                    {'label': '时效性', 'value': 'freshness'}
                                ],
                                style={'width': '100%'}
                            ),
                            label='检查类型'
                        ),
                        fac.AntdFormItem(
                            fac.AntdSelect(
                                id='dq-rule-template',
                                placeholder='请选择规则模板',
                                options=[],
                                style={'width': '100%'}
                            ),
                            label='规则模板'
                        ),
                        html.Div(id='dq-dynamic-params', children=[]),
                        fac.AntdFormItem(
                            fac.AntdInputNumber(
                                id='dq-threshold',
                                placeholder='请输入阈值',
                                style={'width': '100%'}
                            ),
                            label='阈值'
                        ),
                        fac.AntdFormItem(
                            fac.AntdInput(
                                id='dq-description',
                                placeholder='请输入规则描述（可选）',
                                style={'width': '100%'}
                            ),
                            label='备注'
                        )
                    ],
                    style={'height': '100%'}
                ),
                span=12
            )
        ], gutter=10),
        
        # 操作按钮区 + TODO: 后续加上loading进度条
        fac.AntdRow([
            fac.AntdSpace([
                    fac.AntdButton(
                        '开始检查',
                        id='dq-start-check',
                        type='primary',
                    ),
                    fac.AntdButton(
                        '终止检查',
                        id='dq-terminate-check',
                        type='primary',
                    ),
            ]),
        ]), 

        # 执行与结果展示区
        fac.AntdRow([
            fac.AntdCol(
                children=[
                    fac.AntdTabs(
                        items=[
                            {
                                'key': 'result',
                                'label': '检查结果',
                                'children': fac.AntdSpin(
                                    html.Div(
                                        id='dq-result-display',
                                        children=[
                                            fac.AntdEmpty(description='请先配置检查规则并点击开始检查')
                                        ],
                                        style={'minHeight': '200px', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}
                                    ),
                                    text='正在执行检查...',
                                    spinning=False
                                )
                            },
                            {
                                'key': 'log',
                                'label': '执行日志',
                                'children': fac.AntdSpin(
                                    html.Div(
                                        id='dq-log-display',
                                        children=[
                                            fac.AntdEmpty(description='暂无执行日志')
                                        ],
                                        style={'minHeight': '200px'}
                                    ),
                                    text='正在获取日志...',
                                    spinning=False
                                )
                            }
                        ],
                        id='dq-result-tabs'
                    )
                ], span=24
            ),
        ], style={'width': '100%'}),
        
        # 隐藏组件用于存储状态
        html.Div(id='dq-selected-datasource', style={'display': 'none'}),
        html.Div(id='dq-selected-table', style={'display': 'none'}),
        html.Div(id='dq-selected-columns', style={'display': 'none'})
    ], direction='vertical', size='large', style={'width': '100%'})