<template>
  <div class="talent-card" :style="cardStyle">
    <!-- 顶部 10%：姓名 + 潜在天赋档案 -->
    <div class="card-top">
      <span class="top-name">{{ displayName }}</span>
      <span class="top-title">的潜在天赋档案</span>
    </div>

    <!-- 中间 70%：左侧标签 + 右侧头像 -->
    <div class="card-center">
      <!-- 左侧 30%：天赋标签 -->
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
        <p class="talent-summary">{{ talentSummary }}</p>
      </div>

      <!-- 右侧 70%：Q版形象（原图原比例） -->
      <div class="center-right">
        <div class="avatar-frame" :style="{ borderColor: traitInfo.color + '30', boxShadow: `0 8px 32px ${traitInfo.color}20` }">
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
    </div>

    <!-- 底部 20%：特质 + 关键词 + 日柱 -->
    <div class="card-bottom" :style="{ background: traitInfo.color + '08', borderTopColor: traitInfo.color + '20' }">
      <div class="bottom-left">
        <p class="trait-text">{{ traitInfo.description }}</p>
        <div class="keyword-tags">
          <span
            v-for="(kw, i) in displayKeywords"
            :key="i"
            class="keyword-pill"
            :style="{ background: traitInfo.color + '18', color: traitInfo.color }"
          >
            {{ kw }}
          </span>
        </div>
      </div>
      <div class="bottom-right">
        <div class="day-column-label" :style="{ color: traitInfo.color }">
          <span class="dc-badge" :style="{ background: traitInfo.color }">{{ dayMaster }}{{ traitInfo.element }}</span>
          日柱特质
        </div>
        <p class="day-column-desc">{{ dayColumnText }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getDayMasterTrait, getFullAvatarUrl, getDayColumnSummary, ELEMENT_SYMBOLS } from '../data/dayMasterData'

const props = defineProps({
  name: { type: String, default: '探索者' },
  dayMaster: { type: String, default: '甲' },
  gender: { type: String, default: 'male' },
  talentTags: { type: Array, default: () => [] },
  talentSummary: { type: String, default: '' },
  keywords: { type: Array, default: () => [] },
  dayColumnSummary: { type: String, default: '' },
  traitDescription: { type: String, default: '' }
})

const avatarError = ref(false)

const displayName = computed(() => props.name)

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
  return props.keywords?.length ? props.keywords.slice(0, 3) : []
})

// 日柱特质：优先用 prop，降级到前端原生数据
const dayColumnText = computed(() => {
  return props.dayColumnSummary || getDayColumnSummary(props.dayMaster, props.gender) || ''
})

const tagEmojis = ['✨', '🌟', '💫', '🔥', '💎']

const cardStyle = computed(() => ({
  '--card-accent': traitInfo.value.color || '#8EC5FC'
}))
</script>

<style scoped>
.talent-card {
  width: 100%;
  border-radius: 20px;
  background: linear-gradient(145deg, #ffffff 0%, #FAFBFC 100%);
  border: 1px solid rgba(142, 197, 252, 0.15);
  box-shadow: 0 4px 24px rgba(142, 197, 252, 0.08);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* ===== 顶部 10% ===== */
.card-top {
  padding: 16px 20px;
  text-align: center;
  border-bottom: 1px solid rgba(142, 197, 252, 0.08);
}

.top-name {
  font-size: clamp(1.1rem, 5vw, 1.35rem);
  font-weight: 800;
  color: #1E293B;
  letter-spacing: 0.04em;
}

.top-title {
  font-size: clamp(0.85rem, 4vw, 1rem);
  font-weight: 500;
  color: var(--card-accent);
  letter-spacing: 0.06em;
}

/* ===== 中间 70% ===== */
.card-center {
  flex: 1;
  display: flex;
  padding: 16px 16px 12px;
  gap: 12px;
  min-height: 0;
}

/* 左侧 30% */
.center-left {
  flex: 0 0 30%;
  display: flex;
  flex-direction: column;
  gap: 6px;
  justify-content: center;
}

.talent-tag-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 10px;
  border-left: 3px solid;
  font-size: clamp(0.65rem, 3vw, 0.75rem);
  font-weight: 600;
  color: #334155;
}

.tag-emoji {
  font-size: clamp(0.85rem, 3.5vw, 1rem);
  flex-shrink: 0;
}

.tag-label {
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.talent-summary {
  font-size: clamp(0.6rem, 2.5vw, 0.7rem);
  color: #718096;
  line-height: 1.5;
  margin: 4px 0 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 右侧 70% */
.center-right {
  flex: 0 0 70%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-frame {
  width: 90%;
  max-width: 220px;
  aspect-ratio: 3 / 4;
  border-radius: 20px;
  border: 2.5px solid;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #f8fafc;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.placeholder-char { font-size: 40px; font-weight: 800; }
.placeholder-el { font-size: 14px; font-weight: 600; opacity: 0.7; }

/* ===== 底部 20% ===== */
.card-bottom {
  display: flex;
  padding: 12px 16px;
  gap: 12px;
  border-top: 1.5px solid;
}

.bottom-left {
  flex: 1;
  min-width: 0;
}

.trait-text {
  font-size: clamp(0.65rem, 2.8vw, 0.75rem);
  color: #4A5568;
  line-height: 1.5;
  margin: 0 0 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.keyword-pill {
  padding: 2px 10px;
  border-radius: 20px;
  font-size: clamp(0.6rem, 2.5vw, 0.7rem);
  font-weight: 600;
}

.bottom-right {
  flex: 0 0 45%;
  min-width: 0;
}

.day-column-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: clamp(0.6rem, 2.5vw, 0.7rem);
  font-weight: 700;
  margin-bottom: 4px;
}

.dc-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: clamp(0.55rem, 2.3vw, 0.65rem);
  color: #fff;
  white-space: nowrap;
}

.day-column-desc {
  font-size: clamp(0.6rem, 2.5vw, 0.7rem);
  color: #64748B;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ===== 响应式移动端 ===== */
@media (max-width: 640px) {
  .card-top { padding: 12px 14px; }
  .card-center { padding: 12px 12px 8px; gap: 8px; }
  .center-left { flex: 0 0 28%; }
  .center-right { flex: 0 0 72%; }
  .avatar-frame { max-width: 160px; border-radius: 14px; }
  .card-bottom { padding: 10px 12px; gap: 8px; flex-wrap: wrap; }
  .bottom-left { flex: 0 0 100%; }
  .bottom-right { flex: 0 0 100%; }
}

/* ===== 响应式电脑端 ===== */
@media (min-width: 1024px) {
  .card-top { padding: 18px 24px; }
  .card-center { padding: 20px 24px 16px; gap: 16px; }
  .talent-tag-item { padding: 8px 14px; border-radius: 12px; }
  .card-bottom { padding: 16px 24px; }
  .avatar-frame { max-width: 240px; border-radius: 24px; }
}
</style>
