# 八字测试项目组件库

## 页面组件

### 1. LandingPage（引导页）

**用途**：应用入口，展示核心卖点

**包含元素**：
- Logo图标（带动画）
- 主标题 + 副标题
- 3个特色介绍卡片
- 免责声明
- 开始按钮

**设计要点**：
- 背景渐变：`linear-gradient(180deg, #F0F9FF 0%, #FDFCF8 50%, #F0FFF4 100%)`
- Logo呼吸动画：box-shadow 脉动
- 按钮悬浮上移效果

---

### 2. IntroPage（介绍页）

**用途**：说明测试意义，建立用户信任

**包含元素**：
- 4个介绍卡片（发现天赋/自我探索/认识自己/传统+AI）
- 流程步骤指示器
- 下一步按钮

**设计要点**：
- 卡片水平布局，图标在左
- 步骤圆点带渐变背景
- 移动端保持卡片垂直堆叠

---

### 3. StepForm（信息填写页）

**用途**：收集用户出生信息

**包含元素**：
- 姓名输入框
- 性别选择（男/女）
- 出生日期时间选择器
- 出生地点选择器
- 提交按钮

**设计要点**：
- 性别图标：男♂蓝色、女♀粉色
- 日期选择器：iOS原生/自定义滚轮
- 地点选择器：搜索+省份城市双列
- 输入框聚焦边框变蓝

---

### 4. QuizPage（答题页）

**用途**：趣味答题，收集性格倾向

**包含元素**：
- 进度条
- 题号指示器
- 问题卡片
- 4个选项按钮
- 导航按钮

**设计要点**：
- 选项带A/B/C/D字母标识
- 选中状态：渐变背景+阴影
- 自动进入下一题（非最后一题）
- 问题文字带引号装饰

---

### 5. LoadingPage（加载页）

**用途**：报告生成等待，缓解焦虑

**包含元素**：
- 旋转加载动画/完成动画
- 进度步骤（4步）
- 趣味提示（5条轮换）
- 预计时间提示
- 完成后的查看报告按钮

**设计要点**：
- 多层旋转环动画（不同颜色、速度）
- 步骤圆点带动画状态
- 完成时显示勾选动画

---

### 6. ResultDisplay（结果页）

**用途**：展示分析报告

**包含元素**：
- 用户信息头部
- AI报告卡片
- 反馈评分模块
- 下载/重新分析按钮

**设计要点**：
- 报告内容使用Markdown渲染
- 反馈支持多维度评分
- 按钮固定在底部

---

## 通用组件

### Button 按钮

**变体**：
1. **主按钮**：渐变背景，白色文字
2. **次按钮**：白色背景，灰色边框
3. **图标按钮**：仅图标，圆形

**样式**：
```css
.btn-primary {
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  border-radius: 14px;
  padding: 2.5vh 6vw;
  box-shadow: 0 4px 16px rgba(142, 197, 252, 0.3);
}
```

---

### Card 卡片

**样式**：
```css
.card {
  background: white;
  border-radius: 16px;
  padding: 3vh 4vw;
  box-shadow: 0 2px 12px rgba(142, 197, 252, 0.08);
  border: 1px solid rgba(142, 197, 252, 0.15);
}
```

---

### Modal 弹窗

**类型**：
1. **底部弹窗**：日期/地点选择器
2. **居中弹窗**：确认对话框

**样式**：
```css
.modal-overlay {
  position: fixed;
  background: rgba(74, 85, 104, 0.5);
  display: flex;
  align-items: flex-start; /* 顶部对齐 */
  justify-content: center;
  padding-top: 10vh;
}

.modal-content {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-width: 400px;
  max-height: 75vh;
}
```

---

### Input 输入框

**样式**：
```css
.input {
  width: 100%;
  padding: 2vh 4vw;
  font-size: clamp(1rem, 4vw, 1.0625rem);
  border: 2px solid #E2E8F0;
  border-radius: 12px;
  transition: all 0.2s;
}

.input:focus {
  outline: none;
  border-color: #8EC5FC;
  box-shadow: 0 0 0 4px rgba(142, 197, 252, 0.15);
}
```

---

### Icon 图标

**来源**：Lucide Icons（SVG）

**常用图标**：
- 用户：`User`
- 日历：`Calendar`
- 地图：`MapPin`
- 箭头：`ChevronRight`, `ArrowRight`
- 星星：`Star`
- 消息：`MessageCircle`
- 下载：`Download`
- 刷新：`RefreshCw`

---

## 布局规范

### 间距系统

| 名称 | 值 | 用途 |
|------|-----|------|
| xs | 1vh / 1vw | 紧凑间距 |
| sm | 2vh / 2vw | 组件内部 |
| md | 3vh / 3vw | 组件之间 |
| lg | 4vh / 4vw | 区块之间 |
| xl | 5vh / 5vw | 页面边距 |

### 字体层级

| 级别 | 大小 | 用途 |
|------|------|------|
| H1 | clamp(1.5rem, 6vw, 1.75rem) | 页面主标题 |
| H2 | clamp(1.125rem, 5vw, 1.25rem) | 卡片标题 |
| Body | clamp(0.9375rem, 4vw, 1rem) | 正文 |
| Small | clamp(0.75rem, 3vw, 0.8125rem) | 提示文字 |
| Caption | clamp(0.6875rem, 3vw, 0.75rem) | 标签 |

---

## 动画规范

### 过渡时间

- 微交互（按钮悬浮）：200ms
- 页面切换：300ms
- 弹窗出现：300ms
- 加载动画：1s+（循环）

### 缓动函数

```css
/* 标准 */
transition: all 0.3s ease;

/* 弹性 */
transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

/* 平滑 */
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
```

### 常用动画

```css
/* 淡入上移 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 呼吸效果 */
@keyframes breathe {
  0%, 100% { box-shadow: 0 8px 24px rgba(142, 197, 252, 0.4); }
  50% { box-shadow: 0 8px 32px rgba(142, 197, 252, 0.6); }
}

/* 旋转 */
@keyframes spin {
  to { transform: rotate(360deg); }
}
```
