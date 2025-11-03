# Magic Dash

数据质量监控项目，用于数据库质量情况监控、分析。


## 项目结构
```text
magic-dash/
├── assets/             # 静态资源文件（CSS样式、图片、JS脚本等）
│   ├── css/           # CSS样式文件
│   ├── imgs/          # 图片资源
│   ├── js/            # JavaScript脚本文件
│   └── videos/        # 视频资源
├── callbacks/          # 回调逻辑层（处理前端交互逻辑）
│   └── core_pages_c/  # 核心页面回调逻辑
├── components/         # 可复用UI组件封装
├── configs/            # 配置中心（认证、数据库、路由、布局等系统配置）
├── database/           # 数据库文件目录
├── models/             # 数据模型层（使用peewee定义用户、日志等实体）
├── utils/              # 工具脚本（如清理缓存文件）
├── views/              # 视图层（页面布局模块）
│   ├── core_pages/    # 核心页面视图
│   └── status_pages/  # 状态页面视图（403、404、500等）
├── app.py             # 应用入口文件
├── server.py          # 服务配置文件
├── requirements.txt   # 项目依赖文件
├── README.md          # 项目说明文件
├── .env.template      # 环境变量模板文件
└── .gitignore         # Git忽略文件配置
```

## 项目启动方式

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
- 复制 `.env.template` 文件为 `.env`
- 根据实际环境修改 `.env` 文件中的配置
- 初始化登录用户: `python -m models.init_db` (仅需执行一次)

3. 启动应用：
```bash
# 个人本地环境 
conda activate web-dev

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
   - 支持全屏水印功能
