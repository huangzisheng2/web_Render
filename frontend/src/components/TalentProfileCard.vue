<template>
  <div class="talent-card" :style="cardStyle">
    <!-- 顶部区域 -->
    <div class="card-header">
      <!-- 方案徽章行 -->
      <div class="header-badge-row">
        <span class="scheme-badge">方案三</span>
        <span class="style-badge">五行趣姻风</span>
      </div>

      <!-- 主标题 -->
      <h2 class="header-title">{{ displayName }}的潜在天赋档案</h2>

      <!-- 副标题：日柱 + 气势描述 -->
      <div class="header-subtitle">
        <span class="subtitle-icon" :style="{ background: traitInfo.color, color: '#fff' }">{{ dayMaster }}</span>
        <span class="subtitle-text">
          <strong>{{ dayPillarLabel }}</strong> · {{ traitInfo.motto || traitInfo.description.slice(0, 12) }}
        </span>
      </div>
    </div>

    <!-- 中间主体：左侧天赋列表 + 右侧Q版圆形框 -->
    <div class="card-body">
      <!-- 左侧：天赋列表（圆形图标+文字） -->
      <div class="body-left">
        <div
          v-for="(tag, i) in displayTags"
          :key="i"
          class="talent-item"
        >
          <span
            class="talent-icon"
            :style="{ background: talentColors[i], color: '#fff' }"
          >
            {{ tagEmojis[i] }}
          </span>
          <div class="talent-info">
            <span class="talent-name">{{ tag }}</span>
            <span class="talent-desc-icon">{{ tagIcons[i] }}</span>
            <p class="talent-desc">{{ tagDescriptions[i] || '' }}</p>
          </div>
        </div>
      </div>

      <!-- 右侧：Q版形象（中式圆形装饰框） -->
      <div class="body-right">
        <div class="avatar-circle-frame">
          <div class="avatar-inner">
            <img
              v-if="avatarUrl"
              :src="avatarUrl"
              alt="Q版形象"
              class="avatar-img"
              @error="avatarError = true"
            />
            <div v-else class="avatar-placeholder" :style="{ color: traitInfo.color }">
              <span class="ph-char">{{ dayMaster }}</span>
              <span class="ph-el">{{ traitInfo.element }}</span>
            </div>
          </div>
          <!-- 装饰性圆环 -->
          <svg class="circle-decoration" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="96" fill="none" stroke="url(#goldGrad)" stroke-width="1.5" opacity="0.6"/>
            <circle cx="100" cy="100" r="88" fill="none" stroke="url(#goldGrad)" stroke-width="0.5" opacity="0.3"/>
            <defs>
              <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#C9A96E;stop-opacity:1" />
                <stop offset="50%" style="stop-color:#8B7355;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#C9A96E;stop-opacity:1" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>
    </div>

    <!-- 底部：特质语 + 关键词 | 历史人物 -->
    <div class="card-footer">
      <!-- 特质概括语（带金色装饰） -->
      <p class="footer-trait">
        <span class="trait-deco trait-deco-left">☀</span>
        {{ traitDescription || traitInfo.description }}
        <span class="trait-deco trait-deco-right">☀</span>
      </p>

      <!-- 左右分栏：关键词 | 历史人物 -->
      <div class="footer-columns">
        <!-- 左侧：天赋关键词（金棕胶囊） -->
        <div class="footer-left">
          <h4 class="col-title">天赋关键调</h4>
          <div class="keyword-pills">
            <span
              v-for="(kw, i) in displayKeywords"
              :key="i"
              class="keyword-pill"
            >{{ kw }}</span>
          </div>
        </div>

        <!-- 右侧：历史人物（简洁列表） -->
        <div class="footer-right">
          <h4 class="col-title">历史人物</h4>
          <ul class="history-list">
            <li v-for="(figure, i) in historicalFigures" :key="i" class="history-item">
              {{ figure.name }}，{{ figure.title }}。
            </li>
          </ul>
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

// 圆形图标 emoji（对应期望图风格）
const tagEmojis = ['🌊', '🔍', '⚖️', '👑', '💜']
// 每个天赋右侧的小图标
const tagIcons = ['💡', '🔍', '⚖️', '👑', '💙']

// 天赋圆形图标颜色（蓝/绿/金/红/紫 - 对应五行）
const talentColors = [
  '#3B82F6', // 蓝 - 水/创新
  '#10B981', // 绿 - 木/洞察
  '#D4A853', // 金 - 土/调配
  '#DC2626', // 红 - 火/领导
  '#8B5CF6'  // 紫 - 共情
]

// 每个天赋标签配描述
const tagDescriptions = computed(() => {
  const summary = props.talentSummary || ''
  if (!summary) return []
  const parts = summary.split(/[。！？]/).filter(s => s.trim())
  return parts.slice(0, 5).map(p => p.trim().slice(0, 22))
})

const cardStyle = computed(() => ({
  '--card-accent': traitInfo.value.color || '#8EC5FC'
}))
</script>

<style scoped>
/* ===== 整体卡片：古风宣纸底色 ===== */
.talent-card {
  width: 100%;
  border-radius: 16px;
  background: linear-gradient(160deg, #FDF8F0 0%, #FAF3E8 40%, #F5EDE0 100%);
  border: 1px solid rgba(201, 169, 110, 0.25);
  box-shadow:
    0 4px 24px rgba(139, 115, 85, 0.08),
    inset 0 1px 0 rgba(255,255,255,0.6);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  font-family: -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

/* ===== 顶部区域 ===== */
.card-header {
  padding: 14px 18px 10px;
  position: relative;
}

/* 方案徽章行 */
.header-badge-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.scheme-badge {
  font-size: 0.65rem;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #5B6B7C 0%, #4A5568 100%);
  padding: 2px 10px;
  border-radius: 10px 10px 10px 1px;
  letter-spacing: 0.05em;
}

.style-badge {
  font-size: 0.6rem;
  color: #8B7355;
  font-weight: 600;
  opacity: 0.7;
}

/* 主标题 */
.header-title {
  font-size: clamp(1.15rem, 5vw, 1.45rem);
  font-weight: 900;
  color: #2D2416;
  margin: 0 0 6px;
  letter-spacing: 0.06em;
}

/* 副标题（日柱+气势描述） */
.header-subtitle {
  display: flex;
  align-items: center;
  gap: 8px;
}

.subtitle-icon {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  font-weight: 800;
  flex-shrink: 0;
}

.subtitle-text {
  font-size: clamp(0.7rem, 3vw, 0.82rem);
  color: #6B5D4D;
  line-height: 1.4;
}

.subtitle-text strong {
  color: #3D3426;
  font-weight: 700;
}

/* ===== 中间主体 ===== */
.card-body {
  flex: 1;
  display: flex;
  padding: 10px 16px 12px;
  gap: 14px;
  min-height: 0;
  align-items: stretch;
}

/* ===== 左侧天赋列表 ===== */
.body-left {
  flex: 0 0 38%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 7px;
}

.talent-item {
  display: flex;
  align-items: flex-start;
  gap: 9px;
}

.talent-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.talent-info {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 3px 4px;
  min-width: 0;
  padding-top: 3px;
}

.talent-name {
  font-size: clamp(0.72rem, 3vw, 0.86rem);
  font-weight: 800;
  color: #2D2416;
  white-space: nowrap;
}

.talent-desc-icon {
  font-size: 0.65rem;
  flex-shrink: 0;
}

.talent-desc {
  width: 100%;
  font-size: clamp(0.55rem, 2.4vw, 0.66rem);
  color: #8B8070;
  line-height: 1.35;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ===== 右侧Q版形象圆形装饰框 ===== */
.body-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.avatar-circle-frame {
  position: relative;
  width: 100%;
  max-width: 220px;
  aspect-ratio: 1 / 1.15;
}

.avatar-inner {
  width: 100%;
  height: 100%;
  border-radius: 50% / 48%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, rgba(255,255,255,0.5) 0%, rgba(250,243,232,0.8) 100%);
  border: 1.5px solid rgba(201, 169, 110, 0.35);
  box-shadow:
    0 4px 20px rgba(139, 115, 85, 0.1),
    inset 0 2px 8px rgba(255,255,255,0.4);
  position: relative;
  z-index: 1;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.ph-char { font-size: 36px; font-weight: 900; }
.ph-el { font-size: 14px; font-weight: 700; opacity: 0.6; }

/* SVG 装饰圆环 */
.circle-decoration {
  position: absolute;
  top: -3%;
  left: -3%;
  width: 106%;
  height: 106%;
  pointer-events: none;
  z-index: 2;
}

/* ===== 底部区域 ===== */
.card-footer {
  padding: 12px 16px 14px;
  border-top: 1px solid rgba(201, 169, 110, 0.15);
  background: linear-gradient(180deg, rgba(253,248,240,0) 0%, rgba(245,237,224,0.5) 100%);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 特质语（带金色装饰） */
.footer-trait {
  font-size: clamp(0.75rem, 3.2vw, 0.88rem);
  font-weight: 700;
  color: #3D3426;
  text-align: center;
  margin: 0;
  line-height: 1.5;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.trait-deco {
  color: #C9A96E;
  font-size: 0.75rem;
  opacity: 0.7;
  flex-shrink: 0;
}

/* 左右分栏 */
.footer-columns {
  display: flex;
  gap: 16px;
}

.footer-left,
.footer-right {
  flex: 1;
}

.col-title {
  font-size: clamp(0.68rem, 2.8vw, 0.78rem);
  font-weight: 800;
  color: #3D3426;
  margin: 0 0 7px;
  letter-spacing: 0.04em;
}

/* 金棕胶囊关键词 */
.keyword-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.keyword-pill {
  font-size: clamp(0.6rem, 2.5vw, 0.7rem);
  font-weight: 700;
  color: #6B5D4D;
  background: linear-gradient(135deg, #E8DCC8 0%, #DDD0BA 100%);
  border: 1px solid rgba(201, 169, 110, 0.3);
  padding: 4px 14px;
  border-radius: 20px;
  white-space: nowrap;
  cursor: default;
  transition: all 0.2s ease;
}

.keyword-pill:hover {
  background: linear-gradient(135deg, #DDD0BA 0%, #D0C2AA 100%);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(139, 115, 85, 0.15);
}

/* 历史人物简洁列表 */
.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.history-item {
  font-size: clamp(0.62rem, 2.6vw, 0.72rem);
  color: #6B5D4D;
  line-height: 1.5;
  padding-left: 12px;
  position: relative;
}

.history-item::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #C9A96E;
  font-weight: 700;
}

/* ===== 响应式适配 ===== */
@media (max-width: 640px) {
  .card-header { padding: 11px 13px 8px; }
  .card-body {
    padding: 8px 11px 10px;
    gap: 10px;
    flex-direction: column-reverse;
  }
  .body-left { flex: none; gap: 6px; }
  .body-right { flex: none; max-width: 200px; margin: 0 auto; }
  .talent-icon { width: 28px; height: 28px; font-size: 0.78rem; }
  .avatar-circle-frame { max-width: 180px; }
  .footer-columns { flex-direction: column; gap: 10px; }
  .card-footer { padding: 10px 12px 12px; gap: 8px; }
}

@media (min-width: 1024px) {
  .card-header { padding: 18px 26px 14px; }
  .header-title { font-size: 1.55rem; }
  .card-body { padding: 16px 24px 16px; gap: 20px; }
  .body-left { gap: 10px; }
  .talent-icon { width: 38px; height: 38px; font-size: 1rem; }
  .talent-name { font-size: 0.95rem; }
  .talent-desc { font-size: 0.72rem; }
  .avatar-circle-frame { max-width: 260px; }
  .card-footer { padding: 16px 24px 18px; gap: 12px; }
  .keyword-pill { padding: 5px 18px; font-size: 0.76rem; }
  .history-item { font-size: 0.78rem; }
}
</style>
