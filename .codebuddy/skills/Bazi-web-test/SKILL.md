---
name: Bazi-web-test
description: 八字天赋测试网页专用开发助手，负责响应式UI设计、跨平台适配、PDF生成优化和代码提交。自动启动ui-ux-pro-max/pdf/typeset skill，区分用户页面与调试页面，支持iOS/Android/电脑/微信多平台适配，具备需求澄清和Self-Improving能力。
---

# Bazi-web-test Skill

## 概述

本Skill专为八字天赋测试Web应用开发而设计，覆盖从UI设计、跨平台适配到代码提交的完整开发流程。核心目标是提高迭代效率，确保设计标准一致性，减少反复调试。

## 触发条件

当用户提出以下类型的请求时，必须启动本Skill：
- 修改/新增/删除页面UI组件或功能块
- 调整响应式布局（手机/电脑端）
- 优化PDF报告生成
- 修改文字排版或报告内容展示
- 新增页面或调整页面流程
- 修复特定平台（iOS/Android/微信）的兼容性问题

## 标准工作流程

### 阶段1：需求澄清（必须执行）

接收用户指令后，首先检查以下信息是否明确。如不明确，必须向用户提问确认：

| 检查项 | 问题模板 | 示例 |
|--------|---------|------|
| 目标页面 | "此修改针对哪个页面？" | 用户页面/调试页面/全局 |
| 目标平台 | "需要适配哪些平台？" | iOS/Android/电脑/微信/全平台 |
| 功能范围 | "是新增、修改还是删除？" | 新增卡片/修改文字/删除按钮 |
| 响应式要求 | "是否需要同步调整手机/电脑端？" | 是，保持比例一致 |

**禁止假设**：不得假设用户意图，必须确认后再执行。

### 阶段2：Skill联动（自动执行）

根据需求类型，自动启动对应Skill：

```
if (涉及UI设计修改):
    启动 ui-ux-pro-max skill
    
if (涉及PDF报告生成):
    启动 pdf skill
    约束条件: 文件大小 ≤ 10MB, 清晰度保持较高
    
if (涉及文字排版优化):
    启动 typeset skill
    应用场景: 报告内容预览卡片、AI分析报告展示
```

### 阶段3：平台区分设计

#### 3.1 平台识别矩阵

| 平台 | 识别条件 | 设计特点 |
|------|---------|---------|
| 电脑端 | `min-width: 1024px` | 居中布局(max-width: 480px), 固定padding, 紧凑组件 |
| 手机端-通用 | `max-width: 1023px` | 全屏, vh/vw单位, 大触摸区域(≥44px) |
| 手机端-iOS | UserAgent包含iPhone/iPad | 启用safe-area-inset, 原生date/time输入 |
| 手机端-Android | UserAgent包含Android | 标准vh布局, 避免iOS特有样式 |
| 微信内置 | UserAgent包含MicroMessenger | 兼容微信JS-SDK, 注意分享卡片 |

#### 3.2 页面类型定义

**用户页面（User Mode）**：
- 文件位置：`frontend/src/components/*.vue`（除DebugRawData.vue, FeedbackDashboard.vue）
- 特点：简洁UI，隐藏技术细节，专注体验
- 路由：landing → intro → form → quiz → loading → result

**调试页面（Debug Mode）**：
- 文件位置：`frontend/src/components/DebugRawData.vue`, `FeedbackDashboard.vue`
- 入口：`frontend/public/debug.html` 或 URL参数 `?debug=true`
- 特点：展示原始数据、多级论级分析、技术详情

### 阶段4：响应式同步规则

修改任何页面时，必须遵循以下同步规则：

```
Rule 1: 修改电脑端样式时
→ 检查手机端是否需要对应调整
→ 确保视觉比例和谐

Rule 2: 修改手机端样式时
→ 检查是否影响电脑端显示
→ 使用媒体查询隔离变化

Rule 3: 新增组件时
→ 同时提供桌面端和移动端样式
→ 使用clamp()实现流体字体
→ 触摸目标最小44px
```

### 阶段5：代码生成与检查

生成代码后执行以下检查：

- [ ] 是否包含 `env(safe-area-inset-*)` 刘海屏适配
- [ ] 是否使用 `100dvh` 而非 `100vh`
- [ ] 字体大小是否使用 `clamp()` 或相对单位
- [ ] 触摸区域是否 ≥ 44px
- [ ] 是否区分 `.modal-overlay` 和 `.picker-modal-overlay` 位置
- [ ] 性别图标是否正确（男♂蓝/女♀粉）

### 阶段6：Git提交（自动执行）

代码生成完成后：

```bash
# 1. 检查变更
git status

# 2. 添加到暂存区
git add <修改的文件>

# 3. 提交（使用GitHub Desktop风格的消息）
git commit -m "<type>: <description>

- 修改详情1
- 修改详情2

Closes #<issue号>"

# type选项:
# feat: 新功能
# fix: 修复
# ui: UI调整
# refactor: 重构
# perf: 性能优化
```

## 核心设计标准

### 1. 颜色系统

```css
/* 主色调 */
--color-primary: #8EC5FC;      /* 天蓝 - 主要交互 */
--color-secondary: #A8E6CF;    /* 薄荷绿 - 辅助 */
--color-accent: #F472B6;       /* 粉红 - 女性/强调 */
--color-male: #3B82F6;         /* 深蓝 - 男性选中 */
--color-female: #EC4899;       /* 玫红 - 女性选中 */

/* 背景渐变 */
--bg-gradient: linear-gradient(180deg, #F0F9FF 0%, #FDFCF8 50%, #F0FFF4 100%);

/* 文字 */
--text-primary: #4A5568;       /* 深灰 - 标题 */
--text-secondary: #718096;     /* 中灰 - 正文 */
--text-muted: #A0AEC0;         /* 浅灰 - 提示 */
```

### 2. 布局比例

**电脑端（≥1024px）**：
```css
.page-container {
  max-width: 480px;
  margin: 0 auto;
}

.card {
  padding: 20px 24px;
  border-radius: 16px;
}
```

**手机端（<1024px）**：
```css
.page-container {
  padding: env(safe-area-inset-top) 5vw env(safe-area-inset-bottom);
}

.card {
  padding: 3vh 4vw;
  border-radius: 16px;
}
```

### 3. 字体规范

```css
/* 标题 */
font-size: clamp(1.5rem, 6vw, 1.75rem);
font-weight: 700;

/* 正文 */
font-size: clamp(0.9375rem, 4vw, 1rem);
line-height: 1.6;

/* 小字 */
font-size: clamp(0.75rem, 3vw, 0.8125rem);
```

### 4. 组件规范

**按钮**：
- 高度：≥ 44px（触摸目标）
- 圆角：12-16px
- 阴影：`0 4px 16px rgba(142, 197, 252, 0.3)`
- 渐变：`linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%)`

**卡片**：
- 背景：白色
- 边框：`1px solid rgba(142, 197, 252, 0.15)`
- 阴影：`0 2px 12px rgba(142, 197, 252, 0.08)`
- 圆角：16px

**输入框**：
- 边框：`2px solid #E2E8F0`
- 聚焦：`border-color: #8EC5FC`
- 圆角：12px

## 特殊场景处理

### 场景1：日期选择器

- iOS：使用原生 `type="date"` 和 `type="time"`
- Android/电脑：使用滚轮选择器
- 位置：弹窗顶部对齐（约10vh），确保底部可选

### 场景2：PDF生成

约束条件：
- 文件大小 ≤ 10MB
- 图片质量：JPEG 0.88-0.92
- 分辨率：手机1.5x，电脑2x
- 使用 `html2canvas` + `jsPDF`

### 场景3：页面跳转

每次路由切换必须：
```javascript
window.scrollTo({ top: 0, behavior: 'smooth' });
document.documentElement.scrollTop = 0;
document.body.scrollTop = 0;
```

## Self-Improving 机制

### 学习记录

记录以下信息到 `references/lessons-learned.md`：

1. 用户反复修改的点
2. 跨平台兼容性问题及解决方案
3. 性能优化经验
4. 用户反馈的设计问题

### 定期检查

每周检查一次：
- 是否有新的平台适配需求（如新iPhone型号）
- 设计趋势变化
- 性能瓶颈

## 参考资源

- `references/platform-matrix.md` - 平台适配矩阵
- `references/component-library.md` - 组件库文档
- `assets/frontend-template/` - 前端项目模板

## 禁止事项

1. 不得使用固定像素单位（px）定义关键尺寸（应使用rem/vw/vh/clamp）
2. 不得遗漏安全区适配（safe-area-inset）
3. 不得混淆用户页面和调试页面的修改范围
4. 不得在没有确认的情况下假设用户需求
5. PDF文件大小超过10MB必须优化

## 示例对话

**用户**："在结果页面新增一个分享按钮"

**Agent**：
1. 启动 Bazi-web-test skill
2. 提问："此分享按钮是针对用户页面还是调试页面？需要支持哪些平台（微信/系统分享）？"
3. 确认后启动 ui-ux-pro-max skill 设计按钮样式
4. 同时适配电脑端和手机端
5. 生成代码
6. 自动提交到GitHub Desktop

---

**版本**: 1.0.0
**更新日期**: 2026-04-18
**作者**: 根据用户需求定制
