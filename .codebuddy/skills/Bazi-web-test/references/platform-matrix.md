# 平台适配矩阵

## 设备识别代码

```javascript
// 检测是否为移动设备
const isMobileDevice = () => {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera
  return /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent.toLowerCase())
}

// 检测是否为 iOS 设备
const isIOSDevice = () => {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera
  return /iphone|ipad|ipod/i.test(userAgent.toLowerCase())
}

// 检测是否为 Android 设备
const isAndroidDevice = () => {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera
  return /android/i.test(userAgent.toLowerCase())
}

// 检测是否为微信内置浏览器
const isWechat = () => {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera
  return /micromessenger/i.test(userAgent.toLowerCase())
}
```

## CSS 媒体查询

```css
/* 电脑端 */
@media (min-width: 1024px) {
  .page-container {
    max-width: 480px;
    margin: 0 auto;
    box-shadow: 0 0 40px rgba(0, 0, 0, 0.1);
  }
}

/* 平板端 */
@media (min-width: 768px) and (max-width: 1023px) {
  .page-container {
    max-width: 600px;
    margin: 0 auto;
  }
}

/* 手机端 */
@media (max-width: 767px) {
  .page-container {
    width: 100%;
    padding: env(safe-area-inset-top) 5vw env(safe-area-inset-bottom);
  }
}

/* iOS 横屏 */
@media (max-height: 600px) and (orientation: landscape) {
  .modal-overlay {
    padding-top: 5vh;
  }
}
```

## iOS 特殊适配

### 安全区

```css
/* 适配刘海屏/灵动岛 */
.page {
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}

/* 固定底部元素 */
.fixed-bottom {
  padding-bottom: max(20px, env(safe-area-inset-bottom));
}
```

### 输入框防止缩放

```css
input, textarea, select {
  font-size: 16px; /* 小于16px iOS会缩放 */
}
```

### 日期选择器

```vue
<template>
  <!-- iOS使用原生 -->
  <input v-if="isIOS" type="date" v-model="dateValue" />
  <input v-if="isIOS" type="time" v-model="timeValue" />
  
  <!-- Android/电脑使用自定义 -->
  <CustomDatePicker v-else v-model="dateValue" />
</template>
```

## 微信特殊适配

### 分享配置

```javascript
// 微信JS-SDK分享配置
const wxShareConfig = {
  title: '先天天赋探索',
  desc: '发现你与生俱来的潜能',
  link: window.location.href,
  imgUrl: 'https://your-domain.com/share-icon.png',
  success: () => {
    console.log('分享成功')
  }
}
```

### 字体适配

微信内置浏览器可能覆盖字体，需要强制指定：

```css
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif !important;
}
```

## Android 特殊适配

### 底部导航栏

Android可能有虚拟导航栏，需要预留空间：

```css
.bottom-fixed {
  padding-bottom: max(20px, env(safe-area-inset-bottom));
  /* Android可能不需要safe-area，使用vh更安全 */
  margin-bottom: 2vh;
}
```

### 键盘弹起

Android键盘弹起会影响布局，建议：

```javascript
// 输入框聚焦时调整布局
const handleFocus = () => {
  if (isAndroidDevice()) {
    setTimeout(() => {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }, 300)
  }
}
```

## 兼容性测试清单

- [ ] iPhone 14/15 Pro（灵动岛）
- [ ] iPhone 12/13（刘海屏）
- [ ] iPhone SE（无刘海）
- [ ] iPad Pro
- [ ] Android旗舰（三星S系列）
- [ ] Android中端（小米/OPPO/vivo）
- [ ] 微信内置浏览器
- [ ] Chrome桌面
- [ ] Safari桌面
- [ ] 横屏模式
