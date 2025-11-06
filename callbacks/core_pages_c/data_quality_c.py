import dash
from dash import Input, Output, State, callback
from configs.database_config import DataSourceModel, source_db
import feffery_antd_components as fac
import pathlib
from utils.get_tables import get_tables, get_columns
from typing import Optional, List, Tuple, Any

# 获取项目根目录
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent

from utils.get_rules import get_dq_rules

@callback(
    Output('dq-datasource-select', 'options'),
    Input('dq-datasource-select', 'id')  # 触发加载数据源列表
)
def load_datasource_options(trigger):
    """加载数据源选项"""
    try:
        # 从数据库加载所有数据源
        query = DataSourceModel.select()
        options = []
        
        for ds in query:
            options.append({
                'label': ds.name,
                'value': ds.name
            })
        
        return options
    except Exception as e:
        print(f"加载数据源列表失败: {e}")
        return []

@callback(
    [
        Output('dq-table-select', 'options'),
        Output('dq-selected-datasource', 'children')
    ],
    Input('dq-datasource-select', 'value')
)
def load_table_options(datasource_name):
    """根据选择的数据源加载表列表"""
    if not datasource_name:
        return [], ''
    
    try:
        sample_tables = get_tables(DataSourceModel, datasource_name)
        
        options = [{'label': info['table'], 'value': info['table']} for info in sample_tables]
        
        return options, datasource_name
    except Exception as e:
        print(f"加载表列表失败: {e}")
        return [], datasource_name

@callback(
    [
        Output('dq-column-select', 'options'),
        Output('dq-selected-table', 'children')
    ],
    Input('dq-table-select', 'value'),
    State('dq-selected-datasource', 'children')
)
def load_column_options(table_name, datasource_name):
    """根据选择的表加载字段列表"""
    if not table_name or not datasource_name:
        return [], ''
    
    try:
        # 获取字段列表
        columns = get_columns(datasource_name, table_name)
        options = [{'label': col, 'value': col} for col in columns]
        
        return options, table_name
    except Exception as e:
        print(f"加载字段列表失败: {e}")
        return [], table_name

@callback(
    Output('dq-rule-template', 'options'),
    Input('dq-check-type', 'value')
)
def load_rule_templates(check_type):
    """根据检查类型加载规则模板"""
    if not check_type:
        return []
    
    # 获取所有规则
    all_rules = get_dq_rules(PROJECT_ROOT)
    print(f"all_rules : {all_rules}")
    # 根据检查类型过滤规则
    filtered_rules = [rule for rule in all_rules if rule['dimension'] == check_type]
    
    # 转换为选项格式
    options = [{'label': rule['label'], 'value': rule['value']} for rule in filtered_rules]
    
    return options

@callback(
    Output('dq-dynamic-params', 'children'),
    Input('dq-rule-template', 'value')
)
def generate_dynamic_params(rule_template):
    """根据选择的规则模板动态生成参数输入框"""
    if not rule_template:
        return []
    
    try:
        # 解析规则模板路径
        parts = rule_template.split('/')
        if len(parts) != 2:
            return []
        
        dimension, template_name = parts
        
        # 构建SQL文件路径
        sql_file_path = PROJECT_ROOT / "dq_checks" / "sql" / dimension / f"{template_name}.sql"
        
        if not sql_file_path.exists():
            return []
        
        # 读取SQL文件内容
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 提取模板变量（{{ variable }}格式）
        import re
        variables = re.findall(r'\{\{\s*(\w+)\s*\}\}', sql_content)
        
        # 去重
        unique_variables = list(set(variables))
        
        # 生成参数输入框
        param_inputs = []
        for var in unique_variables:
            param_inputs.append(
                fac.AntdFormItem(
                    fac.AntdInput(
                        id=f'dq-param-{var}',
                        placeholder=f'请输入{var}的值',
                        style={'width': '100%'}
                    ),
                    label=var
                )
            )
        
        return param_inputs
    except Exception as e:
        print(f"生成动态参数输入框失败: {e}")
        return []

@callback(
    [
        Output('dq-result-display', 'children'),
        Output('dq-log-display', 'children')
    ],
    Input('dq-start-check', 'nClicks'),
    [
        State('dq-datasource-select', 'value'),
        State('dq-table-select', 'value'),
        State('dq-column-select', 'value'),
        State('dq-check-type', 'value'),
        State('dq-rule-template', 'value'),
        State('dq-threshold', 'value'),
        State('dq-description', 'value')
    ],
    prevent_initial_call=True
)
def execute_data_quality_check(
    n_clicks: int,
    datasource_name: Optional[str],
    table_name: Optional[str],
    column_names: Optional[List[str]],
    check_type: Optional[str],
    rule_template: Optional[str],
    threshold: Optional[float],
    description: Optional[str]
) -> Tuple[Any, Any]:
    """执行数据质量检查（示例）

    说明：保持 KISS，当前仅构造示例结果与日志；
    后续接入 dq_checks/sql 的真实执行时在此扩展。
    """

    if not n_clicks:
        return dash.no_update

    # 检查必要参数
    if not all([datasource_name, table_name, rule_template]):
        result_display = fac.AntdAlert(
            message='参数不完整',
            description='请确保已选择数据源、表名和规则模板',
            type='error',
            showIcon=True
        )
        log_placeholder = fac.AntdEmpty(description='暂无执行日志')
        return result_display, log_placeholder

    try:
        # 获取数据源信息（示例用，不强制使用）
        _ = DataSourceModel.get(DataSourceModel.name == datasource_name)

        # 构建检查结果展示
        result_content = fac.AntdSpace([
            fac.AntdDescriptions(
                items=[
                    {'label': '数据源', 'children': datasource_name},
                    {'label': '表名', 'children': table_name},
                    {'label': '字段', 'children': ', '.join(column_names or []) or '未选择'},
                    {'label': '检查类型', 'children': check_type or '未指定'},
                    {'label': '规则模板', 'children': rule_template},
                    {'label': '阈值', 'children': str(threshold) if threshold is not None else '未设置'},
                    {'label': '备注', 'children': description or '无'}
                ],
                title='检查配置',
                bordered=True,
                size='small'
            ),
            fac.AntdResult(
                status='success',
                title='检查完成',
                subTitle='数据质量检查已成功执行（示例）',
                extra=[
                    fac.AntdStatistic(title='通过率', value='98.5%'),
                    fac.AntdStatistic(title='问题数', value='3')
                ]
            )
        ], direction='vertical', size='middle')

        # 构建日志展示
        log_content = fac.AntdSpace([
            fac.AntdTimeline(
                items=[
                    {'content': '开始执行数据质量检查', 'color': 'blue'},
                    {'content': f'连接到数据源: {datasource_name}', 'color': 'blue'},
                    {'content': f'选择表: {table_name}', 'color': 'blue'},
                    {'content': f'应用规则模板: {rule_template}', 'color': 'blue'},
                    {'content': '执行SQL查询（示例）', 'color': 'blue'},
                    {'content': '分析结果数据（示例）', 'color': 'blue'},
                    {'content': '检查完成', 'color': 'green'}
                ]
            )
        ], direction='vertical')

        return result_content, log_content
    except Exception as e:
        error_display = fac.AntdAlert(
            message='执行失败',
            description=str(e),
            type='error',
            showIcon=True
        )
        return error_display, dash.no_update