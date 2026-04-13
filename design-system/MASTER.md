# 八字天赋分析 - 设计系统

## 项目概述
面向青少年的八字天赋分析应用，设计风格柔和护眼、简约清爽。

---

## 一、配色体系

### 主色调
- **浅蓝色 (Primary Blue)**: `#8EC5FC` - 用于主要按钮、链接、强调
- **米白色 (Off White)**: `#FDFCF8` - 页面背景
- **柔白色 (Soft White)**: `#FFFFFF` - 卡片背景

### 辅助色
- **浅绿色 (Accent Green)**: `#A8E6CF` - 成功状态、正向反馈
- **薄荷绿 (Mint)**: `#DCEDC1` - 次要强调
- **淡紫色 (Soft Purple)**: `#DDBEA9` - 特殊标记

### 中性色
- **深灰 (Text Primary)**: `#4A5568` - 主要文字
- **中灰 (Text Secondary)**: `#718096` - 次要文字
- **浅灰 (Border)**: `#E2E8F0` - 边框、分割线
- **背景灰 (Background)**: `#F7FAFC` - 区块背景

### 功能色
- **错误红**: `#FC8181` (柔和红色)
- **警告黄**: `#F6E05E` (柔和黄色)
- **成功绿**: `#68D391` (柔和绿色)

---

## 二、字体系统

### 字体选择
- **主字体**: `"PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif`
- **特点**: 圆润无衬线，易读性强

### 字号规范
| 级别 | 大小 | 用途 |
|------|------|------|
| 标题 H1 | 28px | 页面大标题 |
| 标题 H2 | 22px | 区块标题 |
| 标题 H3 | 18px | 卡片标题 |
| 正文 | 16px | 主要文字 |
| 辅助文字 | 14px | 描述、提示 |
| 小字 | 12px | 标签、注释 |

### 行高
- 标题: 1.3
- 正文: 1.6
- 紧凑: 1.4

---

## 三、间距系统

### 基础单位: 8px

| 名称 | 值 | 用途 |
|------|-----|------|
| xs | 4px | 图标间距 |
| sm | 8px | 紧凑间距 |
| md | 16px | 标准间距 |
| lg | 24px | 区块间距 |
| xl | 32px | 大区块间距 |
| 2xl | 48px | 页面间距 |

---

## 四、圆角系统

| 名称 | 值 | 用途 |
|------|-----|------|
| sm | 8px | 小按钮、标签 |
| md | 12px | 输入框、卡片 |
| lg | 16px | 大卡片 |
| xl | 24px | 页面容器 |
| full | 9999px | 圆形元素 |

---

## 五、阴影系统

### 柔和阴影（符合护眼理念）
```css
/* 小阴影 */
shadow-sm: 0 2px 8px rgba(142, 197, 252, 0.1)

/* 中阴影 */
shadow-md: 0 4px 16px rgba(142, 197, 252, 0.15)

/* 大阴影 */
shadow-lg: 0 8px 24px rgba(142, 197, 252, 0.2)
```

---

## 六、组件规范

### 按钮

#### 主要按钮
```css
background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
color: #FFFFFF;
padding: 14px 28px;
border-radius: 12px;
font-weight: 600;
box-shadow: 0 4px 16px rgba(142, 197, 252, 0.3);
```

#### 次要按钮
```css
background: #FFFFFF;
border: 2px solid #E2E8F0;
color: #4A5568;
padding: 12px 24px;
border-radius: 12px;
```

#### 幽灵按钮
```css
background: transparent;
border: 2px dashed #8EC5FC;
color: #8EC5FC;
padding: 12px 24px;
border-radius: 12px;
```

### 卡片

#### 标准卡片
```css
background: #FFFFFF;
border-radius: 16px;
padding: 24px;
box-shadow: 0 4px 16px rgba(142, 197, 252, 0.1);
border: 1px solid rgba(142, 197, 252, 0.2);
```

#### 高亮卡片
```css
background: linear-gradient(135deg, #F0F9FF 0%, #F0FFF4 100%);
border-radius: 16px;
padding: 24px;
border: 2px solid rgba(142, 197, 252, 0.3);
```

### 输入框

```css
background: #FFFFFF;
border: 2px solid #E2E8F0;
border-radius: 12px;
padding: 14px 16px;
font-size: 16px;
transition: all 0.3s ease;

&:focus {
  border-color: #8EC5FC;
  box-shadow: 0 0 0 4px rgba(142, 197, 252, 0.2);
}
```

### 滚轮选择器 (Wheel Picker)

```css
.wheel-container {
  background: linear-gradient(180deg, 
    rgba(255,255,255,0) 0%, 
    rgba(255,255,255,1) 20%, 
    rgba(255,255,255,1) 80%, 
    rgba(255,255,255,0) 100%
  );
  border-radius: 12px;
}

.wheel-item {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #718096;
  transition: all 0.2s;
}

.wheel-item.active {
  font-size: 20px;
  font-weight: 600;
  color: #4A5568;
}
```

---

## 七、动画规范

### 过渡时间
- 微交互: 150ms
- 标准过渡: 300ms
- 页面切换: 400ms

### 缓动函数
- 标准: `cubic-bezier(0.4, 0, 0.2, 1)`
- 弹跳: `cubic-bezier(0.68, -0.55, 0.265, 1.55)`
- 平滑: `ease-out`

### 常用动画
```css
/* 淡入 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 上滑进入 */
@keyframes slideUp {
  from { 
    opacity: 0; 
    transform: translateY(20px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}

/* 脉冲（用于强调） */
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* 呼吸光效 */
@keyframes breathe {
  0%, 100% { box-shadow: 0 0 20px rgba(142, 197, 252, 0.3); }
  50% { box-shadow: 0 0 40px rgba(142, 197, 252, 0.6); }
}
```

---

## 八、布局规范

### 页面结构
```
┌─────────────────────────────────────┐
│           居中容器 (max-width)        │
│  ┌───────────────────────────────┐  │
│  │         卡片区域                │  │
│  │                               │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### 响应式断点
- 移动端: < 640px
- 平板: 640px - 1024px
- 桌面: > 1024px

### 容器宽度
- 移动端: 100% - 32px padding
- 平板: 600px
- 桌面: 720px

---

## 九、图标规范

- 使用 Lucide 图标库
- 线性风格（stroke-width: 2）
- 统一尺寸: 20px (标准), 24px (大)
- 颜色跟随文字或使用主色调

---

## 十、特殊元素

### 进度指示器
```css
background: linear-gradient(90deg, #8EC5FC 0%, #A8E6CF 100%);
height: 4px;
border-radius: 2px;
```

### 标签/徽章
```css
background: rgba(142, 197, 252, 0.15);
color: #4A5568;
padding: 6px 12px;
border-radius: 20px;
font-size: 12px;
```

### 星级评分
```css
.star {
  color: #F6E05E;  /* 选中 */
  color: #E2E8F0;  /* 未选中 */
}
```

---

## 十一、UX原则

1. **降低认知负担**: 分步引导，明确进度
2. **正向反馈**: 操作后立即给予视觉反馈
3. **容错设计**: 错误提示亲切友好
4. **触控友好**: 最小点击区域 44×44px
5. **视觉层次**: 通过大小、颜色、间距建立层次
6. **一致性**: 所有页面遵循相同的设计语言
