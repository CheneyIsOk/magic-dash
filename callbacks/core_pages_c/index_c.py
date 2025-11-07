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
    Input('datasource-filter', 'value')
)
def update_statistics(selected_datasource: str) -> list:
    """根据选择的数据源更新统计信息"""
    
    try:
        # 获取数据表数量
        if selected_datasource == 'all' or selected_datasource is None:
            all_tables = get_tables(dbmodel=DataSourceModel)
            datasource_count = len(all_tables)
        else:
            # 选择了特定数据源
            all_tables = get_tables(dbmodel=DataSourceModel, selected_db=selected_datasource)
            datasource_count = len(all_tables)
        
        # 基于项目内置规则统计质量规则数量
        project_dir = Path(__file__).resolve().parents[2]
        dq_rules = get_dq_rules(project_dir)
        quality_rules_count = len(dq_rules)

        # 其他统计暂时保留模拟数据，后续接入真实统计
        if selected_datasource == 'all':
            daily_checks_count = 156  # 全部数据源的今日检查总数（模拟）
            problem_data_count = 23   # 全部数据源的问题数据总数（模拟）
        else:
            daily_checks_count = 42   # 单个数据源的今日检查总数（模拟）
            problem_data_count = 5    # 单个数据源的问题数据总数（模拟）

        return [
            datasource_count,
            quality_rules_count, 
            daily_checks_count,
            problem_data_count
        ]
        
    except Exception as e:
        print(f"更新统计数据失败: {e}")
        # 出错时返回默认值
        return [0, 0, 0, 0]


@callback(
    Output('datasource-filter', 'options'),
    Input('datasource-filter', 'id')  # 使用组件ID作为触发器，页面加载时执行
)
def refresh_datasource_options(_: str) -> list:
    """刷新数据源选项列表"""
    try:
        query = DataSourceModel.select()
        options = [{'label': '全部数据源', 'value': 'all'}]
        
        for ds in query:
            db_type = 'PostgreSQL' if ds.type == 'postgresql' else 'MySQL'
            options.append({
                'label': f"{ds.name} ({db_type})",
                'value': ds.name
            })
        
        return options
        
    except Exception as e:
        print(f"刷新数据源选项失败: {e}")
        return [{'label': '全部数据源', 'value': 'all'}]


@callback(
    Output('active-datasource', 'data'),
    Input('datasource-filter', 'value'),
    prevent_initial_call=True
)
def sync_active_datasource(selected_datasource: str) -> str:
    """同步全局当前活跃数据源Store"""
    return selected_datasource or 'all'