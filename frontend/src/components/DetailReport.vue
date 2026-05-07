<template>
  <section class="detail-report">
    <!-- 已有详细报告 -->
    <template v-if="hasAnalyzed && detailReport">
      <div class="detail-content">
        <header class="detail-header">
          <div class="header-badge">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
            <span>AI 深度分析</span>
          </div>
        </header>

        <!-- AI 报告内容 -->
        <article class="ai-report-card">
          <div class="report-text" v-html="formattedReport"></div>
        </article>

        <!-- 操作按钮 -->
        <div class="detail-actions">
          <button class="action-btn regenerate" @click="$emit('analyze')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 4 23 10 17 10"/>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
            </svg>
            重新生成
          </button>
        </div>
      </div>
    </template>

    <!-- 未分析 - 显示触发卡片 -->
    <template v-else-if="!loading">
      <div class="trigger-card">
        <div class="trigger-icon-wrapper">
          <div class="trigger-icon-bg"></div>
          <div class="trigger-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
            </svg>
          </div>
        </div>

        <h3 class="trigger-title">想要更深入的 AI 天赋探索？</h3>
        <p class="trigger-desc">
          基于 DeepSeek 大模型，为你生成个性化的<br/>
          性格特质、天赋优势、成长路径深度报告
        </p>

        <button class="analyze-btn" @click="$emit('analyze')" :disabled="loading">
          <span v-if="!loading">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            开始深度分析
          </span>
          <span v-else class="btn-loading">
            <span class="loading-spinner"></span>
            分析中...
          </span>
        </button>

        <p class="trigger-hint">预计需要 30 秒 ~ 1 分钟</p>
      </div>
    </template>

    <!-- 加载中状态 -->
    <template v-if="loading && !hasAnalyzed">
      <div class="analyzing-card">
        <div class="analyzing-animation">
          <div class="pulse-ring ring-1"></div>
          <div class="pulse-ring ring-2"></div>
          <div class="pulse-ring ring-3"></div>
        </div>
        <p class="analyzing-title">AI 正在深度分析中...</p>
        <p class="analyzing-subtitle">基于你的出生信息，结合传统智慧与 AI 技术</p>
        <div class="progress-dots">
          <span v-for="i in 5" :key="i" :class="{ active: true }"></span>
        </div>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  detailReport: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  },
  hasAnalyzed: {
    type: Boolean,
    default: false
  }
})

defineEmits(['analyze'])

// 格式化报告文本（Markdown 转 HTML）
const formattedReport = computed(() => {
  const text = props.detailReport || ''
  
  return text
    // 标题处理
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // 加粗
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 换行
    .replace(/\n/g, '<br/>')
})
</script>

<style scoped>
.detail-report {
  padding: 0 16px;
}

/* 触发卡片 */
.trigger-card {
  background: linear-gradient(135deg, #F0F9FF 0%, #F0FFF4 100%);
  border: 2px dashed #8EC5FC;
  border-radius: 20px;
  padding: 36px 24px 32px;
  text-align: center;
}

.trigger-icon-wrapper {
  position: relative;
  width: 72px;
  height: 72px;
  margin: 0 auto 20px;
}

.trigger-icon-bg {
  position: absolute;
  inset: -4px;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  border-radius: 50%;
  opacity: 0.2;
  animation: pulse-bg 2s ease-in-out infinite;
}

.trigger-icon {
  position: relative;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.trigger-icon svg {
  width: 32px;
  height: 32px;
  color: white;
}

@keyframes pulse-bg {
  0%, 100% { transform: scale(1); opacity: 0.2; }
  50% { transform: scale(1.15); opacity: 0.3; }
}

.trigger-title {
  font-size: 19px;
  font-weight: 700;
  color: #1E293B;
  margin: 0 0 10px;
}

.trigger-desc {
  font-size: 14px;
  color: #64748B;
  line-height: 1.7;
  margin: 0 0 24px;
}

.trigger-desc br {
  display: none;
}

.analyze-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 32px;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(142, 197, 252, 0.3);
}

.analyze-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(142, 197, 252, 0.45);
}

.analyze-btn:disabled {
  opacity: 0.85;
  cursor: wait;
}

.analyze-btn svg {
  width: 20px;
  height: 20px;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2.5px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.trigger-hint {
  font-size: 12px;
  color: #94A3B8;
  margin: 16px 0 0;
}

/* 分析中动画 */
.analyzing-card {
  background: white;
  border-radius: 20px;
  padding: 40px 24px;
  text-align: center;
  box-shadow: 0 2px 16px rgba(142, 197, 252, 0.08);
}

.analyzing-animation {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
}

.pulse-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 3px solid transparent;
}

.ring-1 {
  border-top-color: #8EC5FC;
  animation: spin 1.5s linear infinite;
}

.ring-2 {
  inset: 10px;
  border-top-color: #A8E6CF;
  animation: spin 1.2s linear infinite reverse;
}

.ring-3 {
  inset: 20px;
  border-top-color: #DDBEA9;
  animation: spin 0.9s linear infinite;
}

.analyzing-title {
  font-size: 17px;
  font-weight: 600;
  color: #1E293B;
  margin: 0 0 8px;
}

.analyzing-subtitle {
  font-size: 14px;
  color: #64748B;
  margin: 0 0 24px;
}

.progress-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.progress-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #E2E8F0;
}

.progress-dots span.active {
  background: #8EC5FC;
  animation: dot-pulse 1s ease-in-out infinite;
}

.progress-dots span:nth-child(2).active { animation-delay: 0.15s; }
.progress-dots span:nth-child(3).active { animation-delay: 0.3s; }
.progress-dots span:nth-child(4).active { animation-delay: 0.45s; }
.progress-dots span:nth-child(5).active { animation-delay: 0.6s; }

@keyframes dot-pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.4); opacity: 0.6; }
}

/* 详细报告内容区 */
.detail-content {
  /* 内容样式 */
}

.detail-header {
  margin-bottom: 16px;
}

.header-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(142, 197, 252, 0.1);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: #3B82F6;
}

.header-badge svg {
  width: 16px;
  height: 16px;
}

.ai-report-card {
  background: white;
  border-radius: 18px;
  padding: 24px 20px;
  box-shadow: 0 2px 16px rgba(142, 197, 252, 0.08);
  border: 1px solid rgba(142, 197, 252, 0.12);
  margin-bottom: 16px;
}

.report-text {
  font-size: 15px;
  line-height: 1.85;
  color: #334155;
}

.report-text :deep(h1) {
  font-size: 20px;
  font-weight: 700;
  color: #1E293B;
  margin: 20px 0 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #8EC5FC;
}

.report-text :deep(h2) {
  font-size: 17px;
  font-weight: 600;
  color: #334155;
  margin: 18px 0 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid #E2E8F0;
}

.report-text :deep(h3) {
  font-size: 15px;
  font-weight: 600;
  color: #475569;
  margin: 14px 0 8px;
}

.report-text :deep(strong) {
  color: #3B82F6;
  font-weight: 600;
}

/* 操作按钮 */
.detail-actions {
  display: flex;
  justify-content: center;
  padding: 8px 0;
}

.action-btn.regenerate {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: white;
  color: #64748B;
  border: 2px solid #E2E8F0;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
}

.action-btn.regenerate:hover {
  border-color: #8EC5FC;
  color: #3B82F6;
  background: #F0F9FF;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

/* 响应式 - 手机端 */
@media (max-width: 480px) {
  .detail-report {
    padding: 0 12px;
  }

  .trigger-card {
    padding: 28px 18px 26px;
    border-radius: 16px;
  }

  .trigger-icon-wrapper {
    width: 64px;
    height: 64px;
  }

  .trigger-icon svg {
    width: 28px;
    height: 28px;
  }

  .trigger-title {
    font-size: 17px;
  }

  .analyze-btn {
    padding: 13px 28px;
    font-size: 15px;
  }

  .ai-report-card {
    padding: 20px 16px;
    border-radius: 14px;
  }

  .report-text {
    font-size: 14px;
  }
}

/* 响应式 - 电脑端 */
@media (min-width: 1024px) {
  .detail-report {
    padding: 0 32px;
  }

  .trigger-card {
    padding: 44px 32px 38px;
    border-radius: 22px;
  }

  .trigger-icon-wrapper {
    width: 80px;
    height: 80px;
  }

  .trigger-icon svg {
    width: 36px;
    height: 36px;
  }

  .trigger-title {
    font-size: 21px;
  }

  .trigger-desc br {
    display: inline;
  }

  .ai-report-card {
    padding: 28px 32px;
    border-radius: 20px;
  }

  .report-text {
    font-size: 15px;
  }
}
</style>
