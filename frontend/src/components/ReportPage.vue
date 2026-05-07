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
      <!-- 天赋概览 Tab -->
      <template v-if="activeTab === 'simple'">
        <!-- 首页（昵称+Q版形象+配文） -->
        <ReportHome
          :user-info="userInfo"
          :day-master="dayMaster"
          class="section-home"
        />

        <!-- 简易分析卡片 -->
        <SimpleReport
          :simple-report="simpleReport"
          :loading="simpleLoading"
          class="section-simple"
        />

        <!-- 分享按钮 -->
        <div class="share-section">
          <button class="share-btn" @click="handleShare">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="18" cy="5" r="3"/>
              <circle cx="6" cy="12" r="3"/>
              <circle cx="18" cy="19" r="3"/>
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>
              <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
            </svg>
            一键分享
          </button>
        </div>
      </template>

      <!-- 深度探索 Tab：显示原 ResultDisplay 完整内容 -->
      <template v-if="activeTab === 'detail'">
        <ResultDisplay
          :result="result"
          :ai-analyzing="aiAnalyzing"
          :downloading="downloading"
          @reset="$emit('reset')"
          @download="$emit('download')"
          @analyze-ai="$emit('analyze-ai')"
        />
      </template>
    </main>

    <!-- 分享海报（隐藏，用于生成图片） -->
    <SharePoster
      ref="sharePosterRef"
      :user-info="userInfo"
      :day-master="dayMaster"
      :trait-info="traitInfo"
      :talent-tags="talentTags"
      :trait-description="traitDescription"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ReportHome from './ReportHome.vue'
import SimpleReport from './SimpleReport.vue'
import ResultDisplay from './ResultDisplay.vue'
import SharePoster from './SharePoster.vue'
import { getDayMasterTrait } from '../data/dayMasterData'

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

const emit = defineEmits(['analyze-ai', 'download', 'reset'])

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

// 日主特质信息
const traitInfo = computed(() => {
  const gender = userInfo.value?.gender || 'male'
  return getDayMasterTrait(dayMaster.value || '甲', gender)
})

// 简易报告数据
const simpleReport = computed(() => {
  const aiReport = props.result?.ai_report || ''
  if (aiReport && typeof aiReport === 'string') {
    return parseSimpleReport(aiReport)
  }
  return null
})

// 解析简易报告
function parseSimpleReport(report) {
  const sections = report.split(/###\s+/).filter(s => s.trim())
  let coreTalent = ''
  let talentScenario = ''
  let growthAdvice = ''
  
  for (const section of sections) {
    const lower = section.toLowerCase()
    if (lower.startsWith('核心天赋')) {
      coreTalent = section.trim()
    } else if (lower.startsWith('天赋场景')) {
      talentScenario = section.trim()
    } else if (lower.startsWith('成长意见')) {
      growthAdvice = section.trim()
    }
  }
  
  if (coreTalent || talentScenario || growthAdvice) {
    return { coreTalent, talentScenario, growthAdvice }
  }
  
  return { coreTalent: report, talentScenario: '', growthAdvice: '' }
}

// 简易报告加载状态
const simpleLoading = computed(() => {
  return !props.result?.ai_report && !props.result?.error
})

// 从AI报告中提取天赋标签（用于分享图）
const talentTags = computed(() => {
  const aiReport = props.result?.ai_report || ''
  if (!aiReport) return []
  
  // 匹配加粗标签，如 **深度破局者**
  const matches = aiReport.match(/\*\*(.+?)\*\*/g)
  if (matches) {
    return matches.slice(0, 5).map(m => m.replace(/\*\*/g, ''))
  }
  return []
})

// 特质概括文字（用于分享图底部）
const traitDescription = computed(() => {
  return traitInfo.value.description || ''
})

// 分享海报组件引用
const sharePosterRef = ref(null)

// 处理分享
const handleShare = async () => {
  if (sharePosterRef.value) {
    try {
      const dataUrl = await sharePosterRef.value.generateImage()
      if (dataUrl) {
        // 创建下载链接
        const link = document.createElement('a')
        link.download = `天赋档案_${userInfo.value?.name || '我'}.png`
        link.href = dataUrl
        link.click()
      }
    } catch (e) {
      console.error('生成分享图失败:', e)
    }
  }
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

.section-simple {
  animation: fadeInUp 0.35s ease;
}

/* 分享按钮 */
.share-section {
  padding: 24px 16px 32px;
  text-align: center;
}

.share-btn {
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

.share-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(142, 197, 252, 0.45);
}

.share-btn svg {
  width: 20px;
  height: 20px;
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

  .share-btn {
    width: 100%;
    padding: 14px 24px;
    font-size: 15px;
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
