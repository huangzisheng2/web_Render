# 经验教训记录

## 设计标准迭代记录

### 2026-04-18

#### 性别图标规范
- **问题**：最初女性图标使用错误符号
- **解决**：男♂使用蓝色(#3B82F6)，女♀使用粉色(#EC4899)
- **代码**：
  ```vue
  <!-- 男性 -->
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
    <circle cx="10" cy="14" r="5"/>
    <path d="M19 5l-6 6M19 5v4M19 5h-4"/>
  </svg>
  
  <!-- 女性 -->
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
    <circle cx="12" cy="9" r="5"/>
    <path d="M12 14v7M9 18h6"/>
  </svg>
  ```

#### 日期选择器位置
- **问题**：弹窗位置太靠下，底部选项无法点击
- **解决**：使用 `align-items: flex-start` + `padding-top: 10vh`
- **代码**：
  ```css
  .modal-overlay.picker-modal-overlay {
    align-items: flex-start;
    padding-top: 10vh;
  }
  ```

#### 响应式断点
- **确定**：电脑端 ≥1024px，手机端 <1024px
- **电脑端样式**：
  ```css
  @media (min-width: 1024px) {
    .step-form-page {
      max-width: 480px;
      margin: 0 auto;
    }
  }
  ```

#### CORS配置
- **问题**：WiFi网络下无法访问，数据流量可以
- **解决**：允许所有域名访问
- **代码**：
  ```python
  allow_origins=["*"],
  allow_credentials=False,
  ```

#### 页面跳转滚动
- **问题**：跳转后保留上一页的滚动位置
- **解决**：监听路由变化，自动滚动到顶部
- **代码**：
  ```javascript
  watch(currentPage, () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
    document.documentElement.scrollTop = 0
    document.body.scrollTop = 0
  })
  ```

## 待解决问题

### AI报告生成时间过长
- **当前耗时**：15-60秒
- **主要原因**：
  1. DeepSeek API响应慢
  2. 提示词过长（3000-4000字符）
  3. max_tokens=4000设置过高
- **可能的优化方向**：
  1. 缩短提示词，保留核心数据
  2. 使用流式输出
  3. 缓存常见八字结果
  4. 考虑更换更快的模型

## 用户反复询问的问题

1. **平台适配**：需要明确iOS/Android/电脑/微信的区别
2. **页面范围**：需要确认是用户页面还是调试页面
3. **响应式同步**：修改一端需要同步检查另一端

## 性能优化经验

### PDF生成
- 手机端使用 scale: 1.5
- JPEG质量 0.88-0.92
- 目标文件大小 ≤ 10MB

### 图片加载
- 使用WebP格式
- 懒加载非首屏图片
- 设置合适的图片尺寸

## 兼容性备忘

- iOS必须使用 `env(safe-area-inset-*)`
- Android键盘弹起需要特殊处理
- 微信内置浏览器字体可能被覆盖
- 某些WiFi网络限制Render域名访问
