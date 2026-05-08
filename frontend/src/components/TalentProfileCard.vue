<template>
  <div class="talent-card">

    <!-- ===== 顶部：主标题 + 日柱行 ===== -->
    <div class="card-top">
      <div class="title-row">
        <span class="top-name">{{ displayName }}</span>
        <span class="top-title">的潜在天赋档案</span>
      </div>
      <!-- 日柱信息行：大字号高亮色 + 概述 -->
      <div class="daypillar-line">
        <span class="dp-label" :style="{ color: traitInfo.color }">{{ dayPillarLabel }}</span>
        <span class="dp-sep">·</span>
        <span class="dp-desc">{{ dayColumnText }}</span>
      </div>
    </div>

    <!-- ===== 中部：左侧天赋标签(40%) + 右侧Q版人物(60%，放大20%) ===== -->
    <div class="card-center">
      <!-- 左侧 40%（原30%+10%） -->
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
          <span class="tag-desc">{{ tagDescriptions[i] }}</span>
        </div>
      </div>

      <!-- 右侧 60%，图片放大20%，居中偏下 -->
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

    <!-- ===== 底部：概括语 + 关键词 · 分隔 + 历史人物两列 ===== -->
    <div
      class="card-bottom"
      :style="{ borderTopColor: traitInfo.color + '15' }"
    >
      <!-- 一句话概括：大字号书法体，阴影 -->
      <p class="trait-text" :style="{ textShadow: `0 2px 8px ${traitInfo.color}20` }">
        {{ traitDescription || traitInfo.description }}
      </p>

      <!-- 天赋关键词：中等字号，" · " 分隔，一字排开居中 -->
      <div class="keyword-line" v-if="displayKeywords.length">
        <span
          v-for="(kw, i) in displayKeywords"
          :key="i"
          class="kw-item"
        >{{ kw }}<span v-if="i < displayKeywords.length - 1" class="kw-sep"> · </span></span>
      </div>

      <!-- 历史人物：两列并排居中，小字号低不透明度 -->
      <div class="history-row" v-if="historicalFigures.length">
        <div
          v-for="(figure, i) in historicalFigures"
          :key="i"
          class="history-figure"
        >
          <span class="fig-bullet" :style="{ color: traitInfo.color }">·</span>
          <span class="fig-text">{{ figure.name }}，{{ figure.title }}</span>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getDayMasterTrait, getFullAvatarUrl, getDayColumnSummary } from '../data/dayMasterData'

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

// 日柱标签：优先用完整 dayPillar（如"壬辰"），否则用 dayMaster + element
const dayPillarLabel = computed(() => {
  if (props.dayPillar) return props.dayPillar
  return props.dayMaster + (traitInfo.value.element || '')
})

// 日柱概述（来自 DAY_COLUMN_SUMMARIES 或 prop）
const dayColumnText = computed(() => {
  return props.dayColumnSummary || getDayColumnSummary(props.dayMaster, props.gender) || ''
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

// 固定天赋图标（参考图风格）
const tagEmojis = ['💡', '🔍', '⚖️', '👑', '💜']

// 天赋标签描述：从 talentSummary 按标点切分，每段限15字，不足5个用''填充
const tagDescriptions = computed(() => {
  const summary = props.talentSummary || ''
  if (!summary) return ['', '', '', '', '']
  const parts = summary.split(/[。！？]/).filter(s => s.trim())
  const sliced = parts.slice(0, 5).map(p => p.trim().slice(0, 15))
  // 补足到5个
  while (sliced.length < 5) sliced.push('')
  return sliced
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

/* 日柱信息行 */
.daypillar-line {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  flex-wrap: wrap;
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

.dp-desc {
  font-size: clamp(0.65rem, 2.8vw, 0.78rem);
  font-family: "STKaiti", "KaiTi", "Noto Serif SC", serif;
  color: #6B7280;
  letter-spacing: 0.03em;
  font-style: italic;
}

/* ===== 中部 ===== */
.card-center {
  flex: 1;
  display: flex;
  padding: 12px 14px 10px;
  gap: 10px;
  min-height: 0;
}

/* 左侧 • 天赋标签 40%（原30% + 10%） */
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

/* 右侧 • Q版形象 60%，放大20%，居中偏下 */
.center-right {
  flex: 0 0 60%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.avatar-img {
  width: 100%;
  max-width: 288px;  /* 原240px * 1.2 = 288px，放大20% */
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

/* ===== 底部 ===== */
.card-bottom {
  padding: 12px 16px;
  border-top: 1.5px solid;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.5);
}

/* 一句话概括：大字号，书法体，阴影 */
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

/* 天赋关键词：中等字号，" · " 分隔一字排开居中 */
.keyword-line {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0;
}

.kw-item {
  font-size: clamp(0.65rem, 2.8vw, 0.78rem);
  font-weight: 600;
  color: #475569;
  white-space: nowrap;
}

.kw-sep {
  color: #C9A96E;
  font-weight: 700;
  margin: 0 2px;
}

/* 历史人物：两列并排居中，小字号低不透明度 */
.history-row {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.history-figure {
  display: flex;
  align-items: baseline;
  gap: 4px;
  font-size: clamp(0.55rem, 2.4vw, 0.7rem);
  color: #94A3B8;
  opacity: 0.8;
  white-space: nowrap;
  line-height: 1.4;
}

.fig-bullet {
  font-weight: 700;
  font-size: 1.1em;
  line-height: 1;
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
  .card-bottom { padding: 10px 12px; gap: 6px; }
  .history-row { gap: 10px; }
}

@media (min-width: 1024px) {
  .card-top { padding: 16px 24px; }
  .card-center { padding: 16px 20px 12px; gap: 14px; }
  .center-left { flex: 0 0 38%; }
  .center-right { flex: 0 0 62%; }
  .talent-tag-item { padding: 8px 14px; border-radius: 12px; }
  .avatar-img { max-width: 320px; }
  .card-bottom { padding: 14px 20px 16px; gap: 10px; }
}
</style>