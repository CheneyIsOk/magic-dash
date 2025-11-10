from dash import Input, Output, callback
import feffery_antd_components as fac
from configs.database_config import DataSourceModel
from peewee import SqliteDatabase, PostgresqlDatabase, MySQLDatabase
from utils.get_tables import get_tables
from utils.get_rules import get_dq_rules
from pathlib import Path


@callback(
    [
        Output('datasource-table-statistic', 'value'),
        Output('quality-rules-statistic', 'value'),
        Output('daily-checks-statistic', 'value'),
        Output('problem-data-statistic', 'value')
    ],
    Input('core-url', 'pathname')
)
def update_statistics(_: str) -> list:
    """首页统计：直接基于全部数据源进行汇总"""
    try:
        # 获取全部数据源的表总量
        all_tables = get_tables(dbmodel=DataSourceModel)
        datasource_count = len(all_tables)

        # 项目内置质量规则数量
        project_dir = Path(__file__).resolve().parents[2]
        dq_rules = get_dq_rules(project_dir)
        quality_rules_count = len(dq_rules)

        # 模拟统计（全部数据源）
        daily_checks_count = 156
        problem_data_count = 23

        return [
            datasource_count,
            quality_rules_count,
            daily_checks_count,
            problem_data_count,
        ]
    except Exception as e:
        print(f"更新统计数据失败: {e}")
        return [0, 0, 0, 0]


# 首页移除数据源筛选器，保留全局 Store 默认值（all）