<template>
  <section class="report-home">
    <!-- 主视觉区域：昵称 + Q版形象 + 配文 -->
    <div class="hero-section">
      <!-- 背景装饰 -->
      <div class="hero-bg">
        <div class="bg-circle circle-1" :style="{ background: traitInfo.color + '20' }"></div>
        <div class="bg-circle circle-2" :style="{ background: traitInfo.color + '15' }"></div>
        <div class="bg-circle circle-3" :style="{ background: traitInfo.color + '10' }"></div>
      </div>

      <!-- 昵称 -->
      <h1 class="user-nickname">{{ displayName }}</h1>

      <!-- Q版形象区域 -->
      <div class="avatar-container">
        <div 
          class="avatar-wrapper"
          :style="{ borderColor: traitInfo.color }"
        >
          <img 
            v-if="!avatarLoadError"
            :src="avatarUrl" 
            :alt="dayMaster + genderText + ' Q版形象'"
            class="avatar-image"
            @error="handleAvatarError"
          />
          <!-- 图片加载失败时的降级显示 -->
          <div v-else class="avatar-fallback" :style="{ background: traitInfo.color + '20', color: traitInfo.color }">
            <span class="fallback-emoji">{{ traitInfo.element ? ELEMENT_SYMBOLS[traitInfo.element]?.symbol : '🧑' }}</span>
            <span class="fallback-text">{{ dayMaster }}</span>
          </div>
          <span class="day-master-badge" :style="{ background: traitInfo.color, color: '#fff' }">
            {{ dayMaster }}{{ traitInfo.element }}
          </span>
        </div>
      </div>

      <!-- 特质配文 -->
      <p class="trait-description">{{ traitInfo.description }}</p>

      <!-- 日主标签 -->
      <div class="meta-tags">
        <span class="tag day-tag" :style="{ borderColor: traitInfo.color + '40', color: traitInfo.color }">
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
import { computed, ref, onMounted } from 'vue'
import { getDayMasterTrait, getQVersionAvatar, getFullAvatarUrl, ELEMENT_SYMBOLS } from '../data/dayMasterData'

const props = defineProps({
  userInfo: {
    type: Object,
    default: () => ({})
  },
  dayMaster: {
    type: String,
    default: ''
  }
})

// 头像加载失败标记
const avatarLoadError = ref(false)

// 显示昵称
const displayName = computed(() => {
  const name = props.userInfo?.name || '探索者'
  return name.length > 2 ? name : name
})

// 性别
const genderText = computed(() => {
  const g = props.userInfo?.gender
  return (g === 'male' || g === '男') ? '♂' : '♀'
})

// 头像URL - 使用完整路径含 origin，避免 Vite 路径问题
const avatarUrl = computed(() => {
  if (avatarLoadError.value) return ''
  const dm = props.dayMaster || '甲'
  const g = props.userInfo?.gender || 'male'
  const url = getFullAvatarUrl(dm, g)
  console.log('[Avatar] dm:', dm, 'gender:', g, 'url:', url)
  return url
})

// 预加载校验（仅日志，不改变状态）
onMounted(() => {
  const dm = props.dayMaster || '甲'
  const g = props.userInfo?.gender || 'male'
  const testUrl = getFullAvatarUrl(dm, g)
  const img = new Image()
  img.onload = () => console.log('[Avatar] ✅ loaded:', testUrl)
  img.onerror = (e) => console.error('[Avatar] ❌ failed:', testUrl)
  img.src = testUrl
})

// 头像加载失败处理（带重试）
const avatarRetryCount = ref(0)
const handleAvatarError = () => {
  if (avatarRetryCount.value < 2) {
    avatarRetryCount.value++
    console.log(`[Avatar] retry ${avatarRetryCount.value}/2`)
    // 尝试重新加载
    setTimeout(() => {
      avatarLoadError.value = false
    }, 1000)
  } else {
    console.log('[Avatar] fallback after 2 retries')
    avatarLoadError.value = true
  }
}

// 获取日主特质信息
const traitInfo = computed(() => {
  return getDayMasterTrait(props.dayMaster || '甲', props.userInfo?.gender || 'male')
})

// 出生日期文本
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
.report-home {
  /* 容器样式 */
}

.hero-section {
  position: relative;
  padding: 32px 20px 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: hidden;
}

/* 背景装饰圆圈 */
.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: -60px;
  right: -40px;
  opacity: 1;
}

.circle-2 {
  width: 140px;
  height: 140px;
  bottom: 20px;
  left: -30px;
  opacity: 1;
}

.circle-3 {
  width: 80px;
  height: 80px;
  top: 40%;
  left: 50%;
  transform: translateX(-50%);
  opacity: 1;
}

/* 昵称 */
.user-nickname {
  font-size: clamp(1.75rem, 8vw, 2.25rem);
  font-weight: 800;
  color: #1E293B;
  margin: 0 0 24px;
  letter-spacing: 0.05em;
  text-align: center;
  position: relative;
  z-index: 1;
}

/* Q版形象区域 */
.avatar-container {
  position: relative;
  z-index: 1;
  margin-bottom: 20px;
}

.avatar-wrapper {
  width: 140px;
  height: 160px;
  border-radius: 24px;
  border: 2.5px solid;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.avatar-wrapper:hover {
  transform: scale(1.03);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 22px;
}

.avatar-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 22px;
  gap: 4px;
}

.fallback-emoji {
  font-size: 40px;
  line-height: 1;
}

.fallback-text {
  font-size: 18px;
  font-weight: 700;
}

.day-master-badge {
  position: absolute;
  bottom: -10px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* 特质配文 */
.trait-description {
  font-size: clamp(0.9375rem, 4vw, 1rem);
  color: #4A5568;
  line-height: 1.7;
  text-align: center;
  margin: 0 0 16px;
  max-width: 320px;
  position: relative;
  z-index: 1;
  font-weight: 500;
  padding: 0 8px;
}

/* 标签组 */
.meta-tags {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  position: relative;
  z-index: 1;
}

.tag {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.day-tag {
  border: 1.5px solid;
  background: white;
}

.birth-tag {
  background: #F1F5F9;
  color: #64748B;
}

/* 响应式 - 手机端 */
@media (max-width: 480px) {
  .hero-section {
    padding: 24px 16px 22px;
  }

  .avatar-wrapper {
    width: 120px;
    height: 140px;
    border-radius: 20px;
  }

  .avatar-image {
    border-radius: 18px;
  }

  .trait-description {
    font-size: 14px;
  }
}

/* 响应式 - 电脑端 */
@media (min-width: 1024px) {
  .hero-section {
    padding: 40px 32px 36px;
  }

  .user-nickname {
    font-size: 28px;
  }

  .avatar-wrapper {
    width: 160px;
    height: 180px;
    border-radius: 28px;
  }

  .avatar-image {
    border-radius: 26px;
  }

  .trait-description {
    font-size: 17px;
    max-width: 400px;
  }

  .tag {
    padding: 7px 16px;
    font-size: 14px;
  }
}
</style>
