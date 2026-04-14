<template>
  <div class="ai-report-container">
    <!-- 标题区 -->
    <div class="section-header">
      <div class="header-icon ai-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z"/>
          <path d="M12 6v6l4 2"/>
          <circle cx="12" cy="12" r="2"/>
        </svg>
      </div>
      <div class="header-content">
        <h3 class="header-title">AI 天赋分析报告</h3>
        <p class="header-subtitle">基于 DeepSeek 大模型深度分析</p>
      </div>
      <div class="ai-badge">AI</div>
    </div>

    <!-- 报告内容 -->
    <div class="report-content" v-if="report">
      <!-- 报告摘要卡片 -->
      <div class="summary-cards">
        <div class="summary-card character">
          <div class="card-icon">🎯</div>
          <div class="card-title">性格特质</div>
          <div class="card-desc">核心性格与行为模式</div>
        </div>
        <div class="summary-card talent">
          <div class="card-icon">💎</div>
          <div class="card-title">天赋优势</div>
          <div class="card-desc">与生俱来的潜能领域</div>
        </div>
        <div class="summary-card advice">
          <div class="card-icon">🌱</div>
          <div class="card-title">成长建议</div>
          <div class="card-desc">发展方向与提升路径</div>
        </div>
        <div class="summary-card warning">
          <div class="card-icon">⚠️</div>
          <div class="card-title">注意事项</div>
          <div class="card-desc">需要警惕的弱点</div>
        </div>
      </div>

      <!-- 格式化报告内容 -->
      <div class="formatted-report" v-html="formattedReport"></div>
    </div>

    <!-- 加载状态 -->
    <div v-else-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p class="loading-text">AI 正在分析您的命盘...</p>
      <p class="loading-subtext">这可能需要 10-30 秒</p>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M9 12h.01M15 12h.01M10 16c.5.3 1.2.5 2 .5s1.5-.2 2-.5"/>
          <rect x="3" y="3" width="18" height="18" rx="2"/>
        </svg>
      </div>
      <p class="empty-text">暂无 AI 分析报告</p>
      <button class="generate-btn" @click="$emit('generate')">
        生成 AI 报告
      </button>
    </div>

    <!-- 操作按钮 -->
    <div class="report-actions" v-if="report">
      <button class="action-btn primary" @click="handleDownload">
        <svg v-if="!isDownloading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        <svg v-else class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
        </svg>
        {{ isDownloading ? '生成中...' : '下载 PDF 报告' }}
      </button>
      <button class="action-btn secondary" @click="$emit('regenerate')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="23 4 23 10 17 10"/>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
        </svg>
        重新生成
      </button>
    </div>
    
    <!-- 移动端下载提示 -->
    <div v-if="showMobileTip" class="mobile-download-tip">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="16" x2="12" y2="12"/>
        <line x1="12" y1="8" x2="12.01" y2="8"/>
      </svg>
      <p>PDF 已生成！如未自动下载，请检查浏览器下载记录或文件管理器</p>
      <button @click="showMobileTip = false" class="tip-close">知道了</button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  report: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['generate', 'download', 'regenerate'])

// 下载状态
const isDownloading = ref(false)
const showMobileTip = ref(false)

// 检测是否为移动设备
const isMobileDevice = () => {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera
  return /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent.toLowerCase())
}

// 处理下载
const handleDownload = async () => {
  isDownloading.value = true
  
  try {
    await emit('download')
    
    // 移动端显示提示
    if (isMobileDevice()) {
      setTimeout(() => {
        showMobileTip.value = true
      }, 500)
    }
  } finally {
    isDownloading.value = false
  }
}

// 格式化报告内容
const formattedReport = computed(() => {
  if (!props.report) return ''
  
  let content = props.report
  
  // 处理 Markdown 格式
  // 标题
  content = content.replace(/### (.*)/g, '<h4 class="report-h4">$1</h4>')
  content = content.replace(/## (.*)/g, '<h3 class="report-h3">$1</h3>')
  content = content.replace(/# (.*)/g, '<h2 class="report-h2">$1</h2>')
  
  // 加粗
  content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  
  // 列表
  content = content.replace(/^\* (.*)/gm, '<li class="report-li">$1</li>')
  content = content.replace(/(<li.*<\/li>\n)+/g, '<ul class="report-ul">$&</ul>')
  
  // 段落
  content = content.replace(/\n\n/g, '</p><p class="report-p">')
  content = '<p class="report-p">' + content + '</p>'
  
  // 清理多余的空段落
  content = content.replace(/<p class="report-p"><\/p>/g, '')
  content = content.replace(/<p class="report-p">(<h[23])/g, '$1')
  content = content.replace(/(<\/h[23]>)<\/p>/g, '$1')
  
  return content
})
</script>

<style scoped>
.ai-report-container {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* 标题区 */
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.header-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.ai-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header-icon svg {
  width: 22px;
  height: 22px;
}

.header-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.header-subtitle {
  margin: 4px 0 0;
  font-size: 13px;
  color: #64748b;
}

.ai-badge {
  margin-left: auto;
  padding: 4px 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 12px;
  font-weight: 700;
  border-radius: 20px;
}

/* 摘要卡片 */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 16px 12px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f1f5f9;
  transition: all 0.3s;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.card-title {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 2px;
}

.card-desc {
  font-size: 11px;
  color: #94a3b8;
}

/* 格式化报告 */
.formatted-report {
  background: white;
  border-radius: 12px;
  padding: 20px;
  line-height: 1.8;
  color: #334155;
}

:deep(.report-h2) {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 24px 0 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e2e8f0;
}

:deep(.report-h3) {
  font-size: 16px;
  font-weight: 600;
  color: #475569;
  margin: 20px 0 12px;
}

:deep(.report-h4) {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  margin: 16px 0 8px;
}

:deep(.report-p) {
  margin: 0 0 12px;
  font-size: 14px;
}

:deep(.report-ul) {
  margin: 8px 0 16px;
  padding-left: 20px;
}

:deep(.report-li) {
  margin: 6px 0;
  font-size: 14px;
}

:deep(strong) {
  color: #1e293b;
  font-weight: 600;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid #e2e8f0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  margin: 16px 0 4px;
  font-size: 15px;
  color: #475569;
  font-weight: 500;
}

.loading-subtext {
  margin: 0;
  font-size: 13px;
  color: #94a3b8;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
}

.empty-icon {
  width: 64px;
  height: 64px;
  color: #cbd5e1;
  margin-bottom: 16px;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-text {
  margin: 0 0 20px;
  font-size: 15px;
  color: #64748b;
}

.generate-btn {
  padding: 12px 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 24px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

/* 操作按钮 */
.report-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 20px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.action-btn.secondary {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.action-btn.secondary:hover {
  background: #e2e8f0;
}

.action-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 移动端下载提示 */
.mobile-download-tip {
  margin-top: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
}

.mobile-download-tip svg {
  width: 32px;
  height: 32px;
  color: #0ea5e9;
}

.mobile-download-tip p {
  margin: 0;
  font-size: 14px;
  color: #0369a1;
  line-height: 1.5;
}

.tip-close {
  padding: 8px 20px;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.tip-close:hover {
  background: #0284c7;
}

/* 响应式 - 手机端优化 */
@media (max-width: 640px) {
  .ai-report-container {
    padding: 16px;
    border-radius: 12px;
  }
  
  .section-header {
    gap: 10px;
    margin-bottom: 16px;
    padding-bottom: 12px;
  }
  
  .header-icon {
    width: 36px;
    height: 36px;
    border-radius: 8px;
  }
  
  .header-icon svg {
    width: 20px;
    height: 20px;
  }
  
  .header-title {
    font-size: 17px;
  }
  
  .header-subtitle {
    font-size: 12px;
  }
  
  .ai-badge {
    padding: 3px 8px;
    font-size: 11px;
  }
  
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-bottom: 16px;
  }
  
  .summary-card {
    padding: 14px 10px;
    border-radius: 10px;
  }
  
  .card-icon {
    font-size: 24px;
    margin-bottom: 6px;
  }
  
  .card-title {
    font-size: 13px;
  }
  
  .card-desc {
    font-size: 11px;
  }
  
  /* 报告内容手机端优化 */
  .formatted-report {
    padding: 16px;
    border-radius: 10px;
    line-height: 1.75;
  }
  
  :deep(.report-h2) {
    font-size: 17px;
    margin: 20px 0 12px;
    padding-bottom: 6px;
  }
  
  :deep(.report-h3) {
    font-size: 15px;
    margin: 16px 0 10px;
  }
  
  :deep(.report-h4) {
    font-size: 14px;
    margin: 14px 0 8px;
  }
  
  :deep(.report-p) {
    font-size: 15px;
    margin: 0 0 14px;
    line-height: 1.8;
  }
  
  :deep(.report-ul) {
    margin: 10px 0 14px;
    padding-left: 18px;
  }
  
  :deep(.report-li) {
    font-size: 15px;
    margin: 8px 0;
    line-height: 1.7;
  }
  
  /* 操作按钮 */
  .report-actions {
    flex-direction: column;
    gap: 10px;
    margin-top: 16px;
  }
  
  .action-btn {
    padding: 12px 16px;
    font-size: 15px;
  }
  
  .action-btn svg {
    width: 16px;
    height: 16px;
  }
}

@media (max-width: 480px) {
  .ai-report-container {
    padding: 14px;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .summary-card {
    padding: 12px;
    display: flex;
    align-items: center;
    text-align: left;
    gap: 12px;
  }
  
  .card-icon {
    font-size: 22px;
    margin-bottom: 0;
    flex-shrink: 0;
  }
  
  .card-title {
    font-size: 14px;
    margin-bottom: 2px;
  }
  
  .card-desc {
    font-size: 12px;
  }
  
  .formatted-report {
    padding: 14px;
  }
  
  :deep(.report-h2) {
    font-size: 16px;
  }
  
  :deep(.report-h3) {
    font-size: 15px;
  }
  
  :deep(.report-p) {
    font-size: 15px;
  }
  
  :deep(.report-li) {
    font-size: 15px;
  }
}
</style>