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
        <!-- 真太阳时提示 -->
        <p v-if="hasTrueSolarTime" class="true-solar-hint">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 6v6l4 2"/>
          </svg>
          已按真太阳时校正：{{ originalTimeText }} → {{ adjustedTimeText }}
        </p>
      </div>
      <div class="report-badge">
        <span class="badge-text">{{ aiReport ? 'AI报告已生成' : '基础报告' }}</span>
        <!-- 调试模式标识 -->
        <span v-if="isDebug" class="debug-badge">DEBUG</span>
      </div>
    </div>

    <!-- ==================== 调试模式：完整报告区域 ==================== -->
    <template v-if="isDebug">
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

      <!-- 调试面板 - 显示原始数据 -->
      <DebugRawData 
        :rawData="rawAnalysisData"
        :aiPrompt="aiPrompt"
        class="section-block"
      />
    </template>

    <!-- ==================== 用户模式：简化报告区域 ==================== -->
    <template v-else>
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
    </template>

    <!-- 用户反馈模块 -->
    <div class="feedback-section section-block">
      <div class="feedback-card">
        <div class="feedback-header">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
          </svg>
          <h3>您的反馈对我们很重要</h3>
        </div>
        
        <!-- 多维度评分区域 -->
        <div class="rating-dimensions">
          <div v-for="dim in ratingDimensions" :key="dim.key" class="rating-row">
            <span class="rating-label">{{ dim.label }}</span>
            <div class="star-rating small">
              <button
                v-for="star in 5"
                :key="star"
                class="star-btn small"
                :class="{ active: dimRatings[dim.key] >= star }"
                @click="dimRatings[dim.key] = star"
                @mouseenter="dimHover[dim.key] = star"
                @mouseleave="dimHover[dim.key] = 0"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" stroke="none">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
              </button>
            </div>
            <span class="rating-value">{{ dimRatings[dim.key] ? dimRatings[dim.key] + '分' : '-' }}</span>
          </div>
        </div>

        <!-- 反馈文字输入 -->
        <textarea
          v-model="feedbackText"
          class="feedback-textarea"
          placeholder="欢迎分享您的使用体验、建议或任何想法..."
          maxlength="500"
          rows="4"
        ></textarea>
        <p class="char-count">{{ feedbackText.length }}/500</p>

        <!-- 提交按钮 -->
        <button 
          class="feedback-submit-btn"
          :disabled="!hasAnyRating || feedbackSubmitting"
          @click="handleSubmitFeedback"
        >
          <svg v-if="!feedbackSubmitting" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
          <svg v-else class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
          </svg>
          {{ feedbackSubmitting ? '提交中...' : '提交反馈' }}
        </button>

        <!-- 提交成功提示 -->
        <div v-if="feedbackSubmitted" class="feedback-success">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          <span>感谢您的反馈！我们会持续改进。</span>
        </div>

        <p class="feedback-privacy">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          完全匿名，不收集任何个人隐私信息
        </p>
      </div>
    </div>

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
import { computed, ref, getCurrentInstance } from 'vue'
import BaziPillars from './BaziPillars.vue'
import SixLevelAnalysis from './SixLevelAnalysis.vue'
import EnergyCharts from './EnergyCharts.vue'
import AIReport from './AIReport.vue'
import DebugRawData from './DebugRawData.vue'
import { submitFeedback } from '../api/bazi'

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

// 检测调试模式
const { appContext } = getCurrentInstance()
const isDebug = computed(() => appContext.config.globalProperties.$isDebug || false)

// AI 分析状态
const aiLoading = computed(() => props.aiAnalyzing)

// 反馈相关状态（多维度评分）
const dimRatings = ref({
  overall: 0,
  design: 0,
  content: 0,
  helpful: 0
})
const dimHover = ref({
  overall: 0,
  design: 0,
  content: 0,
  helpful: 0
})
const feedbackText = ref('')
const feedbackSubmitting = ref(false)
const feedbackSubmitted = ref(false)

// 评分维度配置
const ratingDimensions = [
  { key: 'overall', label: '整体体验' },
  { key: 'design', label: '设计美观' },
  { key: 'content', label: '分析内容' },
  { key: 'helpful', label: '是否对你有帮助' }
]

// 是否至少有一个评分
const hasAnyRating = computed(() => {
  return Object.values(dimRatings.value).some(r => r > 0)
})

// 提交反馈（多维度评分）
const handleSubmitFeedback = async () => {
  if (!hasAnyRating.value) return
  
  feedbackSubmitting.value = true
  
  try {
    const result = await submitFeedback({
      rating_overall: dimRatings.value.overall || null,
      rating_design: dimRatings.value.design || null,
      rating_content: dimRatings.value.content || null,
      rating_helpful: dimRatings.value.helpful || null,
      feedback_text: feedbackText.value
    })
    
    if (result.success) {
      feedbackSubmitted.value = true
      // 3秒后重置表单
      setTimeout(() => {
        dimRatings.value = { overall: 0, design: 0, content: 0, helpful: 0 }
        feedbackText.value = ''
        feedbackSubmitted.value = false
      }, 3000)
    } else {
      alert('提交失败，请稍后重试')
    }
  } catch (error) {
    console.error('提交反馈失败:', error)
    alert('提交失败，请检查网络连接')
  } finally {
    feedbackSubmitting.value = false
  }
}

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
  const original = props.result?.user_info?.birth_time?.original
  const adjusted = props.result?.user_info?.birth_time?.adjusted
  const location = props.result?.user_info?.birth_time?.location
  
  if (!original || original.hour === null) return '时辰未知'
  
  // 如果有真太阳时调整且地点信息，显示调整后的时间
  if (adjusted && location?.city) {
    return `${adjusted.hour.toString().padStart(2, '0')}:${adjusted.minute.toString().padStart(2, '0')}`
  }
  
  return `${original.hour.toString().padStart(2, '0')}:${original.minute.toString().padStart(2, '0')}`
})

// 是否有真太阳时调整
const hasTrueSolarTime = computed(() => {
  const adjusted = props.result?.user_info?.birth_time?.adjusted
  const location = props.result?.user_info?.birth_time?.location
  return adjusted && location?.city && location?.longitude
})

// 原始时间显示
const originalTimeText = computed(() => {
  const original = props.result?.user_info?.birth_time?.original
  if (!original) return ''
  return `${original.hour?.toString().padStart(2, '0') || '--'}:${original.minute?.toString().padStart(2, '0') || '--'}`
})

// 调整后时间显示
const adjustedTimeText = computed(() => {
  const adjusted = props.result?.user_info?.birth_time?.adjusted
  if (!adjusted) return ''
  return `${adjusted.hour?.toString().padStart(2, '0') || '--'}:${adjusted.minute?.toString().padStart(2, '0') || '--'}`
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

// AI 分析提示词（用于调试）
const aiPrompt = computed(() => {
  return props.result?.ai_prompt || ''
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
  max-width: 720px;
  margin: 0 auto;
  padding: 24px;
  background: linear-gradient(180deg, #FDFCF8 0%, #F0F9FF 100%);
  min-height: 100vh;
}

/* 全局移动端字体优化 */
@media (max-width: 640px) {
  html {
    font-size: 16px;
    -webkit-text-size-adjust: 100%;
  }
  
  body {
    font-size: 16px;
    line-height: 1.6;
  }
}

/* 报告头部 */
.report-header {
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  border-radius: 20px;
  padding: 28px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  color: white;
  box-shadow: 0 8px 24px rgba(142, 197, 252, 0.3);
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

.true-solar-hint {
  margin: 8px 0 0;
  font-size: 12px;
  color: #A8E6CF;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.true-solar-hint svg {
  width: 14px;
  height: 14px;
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

.debug-badge {
  display: block;
  margin-top: 4px;
  padding: 2px 8px;
  background: #e53e3e;
  color: white;
  font-size: 10px;
  font-weight: 700;
  border-radius: 4px;
  text-align: center;
}

/* 区块间距 */
.section-block {
  margin-bottom: 20px;
}

/* AI 触发区域 */
.ai-trigger-section {
  margin-bottom: 24px;
}

.ai-trigger-card {
  background: linear-gradient(135deg, #F0F9FF 0%, #F0FFF4 100%);
  border: 2px dashed #8EC5FC;
  border-radius: 16px;
  padding: 32px;
  text-align: center;
}

.ai-trigger-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-trigger-icon svg {
  width: 32px;
  height: 32px;
  color: white;
}

.ai-trigger-title {
  font-size: 20px;
  font-weight: 700;
  color: #4A5568;
  margin: 0 0 8px;
}

.ai-trigger-desc {
  font-size: 14px;
  color: #718096;
  margin: 0 0 20px;
  line-height: 1.6;
}

.ai-trigger-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 16px rgba(142, 197, 252, 0.3);
}

.ai-trigger-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(142, 197, 252, 0.4);
}

.ai-trigger-btn svg {
  width: 20px;
  height: 20px;
}

/* AI 加载状态 */
.ai-loading-section {
  background: linear-gradient(135deg, #F0F9FF 0%, #F0FFF4 100%);
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  margin-bottom: 24px;
}

.ai-loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid #E2E8F0;
  border-top-color: #8EC5FC;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

.ai-loading-text {
  font-size: 16px;
  font-weight: 600;
  color: #4A5568;
  margin: 0 0 4px;
}

.ai-loading-subtext {
  font-size: 14px;
  color: #718096;
  margin: 0;
}

/* 反馈模块 */
.feedback-section {
  margin-bottom: 24px;
}

.feedback-card {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(142, 197, 252, 0.1);
  border: 1px solid rgba(142, 197, 252, 0.2);
}

.feedback-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.feedback-header svg {
  width: 24px;
  height: 24px;
  color: #8EC5FC;
}

.feedback-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #4A5568;
  margin: 0;
}

/* 多维度评分区域 */
.rating-dimensions {
  margin-bottom: 20px;
}

.rating-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #F0F0F0;
}

.rating-row:last-child {
  border-bottom: none;
}

.rating-label {
  font-size: 14px;
  color: #4A5568;
  font-weight: 500;
  min-width: 80px;
}

.rating-value {
  font-size: 13px;
  color: #8EC5FC;
  font-weight: 600;
  min-width: 30px;
  text-align: right;
}

.star-rating {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.star-rating.small {
  gap: 4px;
}

.star-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 4px;
  transition: transform 0.2s;
}

.star-btn.small {
  width: 28px;
  height: 28px;
  padding: 2px;
}

.star-btn:hover {
  transform: scale(1.1);
}

.star-btn svg {
  width: 100%;
  height: 100%;
  color: #E2E8F0;
  transition: color 0.2s;
}

.star-btn.active svg {
  color: #F6E05E;
}

/* 反馈类型选择 */
.feedback-types {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.type-btn {
  padding: 8px 16px;
  background: #F7FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  font-size: 13px;
  color: #718096;
  cursor: pointer;
  transition: all 0.2s;
}

.type-btn:hover {
  border-color: #8EC5FC;
  color: #8EC5FC;
}

.type-btn.active {
  background: rgba(142, 197, 252, 0.15);
  border-color: #8EC5FC;
  color: #4A5568;
  font-weight: 500;
}

/* 反馈文字输入 */
.feedback-textarea {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #E2E8F0;
  border-radius: 12px;
  font-size: 15px;
  color: #4A5568;
  resize: vertical;
  transition: all 0.2s;
  font-family: inherit;
}

.feedback-textarea:focus {
  outline: none;
  border-color: #8EC5FC;
  box-shadow: 0 0 0 4px rgba(142, 197, 252, 0.15);
}

.feedback-textarea::placeholder {
  color: #A0AEC0;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #A0AEC0;
  margin: 4px 0 16px;
}

/* 提交按钮 */
.feedback-submit-btn {
  width: 100%;
  padding: 14px 24px;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s;
  box-shadow: 0 4px 16px rgba(142, 197, 252, 0.3);
}

.feedback-submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(142, 197, 252, 0.4);
}

.feedback-submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.feedback-submit-btn svg {
  width: 18px;
  height: 18px;
}

/* 提交成功提示 */
.feedback-success {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  background: rgba(168, 230, 207, 0.2);
  border-radius: 12px;
  margin-top: 16px;
  color: #38A169;
  font-size: 14px;
  font-weight: 500;
}

.feedback-success svg {
  width: 20px;
  height: 20px;
}

/* 隐私说明 */
.feedback-privacy {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin: 16px 0 0;
  font-size: 12px;
  color: #A0AEC0;
}

.feedback-privacy svg {
  width: 14px;
  height: 14px;
}

/* 底部操作栏 */
.action-bar {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #E2E8F0;
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
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(142, 197, 252, 0.3);
}

.action-btn.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(142, 197, 252, 0.4);
}

.action-btn.primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.action-btn.secondary {
  background: #FFFFFF;
  color: #718096;
  border: 2px solid #E2E8F0;
}

.action-btn.secondary:hover {
  border-color: #8EC5FC;
  color: #8EC5FC;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 响应式 - 手机端优化 */
@media (max-width: 640px) {
  .result-container {
    padding: 12px;
  }
  
  .report-header {
    flex-direction: column;
    gap: 12px;
    padding: 16px;
    border-radius: 16px;
    margin-bottom: 16px;
  }
  
  .user-name {
    font-size: 18px;
    margin: 0 0 6px;
  }
  
  .user-meta {
    flex-wrap: wrap;
    gap: 4px 8px;
    font-size: 13px;
  }
  
  .meta-separator {
    display: none;
  }
  
  .true-solar-hint {
    font-size: 11px;
    margin-top: 6px;
    padding: 4px 8px;
    background: rgba(255,255,255,0.15);
    border-radius: 6px;
    display: inline-flex;
  }
  
  .report-badge {
    padding: 4px 12px;
    align-self: flex-start;
  }
  
  .badge-text {
    font-size: 12px;
  }
  
  .section-block {
    margin-bottom: 16px;
  }
  
  /* AI 触发区域 */
  .ai-trigger-section {
    margin-bottom: 16px;
  }
  
  .ai-trigger-card {
    padding: 20px 16px;
    border-radius: 12px;
  }
  
  .ai-trigger-icon {
    width: 52px;
    height: 52px;
    border-radius: 12px;
    font-size: 24px;
  }
  
  .ai-trigger-title {
    font-size: 16px;
    margin: 0 0 6px;
  }
  
  .ai-trigger-desc {
    font-size: 13px;
    margin: 0 0 16px;
    line-height: 1.6;
  }
  
  .ai-trigger-desc br {
    display: none;
  }
  
  .ai-trigger-btn {
    padding: 12px 20px;
    font-size: 15px;
    border-radius: 10px;
  }
  
  /* AI 加载状态 */
  .ai-loading-section {
    padding: 32px 20px;
    border-radius: 12px;
    margin-bottom: 16px;
  }
  
  .ai-loading-spinner {
    width: 40px;
    height: 40px;
  }
  
  .ai-loading-text {
    font-size: 15px;
  }
  
  .ai-loading-subtext {
    font-size: 13px;
  }
  
  /* 反馈模块 */
  .feedback-section {
    margin-bottom: 16px;
  }
  
  .feedback-card {
    padding: 16px;
    border-radius: 12px;
  }
  
  .feedback-header {
    margin-bottom: 16px;
  }
  
  .feedback-header h3 {
    font-size: 16px;
  }
  
  /* 评分区域 */
  .rating-dimensions {
    margin-bottom: 16px;
  }
  
  .rating-row {
    padding: 10px 0;
  }
  
  .rating-label {
    font-size: 14px;
    min-width: 70px;
  }
  
  .star-btn.small {
    width: 26px;
    height: 26px;
  }
  
  .rating-value {
    font-size: 12px;
    min-width: 24px;
  }
  
  /* 反馈输入 */
  .feedback-textarea {
    padding: 12px;
    font-size: 15px;
    border-radius: 10px;
    line-height: 1.6;
  }
  
  .char-count {
    font-size: 12px;
    margin: 4px 0 12px;
  }
  
  .feedback-submit-btn {
    padding: 12px 20px;
    font-size: 15px;
    border-radius: 10px;
  }
  
  .feedback-success {
    padding: 12px;
    font-size: 13px;
  }
  
  .feedback-privacy {
    font-size: 11px;
    margin-top: 12px;
  }
  
  /* 底部操作栏 */
  .action-bar {
    flex-direction: column;
    gap: 10px;
    margin-top: 16px;
    padding-top: 16px;
  }
  
  .action-btn {
    padding: 14px 20px;
    font-size: 15px;
  }
}
</style>