<template>
  <div class="loading-page">
    <!-- 背景动画 -->
    <div class="bg-animation">
      <div class="floating-shape shape-1"></div>
      <div class="floating-shape shape-2"></div>
      <div class="floating-shape shape-3"></div>
    </div>
    
    <!-- 主内容 -->
    <div class="content">
      <!-- 加载动画 -->
      <div class="loading-animation">
        <div class="spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
        </div>
      </div>
      
      <!-- 标题 -->
      <h1 class="loading-title">正在生成你的天赋报告</h1>
      
      <!-- 进度提示 -->
      <div class="progress-steps">
        <div 
          v-for="(step, idx) in steps" 
          :key="idx"
          class="step"
          :class="{ active: currentStep >= idx, completed: currentStep > idx }"
        >
          <div class="step-dot">
            <svg v-if="currentStep > idx" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <span v-else>{{ idx + 1 }}</span>
          </div>
          <span class="step-text">{{ step }}</span>
        </div>
      </div>
      
      <!-- 趣味提示 -->
      <transition name="fade" mode="out-in">
        <p class="fun-tip" :key="currentTip">{{ tips[currentTip] }}</p>
      </transition>
      
      <!-- 预计时间 -->
      <p class="time-estimate">预计需要 10-20 秒</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const steps = ['分析八字', '计算五行', 'AI解读', '生成报告']
const currentStep = ref(0)

const tips = [
  '每个人的天赋都是独一无二的',
  '发现优势，比弥补短板更重要',
  '传统智慧 + AI技术 = 专属分析',
  '了解自己的潜能，是成长的第一步',
  '你的独特之处，正是你的价值所在'
]
const currentTip = ref(0)

let stepInterval = null
let tipInterval = null

onMounted(() => {
  // 步骤进度动画
  stepInterval = setInterval(() => {
    if (currentStep.value < steps.length - 1) {
      currentStep.value++
    }
  }, 3000)
  
  // 趣味提示轮换
  tipInterval = setInterval(() => {
    currentTip.value = (currentTip.value + 1) % tips.length
  }, 4000)
})

onUnmounted(() => {
  clearInterval(stepInterval)
  clearInterval(tipInterval)
})
</script>

<style scoped>
.loading-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #F0F9FF 0%, #FDFCF8 50%, #F0FFF4 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

/* 背景动画 */
.bg-animation {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.floating-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  top: 10%;
  left: -50px;
  animation-delay: 0s;
}

.shape-2 {
  width: 150px;
  height: 150px;
  background: linear-gradient(135deg, #A8E6CF 0%, #DCEDC1 100%);
  top: 50%;
  right: -30px;
  animation-delay: 2s;
}

.shape-3 {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #DDBEA9 0%, #E8D5C4 100%);
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* 主内容 */
.content {
  text-align: center;
  z-index: 1;
  max-width: 360px;
}

/* 加载动画 */
.loading-animation {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 32px;
}

.spinner {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.spinner-ring {
  position: absolute;
  border-radius: 50%;
  border: 3px solid transparent;
  border-top-color: #8EC5FC;
  animation: spin 1.5s linear infinite;
}

.spinner-ring:nth-child(1) {
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.spinner-ring:nth-child(2) {
  top: 10px;
  left: 10px;
  right: 10px;
  bottom: 10px;
  border-top-color: #A8E6CF;
  animation-duration: 1.2s;
  animation-direction: reverse;
}

.spinner-ring:nth-child(3) {
  top: 20px;
  left: 20px;
  right: 20px;
  bottom: 20px;
  border-top-color: #DDBEA9;
  animation-duration: 0.9s;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 36px;
  height: 36px;
  animation: pulse 2s ease-in-out infinite;
}

.loading-icon svg {
  width: 100%;
  height: 100%;
  color: #8EC5FC;
}

@keyframes pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    transform: translate(-50%, -50%) scale(1.2);
  }
}

/* 标题 */
.loading-title {
  font-size: 22px;
  font-weight: 700;
  color: #4A5568;
  margin: 0 0 32px;
}

/* 进度步骤 */
.progress-steps {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.step-dot {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #E2E8F0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: #A0AEC0;
  transition: all 0.3s ease;
}

.step-dot svg {
  width: 18px;
  height: 18px;
}

.step.active .step-dot {
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(142, 197, 252, 0.4);
}

.step.completed .step-dot {
  background: #8EC5FC;
  color: white;
}

.step-text {
  font-size: 12px;
  color: #A0AEC0;
  transition: all 0.3s ease;
}

.step.active .step-text,
.step.completed .step-text {
  color: #4A5568;
  font-weight: 500;
}

/* 趣味提示 */
.fun-tip {
  font-size: 15px;
  color: #718096;
  margin: 0 0 16px;
  min-height: 24px;
}

/* 预计时间 */
.time-estimate {
  font-size: 13px;
  color: #A0AEC0;
  margin: 0;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式 */
@media (max-width: 480px) {
  .loading-title {
    font-size: 20px;
  }
  
  .progress-steps {
    gap: 12px;
  }
  
  .step-text {
    font-size: 11px;
  }
  
  .fun-tip {
    font-size: 14px;
  }
}
</style>