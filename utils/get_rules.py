def get_dq_rules(proj_dir):
    """获取数据质量检查规则"""
    rules = []
    
    # 规则目录路径
    dq_checks_path = proj_dir / "dq_checks" / "sql"
    # 遍历所有质量维度目录
    if dq_checks_path.exists():
        for dimension_dir in dq_checks_path.iterdir():
            if dimension_dir.is_dir():
                # 遍历目录中的所有SQL文件
                for sql_file in dimension_dir.iterdir():
                    if sql_file.suffix == '.sql':
                        rules.append({
                            'label': sql_file.stem,
                            'value': f"{dimension_dir.name}/{sql_file.stem}",
                            'dimension': dimension_dir.name
                        })
    
    return rules