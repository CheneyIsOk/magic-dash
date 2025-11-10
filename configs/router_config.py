import re
from typing import List, Union


class RouterConfig:
    """路由配置参数"""

    # 与应用首页对应的pathname地址
    index_pathname: str = "/index"

    # 核心页面侧边菜单完整结构
    core_side_menu: List[dict] = [
        # 主要页面
        {
            "component": "ItemGroup",
            "props": {
                "title": "主要页面",
                "key": "主要页面",
            },
            "children": [
                {
                    "component": "Item",
                    "props": {
                        "title": "首页",
                        "key": "/",
                        "icon": "antd-home",
                        "href": "/",
                    },
                },
            ],
        },

        # 数据资产
        {
            "component": "ItemGroup",
            "props": {
                "title": "数据资产",
                "key": "数据资产",
            },
            "children": [
                {
                    "component": "Item",
                    "props": {
                        "title": "资产盘点",
                        "key": "/core/asset-inventory",
                        "icon": "antd-file-text",
                        "href": "/core/asset-inventory",
                    },
                },
                {
                    "component": "Item",
                    "props": {
                        "title": "数据发现",
                        "key": "/core/asset-search",
                        "icon": "antd-file-search",
                        "href": "/core/asset-search",
                    },
                },
            ]
        },    

        # 数据质量
        {
            "component": "ItemGroup",
            "props": {
                "title": "数据质量",
                "key": "数据质量",
            },
            "children": [
                {
                    "component": "Item",
                    "props": {
                        "title": "数据质量检查",
                        "key": "/core/data-quality-page",
                        "icon": "pi-crosshair",
                        "href": "/core/data-quality-page",
                    },
                },
            ],
        },
        
        # 系统管理
        {
            "component": "ItemGroup",
            "props": {
                "title": "系统管理",
                "key": "系统管理",
            },
            "children": [
                {
                    "component": "Item",
                    "props": {
                        "title": "数据源管理",
                        "key": "/core/data-source-page",
                        "icon": "antd-database",
                        "href": "/core/data-source-page",
                    },
                },
                {
                    "component": "SubMenu",
                    "props": {
                        "key": "日志管理",
                        "title": "日志管理",
                        "icon": "antd-history",
                    },
                    "children": [
                        {
                            "component": "Item",
                            "props": {
                                "key": "/core/login-logs",
                                "title": "登录日志",
                                "icon": "antd-login",
                                "href": "/core/login-logs",
                            },
                        },
                    ],
                },
            ],
        },
    ]

    # 有效页面pathname地址 -> 页面标题映射字典
    valid_pathnames: dict = {
        "/login": "登录页",
        "/": "首页",
        index_pathname: "首页",
        "/core/page1": "主要页面1",
        "/core/login-logs": "登录日志",
        
        # 新增页面
        "/core/asset-inventory": "资产盘点",
        "/core/asset-search": "资产搜索",
        "/core/data-source-page": "数据源管理",
        "/core/data-quality-page": "数据质量检查",
        
        "/403-demo": "403状态页演示",
        "/404-demo": "404状态页演示",
        "/500-demo": "500状态页演示",
    }

    # 无需权限校验的公开页面
    public_pathnames: List[str] = [
        "/login",
        "/logout",
        "/403-demo",
        "/404-demo",
        "/500-demo",
    ]

    # 部分页面pathname对应要展开的子菜单层级
    side_menu_open_keys: dict = {
        "/core/sub-menu-page1": ["子菜单演示"],
        "/core/sub-menu-page2": ["子菜单演示"],
        "/core/sub-menu-page3": ["子菜单演示"],
        "/core/login-logs": ["日志管理"],
    }
