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
      <div v-if="!reportReady" class="loading-animation">
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
      
      <!-- 完成动画 -->
      <div v-else class="complete-animation">
        <div class="complete-circle">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
        </div>
      </div>
      
      <!-- 标题 -->
      <h1 class="loading-title">
        {{ reportReady ? '报告已生成' : '正在生成你的天赋报告' }}
      </h1>
      
      <!-- 副标题 -->
      <p class="loading-subtitle" v-if="reportReady">
        点击下方按钮查看你的专属报告
      </p>
      
      <!-- 进度提示 -->
      <div v-if="!reportReady" class="progress-steps">
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
      
      <!-- 继续按钮 -->
      <button v-if="reportReady" class="continue-btn" @click="$emit('continue')">
        <span>查看报告</span>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </button>
      
      <!-- 趣味提示 -->
      <transition v-if="!reportReady" name="fade" mode="out-in">
        <p class="fun-tip" :key="currentTip">{{ tips[currentTip] }}</p>
      </transition>
      
      <!-- 预计时间 -->
      <p v-if="!reportReady" class="time-estimate">预计需要 10-20 秒</p>
      
      <!-- 错误重试提示 -->
      <div v-if="!reportReady" class="error-hint">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <p>若分析遇到问题，可返回重试或检查网络连接</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  reportReady: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['continue'])

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
    if (currentStep.value < steps.length - 1 && !props.reportReady) {
      currentStep.value++
    }
  }, 3000)
  
  // 趣味提示轮换
  tipInterval = setInterval(() => {
    if (!props.reportReady) {
      currentTip.value = (currentTip.value + 1) % tips.length
    }
  }, 4000)
})

onUnmounted(() => {
  clearInterval(stepInterval)
  clearInterval(tipInterval)
})

// 当报告准备好时，自动完成所有步骤
watch(() => props.reportReady, (newVal) => {
  if (newVal) {
    currentStep.value = steps.length - 1
  }
})
</script>

<style scoped>
.loading-page {
  min-height: 100vh;
  min-height: 100dvh;
  background: linear-gradient(180deg, #F0F9FF 0%, #FDFCF8 50%, #F0FFF4 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: env(safe-area-inset-top) 5vw env(safe-area-inset-bottom);
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
  width: 50vw;
  height: 50vw;
  max-width: 200px;
  max-height: 200px;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  top: 10%;
  left: -10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 40vw;
  height: 40vw;
  max-width: 150px;
  max-height: 150px;
  background: linear-gradient(135deg, #A8E6CF 0%, #DCEDC1 100%);
  top: 50%;
  right: -5%;
  animation-delay: 2s;
}

.shape-3 {
  width: 30vw;
  height: 30vw;
  max-width: 100px;
  max-height: 100px;
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
  max-width: 90vw;
  width: 100%;
  max-width: 360px;
  padding: 4vh 0;
}

/* 加载动画 */
.loading-animation {
  position: relative;
  width: 30vw;
  height: 30vw;
  max-width: 120px;
  max-height: 120px;
  min-width: 80px;
  min-height: 80px;
  margin: 0 auto 4vh;
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
  top: 10%;
  left: 10%;
  right: 10%;
  bottom: 10%;
  border-top-color: #A8E6CF;
  animation-duration: 1.2s;
  animation-direction: reverse;
}

.spinner-ring:nth-child(3) {
  top: 20%;
  left: 20%;
  right: 20%;
  bottom: 20%;
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
  width: 30%;
  height: 30%;
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

/* 完成动画 */
.complete-animation {
  margin: 0 auto 4vh;
}

.complete-circle {
  width: 25vw;
  height: 25vw;
  max-width: 100px;
  max-height: 100px;
  min-width: 72px;
  min-height: 72px;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  animation: scaleIn 0.5s ease;
  box-shadow: 0 8px 24px rgba(142, 197, 252, 0.4);
}

.complete-circle svg {
  width: 50%;
  height: 50%;
  color: white;
}

@keyframes scaleIn {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 标题 */
.loading-title {
  font-size: clamp(1.375rem, 5.5vw, 1.5rem);
  font-weight: 700;
  color: #4A5568;
  margin: 0 0 2vh;
}

.loading-subtitle {
  font-size: clamp(0.9375rem, 4vw, 1rem);
  color: #718096;
  margin: 0 0 4vh;
}

/* 进度步骤 */
.progress-steps {
  display: flex;
  justify-content: center;
  gap: 4vw;
  margin-bottom: 5vh;
  flex-wrap: wrap;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1vh;
}

.step-dot {
  width: 9vw;
  height: 9vw;
  max-width: 36px;
  max-height: 36px;
  min-width: 28px;
  min-height: 28px;
  border-radius: 50%;
  background: #E2E8F0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: clamp(0.75rem, 3vw, 0.875rem);
  font-weight: 600;
  color: #A0AEC0;
  transition: all 0.3s ease;
}

.step-dot svg {
  width: 50%;
  height: 50%;
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
  font-size: clamp(0.6875rem, 2.8vw, 0.75rem);
  color: #A0AEC0;
  transition: all 0.3s ease;
}

.step.active .step-text,
.step.completed .step-text {
  color: #4A5568;
  font-weight: 500;
}

/* 继续按钮 */
.continue-btn {
  width: 70vw;
  max-width: 280px;
  padding: 2.5vh 6vw;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: clamp(1rem, 4vw, 1.125rem);
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2vw;
  margin: 0 auto 4vh;
  box-shadow: 0 6px 20px rgba(142, 197, 252, 0.4);
  transition: all 0.3s ease;
  animation: slideUp 0.5s ease 0.3s both;
}

.continue-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(142, 197, 252, 0.5);
}

.continue-btn:active {
  transform: translateY(0);
}

.continue-btn svg {
  width: 5vw;
  max-width: 20px;
  min-width: 18px;
  height: auto;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 趣味提示 */
.fun-tip {
  font-size: clamp(0.9375rem, 4vw, 1rem);
  color: #718096;
  margin: 0 0 2vh;
  min-height: 1.5em;
  padding: 0 4vw;
}

/* 预计时间 */
.time-estimate {
  font-size: clamp(0.8125rem, 3.5vw, 0.875rem);
  color: #A0AEC0;
  margin: 0 0 3vh;
}

/* 错误重试提示 */
.error-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2vw;
  padding: 2vh 4vw;
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border-radius: 10px;
  border: 1px solid #FCD34D;
  max-width: 90%;
  margin: 0 auto;
}

.error-hint svg {
  width: 5vw;
  max-width: 18px;
  min-width: 16px;
  height: auto;
  color: #D97706;
  flex-shrink: 0;
}

.error-hint p {
  font-size: clamp(0.8125rem, 3.5vw, 0.875rem);
  color: #92400E;
  margin: 0;
  line-height: 1.5;
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
  .loading-animation {
    margin-bottom: 3vh;
  }
  
  .complete-animation {
    margin-bottom: 3vh;
  }
  
  .progress-steps {
    gap: 3vw;
    margin-bottom: 4vh;
  }
  
  .error-hint {
    padding: 1.5vh 3vw;
  }
}

@media (max-height: 600px) and (orientation: landscape) {
  .loading-page {
    padding-top: 2vh;
    padding-bottom: 2vh;
  }
  
  .content {
    padding: 2vh 0;
  }
  
  .loading-animation,
  .complete-animation {
    margin-bottom: 2vh;
  }
  
  .progress-steps {
    margin-bottom: 3vh;
  }
}
</style>
