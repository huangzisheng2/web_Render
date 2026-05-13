<template>
  <div class="talent-card">

    <!-- ===== 顶部 20%：标题 + 日柱·身份 + 日柱描述 ===== -->
    <div class="card-top">
      <div class="title-row">
        <span class="top-name">{{ displayName }}</span>
        <span class="top-title">的潜在天赋档案</span>
      </div>
      <!-- 日柱行：五行符号(高亮) + 日柱(高亮) + · + 身份(五行色) -->
      <div class="daypillar-line">
        <span class="dp-element-icon" :style="{ color: traitInfo.color }">{{ elementSymbol }}</span>
        <span class="dp-label" :style="{ color: traitInfo.color }">{{ dayPillarLabel }}</span>
        <span class="dp-sep">·</span>
        <span class="dp-identity" :style="{ color: traitInfo.color }">{{ dayColumnIdentity }}</span>
      </div>
      <!-- 日柱描述：恢复原来格式，居中偏左对齐 -->
      <p class="day-column-text" v-if="dayColumnDescription">{{ dayColumnDescription }}</p>
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
        </div>
      </div>

      <div class="center-right">
        <!-- 日柱概述 + Q版头像统一宽度包裹 -->
        <div class="avatar-wrapper">
          <p
            v-if="dayPillarSummary"
            class="daypillar-summary-art"
            :style="{ color: traitInfo.color }"
          >{{ dayPillarSummary }}</p>
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
    </div>

    <!-- ===== 底部：概括语 + 双列布局 ===== -->
    <div
      class="card-bottom"
      :style="{ borderTopColor: traitInfo.color + '15' }"
    >
      <!-- 一句话概括：正楷加粗毛笔字体 -->
      <p class="trait-text" :style="{ textShadow: `0 2px 8px ${traitInfo.color}20` }">
        {{ traitDescription || traitInfo.description }}
      </p>

      <!-- 双列布局：天赋关键词 | 历史人物画像 -->
      <div class="bottom-columns" v-if="displayKeywords.length || displayHistoricalFigures.length">
        <!-- 左列：天赋关键词 -->
        <div class="bottom-col left-col" v-if="displayKeywords.length">
          <div class="col-title"><span class="col-icon">💎</span>天赋关键词</div>
          <div class="keyword-pills">
            <span
              v-for="(kw, i) in displayKeywords"
              :key="i"
              class="kw-pill"
            >{{ kw }}</span>
          </div>
        </div>

        <!-- 右列：历史人物画像 -->
        <div class="bottom-col right-col" v-if="displayHistoricalFigures.length">
          <div class="col-title"><span class="col-icon">📜</span>历史人物画像</div>
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
import { getDayMasterTrait, getFullAvatarUrl, DAY_PILLAR_SUMMARIES, getDayColumnIdentity, getDayColumnDescription } from '../data/dayMasterData'

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

// 五行符号
const elementSymbol = computed(() => {
  const map = { '木': '🌲', '火': '🔥', '土': '⛰️', '金': '⚔️', '水': '💧' }
  return map[traitInfo.value.element] || '✨'
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
  return ''
})

// 日柱身份（六十日柱数据库）
const dayColumnIdentity = computed(() => {
  if (props.dayPillar) {
    return getDayColumnIdentity(props.dayPillar, props.gender)
  }
  return ''
})

// 日柱描述（六十日柱数据库）
const dayColumnDescription = computed(() => {
  if (props.dayPillar) {
    return getDayColumnDescription(props.dayPillar, props.gender)
  }
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

// 天赋关键词（最多5个），清理"天赋关键词"前缀和*号
const displayKeywords = computed(() => {
  return (props.keywords || [])
    .map(kw => kw.replace(/\*+/g, '').replace(/^天赋关键词[：:\s]*/g, '').trim())
    .filter(Boolean)
    .slice(0, 5)
})

// 历史人物（最多2个），清理*号
const displayHistoricalFigures = computed(() => {
  return (props.historicalFigures || [])
    .map(f => ({
      name: (f.name || '').replace(/\*+/g, '').trim(),
      title: (f.title || '').replace(/\*+/g, '').trim()
    }))
    .slice(0, 2)
})

// 固定天赋图标
const tagEmojis = ['💡', '🔍', '⚖️', '👑', '💜']
</script>

<style scoped>
.talent-card {
  width: 100%;
  max-width: 100vw;
  border-radius: 18px;
  background: linear-gradient(145deg, #ffffff 0%, #FAFBFC 100%);
  border: 1px solid rgba(142, 197, 252, 0.12);
  box-shadow: 0 4px 20px rgba(142, 197, 252, 0.06);
  overflow: hidden;
  display: -webkit-box;
  display: -webkit-flex;
  display: flex;
  -webkit-box-orient: vertical;
  -webkit-box-direction: normal;
  -webkit-flex-direction: column;
  flex-direction: column;
  font-family: -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", "WenQuanYi Micro Hei", "STSong", "Noto Serif SC", sans-serif;
  color: #1E293B;
  box-sizing: border-box;
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
  gap: 5px;
  flex-wrap: wrap;
}

.dp-element-icon {
  font-size: clamp(0.95rem, 4vw, 1.15rem);
  flex-shrink: 0;
}

.dp-label {
  font-size: clamp(0.95rem, 4vw, 1.15rem);
  font-weight: 800;
  font-family: "STKaiti", "KaiTi", "Noto Serif SC", serif;
  letter-spacing: 0.06em;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.dp-sep {
  font-size: clamp(0.8rem, 3.2vw, 0.95rem);
  color: #C9A96E;
  font-weight: 600;
}

.dp-identity {
  font-size: clamp(0.95rem, 4vw, 1.15rem);
  font-weight: 800;
  font-family: "STKaiti", "KaiTi", "Noto Serif SC", serif;
  letter-spacing: 0.06em;
}

/* 日柱描述：恢复原来格式（黑体书法风格），居中偏左对齐 */
.day-column-text {
  margin: 6px 0 0;
  padding: 0 8px;
  font-size: clamp(0.62rem, 2.6vw, 0.75rem);
  font-weight: 600;
  font-family: "STHeiti", "SimHei", "STKaiti", "KaiTi", "Noto Serif SC", serif;
  color: #475569;
  line-height: 1.6;
  text-align: left;
  letter-spacing: 0.02em;
}

/* 日柱概述：始终在图片顶部，宽度=图片宽度，居中横向排版 */
.daypillar-summary-art {
  margin: 0 0 8px;
  padding: 0 4px;
  width: 100%;
  box-sizing: border-box;
  font-size: clamp(0.7rem, 3vw, 0.85rem);
  font-weight: 700;
  font-family: "STXingkai", "STKaiti", "KaiTi", "Noto Serif SC", serif;
  font-style: italic;
  line-height: 1.5;
  text-align: center;
  letter-spacing: 0.04em;
  text-shadow: 0 1px 6px currentColor;
  opacity: 0.9;
  word-break: keep-all;
  overflow-wrap: break-word;
}

/* ===== 中部 ===== */
.card-center {
  flex: 1;
  display: -webkit-box;
  display: -webkit-flex;
  display: flex;
  padding: 12px 14px 10px;
  gap: 10px;
  min-height: 0;
  box-sizing: border-box;
}
/* flex gap 兜底（不支持 gap 的浏览器用 margin） */
@supports not (gap: 10px) {
  .card-center > * + * { margin-left: 10px; }
}

/* 左侧 · 天赋标签 40% */
.center-left {
  flex: 0 0 40%;
  display: -webkit-box;
  display: -webkit-flex;
  display: flex;
  -webkit-box-orient: vertical;
  -webkit-box-direction: normal;
  -webkit-flex-direction: column;
  flex-direction: column;
  gap: 6px;
  -webkit-box-pack: center;
  -webkit-justify-content: center;
  justify-content: center;
  min-width: 0;
  box-sizing: border-box;
}
@supports not (gap: 6px) {
  .center-left > * + * { margin-top: 6px; }
}

.talent-tag-item {
  padding: 6px 10px;
  border-radius: 10px;
  border-left: 3px solid;
  line-height: 1.2;
  box-sizing: border-box;
  min-height: 44px;
  display: -webkit-box;
  display: -webkit-flex;
  display: flex;
  -webkit-box-align: center;
  -webkit-align-items: center;
  align-items: center;
}

.tag-upper {
  display: -webkit-box;
  display: -webkit-flex;
  display: flex;
  -webkit-box-align: center;
  -webkit-align-items: center;
  align-items: center;
  gap: 5px;
  width: 100%;
  box-sizing: border-box;
}
@supports not (gap: 5px) {
  .tag-upper > * + * { margin-left: 5px; }
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

/* 右侧 · Q版形象 60% */
.center-right {
  flex: 0 0 60%;
  display: -webkit-box;
  display: -webkit-flex;
  display: flex;
  -webkit-box-align: start;
  -webkit-align-items: flex-start;
  align-items: flex-start;
  -webkit-box-pack: center;
  -webkit-justify-content: center;
  justify-content: center;
  box-sizing: border-box;
}

/* 头像包裹：文字 + 图片统一宽度，居中对齐，始终绑定 */
.avatar-wrapper {
  display: -webkit-box;
  display: -webkit-flex;
  display: flex;
  -webkit-box-orient: vertical;
  -webkit-box-direction: normal;
  -webkit-flex-direction: column;
  flex-direction: column;
  -webkit-box-align: center;
  -webkit-align-items: center;
  align-items: center;
  width: 100%;
  max-width: 288px;
  box-sizing: border-box;
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

/* ===== 底部 ===== */
.card-bottom {
  padding: 12px 16px;
  border-top: 1.5px solid;
  display: -webkit-box;
  display: -webkit-flex;
  display: flex;
  -webkit-box-orient: vertical;
  -webkit-box-direction: normal;
  -webkit-flex-direction: column;
  flex-direction: column;
  -webkit-box-align: center;
  -webkit-align-items: center;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.5);
  box-sizing: border-box;
}
@supports not (gap: 10px) {
  .card-bottom > * + * { margin-top: 10px; }
}

/* 一句话概括：正楷加粗毛笔字体 */
.trait-text {
  margin: 0;
  font-size: clamp(0.9rem, 4vw, 1.1rem);
  font-weight: 900;
  font-family: "STXingkai", "STKaiti", "KaiTi", "Noto Serif SC", serif;
  color: #334155;
  text-align: center;
  line-height: 1.6;
  letter-spacing: 0.06em;
  word-break: break-word;
}

/* 双列布局 */
.bottom-columns {
  display: -webkit-box;
  display: -webkit-flex;
  display: flex;
  width: 100%;
  gap: 16px;
  box-sizing: border-box;
}
@supports not (gap: 16px) {
  .bottom-columns > * + * { margin-left: 16px; }
}

.bottom-col {
  -webkit-box-flex: 1;
  -webkit-flex: 1;
  flex: 1;
  min-width: 0;
  box-sizing: border-box;
}

.col-title {
  font-size: clamp(0.65rem, 2.8vw, 0.78rem);
  font-weight: 700;
  color: #1E293B;
  margin-bottom: 6px;
  letter-spacing: 0.03em;
}

.col-icon {
  display: inline-block;
  margin-right: 4px;
  font-size: clamp(0.75rem, 3vw, 0.9rem);
  vertical-align: middle;
}

/* 左列：天赋关键词 pill 按钮 */
.keyword-pills {
  display: -webkit-box;
  display: -webkit-flex;
  display: flex;
  -webkit-flex-wrap: wrap;
  flex-wrap: wrap;
  gap: 6px;
  box-sizing: border-box;
}
@supports not (gap: 6px) {
  .keyword-pills > * { margin: 3px; }
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
  box-sizing: border-box;
}

/* 右列：历史人物画像 */
.history-list {
  display: -webkit-box;
  display: -webkit-flex;
  display: flex;
  -webkit-box-orient: vertical;
  -webkit-box-direction: normal;
  -webkit-flex-direction: column;
  flex-direction: column;
  gap: 4px;
  box-sizing: border-box;
}
@supports not (gap: 4px) {
  .history-list > * + * { margin-top: 4px; }
}

.history-figure {
  display: -webkit-box;
  display: -webkit-flex;
  display: flex;
  -webkit-box-align: baseline;
  -webkit-align-items: baseline;
  align-items: baseline;
  gap: 4px;
  font-size: clamp(0.55rem, 2.4vw, 0.7rem);
  color: #1E293B;
  line-height: 1.4;
  box-sizing: border-box;
}

.fig-bullet {
  font-weight: 700;
  font-size: 1.1em;
  line-height: 1;
  flex-shrink: 0;
}

.fig-text {
  color: #1E293B;
  letter-spacing: 0.02em;
}

/* ===== 响应式 ===== */

/* ---------- 超小屏 ≤360px（iPhone SE / 小安卓） ---------- */
@media (max-width: 360px) {
  .talent-card { border-radius: 12px; }
  .card-top { padding: 8px 10px; }
  .card-center {
    padding: 8px 6px 6px;
    -webkit-flex-wrap: wrap;
    flex-wrap: wrap;
    gap: 6px;
  }
  .center-left {
    flex: 0 0 100%;
    -webkit-box-orient: horizontal;
    -webkit-box-direction: normal;
    -webkit-flex-direction: row;
    flex-direction: row;
    -webkit-flex-wrap: wrap;
    flex-wrap: wrap;
    gap: 4px;
    justify-content: flex-start;
  }
  .center-right {
    flex: 0 0 100%;
    justify-content: center;
  }
  .talent-tag-item {
    padding: 4px 8px;
    border-radius: 8px;
    border-left-width: 2px;
    min-height: 36px;
  }
  .tag-label { font-size: 0.65rem; max-width: 80px; }
  .tag-emoji { font-size: 0.75rem; }
  .avatar-wrapper { max-width: 180px; }
  .avatar-img { max-width: 180px; }
  .avatar-placeholder { max-width: 140px; }
  .daypillar-summary-art { font-size: 0.62rem; margin-bottom: 4px; }
  .day-column-text { font-size: 0.58rem; }
  .card-bottom { padding: 8px 10px; gap: 6px; }
  .trait-text { font-size: 0.78rem; }
  .bottom-columns {
    -webkit-box-orient: vertical;
    -webkit-box-direction: normal;
    -webkit-flex-direction: column;
    flex-direction: column;
    gap: 8px;
  }
  .col-title { font-size: 0.6rem; }
  .col-icon { font-size: 0.7rem; }
  .kw-pill { font-size: 0.52rem; padding: 2px 8px; }
  .history-figure { font-size: 0.52rem; }
}

/* ---------- 小屏 361-640px（主流手机） ---------- */
@media (min-width: 361px) and (max-width: 640px) {
  .card-top { padding: 10px 12px; }
  .card-center { padding: 10px 8px 8px; gap: 8px; }
  .center-left { flex: 0 0 42%; }
  .center-right { flex: 0 0 58%; }
  .avatar-wrapper { max-width: 220px; }
  .avatar-img { max-width: 220px; }
  .card-bottom { padding: 10px 12px; gap: 8px; }
  .bottom-columns { gap: 10px; }
}

/* ---------- 平板 641-1023px ---------- */
@media (min-width: 641px) and (max-width: 1023px) {
  .card-center { padding: 14px 16px 12px; gap: 12px; }
  .center-left { flex: 0 0 38%; }
  .center-right { flex: 0 0 62%; }
  .avatar-wrapper { max-width: 260px; }
  .avatar-img { max-width: 260px; }
  .talent-tag-item { padding: 7px 12px; }
  .card-bottom { padding: 12px 16px; gap: 10px; }
}

/* ---------- 桌面 ≥1024px ---------- */
@media (min-width: 1024px) {
  .card-top { padding: 16px 24px; }
  .card-center { padding: 16px 20px 12px; gap: 14px; }
  .center-left { flex: 0 0 38%; }
  .center-right { flex: 0 0 62%; }
  .talent-tag-item { padding: 8px 14px; border-radius: 12px; }
  .avatar-wrapper { max-width: 320px; }
  .avatar-img { max-width: 320px; }
  .card-bottom { padding: 14px 20px 16px; gap: 12px; }
  .bottom-columns { gap: 20px; }
}

/* ---------- iOS 安全区适配（刘海屏/灵动岛） ---------- */
@supports (padding-top: env(safe-area-inset-top)) {
  .talent-card {
    padding-left: env(safe-area-inset-left, 0px);
    padding-right: env(safe-area-inset-right, 0px);
  }
}

/* ---------- QQ/微信内置浏览器兼容 ---------- */
/* 微信/QQ 浏览器对某些 CSS 属性支持不完整，做降级处理 */
@media screen and (-webkit-min-device-pixel-ratio: 2) {
  /* 在高分屏（大部分手机）上确保图片清晰 */
  .avatar-img { image-rendering: -webkit-optimize-contrast; }
}

/* 针对不支持 clamp() 的旧浏览器降级 */
@supports not (font-size: clamp(1rem, 1vw, 1rem)) {
  .top-name { font-size: 1.35rem; }
  .top-title { font-size: 0.9rem; }
  .dp-label, .dp-identity, .dp-element-icon { font-size: 1.05rem; }
  .day-column-text { font-size: 0.68rem; }
  .daypillar-summary-art { font-size: 0.78rem; }
  .tag-label { font-size: 0.75rem; }
  .tag-emoji { font-size: 0.9rem; }
  .trait-text { font-size: 1rem; }
  .col-title { font-size: 0.7rem; }
  .kw-pill { font-size: 0.6rem; }
  .history-figure { font-size: 0.6rem; }
}
</style>
