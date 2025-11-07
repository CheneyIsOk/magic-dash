import dash
from dash import Input, Output, State, callback, html
from configs.database_config import DataSourceModel, source_db
import feffery_antd_components as fac
import pathlib
from utils.get_tables import get_tables, get_columns
from utils.execute_query import run_sql, run_dataframe
import re
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
    [
        Input('active-datasource', 'data'),
        Input('dq-datasource-select', 'value')
    ]
)
def load_table_options(active_datasource: str | None, page_selected_ds: str | None):
    """根据当前活跃数据源或页面选择加载表列表

    规则：优先使用页面选择值，其次使用全局 active-datasource；当为'all'或空时不返回表。
    """
    datasource_name = page_selected_ds or active_datasource
    if not datasource_name or datasource_name == 'all':
        return [], ''

    try:
        sample_tables = get_tables(DataSourceModel, datasource_name)
        options = [{'label': info['table'], 'value': info['table']} for info in sample_tables]
        return options, datasource_name
    except Exception as e:
        print(f"加载表列表失败: {e}")
        return [], datasource_name or ''

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
        State('active-datasource', 'data'),
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
    active_datasource: Optional[str],
    page_selected_ds: Optional[str],
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

    # 选择数据源：优先页面选择，其次全局；若为'all'则视为未选择
    datasource_name = page_selected_ds or active_datasource

    # 检查必要参数
    if not all([datasource_name, table_name, rule_template]) or datasource_name == 'all':
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

        # 示例：执行一个轻量 SQL 验证连接（跨数据库通用）
        try:
            _ping_res = run_sql(datasource_name, "SELECT 1")
        except Exception as _e:
            raise RuntimeError(f"连接或基本查询失败: {_e}")

        # 渲染并执行模板SQL（接入真实流程）
        try:
            parts = rule_template.split('/')
            if len(parts) != 2:
                raise ValueError('规则模板格式不正确，应为 <dimension>/<template>')
            dimension, template_name = parts
            sql_file_path = PROJECT_ROOT / "dq_checks" / "sql" / dimension / f"{template_name}.sql"
            if not sql_file_path.exists():
                raise FileNotFoundError(f"规则SQL文件不存在: {sql_file_path}")

            with open(sql_file_path, 'r', encoding='utf-8') as f:
                raw_sql = f.read()

            # 提取模板变量
            vars_in_template = re.findall(r'\{\{\s*(\w+)\s*\}\}', raw_sql)

            # 标识符类变量（不能用命名参数绑定）
            identifier_vars = {'table', 'column', 'columns'}
            # 值类变量（可以用命名参数）当前仅支持 threshold，KISS
            value_vars_supported = {'threshold'}

            # 构造标识符值
            identifier_values: dict = {'table': table_name}
            if column_names:
                identifier_values['column'] = column_names[0]
                identifier_values['columns'] = ','.join(column_names)

            # 构造命名参数
            params: dict = {}
            if 'threshold' in vars_in_template and (threshold is not None):
                params['threshold'] = threshold

            # 检查未知变量并给出友好报错
            unknown_vars = [v for v in set(vars_in_template) if v not in identifier_vars and v not in value_vars_supported]
            if unknown_vars:
                raise ValueError(f"模板包含当前未支持的参数: {', '.join(unknown_vars)}；请仅使用 {{table}}, {{column}}, {{columns}} 或 {{threshold}}（现阶段UI支持）")

            # 渲染SQL：标识符直接替换，值变量替换为命名参数
            rendered_sql = raw_sql
            for var in set(vars_in_template):
                if var in identifier_vars:
                    # 直接替换为经过选项校验后的安全标识符
                    safe_value = identifier_values.get(var, '')
                    rendered_sql = re.sub(fr'\{{\{{\s*{var}\s*\}}\}}', safe_value, rendered_sql)
                else:
                    # 值变量改为命名参数 :var
                    rendered_sql = re.sub(fr'\{{\{{\s*{var}\s*\}}\}}', f':{var}', rendered_sql)

            # 执行SQL并获取DataFrame
            df = run_dataframe(datasource_name, rendered_sql, params=params)
            df_records = df.to_dict(orient='records')
            df_columns = [{'title': c, 'dataIndex': c} for c in df.columns]
        except Exception as _exec_e:
            # 若模板执行失败，则在结果区提示错误
            df_records = []
            df_columns = []

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
            fac.AntdCollapse(
                title='渲染SQL预览',
                children=html.Pre(
                    rendered_sql if 'rendered_sql' in locals() else 'SQL渲染失败',
                    style={'whiteSpace': 'pre-wrap', 'fontFamily': 'monospace'}
                ),
                isOpen=False,
                ghost=True,
                bordered=True,
                showArrow=True,
                size='small'
            ),
            fac.AntdTable(
                columns=df_columns,
                data=df_records,
                bordered=True,
                pagination={'pageSize': 10},
                size='small'
            ),
        ], direction='vertical', size='middle')

        # 构建日志展示
        log_content = fac.AntdSpace([
            fac.AntdTimeline(
                items=[
                    {'content': '开始执行数据质量检查', 'color': 'blue'},
                    {'content': f'连接到数据源: {datasource_name}', 'color': 'blue'},
                    {'content': f'选择表: {table_name}', 'color': 'blue'},
                    {'content': f'应用规则模板: {rule_template}', 'color': 'blue'},
                    {'content': '执行基本SQL: SELECT 1（用于连接与权限快速验证）', 'color': 'blue'},
                    {'content': f'渲染并执行模板SQL: {rule_template}', 'color': 'blue'},
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