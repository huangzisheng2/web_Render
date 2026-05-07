<template>
  <div class="report-page">
    <!-- 顶部导航栏 -->
    <nav class="top-nav">
      <div class="nav-container">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="nav-tab"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>
    </nav>

    <!-- 内容区域 -->
    <main class="report-content">
      <!-- 首页（始终显示在顶部） -->
      <ReportHome
        :user-info="userInfo"
        :day-master="dayMaster"
        class="section-home"
      />

      <!-- 简易分析模块 -->
      <SimpleReport
        v-if="activeTab === 'simple' || activeTab === 'detail'"
        :simple-report="simpleReport"
        :loading="simpleLoading"
        class="section-simple"
      />

      <!-- 详细分析模块 -->
      <DetailReport
        v-if="activeTab === 'detail'"
        :detail-report="detailReport"
        :loading="detailLoading"
        :has-analyzed="hasDetailAnalyzed"
        @analyze="handleDetailAnalyze"
        class="section-detail"
      />
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ReportHome from './ReportHome.vue'
import SimpleReport from './SimpleReport.vue'
import DetailReport from './DetailReport.vue'

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

const emit = defineEmits(['analyze-ai', 'download'])

// 当前激活的标签
const activeTab = ref('simple')

// 导航标签配置
const tabs = [
  { key: 'simple', label: '天赋概览' },
  { key: 'detail', label: '深度探索' }
]

// 用户信息
const userInfo = computed(() => {
  return props.result?.user_info || {}
})

// 日主天干
const dayMaster = computed(() => {
  return props.result?.bazi?.day_master || ''
})

// 简易报告数据（从后端返回的AI报告中提取）
const simpleReport = computed(() => {
  const aiReport = props.result?.ai_report || ''
  
  // 如果有完整的AI报告，解析出简易版内容
  if (aiReport && typeof aiReport === 'string') {
    // 尝试按标题分割成不同板块
    return parseSimpleReport(aiReport)
  }
  
  return null
})

// 解析简易报告
function parseSimpleReport(report) {
  // 按新提示词的 ### 标题分割
  const sections = report.split(/###\s+/).filter(s => s.trim())
  
  let coreTalent = ''
  let talentScenario = ''
  let growthAdvice = ''
  
  for (const section of sections) {
    const lower = section.toLowerCase()
    const content = section.replace(/^.*?\n/, '').trim() // 去掉标题行
    
    if (lower.startsWith('核心天赋')) {
      coreTalent = section.trim() // 保留标题和内容
    } else if (lower.startsWith('天赋场景')) {
      talentScenario = section.trim()
    } else if (lower.startsWith('成长意见')) {
      growthAdvice = section.trim()
    }
  }
  
  if (coreTalent || talentScenario || growthAdvice) {
    return { coreTalent, talentScenario, growthAdvice }
  }
  
  // 如果无法按标题分割，将全文作为核心天赋
  return {
    coreTalent: report,
    talentScenario: '',
    growthAdvice: ''
  }
}

// 简易报告加载状态
const simpleLoading = computed(() => {
  return !props.result?.ai_report && !props.result?.error
})

// 详细报告数据
const detailReport = computed(() => {
  return props.result?.ai_report || ''
})

// 详细分析状态
const detailLoading = computed(() => false) // 由外部控制
const hasDetailAnalyzed = computed(() => !!props.result?.ai_report)

// 处理详细分析请求
const handleDetailAnalyze = () => {
  emit('analyze-ai')
}
</script>

<style scoped>
.report-page {
  min-height: 100vh;
  min-height: 100dvh;
  background: linear-gradient(180deg, #F0F9FF 0%, #FDFCF8 50%, #F0FFF4 100%);
}

/* 顶部导航栏 */
.top-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(142, 197, 252, 0.15);
  padding-top: env(safe-area-inset-top);
}

.nav-container {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  max-width: 600px;
  margin: 0 auto;
}

.nav-tab {
  flex: 1;
  max-width: 160px;
  padding: 10px 20px;
  background: transparent;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  color: #718096;
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
}

.nav-tab:hover {
  color: #4A5568;
  background: rgba(142, 197, 252, 0.08);
}

.nav-tab.active {
  color: #3B82F6;
  font-weight: 600;
  background: rgba(59, 130, 246, 0.08);
}

.nav-tab.active::after {
  content: '';
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 3px;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  border-radius: 2px;
}

.tab-label {
  position: relative;
  z-index: 1;
}

/* 内容区域 */
.report-content {
  padding-bottom: env(safe-area-inset-bottom);
}

.section-home {
  /* 首页样式由组件内部定义 */
}

.section-simple {
  animation: fadeInUp 0.35s ease;
}

.section-detail {
  animation: fadeInUp 0.35s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式 - 手机端 */
@media (max-width: 640px) {
  .nav-container {
    gap: 6px;
    padding: 10px 12px;
  }

  .nav-tab {
    padding: 9px 16px;
    font-size: 14px;
    border-radius: 8px;
  }
}

/* 响应式 - 电脑端 */
@media (min-width: 1024px) {
  .report-page {
    max-width: 600px;
    margin: 0 auto;
    box-shadow: 0 0 40px rgba(0, 0, 0, 0.06);
  }

  .top-nav {
    border-bottom-color: rgba(142, 197, 252, 0.2);
  }

  .nav-container {
    padding: 14px 32px;
    gap: 12px;
  }

  .nav-tab {
    padding: 11px 28px;
    font-size: 15px;
    border-radius: 12px;
  }
}
</style>
