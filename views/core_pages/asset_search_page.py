"""
资产搜索页面
"""


from dash import html
import feffery_antd_components as fac

def render():
    """资产搜索页面"""
    return fac.AntdSpace(
        [
            fac.AntdBreadcrumb(items=[{"title": "数据资产"}, {"title": "资产搜索"}]),

            fac.AntdButton(
                "搜索",
                id="asset-search-btn",
                type="primary",
            ),
        ],
    ) 