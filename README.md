# 天赋性格测评系统

基于中国传统八字命理学的天赋与性格分析系统，结合 AI 技术生成个性化报告。

**技术架构**：Vue3 + Vite + Vant UI（前端）+ FastAPI + Python（后端）+ Render（后端托管）+ GitHub Pages（前端托管）

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
bazi-talent-render/
├── 📂 backend/                 # FastAPI 后端
│   ├── 📄 main.py             # 主入口，路由配置
│   ├── 📂 services/           # 业务服务层
│   │   ├── 📄 bazi_service.py      # 八字分析核心服务
│   │   └── 📄 pdf_service.py       # PDF 生成服务
│   ├── 📂 bazi_modules/       # 命理模块（需从本地复制）
│   ├── 📄 requirements.txt    # Python 依赖
│   ├── 📄 render.yaml         # Render 部署配置
│   ├── 📄 Dockerfile          # Docker 配置
│   └── 📄 .env.example        # 环境变量模板
│
├── 📂 frontend/               # Vue3 前端
│   ├── 📂 src/
│   │   ├── 📂 components/     # Vue 组件
│   │   │   ├── 📄 BaziForm.vue       # 表单组件（输入出生信息）
│   │   │   └── 📄 ResultDisplay.vue  # 结果展示组件
│   │   ├── 📂 api/            # API 接口封装
│   │   │   └── 📄 bazi.js           # 后端接口调用
│   │   ├── 📂 data/           # 静态数据
│   │   │   └── 📄 cities.js         # 全国省市数据
│   │   ├── 📄 App.vue         # 根组件
│   │   └── 📄 main.js         # 入口文件
│   ├── 📄 package.json        # npm 依赖
│   ├── 📄 vite.config.js      # Vite 配置
│   └── 📄 index.html          # HTML 模板
│
├── 📂 .github/workflows/      # GitHub Actions
│   └── 📄 deploy.yml          # 自动部署到 GitHub Pages
│
├── 📄 copy_bazi_modules.bat   # 一键复制命理模块脚本
├── 📄 README.md               # 本文件
└── 📄 .gitignore              # Git 忽略配置
```

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
  "city": "北京市"
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
| province | string | ✓ | 省份 |
| city | string | ✓ | 城市 |

**响应**：
```json
{
  "success": true,
  "data": {
    "report_id": "20240410120000_1234",
    "user_info": { ... },
    "bazi": {
      "year_pillar": "庚午",
      "month_pillar": "辛巳",
      "day_pillar": "壬申",
      "time_pillar": "丁未",
      "day_master": "壬"
    },
    "analysis": {
      "strength": "身强",
      "main_pattern": "食神格",
      "wuxing_energy": { "木": 15.5, "火": 20.3, ... },
      "shishen_energy": { "食神": 25.0, ... }
    },
    "ai_report": "AI 生成的分析报告文本..."
  }
}
```

### 3. 获取城市列表

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
    ...
  }
}
```

### 4. 下载报告

```http
GET /api/download/{report_id}
```

**响应**：
```json
{
  "success": true,
  "download_url": "data:application/pdf;base64,..."
}
```

---

## ❓ 常见问题

### Q1: 后端启动报错 `ModuleNotFoundError: No module named 'lunar_python'`

**原因**：命理模块未复制

**解决**：
```bash
# 运行复制脚本
copy_bazi_modules.bat

# 或手动复制
xcopy /Y /E "G:\07.Project\02.性格测试\01.八字排盘与计算\bazi-master_new\bazi-master\*" "backend\bazi_modules\"
```

### Q2: 前端调用 API 报 CORS 错误

**原因**：后端 CORS 配置不正确或后端未启动

**解决**：
1. 确保后端已启动
2. 检查 `main.py` 中的 `allow_origins` 是否包含前端域名

### Q3: DeepSeek API 调用失败

**原因**：API Key 无效或网络问题

**解决**：
1. 检查 `.env` 文件中的 `DEEPSEEK_API_KEY`
2. 测试 API Key 是否有效
3. 检查网络是否能访问 `api.deepseek.com`

### Q4: PDF 下载失败

**原因**：reportlab 未安装或浏览器阻止下载

**解决**：
1. 安装依赖：`pip install reportlab`
2. 前端会自动回退到 html2pdf 方案
3. 检查浏览器是否阻止了弹出窗口

### Q5: Render 服务休眠导致首次访问慢

**原因**：Render 免费版 15 分钟无请求会休眠

**解决**：
- 正常现象，首次访问需要 30 秒左右冷启动
- 可购买 Render 付费版避免休眠

### Q6: GitHub Pages 部署后 404

**原因**：路径配置不正确

**解决**：
1. 检查 `vite.config.js` 中的 `base` 是否为 `/web_Render/`
2. 检查仓库名是否正确
3. 确保已启用 GitHub Pages

---

## 📋 后续计划

### 短期计划（1-2周）

- [ ] **功能完善**
  - [ ] 添加更多命理分析维度（大运、流年）
  - [ ] 支持八字合婚功能
  - [ ] 添加历史记录功能（本地存储）

- [ ] **体验优化**
  - [ ] 添加分析进度条
  - [ ] 优化移动端适配
  - [ ] 添加加载动画

- [ ] **Bug修复**
  - [ ] 修复真太阳时计算精度问题
  - [ ] 修复部分城市找不到经纬度的问题

### 中期计划（1个月）

- [ ] **存储升级**
  - [ ] 接入数据库存储（PostgreSQL/SQLite）
  - [ ] 用户历史报告查询
  - [ ] 报告分享功能

- [ ] **PDF增强**
  - [ ] 更多 PDF 模板选择
  - [ ] 添加命理图表到 PDF
  - [ ] 支持导出 Word 格式

- [ ] **AI优化**
  - [ ] 支持多个 AI 模型切换
  - [ ] 自定义提示词功能
  - [ ] 报告多语言支持（英文、日文）

### 长期计划（3个月）

- [ ] **商业化**
  - [ ] 接入支付系统（微信支付、支付宝）
  - [ ] VIP 会员功能
  - [ ] 专家在线咨询

- [ ] **生态扩展**
  - [ ] 小程序版本
  - [ ] App 版本（Flutter）
  - [ ] API 开放平台

- [ ] **数据积累**
  - [ ] 命理案例库
  - [ ] AI 模型微调
  - [ ] 预测准确率统计

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
