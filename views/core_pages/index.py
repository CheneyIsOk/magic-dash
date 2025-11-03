from dash import html
import feffery_antd_components as fac
from feffery_dash_utils.style_utils import style


# 模拟数据库连接配置
db_configs = []

# 模拟数据质量规则
quality_rules = []


def render():
    """子页面：首页渲染简单示例"""

    return fac.AntdSpace(
        [
            fac.AntdBreadcrumb(items=[{"title": "主要页面"}, {"title": "首页"}]),
            # 首页统计卡片
            fac.AntdRow([
                fac.AntdCol(
                    fac.AntdCard(
                        fac.AntdStatistic(
                            value=len(db_configs),
                            valueStyle={'color': '#1890ff'},
                            prefix=fac.AntdIcon(icon='antd-database'),
                        ),
                        title='数据源总数',
                        variant='borderless',
                        hoverable=True
                    ),
                    span=6
                ),
                fac.AntdCol(
                    fac.AntdCard(
                        fac.AntdStatistic(
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
            ], gutter=16, style={'marginBottom': '24px'}),
        ],
        direction="vertical",
        style=style(width="100%"),
    )
