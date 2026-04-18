<template>
  <div class="quiz-page">
    <!-- 进度条 -->
    <div class="progress-bar">
      <div class="progress-fill" :style="{ width: progress + '%' }"></div>
    </div>
    
    <!-- 主内容 -->
    <div class="quiz-container">
      <!-- 题号 -->
      <div class="question-number">
        <span class="current">{{ currentIndex + 1 }}</span>
        <span class="total">/ {{ questions.length }}</span>
      </div>
      
      <!-- 问题卡片 -->
      <transition name="slide" mode="out-in">
        <div class="question-card" :key="currentIndex">
          <h2 class="question-text">{{ currentQuestion.text }}</h2>
          
          <div class="options-list">
            <button
              v-for="(option, idx) in currentQuestion.options"
              :key="idx"
              class="option-btn"
              :class="{ selected: answers[currentIndex] === idx }"
              @click="selectOption(idx)"
            >
              <span class="option-letter">{{ ['A', 'B', 'C', 'D'][idx] }}</span>
              <span class="option-text">{{ option }}</span>
            </button>
          </div>
        </div>
      </transition>
      
      <!-- 导航按钮 -->
      <div class="nav-buttons">
        <button 
          v-if="currentIndex > 0" 
          class="nav-btn prev"
          @click="prevQuestion"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          上一题
        </button>
        
        <button 
          v-if="currentIndex < questions.length - 1" 
          class="nav-btn next"
          :disabled="answers[currentIndex] === undefined"
          @click="nextQuestion"
        >
          下一题
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </button>
        
        <button 
          v-else 
          class="nav-btn submit"
          :disabled="answers[currentIndex] === undefined"
          @click="submitQuiz"
        >
          完成
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
        </button>
      </div>
    </div>
    
    <!-- 提示文字 -->
    <p class="quiz-tip">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="16" x2="12" y2="12"/>
        <line x1="12" y1="8" x2="12.01" y2="8"/>
      </svg>
      没有标准答案，凭直觉选择最符合你的选项
    </p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['complete'])

// 趣味测试题目
const questions = [
  {
    text: '你发现床底下有一双拖鞋，但它们正在小声商量什么？',
    options: ['今晚往东跑', '把你变成袜子', '辞职', '它们其实是一对']
  },
  {
    text: '你面前有一堵墙，墙在对你眨眼睛，你会？',
    options: ['也眨回去', '问它今天星期几', '假装没看见', '拆了它']
  },
  {
    text: '你的影子突然站起来，自己走了，临走前它对你说了一句话，是？',
    options: ['我先下班了', '你太重了', '换个方向试试', '别等我']
  },
  {
    text: '冰箱里的灯有一天开口问你："我到底是灯还是冰箱？"你怎么回答？',
    options: ['你是我心里的光', '你是冰箱的歌手', '你是凉的', '别问了，关门']
  },
  {
    text: '你走在路上，忽然从天上下起了"选择题"，选项有四个：甲、乙、丙、丁。你会？',
    options: ['选戊', '举报老天', '打伞继续走', '把它们全部吃掉']
  },
  {
    text: '你收到一条来自"昨天"的短信，内容是："别忘了明天要做什么。"你会？',
    options: ['回复"好的"', '问"你是谁"', '删除', '把它转发给"后天"']
  }
]

const currentIndex = ref(0)
const answers = ref([])

const currentQuestion = computed(() => questions[currentIndex.value])
const progress = computed(() => ((currentIndex.value + 1) / questions.length) * 100)

const selectOption = (idx) => {
  answers.value[currentIndex.value] = idx
  // 自动下一题，最后一题不自动跳转
  if (currentIndex.value < questions.length - 1) {
    setTimeout(() => {
      currentIndex.value++
    }, 300)
  }
}

const nextQuestion = () => {
  if (currentIndex.value < questions.length - 1) {
    currentIndex.value++
  }
}

const prevQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

const submitQuiz = () => {
  emit('complete', answers.value)
}
</script>

<style scoped>
.quiz-page {
  min-height: 100vh;
  min-height: 100dvh;
  background: linear-gradient(180deg, #F0F9FF 0%, #FDFCF8 50%, #F0FFF4 100%);
  padding: env(safe-area-inset-top) 5vw env(safe-area-inset-bottom);
  display: flex;
  flex-direction: column;
}

/* 进度条 */
.progress-bar {
  width: 100%;
  height: 4px;
  background: rgba(142, 197, 252, 0.2);
  border-radius: 2px;
  margin-bottom: 4vh;
  overflow: hidden;
  flex-shrink: 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8EC5FC 0%, #A8E6CF 100%);
  border-radius: 2px;
  transition: width 0.3s ease;
}

/* 主容器 */
.quiz-container {
  flex: 1;
  max-width: 100%;
  width: 100%;
  max-width: 520px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
}

/* 题号 */
.question-number {
  text-align: center;
  margin-bottom: 3vh;
}

.current {
  font-size: clamp(1.75rem, 7vw, 2rem);
  font-weight: 700;
  color: #8EC5FC;
}

.total {
  font-size: clamp(1rem, 4vw, 1.125rem);
  color: #A0AEC0;
}

/* 问题卡片 */
.question-card {
  background: white;
  border-radius: 20px;
  padding: 4vh 5vw;
  margin-bottom: 3vh;
  box-shadow: 0 4px 16px rgba(142, 197, 252, 0.1);
  border: 1px solid rgba(142, 197, 252, 0.2);
  flex: 1;
  display: flex;
  flex-direction: column;
}

.question-text {
  font-size: clamp(1rem, 4.2vw, 1.125rem);
  font-weight: 600;
  color: #4A5568;
  margin: 0 0 3vh;
  line-height: 1.7;
}

/* 问题强调样式 - 针对趣味抽象问题 */
.question-text::before {
  content: '"';
  color: #8EC5FC;
  font-size: clamp(1.25rem, 5vw, 1.5rem);
  font-weight: 700;
  margin-right: 4px;
  line-height: 1;
}

.question-text::after {
  content: '"';
  color: #8EC5FC;
  font-size: clamp(1.25rem, 5vw, 1.5rem);
  font-weight: 700;
  margin-left: 4px;
  line-height: 1;
}

/* 选项列表 */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 2vh;
  flex: 1;
}

.option-btn {
  display: flex;
  align-items: flex-start;
  gap: 3vw;
  padding: 2.5vh 4vw;
  background: #F7FAFC;
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.option-btn:hover {
  background: #F0F9FF;
  border-color: #8EC5FC;
  transform: translateY(-1px);
}

.option-btn.selected {
  background: linear-gradient(135deg, #F0F9FF 0%, #F0FFF4 100%);
  border-color: #8EC5FC;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(142, 197, 252, 0.2);
}

.option-letter {
  width: 7vw;
  height: 7vw;
  max-width: 28px;
  max-height: 28px;
  min-width: 24px;
  min-height: 24px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #8EC5FC;
  font-size: clamp(0.8125rem, 3.5vw, 0.875rem);
  flex-shrink: 0;
  border: 2px solid rgba(142, 197, 252, 0.4);
  margin-top: 2px;
}

.option-btn.selected .option-letter {
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  border-color: transparent;
}

.option-text {
  font-size: clamp(0.9375rem, 4vw, 1rem);
  color: #4A5568;
  line-height: 1.6;
  flex: 1;
}

/* 选项描述文字样式 */
.option-text .desc {
  color: #718096;
  font-size: clamp(0.8125rem, 3.5vw, 0.875rem);
}

/* 导航按钮 */
.nav-buttons {
  display: flex;
  gap: 3vw;
  margin-top: auto;
  flex-shrink: 0;
}

.nav-btn {
  flex: 1;
  padding: 2.5vh 5vw;
  border-radius: 12px;
  font-size: clamp(0.9375rem, 4vw, 1rem);
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2vw;
  transition: all 0.3s ease;
  border: none;
}

.nav-btn svg {
  width: 5vw;
  max-width: 18px;
  min-width: 16px;
  height: auto;
}

.nav-btn.prev {
  background: white;
  color: #718096;
  border: 2px solid #E2E8F0;
}

.nav-btn.prev:hover {
  border-color: #8EC5FC;
  color: #8EC5FC;
}

.nav-btn.next,
.nav-btn.submit {
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(142, 197, 252, 0.3);
}

.nav-btn.next:hover,
.nav-btn.submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(142, 197, 252, 0.4);
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

/* 提示文字 */
.quiz-tip {
  text-align: center;
  font-size: clamp(0.8125rem, 3.5vw, 0.875rem);
  color: #A0AEC0;
  margin-top: 3vh;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5vw;
  flex-shrink: 0;
}

.quiz-tip svg {
  width: 4vw;
  max-width: 16px;
  min-width: 14px;
  height: auto;
  color: #8EC5FC;
}

/* 过渡动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* 响应式 - 手机端优化 */
@media (max-width: 640px) {
  .quiz-page {
    padding: env(safe-area-inset-top) 4vw env(safe-area-inset-bottom);
  }
  
  .progress-bar {
    margin-bottom: 3vh;
  }
  
  .question-number {
    margin-bottom: 2.5vh;
  }
  
  .question-card {
    padding: 3vh 4vw;
    border-radius: 16px;
    margin-bottom: 2.5vh;
  }
  
  .options-list {
    gap: 1.8vh;
  }
  
  .option-btn {
    padding: 2.2vh 3.5vw;
  }
}

@media (max-width: 480px) {
  .question-card {
    padding: 2.5vh 4vw;
    border-radius: 14px;
  }
  
  .question-text {
    margin-bottom: 2.5vh;
  }
  
  .option-btn {
    padding: 2vh 3vw;
    gap: 2.5vw;
  }
  
  .nav-buttons {
    gap: 2.5vw;
  }
  
  .nav-btn {
    padding: 2.2vh 4vw;
  }
}

/* 横屏适配 */
@media (max-height: 600px) and (orientation: landscape) {
  .quiz-page {
    padding-top: 2vh;
    padding-bottom: 2vh;
  }
  
  .progress-bar {
    margin-bottom: 2vh;
  }
  
  .question-number {
    margin-bottom: 2vh;
  }
  
  .question-card {
    padding: 2.5vh 4vw;
    margin-bottom: 2vh;
  }
  
  .options-list {
    gap: 1.5vh;
  }
  
  .option-btn {
    padding: 2vh 3vw;
  }
  
  .quiz-tip {
    margin-top: 2vh;
  }
}

/* 电脑端 */
@media (min-width: 1024px) {
  .quiz-page {
    max-width: 600px;
    margin: 0 auto;
    box-shadow: 0 0 40px rgba(0, 0, 0, 0.1);
    padding: 48px 32px;
  }
  
  .quiz-container {
    max-width: 520px;
  }
  
  .progress-bar {
    margin-bottom: 24px;
  }
  
  .question-number {
    margin-bottom: 20px;
  }
  
  .current {
    font-size: 28px;
  }
  
  .total {
    font-size: 16px;
  }
  
  .question-card {
    padding: 32px;
    margin-bottom: 24px;
  }
  
  .question-text {
    font-size: 17px;
    margin-bottom: 24px;
  }
  
  .options-list {
    gap: 12px;
  }
  
  .option-btn {
    padding: 16px 20px;
  }
  
  .option-letter {
    width: 28px;
    height: 28px;
  }
  
  .option-text {
    font-size: 15px;
  }
  
  .nav-buttons {
    gap: 12px;
  }
  
  .nav-btn {
    padding: 16px 24px;
    font-size: 15px;
  }
  
  .quiz-tip {
    margin-top: 24px;
    font-size: 13px;
  }
}
</style>
