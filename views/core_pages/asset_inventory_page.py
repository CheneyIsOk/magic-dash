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
from feffery_dash_utils.style_utils import style

import callbacks.core_pages_c.asset_inventory_c  # noqa: F401


def render():
    """资产盘点页面"""
    return fac.AntdSpace(
        [
            fac.AntdBreadcrumb(items=[{"title": "数据资产"}, {"title": "资产盘点"}]),
             
            # 数据源筛选器
            fac.AntdRow([
                fac.AntdCol(
                    fac.AntdFormItem(
                        fac.AntdSelect(
                            id='ai-snapshot-ds-select',
                            options=[],
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
