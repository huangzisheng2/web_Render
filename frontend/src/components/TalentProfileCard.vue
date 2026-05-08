<template>
  <div class="talent-card" :style="cardStyle">
    <!-- 顶部 10%：姓名 + 潜在天赋档案 + 日柱 -->
    <div class="card-top">
      <span class="top-name">{{ displayName }}</span>
      <span class="top-title">的潜在天赋档案</span>
      <span class="top-divider"></span>
      <span class="top-daypillar">{{ dayPillar || (dayMaster + traitInfo.element) }}</span>
    </div>

    <!-- 中间 75%：左侧标签(30%) + 右侧头像(70%) -->
    <div class="card-center">
      <!-- 左侧 30%：天赋标签 -->
      <div class="center-left">
        <div class="tag-scroll">
          <div
            v-for="(tag, i) in displayTags"
            :key="i"
            class="talent-tag-item"
            :style="{ borderColor: traitInfo.color + '50', background: traitInfo.color + '08' }"
          >
            <span class="tag-emoji">{{ tagEmojis[i] }}</span>
            <span class="tag-label">{{ tag }}</span>
            <span class="tag-desc" v-if="tagDescriptions[i]">{{ tagDescriptions[i] }}</span>
          </div>
        </div>
      </div>

      <!-- 右侧 70%：Q版形象（无圆角框，原比例） -->
      <div class="center-right">
        <img
          v-if="avatarUrl"
          :src="avatarUrl"
          alt="Q版形象"
          class="avatar-img"
          @error="avatarError = true"
        />
        <div v-else class="avatar-placeholder" :style="{ background: traitInfo.color + '15', color: traitInfo.color }">
          <span class="placeholder-char">{{ dayMaster }}</span>
          <span class="placeholder-el">{{ traitInfo.element }}</span>
        </div>
      </div>
    </div>

    <!-- 底部：特质 + 关键词 + 历史人物 -->
    <div class="card-bottom" :style="{ background: `linear-gradient(135deg, ${traitInfo.color}08, ${traitInfo.color}02)`, borderTopColor: traitInfo.color + '15' }">
      <!-- 第一行：特质概括（大字体） -->
      <p class="trait-text">{{ traitDescription || traitInfo.description }}</p>

      <!-- 第二行：五个天赋关键词横向等距 -->
      <div class="keyword-row" v-if="displayKeywords.length">
        <span
          v-for="(kw, i) in displayKeywords"
          :key="i"
          class="keyword-item"
          :style="{ color: traitInfo.color, background: traitInfo.color + '12' }"
        >{{ kw }}</span>
      </div>

      <!-- 第三行：历史人物两列排布 -->
      <div class="history-row" v-if="historicalFigures.length">
        <div
          v-for="(figure, i) in historicalFigures"
          :key="i"
          class="history-figure"
          :style="{ borderColor: traitInfo.color + '20' }"
        >
          <span class="figure-name">{{ figure.name }}</span>
          <span class="figure-title">{{ figure.title }}</span>
          <p class="figure-quote">{{ figure.quote }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getDayMasterTrait, getFullAvatarUrl } from '../data/dayMasterData'

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
const dayPillarLabel = computed(() => {
  if (props.dayPillar) return props.dayPillar
  return props.dayMaster + (traitInfo.value.element || '')
})

const traitInfo = computed(() => {
  return getDayMasterTrait(props.dayMaster, props.gender)
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

const tagEmojis = ['✨', '🌟', '💫', '🔥', '💎']

// 每个天赋标签配前25字说明
const tagDescriptions = computed(() => {
  const summary = props.talentSummary || ''
  if (!summary) return []
  // 按标点分割取段落
  const parts = summary.split(/[。！？]/).filter(s => s.trim())
  return parts.slice(0, 5).map(p => p.trim().slice(0, 25))
})

const cardStyle = computed(() => ({
  '--card-accent': traitInfo.value.color || '#8EC5FC'
}))
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
}

/* ===== 顶部 ===== */
.card-top {
  padding: 14px 18px;
  text-align: center;
  border-bottom: 1px solid rgba(142, 197, 252, 0.06);
}

.top-name {
  font-size: clamp(1.05rem, 4.8vw, 1.3rem);
  font-weight: 800;
  color: #1E293B;
  letter-spacing: 0.04em;
}

.top-title {
  font-size: clamp(0.8rem, 3.8vw, 0.95rem);
  font-weight: 500;
  color: var(--card-accent);
  letter-spacing: 0.04em;
}

.top-divider {
  display: inline-block;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--card-accent);
  margin: 0 8px 3px;
  opacity: 0.4;
}

.top-daypillar {
  font-size: clamp(0.7rem, 3vw, 0.8rem);
  font-weight: 600;
  color: var(--card-accent);
  opacity: 0.7;
}

/* ===== 中间 75% ===== */
.card-center {
  flex: 1;
  display: flex;
  padding: 12px 14px 10px;
  gap: 10px;
  min-height: 0;
}

.center-left {
  flex: 0 0 30%;
  display: flex;
  flex-direction: column;
  gap: 5px;
  justify-content: center;
}

.tag-scroll {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.talent-tag-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  padding: 5px 8px;
  border-radius: 8px;
  border-left: 3px solid;
  font-size: clamp(0.6rem, 2.8vw, 0.72rem);
  font-weight: 600;
  color: #334155;
  line-height: 1.2;
}

.tag-emoji {
  font-size: clamp(0.75rem, 3.2vw, 0.9rem);
  flex-shrink: 0;
}

.tag-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-desc {
  width: 100%;
  font-size: clamp(0.5rem, 2.2vw, 0.6rem);
  font-weight: 400;
  color: #94A3B8;
  line-height: 1.3;
  padding-left: 2px;
}

.center-right {
  flex: 0 0 70%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-img {
  width: 100%;
  max-width: 240px;
  height: auto;
  aspect-ratio: auto;
  object-fit: contain;
  background: transparent;
}

.avatar-placeholder {
  width: 80%;
  max-width: 200px;
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
  padding: 12px 16px 14px;
  border-top: 1px solid;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trait-text {
  font-size: clamp(0.75rem, 3.2vw, 0.85rem);
  font-weight: 600;
  color: #334155;
  line-height: 1.5;
  margin: 0;
  text-align: center;
}

/* 关键词横向等距 */
.keyword-row {
  display: flex;
  justify-content: space-around;
  gap: 6px;
  flex-wrap: wrap;
}

.keyword-item {
  padding: 3px 14px;
  border-radius: 16px;
  font-size: clamp(0.6rem, 2.6vw, 0.7rem);
  font-weight: 600;
  white-space: nowrap;
}

/* 历史人物两列 */
.history-row {
  display: flex;
  gap: 10px;
}

.history-figure {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid;
  border-radius: 10px;
  background: rgba(255,255,255,0.7);
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.figure-name {
  font-size: clamp(0.65rem, 2.8vw, 0.75rem);
  font-weight: 700;
  color: var(--card-accent);
}

.figure-title {
  font-size: clamp(0.5rem, 2.2vw, 0.6rem);
  color: #94A3B8;
}

.figure-quote {
  font-size: clamp(0.5rem, 2.2vw, 0.6rem);
  color: #64748B;
  line-height: 1.4;
  margin: 2px 0 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ===== 响应式 ===== */
@media (max-width: 640px) {
  .card-top { padding: 10px 12px; }
  .card-center { padding: 10px 10px 8px; gap: 8px; }
  .center-left { flex: 0 0 28%; }
  .center-right { flex: 0 0 72%; }
  .avatar-img { max-width: 180px; }
  .card-bottom { padding: 10px 12px 12px; gap: 6px; }
  .history-row { flex-direction: column; gap: 6px; }
}

@media (min-width: 1024px) {
  .card-top { padding: 16px 24px; }
  .card-center { padding: 16px 20px 12px; gap: 14px; }
  .talent-tag-item { padding: 7px 12px; border-radius: 10px; }
  .avatar-img { max-width: 260px; }
  .card-bottom { padding: 14px 20px 16px; }
}
</style>
