# Magic Dash
【当前定位】全域数据资产与数据治理。
~~【定位 V0】数据质量监控项目，用于数据库质量情况监控、分析。~~


## 项目结构
```text
magic-dash/
├── assets/                 # 静态资源文件（CSS样式、图片、JS脚本等）
│   ├── css/                # CSS样式文件
│   ├── imgs/               # 图片资源
│   ├── js/                 # JavaScript脚本文件
│   └── videos/             # 视频资源
├── callbacks/              # 回调逻辑层（处理前端交互逻辑）
│   └── core_pages_c/       # 核心页面回调逻辑
├── core/                   # 数据资产核心配置
│   ├── sql/                # 存放SQL文件（纯SQL语句，便于复用）
│   │   ├── freshness/      # 数据新鲜度监控SQL
│   │   ├── completeness/   # 数据完整性监控SQL
│   │   ├── accuracy/       # 数据准确性监控SQL
│   │   ├── consistency/    # 数据一致性监控SQL
│   └── └── metadata/       # 数据元数据监控SQL
├── components/             # 可复用UI组件封装
├── configs/                # 配置中心（认证、数据库、路由、布局等系统配置）
├── database/               # 数据库文件目录
├── models/                 # 数据模型层
├── utils/                  # 工具脚本（如清理缓存文件）
├── views/                  # 视图层（页面布局模块）
│   ├── core_pages/        # 核心页面视图（如数据质量监控、用户管理等）
│   └── status_pages/      # 状态页面视图（403、404、500等）
├── app.py                 # 应用入口文件
├── server.py              # 服务配置文件
├── requirements.txt       # 项目依赖文件
├── README.md              # 项目说明文件
├── .env.template          # 环境变量模板文件
└── .gitignore             # Git忽略文件配置
```

## 项目启动方式

1. 安装依赖：
```bash
# 个人本地环境 
conda activate web-dev

pip install -r requirements.txt
```

2. 配置环境变量：
- 复制 `.env.template` 文件为 `.env`
- 根据实际环境修改 `.env` 文件中的配置
- 初始化登录用户: `python -m models.init_db` (仅需执行一次)

3. 启动应用：
```bash
# 启动应用
python app.py
```

4. 访问地址：
- 本地访问: http://localhost:8050
- 开发环境: http://127.0.0.1:8050


## 技术栈

- **Web框架**: Dash（>=3.1.1,<4.0.0）结合 Flask 构建应用
- **UI组件库**: feffery_antd_components（Ant Design 风格组件）
- **数据库ORM**: peewee（==3.18.2）
- **用户认证**: Flask_Login（==0.6.3）
- **工具库**: feffery_dash_utils, feffery_utils_components, user_agents, flask-compress, flask-principal
- **数据处理**: pandas（==2.3.3）, duckdb（==1.4.1）
- **数据库驱动**: psycopg2-binary（PostgreSQL支持）
 - **ORM/连接池**: SQLAlchemy（==2.0.44）用于统一连接与反射
 - **缓存**: Flask-Caching（==2.3.0）用于元数据查询缓存


## 核心功能模块

1. **用户认证与权限管理**
   - 基于Flask-Login的用户登录/登出功能
   - 基于Flask-Principal的角色权限控制
   - 支持管理员和普通用户两种角色

2. **页面路由系统**
   - 支持静态路由和动态路由
   - 权限控制的页面访问机制
   - 自定义403、404、500状态页面

3. **UI组件系统**
   - 可复用的侧边菜单组件
   - 用户个人信息管理面板
   - 用户管理界面

4. **数据源管理**
   - 支持多种数据库类型（SQLite、PostgreSQL、MySQL）
   - 数据源配置页面

5. **系统日志**
   - 用户登录日志记录与展示

6. **响应式布局**
   - 基于Ant Design的响应式页面布局


## TODO
- 【数据库管理】缓存数据库连接，所有页面复用一个连接池，避免重复连接（已完成MVP）
   * 通过 @lru_cache + SQLAlchemy连接池 + Flask-Caching（已集成）
   * 新增 utils/db_pool.py：统一构建 Engine、提供 get_connection 上下文、invalidate_engine 失效机制
   * 迁移 utils/get_tables.py：使用 SQLAlchemy inspector 获取表/列，并添加缓存 @cache.memoize
   * 在 callbacks/core_pages_c/data_source_c.py 的新增/编辑/删除后，清理连接池缓存与应用缓存
   * 全局注入 dcc.Store(id='active-datasource')，首页筛选器维护该值，用于跨页共享当前活跃数据源
   * 后续计划：其他页面统一读取 active-datasource，完善上下文管理与并发测试
```
一、数据库连接池与缓存策略

为避免跨页面频繁建立数据库连接、提升性能与稳定性，项目实现了统一的连接管理与缓存方案：
- 连接管理
  * 工具模块：utils/db_pool.py
  * 基于 SQLAlchemy Engine + @lru_cache 实现按数据源名称复用连接
  * 提供 get_connection(name) 上下文管理，确保连接安全归还
  * invalidate_engine(name) 失效接口，在数据源配置变更/删除后清理缓存，避免旧连接

- 元数据缓存
  * 应用级缓存：Flask-Caching SimpleCache
  * get_tables/get_columns 使用 @cache.memoize 缓存结果
  * 在数据源新增/编辑/删除后，统一 cache.clear() 失效缓存，确保反射元数据最新

- 全局活跃数据源状态
  * app.py 中注入 dcc.Store(id='active-datasource', data='all')
  * 首页数据源筛选器变化时同步更新该 Store（callbacks/core_pages_c/index_c.py）
  * 其他页面可读取该 Store，避免重复建立连接与参数传递

二、使用建议
- 执行数据库查询时优先通过 utils/db_pool.get_engine_by_name 或 get_connection(name) 获取连接
- 若编写新的元数据读取函数，考虑添加 @cache.memoize 并在数据源变更场景清理缓存
- 若数据源配置发生变化（名称、主机、库名等），确保调用 invalidate_engine 并清理缓存
- 避免在页面回调中频繁创建新 Engine 或直接使用底层驱动连接，统一走连接池
```

- 【后台定时任务】数据质量检查实现定时自动触发检查
   * 前台手动触发-后台定时任务，结果入库，独立页面显示数据趋势和问题明细。
   * 通过定时调度框架（如 APScheduler/Dagster/Perfect/Airflow），实现每日自动运行。
   * 配置文件中指定检查规则、目标数据库、目标表、通知方式（邮箱/短信/微信等）。
   * 执行控制： 手动触发、自动触发、暂停/恢复（可选）、取消任务。