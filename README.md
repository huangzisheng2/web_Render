# 天赋性格测评系统

基于中国传统八字命理学的天赋与性格分析系统，结合 AI 技术生成个性化报告。

**技术架构**：Vue3 + Vite（前端）+ FastAPI + Python（后端）+ Render（后端托管）+ GitHub Pages（前端托管）

**在线访问**：
- 用户版：https://huangzisheng2.github.io/web_Render/
- 调试版：https://huangzisheng2.github.io/web_Render/debug.html

---

## 系统概述

### 双版本架构

本系统采用**双版本架构设计**，分别面向普通用户和开发者：

| 版本 | 访问地址 | 功能特点 | 目标用户 |
|------|----------|----------|----------|
| **用户版** | `/index.html` | 简洁界面，仅展示AI报告，隐藏命理数据 | 普通用户 |
| **调试版** | `/debug.html` | 完整数据展示，支持Debug模式查看原始数据 | 开发者、测试人员 |

### 核心功能

1. **趣味答题**：6道性格测试题，无标准答案，增强互动体验
2. **信息收集**：姓名、出生日期时间（支持真太阳时）、性别、出生地
3. **八字计算**：后台自动排盘、计算五行、十神能量
4. **AI分析**：调用DeepSeek API生成个性化天赋报告
5. **报告下载**：支持PDF导出
6. **用户反馈**：1-5星评分+文字反馈，存储到PostgreSQL数据库

---

## 功能架构

### 前端功能模块

```
┌─────────────────────────────────────────────────────────┐
│                     前端应用层                           │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ 引导页   │→│ 答题页   │→│ 表单页   │→│ 结果页  │ │
│  │ Landing  │  │  Quiz    │  │  Form    │  │ Result  │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
│       ↑                                    ↓            │
│       └──────────── 重新分析 ←─────────────┘            │
├─────────────────────────────────────────────────────────┤
│  核心组件：                                             │
│  • 姓名/性别输入                                        │
│  • 日期时间选择器（滚轮+快速输入8/10/12位数字）        │
│  • 省市级联选择器（支持真太阳时计算）                  │
│  • AI报告渲染（Markdown格式）                          │
│  • PDF生成（html2canvas + jsPDF）                      │
│  • 用户反馈模块（星级评分+文字）                       │
└─────────────────────────────────────────────────────────┘
```

### 后端功能模块

```
┌─────────────────────────────────────────────────────────┐
│                     后端服务层                           │
├─────────────────────────────────────────────────────────┤
│  FastAPI 应用                                          │
│  ├─ /api/analyze          # 八字分析主接口             │
│  ├─ /api/analyze-ai       # AI报告生成接口             │
│  ├─ /api/feedback         # 用户反馈接口               │
│  ├─ /api/cities           # 城市列表接口               │
│  └─ /api/download/{id}    # PDF下载接口                │
├─────────────────────────────────────────────────────────┤
│  业务服务层：                                           │
│  • BaziAnalysisServiceWeb   # 八字分析服务             │
│  │   ├─ get_location()      # 获取城市经纬度           │
│  │   ├─ apply_true_solar_time()  # 真太阳时计算        │
│  │   ├─ convert_to_bazi()   # 转换为八字               │
│  │   ├─ analyze_basic()     # 基础分析（六级论级）     │
│  │   └─ analyze_ai()        # AI分析报告生成           │
│  │                                                      │
│  • PDFService               # PDF生成服务              │
│      ├─ generate_pdf_report()  # ReportLab生成PDF      │
│      └─ get_download_url()     # 获取下载链接          │
├─────────────────────────────────────────────────────────┤
│  命理模块层（bazi_modules）：                           │
│  • lunar_python          # 农历阳历转换                │
│  • bazi_bridge           # 八字计算核心                │
│  • true_solar_time       # 真太阳时计算                │
│  • city_database         # 城市经纬度数据库            │
│  • bazi_geju_refactored_v5  # 格局分析                 │
├─────────────────────────────────────────────────────────┤
│  数据存储层：                                           │
│  • PostgreSQL (Render)   # 用户反馈数据                │
│  • DeepSeek API          # AI分析报告生成              │
└─────────────────────────────────────────────────────────┘
```

---

## 数据处理流程

### 1. 用户输入流程

```
用户访问页面
    ↓
引导页（Landing）→ 点击"开始探索"
    ↓
答题页（Quiz）→ 6道选择题，自动跳转
    ↓
表单页（Form）→ 填写：
    • 姓名
    • 出生日期时间（支持快速输入：YYYYMMDD/HH/mm）
    • 性别
    • 出生地（省/市，可选，用于真太阳时）
    ↓
点击"开始分析"
```

### 2. 后端数据处理流程

```
接收前端请求 POST /api/analyze
    ↓
【Step 1: 参数解析】
    • 解析姓名、性别、出生年月日时分
    • 解析出生地（省/市）
    • 检查 X-Debug-Mode 请求头
    ↓
【Step 2: 真太阳时计算】（如果提供了出生地）
    • 根据省市查询 city_database 获取经纬度
    • calculate_longitude_diff(): 计算经度时差 (经度-120°)×4分钟
    • get_equation_of_time(): 获取均时差（地球轨道修正）
    • calculate_true_solar_time(): 计算真太阳时
    • 输出：调整后的年月日时分
    ↓
【Step 3: 八字排盘】
    • Solar.to_lunar(): 公历转农历
    • 计算四柱（年柱、月柱、日柱、时柱）
    • 每柱包含：天干 + 地支
    ↓
【Step 4: 命理分析】
    • 分析日主（日柱天干）
    • 计算十神（比肩、劫财、食神、伤官、正财、偏财、正官、七杀、正印、偏印）
    • 判断身强身弱
    • 判定格局（食神格、伤官格、财格等）
    • 分析五行能量（金木水火土）
    • 六级论级分析（月令→地支→天干→干支关系→定喜忌→大运流年）
    ↓
【Step 5: AI报告生成】（异步）
    • 构建 AI Prompt（包含八字数据、格局分析）
    • 调用 DeepSeek API (deepseek-chat 模型)
    • 生成个性化天赋分析报告（Markdown格式）
    ↓
【Step 6: 响应组装】
    • 用户模式：返回 {report_id, user_info, ai_report}
    • 调试模式：额外返回 {_debug_full_data: 完整命理数据}
```

### 3. 真太阳时计算详解

```
输入：出生时间 + 出生地经纬度
    ↓
1. 经度时差计算
   公式：(经度 - 120°) × 4 分钟
   示例：乌鲁木齐（经度87.6°）
   (87.6 - 120) × 4 = -129.6 分钟（约-2小时10分）

2. 均时差计算
   根据日期查询均时差表（地球公转轨道椭圆修正）
   示例：1月1日约 -3分钟

3. 总时差
   总时差 = 经度时差 + 均时差
   示例：-129.6 + (-3) = -132.6 分钟

4. 真太阳时
   真太阳时 = 平太阳时 + 总时差
   示例：14:20（北京时间）→ 12:07（真太阳时）

输出：调整后的年月日时分
```

### 4. 数据流向图

```
┌─────────┐     ┌──────────────────────────────────────────┐
│  用户   │     │              前端应用                     │
└────┬────┘     │  ┌─────────┐  ┌─────────┐  ┌──────────┐  │
     │          │  │Landing  │  │  Quiz   │  │   Form   │  │
     │          │  └────┬────┘  └────┬────┘  └────┬─────┘  │
     │          │       └────────────┴────────────┘        │
     │          │                    │                      │
     │          │              ┌─────┴──────┐               │
     │          │              │   Result   │←──────────────┤
     │          │              │  (AI报告)  │               │
     │          └──────────────┴─────┬──────┘               │
     │                               │                      │
     │          ┌────────────────────┼────────────────────┐ │
     │          │     后端 API        │                    │ │
     │          │  ┌──────────────────┼──────────────┐    │ │
     │          │  │ /api/analyze     │              │    │ │
     │          │  │ /api/analyze-ai  │              │    │ │
     │          │  │ /api/feedback    │              │    │ │
     │          │  └──────────────────┼──────────────┘    │ │
     │          └─────────────────────┼───────────────────┘ │
     │                                │                     │
     │          ┌─────────────────────┼──────────────────┐  │
     │          │    业务服务层       │                  │  │
     │          │  ┌────────────────┐ │                  │  │
     │          │  │ 真太阳时计算   │ │                  │  │
     │          │  │ 八字排盘       │ │                  │  │
     │          │  │ 命理分析       │ │                  │  │
     │          │  │ AI报告生成     │ │                  │  │
     │          │  └────────────────┘ │                  │  │
     │          └─────────────────────┼──────────────────┘  │
     │                                │                      │
     │          ┌─────────────────────┼──────────────────┐  │
     │          │    外部服务         │                  │  │
     │          │  ┌────────────────┐ │                  │  │
     │          │  │ DeepSeek API   │←┘                  │  │
     │          │  │ PostgreSQL     │←── 用户反馈        │  │
     │          │  └────────────────┘                     │  │
     │          └─────────────────────────────────────────┘  │
     │                                                       │
┌────┴────┐                                                 │
│ AI报告  │←─────────────────────────────────────────────────┘
└─────────┘
```

### 5. 用户反馈数据流

```
用户在结果页提交反馈
    ↓
前端 POST /api/feedback
    {
        rating: 1-5,
        feedback_text: "...",
        experience_type: "overall|design|content|feature"
    }
    ↓
后端接收 → feedback.py submit_feedback()
    • 验证评分范围（1-5）
    • 获取 User-Agent 和 IP（防滥用）
    ↓
PostgreSQL 存储
    表：user_feedback
    字段：id, rating, feedback_text, experience_type, 
         created_at, user_agent, ip_address
    ↓
返回成功响应
```

---

## 📁 项目结构

---

## 📑 目录

- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [文件说明](#文件说明)
- [本地调试](#本地调试)
- [部署指南](#部署指南)
- [使用说明](#使用说明)
- [API 文档](#api-文档)
- [常见问题](#常见问题)
- [后续计划](#后续计划)

---

## 🚀 快速开始

### 一键启动（Windows）

```bash
# 1. 进入项目目录
cd "g:\07.Project\02.性格测试\03.bazi-talent-render"

# 2. 复制命理模块（首次运行）
copy_bazi_modules.bat

# 3. 启动后端
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# 4. 新终端 - 启动前端
cd frontend
npm install
npm run dev
```

**访问地址**：
- 前端：http://localhost:5173/web_Render/
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

---

## 📁 项目结构

```
web_Render/
├── 📂 backend/                      # FastAPI 后端
│   ├── 📄 main.py                  # 主入口，路由配置，含Debug模式判断
│   ├── 📄 feedback.py              # 用户反馈模块，PostgreSQL存储
│   ├── 📂 services/                # 业务服务层
│   │   ├── 📄 bazi_service_web.py  # 八字分析服务（真太阳时+AI）
│   │   └── 📄 pdf_service.py       # PDF生成服务
│   ├── 📂 bazi_modules/            # 命理模块（需从本地复制）
│   │   ├── 📄 bazi_bridge.py       # 八字计算核心桥接
│   │   ├── 📄 bazi_geju_refactored_v5.py  # 格局分析
│   │   ├── 📄 true_solar_time.py   # 真太阳时计算
│   │   ├── 📄 city_database.py     # 城市经纬度数据库
│   │   └── 📄 lunar_python/        # 农历阳历转换库
│   ├── 📄 requirements.txt         # Python依赖
│   ├── 📄 render.yaml              # Render部署配置
│   └── 📄 Dockerfile               # Docker配置
│
├── 📂 frontend/                     # 前端（双版本）
│   ├── 📄 index.html               # ⭐ 用户版入口（单文件HTML）
│   ├── 📄 debug.html               # ⭐ 调试版入口（单文件HTML）
│   │
│   ├── 📂 src/                     # Vue3源码（开发版）
│   │   ├── 📂 components/
│   │   │   ├── 📄 LandingPage.vue  # 引导页组件
│   │   │   ├── 📄 QuizPage.vue     # 答题页组件
│   │   │   ├── 📄 StepForm.vue     # 表单页组件
│   │   │   ├── 📄 ResultDisplay.vue # 结果展示组件
│   │   │   └── 📄 ...              # 其他组件
│   │   ├── 📂 api/
│   │   │   └── 📄 bazi.js          # API接口封装
│   │   ├── 📂 data/
│   │   │   └── 📄 cities.js        # 省市数据
│   │   └── 📄 App.vue              # Vue应用根组件
│   │
│   ├── 📄 package.json             # npm依赖
│   └── 📄 vite.config.js           # Vite配置
│
├── 📂 design-system/               # 设计系统文档
│   └── 📄 MASTER.md                # 设计规范
│
├── 📄 copy_bazi_modules.bat        # 一键复制命理模块脚本
├── 📄 README.md                    # 本文件
└── 📄 .gitignore                   # Git忽略配置
```

### 前端双版本说明

| 文件 | 类型 | 特点 | 用途 |
|------|------|------|------|
| `index.html` | 单文件HTML | 内嵌Vue3 CDN，独立部署 | 用户版，GitHub Pages部署 |
| `debug.html` | 单文件HTML | 内嵌Vue3 CDN，Debug模式 | 开发者调试用 |
| `src/` | Vue3源码 | 组件化开发，需构建 | 开发环境使用 |

---

## 📄 文件说明

### 后端文件

| 文件 | 说明 | 核心功能 |
|------|------|----------|
| `main.py` | FastAPI 主入口 | 定义路由、CORS配置、服务启动 |
| `services/bazi_service.py` | 八字分析服务 | 真太阳时计算、DeepSeek API调用、结果组装 |
| `services/pdf_service.py` | PDF生成服务 | reportlab生成PDF、html2pdf备用方案 |
| `requirements.txt` | Python依赖 | fastapi, uvicorn, reportlab等 |
| `render.yaml` | Render部署配置 | 免费版Web服务配置 |
| `bazi_modules/` | 命理模块目录 | 存放从本地复制的命理Python文件 |

### 前端文件

| 文件 | 说明 | 核心功能 |
|------|------|----------|
| `components/BaziForm.vue` | 表单组件 | 姓名输入、日期选择、时间选择、省市联动 |
| `components/ResultDisplay.vue` | 结果展示 | 四柱排盘、五行能量条、AI报告渲染 |
| `api/bazi.js` | API封装 | axios配置、接口调用、错误处理 |
| `data/cities.js` | 城市数据 | 全国省市数据，用于出生地选择 |
| `vite.config.js` | Vite配置 | 开发代理、生产路径、构建设置 |

---

## 🔧 本地调试

### 环境要求

- **Node.js**: >= 16.x
- **Python**: >= 3.10
- **Git**: 任意版本

### 步骤1：复制命理模块

**方式A：双击脚本（推荐）**
```
copy_bazi_modules.bat
```

**方式B：手动复制**
```bash
xcopy /Y /E "G:\07.Project\02.性格测试\01.八字排盘与计算\bazi-master_new\bazi-master\*.py" "backend\bazi_modules\"
xcopy /Y /E "G:\07.Project\02.八字排盘与计算\bazi-master_new\bazi-master\lunar_python" "backend\bazi_modules\lunar_python\"
xcopy /Y /E "G:\07.Project\02.性格测试\01.八字排盘与计算\bazi-master_new\bazi-master\bidict" "backend\bazi_modules\bidict\"
```

### 步骤2：启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活（Windows PowerShell）
venv\Scripts\Activate.ps1

# 激活（Windows CMD）
venv\Scripts\activate.bat

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**验证后端**：
- 浏览器访问 http://localhost:8000 应返回 `{"status": "ok"}`
- 访问 http://localhost:8000/docs 查看 API 文档

### 步骤3：启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

**访问前端**：http://localhost:5173/web_Render/

### 调试技巧

| 操作 | 命令/方法 |
|------|-----------|
| 只调试前端UI | 前端启动后，不需要后端也能看到界面 |
| 测试后端API | 使用 http://localhost:8000/docs 可视化测试 |
| 查看后端日志 | 后端终端会显示请求和错误信息 |
| 前端热更新 | 修改代码自动刷新，无需重启 |
| 后端热更新 | 使用 `--reload` 参数，代码修改自动重启 |

---

## 📤 部署指南

### 部署架构

```
┌─────────────────┐         ┌─────────────────┐
│   GitHub Pages  │ ◀────── │    Vue3 前端    │
│  (静态网站托管)  │         │  编译后的 dist  │
└─────────────────┘         └─────────────────┘
         │
         │ HTTPS
         ▼
┌─────────────────┐         ┌─────────────────┐
│     Render      │ ◀────── │  FastAPI 后端   │
│  (Python服务托管)│         │   bazi_modules  │
└─────────────────┘         └─────────────────┘
         │
         │ API Key
         ▼
┌─────────────────┐
│   DeepSeek API  │
│  (AI分析报告生成)│
└─────────────────┘
```

### 第一步：上传代码到 GitHub

#### 首次上传（初始化）

```bash
# 进入项目目录
cd "g:\07.Project\02.性格测试\03.bazi-talent-render"

# 确保命理模块已复制
xcopy /Y /E "G:\07.Project\02.性格测试\01.八字排盘与计算\bazi-master_new\bazi-master\*.py" "backend\bazi_modules\"
xcopy /Y /E "G:\07.Project\02.性格测试\01.八字排盘与计算\bazi-master_new\bazi-master\lunar_python" "backend\bazi_modules\lunar_python\"
xcopy /Y /E "G:\07.Project\02.性格测试\01.八字排盘与计算\bazi-master_new\bazi-master\bidict" "backend\bazi_modules\bidict\"

# 初始化 Git（如果未初始化）
git init

# 配置用户信息（首次需要）
git config user.email "your-email@example.com"
git config user.name "Your Name"

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: 天赋性格测评系统 v1.0"

# 添加远程仓库
git remote add origin https://github.com/huangzisheng2/web_Render.git

# 推送到 GitHub（如有网络问题，见下方网络配置）
git branch -M main
git push -u origin main
```

#### 🔧 网络问题解决方案

如果推送失败（`Failed to connect to github.com`），使用代理：

```bash
# 设置代理（根据你的代理软件修改端口，如 7890、1080 等）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 推送
git push -u origin main

# 成功后取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

如果提示 `rejected`，强制推送：
```bash
git push -f origin main
```

---

### 📦 日常更新代码流程

每次修改代码后，按以下步骤更新到 GitHub：

```bash
# 1. 进入项目目录
cd "g:\07.Project\02.性格测试\03.bazi-talent-render"

# 2. 查看修改状态
git status

# 3. 添加修改的文件（可以单独添加，也可以用 . 添加所有）
git add .

# 4. 提交修改（写有意义的提交信息）
git commit -m "描述你的修改，如：修复八字计算bug"

# 5. 推送到 GitHub（如有网络问题，先设置代理）
git push origin main
```

#### 完整示例

```bash
# 示例：修改了后端代码
cd "g:\07.Project\02.性格测试\03.bazi-talent-render"

# 修改文件后...

# 检查哪些文件被修改了
git status

# 添加修改
git add backend/services/bazi_service.py
git add backend/main.py

# 提交
git commit -m "优化八字分析算法，提升计算速度"

# 推送（如有网络问题，设置代理）
git config --global http.proxy http://127.0.0.1:7890
git push origin main
git config --global --unset http.proxy
```

#### 常用 Git 命令速查

| 命令 | 作用 |
|------|------|
| `git status` | 查看当前修改状态 |
| `git add 文件名` | 添加指定文件到暂存区 |
| `git add .` | 添加所有修改的文件 |
| `git commit -m "说明"` | 提交修改 |
| `git push origin main` | 推送到 GitHub |
| `git pull origin main` | 拉取远程更新 |
| `git log --oneline` | 查看提交历史 |
| `git diff` | 查看具体修改内容 |

### 第二步：部署后端到 Render

1. **访问** https://dashboard.render.com/

2. **创建 Web Service**：
   - 点击 "New +" → "Web Service"
   - 选择你的 GitHub 仓库 `web_Render`
   - 配置如下：

   | 配置项 | 值 |
   |--------|-----|
   | **Name** | `bazi-talent-api` |
   | **Root Directory** | `backend` |
   | **Runtime** | Python 3 |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

3. **添加环境变量**：
   - `DEEPSEEK_API_KEY` = `sk-99f76dba24a242d9b6b358365b356d79`

4. **点击 "Create Web Service"**

5. **等待部署完成**，记下 Render 提供的 URL（如 `https://bazi-talent-api.onrender.com`）

### 第三步：更新前端 API 地址

编辑 `frontend/src/api/bazi.js`：

```javascript
const BASE_URL = import.meta.env.PROD 
  ? 'https://bazi-talent-api.onrender.com'  // ← 修改为你的 Render 地址
  : ''
```

提交修改：
```bash
git add .
git commit -m "更新 API 地址"
git push
```

### 第四步：部署前端到 GitHub Pages

1. **GitHub 仓库 → Settings → Pages**

2. **配置 Source**：
   - Source: "GitHub Actions"

3. **自动部署**：
   - 推送代码后会自动触发 `.github/workflows/deploy.yml`
   - 等待 Actions 运行完成

4. **访问地址**：
   - `https://huangzisheng2.github.io/web_Render/`

---

## 📖 使用说明

### 用户操作流程

1. **填写基本信息**
   - 姓名：输入您的姓名
   - 性别：选择男/女

2. **选择出生时间**
   - 出生日期：选择公历出生日期
   - 出生时间：
     - 知道具体时间：选择小时和分钟
     - 不知道时间：点击"未知"按钮（时柱将不计算）

3. **选择出生地**
   - 省份：先选择省份
   - 城市：再选择城市
   - 用于真太阳时计算

4. **提交分析**
   - 点击"开始分析"按钮
   - 等待 10-30 秒（AI 生成报告需要时间）

5. **查看结果**
   - 四柱排盘：显示年柱、月柱、日柱、时柱
   - 基本分析：身强身弱、主要格局
   - 五行能量：可视化能量分布
   - AI 报告：完整的天赋性格分析

6. **下载报告**
   - 点击"下载 PDF 报告"按钮
   - 保存到本地

### 分析结果说明

| 项目 | 说明 |
|------|------|
| **四柱** | 年柱、月柱、日柱、时柱，各由天干地支组成 |
| **日主** | 日柱的天干，代表命主本人 |
| **身强身弱** | 八字五行力量的平衡状态 |
| **格局** | 八字的组合类型，影响性格和命运 |
| **五行能量** | 金木水火土五行的相对强弱 |
| **十神能量** | 比肩、劫财、食神、伤官、正财、偏财、正官、七杀、正印、偏印的能量分布 |
| **用神/喜神/忌神** | 对命主有利和不利的五行 |

---

## 📚 API 文档

### 请求头说明

| 请求头 | 说明 |
|--------|------|
| `Content-Type: application/json` | 必须，所有POST请求 |
| `X-Debug-Mode: true` | 可选，调试模式返回完整命理数据 |

### 1. 健康检查

```http
GET /
```

**响应**：
```json
{
  "status": "ok",
  "service": "天赋性格测评系统 API"
}
```

### 2. 八字分析

```http
POST /api/analyze
Content-Type: application/json
X-Debug-Mode: true  # 可选，开启调试模式
```

**请求体**：
```json
{
  "name": "张三",
  "year": 1990,
  "month": 5,
  "day": 15,
  "hour": 14,
  "minute": 30,
  "gender": "male",
  "province": "北京市",
  "city": "北京市",
  "answers": [0, 1, 2, 0, 1, 2]  // 答题答案（可选）
}
```

**参数说明**：
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| name | string | ✓ | 姓名（最多20字符） |
| year | integer | ✓ | 出生年（1900-2100） |
| month | integer | ✓ | 出生月（1-12） |
| day | integer | ✓ | 出生日（1-31） |
| hour | integer | ✗ | 出生时（0-23），null表示未知 |
| minute | integer | ✓ | 出生分（0-59） |
| gender | string | ✓ | male 或 female |
| province | string | ✗ | 省份（用于真太阳时） |
| city | string | ✗ | 城市（用于真太阳时） |
| answers | array | ✗ | 答题答案数组 |

**用户模式响应**（无 X-Debug-Mode）：
```json
{
  "success": true,
  "data": {
    "report_id": "20240410120000_1234",
    "user_info": {
      "name": "张三",
      "gender": "男",
      "birth_time": {
        "original": { "year": 1990, "month": 5, "day": 15, "hour": 14, "minute": 30 },
        "adjusted": { "year": 1990, "month": 5, "day": 15, "hour": 14, "minute": 30 },
        "location": { "province": "北京市", "city": "北京市", "longitude": 116.41, "latitude": 39.91 }
      }
    },
    "ai_report": "AI生成的天赋分析报告..."
  }
}
```

**调试模式响应**（有 X-Debug-Mode: true）：
```json
{
  "success": true,
  "data": {
    "report_id": "...",
    "user_info": { ... },
    "bazi": {
      "year_gan": "庚", "year_zhi": "午",
      "month_gan": "辛", "month_zhi": "巳",
      "day_gan": "壬", "day_zhi": "申",
      "time_gan": "丁", "time_zhi": "未",
      "day_master": "壬"
    },
    "analysis": {
      "strength": "身强",
      "main_pattern": "食神格",
      "wuxing_energy": { "金": 25.0, "木": 15.5, "水": 20.3, "火": 18.2, "土": 21.0 },
      "shishen_energy": { "食神": 25.0, "伤官": 15.0, ... },
      "yong_shen": ["木", "火"],
      "xi_shen": ["金", "水"],
      "ji_shen": ["土"]
    },
    "ai_report": "...",
    "ai_prompt": "AI提示词...",
    "_debug_full_data": { ... }  // 完整六级论级数据
  }
}
```

### 3. AI分析报告生成

```http
POST /api/analyze-ai
Content-Type: application/json
X-Debug-Mode: true  # 可选
```

**请求体**：
```json
{
  "report_id": "20240410120000_1234",
  "basic_result": { ... }  // /api/analyze 返回的完整数据
}
```

**响应**：
```json
{
  "success": true,
  "ai_report": "# 您的天赋分析报告\n\n## 一、性格特质..."
}
```

### 4. 提交用户反馈

```http
POST /api/feedback
Content-Type: application/json
```

**请求体**：
```json
{
  "rating": 5,                    // 评分 1-5
  "feedback_text": "非常好用！",   // 反馈文字（可选）
  "experience_type": "overall"    // 类型：overall|design|content|feature
}
```

**响应**：
```json
{
  "success": true,
  "message": "感谢您的反馈！",
  "feedback_id": 123
}
```

### 5. 获取城市列表

```http
GET /api/cities
```

**响应**：
```json
{
  "success": true,
  "cities": {
    "北京市": ["北京市"],
    "上海市": ["上海市"],
    "广东省": ["广州市", "深圳市", "珠海市", ...],
    ...
  }
}
```

### 6. 获取反馈统计（管理用途）

```http
GET /api/feedback/stats
```

**响应**：
```json
{
  "success": true,
  "total_feedback": 100,
  "average_rating": 4.5,
  "rating_distribution": [
    { "rating": 1, "count": 5 },
    { "rating": 2, "count": 3 },
    { "rating": 3, "count": 12 },
    { "rating": 4, "count": 30 },
    { "rating": 5, "count": 50 }
  ]
}
```

---

## ❓ 常见问题

### 真太阳时相关问题

#### Q1: 什么是真太阳时？为什么要使用？

**解答**：
- **真太阳时**：根据太阳实际位置计算的时间，与标准北京时间（东经120°）可能有差异
- **为什么要用**：八字计算需要准确的太阳位置，中国东西跨度大，新疆与北京时差约2小时
- **使用方式**：选择出生地后，系统自动计算真太阳时校正

#### Q2: 真太阳时计算准确吗？

**计算原理**：
```
真太阳时 = 平太阳时 + 经度时差 + 均时差

经度时差 = (当地经度 - 120°) × 4分钟
均时差 = 地球公转轨道修正（根据日期查表）
```

**精度**：
- 经度时差：精确到分钟
- 均时差：采用插值算法，误差约±30秒
- 满足八字计算需求

### 部署相关问题

#### Q3: 后端启动报错 `ModuleNotFoundError: No module named 'lunar_python'`

**原因**：命理模块未复制

**解决**：
```bash
# 运行复制脚本
copy_bazi_modules.bat

# 或手动复制
xcopy /Y /E "本地路径\bazi-master\*.py" "backend\bazi_modules\"
xcopy /Y /E "本地路径\bazi-master\lunar_python" "backend\bazi_modules\lunar_python\"
```

#### Q4: 前端调用 API 报 CORS 错误

**原因**：后端 CORS 配置不正确

**解决**：
1. 确保后端 `main.py` 中 `allow_origins` 包含前端域名
2. 检查前端 `api/bazi.js` 中 `BASE_URL` 配置正确
3. 本地开发时使用代理或确保前后端同时运行

#### Q5: Render 服务休眠导致首次访问慢

**原因**：Render 免费版 15 分钟无请求会休眠

**解决**：
- 正常现象，首次访问需要 30-60 秒冷启动
- 可购买 Render 付费版避免休眠
- 或使用其他免费方案：Fly.io、Railway（也有类似限制）

### 功能使用问题

#### Q6: 为什么选择了城市，八字结果没有变化？

**可能原因**：
1. 出生地经度接近东经120°（如上海、杭州），时差很小
2. 时辰未知时，不参与真太阳时计算
3. 真太阳时校正后仍在同一时辰内（时辰跨度2小时）

**查看方式**：调试版会显示「已按真太阳时校正：原时间 → 调整后时间」

#### Q7: AI报告生成失败怎么办？

**排查步骤**：
1. 检查后端日志，确认 DeepSeek API Key 是否有效
2. 确认网络能访问 `api.deepseek.com`
3. 检查是否超出 API 调用限制
4. 后端会自动重试，如仍失败会返回错误提示

**备用方案**：基础八字分析不依赖AI，可正常使用

#### Q8: PDF下载中文乱码？

**解决方式**：
- 前端已使用 html2canvas + jsPDF 方案，将HTML渲染为图片再生成PDF
- 避免直接使用中文字体导致的乱码问题
- 确保 html2canvas 和 jspdf 库正确加载

### 开发调试问题

#### Q9: 如何查看完整命理数据？

**方法一**：使用调试版
- 访问 `https://你的域名/debug.html`
- 提交后切换到「调试数据」标签页

**方法二**：API直接调用
```bash
curl -X POST https://bazi-talent-api.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -H "X-Debug-Mode: true" \
  -d '{"name":"测试","year":2000,"month":1,"day":1,"hour":12,"minute":0,"gender":"male"}'
```

#### Q10: 如何修改AI报告的提示词？

**位置**：`backend/services/bazi_service_web.py` 中的 `_build_ai_prompt()` 方法

**修改后**：
1. 本地测试验证
2. 提交到GitHub
3. Render自动重新部署

---

## 📋 功能更新记录

### 已完成功能 ✅

- [x] **双版本架构**
  - [x] 用户版（index.html）- 简洁界面，仅展示AI报告
  - [x] 调试版（debug.html）- 完整数据展示，Debug模式
  
- [x] **用户交互**
  - [x] 引导启动页
  - [x] 6道趣味答题（自动跳转）
  - [x] 出生信息表单（快速输入8/10/12位数字）
  - [x] 省市级联选择器
  - [x] 日期时间滚轮选择器

- [x] **命理计算**
  - [x] 真太阳时自动计算
  - [x] 八字排盘（四柱）
  - [x] 五行能量分析
  - [x] 十神能量分析
  - [x] 格局判定（食神格、伤官格等）
  - [x] 身强身弱判断

- [x] **AI报告**
  - [x] DeepSeek API集成
  - [x] 个性化天赋分析报告
  - [x] Markdown格式渲染

- [x] **数据存储**
  - [x] PostgreSQL用户反馈存储
  - [x] 星级评分系统
  - [x] 反馈统计分析

- [x] **导出功能**
  - [x] PDF报告下载（html2canvas + jsPDF）
  - [x] 中文无乱码方案

---

## 后续计划

### 短期计划（2-4周）

- [ ] **功能增强**
  - [ ] 添加大运流年分析
  - [ ] 支持八字合婚功能
  - [ ] 本地历史记录存储

- [ ] **体验优化**
  - [ ] 添加分析进度动画
  - [ ] 优化真太阳时展示
  - [ ] 添加时辰参考表（帮助用户选择）

### 中期计划（1-2个月）

- [ ] **报告增强**
  - [ ] 多模板PDF导出
  - [ ] 添加命理图表可视化
  - [ ] 支持报告分享（图片/链接）

- [ ] **AI升级**
  - [ ] 支持多AI模型（GPT-4、Claude等）
  - [ ] 提示词自定义功能
  - [ ] 报告多语言支持

### 长期计划（3个月+）

- [ ] **商业化**
  - [ ] 接入支付系统
  - [ ] VIP会员（详细报告、多次分析）
  - [ ] 专家咨询服务

- [ ] **多端扩展**
  - [ ] 微信小程序版本
  - [ ] App版本（Flutter/React Native）

---

## 技术栈总结

| 层级 | 技术 | 用途 |
|------|------|------|
| **前端** | Vue 3 (CDN) | 用户交互界面 |
| **前端构建** | Vite | 开发环境构建 |
| **后端** | FastAPI | API服务框架 |
| **命理计算** | Python + 自定义模块 | 八字排盘、真太阳时 |
| **AI** | DeepSeek API | 个性化报告生成 |
| **数据库** | PostgreSQL | 用户反馈存储 |
| **部署** | GitHub Pages + Render | 前后端分离部署 |
| **PDF** | html2canvas + jsPDF | 前端PDF生成 |

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

**提交规范**：
- Bug 修复：`fix: 修复xxx问题`
- 新功能：`feat: 添加xxx功能`
- 文档更新：`docs: 更新xxx文档`

---

## 📄 开源协议

本项目仅供学习研究使用，命理分析结果仅供参考。

---

## 📞 联系方式

如有问题，请通过 GitHub Issue 反馈。

**项目地址**：https://github.com/huangzisheng2/web_Render

---

**最后更新**：2024年



更新到github：用户遇到了 Git 推送错误：`src refspec main does not match any`。这个错误通常是因为本地没有 `main` 分支，或者没有任何提交。

让我分析一下可能的原因：
1. 可能本地分支名是 `master` 而不是 `main`
2. 可能还没有创建任何提交
3. 可能需要先创建分支

我应该提供解决方案。
这个错误通常是因为本地没有 `main` 分支。让我帮你解决：
原来如此！Git 仓库还没有初始化。让我提供完整的解决方案。
找到原因了！**Git 仓库还没有初始化**。执行以下完整命令：
需要配置 Git 用户信息。让我提供完整的解决方案。
需要配置 Git 用户信息。请按以下步骤操作：

## 完整解决步骤

```bash
# 1. 进入项目目录
cd "g:\07.Project\02.性格测试\03.bazi-talent-render"

# 2. 配置 Git 用户信息（用你的信息替换）
git config user.email "your-email@example.com"
git config user.name "Your Name"

# 3. 初始化仓库（如果还没做）
git init

# 4. 添加所有文件
git add .

# 5. 提交
git commit -m "Initial commit: 天赋性格测评系统"

# 6. 创建 main 分支
git branch -M main

# 7. 添加远程仓库
git remote add origin https://github.com/huangzisheng2/web_Render.git

# 8. 推送（可能需要输入 GitHub 用户名和密码/Token）
git push -u origin main
```

---

## 如果推送被拒绝

**情况 A：远程仓库不为空**

```bash
# 强制推送（会覆盖远程内容，谨慎使用）
git push -f origin main
```

**情况 B：需要 GitHub Token**

GitHub 不再支持密码登录，需要创建 Personal Access Token：
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. 勾选 `repo` 权限
4. 生成后复制 Token
5. 推送时用这个 Token 代替密码

---

## 一键命令（复制粘贴）

```bash
cd "g:\07.Project\02.性格测试\03.bazi-talent-render" && git config user.email "huangzisheng2@example.com" && git config user.name "huangzisheng2" && git init && git add . && git commit -m "Initial commit" && git branch -M main && git remote add origin https://github.com/huangzisheng2/web_Render.git && git push -u origin main
```

**请把邮箱和用户名改成你自己的**，然后粘贴到 PowerShell 执行。"# trigger rebuild"  
