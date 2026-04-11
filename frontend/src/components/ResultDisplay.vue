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
        <span class="badge-text">已生成</span>
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

    <!-- AI 报告 -->
    <AIReport 
      :report="aiReport"
      :loading="aiLoading"
      @download="$emit('download')"
      @regenerate="regenerateAIReport"
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
  }
})

const emit = defineEmits(['reset', 'download', 'regenerate'])

const aiLoading = ref(false)

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

// 八字数据
const baziData = computed(() => {
  const bazi = props.result?.bazi || {}
  const display = props.result?.bazi_display || {}
  return {
    year_gan: display.year?.[0] || '',
    year_zhi: display.year?.[1] || '',
    month_gan: display.month?.[0] || '',
    month_zhi: display.month?.[1] || '',
    day_gan: display.day?.[0] || '',
    day_zhi: display.day?.[1] || '',
    time_gan: display.time?.[0] || '',
    time_zhi: display.time?.[1] || ''
  }
})

// 十神数据
const shishenData = computed(() => {
  return props.result?.analysis?.shishen || {}
})

// 日主
const dayMaster = computed(() => {
  return props.result?.bazi?.day_master || ''
})

// 原始分析数据
const rawAnalysisData = computed(() => {
  return props.result?.raw_data || {}
})

// 五行能量
const wuxingEnergy = computed(() => {
  return props.result?.analysis?.wuxing_energy || {}
})

// 十神能量
const shishenEnergy = computed(() => {
  return props.result?.analysis?.shishen_energy || {}
})

// 大运能量
const dayunEnergy = computed(() => {
  const dayun = rawAnalysisData.value?.第六论级_大运流年
  return dayun ? {
    ganzhi: dayun.当前大运?.ganzhi,
    trend: dayun.当前大运?.trend || 'stable'
  } : null
})

// AI 报告
const aiReport = computed(() => {
  return props.result?.ai_report || ''
})

// 重新生成 AI 报告
const regenerateAIReport = async () => {
  aiLoading.value = true
  emit('regenerate')
  // 模拟加载，实际应在父组件处理
  setTimeout(() => {
    aiLoading.value = false
  }, 1000)
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
}
</style>