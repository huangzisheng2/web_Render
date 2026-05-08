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
4. **AI分析**：双模式AI分析（简易版+深度探索版），调用DeepSeek API生成个性化天赋报告
5. **天赋画像**：综合画像卡片展示日柱概述、天赋标签、Q版人物、五行属性、关键词等
6. **报告下载**：支持PDF导出
7. **用户反馈**：1-5星评分+文字反馈，存储到PostgreSQL数据库

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
│  结果页双Tab架构：                                       │
│  • 天赋概览（Tab 1）：天赋综合画像 + 性格/天赋/场景卡片  │
│  • 深度探索（Tab 2）：一键深度分析 + 四模块AI报告        │
├─────────────────────────────────────────────────────────┤
│  核心组件：                                             │
│  • TalentProfileCard  天赋综合画像卡片                  │
│  • StepForm           表单（日期选择/省市联动）         │
│  • LoadingPage        分析等待页（步骤动画）            │
│  • ReportPage         报告页（双Tab+AI分析）            │
│  • PDF生成（html2canvas + jsPDF）                      │
│  • 用户反馈模块（星级评分+文字）                       │
└─────────────────────────────────────────────────────────┘
```

### AI提示词架构

```
┌──────────────────────────────────────────────────────────┐
│                    AI 分析双模式                          │
├──────────────────────────────────────────────────────────┤
│  天赋概览（自动触发）                                    │
│  ├─ 接口：POST /api/analyze (mode=simple)               │
│  ├─ 提示词：_build_simple_prompt()                      │
│  ├─ 输出：3个板块（核心天赋/性格分析/场景建议）          │
│  └─ max_tokens: 4000                                    │
├──────────────────────────────────────────────────────────┤
│  深度探索（手动触发）                                    │
│  ├─ 接口：POST /api/analyze (mode=deep_explore)         │
│  ├─ 提示词：_build_deep_explore_prompt()                │
│  ├─ 输出：4个模块+结语（天赋图谱/落地指南/使用说明/成长提醒）│
│  └─ max_tokens: 8000                                    │
├──────────────────────────────────────────────────────────┤
│  规则：                                                  │
│  • 两种模式使用同一份用户输入信息                        │
│  • 两个Tab的AI分析结果完全独立，互不干扰                 │
│  • 深度探索从 props.result 中提取完整出生信息            │
└──────────────────────────────────────────────────────────┘
```

### 后端功能模块

```
┌─────────────────────────────────────────────────────────┐
│                     后端服务层                           │
├─────────────────────────────────────────────────────────┤
│  FastAPI 应用                                          │
│  ├─ /api/analyze          # 八字分析主接口              │
│  │                          mode: simple/detail/deep    │
│  ├─ /api/analyze-ai       # AI报告生成（兼容旧版）      │
│  ├─ /api/feedback         # 用户反馈接口                │
│  ├─ /api/cities           # 城市列表接口                │
│  └─ /api/download/{id}    # PDF下载接口                 │
├─────────────────────────────────────────────────────────┤
│  业务服务层：                                           │
│  • BaziAnalysisServiceWeb   # 八字分析服务              │
│  │   ├─ get_location()      # 获取城市经纬度            │
│  │   ├─ apply_true_solar_time()  # 真太阳时计算         │
│  │   ├─ convert_to_bazi()   # 转换为八字                │
│  │   ├─ analyze_basic()     # 基础分析（六级论级）      │
│  │   ├─ analyze_ai()        # AI分析报告生成            │
│  │   │   ├─ _build_simple_prompt()     # 简易版提示词   │
│  │   │   ├─ _build_deep_explore_prompt() # 深度版提示词 │
│  │   │   └─ _build_ai_prompt()         # 旧版兼容      │
│  │   └─ _call_deepseek_api() # DeepSeek API调用        │
│  │                                                      │
│  • PDFService               # PDF生成服务               │
│      ├─ generate_pdf_report()  # ReportLab生成PDF       │
│      └─ get_download_url()     # 获取下载链接           │
├─────────────────────────────────────────────────────────┤
│  命理模块层（bazi_modules）：                            │
│  • lunar_python          # 农历阳历转换                 │
│  • bazi_bridge           # 八字计算核心                 │
│  • true_solar_time       # 真太阳时计算                 │
│  • city_database         # 城市经纬度数据库             │
│  • bazi_geju_refactored_v5  # 格局分析                  │
│  • ganzhi                # 天干地支数据库               │
├─────────────────────────────────────────────────────────┤
│  数据存储层：                                           │
│  • PostgreSQL (Render)   # 用户反馈数据                 │
│  • DeepSeek API          # AI分析报告生成               │
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
    • 解析 mode 参数（simple/detail/deep_explore）
    • 检查 X-Debug-Mode 请求头
    ↓
【Step 2: 真太阳时计算】（如果提供了出生地）
    • 根据省市查询 city_database 获取经纬度
    • calculate_longitude_diff(): 计算经度时差
    • get_equation_of_time(): 获取均时差
    • calculate_true_solar_time(): 计算真太阳时
    ↓
【Step 3: 八字排盘】
    • Solar.to_lunar(): 公历转农历
    • 计算四柱（年柱、月柱、日柱、时柱）
    ↓
【Step 4: 命理分析】
    • 分析日主（日柱天干）
    • 计算十神、判断身强身弱
    • 判定格局、分析五行能量
    • 六级论级分析
    ↓
【Step 5: AI报告生成】
    • simple 模式：_build_simple_prompt()，3板块
    • deep_explore 模式：_build_deep_explore_prompt()，4模块+结语
    • detail 模式：不自动执行AI，等待手动触发
    ↓
【Step 6: 响应组装】
    • 用户模式：返回 {report_id, user_info, bazi, ai_report, raw_data}
    • 调试模式：额外返回完整命理数据
```

### 3. 前端天赋画像数据流

```
/api/analyze 返回结果 (props.result)
    ↓
TalentProfileCard 组件
    ├─ 日主 → getDayMasterTrait() → 五行颜色/图标/Q版头像
    ├─ 日柱 → dayPillar (如"壬辰")
    ├─ 日柱概述 → DAY_PILLAR_SUMMARIES["壬辰"] → "气魄雄浑，龙归大海"
    ├─ 日柱长文 → DAY_COLUMN_SUMMARIES[dayMaster] → 天干性格描述
    ├─ 天赋标签 → talentTags (AI返回的**标签名**)
    ├─ 天赋关键词 → keywords → pill按钮展示
    ├─ 特质概括 → traitDescription
    └─ 历史人物画像 → historicalFigures (最多2位)
```

---

## 📁 项目结构

```
web_Render/
├── 📂 backend/                      # FastAPI 后端
│   ├── 📄 main.py                  # 主入口，路由配置
│   ├── 📄 feedback.py              # 用户反馈模块，PostgreSQL存储
│   ├── 📂 services/                # 业务服务层
│   │   ├── 📄 bazi_service_web.py  # 八字分析服务（真太阳时+AI+双模式提示词）
│   │   └── 📄 pdf_service.py       # PDF生成服务
│   ├── 📂 bazi_modules/            # 命理模块
│   │   ├── 📄 bazi_bridge.py       # 八字计算核心桥接
│   │   ├── 📄 bazi_geju_refactored_v5.py  # 格局分析
│   │   ├── 📄 ganzhi.py            # 天干地支数据库
│   │   ├── 📄 true_solar_time.py   # 真太阳时计算
│   │   ├── 📄 city_database.py     # 城市经纬度数据库
│   │   └── 📂 lunar_python/        # 农历阳历转换库
│   ├── 📄 requirements.txt         # Python依赖
│   ├── 📄 render.yaml              # Render部署配置
│   └── 📄 Dockerfile               # Docker配置
│
├── 📂 frontend/                     # 前端（Vue3 + Vite）
│   ├── 📄 index.html               # 用户版入口
│   ├── 📄 debug.html               # 调试版入口
│   │
│   ├── 📂 src/
│   │   ├── 📂 components/
│   │   │   ├── 📄 LandingPage.vue       # 引导页
│   │   │   ├── 📄 QuizPage.vue          # 答题页
│   │   │   ├── 📄 StepForm.vue          # 表单页（日期/省市选择）
│   │   │   ├── 📄 LoadingPage.vue       # 分析等待页
│   │   │   ├── 📄 ReportPage.vue        # 报告页（双Tab架构）
│   │   │   ├── 📄 TalentProfileCard.vue # ⭐ 天赋综合画像卡片
│   │   │   ├── 📄 SimpleReport.vue      # 简易报告
│   │   │   ├── 📄 DetailReport.vue      # 详细报告
│   │   │   ├── 📄 AIReport.vue          # AI报告渲染
│   │   │   ├── 📄 BaziForm.vue          # 八字表单
│   │   │   ├── 📄 BaziPillars.vue       # 四柱排盘
│   │   │   ├── 📄 EnergyCharts.vue      # 五行能量图表
│   │   │   ├── 📄 SharePoster.vue       # 分享海报
│   │   │   ├── 📄 ReportHome.vue        # 报告首页
│   │   │   ├── 📄 SixLevelAnalysis.vue  # 六级论级
│   │   │   ├── 📄 DebugRawData.vue      # 调试原始数据
│   │   │   ├── 📄 FeedbackDashboard.vue # 反馈仪表盘
│   │   │   ├── 📄 ResultDisplay.vue     # 结果展示
│   │   │   └── 📄 IntroPage.vue         # 介绍页
│   │   ├── 📂 api/
│   │   │   └── 📄 bazi.js          # API接口封装（含网络重试）
│   │   ├── 📂 data/
│   │   │   ├── 📄 cities.js        # 省市数据
│   │   │   └── 📄 dayMasterData.js # ⭐ 日主数据（特质/五行/日柱概述/Q版头像）
│   │   ├── 📂 utils/
│   │   │   └── 📄 wuxing.js        # 五行工具函数
│   │   ├── 📂 styles/
│   │   │   └── 📄 index.css        # 全局样式
│   │   ├── 📄 App.vue              # Vue应用根组件
│   │   └── 📄 main.js              # 应用入口
│   │
│   ├── 📄 package.json             # npm依赖
│   └── 📄 vite.config.js           # Vite配置（含0.0.0.0局域网访问）
│
├── 📂 design-system/               # 设计系统文档
│   └── 📄 MASTER.md                # 设计规范
│
├── 📄 copy_bazi_modules.bat        # 一键复制命理模块脚本
├── 📄 README.md                    # 本文件
└── 📄 .gitignore                   # Git忽略配置
```

---

## 📑 目录

- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [本地调试](#本地调试)
- [部署指南](#部署指南)
- [API 文档](#api-文档)
- [常见问题](#常见问题)

---

## 🚀 快速开始

### 一键启动

```bash
# 1. 进入项目目录
cd "c:/Users/10302/Desktop/web_Render"

# 2. 复制命理模块（首次运行）
copy_bazi_modules.bat

# 3. 启动后端
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 4. 新终端 - 启动前端
cd frontend
npm install
npm run dev
```

**访问地址**：
- 前端：http://localhost:5173/web_Render/
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs
- 局域网访问：http://你的IP:5173/web_Render/（Vite 已配置 host: 0.0.0.0）

---

## 🔧 本地调试

### 环境要求

- **Node.js**: >= 16.x
- **Python**: >= 3.10
- **Git**: 任意版本

### 步骤1：复制命理模块

```
copy_bazi_modules.bat
```

### 步骤2：启动后端

```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 步骤3：启动前端

```bash
cd frontend
npm install
npm run dev
```

**局域网访问**：Vite 已配置 `host: '0.0.0.0'`，手机热点连接后可通过电脑IP访问前端页面。

### 调试技巧

| 操作 | 命令/方法 |
|------|-----------|
| 只调试前端UI | 前端启动后，不需要后端也能看到界面 |
| 测试后端API | 使用 http://localhost:8000/docs 可视化测试 |
| 查看后端日志 | 后端终端会显示请求和错误信息 |
| 前端热更新 | 修改代码自动刷新，无需重启 |
| 手机热点测试 | 前端 `0.0.0.0` 已配置，直接用电脑IP+端口访问 |

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

### 部署后端到 Render

1. 访问 https://dashboard.render.com/
2. 创建 Web Service，选择 GitHub 仓库 `web_Render`
3. 配置：

| 配置项 | 值 |
|--------|-----|
| **Name** | `bazi-talent-api` |
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

4. 添加环境变量：`DEEPSEEK_API_KEY` = `你的 Key`

### 部署前端到 GitHub Pages

1. GitHub 仓库 → Settings → Pages → Source: "GitHub Actions"
2. 推送代码后自动触发部署
3. 访问地址：`https://huangzisheng2.github.io/web_Render/`

---

## 📚 API 文档

### 1. 八字分析主接口

```http
POST /api/analyze
Content-Type: application/json
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
  "mode": "simple"
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
| mode | string | ✗ | `simple`(默认) / `detail` / `deep_explore` |

**mode 说明**：

| mode | 行为 | AI提示词 | max_tokens |
|------|------|----------|------------|
| `simple` | 自动执行AI分析 | `_build_simple_prompt()` 3板块 | 4000 |
| `detail` | 不执行AI，返回基础数据 | — | — |
| `deep_explore` | 自动执行深度AI分析 | `_build_deep_explore_prompt()` 4模块 | 8000 |

**用户模式响应**：
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
    "bazi": {
      "day_master": "壬",
      "day_pillar": "壬申"
    },
    "ai_report": "AI生成的天赋分析报告..."
  }
}
```

### 2. AI报告生成（兼容旧版）

```http
POST /api/analyze-ai
Content-Type: application/json
```

**请求体**：
```json
{
  "report_id": "20240410120000_1234",
  "basic_result": { ... },
  "mode": "deep_explore"
}
```

> ⚠️ 推荐使用 `/api/analyze` 的 `mode` 参数替代此接口

### 3. 其他接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/cities` | GET | 获取省市列表 |
| `/api/feedback` | POST | 提交用户反馈 |
| `/api/feedback/stats` | GET | 获取反馈统计 |
| `/api/download/{id}` | GET | 下载PDF报告 |

---

## ❓ 常见问题

### Q1: 手机热点连接后无法访问前端？

**解决**：Vite 已配置 `host: '0.0.0.0'`，确保：
1. 前端开发服务器已启动（`npm run dev`）
2. 手机和电脑在同一热点网络下
3. 用电脑的局域网IP访问（如 `http://192.168.x.x:5173/web_Render/`）
4. API 请求有自动重试机制（最多2次），网络不稳定时会自动重试

### Q2: 深度探索AI分析不可用？

**检查**：
1. 后端 DeepSeek API Key 是否有效
2. 网络能否访问 `api.deepseek.com`
3. 查看浏览器控制台和后端日志的错误信息

### Q3: 真太阳时计算原理？

```
真太阳时 = 平太阳时 + 经度时差 + 均时差
经度时差 = (当地经度 - 120°) × 4分钟
均时差 = 地球公转轨道修正（根据日期查表）
```

### Q4: PDF下载中文乱码？

前端使用 `html2canvas + jsPDF` 方案，将HTML渲染为图片再生成PDF，避免中文字体问题。

### Q5: 如何修改AI报告的提示词？

**位置**：`backend/services/bazi_service_web.py`
- 简易版：`_build_simple_prompt()` 方法
- 深度版：`_build_deep_explore_prompt()` 方法
- 修改后本地测试 → 提交到GitHub → Render自动重新部署

---

## 📋 功能更新记录

### 已完成功能 ✅

- [x] **双版本架构**（用户版 + 调试版）
- [x] **用户交互**（引导页/答题/表单/省市联动/日期滚轮）
- [x] **命理计算**（真太阳时/八字排盘/五行十神/格局判定/六级论级）
- [x] **AI双模式分析**（简易版3板块 + 深度版4模块）
- [x] **天赋综合画像卡片**
  - [x] 日主五行图标 + 日柱 + 日柱概述
  - [x] 60组日柱概述数据（DAY_PILLAR_SUMMARIES）
  - [x] 日柱长文说明（DAY_COLUMN_SUMMARIES）
  - [x] 5个天赋标签 + Q版人物头像
  - [x] 一句话特质概括（书法体）
  - [x] 天赋关键词pill按钮 + 历史人物画像双列布局
- [x] **数据存储**（PostgreSQL反馈存储/星级评分）
- [x] **导出功能**（PDF报告下载）
- [x] **网络兼容**（Vite 0.0.0.0/热点WiFi/API自动重试）

---

## 技术栈总结

| 层级 | 技术 | 用途 |
|------|------|------|
| **前端** | Vue 3 | 用户交互界面 |
| **前端构建** | Vite | 开发环境构建 |
| **后端** | FastAPI | API服务框架 |
| **命理计算** | Python + 自定义模块 | 八字排盘、真太阳时 |
| **AI** | DeepSeek API | 个性化报告生成（双模式） |
| **数据库** | PostgreSQL | 用户反馈存储 |
| **部署** | GitHub Pages + Render | 前后端分离部署 |
| **PDF** | html2canvas + jsPDF | 前端PDF生成 |

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

**提交规范**：
- Bug 修复：`fix: 修复xxx问题`
- 新功能：`feat: 添加xxx功能`
- UI调整：`ui: 优化xxx样式`
- 文档更新：`docs: 更新xxx文档`

---

## 📄 开源协议

本项目仅供学习研究使用，命理分析结果仅供参考。

---

**最后更新**：2026年5月
