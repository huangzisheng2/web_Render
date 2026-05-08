<template>
  <div class="talent-card">
    <!-- 淡雅水墨晕染背景 -->
    <div class="ink-wash-bg" aria-hidden="true"></div>

    <!-- 左侧五行侧边栏 -->
    <aside class="element-sidebar">
      <div
        v-for="el in elementList"
        :key="el"
        :class="['sidebar-item', { active: el === currentElement }]"
      >
        {{ el }}
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="card-main">
      <!-- ===== 顶部标题区 ===== -->
      <header class="card-header">
        <h1 class="main-title">
          <span class="name-text">{{ displayName }}</span>
          <span class="title-suffix">的潜在天赋档案</span>
        </h1>
        <div class="daypillar-row">
          <span class="dp-badge" :style="dpBadgeStyle">
            <span class="dp-icon">{{ elementIcon }}</span>
            <span class="dp-name">{{ dayPillarLabel }}</span>
          </span>
          <span class="dp-dot">·</span>
          <span class="dp-summary">{{ dayPillarSummaryText }}</span>
        </div>
      </header>

      <!-- ===== 中部主视觉区 ===== -->
      <div class="card-body">
        <!-- 左侧：天赋标签 -->
        <div class="talent-list">
          <div
            v-for="(tag, i) in displayTags"
            :key="i"
            class="talent-item"
          >
            <div class="talent-icon" :style="{ background: talentColors[i] }">
              <span class="t-icon">{{ talentEmojis[i] }}</span>
            </div>
            <div class="talent-info">
              <div class="talent-name">{{ tag }}</div>
              <div v-if="tagDescriptions[i]" class="talent-desc">{{ tagDescriptions[i] }}</div>
            </div>
          </div>
        </div>

        <!-- 右侧：Q版人物形象 -->
        <div class="avatar-area">
          <div class="avatar-ring" :style="{ borderColor: elementAccent + '40' }">
            <div class="avatar-inner">
              <img
                v-if="avatarUrl"
                :src="avatarUrl"
                alt="Q版形象"
                class="avatar-img"
                @error="avatarError = true"
              />
              <div v-else class="avatar-placeholder">
                <span class="ph-char">{{ dayMaster }}</span>
                <span class="ph-label">{{ currentElement }}</span>
              </div>
            </div>
          </div>
          <!-- 右下角水波纹装饰 -->
          <div class="wave-deco" aria-hidden="true" :style="{ color: elementAccent }">
            <svg viewBox="0 0 160 80" preserveAspectRatio="none">
              <path d="M0,40 Q40,10 80,40 T160,40 L160,80 L0,80 Z" fill="currentColor" opacity="0.08"/>
              <path d="M0,55 Q40,30 80,55 T160,55 L160,80 L0,80 Z" fill="currentColor" opacity="0.05"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- ===== 底部总结区 ===== -->
      <footer class="card-footer">
        <!-- 金色装饰线 -->
        <div class="deco-line">
          <span class="deco-left">◆</span>
          <span class="deco-dragon">🐉</span>
          <span class="deco-right">◆</span>
        </div>

        <!-- 一句话概括 -->
        <p class="trait-summary">{{ traitDescription || traitInfo.description }}</p>

        <!-- 关键词 + 历史人物 -->
        <div class="bottom-grid">
          <div class="keywords-section">
            <h3 class="section-title">天赋关键词</h3>
            <div class="keywords-pills">
              <span
                v-for="(kw, i) in displayKeywords"
                :key="i"
                class="keyword-pill"
              >{{ kw }}</span>
            </div>
          </div>
          <div class="history-section">
            <h3 class="section-title">历史人物</h3>
            <div class="history-list">
              <div
                v-for="(figure, i) in historicalFigures"
                :key="i"
                class="history-item"
              >
                <span class="fig-bullet">•</span>
                <span class="fig-text">{{ figure.name }}，{{ figure.title }}</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
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

const currentElement = computed(() => traitInfo.value.element || '水')

const dayPillarLabel = computed(() => {
  if (props.dayPillar) return props.dayPillar
  return props.dayMaster + (traitInfo.value.element || '')
})

// 日柱概述（取前12字）
const dayPillarSummaryText = computed(() => {
  if (props.dayColumnSummary) return props.dayColumnSummary
  const summaries = DAY_COLUMN_SUMMARIES[props.dayMaster]
  if (!summaries) return ''
  const isMale = (props.gender === 'male' || props.gender === '男')
  const full = summaries[isMale ? 'male' : 'female'] || ''
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

// 固定天赋图标与配色（与参考图一致）
const talentEmojis = ['💡', '🔍', '⚖️', '👑', '💜']
const talentColors = ['#4A90D9', '#52B788', '#D4A853', '#E06C75', '#9B8EC2']

// 天赋说明（从 talentSummary 切分，每段限25字）
const tagDescriptions = computed(() => {
  const summary = props.talentSummary || ''
  if (!summary) return []
  const parts = summary.split(/[。！？]/).filter(s => s.trim())
  return parts.slice(0, 5).map(p => p.trim().slice(0, 25))
})

// ===== 五行主题配置 =====
const elementList = ['金', '木', '水', '火', '土']

const elementMeta = {
  '水': { accent: '#4A90D9', bgLight: '#EFF6FF', icon: '💧' },
  '木': { accent: '#52B788', bgLight: '#F0FDF4', icon: '🌿' },
  '火': { accent: '#E06C75', bgLight: '#FEF2F2', icon: '🔥' },
  '土': { accent: '#D4A853', bgLight: '#FFFBEB', icon: '⛰️' },
  '金': { accent: '#9CA3AF', bgLight: '#F3F4F6', icon: '⚜️' }
}

const currentMeta = computed(() => elementMeta[currentElement.value] || elementMeta['水'])

const elementAccent = computed(() => currentMeta.value.accent)
const elementBgLight = computed(() => currentMeta.value.bgLight)
const elementIcon = computed(() => currentMeta.value.icon)

const dpBadgeStyle = computed(() => ({
  background: elementBgLight.value,
  color: elementAccent.value
}))
</script>

<style scoped>
/* ===== 整体卡片 ===== */
.talent-card {
  width: 100%;
  aspect-ratio: 3 / 4;
  border-radius: 16px;
  background: #F8F5EE;
  overflow: hidden;
  display: flex;
  position: relative;
  font-family: "PingFang SC", "Microsoft YaHei", "STSong", "Noto Serif SC", serif;
  box-shadow: 0 8px 32px rgba(44, 36, 22, 0.08);
  color: #2C2416;
}

/* 淡雅水墨晕染背景 */
.ink-wash-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    radial-gradient(ellipse 80% 50% at 10% 20%, rgba(74, 144, 217, 0.04) 0%, transparent 70%),
    radial-gradient(ellipse 60% 40% at 90% 80%, rgba(212, 169, 83, 0.03) 0%, transparent 70%),
    radial-gradient(ellipse 50% 50% at 50% 50%, rgba(44, 36, 22, 0.015) 0%, transparent 70%);
}

/* ===== 左侧五行侧边栏 ===== */
.element-sidebar {
  width: 32px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px 0;
  border-right: 1px solid rgba(44, 36, 22, 0.06);
  position: relative;
  z-index: 1;
}

.sidebar-item {
  writing-mode: vertical-rl;
  text-orientation: upright;
  font-size: 12px;
  font-weight: 700;
  color: #C4BDB0;
  padding: 8px 2px;
  border-radius: 10px;
  transition: all 0.25s ease;
  letter-spacing: 0.06em;
  cursor: default;
}

.sidebar-item.active {
  background: v-bind(elementAccent);
  color: #FFFFFF;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

/* ===== 主内容区 ===== */
.card-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 14px 16px 12px;
  min-width: 0;
  position: relative;
  z-index: 1;
}

/* ===== 顶部标题区 ===== */
.card-header {
  text-align: center;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.main-title {
  margin: 0 0 6px;
  font-size: clamp(1.2rem, 5vw, 1.7rem);
  font-weight: 900;
  color: #2C2416;
  letter-spacing: 0.04em;
  line-height: 1.25;
}

.name-text {
  color: #2C2416;
}

.title-suffix {
  color: #5A5040;
}

.daypillar-row {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  flex-wrap: wrap;
}

.dp-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 14px;
  font-size: clamp(0.7rem, 2.8vw, 0.85rem);
  font-weight: 800;
}

.dp-icon {
  font-size: 13px;
  line-height: 1;
}

.dp-name {
  letter-spacing: 0.04em;
}

.dp-dot {
  color: #C9A96E;
  font-weight: 700;
  font-size: clamp(0.75rem, 3vw, 0.9rem);
}

.dp-summary {
  font-size: clamp(0.62rem, 2.5vw, 0.78rem);
  color: #8A8070;
  font-style: italic;
  letter-spacing: 0.03em;
}

/* ===== 中部主视觉区 ===== */
.card-body {
  flex: 1;
  display: flex;
  gap: 12px;
  min-height: 0;
  margin-bottom: 10px;
}

/* 左侧天赋标签 */
.talent-list {
  flex: 0 0 36%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: clamp(6px, 1.8vw, 10px);
  min-width: 0;
}

.talent-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.talent-icon {
  width: clamp(28px, 7.5vw, 36px);
  height: clamp(28px, 7.5vw, 36px);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.t-icon {
  font-size: clamp(13px, 3.2vw, 16px);
  line-height: 1;
  filter: grayscale(0.2) brightness(1.1);
}

.talent-info {
  min-width: 0;
  padding-top: 1px;
}

.talent-name {
  font-size: clamp(0.72rem, 3vw, 0.88rem);
  font-weight: 800;
  color: #2C2416;
  letter-spacing: 0.02em;
  line-height: 1.2;
}

.talent-desc {
  margin: 2px 0 0;
  font-size: clamp(0.52rem, 2.1vw, 0.65rem);
  color: #8A8070;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 右侧人物形象 */
.avatar-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  min-width: 0;
}

.avatar-ring {
  width: clamp(150px, 42vw, 260px);
  aspect-ratio: 1;
  border-radius: 50%;
  border: 2px solid;
  padding: 5px;
  position: relative;
  z-index: 1;
}

.avatar-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(180deg, #F5F0E6 0%, #EBE4D6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
}

.avatar-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.ph-char {
  font-size: clamp(32px, 9vw, 48px);
  font-weight: 900;
  color: #C4BDB0;
}

.ph-label {
  font-size: 14px;
  font-weight: 700;
  color: #B0A898;
}

/* 右下角水波纹装饰 */
.wave-deco {
  position: absolute;
  right: -6%;
  bottom: -4%;
  width: 55%;
  height: 35%;
  pointer-events: none;
  z-index: 0;
}

.wave-deco svg {
  width: 100%;
  height: 100%;
}

/* ===== 底部总结区 ===== */
.card-footer {
  flex-shrink: 0;
  border-top: 1px solid #E8E0D0;
  padding-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 金色装饰线 */
.deco-line {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.deco-left,
.deco-right {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, #C9A96E 30%, #C9A96E 70%, transparent);
  font-size: 0;
}

.deco-dragon {
  font-size: 14px;
  color: #C9A96E;
  flex-shrink: 0;
}

/* 一句话概括 */
.trait-summary {
  margin: 0;
  font-size: clamp(0.8rem, 3.4vw, 1rem);
  font-weight: 700;
  color: #C9A96E;
  text-align: center;
  line-height: 1.5;
  letter-spacing: 0.04em;
}

/* 关键词 + 历史人物 */
.bottom-grid {
  display: flex;
  gap: 12px;
}

.keywords-section,
.history-section {
  flex: 1;
  min-width: 0;
}

.section-title {
  margin: 0 0 6px;
  font-size: clamp(0.6rem, 2.4vw, 0.72rem);
  font-weight: 800;
  color: #5A5040;
  letter-spacing: 0.04em;
}

.keywords-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.keyword-pill {
  font-size: clamp(0.55rem, 2.2vw, 0.7rem);
  font-weight: 700;
  color: #C9A96E;
  background: #F0E8D8;
  padding: 3px 9px;
  border-radius: 10px;
  border: 1px solid #E8DCC8;
  white-space: nowrap;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.history-item {
  display: flex;
  align-items: baseline;
  gap: 4px;
  font-size: clamp(0.55rem, 2.2vw, 0.7rem);
  color: #6A6050;
  line-height: 1.4;
}

.fig-bullet {
  color: #C9A96E;
  font-size: 1.1em;
  line-height: 1;
}

.fig-text {
  letter-spacing: 0.02em;
}

/* ===== 响应式 ===== */
@media (max-width: 480px) {
  .card-main {
    padding: 10px 12px 10px;
  }
  .card-body {
    flex-direction: column-reverse;
    gap: 8px;
  }
  .talent-list {
    flex: none;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 6px;
  }
  .talent-item {
    flex: 0 0 48%;
  }
  .avatar-ring {
    width: 140px;
  }
  .bottom-grid {
    flex-direction: column;
    gap: 8px;
  }
}

@media (min-width: 768px) {
  .card-main {
    padding: 18px 24px 14px;
  }
  .main-title {
    font-size: 1.85rem;
  }
  .talent-icon {
    width: 40px;
    height: 40px;
  }
  .t-icon {
    font-size: 18px;
  }
  .talent-name {
    font-size: 0.95rem;
  }
  .talent-desc {
    font-size: 0.72rem;
  }
  .avatar-ring {
    width: 280px;
  }
  .trait-summary {
    font-size: 1.05rem;
  }
  .keyword-pill {
    font-size: 0.78rem;
    padding: 4px 12px;
  }
  .history-item {
    font-size: 0.78rem;
  }
}
</style>