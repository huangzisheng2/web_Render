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

        <!-- 天赋档案卡片（新增） -->
        <div class="section-profile-card" v-if="talentTags.length > 0">
          <TalentProfileCard
            :name="userInfo.name || '探索者'"
            :day-master="dayMaster"
            :gender="userInfo.gender || 'male'"
            :talent-tags="talentTags"
            :talent-summary="profileTalentSummary"
            :keywords="profileKeywords"
            :day-column-summary="profileDayColumn"
            :trait-description="traitDescription"
          />
        </div>

        <!-- 简易分析卡片 -->
        <SimpleReport
          :simple-report="simpleReport"
          :loading="simpleLoading"
          class="section-simple"
        />

        <!-- 分享按钮 -->
        <div class="share-section">
          <button class="share-btn" :class="{ generating: shareGenerating }" @click="handleShare" :disabled="shareGenerating">
            <svg v-if="!shareGenerating" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="18" cy="5" r="3"/>
              <circle cx="6" cy="12" r="3"/>
              <circle cx="18" cy="19" r="3"/>
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>
              <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
            </svg>
            <span v-else class="share-spinner"></span>
            {{ shareGenerating ? '生成中...' : '一键分享' }}
          </button>
        </div>
      </template>

      <!-- 深度探索 Tab -->
      <template v-if="activeTab === 'detail'">
        <div class="deep-explore">
          <!-- 未开始分析：显示按钮 -->
          <template v-if="!deepExploreReport && !deepExploreLoading">
            <div class="deep-explore-intro">
              <div class="deco-icon">
                <svg viewBox="0 0 80 80" fill="none" width="80" height="80">
                  <circle cx="40" cy="40" r="36" stroke="#8EC5FC" stroke-width="2" fill="rgba(142,197,252,0.08)"/>
                  <path d="M40 20v12M40 48v12M28 40h12M52 40h12" stroke="#8EC5FC" stroke-width="2.5" stroke-linecap="round"/>
                  <circle cx="40" cy="40" r="6" fill="#8EC5FC"/>
                </svg>
              </div>
              <h2 class="deep-explore-title">深度天赋探索</h2>
              <p class="deep-explore-desc">AI 将根据你的出生信息，从核心天赋图谱、落地指南、场景演绎等维度进行全方位的深度分析。整个过程约需 30~60 秒。</p>
              <button class="deep-explore-btn" @click="handleDeepExplore">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
                一键天赋分析
              </button>
            </div>
          </template>

          <!-- 加载中 -->
          <div v-if="deepExploreLoading" class="deep-explore-loading">
            <div class="loading-pulse">
              <div class="pulse-ring"></div>
              <div class="pulse-ring delay"></div>
            </div>
            <p class="loading-text">AI 正在为你深度解析天赋...</p>
            <p class="loading-sub">分析内容越详细，等待时间越长，请耐心等候 ~</p>
          </div>

          <!-- 分析结果 -->
          <div v-if="deepExploreReport" class="deep-explore-result">
            <div class="result-header">
              <h2>深度天赋分析报告</h2>
              <div class="result-meta">
                <span>{{ userInfo?.name || '探索者' }}</span>
                <span class="dot">·</span>
                <span>{{ new Date().toLocaleDateString('zh-CN') }}</span>
              </div>
            </div>
            <!-- 天赋档案卡片（深度探索） -->
            <div class="section-profile-card" v-if="deepExploreReport">
              <TalentProfileCard
                :name="userInfo.name || '探索者'"
                :day-master="dayMaster"
                :gender="userInfo.gender || 'male'"
                :talent-tags="deepProfileTags"
                :talent-summary="deepProfileSummary"
                :keywords="deepProfileKeywords"
                :day-column-summary="deepProfileDayColumn"
                :trait-description="traitDescription"
              />
            </div>

            <!-- 模块卡片 -->
            <div class="result-cards">
              <div
                v-for="(section, idx) in deepReportSections"
                :key="idx"
                class="deep-card"
                :class="section.type"
              >
                <div class="card-header">
                  <span class="card-icon">{{ section.icon }}</span>
                  <h3 class="card-title">{{ section.title }}</h3>
                </div>
                <div class="card-body markdown-body" v-html="section.html"></div>
              </div>
            </div>
            <div class="result-actions">
              <button class="regenerate-btn" @click="resetDeepExplore">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <polyline points="23 4 23 10 17 10"/>
                  <path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/>
                </svg>
                重新分析
              </button>
            </div>
          </div>

          <!-- 错误提示 -->
          <div v-if="deepExploreError" class="deep-explore-error">
            <p>{{ deepExploreError }}</p>
            <button class="retry-btn" @click="resetDeepExplore">重新尝试</button>
          </div>
        </div>
      </template>
    </main>

    <!-- 导出 PDF 按钮（统一放在底部） -->
    <div class="export-section">
      <button class="export-btn" :disabled="downloading" @click="handleExportPdf">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        {{ downloading ? '生成中...' : '导出PDF' }}
      </button>
    </div>

    <!-- 分享海报 -->
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
import SharePoster from './SharePoster.vue'
import TalentProfileCard from './TalentProfileCard.vue'
import { getDayMasterTrait } from '../data/dayMasterData'
import { analyzeAI } from '../api/bazi'

const props = defineProps({
  result: { type: Object, required: true },
  downloading: { type: Boolean, default: false },
  aiAnalyzing: { type: Boolean, default: false }
})

const emit = defineEmits(['export-pdf', 'reset'])

// Tabs
const activeTab = ref('simple')
const tabs = [
  { key: 'simple', label: '天赋概览' },
  { key: 'detail', label: '深度探索' }
]

// 用户信息
const userInfo = computed(() => props.result?.user_info || {})
const dayMaster = computed(() => props.result?.bazi?.day_master || '')

const traitInfo = computed(() => {
  const gender = userInfo.value?.gender || 'male'
  return getDayMasterTrait(dayMaster.value || '甲', gender)
})

// 简易报告
const simpleReport = computed(() => {
  const aiReport = props.result?.ai_report || ''
  if (aiReport && typeof aiReport === 'string') {
    return parseSimpleReport(aiReport)
  }
  return null
})

function parseSimpleReport(report) {
  const sections = report.split(/###\s+/).filter(s => s.trim())
  let coreTalent = '', talentScenario = '', growthAdvice = '', keywords = '', dayColumn = ''
  for (const section of sections) {
    const lower = section.toLowerCase()
    if (lower.startsWith('核心天赋')) coreTalent = section.trim()
    else if (lower.startsWith('天赋场景')) talentScenario = section.trim()
    else if (lower.startsWith('成长意见')) growthAdvice = section.trim()
    else if (lower.startsWith('天赋关键词')) keywords = section.trim()
    else if (lower.startsWith('日柱特质')) dayColumn = section.trim()
  }
  return { coreTalent, talentScenario, growthAdvice, keywords, dayColumn }
}

const simpleLoading = computed(() => {
  return !props.result?.ai_report && !props.result?.error
})

// 分享图天赋标签
const talentTags = computed(() => {
  const aiReport = props.result?.ai_report || ''
  if (!aiReport) return []
  const matches = aiReport.match(/\*\*(.+?)\*\*/g)
  return matches ? matches.slice(0, 5).map(m => m.replace(/\*\*/g, '')) : []
})

const traitDescription = computed(() => traitInfo.value.description || '')

// ===== 天赋档案卡片数据（简易版） =====
const profileKeywords = computed(() => {
  const kw = simpleReport.value?.keywords || ''
  // 提取 "天赋关键词：xxx、xxx、xxx" 中的关键词
  const content = kw.replace(/^天赋关键词[：:]\s*/i, '')
  return content.split(/[、,，]/).map(s => s.trim()).filter(Boolean).slice(0, 3)
})

const profileDayColumn = computed(() => {
  // 优先用AI返回的日柱特质，为空时 TalentProfileCard 会自动使用前端原生数据
  const dc = simpleReport.value?.dayColumn || ''
  return dc.replace(/^日柱特质[：:]\s*/i, '').trim()
})

const profileTalentSummary = computed(() => {
  const ct = simpleReport.value?.coreTalent || ''
  // 去掉"核心天赋"标题后的前60个字作为摘要
  const text = ct.replace(/^核心天赋[\s\S]*?\*\*(.+?)\*\*/g, '$1').trim()
  return text.slice(0, 80) || ''
})

// ========== 分享海报 ==========
const sharePosterRef = ref(null)
const shareGenerating = ref(false)

const handleShare = async () => {
  if (shareGenerating.value || !sharePosterRef.value) return
  shareGenerating.value = true
  try {
    const dataUrl = await sharePosterRef.value.generateImage()
    if (dataUrl) {
      const link = document.createElement('a')
      link.download = `天赋档案_${userInfo.value?.name || '我'}.png`
      link.href = dataUrl
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  } catch (e) {
    console.error('生成分享图失败:', e)
  } finally {
    shareGenerating.value = false
  }
}

// ========== 导出 PDF ==========
const handleExportPdf = () => {
  if (props.downloading) return
  if (activeTab.value === 'simple') {
    const content = props.result?.ai_report
    if (!content) return
    emit('export-pdf', { type: 'simple', content, userName: userInfo.value?.name || '探索者' })
  } else {
    const content = deepExploreReport.value
    if (!content) return
    emit('export-pdf', { type: 'deep', content, userName: userInfo.value?.name || '探索者' })
  }
}

// ========== 深度探索 ==========
const deepExploreReport = ref('')
const deepExploreLoading = ref(false)
const deepExploreError = ref('')

async function handleDeepExplore() {
  if (!props.result?.report_id) return
  deepExploreLoading.value = true
  deepExploreError.value = ''
  deepExploreReport.value = ''

  try {
    const response = await analyzeAI({
      report_id: props.result.report_id,
      basic_result: props.result
    }, 'deep_explore')

    if (response.success && response.ai_report) {
      deepExploreReport.value = response.ai_report
    } else {
      deepExploreError.value = response.error || '分析失败，请稍后重试'
    }
  } catch (e) {
    console.error('深度探索失败:', e)
    deepExploreError.value = '网络错误，请检查网络后重试'
  } finally {
    deepExploreLoading.value = false
  }
}

function resetDeepExplore() {
  deepExploreReport.value = ''
  deepExploreLoading.value = false
  deepExploreError.value = ''
}

// ===== 深度探索报告解析 =====
// 模块配置
const MODULE_CONFIG = [
  { key: '模块一', title: '核心天赋图谱', icon: '🌟', type: 'talent' },
  { key: '模块二', title: '专属天赋落地指南', icon: '📍', type: 'guide' },
  { key: '模块三', title: '天赋使用说明书', icon: '🎭', type: 'scene' },
  { key: '模块四', title: '与天赋共舞的成长提醒', icon: '⚡', type: 'growth' }
]

// 解析报告为模块
const deepReportSections = computed(() => {
  const text = deepExploreReport.value
  if (!text) return []

  const modules = []

  // 按模块标题分割
  const modulePattern = /####\s*\*\*模块[一二三四]：(.+?)\*\*/
  const parts = text.split(modulePattern)
  
  // parts: [beforeM1, title1, content1_beforeM2, title2, content2_beforeM3, ...]
  // 提取模块一之前的文字（可能是「结语」或其他前导内容）
  if (parts.length >= 1 && parts[0].trim()) {
    const intro = parts[0].trim()
    // 结语可能在最后，暂不处理
  }

  for (let i = 1; i < parts.length - 1; i += 2) {
    const rawTitle = parts[i] || ''
    const content = parts[i + 1] || ''
    
    // 匹配模块序号
    let matchedConfig = null
    for (const cfg of MODULE_CONFIG) {
      if (rawTitle.includes(cfg.key)) {
        matchedConfig = cfg
        break
      }
    }
    if (!matchedConfig) continue

    modules.push({
      ...matchedConfig,
      rawTitle,
      html: renderModuleContent(content)
    })
  }

  // 提取结语（最后一个 `## **结语**` 或 `## 结语` 之后的内容）
  const closingMatch = text.match(/##\s*\*?\*?结语\*?\*?[\s\S]*$/m)
  if (closingMatch) {
    const closingText = closingMatch[0].replace(/^##\s*\*?\*?结语\*?\*?/, '').trim()
    if (closingText) {
      modules.push({
        type: 'closing',
        title: '结语',
        icon: '💫',
        html: renderModuleContent(closingText)
      })
    }
  }

  return modules
})

// ===== 深度探索天赋档案数据 =====
const deepProfileTags = computed(() => {
  const text = deepExploreReport.value || ''
  const matches = text.match(/\*\*(.+?)\*\*/g)
  return matches ? matches.slice(0, 5).map(m => m.replace(/\*\*/g, '')) : talentTags.value
})

const deepProfileKeywords = computed(() => {
  // 提取模块一中【两大心智超能力】的标签
  const text = deepExploreReport.value || ''
  const labels = text.match(/【(.+?)】/g)
  return labels ? labels.slice(0, 3).map(m => m.replace(/[【】]/g, '')) : profileKeywords.value
})

const deepProfileSummary = computed(() => {
  // 取模块一第一个有效段落
  const mod1 = deepReportSections.value.find(s => s.type === 'talent')
  if (mod1?.html) {
    const plain = mod1.html.replace(/<[^>]+>/g, '').trim()
    return plain.slice(0, 100)
  }
  return ''
})

const deepProfileDayColumn = computed(() => {
  // 从模块四中找能量密码相关描述
  const mod4 = deepReportSections.value.find(s => s.type === 'growth')
  if (mod4?.html) {
    const plain = mod4.html.replace(/<[^>]+>/g, '').trim()
    return plain.slice(0, 120)
  }
  return traitDescription.value
})

// 渲染模块内容（Markdown → HTML）
function renderModuleContent(text) {
  if (!text) return ''
  let html = text.trim()
    // 子标题: **【标题】**
    .replace(/\*\*【(.+?)】\*\*/g, '<h4 class="md-sub">【$1】</h4>')
    // 数字子标题: 1. **标题**
    .replace(/^\d+\.\s+\*\*(.+?)\*\*/gm, '<h4 class="md-sub">$1</h4>')
    // 一般加粗
    .replace(/\*\*(.+?)\*\*/g, '<strong class="md-strong">$1</strong>')
    // 引用 >
    .replace(/>\s?(.+)/g, '<blockquote>$1</blockquote>')
    // 无序列表
    .replace(/^-\s+(.+)/gm, '<li>$1</li>')
    // 包裹连续 <li> 为 <ul>
    .replace(/(<li>.*<\/li>\n?)+/g, (match) => `<ul>${match}</ul>`)
    .replace(/<\/ul>\n?<ul>/g, '')
    // 段落
    .replace(/\n\n/g, '</p><p>')
    // 换行
    .replace(/\n/g, '<br>')
  
  return `<p>${html}</p>`
}
</script>

<style scoped>
.report-page {
  min-height: 100vh;
  min-height: 100dvh;
  background: linear-gradient(180deg, #F0F9FF 0%, #FDFCF8 50%, #F0FFF4 100%);
}

/* 导航栏 */
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

.report-content { padding-bottom: env(safe-area-inset-bottom); }
.section-simple { animation: fadeInUp 0.35s ease; }

/* 天赋档案卡片容器 */
.section-profile-card {
  padding: 0 16px;
  margin-bottom: 16px;
  animation: fadeInUp 0.4s ease;
}

@media (min-width: 1024px) {
  .section-profile-card { padding: 0 24px; }
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
  box-shadow: 0 4px 16px rgba(142, 197, 252, 0.3);
  transition: all 0.3s ease;
}

.share-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(142, 197, 252, 0.45); }
.share-btn.generating { opacity: 0.7; cursor: not-allowed; }
.share-btn:disabled { pointer-events: none; }

.share-spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2.5px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.share-btn svg { width: 20px; height: 20px; }

/* 导出 PDF 按钮 */
.export-section {
  text-align: center;
  padding: 8px 16px 32px;
}

.export-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 13px 28px;
  background: white;
  color: #4A5568;
  border: 1.5px solid #E2E8F0;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.export-btn:hover {
  border-color: #8EC5FC;
  color: #3B82F6;
  box-shadow: 0 2px 8px rgba(142, 197, 252, 0.15);
}

.export-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

/* ===== 深度探索 ===== */
.deep-explore {
  padding: 32px 20px;
  max-width: 600px;
  margin: 0 auto;
}

/* 引导页 */
.deep-explore-intro {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 48px 20px;
}

.deco-icon { margin-bottom: 20px; opacity: 0.8; }

.deep-explore-title {
  font-size: 22px;
  font-weight: 700;
  color: #1E293B;
  margin: 0 0 12px;
}

.deep-explore-desc {
  font-size: 15px;
  color: #64748B;
  line-height: 1.7;
  max-width: 360px;
  margin: 0 0 28px;
}

.deep-explore-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 36px;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(142, 197, 252, 0.35);
  transition: all 0.3s ease;
}

.deep-explore-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(142, 197, 252, 0.45);
}

/* 加载动画 */
.deep-explore-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 20px;
}

.loading-pulse {
  position: relative;
  width: 80px;
  height: 80px;
  margin-bottom: 24px;
}

.pulse-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 3px solid #8EC5FC;
  animation: pulse 1.5s ease-out infinite;
}

.pulse-ring.delay {
  animation-delay: 0.5s;
}

@keyframes pulse {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

.loading-text {
  font-size: 16px;
  font-weight: 600;
  color: #334155;
  margin: 0 0 8px;
}

.loading-sub {
  font-size: 13px;
  color: #94A3B8;
  margin: 0;
}

/* 分析结果 */
.deep-explore-result {
  animation: fadeInUp 0.4s ease;
}

.result-header {
  text-align: center;
  padding: 24px 0 20px;
  border-bottom: 1px solid rgba(142, 197, 252, 0.15);
  margin-bottom: 20px;
}

.result-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: #1E293B;
  margin: 0 0 8px;
}

.result-meta {
  font-size: 13px;
  color: #94A3B8;
}

.result-meta .dot { margin: 0 6px; }

/* 渲染内容 - 卡片布局 */
.result-cards {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 0 16px;
}

.deep-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(142, 197, 252, 0.08);
  border: 1px solid rgba(142, 197, 252, 0.12);
}

.deep-card.talent { border-top: 3px solid #8EC5FC; }
.deep-card.guide { border-top: 3px solid #A8E6CF; }
.deep-card.scene { border-top: 3px solid #FBBF24; }
.deep-card.growth { border-top: 3px solid #F472B6; }
.deep-card.closing { border-top: 3px solid #C084FC; }

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 20px 14px;
  border-bottom: 1px solid rgba(142, 197, 252, 0.08);
}

.card-icon {
  font-size: 26px;
  line-height: 1;
}

.card-title {
  font-size: 17px;
  font-weight: 700;
  color: #1E293B;
  margin: 0;
}

.card-body {
  padding: 16px 20px 20px;
  line-height: 1.85;
  color: #334155;
  font-size: 14px;
}

/* Markdown 渲染样式 */
.card-body .md-sub {
  font-size: 15px;
  font-weight: 600;
  color: #3B82F6;
  margin: 16px 0 8px;
}

.card-body .md-strong {
  color: #2563EB;
  font-weight: 600;
}

.card-body p {
  margin: 0 0 10px;
}

.card-body blockquote {
  background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
  border-left: 3px solid #8EC5FC;
  padding: 10px 14px;
  margin: 10px 0;
  border-radius: 0 8px 8px 0;
  font-size: 13px;
  color: #475569;
  line-height: 1.7;
}

.card-body ul {
  padding-left: 18px;
  margin: 8px 0;
}

.card-body li {
  margin-bottom: 5px;
  list-style: disc;
  color: #475569;
}

.result-actions {
  text-align: center;
  padding: 28px 16px 32px;
}

.regenerate-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  background: white;
  color: #4A5568;
  border: 1.5px solid #E2E8F0;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.regenerate-btn:hover {
  border-color: #8EC5FC;
  color: #3B82F6;
}

/* 错误状态 */
.deep-explore-error {
  text-align: center;
  padding: 60px 20px;
  color: #EF4444;
}

.deep-explore-error p {
  font-size: 15px;
  margin: 0 0 20px;
}

.retry-btn {
  padding: 12px 32px;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}

/* 响应式 */
@media (max-width: 640px) {
  .nav-container { gap: 6px; padding: 10px 12px; }
  .nav-tab { padding: 9px 16px; font-size: 14px; border-radius: 8px; }
  .share-btn { width: 100%; padding: 14px 24px; font-size: 15px; }
  .deep-explore { padding: 24px 12px; }
  .deep-explore-title { font-size: 20px; }
  .result-cards { padding: 0 8px; }
  .card-body { font-size: 13px; padding: 14px 16px 18px; }
  .card-header { padding: 14px 16px 12px; }
  .card-icon { font-size: 22px; }
  .card-title { font-size: 15px; }
}

@media (min-width: 1024px) {
  .report-page { max-width: 600px; margin: 0 auto; box-shadow: 0 0 40px rgba(0, 0, 0, 0.06); }
  .top-nav { border-bottom-color: rgba(142, 197, 252, 0.2); }
  .nav-container { padding: 14px 32px; gap: 12px; }
  .nav-tab { padding: 11px 28px; font-size: 15px; border-radius: 12px; }
}
</style>
