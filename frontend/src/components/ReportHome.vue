<template>
  <section class="report-home">
    <div class="hero-section">
      <!-- 背景装饰 -->
      <div class="hero-bg">
        <div class="bg-circle circle-1" :style="{ background: traitInfo.color + '18' }"></div>
        <div class="bg-circle circle-2" :style="{ background: traitInfo.color + '12' }"></div>
      </div>

      <!-- 昵称 -->
      <h1 class="user-nickname">{{ displayName }}</h1>

      <!-- 天赋主卡片（取代原Q版形象） -->
      <div class="profile-card" :style="{ borderColor: traitInfo.color + '30' }">
        <div class="profile-left">
          <div class="day-master-circle" :style="{ background: traitInfo.color + '15', color: traitInfo.color }">
            <span class="dm-char">{{ dayMaster }}</span>
            <span class="dm-element">{{ traitInfo.element }}</span>
          </div>
        </div>
        <div class="profile-right">
          <div class="profile-tag" :style="{ color: traitInfo.color }">
            {{ elementSymbol }} {{ dayMaster }}{{ traitInfo.element }} · {{ genderText === '♂' ? '阳' : '阴' }}
          </div>
          <p class="profile-desc">{{ traitInfo.description }}</p>
        </div>
      </div>

      <!-- 标签组 -->
      <div class="meta-tags">
        <span class="tag day-tag" :style="{ borderColor: traitInfo.color + '40', color: traitInfo.color, background: traitInfo.color + '08' }">
          日主 · {{ dayMaster }}{{ traitInfo.element }}
        </span>
        <span class="tag birth-tag">
          {{ birthDateText }}
        </span>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { getDayMasterTrait, ELEMENT_SYMBOLS } from '../data/dayMasterData'

const props = defineProps({
  userInfo: { type: Object, default: () => ({}) },
  dayMaster: { type: String, default: '' }
})

const displayName = computed(() => props.userInfo?.name || '探索者')

const genderText = computed(() => {
  const g = props.userInfo?.gender
  return (g === 'male' || g === '男') ? '♂' : '♀'
})

const traitInfo = computed(() => {
  return getDayMasterTrait(props.dayMaster || '甲', props.userInfo?.gender || 'male')
})

const elementSymbol = computed(() => {
  return ELEMENT_SYMBOLS[traitInfo.value.element]?.symbol || '✨'
})

const birthDateText = computed(() => {
  const time = props.userInfo?.birth_time?.original
  if (!time) return ''
  let text = `${time.year}年${time.month}月${time.day}日`
  if (time.hour !== null && time.hour !== undefined) {
    text += ` ${String(time.hour).padStart(2, '0')}:${String(time.minute).padStart(2, '0')}`
  }
  return text
})
</script>

<style scoped>
.report-home { /* 容器 */ }

.hero-section {
  position: relative;
  padding: 36px 20px 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: hidden;
}

/* ===== 背景装饰 ===== */
.hero-bg {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
}

.circle-1 {
  width: 220px; height: 220px;
  top: -80px; right: -60px;
}

.circle-2 {
  width: 160px; height: 160px;
  bottom: -40px; left: -50px;
}

/* ===== 昵称 ===== */
.user-nickname {
  font-size: clamp(1.75rem, 8vw, 2.25rem);
  font-weight: 800;
  color: #1E293B;
  margin: 0 0 24px;
  letter-spacing: 0.06em;
  text-align: center;
  position: relative;
  z-index: 1;
}

.user-nickname::after {
  content: '';
  display: block;
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, #8EC5FC, #A8E6CF);
  border-radius: 2px;
  margin: 10px auto 0;
}

/* ===== 天赋主卡片（仿分享页设计） ===== */
.profile-card {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
  max-width: 340px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(8px);
  border-radius: 16px;
  border: 1.5px solid;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  position: relative;
  z-index: 1;
  margin-bottom: 20px;
}

.profile-left { flex-shrink: 0; }

.day-master-circle {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.dm-char {
  font-size: 28px;
  font-weight: 800;
}

.dm-element {
  font-size: 12px;
  font-weight: 600;
  opacity: 0.7;
  margin-top: 2px;
}

.profile-right {
  flex: 1;
  min-width: 0;
}

.profile-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 6px;
}

.profile-desc {
  font-size: 14px;
  line-height: 1.6;
  color: #475569;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ===== 标签组 ===== */
.meta-tags {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  position: relative;
  z-index: 1;
  margin-top: 4px;
}

.tag {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.day-tag {
  border: 1.5px solid;
}

.birth-tag {
  background: #F1F5F9;
  color: #64748B;
}

/* ===== 响应式 ===== */
@media (max-width: 480px) {
  .hero-section { padding: 28px 16px 22px; }
  .profile-card { max-width: 300px; padding: 16px; }
  .profile-desc { font-size: 13px; }
}

@media (min-width: 1024px) {
  .hero-section { padding: 44px 32px 36px; }
  .user-nickname { font-size: 28px; }
  .profile-card { max-width: 380px; padding: 24px; }
  .profile-desc { font-size: 15px; }
  .tag { padding: 7px 16px; font-size: 14px; }
}
</style>
