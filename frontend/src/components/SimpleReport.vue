<template>
  <section class="simple-report">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="skeleton-cards">
        <div class="skeleton-card" v-for="i in 3" :key="i">
          <div class="skeleton-header"></div>
          <div class="skeleton-line long"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line short"></div>
        </div>
      </div>
    </div>

    <!-- 卡片内容 -->
    <template v-else-if="simpleReport">
      <!-- 卡片1：核心天赋 -->
      <article v-if="simpleReport.coreTalent" class="report-card card-talent">
        <header class="card-header">
          <div class="header-icon icon-talent">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
          </div>
          <h2 class="card-title">核心天赋</h2>
        </header>
        <div class="card-body">
          <div class="card-text" v-html="formatReportText(simpleReport.coreTalent)"></div>
        </div>
      </article>

      <!-- 卡片2：天赋场景 -->
      <article v-if="simpleReport.talentScenario" class="report-card card-scenario">
        <header class="card-header">
          <div class="header-icon icon-scenario">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
              <line x1="9" y1="9" x2="9.01" y2="9"/>
              <line x1="15" y1="9" x2="15.01" y2="9"/>
            </svg>
          </div>
          <h2 class="card-title">天赋场景</h2>
        </header>
        <div class="card-body">
          <div class="card-text" v-html="formatReportText(simpleReport.talentScenario)"></div>
        </div>
      </article>

      <!-- 卡片3：成长建议 -->
      <article v-if="simpleReport.growthAdvice" class="report-card card-growth">
        <header class="card-header">
          <div class="header-icon icon-growth">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 20V10"/>
              <path d="M18 20V4"/>
              <path d="M6 20v-4"/>
            </svg>
          </div>
          <h2 class="card-title">成长建议</h2>
        </header>
        <div class="card-body">
          <div class="card-text" v-html="formatReportText(simpleReport.growthAdvice)"></div>
        </div>
      </article>

      <!-- 如果只有全文，显示为单卡片 -->
      <article v-if="!simpleReport.talentScenario && !simpleReport.growthAdvice && simpleReport.coreTalent" class="report-card card-full">
        <div class="card-body">
          <div class="card-text" v-html="formatReportText(simpleReport.coreTalent)"></div>
        </div>
      </article>
    </template>

    <!-- 无数据状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
        </svg>
      </div>
      <p>正在生成你的专属天赋报告...</p>
    </div>
  </section>
</template>

<script setup>
defineProps({
  simpleReport: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// 格式化报告文本（简易Markdown转HTML）
function formatReportText(text) {
  if (!text) return ''
  
  return text
    // 去掉 "### 核心天赋" 等标题行（卡片已有标题）
    .replace(/^###\s+.*$/gm, '')
    // 加粗
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 引用块
    .replace(/^>\s+(.+)$/gm, '<blockquote>$1</blockquote>')
    // 列表项
    .replace(/^[-*]\s+(.+)$/gm, '<li>$1</li>')
    // 换行
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>')
    // 清理多余空标签
    .replace(/<p>\s*<\/p>/g, '')
}
</script>

<style scoped>
.simple-report {
  padding: 0 16px;
}

/* 卡片通用样式 */
.report-card {
  background: white;
  border-radius: 18px;
  padding: 22px 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 16px rgba(142, 197, 252, 0.08);
  border: 1px solid rgba(142, 197, 252, 0.12);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(142, 197, 252, 0.15);
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.header-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-icon svg {
  width: 20px;
  height: 20px;
  color: white;
}

.icon-talent {
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
}

.icon-scenario {
  background: linear-gradient(135deg, #FBBF24 0%, #F59E0B 100%);
}

.icon-growth {
  background: linear-gradient(135deg, #A78BFA 0%, #8B5CF6 100%);
}

.card-title {
  font-size: 17px;
  font-weight: 700;
  color: #1E293B;
  margin: 0;
}

/* 卡片内容 */
.card-body {
  /* 内容区 */
}

.card-text {
  font-size: 15px;
  line-height: 1.8;
  color: #475569;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.card-text :deep(strong) {
  color: #3B82F6;
  font-weight: 600;
}

.card-text :deep(blockquote) {
  margin: 12px 0;
  padding: 12px 16px;
  background: linear-gradient(135deg, #F0F9FF 0%, #F0FFF4 100%);
  border-left: 3px solid #8EC5FC;
  border-radius: 0 10px 10px 0;
  font-style: italic;
  color: #475569;
  line-height: 1.7;
}

.card-text :deep(li) {
  margin: 6px 0 6px 16px;
  padding-left: 4px;
  list-style-type: disc;
}

.card-text :deep(p) {
  margin: 8px 0;
}

/* 加载骨架屏 */
.loading-state {
  padding: 0 4px;
}

.skeleton-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeleton-card {
  background: white;
  border-radius: 18px;
  padding: 22px 20px;
  box-shadow: 0 2px 16px rgba(142, 197, 252, 0.08);
  border: 1px solid rgba(142, 197, 252, 0.12);
}

.skeleton-header {
  width: 120px;
  height: 20px;
  background: linear-gradient(90deg, #E2E8F0 25%, #F1F5F9 50%, #E2E8F0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
  margin-bottom: 16px;
}

.skeleton-line {
  height: 14px;
  background: linear-gradient(90deg, #F1F5F9 25%, #F8FAFC 50%, #F1F5F9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 6px;
  margin-bottom: 10px;
}

.skeleton-line.long { width: 90%; }
.skeleton-line.short { width: 60%; }

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 48px 20px;
  color: #94A3B8;
}

.empty-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 16px;
  opacity: 0.4;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-state p {
  font-size: 15px;
  margin: 0;
}

/* 响应式 - 手机端 */
@media (max-width: 480px) {
  .simple-report {
    padding: 0 12px;
  }

  .report-card {
    padding: 18px 16px;
    border-radius: 14px;
    margin-bottom: 12px;
  }

  .header-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
  }

  .header-icon svg {
    width: 18px;
    height: 18px;
  }

  .card-title {
    font-size: 15px;
  }

  .card-text {
    font-size: 14px;
  }
}

/* 响应式 - 电脑端 */
@media (min-width: 1024px) {
  .simple-report {
    padding: 0 32px;
  }

  .report-card {
    padding: 26px 28px;
    border-radius: 20px;
    margin-bottom: 20px;
  }

  .header-icon {
    width: 44px;
    height: 44px;
    border-radius: 14px;
  }

  .header-icon svg {
    width: 22px;
    height: 22px;
  }

  .card-title {
    font-size: 18px;
  }

  .card-text {
    font-size: 15px;
    line-height: 1.9;
  }
}
</style>
