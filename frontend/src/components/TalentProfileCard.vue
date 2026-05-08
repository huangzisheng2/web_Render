<template>
  <div class="talent-card" :style="cardStyle">
    <!-- 水波纹背景装饰 -->
    <div class="wave-bg" aria-hidden="true">
      <svg class="wave wave-1" viewBox="0 0 800 400" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M0,200 C200,150 350,250 500,200 C650,150 750,220 800,180 L800,400 L0,400 Z" fill="currentColor" opacity="0.06"/>
      </svg>
      <svg class="wave wave-2" viewBox="0 0 800 400" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M0,250 C150,200 300,300 450,250 C600,200 700,280 800,240 L800,400 L0,400 Z" fill="currentColor" opacity="0.04"/>
      </svg>
      <svg class="wave wave-3" viewBox="0 0 800 400" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M0,300 C100,270 250,330 400,290 C550,250 680,310 800,280 L800,400 L0,400 Z" fill="currentColor" opacity="0.03"/>
      </svg>
    </div>

    <!-- ===== 顶部标题区 ~10% ===== -->
    <header class="card-header">
      <h1 class="main-title">
        <span class="name-text">{{ displayName }}</span>
        <span class="title-suffix">的潜在天赋档案</span>
      </h1>
      <div class="daypillar-row">
        <span class="daypillar-badge" :style="{ background: elementGradient }">{{ dayPillarLabel }}</span>
        <span class="daypillar-dot">·</span>
        <span class="daypillar-summary">{{ dayPillarSummaryText }}</span>
      </div>
    </header>

    <!-- ===== 中部主视觉区 ~70% ===== -->
    <div class="card-body">
      <!-- 左侧 30%：核心天赋标签 -->
      <div class="body-left">
        <div
          v-for="(tag, i) in displayTags"
          :key="i"
          class="talent-item"
        >
          <span class="talent-icon" :style="{ background: talentColors[i] }">
            {{ talentEmojis[i] }}
          </span>
          <div class="talent-text">
            <span class="talent-name">{{ tag }}</span>
            <p class="talent-desc" v-if="tagDescriptions[i]">{{ tagDescriptions[i] }}</p>
          </div>
        </div>
      </div>

      <!-- 右侧 70%：Q版形象 -->
      <div class="body-right">
        <div class="avatar-area">
          <!-- 光晕背景 -->
          <div class="avatar-glow" :style="{ background: elementGlowColor }"></div>
          <img
            v-if="avatarUrl"
            :src="avatarUrl"
            alt="Q版形象"
            class="avatar-img"
            @error="avatarError = true"
          />
          <div v-else class="avatar-placeholder">
            <span class="ph-char">{{ dayMaster }}</span>
            <span class="ph-el">{{ traitInfo.element }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 底部总结区 ~20% ===== -->
    <footer class="card-footer">
      <!-- 一句话概括 -->
      <p class="trait-summary">{{ traitDescription || traitInfo.description }}</p>

      <!-- 天赋关键词 -->
      <div class="keywords-row" v-if="displayKeywords.length">
        <span
          v-for="(kw, i) in displayKeywords"
          :key="i"
          class="keyword-dot"
        >{{ kw }}<span v-if="i < displayKeywords.length - 1" class="dot-sep"> · </span></span>
      </div>

      <!-- 历史人物 -->
      <div class="history-row" v-if="historicalFigures.length">
        <div
          v-for="(figure, i) in historicalFigures"
          :key="i"
          class="history-item"
        >
          <span class="fig-bullet">•</span>
          <span class="fig-name">{{ figure.name }}</span>
          <span class="fig-title">，{{ figure.title }}</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getDayMasterTrait, getFullAvatarUrl, DAY_COLUMN_SUMMARIES } from '../data/dayMasterData'

const props = defineProps({
  name: { type: String, default: '探索者' },
  dayMaster: { type: String, default: '甲' },
  gender: { type: String, default: 'male' },
  dayPillar: { type: String, default: '' },
  talentTags: { type: Array, default: () => [] },
  talentSummary: { type: String, default: '' },
  keywords: { type: Array, default: () => [] },
  dayColumnSummary: { type: String, default: '' },
  traitDescription: { type: String, default: '' },
  historicalFigures: { type: Array, default: () => [] }
})

const avatarError = ref(false)

const displayName = computed(() => props.name)

const traitInfo = computed(() => {
  return getDayMasterTrait(props.dayMaster, props.gender)
})

const dayPillarLabel = computed(() => {
  if (props.dayPillar) return props.dayPillar
  return props.dayMaster + (traitInfo.value.element || '')
})

// 日柱概述（如"气势雄浑，龙归大海"）
const dayPillarSummaryText = computed(() => {
  if (props.dayColumnSummary) return props.dayColumnSummary
  const summaries = DAY_COLUMN_SUMMARIES[props.dayMaster]
  if (!summaries) return ''
  const isMale = (props.gender === 'male' || props.gender === '男')
  const full = summaries[isMale ? 'male' : 'female'] || ''
  // 取前12字作为概述
  return full.slice(0, 12) + (full.length > 12 ? '…' : '')
})

const avatarUrl = computed(() => {
  if (avatarError.value) return ''
  return getFullAvatarUrl(props.dayMaster, props.gender)
})

const displayTags = computed(() => {
  return props.talentTags?.length ? props.talentTags.slice(0, 5) : []
})

const displayKeywords = computed(() => {
  return props.keywords?.length ? props.keywords.slice(0, 5) : []
})

// 五行对应的 emoji 和颜色
const talentEmojis = ['🌊', '🔍', '⚖️', '👑', '💜']

const talentColors = [
  '#3B82F6', // 蓝 - 水/创新
  '#10B981', // 绿 - 木/洞察
  '#D4A853', // 金 - 土/调配
  '#EF4444', // 红 - 火/领导
  '#8B5CF6'  // 紫 - 共情
]

// 天赋标签配25字说明
const tagDescriptions = computed(() => {
  const summary = props.talentSummary || ''
  if (!summary) return []
  const parts = summary.split(/[。！？]/).filter(s => s.trim())
  return parts.slice(0, 5).map(p => p.trim().slice(0, 25))
})

// ===== 五行主题色系 =====
const elementThemes = {
  '水': {
    bgFrom: '#0A1628',
    bgTo: '#0C2D4A',
    bgMid: '#0E2240',
    accent: '#38BDF8',
    accentLight: '#7DD3FC',
    glowColor: 'rgba(56, 189, 248, 0.15)',
    waveColor: '#38BDF8',
    goldAccent: '#C9A96E'
  },
  '木': {
    bgFrom: '#071A0E',
    bgTo: '#0A3320',
    bgMid: '#0C2818',
    accent: '#22C55E',
    accentLight: '#4ADE80',
    glowColor: 'rgba(34, 197, 94, 0.15)',
    waveColor: '#22C55E',
    goldAccent: '#C9A96E'
  },
  '火': {
    bgFrom: '#1A0A0A',
    bgTo: '#3D1010',
    bgMid: '#2A0E0E',
    accent: '#EF4444',
    accentLight: '#F87171',
    glowColor: 'rgba(239, 68, 68, 0.15)',
    waveColor: '#EF4444',
    goldAccent: '#C9A96E'
  },
  '土': {
    bgFrom: '#1A1508',
    bgTo: '#33280E',
    bgMid: '#2A200C',
    accent: '#D97706',
    accentLight: '#F59E0B',
    glowColor: 'rgba(217, 119, 6, 0.15)',
    waveColor: '#D97706',
    goldAccent: '#C9A96E'
  },
  '金': {
    bgFrom: '#111318',
    bgTo: '#1E2430',
    bgMid: '#181C26',
    accent: '#94A3B8',
    accentLight: '#CBD5E1',
    glowColor: 'rgba(148, 163, 184, 0.15)',
    waveColor: '#94A3B8',
    goldAccent: '#C9A96E'
  }
}

const currentTheme = computed(() => {
  return elementThemes[traitInfo.value.element] || elementThemes['水']
})

const elementGradient = computed(() => {
  return `linear-gradient(135deg, ${currentTheme.value.accent}, ${currentTheme.value.accentLight})`
})

const elementGlowColor = computed(() => {
  return currentTheme.value.glowColor
})

const cardStyle = computed(() => {
  const t = currentTheme.value
  return {
    '--bg-from': t.bgFrom,
    '--bg-to': t.bgTo,
    '--bg-mid': t.bgMid,
    '--accent': t.accent,
    '--accent-light': t.accentLight,
    '--glow': t.glowColor,
    '--wave-color': t.waveColor,
    '--gold': t.goldAccent
  }
})
</script>

<style scoped>
/* ===== 整体卡片：深色五行渐变 ===== */
.talent-card {
  width: 100%;
  aspect-ratio: 3 / 4;
  border-radius: 16px;
  background: linear-gradient(165deg, var(--bg-from) 0%, var(--bg-mid) 50%, var(--bg-to) 100%);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  font-family: -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "STSong", serif;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  color: #E8E4DF;
}

/* ===== 水波纹背景 ===== */
.wave-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.wave {
  position: absolute;
  width: 200%;
  height: 100%;
  color: var(--wave-color);
}

.wave-1 {
  bottom: 30%;
  left: -10%;
  animation: waveDrift 12s ease-in-out infinite;
}

.wave-2 {
  bottom: 20%;
  left: -30%;
  animation: waveDrift 16s ease-in-out infinite reverse;
}

.wave-3 {
  bottom: 10%;
  left: -20%;
  animation: waveDrift 20s ease-in-out infinite;
}

@keyframes waveDrift {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(5%); }
}

/* ===== 顶部标题区 ~10% ===== */
.card-header {
  position: relative;
  z-index: 1;
  padding: clamp(14px, 4vw, 22px) clamp(16px, 5vw, 28px) clamp(8px, 2.5vw, 14px);
  text-align: center;
}

.main-title {
  margin: 0 0 6px;
  font-size: clamp(1.2rem, 5.5vw, 1.65rem);
  font-weight: 900;
  color: #FFFFFF;
  letter-spacing: 0.06em;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  line-height: 1.3;
}

.name-text {
  color: var(--gold);
}

.title-suffix {
  color: rgba(255, 255, 255, 0.92);
}

.daypillar-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  flex-wrap: wrap;
}

.daypillar-badge {
  display: inline-block;
  font-size: clamp(0.7rem, 3vw, 0.85rem);
  font-weight: 800;
  color: #FFFFFF;
  padding: 2px 12px;
  border-radius: 12px;
  letter-spacing: 0.08em;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.daypillar-dot {
  color: var(--gold);
  font-size: clamp(0.8rem, 3vw, 1rem);
  font-weight: 700;
}

.daypillar-summary {
  font-size: clamp(0.65rem, 2.8vw, 0.78rem);
  color: rgba(255, 255, 255, 0.65);
  font-style: italic;
  letter-spacing: 0.04em;
}

/* ===== 中部主视觉区 ~70% ===== */
.card-body {
  flex: 1;
  display: flex;
  position: relative;
  z-index: 1;
  padding: 0 clamp(14px, 4vw, 24px) clamp(8px, 2.5vw, 14px);
  gap: clamp(10px, 3vw, 18px);
  min-height: 0;
}

/* ===== 左侧天赋标签 ~30% ===== */
.body-left {
  flex: 0 0 32%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: clamp(7px, 2vw, 11px);
}

.talent-item {
  display: flex;
  align-items: flex-start;
  gap: clamp(7px, 2vw, 10px);
}

.talent-icon {
  width: clamp(28px, 8vw, 36px);
  height: clamp(28px, 8vw, 36px);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: clamp(0.8rem, 3vw, 1rem);
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
}

.talent-text {
  min-width: 0;
  padding-top: 2px;
}

.talent-name {
  display: block;
  font-size: clamp(0.75rem, 3.2vw, 0.92rem);
  font-weight: 800;
  color: #FFFFFF;
  letter-spacing: 0.03em;
  line-height: 1.2;
}

.talent-desc {
  margin: 2px 0 0;
  font-size: clamp(0.52rem, 2.2vw, 0.64rem);
  color: rgba(255, 255, 255, 0.55);
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ===== 右侧Q版形象 ~70% ===== */
.body-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.avatar-area {
  position: relative;
  width: 100%;
  max-width: clamp(180px, 45vw, 280px);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 光晕 */
.avatar-glow {
  position: absolute;
  width: 120%;
  height: 120%;
  border-radius: 50%;
  filter: blur(30px);
  z-index: 0;
}

.avatar-img {
  position: relative;
  z-index: 1;
  width: 100%;
  height: auto;
  object-fit: contain;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3));
}

.avatar-placeholder {
  position: relative;
  z-index: 1;
  width: 70%;
  aspect-ratio: 3 / 4;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.15);
}

.ph-char {
  font-size: clamp(28px, 8vw, 44px);
  font-weight: 900;
  color: var(--accent-light);
}

.ph-el {
  font-size: clamp(12px, 3.5vw, 16px);
  font-weight: 700;
  color: rgba(255, 255, 255, 0.6);
}

/* ===== 底部总结区 ~20% ===== */
.card-footer {
  position: relative;
  z-index: 1;
  padding: clamp(10px, 3vw, 16px) clamp(16px, 5vw, 28px) clamp(12px, 3.5vw, 18px);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.15) 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: clamp(6px, 2vw, 10px);
}

.trait-summary {
  margin: 0;
  font-size: clamp(0.82rem, 3.6vw, 1rem);
  font-weight: 700;
  color: rgba(255, 255, 255, 0.92);
  text-align: center;
  line-height: 1.5;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.04em;
}

/* 关键词行 */
.keywords-row {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0;
}

.keyword-dot {
  font-size: clamp(0.65rem, 2.8vw, 0.8rem);
  font-weight: 700;
  color: var(--gold);
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.dot-sep {
  color: rgba(255, 255, 255, 0.3);
  margin: 0 2px;
}

/* 历史人物两列 */
.history-row {
  display: flex;
  gap: clamp(12px, 4vw, 24px);
  justify-content: center;
  flex-wrap: wrap;
}

.history-item {
  display: flex;
  align-items: baseline;
  gap: 4px;
  font-size: clamp(0.58rem, 2.4vw, 0.7rem);
  color: rgba(255, 255, 255, 0.45);
  white-space: nowrap;
}

.fig-bullet {
  color: var(--gold);
  font-size: 0.7em;
  opacity: 0.7;
}

.fig-name {
  color: rgba(255, 255, 255, 0.6);
  font-weight: 700;
}

.fig-title {
  color: rgba(255, 255, 255, 0.4);
}

/* ===== 响应式 ===== */
@media (max-width: 480px) {
  .card-body {
    flex-direction: column-reverse;
    gap: 8px;
    padding: 6px 12px 10px;
  }
  .body-left {
    flex: none;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 6px;
  }
  .talent-item {
    flex: 0 0 48%;
  }
  .body-right {
    flex: none;
  }
  .avatar-area {
    max-width: 160px;
  }
  .history-row {
    flex-direction: column;
    gap: 4px;
    align-items: center;
  }
}

@media (min-width: 768px) {
  .card-header { padding: 22px 28px 14px; }
  .main-title { font-size: 1.7rem; }
  .talent-icon { width: 40px; height: 40px; font-size: 1.1rem; }
  .talent-name { font-size: 0.95rem; }
  .talent-desc { font-size: 0.68rem; }
  .avatar-area { max-width: 300px; }
  .trait-summary { font-size: 1.05rem; }
  .keyword-dot { font-size: 0.82rem; }
}
</style>
