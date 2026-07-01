# 🏫 智慧校园失物招领与物品交换平台

一个功能完整、界面现代的校园失物招领与物品交换Web应用。

## ✨ 功能特性

### 基础功能
- 👤 **用户注册与登录** — 校园用户注册、登录、个人信息管理
- 📦 **发布拾物信息** — 物品名称、拾取地点、时间、图片上传
- 🔍 **发布寻物信息** — 丢失物品描述、丢失地点、联系方式
- 🔄 **闲置物品交换** — 物品图片、新旧程度、期望交换物品
- 📂 **分类浏览与搜索** — 按6大分类（电子/书籍/证件/生活/服饰/其他）筛选
- 💬 **留言互动** — 失主与拾取者在线沟通

### 高阶亮点
- 🧠 **智能匹配引擎** — jieba分词 + TF-IDF余弦相似度，自动匹配失物与寻物
- 📊 **后台可视化看板** — ECharts图表：失物高发区域分布、时段统计、分类分布
- 🔔 **通知推送** — 匹配成功自动推送通知给双方用户
- 📱 **响应式设计** — 手机/平板/桌面全适配

## 🚀 快速启动

### 环境要求
- Python 3.8+
- pip

### 安装与启动

```bash
# 1. 进入项目目录
cd smart-campus-lostfound

# 2. 安装依赖
pip install -r requirements.txt

# 3. 一键启动（自动建表 + 导入演示数据）
python run.py
```

浏览器访问 **http://127.0.0.1:5000**

### 演示账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| `admin` | `admin123` | 管理员 |
| `zhangsan` | `123456` | 学生 |
| `lisi` | `123456` | 学生 |
| `wangwu` | `123456` | 学生 |

## 📂 项目结构

```
smart-campus-lostfound/
├── app.py                  # Flask应用工厂
├── config.py               # 配置类
├── run.py                  # 一键启动入口
├── seed_data.py            # 演示数据
├── requirements.txt        # Python依赖
├── models/
│   └── database.py         # 数据库DDL与初始化
├── routes/
│   ├── auth.py             # 认证API
│   ├── items.py            # 物品CRUD API
│   ├── search.py           # 搜索API
│   ├── messages.py         # 留言API
│   ├── notifications.py    # 通知API
│   └── admin.py            # 管理后台API
├── services/
│   ├── auth_service.py     # 认证业务逻辑
│   ├── item_service.py     # 物品CRUD逻辑
│   ├── match_service.py    # 智能匹配引擎
│   └── notification_service.py
├── utils/
│   ├── decorators.py       # 权限装饰器
│   ├── validators.py       # 输入校验
│   └── upload.py           # 图片上传处理
├── templates/
│   └── index.html          # SPA外壳
├── static/
│   ├── css/                # 样式文件
│   └── js/
│       ├── app.js          # SPA路由入口
│       ├── api.js          # API请求封装
│       ├── utils.js        # 工具函数
│       ├── components/     # 可复用组件
│       └── pages/          # 页面模块
└── .gitignore
```

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Flask 3.x |
| 数据库 | SQLite |
| 中文分词 | jieba |
| 文本匹配 | scikit-learn TF-IDF + 余弦相似度 |
| 前端架构 | Vanilla JS ES Modules SPA |
| 图表 | ECharts 5.x |
| CSS | 原生 CSS Grid/Flexbox |
| 图片处理 | Pillow |
| 认证 | Flask Session + werkzeug |

## 📡 API 概览

- `POST /api/auth/register` — 注册
- `POST /api/auth/login` — 登录
- `GET/POST /api/items/found` — 拾物 CRUD
- `GET/POST /api/items/lost` — 寻物 CRUD
- `GET/POST /api/items/exchange` — 交换 CRUD
- `GET /api/search` — 统一搜索
- `GET/POST /api/messages` — 留言互动
- `GET /api/notifications` — 通知中心
- `GET /api/admin/stats/*` — 管理后台统计

## 🧠 智能匹配算法

综合4个维度计算匹配分数：

| 维度 | 权重 | 算法 |
|------|------|------|
| 分类匹配 | 30% | 同分类=1.0 |
| 地点相似度 | 25% | jieba分词 + Jaccard |
| 时间接近度 | 15% | 时间差梯度评分 |
| TF-IDF余弦 | 30% | 文本向量相似度 |

- ≥55% → 推送通知给双方
- ≥40% → 记录匹配日志
- <40% → 过滤

## 📝 License

MIT
