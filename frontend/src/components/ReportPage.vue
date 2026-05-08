<template>
  <div class="report-page">
    <!-- 顶部导航栏 -->
    <nav class="top-nav">
      <div class="nav-container">
        <button v-for="tab in tabs" :key="tab.key"
          class="nav-tab" :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key">
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>
    </nav>

    <main class="report-content">
      <!-- ========== 天赋概览 Tab ========== -->
      <template v-if="activeTab === 'simple'">
        <!-- 天赋综合画像卡片 -->
        <div class="section-profile-card" v-if="talentTags.length">
          <TalentProfileCard
            :name="userInfo.name || '探索者'"
            :day-master="dayMaster"
            :day-pillar="dayPillar"
            :gender="userInfo.gender || 'male'"
            :talent-tags="talentTags"
            :talent-summary="profileTalentSummary"
            :keywords="profileKeywords"
            :trait-description="traitDescription"
            :historical-figures="historicalFigures"
          />
        </div>

        <!-- 性格分析卡片 -->
        <div class="section-cards">
          <article v-if="profilePersonality" class="info-card card-personality">
            <header class="card-header">
              <span class="card-icon personality-icon">🧠</span>
              <h3 class="card-title">性格综合分析</h3>
            </header>
            <div class="card-body" v-html="profilePersonality"></div>
          </article>

          <!-- 核心天赋卡片 -->
          <article v-if="profileCoreTalent" class="info-card card-core-talent">
            <header class="card-header">
              <span class="card-icon talent-icon">🌟</span>
              <h3 class="card-title">核心天赋</h3>
            </header>
            <div class="card-body" v-html="profileCoreTalent"></div>
          </article>

          <!-- 天赋场景卡片 -->
          <article v-if="profileScenario" class="info-card card-scenario">
            <header class="card-header">
              <span class="card-icon scenario-icon">🎭</span>
              <h3 class="card-title">天赋场景</h3>
            </header>
            <div class="card-body" v-html="profileScenario"></div>
          </article>

          <!-- 成长意见卡片 -->
          <article v-if="profileGrowth" class="info-card card-growth">
            <header class="card-header">
              <span class="card-icon growth-icon">📈</span>
              <h3 class="card-title">成长意见</h3>
            </header>
            <div class="card-body" v-html="profileGrowth"></div>
          </article>

          <!-- 历史人物画像卡片 -->
          <article v-if="profileFigures" class="info-card card-figures">
            <header class="card-header">
              <span class="card-icon figures-icon">📜</span>
              <h3 class="card-title">历史人物画像</h3>
            </header>
            <div class="card-body" v-html="profileFigures"></div>
          </article>
        </div>
      </template>

      <!-- ========== 深度探索 Tab ========== -->
      <template v-if="activeTab === 'detail'">
        <!-- 深度探索内容保持不变 -->
        <div class="deep-explore">
          <template v-if="!deepExploreReport && !deepExploreLoading && !deepExploreError">
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
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                一键天赋分析
              </button>
            </div>
          </template>

          <div v-if="deepExploreLoading" class="deep-explore-loading">
            <div class="loading-pulse"><div class="pulse-ring"></div><div class="pulse-ring delay"></div></div>
            <p class="loading-text">AI 正在为你深度解析天赋...</p>
            <p class="loading-sub">分析内容越详细，等待时间越长，请耐心等候 ~</p>
          </div>

          <div v-if="deepExploreReport" class="deep-explore-result">
            <!-- 深度探索专属头部 -->
            <div class="deep-header">
              <span class="deep-header-icon">🔮</span>
              <h2 class="deep-header-title">{{ displayName }}的深度天赋探索</h2>
              <p class="deep-header-sub">{{ dayPillar }} · {{ traitInfo.element }}属性</p>
            </div>

            <!-- 全部文字统一放到同一卡片 -->
            <div class="deep-single-card">
              <div class="deep-single-body" v-html="deepFullHtml"></div>
            </div>

            <div class="result-actions">
              <button class="regenerate-btn" @click="resetDeepExplore">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>
                重新分析
              </button>
            </div>
          </div>

          <div v-if="deepExploreError" class="deep-explore-error">
            <p>{{ deepExploreError }}</p>
            <button class="retry-btn" @click="resetDeepExplore">重新尝试</button>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import TalentProfileCard from './TalentProfileCard.vue'
import { getDayMasterTrait } from '../data/dayMasterData'
import { analyzeBazi } from '../api/bazi'

const props = defineProps({
  result: { type: Object, default: null },
  downloading: { type: Boolean, default: false },
  aiAnalyzing: { type: Boolean, default: false }
})

const emit = defineEmits(['reset'])

// Tabs
const savedTab = typeof sessionStorage !== 'undefined' ? sessionStorage.getItem('bazi_activeTab') : null
const activeTab = ref(savedTab || 'simple')
const tabs = [
  { key: 'simple', label: '天赋概览' },
  { key: 'detail', label: '深度探索' }
]
watch(activeTab, (val) => {
  try { sessionStorage.setItem('bazi_activeTab', val) } catch {}
})

// 基础数据
const userInfo = computed(() => props.result?.user_info || {})
const dayMaster = computed(() => props.result?.bazi?.day_master || '')
const dayPillar = computed(() => props.result?.bazi?.day_pillar || '')
const displayName = computed(() => userInfo.value?.name || '探索者')

const traitInfo = computed(() => {
  return getDayMasterTrait(dayMaster.value || '甲', userInfo.value?.gender || 'male')
})
const traitDescription = computed(() => traitInfo.value.description || '')

// ===== 简易报告解析 =====
const simpleReport = computed(() => {
  const aiReport = props.result?.ai_report || ''
  if (aiReport && typeof aiReport === 'string') {
    return parseSimpleReport(aiReport)
  }
  return null
})

function parseSimpleReport(report) {
  const sections = report.split(/###\s+/).filter(s => s.trim())
  let coreTalent = '', personality = '', talentScenario = '', growthAdvice = '', keywords = '', figures = ''
  for (const section of sections) {
    const lower = section.toLowerCase()
    if (lower.startsWith('核心天赋')) coreTalent = section.trim()
    else if (lower.startsWith('性格综合分析')) personality = section.trim()
    else if (lower.startsWith('天赋场景')) talentScenario = section.trim()
    else if (lower.startsWith('成长意见')) growthAdvice = section.trim()
    else if (lower.startsWith('天赋关键词')) keywords = section.trim()
    else if (lower.startsWith('历史人物画像')) figures = section.trim()
  }
  if (!coreTalent && !talentScenario && !growthAdvice && !keywords && !personality && !figures) {
    coreTalent = report.trim()
  }
  return { coreTalent, personality, talentScenario, growthAdvice, keywords, figures }
}

// 天赋标签
const talentTags = computed(() => {
  const aiReport = props.result?.ai_report || ''
  if (!aiReport) return []
  const matches = aiReport.match(/\*\*(.+?)\*\*/g)
  return matches ? matches.slice(0, 5).map(m => m.replace(/\*\*/g, '')) : []
})

// 天赋关键词解析
const profileKeywords = computed(() => {
  const kw = simpleReport.value?.keywords || ''
  // 去掉section标题行，仅保留关键词内容
  const content = kw.replace(/^天赋关键词[：:\s]*/i, '').replace(/\n/g, ' ').trim()
  // 按分隔符拆分，清理 * 号和空格
  return content.split(/[、,，\s]+/).map(s => s.replace(/\*+/g, '').trim()).filter(Boolean).slice(0, 5)
})

// 天赋摘要
const profileTalentSummary = computed(() => {
  const ct = simpleReport.value?.coreTalent || ''
  return ct.replace(/^核心天赋[\s\S]*?\*\*(.+?)\*\*/g, '$1').trim().slice(0, 80) || ''
})



// 各卡片内容（Markdown→HTML）
function mdToHtml(text) {
  if (!text) return ''
  return text
    .replace(/^###\s+.*$/gm, '')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^>\s+(.+)$/gm, '<blockquote>$1</blockquote>')
    .replace(/^[-*]\s+(.+)$/gm, '<li>$1</li>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>')
    .replace(/<p>\s*<\/p>/g, '')
}

const profilePersonality = computed(() => {
  const text = simpleReport.value?.personality || ''
  const content = text.replace(/^性格综合分析[\s\S]*?(?:\n|$)/, '').trim()
  return content ? `<p>${mdToHtml(content)}</p>` : ''
})

const profileCoreTalent = computed(() => {
  const text = simpleReport.value?.coreTalent || ''
  const content = text.replace(/^核心天赋[\s\S]*?(?:\n|$)/, '').trim()
  return content ? `<p>${mdToHtml(content)}</p>` : ''
})

const profileScenario = computed(() => {
  const text = simpleReport.value?.talentScenario || ''
  const content = text.replace(/^天赋场景[\s\S]*?(?:\n|$)/, '').trim()
  return content ? `<p>${mdToHtml(content)}</p>` : ''
})

const profileGrowth = computed(() => {
  const text = simpleReport.value?.growthAdvice || ''
  const content = text.replace(/^成长意见[\s\S]*?(?:\n|$)/, '').trim()
  return content ? `<p>${mdToHtml(content)}</p>` : ''
})

const profileFigures = computed(() => {
  const text = simpleReport.value?.figures || ''
  if (!text) return ''
  const content = text.replace(/^历史人物画像[\s\S]*?(?:\n|$)/, '').trim()
  return content ? `<p>${mdToHtml(content)}</p>` : ''
})

// 历史人物结构化数据
const historicalFigures = computed(() => {
  const text = simpleReport.value?.figures || ''
  if (!text) return []
  // 尝试解析历史人物
  const lines = text.split('\n').filter(l => l.trim())
  const figures = []
  for (const line of lines) {
    // 匹配如 "王羲之，东晋书法家" 或 "- 王羲之" 等模式
    const match = line.match(/(.+?)[，,]\s*(.+?)(?=[。，]|$)/)
    if (match) {
      figures.push({
        name: match[1].replace(/^[-*]\s*/, ''),
        title: match[2].trim(),
        quote: line.slice(line.indexOf('"') !== -1 ? line.indexOf('"') : 0).replace(/^[-*\s]+/, '').slice(0, 40)
      })
    }
  }
  return figures.slice(0, 2)
})

// ===== 深度探索 =====
const deepExploreReport = ref('')
const deepExploreLoading = ref(false)
const deepExploreError = ref('')

async function handleDeepExplore() {
  if (!props.result?.report_id) return
  deepExploreLoading.value = true
  deepExploreError.value = ''
  deepExploreReport.value = ''
  try {
    // 使用 /api/analyze 接口，传入 deep_explore 模式
    const userInfo = props.result.user_info || {}
    const birthTime = userInfo.birth_time?.original || {}
    const birthLocation = userInfo.birth_time?.location || {}
    const birthData = {
      name: userInfo.name || '探索者',
      gender: userInfo.gender === '男' ? 'male' : 'female',
      year: birthTime.year || 2000,
      month: birthTime.month || 1,
      day: birthTime.day || 1,
      hour: birthTime.hour,
      minute: birthTime.minute || 0,
      province: birthLocation.province || '北京',
      city: birthLocation.city || '北京',
      mode: 'deep_explore'
    }
    const response = await analyzeBazi(birthData)
    if (response.success && response.data?.ai_report) {
      deepExploreReport.value = response.data.ai_report
    } else if (response.success && response.data) {
      deepExploreError.value = '深度分析未返回报告，请重试'
    } else {
      deepExploreError.value = response.error || '分析失败'
    }
  } catch (e) {
    console.error('深度探索失败:', e)
    deepExploreError.value = '网络错误，请检查网络连接后重试'
  } finally {
    deepExploreLoading.value = false
  }
}
function resetDeepExplore() {
  deepExploreReport.value = ''
  deepExploreLoading.value = false
  deepExploreError.value = ''
}

const MODULE_CONFIG = [
  { key: '模块一', title: '核心天赋图谱', icon: '🌟', type: 'talent' },
  { key: '模块二', title: '专属天赋落地指南', icon: '📍', type: 'guide' },
  { key: '模块三', title: '天赋使用说明书', icon: '🎭', type: 'scene' },
  { key: '模块四', title: '与天赋共舞的成长提醒', icon: '⚡', type: 'growth' }
]

// 深度探索全文HTML（不再分模块，直接渲染整篇报告）
const deepFullHtml = computed(() => {
  return renderModuleContent(deepExploreReport.value)
})


function renderModuleContent(text) {
  if (!text) return ''
  let html = text.trim()
    .replace(/\*\*【(.+?)】\*\*/g, '<h4 class="md-sub">【$1】</h4>')
    .replace(/^\d+\.\s+\*\*(.+?)\*\*/gm, '<h4 class="md-sub">$1</h4>')
    .replace(/\*\*(.+?)\*\*/g, '<strong class="md-strong">$1</strong>')
    .replace(/>\s?(.+)/g, '<blockquote>$1</blockquote>')
    .replace(/^-\s+(.+)/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, (match) => `<ul>${match}</ul>`)
    .replace(/<\/ul>\n?<ul>/g, '')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
  return `<p>${html}</p>`
}
</script>

<style scoped>
.report-page {
  min-height: 100vh; min-height: 100dvh;
  background: linear-gradient(180deg, #F0F9FF 0%, #FDFCF8 50%, #F0FFF4 100%);
}

/* 导航栏 */
.top-nav {
  position: sticky; top: 0; z-index: 100;
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(142,197,252,0.15);
  padding-top: env(safe-area-inset-top);
}
.nav-container { display: flex; justify-content: center; gap: 8px; padding: 12px 16px; max-width: 600px; margin: 0 auto; }
.nav-tab {
  flex: 1; max-width: 160px; padding: 10px 20px;
  background: transparent; border: none; border-radius: 10px;
  font-size: 15px; font-weight: 500; color: #718096;
  cursor: pointer; transition: all .25s ease;
}
.nav-tab:hover { color: #4A5568; background: rgba(142,197,252,0.08); }
.nav-tab.active { color: #3B82F6; font-weight: 600; background: rgba(59,130,246,0.08); }
.nav-tab.active::after {
  content: ''; position: absolute; bottom: 4px; left: 50%;
  transform: translateX(-50%); width: 24px; height: 3px;
  background: linear-gradient(135deg,#8EC5FC,#A8E6CF); border-radius: 2px;
}

.report-content { padding-bottom: env(safe-area-inset-bottom); }

/* 天赋档案卡片容器 */
.section-profile-card { padding: 14px 14px 0; animation: fadeInUp 0.3s ease; }

/* 信息卡片列表 */
.section-cards {
  display: flex; flex-direction: column; gap: 12px;
  padding: 12px 14px 24px;
  animation: fadeInUp 0.4s ease;
}

.info-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(142,197,252,0.06);
  border: 1px solid rgba(142,197,252,0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px 10px;
  border-bottom: 1px solid rgba(142,197,252,0.06);
}

.card-icon {
  font-size: 20px;
  line-height: 1;
}

.card-title {
  font-size: 15px;
  font-weight: 700;
  color: #1E293B;
  margin: 0;
}

.card-body {
  padding: 12px 16px 16px;
  line-height: 1.8;
  color: #475569;
  font-size: 14px;
}

.card-body :deep(strong) {
  color: #3B82F6;
  font-weight: 600;
}

.card-body :deep(blockquote) {
  margin: 8px 0;
  padding: 8px 14px;
  background: linear-gradient(135deg, #F0F9FF 0%, #F0FFF4 100%);
  border-left: 3px solid #8EC5FC;
  border-radius: 0 8px 8px 0;
  font-size: 13px;
  color: #475569;
  line-height: 1.7;
  font-style: italic;
}

.card-body :deep(li) {
  margin: 4px 0 4px 14px;
  padding-left: 4px;
  list-style-type: disc;
}

.card-body :deep(p) {
  margin: 6px 0;
}

/* 卡片顶部颜色标识 */
.card-personality { border-top: 3px solid #8EC5FC; }
.card-core-talent { border-top: 3px solid #A8E6CF; }
.card-scenario { border-top: 3px solid #FBBF24; }
.card-growth { border-top: 3px solid #A78BFA; }
.card-figures { border-top: 3px solid #F472B6; }

/* ===== 深度探索 ===== */
.deep-explore { padding: 32px 14px; max-width: 600px; margin: 0 auto; }
.deep-explore-intro { display: flex; flex-direction: column; align-items: center; text-align: center; padding: 48px 16px; }
.deco-icon { margin-bottom: 16px; opacity: .8; }
.deep-explore-title { font-size: 22px; font-weight: 700; color: #1E293B; margin: 0 0 10px; }
.deep-explore-desc { font-size: 15px; color: #64748B; line-height: 1.7; max-width: 360px; margin: 0 0 24px; }
.deep-explore-btn {
  display: inline-flex; align-items: center; gap: 10px; padding: 16px 36px;
  background: linear-gradient(135deg,#8EC5FC,#A8E6CF); color: #fff;
  border: none; border-radius: 14px; font-size: 17px; font-weight: 600;
  cursor: pointer; box-shadow: 0 6px 20px rgba(142,197,252,0.35);
  transition: all .3s ease;
}
.deep-explore-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(142,197,252,0.45); }

.deep-explore-loading { display: flex; flex-direction: column; align-items: center; padding: 80px 20px; }
.loading-pulse { position: relative; width: 80px; height: 80px; margin-bottom: 24px; }
.pulse-ring { position: absolute; inset: 0; border-radius: 50%; border: 3px solid #8EC5FC; animation: pulse 1.5s ease-out infinite; }
.pulse-ring.delay { animation-delay: .5s; }
@keyframes pulse { 0% { transform: scale(.5); opacity: 1; } 100% { transform: scale(1.5); opacity: 0; } }
.loading-text { font-size: 16px; font-weight: 600; color: #334155; margin: 0 0 8px; }
.loading-sub { font-size: 13px; color: #94A3B8; margin: 0; }

.deep-explore-result { animation: fadeInUp .4s ease; }

/* 深度探索头部 */
.deep-header {
  text-align: center;
  padding: 24px 16px 16px;
}
.deep-header-icon {
  font-size: 36px;
  display: block;
  margin-bottom: 8px;
}
.deep-header-title {
  font-size: clamp(1.1rem, 4.5vw, 1.3rem);
  font-weight: 800;
  color: #1E293B;
  margin: 0 0 4px;
  letter-spacing: 0.03em;
}
.deep-header-sub {
  font-size: clamp(0.7rem, 3vw, 0.82rem);
  color: #94A3B8;
  margin: 0;
  font-family: "STKaiti", "KaiTi", serif;
  letter-spacing: 0.04em;
}

/* 深度探索单卡片 */
.deep-single-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-top: 3px solid #8EC5FC;
  margin: 0 14px;
}

.deep-single-body {
  padding: 18px 18px 24px;
  font-size: clamp(0.82rem, 3.4vw, 0.92rem);
  line-height: 1.85;
  color: #475569;
}

/* Markdown 子元素样式 */
.deep-single-body :deep(h4) {
  font-size: clamp(0.88rem, 3.6vw, 1rem);
  font-weight: 700;
  color: #334155;
  margin: 16px 0 8px;
  padding-left: 10px;
  border-left: 3px solid #8EC5FC;
}

.deep-single-body :deep(.md-sub) {
  display: block;
  font-size: clamp(0.85rem, 3.5vw, 0.95rem);
  font-weight: 700;
  color: #334155;
  margin: 14px 0 6px;
  padding-left: 10px;
  border-left: 3px solid #8EC5FC;
}

.deep-single-body :deep(.md-strong) {
  color: #3B82F6;
  font-weight: 600;
}

.deep-single-body :deep(blockquote) {
  margin: 10px 0;
  padding: 10px 16px;
  background: linear-gradient(135deg, #F0F9FF 0%, #F0FFF4 100%);
  border-left: 3px solid #8EC5FC;
  border-radius: 0 8px 8px 0;
  font-size: clamp(0.75rem, 3.2vw, 0.85rem);
  color: #475569;
  line-height: 1.7;
  font-style: italic;
}

.deep-single-body :deep(ul) {
  margin: 8px 0;
  padding-left: 20px;
}
.deep-single-body :deep(li) {
  margin: 4px 0;
  line-height: 1.7;
}
.deep-single-body :deep(p) {
  margin: 6px 0;
}
.deep-single-body :deep(h3),
.deep-single-body :deep(h2) {
  font-size: clamp(0.95rem, 4vw, 1.1rem);
  font-weight: 700;
  color: #1E293B;
  margin: 18px 0 8px;
}

.result-actions { text-align: center; padding: 20px 14px 28px; }
.regenerate-btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 24px; background: #fff; color: #4A5568; border: 1.5px solid #E2E8F0; border-radius: 10px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all .3s ease; }
.regenerate-btn:hover { border-color: #8EC5FC; color: #3B82F6; }

.deep-explore-error { text-align: center; padding: 60px 20px; color: #EF4444; }
.deep-explore-error p { font-size: 15px; margin: 0 0 20px; }
.retry-btn { padding: 12px 32px; background: linear-gradient(135deg,#8EC5FC,#A8E6CF); color: #fff; border: none; border-radius: 12px; font-size: 15px; font-weight: 600; cursor: pointer; }

@keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* 响应式 */
@media (max-width: 640px) {
  .nav-container { gap: 6px; padding: 10px 12px; }
  .nav-tab { padding: 9px 16px; font-size: 14px; border-radius: 8px; }
  .section-profile-card { padding: 10px 10px 0; }
  .section-cards { padding: 8px 10px 18px; gap: 10px; }
  .info-card { border-radius: 14px; }
  .card-header { padding: 12px 14px 8px; }
  .card-title { font-size: 14px; }
  .card-body { padding: 10px 14px 14px; font-size: 13px; }
  .deep-explore { padding: 24px 10px; }
  .deep-single-card { margin: 0 10px; }
  .deep-single-body { padding: 14px 14px 18px; }
}
@media (min-width: 1024px) {
  .report-page { max-width: 600px; margin: 0 auto; box-shadow: 0 0 40px rgba(0,0,0,0.06); }
  .nav-container { padding: 14px 32px; gap: 12px; }
  .nav-tab { padding: 11px 28px; font-size: 15px; border-radius: 12px; }
  .section-profile-card { padding: 20px 20px 0; }
  .section-cards { padding: 14px 20px 28px; gap: 16px; }
  .info-card { border-radius: 18px; }
  .card-header { padding: 16px 20px 12px; }
  .card-body { padding: 14px 20px 18px; font-size: 14px; line-height: 1.9; }
  .card-title { font-size: 16px; }
  .deep-single-card { margin: 0 20px; }
  .deep-single-body { padding: 20px 24px 28px; font-size: 14px; line-height: 1.9; }
  .deep-header { padding: 28px 20px 20px; }
}
</style>
