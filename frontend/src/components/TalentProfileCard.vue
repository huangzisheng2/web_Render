<template>
  <div class="talent-card" :style="cardStyle">
    <!-- 顶部：姓名 + 潜在天赋档案 -->
    <div class="card-top">
      <span class="top-name">{{ displayName }}</span>
      <span class="top-title">的潜在天赋档案</span>
    </div>

    <!-- 中间：左侧标签 + 右侧头像 -->
    <div class="card-center">
      <!-- 左侧天赋标签 -->
      <div class="center-left">
        <div
          v-for="(tag, i) in displayTags"
          :key="i"
          class="talent-tag-item"
          :style="{ borderColor: traitInfo.color + '50', background: traitInfo.color + '08' }"
        >
          <span class="tag-emoji">{{ tagEmojis[i] }}</span>
          <span class="tag-label">{{ tag }}</span>
        </div>
      </div>

      <!-- 右侧 Q版形象 -->
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

    <!-- 底部：特质 + 关键词横向 + 日柱 -->
    <div class="card-bottom" :style="{ background: traitInfo.color + '08', borderTopColor: traitInfo.color + '20' }">
      <div class="bottom-left">
        <p class="trait-text">{{ traitInfo.description }}</p>
      </div>
      <div class="bottom-right">
        <div class="day-column-label" :style="{ color: traitInfo.color }">
          <span class="dc-badge" :style="{ background: traitInfo.color }">{{ dayPillar || (dayMaster + traitInfo.element) }}</span>
        </div>
        <p class="day-column-desc">{{ dayColumnText }}</p>
      </div>
    </div>
    <!-- 关键词横向等距行 -->
    <div v-if="displayKeywords.length" class="keyword-row" :style="{ borderTopColor: traitInfo.color + '15' }">
      <span
        v-for="(kw, i) in displayKeywords"
        :key="i"
        class="kw-item"
        :style="{ color: traitInfo.color }"
      >{{ kw }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getDayMasterTrait, getFullAvatarUrl, getDayColumnSummary } from '../data/dayMasterData'

const props = defineProps({
  name: { type: String, default: '探索者' },
  dayMaster: { type: String, default: '甲' },
  dayPillar: { type: String, default: '' },
  gender: { type: String, default: 'male' },
  talentTags: { type: Array, default: () => [] },
  talentSummary: { type: String, default: '' },
  keywords: { type: Array, default: () => [] },
  dayColumnSummary: { type: String, default: '' },
  traitDescription: { type: String, default: '' }
})

const avatarError = ref(false)
const displayName = computed(() => props.name)

const traitInfo = computed(() => getDayMasterTrait(props.dayMaster, props.gender))

const avatarUrl = computed(() => {
  if (avatarError.value) return ''
  return getFullAvatarUrl(props.dayMaster, props.gender)
})

const displayTags = computed(() => props.talentTags?.length ? props.talentTags.slice(0, 5) : [])
const displayKeywords = computed(() => props.keywords?.length ? props.keywords.slice(0, 5) : [])
const dayColumnText = computed(() => props.dayColumnSummary || getDayColumnSummary(props.dayPillar) || '')

const tagEmojis = ['✨', '🌟', '💫', '🔥', '💎']

const cardStyle = computed(() => ({
  '--card-accent': traitInfo.value.color || '#8EC5FC'
}))
</script>

<style scoped>
.talent-card {
  width: 100%;
  border-radius: 16px;
  background: #fff;
  border: 1px solid rgba(142,197,252,0.12);
  box-shadow: 0 2px 16px rgba(142,197,252,0.06);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* ===== 顶部 ===== */
.card-top {
  padding: 14px 18px;
  text-align: center;
  border-bottom: 1px solid rgba(142,197,252,0.06);
}
.top-name { font-size: clamp(1.05rem,4.5vw,1.25rem); font-weight: 800; color: #1E293B; letter-spacing: .03em; }
.top-title { font-size: clamp(0.8rem,3.5vw,0.95rem); font-weight: 500; color: var(--card-accent); letter-spacing: .05em; }

/* ===== 中间：标签 + 头像 ===== */
.card-center {
  display: flex;
  padding: 14px 14px 10px;
  gap: 10px;
  min-height: 0;
}

/* 左侧标签 25% */
.center-left {
  flex: 0 0 25%;
  display: flex;
  flex-direction: column;
  gap: 5px;
  justify-content: center;
}
.talent-tag-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 8px;
  border-radius: 8px;
  border-left: 3px solid;
  font-size: clamp(0.6rem,2.6vw,0.7rem);
  font-weight: 600;
  color: #334155;
}
.tag-emoji { font-size: clamp(0.8rem,3vw,0.9rem); flex-shrink: 0; }
.tag-label { line-height: 1.2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* 右侧头像 75%（更大，无圆角框） */
.center-right {
  flex: 0 0 75%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.avatar-img {
  width: 92%;
  max-width: 280px;
  aspect-ratio: 3/4;
  object-fit: contain;
  background: #f8fafc;
  border-radius: 0;
}
.avatar-placeholder {
  width: 92%; max-width: 280px; aspect-ratio: 3/4;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
  border-radius: 0;
}
.placeholder-char { font-size: 44px; font-weight: 800; }
.placeholder-el { font-size: 16px; font-weight: 600; opacity: .7; }

/* ===== 底部：特质 + 日柱 ===== */
.card-bottom {
  display: flex;
  padding: 10px 14px;
  gap: 10px;
  border-top: 1.5px solid;
}
.bottom-left { flex: 1; min-width: 0; }
.trait-text {
  font-size: clamp(0.65rem,2.8vw,0.75rem);
  color: #4A5568; line-height: 1.5; margin: 0;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.bottom-right { flex: 0 0 48%; min-width: 0; }
.day-column-label { display: flex; align-items: center; gap: 6px; font-size: clamp(0.6rem,2.6vw,0.7rem); font-weight: 700; margin-bottom: 3px; }
.dc-badge { padding: 2px 8px; border-radius: 10px; font-size: clamp(0.55rem,2.3vw,0.65rem); color: #fff; white-space: nowrap; }
.day-column-desc {
  font-size: clamp(0.6rem,2.5vw,0.7rem); color: #64748B; line-height: 1.5; margin: 0;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}

/* ===== 关键词横向等距行 ===== */
.keyword-row {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 8px 10px;
  border-top: 1px solid;
}
.kw-item {
  font-size: clamp(0.7rem,3vw,0.85rem);
  font-weight: 700;
  letter-spacing: .04em;
  text-align: center;
  flex: 1;
}

/* ===== 响应式 ===== */
@media (max-width: 640px) {
  .card-top { padding: 10px 12px; }
  .card-center { padding: 10px 10px 6px; gap: 6px; }
  .center-left { flex: 0 0 22%; }
  .center-right { flex: 0 0 78%; }
  .avatar-img { width: 95%; max-width: 200px; }
  .card-bottom { padding: 8px 10px; gap: 6px; flex-wrap: wrap; }
  .bottom-left { flex: 0 0 100%; }
  .bottom-right { flex: 0 0 100%; }
  .keyword-row { padding: 6px 6px; gap: 2px; }
  .kw-item { font-size: clamp(0.6rem,2.5vw,0.75rem); }
}
@media (min-width: 1024px) {
  .card-top { padding: 16px 22px; }
  .card-center { padding: 18px 22px 12px; gap: 14px; }
  .center-left { flex: 0 0 22%; }
  .center-right { flex: 0 0 78%; }
  .avatar-img { width: 88%; max-width: 300px; }
  .talent-tag-item { padding: 6px 12px; }
  .card-bottom { padding: 12px 22px; }
  .keyword-row { padding: 10px 16px; }
}
</style>
