<template>
  <div class="result-container">
    <!-- 报告头部 -->
    <div class="report-header">
      <div class="user-info">
        <h1 class="user-name">{{ userName }} 的命理报告</h1>
        <p class="user-meta">
          <span class="meta-item">{{ genderText }}</span>
          <span class="meta-separator">·</span>
          <span class="meta-item">{{ birthDateText }}</span>
          <span class="meta-separator">·</span>
          <span class="meta-item">{{ birthTimeText }}</span>
        </p>
      </div>
      <div class="report-badge">
        <span class="badge-text">{{ aiReport ? 'AI报告已生成' : '基础报告' }}</span>
      </div>
    </div>

    <!-- 四柱排盘 -->
    <BaziPillars 
      :bazi="baziData"
      :shishen="shishenData"
      :dayMaster="dayMaster"
      class="section-block"
    />

    <!-- 六级论级分析 -->
    <SixLevelAnalysis 
      :analysisData="rawAnalysisData"
      class="section-block"
    />

    <!-- 能量分析 -->
    <EnergyCharts 
      :wuxingEnergy="wuxingEnergy"
      :shishenEnergy="shishenEnergy"
      :dayunEnergy="dayunEnergy"
      class="section-block"
    />

    <!-- AI 分析按钮（未分析时显示） -->
    <div v-if="!aiReport && !aiLoading" class="ai-trigger-section">
      <div class="ai-trigger-card">
        <div class="ai-trigger-icon">🤖</div>
        <h3 class="ai-trigger-title">想要更深入的 AI 天赋分析？</h3>
        <p class="ai-trigger-desc">
          基于 DeepSeek 大模型，为您生成个性化的<br>
          性格特质、天赋优势、成长建议报告
        </p>
        <button class="ai-trigger-btn" @click="handleAIAnalyze">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z"/>
            <path d="M12 6v6l4 2"/>
          </svg>
          一键分析天赋
        </button>
      </div>
    </div>

    <!-- AI 分析加载状态 -->
    <div v-if="aiLoading" class="ai-loading-section">
      <div class="ai-loading-spinner"></div>
      <p class="ai-loading-text">AI 正在分析您的命盘...</p>
      <p class="ai-loading-subtext">这需要 10-30 秒，请稍候</p>
    </div>

    <!-- AI 报告（分析完成后显示） -->
    <AIReport 
      v-if="aiReport"
      :report="aiReport"
      :loading="false"
      @download="$emit('download')"
      @regenerate="handleRegenerateAI"
      class="section-block"
    />

    <!-- 底部操作 -->
    <div class="action-bar">
      <button class="action-btn secondary" @click="$emit('reset')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 12"/>
          <path d="M3 3v9h9"/>
        </svg>
        重新分析
      </button>
      <button class="action-btn primary" @click="$emit('download')" :disabled="downloading">
        <svg v-if="!downloading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        <svg v-else class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
        </svg>
        {{ downloading ? '生成中...' : '下载报告' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import BaziPillars from './BaziPillars.vue'
import SixLevelAnalysis from './SixLevelAnalysis.vue'
import EnergyCharts from './EnergyCharts.vue'
import AIReport from './AIReport.vue'

const props = defineProps({
  result: {
    type: Object,
    required: true
  },
  downloading: {
    type: Boolean,
    default: false
  },
  aiAnalyzing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['reset', 'download', 'analyze-ai'])

// AI 分析状态
const aiLoading = computed(() => props.aiAnalyzing)

// 用户信息
const userName = computed(() => {
  return props.result?.user_info?.name || '匿名'
})

const genderText = computed(() => {
  return props.result?.user_info?.gender === '男' ? '男' : '女'
})

const birthDateText = computed(() => {
  const time = props.result?.user_info?.birth_time?.original
  if (!time) return '未知日期'
  return `${time.year}年${time.month}月${time.day}日`
})

const birthTimeText = computed(() => {
  const time = props.result?.user_info?.birth_time?.original
  if (!time || time.hour === null) return '时辰未知'
  return `${time.hour.toString().padStart(2, '0')}:${time.minute.toString().padStart(2, '0')}`
})

// 八字数据 - 直接使用后端返回的bazi数据
const baziData = computed(() => {
  const bazi = props.result?.bazi || {}
  return {
    year_gan: bazi.year_gan || '',
    year_zhi: bazi.year_zhi || '',
    month_gan: bazi.month_gan || '',
    month_zhi: bazi.month_zhi || '',
    day_gan: bazi.day_gan || '',
    day_zhi: bazi.day_zhi || '',
    time_gan: bazi.time_gan || '',
    time_zhi: bazi.time_zhi || ''
  }
})

// 十神数据 - 从raw_data中获取
const shishenData = computed(() => {
  const raw = props.result?.raw_data || {}
  return {
    year_gan: raw.第一论级_月令与格局?.十神?.年干 || '',
    month_gan: raw.第一论级_月令与格局?.十神?.月干 || '',
    day_gan: raw.第一论级_月令与格局?.十神?.日干 || '',
    time_gan: raw.第一论级_月令与格局?.十神?.时干 || '',
    year_zhi: raw.第一论级_月令与格局?.十神?.年支 || '',
    month_zhi: raw.第一论级_月令与格局?.十神?.月支 || '',
    day_zhi: raw.第一论级_月令与格局?.十神?.日支 || '',
    time_zhi: raw.第一论级_月令与格局?.十神?.时支 || ''
  }
})

// 日主
const dayMaster = computed(() => {
  return props.result?.bazi?.day_master || props.result?.raw_data?.第一论级_月令与格局?.日主 || ''
})

// 原始分析数据
const rawAnalysisData = computed(() => {
  const data = props.result?.raw_data || {}
  // 调试：打印数据结构
  console.log('=== ResultDisplay raw_data ===', data)
  console.log('第一论级:', data['第一论级_月令与格局'])
  console.log('第二论级:', data['第二论级_地支关系'])
  console.log('第三论级:', data['第三论级_天干关系'])
  console.log('第四论级:', data['第四论级_天干与地支的关系'])
  console.log('第五论级定喜忌:', data['第五论级_定喜忌'])
  console.log('第五论级辅助:', data['第五论级_辅助信息'])
  console.log('第六论级:', data['第六论级_大运流年'])
  console.log('起运计算:', data['起运计算过程'])
  console.log('大运表:', data['大运表'])
  return data
})

// 五行能量
const wuxingEnergy = computed(() => {
  const raw = props.result?.raw_data || {}
  return raw.格局综合判定?.五行能量 || props.result?.analysis?.wuxing_energy || {}
})

// 十神能量
const shishenEnergy = computed(() => {
  const raw = props.result?.raw_data || {}
  return raw.格局综合判定?.十神能量分析 || props.result?.analysis?.shishen_energy || {}
})

// 大运能量
const dayunEnergy = computed(() => {
  const raw = props.result?.raw_data || {}
  const dayun = raw.第六论级_大运流年
  return dayun ? {
    ganzhi: dayun.当前大运?.干支,
    trend: dayun.当前大运?.趋势 || 'stable'
  } : null
})

// AI 报告
const aiReport = computed(() => {
  return props.result?.ai_report || ''
})

// 处理 AI 分析
const handleAIAnalyze = async () => {
  aiLoading.value = true
  emit('analyze-ai')
}

// 重新生成 AI 报告
const handleRegenerateAI = () => {
  handleAIAnalyze()
}
</script>

<style scoped>
.result-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

/* 报告头部 */
.report-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 28px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  color: white;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
}

.user-name {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 700;
}

.user-meta {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  opacity: 0.9;
}

.meta-separator {
  opacity: 0.5;
}

.report-badge {
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

.badge-text {
  font-size: 13px;
  font-weight: 600;
}

/* 区块间距 */
.section-block {
  margin-bottom: 20px;
}

/* AI 触发区域 */
.ai-trigger-section {
  margin-bottom: 20px;
}

.ai-trigger-card {
  background: linear-gradient(135deg, #f0f4ff 0%, #e8edff 100%);
  border: 2px dashed #667eea;
  border-radius: 16px;
  padding: 32px;
  text-align: center;
}

.ai-trigger-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.ai-trigger-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px;
}

.ai-trigger-desc {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 20px;
  line-height: 1.6;
}

.ai-trigger-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.ai-trigger-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.ai-trigger-btn svg {
  width: 20px;
  height: 20px;
}

/* AI 加载状态 */
.ai-loading-section {
  background: linear-gradient(135deg, #f0f4ff 0%, #e8edff 100%);
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  margin-bottom: 20px;
}

.ai-loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid #e0e7ff;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

.ai-loading-text {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px;
}

.ai-loading-subtext {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

/* 底部操作栏 */
.action-bar {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px 24px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.action-btn svg {
  width: 20px;
  height: 20px;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.action-btn.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.action-btn.primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.action-btn.secondary {
  background: #f1f5f9;
  color: #475569;
}

.action-btn.secondary:hover {
  background: #e2e8f0;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 响应式 */
@media (max-width: 640px) {
  .result-container {
    padding: 16px;
  }
  
  .report-header {
    flex-direction: column;
    gap: 16px;
    padding: 20px;
  }
  
  .user-name {
    font-size: 20px;
  }
  
  .user-meta {
    flex-wrap: wrap;
  }
  
  .action-bar {
    flex-direction: column;
  }
  
  .ai-trigger-card {
    padding: 24px;
  }
  
  .ai-trigger-title {
    font-size: 18px;
  }
}
</style>