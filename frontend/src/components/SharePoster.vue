<template>
  <div class="share-poster-wrapper">
    <!-- 海报容器（隐藏，用于截图） -->
    <div ref="posterRef" class="poster-canvas">
      <!-- 顶部（10%）：姓名 + 天赋档案 -->
      <div class="poster-top">
        <span class="poster-name">{{ displayName }}</span>
        <span class="poster-title">天赋档案</span>
      </div>

      <!-- C位（70%）：左侧天赋标签 + 右侧Q版形象 -->
      <div class="poster-center">
        <!-- 左侧：5个天赋标签 -->
        <div class="poster-tags">
          <div
            v-for="(tag, index) in displayTags"
            :key="index"
            class="poster-tag"
            :style="{ borderColor: traitInfo.color }"
          >
            <span class="tag-emoji">{{ tagEmojis[index] }}</span>
            <span class="tag-text">{{ tag }}</span>
          </div>
        </div>

        <!-- 右侧：Q版形象 + 昵称 -->
        <div class="poster-avatar-area">
          <img :src="avatarUrl" class="poster-avatar" crossorigin="anonymous" />
          <span class="poster-nickname">{{ displayName }}</span>
        </div>
      </div>

      <!-- 底部（20%）：特质概括 + 二维码 -->
      <div class="poster-bottom">
        <div class="poster-trait-text">{{ traitDescription }}</div>
        <div class="poster-qr-area">
          <img src="/qrcode.jpg" class="poster-qr" crossorigin="anonymous" />
          <span class="poster-qr-text">扫码测测你的隐藏天赋</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import html2canvas from 'html2canvas'
import { getQVersionAvatar } from '../data/dayMasterData'

const props = defineProps({
  userInfo: {
    type: Object,
    default: () => ({})
  },
  dayMaster: {
    type: String,
    default: '甲'
  },
  traitInfo: {
    type: Object,
    default: () => ({})
  },
  talentTags: {
    type: Array,
    default: () => []
  },
  traitDescription: {
    type: String,
    default: ''
  }
})

const posterRef = ref(null)

// 显示名称
const displayName = computed(() => {
  return props.userInfo?.name || '我'
})

// Q版头像路径
const avatarUrl = computed(() => {
  const gender = props.userInfo?.gender || 'male'
  return getQVersionAvatar(props.dayMaster, gender)
})

// 天赋标签（最多5个）
const displayTags = computed(() => {
  const tags = props.talentTags?.length ? props.talentTags : ['天赋探索者']
  return tags.slice(0, 5)
})

// 标签 emoji
const tagEmojis = ['✨', '🌟', '💫', '🔥', '💎']

/**
 * 生成分享图片
 * @returns {Promise<string>} 图片 data URL
 */
async function generateImage() {
  if (!posterRef.value) return null

  try {
    // 临时将海报移到可见区域以便 html2canvas 渲染
    const wrapper = posterRef.value.closest('.share-poster-wrapper')
    const origLeft = wrapper?.style.left
    if (wrapper) {
      wrapper.style.left = '0px'
      wrapper.style.zIndex = '9999'
    }

    // 等待图片加载完成
    const images = posterRef.value.querySelectorAll('img')
    await Promise.all(
      Array.from(images).map(img => {
        if (img.complete) return Promise.resolve()
        return new Promise((resolve) => {
          img.onload = resolve
          img.onerror = resolve
        })
      })
    )

    const canvas = await html2canvas(posterRef.value, {
      width: 1080,
      height: 1440,
      scale: 1,
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#F0F9FF',
      logging: false,
      imageTimeout: 15000
    })

    // 恢复隐藏位置
    if (wrapper) {
      wrapper.style.left = origLeft || '-9999px'
      wrapper.style.zIndex = '-1'
    }

    return canvas.toDataURL('image/png')
  } catch (e) {
    console.error('生成分享图失败:', e)
    // 确保恢复隐藏位置
    const wrapper = posterRef.value?.closest('.share-poster-wrapper')
    if (wrapper) {
      wrapper.style.left = '-9999px'
      wrapper.style.zIndex = '-1'
    }
    return null
  }
}

defineExpose({ generateImage })
</script>

<style scoped>
.share-poster-wrapper {
  position: fixed;
  left: -9999px;
  top: 0;
  z-index: -1;
  pointer-events: none;
  opacity: 1;
}

.poster-canvas {
  width: 1080px;
  height: 1440px;
  background: linear-gradient(160deg, #F0F9FF 0%, #E8F4FD 25%, #FDFCF8 50%, #F0FFF4 75%, #E8FDF5 100%);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
  position: relative;
}

/* 背景装饰 */
.poster-canvas::before {
  content: '';
  position: absolute;
  top: -80px;
  right: -80px;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(142, 197, 252, 0.12) 0%, transparent 70%);
}

.poster-canvas::after {
  content: '';
  position: absolute;
  bottom: 200px;
  left: -60px;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(168, 230, 207, 0.12) 0%, transparent 70%);
}

/* 顶部区域 10% */
.poster-top {
  height: 144px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 0 60px;
}

.poster-name {
  font-size: 42px;
  font-weight: 700;
  color: #1A202C;
  letter-spacing: 2px;
}

.poster-title {
  font-size: 32px;
  font-weight: 500;
  color: #718096;
  letter-spacing: 4px;
  position: relative;
  padding-left: 20px;
}

.poster-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 24px;
  background: linear-gradient(180deg, #8EC5FC, #A8E6CF);
  border-radius: 2px;
}

/* 中间区域 70% */
.poster-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 40px 80px;
  position: relative;
  z-index: 1;
}

/* 左侧天赋标签 */
.poster-tags {
  display: flex;
  flex-direction: column;
  gap: 24px;
  flex: 1;
}

.poster-tag {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 18px 28px;
  background: rgba(255, 255, 255, 0.85);
  border-radius: 16px;
  border-left: 5px solid;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  backdrop-filter: blur(8px);
}

.tag-emoji {
  font-size: 36px;
  line-height: 1;
}

.tag-text {
  font-size: 30px;
  font-weight: 600;
  color: #2D3748;
  letter-spacing: 1px;
}

/* 右侧Q版形象 */
.poster-avatar-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  margin-left: 40px;
}

.poster-avatar {
  width: 380px;
  height: 420px;
  object-fit: contain;
  filter: drop-shadow(0 8px 24px rgba(0, 0, 0, 0.08));
}

.poster-nickname {
  font-size: 32px;
  font-weight: 600;
  color: #2D3748;
  text-align: center;
  padding: 8px 24px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 20px;
  letter-spacing: 2px;
}

/* 底部区域 20% */
.poster-bottom {
  height: 288px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 80px 40px;
  position: relative;
  z-index: 1;
}

.poster-trait-text {
  flex: 1;
  font-size: 28px;
  line-height: 1.6;
  color: #4A5568;
  font-weight: 400;
  padding-right: 40px;
  letter-spacing: 1px;
}

.poster-qr-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.poster-qr {
  width: 140px;
  height: 140px;
  border-radius: 12px;
  border: 3px solid rgba(142, 197, 252, 0.3);
}

.poster-qr-text {
  font-size: 18px;
  color: #A0AEC0;
  white-space: nowrap;
  letter-spacing: 1px;
}
</style>
