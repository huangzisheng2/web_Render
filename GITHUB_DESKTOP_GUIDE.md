# GitHub Desktop 使用指南

## 提交本次修改的步骤

### 1. 在GitHub Desktop中提交更改

1. 打开GitHub Desktop应用
2. 确保左侧选中的是 `03.bazi-talent-render` 仓库
3. 在左侧栏会看到所有修改的文件列表：
   - `backend/services/bazi_service.py`
   - `backend/services/pdf_service.py`
   - `backend/main.py`
   - `frontend/index.html`
   - `frontend/src/App.vue`
   - `frontend/src/components/BaziForm.vue`
   - `frontend/src/components/SixLevelAnalysis.vue`

4. 在下方的 "Summary (required)" 框中输入提交信息：
```
更新八字分析系统功能

- 移除废弃的apple-mobile-web-app-capable meta标签
- 分离基础分析和AI分析，基础分析不再同步执行AI
- PDF报告仅保留AI分析文字结果
- 添加快速文本输入功能（支持YYYYMMDD、YYYYMMDDHH、YYYYMMDDHHmm格式）
- 整合出生日期和时间选择，添加"时辰未知"按钮
- 优化六级论级分析结果显示，支持更多详细数据展示
```

5. 点击 "Commit to main" 按钮

6. 点击 "Push origin" 将更改推送到GitHub

### 2. 部署后端到Render

如果使用Render部署后端：

1. 修改推送到GitHub后，Render会自动检测到更改并开始部署
2. 访问Render Dashboard查看部署进度
3. 等待部署完成即可测试新功能

### 3. 部署前端到GitHub Pages

1. 在本地终端执行：
```bash
cd frontend
npm run build
```

2. 将 `dist` 文件夹中的内容推送到 `gh-pages` 分支：
```bash
git subtree push --prefix frontend/dist origin gh-pages
```

或者使用 GitHub Actions 自动部署（如果已配置）

## 本次修改的功能清单

### ✅ 已完成的修改

1. **Meta标签修复**
   - 删除了已废弃的 `apple-mobile-web-app-capable`

2. **基础分析与AI分析分离**
   - `/api/analyze` 接口现在只执行基础分析（四柱、六级论级）
   - AI分析通过 `/api/analyze-ai` 接口单独调用
   - 点击"开始分析"后不再等待AI，立即显示基础结果

3. **PDF报告简化**
   - 只包含用户信息和AI分析文字内容
   - 去除了四柱、五行能量等基础信息

4. **输入界面优化**
   - 新增快速文本输入框
   - 支持格式：
     - `19980614` - 无时柱（8位）
     - `1998061416` - 有时辰无分钟（10位）
     - `199806141600` - 有时辰有分钟（12位）
   - 点击"解析"按钮自动填充表单
   - 新增"时辰未知"按钮
   - 出生日期和时间整合在一起显示

5. **基础分析结果优化**
   - 修复了"未知"数据显示问题
   - 支持显示起运计算过程
   - 支持显示十二长生、纳音、神煞等详细信息
   - 支持显示天干地支作用关系详解
   - 支持显示大运流年五行能量影响

## 测试建议

提交后请测试以下场景：

1. 快速输入测试：
   - 输入 `19980614` 点击解析
   - 输入 `1998061416` 点击解析
   - 输入 `199806141630` 点击解析

2. 时辰未知测试：
   - 点击"时辰未知"按钮，确认时柱显示为"未提供"

3. 基础分析测试：
   - 确认点击"开始分析"后快速返回结果（不等待AI）
   - 确认六级论级都有数据（不是"未知"）
   - 展开各论级查看详细信息

4. AI分析测试：
   - 点击"一键分析天赋"按钮
   - 确认10-30秒后AI报告生成

5. PDF下载测试：
   - AI报告生成后点击"下载报告"
   - 确认PDF只包含AI分析文字

## 问题排查

如果基础分析结果仍显示"未知"：
1. 检查Render后端日志
2. 确认 `bazi_modules` 目录已正确上传
3. 确认 `bazi_geju_refactored_v5.py` 文件完整

如果需要帮助，请提供：
- Render后端日志
- 浏览器控制台错误信息
- 具体输入的测试数据
