from dash import Input, Output, callback
import feffery_antd_components as fac
from configs.database_config import DataSourceModel
from peewee import SqliteDatabase, PostgresqlDatabase, MySQLDatabase
from utils.get_tables import get_tables


@callback(
    [
        Output('datasource-table-statistic', 'value'),
        Output('quality-rules-statistic', 'value'),
        Output('daily-checks-statistic', 'value'),
        Output('problem-data-statistic', 'value')
    ],
    Input('datasource-filter', 'value')
)
def update_statistics(selected_datasource):
    """根据选择的数据源更新统计信息"""
    
    try:
        # 获取数据表数量
        if selected_datasource == 'all':
            all_tables = get_tables(dbmodel=DataSourceModel)
            datasource_count = len(all_tables)
        else:
            # 选择了特定数据源
            print(f"selected specific datasource: {selected_datasource}")
            all_tables = get_tables(dbmodel=DataSourceModel, selected_db=selected_datasource)
            datasource_count = len(all_tables)
        
        # TODO: 目前使用模拟数据，后续可以接入真实的数据质量统计
        if selected_datasource == 'all':
            quality_rules_count = 15  # 全部数据源的质量规则总数
            daily_checks_count = 156  # 全部数据源的今日检查总数
            problem_data_count = 23   # 全部数据源的问题数据总数
        else:
            # 单个数据源的模拟统计
            quality_rules_count = 5
            daily_checks_count = 42
            problem_data_count = 5

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
def refresh_datasource_options(_):
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