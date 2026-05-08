<template>
  <div class="talent-card">

    <!-- ===== 顶部：主标题 + 日柱行（含概述） ===== -->
    <div class="card-top">
      <div class="title-row">
        <span class="top-name">{{ displayName }}</span>
        <span class="top-title">的潜在天赋档案</span>
      </div>
      <!-- 日柱行：五行图标 + 日柱(高亮) + · + 日柱概述(高亮) -->
      <div class="daypillar-line">
        <span class="dp-element-icon">{{ traitInfo.elementSymbol }}</span>
        <span class="dp-label" :style="{ color: traitInfo.color }">{{ dayPillarLabel }}</span>
        <span class="dp-sep">·</span>
        <span class="dp-summary" :style="{ color: traitInfo.color }">{{ dayPillarSummary }}</span>
      </div>
    </div>

    <!-- ===== 中部：左侧天赋标签(40%) + 右侧Q版人物(60%) ===== -->
    <div class="card-center">
      <div class="center-left">
        <div
          v-for="(tag, i) in displayTags"
          :key="i"
          class="talent-tag-item"
          :style="{ borderColor: traitInfo.color + '50', background: traitInfo.color + '08' }"
        >
          <div class="tag-upper">
            <span class="tag-emoji">{{ tagEmojis[i] }}</span>
            <span class="tag-label">{{ tag }}</span>
          </div>
          <span class="tag-desc" v-if="tagDescriptions[i]">{{ tagDescriptions[i] }}</span>
        </div>
      </div>

      <div class="center-right">
        <img
          v-if="avatarUrl"
          :src="avatarUrl"
          alt="Q版形象"
          class="avatar-img"
          @error="avatarError = true"
        />
        <div
          v-else
          class="avatar-placeholder"
          :style="{ background: traitInfo.color + '15', color: traitInfo.color }"
        >
          <span class="placeholder-char">{{ dayMaster }}</span>
          <span class="placeholder-el">{{ traitInfo.element }}</span>
        </div>
      </div>
    </div>

    <!-- ===== 五行图标行 ===== -->
    <div class="five-element-row">
      <div
        v-for="el in elementList"
        :key="el.name"
        class="element-icon-wrap"
        :class="{ active: el.name === traitInfo.element }"
        :style="el.name === traitInfo.element ? { color: el.color, borderColor: el.color, background: el.color + '12' } : {}"
      >
        <span class="el-symbol">{{ el.symbol }}</span>
        <span class="el-name">{{ el.name }}</span>
      </div>
    </div>

    <!-- ===== 底部：概括语 + 双列布局 ===== -->
    <div
      class="card-bottom"
      :style="{ borderTopColor: traitInfo.color + '15' }"
    >
      <!-- 一句话概括 -->
      <p class="trait-text" :style="{ textShadow: `0 2px 8px ${traitInfo.color}20` }">
        {{ traitDescription || traitInfo.description }}
      </p>

      <!-- 双列布局：天赋关键词 | 历史人物 -->
      <div class="bottom-columns" v-if="displayKeywords.length || historicalFigures.length">
        <!-- 左列：天赋关键词 -->
        <div class="bottom-col left-col" v-if="displayKeywords.length">
          <div class="col-title">天赋关键词</div>
          <div class="keyword-pills">
            <span
              v-for="(kw, i) in displayKeywords"
              :key="i"
              class="kw-pill"
            >{{ kw }}</span>
          </div>
        </div>

        <!-- 右列：历史人物 -->
        <div class="bottom-col right-col" v-if="displayHistoricalFigures.length">
          <div class="col-title">历史人物</div>
          <div class="history-list">
            <div
              v-for="(figure, i) in displayHistoricalFigures"
              :key="i"
              class="history-figure"
            >
              <span class="fig-bullet" :style="{ color: traitInfo.color }">·</span>
              <span class="fig-text">{{ figure.name }}，{{ figure.title }}</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getDayMasterTrait, getFullAvatarUrl, DAY_PILLAR_SUMMARIES, ELEMENT_COLORS } from '../data/dayMasterData'

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

// 日柱标签：优先用完整 dayPillar（如"壬辰"）
const dayPillarLabel = computed(() => {
  if (props.dayPillar) return props.dayPillar
  return props.dayMaster + (traitInfo.value.element || '')
})

// 日柱概述：从 DAY_PILLAR_SUMMARIES 取精简短句
const dayPillarSummary = computed(() => {
  if (props.dayPillar && DAY_PILLAR_SUMMARIES[props.dayPillar]) {
    return DAY_PILLAR_SUMMARIES[props.dayPillar]
  }
  // 回退：用日柱名拼接尝试
  return ''
})

const avatarUrl = computed(() => {
  if (avatarError.value) return ''
  return getFullAvatarUrl(props.dayMaster, props.gender)
})

// 天赋标签（最多5个）
const displayTags = computed(() => {
  return props.talentTags?.length ? props.talentTags.slice(0, 5) : []
})

// 天赋关键词（最多5个）
const displayKeywords = computed(() => {
  return props.keywords?.length ? props.keywords.slice(0, 5) : []
})

// 历史人物（最多2个）
const displayHistoricalFigures = computed(() => {
  return props.historicalFigures?.slice(0, 2) || []
})

// 固定天赋图标
const tagEmojis = ['💡', '🔍', '⚖️', '👑', '💜']

// 五行列表（用于图标行）
const elementList = computed(() => [
  { name: '金', symbol: '⚔️', color: ELEMENT_COLORS['金'] },
  { name: '木', symbol: '🌲', color: ELEMENT_COLORS['木'] },
  { name: '水', symbol: '💧', color: ELEMENT_COLORS['水'] },
  { name: '火', symbol: '🔥', color: ELEMENT_COLORS['火'] },
  { name: '土', symbol: '⛰️', color: ELEMENT_COLORS['土'] }
])

/**
 * 天赋标签描述：
 * 对每个 displayTags[i]，在 talentSummary 中按标签名匹配对应段落，
 * 取该段落中标签名后（即"标签名："之后）的前15个字，超出用…省略。
 */
const tagDescriptions = computed(() => {
  const summary = props.talentSummary || ''
  const tags = props.talentTags?.slice(0, 5) || []
  const result = []

  for (let i = 0; i < 5; i++) {
    const tag = tags[i]
    if (!tag || !summary) { result.push(''); continue }

    let startIdx = -1
    const candidates = [
      `**${tag}**：`, `${tag}：`, `**${tag}**:`, `${tag}:`
    ]
    for (const pat of candidates) {
      startIdx = summary.indexOf(pat)
      if (startIdx !== -1) break
    }
    if (startIdx === -1) { result.push(''); continue }

    const colonIdx = summary.indexOf('：', startIdx)
    const colonIdx2 = summary.indexOf(':', startIdx)
    const realColonIdx = (colonIdx !== -1 && (colonIdx2 === -1 || colonIdx < colonIdx2)) ? colonIdx : colonIdx2
    if (realColonIdx === -1 || realColonIdx >= summary.length - 1) { result.push(''); continue }

    const contentStart = realColonIdx + 1

    let endIdx = summary.length
    for (let j = 0; j < 5; j++) {
      if (j === i) continue
      const nextTag = tags[j]
      if (!nextTag) continue
      const nextCandidates = [
        `**${nextTag}**：`, `**${nextTag}**:`,
        `${nextTag}：`, `${nextTag}:`
      ]
      for (const np of nextCandidates) {
        const idx = summary.indexOf(np, startIdx + 1)
        if (idx !== -1 && idx < endIdx) endIdx = idx
      }
    }

    const text = summary.substring(contentStart, endIdx).trim()
    if (text) {
      result.push(text.slice(0, 15) + (text.length > 15 ? '…' : ''))
    } else {
      result.push('')
    }
  }

  while (result.length < 5) result.push('')
  return result
})
</script>

<style scoped>
.talent-card {
  width: 100%;
  border-radius: 18px;
  background: linear-gradient(145deg, #ffffff 0%, #FAFBFC 100%);
  border: 1px solid rgba(142, 197, 252, 0.12);
  box-shadow: 0 4px 20px rgba(142, 197, 252, 0.06);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  font-family: "PingFang SC", "Microsoft YaHei", "STSong", "Noto Serif SC", serif;
  color: #1E293B;
}

/* ===== 顶部 ===== */
.card-top {
  padding: 14px 18px;
  text-align: center;
  border-bottom: 1px solid rgba(142, 197, 252, 0.06);
}

.title-row {
  margin-bottom: 6px;
}

.top-name {
  font-size: clamp(1.2rem, 5vw, 1.5rem);
  font-weight: 800;
  color: #1E293B;
  letter-spacing: 0.04em;
}

.top-title {
  font-size: clamp(0.85rem, 3.8vw, 1rem);
  font-weight: 500;
  color: #64748B;
  letter-spacing: 0.04em;
  margin-left: 2px;
}

/* 日柱信息行：五行图标 + 日柱 + · + 概述 */
.daypillar-line {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  flex-wrap: wrap;
}

.dp-element-icon {
  font-size: clamp(1rem, 4vw, 1.2rem);
  flex-shrink: 0;
}

.dp-label {
  font-size: clamp(0.9rem, 3.8vw, 1.1rem);
  font-weight: 800;
  letter-spacing: 0.06em;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.dp-sep {
  font-size: clamp(0.75rem, 3vw, 0.9rem);
  color: #C9A96E;
  font-weight: 600;
}

.dp-summary {
  font-size: clamp(0.85rem, 3.6vw, 1rem);
  font-weight: 700;
  font-family: "STKaiti", "KaiTi", "Noto Serif SC", serif;
  letter-spacing: 0.04em;
}

/* ===== 中部 ===== */
.card-center {
  flex: 1;
  display: flex;
  padding: 12px 14px 10px;
  gap: 10px;
  min-height: 0;
}

/* 左侧 · 天赋标签 40% */
.center-left {
  flex: 0 0 40%;
  display: flex;
  flex-direction: column;
  gap: 6px;
  justify-content: center;
}

.talent-tag-item {
  padding: 6px 10px;
  border-radius: 10px;
  border-left: 3px solid;
  line-height: 1.2;
}

.tag-upper {
  display: flex;
  align-items: center;
  gap: 5px;
}

.tag-emoji {
  font-size: clamp(0.85rem, 3.5vw, 1rem);
  flex-shrink: 0;
}

.tag-label {
  font-size: clamp(0.7rem, 3vw, 0.82rem);
  font-weight: 700;
  color: #334155;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-desc {
  display: block;
  margin-top: 2px;
  font-size: clamp(0.5rem, 2.2vw, 0.62rem);
  font-weight: 400;
  color: #94A3B8;
  line-height: 1.3;
  padding-left: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 右侧 · Q版形象 60% */
.center-right {
  flex: 0 0 60%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.avatar-img {
  width: 100%;
  max-width: 288px;
  height: auto;
  object-fit: contain;
  object-position: center bottom;
  display: block;
}

.avatar-placeholder {
  width: 80%;
  max-width: 240px;
  aspect-ratio: 3 / 4;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border-radius: 12px;
}

.placeholder-char { font-size: 48px; font-weight: 800; }
.placeholder-el { font-size: 16px; font-weight: 600; opacity: 0.7; }

/* ===== 五行图标行 ===== */
.five-element-row {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 8px 18px 6px;
}

.element-icon-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 6px 10px;
  border-radius: 10px;
  border: 1.5px solid #E2E8F0;
  color: #CBD5E1;
  transition: all 0.3s ease;
}

.element-icon-wrap.active {
  border-width: 2px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.el-symbol {
  font-size: clamp(1rem, 4vw, 1.3rem);
  line-height: 1;
}

.el-name {
  font-size: clamp(0.5rem, 2.2vw, 0.65rem);
  font-weight: 600;
  letter-spacing: 0.06em;
  font-family: "STKaiti", "KaiTi", serif;
}

/* ===== 底部 ===== */
.card-bottom {
  padding: 12px 16px;
  border-top: 1.5px solid;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.5);
}

/* 一句话概括 */
.trait-text {
  margin: 0;
  font-size: clamp(0.85rem, 3.8vw, 1.05rem);
  font-weight: 700;
  font-family: "STKaiti", "KaiTi", "Noto Serif SC", serif;
  color: #334155;
  text-align: center;
  line-height: 1.5;
  letter-spacing: 0.04em;
}

/* 双列布局 */
.bottom-columns {
  display: flex;
  width: 100%;
  gap: 16px;
}

.bottom-col {
  flex: 1;
  min-width: 0;
}

.col-title {
  font-size: clamp(0.65rem, 2.8vw, 0.78rem);
  font-weight: 700;
  color: #1E293B;
  margin-bottom: 6px;
  letter-spacing: 0.03em;
}

/* 左列：天赋关键词 pill 按钮 */
.keyword-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.kw-pill {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  background: #F5ECD7;
  color: #5C4A1E;
  font-size: clamp(0.55rem, 2.4vw, 0.7rem);
  font-weight: 600;
  white-space: nowrap;
  letter-spacing: 0.02em;
}

/* 右列：历史人物 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-figure {
  display: flex;
  align-items: baseline;
  gap: 4px;
  font-size: clamp(0.55rem, 2.4vw, 0.7rem);
  color: #94A3B8;
  opacity: 0.85;
  line-height: 1.4;
}

.fig-bullet {
  font-weight: 700;
  font-size: 1.1em;
  line-height: 1;
  flex-shrink: 0;
}

.fig-text {
  letter-spacing: 0.02em;
}

/* ===== 响应式 ===== */
@media (max-width: 640px) {
  .card-top { padding: 10px 12px; }
  .card-center { padding: 10px 10px 8px; gap: 8px; }
  .center-left { flex: 0 0 42%; }
  .center-right { flex: 0 0 58%; }
  .avatar-img { max-width: 220px; }
  .five-element-row { gap: 8px; padding: 6px 12px 4px; }
  .element-icon-wrap { padding: 4px 7px; }
  .card-bottom { padding: 10px 12px; gap: 8px; }
  .bottom-columns { gap: 10px; }
}

@media (min-width: 1024px) {
  .card-top { padding: 16px 24px; }
  .card-center { padding: 16px 20px 12px; gap: 14px; }
  .center-left { flex: 0 0 38%; }
  .center-right { flex: 0 0 62%; }
  .talent-tag-item { padding: 8px 14px; border-radius: 12px; }
  .avatar-img { max-width: 320px; }
  .five-element-row { gap: 16px; padding: 10px 24px 8px; }
  .element-icon-wrap { padding: 8px 14px; border-radius: 12px; }
  .card-bottom { padding: 14px 20px 16px; gap: 12px; }
  .bottom-columns { gap: 20px; }
}
</style>
