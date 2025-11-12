"""
资产盘点页面：
1. 【暂时不管】管理的数据资产分布：展示当前系统管理下的所有数据资产，包括数据库、数据仓库、数据湖等。
2. 数据存储资源占用：展示当前系统中数据资产占用的存储资源。
3. 数据表行数：展示当前系统中所有数据表的行数。
4. 数据地图功能：
    * 数据资产详情：单独页面。点击某个数据资产，展示其详细信息，包括数据资产类型、数据资产名称、数据资产描述、数据资产存储位置、数据资产占用的存储资源、数据资产的行数等。
    * 数据发现：单独页面。对话沟通方式，用户可以通过对话的方式，向系统咨询数据资产相关的问题，系统会根据用户的问题，从数据库中查询相关的信息，并返回给用户。

记录的信息存储在database/data_asset.db
"""

from dash import html
import feffery_antd_components as fac
import feffery_antd_charts as fac_charts
from feffery_dash_utils.style_utils import style

import callbacks.core_pages_c.asset_inventory_c  # noqa: F401


def render():
    """资产盘点页面"""
    return fac.AntdSpace(
        [
            fac.AntdBreadcrumb(items=[{"title": "数据资产"}, {"title": "资产盘点"}]),
            
            html.Br(),

            # 筛选器
            fac.AntdRow([
                fac.AntdCol(
                    fac.AntdText("数据源：", style={'fontSize': '14px'}),
                ),
                fac.AntdCol(
                    fac.AntdSelect(
                        id='ai-snapshot-ds-select',
                        options=[],
                        defaultValue='all',
                        placeholder='请选择数据源',
                        style={'width': '120px'}
                    ),
                ),
                fac.AntdCol(
                    fac.AntdText("时间范围：", style={'fontSize': '14px'}),
                ),
                fac.AntdCol(
                    fac.AntdRadioGroup(
                        id="ai-time-range",
                        options=["近一周", "近一月", "近三月", "近半年"],
                        defaultValue="近一周",
                        optionType="button",
                        buttonStyle="solid",
                    ),
                ),
            ], gutter=10),

            html.Br(),
            
            # 表命名开头 ods/dim/dwd/dws/ads 分布（饼图）与每日总量（柱状图）
            fac.AntdRow([
                fac.AntdCol(
                    fac_charts.AntdPie(
                        id='ai-prefix-pie',
                        data=[],
                        colorField='type',
                        angleField='value',
                        radius=0.8,
                        innerRadius=0.5,
                        height=300,
                    ),
                    span=9,
                ),
                # 资产占用存储资源（双轴折线图：左轴=每日总量，右轴=每日表数量）
                fac.AntdCol(
                    fac.AntdSpace([
                        fac.AntdText(id='ai-volume-unit-text', type='secondary'),
                        fac_charts.AntdDualAxes(
                            id='ai-volume-dual',
                            data=[[], []],
                            xField='date',
                            yField=['y1', 'y2'],
                            geometryOptions=[
                                {
                                    'geometry': 'line', 
                                    'smooth': True,
                                    'point': {
                                        'shape': 'circle',
                                        'size': 4,
                                        'style': {
                                            'opacity': 0.5,
                                            'stroke': '#5AD8A6',
                                            'fill': '#fff',
                                        },
                                    },
                                }, 
                                {
                                    'geometry': 'column',
                                    'barSize': 12,
                                }   
                            ],  # 左边=line，右边=column
                            legend={'position': 'top'},
                            # 初始轴标题，回调会动态更新左轴单位
                            yAxis={
                                'left': {'min': 0, 'title': {'text': '每日总量（存储）'}},
                                'right': {'min': 0, 'title': {'text': '每日表数量（张）'}}
                            },
                            # 优化图例与tooltip字段名，避免显示 y1/y2
                            meta={
                                'y1': {'alias': '每日总量（存储）'},
                                'y2': {'alias': '每日表数量（张）'}
                            },
                            height=300,
                        ),
                    ], direction='vertical', style={'width': '100%'}),
                    span=15,
                ),
            ], gutter=16),

            # 今日占用Top10（读取快照库）
            fac.AntdCard(
                title="今日占用 Top10（快照库）",
                children=fac.AntdForm(
                    [
                        fac.AntdRow([
                            fac.AntdCol(
                                fac.AntdFormItem(
                                    fac.AntdSpace([
                                        fac.AntdButton(
                                            "刷新今日Top10",
                                            id="ai-snapshot-refresh",
                                            type="primary",
                                        ),
                                        fac.AntdText(id="ai-snapshot-dt-text", type="secondary"),
                                        fac.AntdText(id="ai-snapshot-run-status", type="secondary"),
                                    ]),
                                    label="操作",
                                ),
                                span=16,
                            ),
                        ], gutter=16),
                        fac.AntdTable(
                            id="ai-snapshot-top10-table",
                            columns=[],
                            data=[],
                            bordered=True,
                            pagination={"pageSize": 10},
                            size="small",
                        ),
                    ],
                    layout="vertical",
                ),
                variant="borderless",
            ),
        ],
        direction="vertical",
        style=style(width="100%",),
    )
