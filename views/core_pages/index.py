from dash import html
import feffery_antd_components as fac
from feffery_dash_utils.style_utils import style
from configs.database_config import DataSourceModel


import callbacks.core_pages_c.index_c


def load_datasource_options():
    """从数据库加载数据源选项，生成下拉选择器的选项列表"""
    try:
        query = DataSourceModel.select()
        options = [{'label': '全部数据源', 'value': 'all'}]
        for ds in query:
            options.append({
                'label': f"{ds.name} ({ds.type})",
                'value': ds.name
            })
        return options
    except Exception as e:
        print(f"加载数据源选项失败: {e}")
        return [{'label': '全部数据源', 'value': 'all'}]

# 模拟数据质量规则
quality_rules = []


def render():
    """子页面：首页渲染简单示例"""
    # 加载数据源选项
    datasource_options = load_datasource_options()
    
    return fac.AntdSpace(
        [
            fac.AntdBreadcrumb(items=[{"title": "主要页面"}, {"title": "首页"}]),
            
            # 数据源筛选器
            fac.AntdRow([
                fac.AntdCol(
                    fac.AntdFormItem(
                        fac.AntdSelect(
                            id='datasource-filter',
                            options=datasource_options,
                            defaultValue='all',
                            placeholder='请选择数据源',
                            style={'width': '200px'}
                        ),
                        label='数据源筛选',
                    ),
                    span=24,
                    style={'textAlign': 'right', 'marginBottom': '16px'}
                )
            ]),
            
            # 首页统计卡片
            fac.AntdRow([
                fac.AntdCol(
                    fac.AntdCard(
                        fac.AntdStatistic(
                            id='datasource-table-statistic',
                            # value=len([opt for opt in datasource_options if opt['value'] != 'all']),
                            valueStyle={'color': '#1890ff'},
                            prefix=fac.AntdIcon(icon='antd-database'),
                        ),
                        title='数据表数量',
                        variant='borderless',
                        hoverable=True
                    ),
                    span=6
                ),
                fac.AntdCol(
                    fac.AntdCard(
                        fac.AntdStatistic(
                            id='quality-rules-statistic',
                            value=len(quality_rules),
                            valueStyle={'color': '#52c41a'},
                            prefix=fac.AntdIcon(icon='antd-bulb'),
                        ),
                        title='质量规则',
                        variant='borderless',
                        hoverable=True
                    ),
                    span=6
                ),
                fac.AntdCol(
                    fac.AntdCard(
                        fac.AntdStatistic(
                            id='daily-checks-statistic',
                            value=42,
                            valueStyle={'color': '#faad14'},
                            prefix=fac.AntdIcon(icon='antd-check-circle'),
                        ),
                        title='今日检查',
                        variant='borderless',
                        hoverable=True
                    ),
                    span=6
                ),
                fac.AntdCol(
                    fac.AntdCard(
                        fac.AntdStatistic(
                            id='problem-data-statistic',
                            value=5,
                            valueStyle={'color': '#f5222d'},
                            prefix=fac.AntdIcon(icon='antd-warning'),
                        ),
                        title='问题数据',
                        variant='borderless',
                        hoverable=True
                    ),
                    span=6
                ),
            ], gutter=15, style={'marginBottom': '24px'}),
        ],
        direction="vertical",
        style=style(width="100%"),
    )
