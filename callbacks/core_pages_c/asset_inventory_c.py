from __future__ import annotations

import re
import pathlib
from datetime import date, timedelta
from typing import List, Dict, Any, Optional, Tuple

import dash
from dash import Input, Output, State, callback, html
import feffery_antd_components as fac

from configs.database_config import DataSourceModel
from utils.execute_query import run_dataframe

# 快照持久化（本地SQLite）
try:
    from models.data_assets import AssetDB, CheckTableSize
    _snapshot_available = True
except Exception:
    # 若模型未就绪，则跳过持久化
    _snapshot_available = False

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent


@callback(
    Output("ai-datasource-select", "options"),
    Input("ai-datasource-select", "id"),
)
def load_ai_datasource_options(_trigger: str) -> List[Dict[str, str]]:
    """加载数据源选项（仅展示PostgreSQL类型，因SQL依赖pg_*函数）"""
    options: List[Dict[str, str]] = []
    try:
        query = DataSourceModel.select()
        for ds in query:
            if ds.type == "postgresql":
                options.append({"label": ds.name, "value": ds.name})
    except Exception as e:
        print(f"加载数据源列表失败: {e}")
    return options


@callback(
    Output("ai-snapshot-ds-select", "options"),
    Input("ai-snapshot-ds-select", "id"),
)
def load_snapshot_ds_options(_trigger: str) -> List[Dict[str, str]]:
    """加载快照数据源筛选选项（包含“全部”）"""
    options: List[Dict[str, str]] = [{"label": "全部", "value": "all"}]
    try:
        query = DataSourceModel.select()
        for ds in query:
            options.append({"label": ds.name, "value": ds.name})
    except Exception as e:
        print(f"加载快照数据源列表失败: {e}")
    return options


def _parse_pretty_size_to_bytes(text: str) -> float:
    """将pg_size_pretty的字符串解析为字节数用于排序，例如 '123 MB', '9 kB', '42 bytes'"""
    if not text:
        return 0.0
    try:
        m = re.match(r"^(\d+(?:\.\d+)?)\s*([A-Za-z]+)\s*$", text)
        if not m:
            # 可能是纯数字（字节）
            return float(text)
        value = float(m.group(1))
        unit = m.group(2).lower()
        unit_map = {
            "b": 1,
            "byte": 1,
            "bytes": 1,
            "kb": 1024,
            "mb": 1024 ** 2,
            "gb": 1024 ** 3,
            "tb": 1024 ** 4,
            "pb": 1024 ** 5,
            "eb": 1024 ** 6,
        }
        # pg_size_pretty 使用 "kB"（小写k），但我们统一lower处理
        return value * unit_map.get(unit, 1)
    except Exception:
        return 0.0


# 将资产盘点页的“快照数据源筛选”作为全局活跃数据源的驱动
@callback(
    Output("active-datasource", "data"),
    Input("ai-snapshot-ds-select", "value"),
    prevent_initial_call=True,
)
def sync_active_datasource_from_asset_inventory(ds_value: Optional[str]) -> str:
    """同步全局当前活跃数据源Store：优先使用资产盘点页顶部的快照数据源筛选"""
    return ds_value or "all"


@callback(
    [
        Output("ai-snapshot-top10-table", "columns"),
        Output("ai-snapshot-top10-table", "data"),
        Output("ai-snapshot-dt-text", "children"),
        Output("ai-snapshot-run-status", "children"),
    ],
    Input("ai-snapshot-refresh", "nClicks"),
    State("ai-snapshot-ds-select", "value"),
    prevent_initial_call=True,
)
def load_today_top10(nClicks: int, ds_filter: Optional[str]):
    """从快照库读取当天数据，按 total_size 排序返回 Top10"""
    dt_str = date.today().isoformat()

    if not _snapshot_available:
        return [], [], f"今日: {dt_str}", fac.AntdText("本地快照库不可用", type="danger")

    try:
        AssetDB.connect(reuse_if_open=True)
        query = CheckTableSize.select().where(CheckTableSize.dt == dt_str)
        if ds_filter and ds_filter != "all":
            query = query.where(CheckTableSize.data_source == ds_filter)

        records = [
            {
                "table_schema": r.table_schema,
                "table_name": r.table_name,
                "table_size": r.table_size,
                "indexes_size": r.indexes_size,
                "total_size": r.total_size,
                "data_source": r.data_source,
            }
            for r in query
        ]
    except Exception as e:
        try:
            AssetDB.close()
        except Exception:
            pass
        return [], [], f"今日: {dt_str}", fac.AntdText(f"读取快照失败: {e}", type="danger")

    # 排序并取前10
    records_sorted = sorted(
        records,
        key=lambda x: _parse_pretty_size_to_bytes(x.get("total_size", "0")),
        reverse=True,
    )[:10]

    columns = [
        {"title": "schema", "dataIndex": "table_schema"},
        {"title": "表名", "dataIndex": "table_name"},
        {"title": "表数据大小", "dataIndex": "table_size"},
        {"title": "索引大小", "dataIndex": "indexes_size"},
        {"title": "合计大小", "dataIndex": "total_size"},
        {"title": "数据源", "dataIndex": "data_source"},
    ]

    status_msg = (
        fac.AntdText(f"已加载今日Top10（{dt_str}），共 {len(records_sorted)} 条", type="success")
        if records_sorted
        else fac.AntdText(f"今日（{dt_str}）暂无匹配快照记录", type="warning")
    )

    try:
        AssetDB.close()
    except Exception:
        pass

    return columns, records_sorted, f"今日: {dt_str}", status_msg


def _resolve_time_range_days(range_label: Optional[str]) -> int:
    """将时间范围标签解析为天数"""
    mapping = {
        "近一周": 7,
        "近一月": 30,
        "近三月": 90,
        "近半年": 180,
    }
    return mapping.get(range_label or "近一周", 7)


@callback(
    [
        Output("ai-prefix-pie", "data"),
        Output("ai-volume-dual", "data"),
        Output("ai-volume-unit-text", "children"),
    ],
    [
        Input("ai-snapshot-ds-select", "value"),
        Input("ai-time-range", "value"),
    ],
)
def update_prefix_pie_and_volume_dual(ds_filter: Optional[str], time_range: Optional[str]):
    """
    更新：
    - 表命名前缀分布（饼图）：按 total_size 累加，分类为 ods/dim/dwd/dws/ads/other
    - 每日总量（柱状图）：按日期汇总 total_size
    以上均受数据源筛选与时间范围筛选影响。
    """
    if not _snapshot_available:
        return [], [], ""

    days = _resolve_time_range_days(time_range)
    end_dt = date.today()
    start_dt = end_dt - timedelta(days=days - 1)
    start_str, end_str = start_dt.isoformat(), end_dt.isoformat()

    # 初始化聚合结构
    # 饼图：统计表数量（唯一表），而非 total_size
    prefix_unique: Dict[str, set] = {k: set() for k in ["ods", "dim", "dwd", "dws", "ads", "other"]}
    # 折线：每日总量（字节）与每日表数量
    daily_sum: Dict[str, float] = {}
    daily_count: Dict[str, int] = {}

    try:
        AssetDB.connect(reuse_if_open=True)
        query = CheckTableSize.select().where(
            (CheckTableSize.dt >= start_str) & (CheckTableSize.dt <= end_str)
        )
        if ds_filter and ds_filter != "all":
            query = query.where(CheckTableSize.data_source == ds_filter)

        for r in query:
            # 解析总大小
            total_bytes = _parse_pretty_size_to_bytes(r.total_size or "0")
            # 前缀分类（唯一表）
            name = (r.table_name or "").lower()
            prefix = name.split("_")[0] if "_" in name else name
            if prefix not in prefix_unique:
                prefix = "other"
            unique_key = f"{r.table_schema}|{r.table_name}"
            prefix_unique[prefix].add(unique_key)

            # 日期汇总
            dt_key = r.dt
            daily_sum[dt_key] = daily_sum.get(dt_key, 0.0) + total_bytes
            daily_count[dt_key] = daily_count.get(dt_key, 0) + 1

    except Exception as e:
        print(f"更新前缀分布与每日总量失败: {e}")
    finally:
        try:
            AssetDB.close()
        except Exception:
            pass

    pie_data = [
        {"type": k, "value": len(v)}
        for k, v in prefix_unique.items()
        if len(v) > 0
    ]

    # 日期排序后输出柱状图数据
    # 左轴单位自动转换：优先GB，否则MB
    max_total = max(daily_sum.values()) if daily_sum else 0.0
    gb = 1024 ** 3
    mb = 1024 ** 2
    scale = gb if max_total >= gb else mb
    unit_label = "GB" if scale == gb else "MB"

    # 按时间范围生成完整日期序列，填充缺失日期为0，避免仅单点显示不直观
    date_list = [
        (start_dt + timedelta(days=i)).isoformat()
        for i in range((end_dt - start_dt).days + 1)
    ]
    left_line = [
        {"date": d, "y1": round((daily_sum.get(d, 0.0)) / scale, 3)}
        for d in date_list
    ]
    right_line = [
        {"date": d, "y2": daily_count.get(d, 0)}
        for d in date_list
    ]

    unit_text = f"左轴单位：{unit_label}；右轴：表数量"
    return pie_data, [left_line, right_line], unit_text
