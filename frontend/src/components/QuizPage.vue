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
  // 这里可以处理答题结果，然后进入信息填写页
  emit('complete', answers.value)
}
</script>

<style scoped>
.quiz-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #F0F9FF 0%, #FDFCF8 50%, #F0FFF4 100%);
  padding: 20px;
  display: flex;
  flex-direction: column;
}

/* 进度条 */
.progress-bar {
  width: 100%;
  height: 4px;
  background: rgba(142, 197, 252, 0.2);
  border-radius: 2px;
  margin-bottom: 32px;
  overflow: hidden;
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
  max-width: 400px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
}

/* 题号 */
.question-number {
  text-align: center;
  margin-bottom: 24px;
}

.current {
  font-size: 32px;
  font-weight: 700;
  color: #8EC5FC;
}

.total {
  font-size: 16px;
  color: #A0AEC0;
}

/* 问题卡片 */
.question-card {
  background: white;
  border-radius: 20px;
  padding: 28px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(142, 197, 252, 0.1);
  border: 1px solid rgba(142, 197, 252, 0.2);
  flex: 1;
}

.question-text {
  font-size: 17px;
  font-weight: 600;
  color: #4A5568;
  margin: 0 0 24px;
  line-height: 1.7;
}

/* 问题强调样式 - 针对趣味抽象问题 */
.question-text::before {
  content: '"';
  color: #8EC5FC;
  font-size: 24px;
  font-weight: 700;
  margin-right: 4px;
  line-height: 1;
}

.question-text::after {
  content: '"';
  color: #8EC5FC;
  font-size: 24px;
  font-weight: 700;
  margin-left: 4px;
  line-height: 1;
}

/* 选项列表 */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-btn {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
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
  width: 28px;
  height: 28px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #8EC5FC;
  font-size: 13px;
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
  font-size: 15px;
  color: #4A5568;
  line-height: 1.6;
  flex: 1;
}

/* 选项描述文字样式 */
.option-text .desc {
  color: #718096;
  font-size: 13px;
}

/* 导航按钮 */
.nav-buttons {
  display: flex;
  gap: 12px;
  margin-top: auto;
}

.nav-btn {
  flex: 1;
  padding: 16px 24px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  border: none;
}

.nav-btn svg {
  width: 18px;
  height: 18px;
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
  font-size: 13px;
  color: #A0AEC0;
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.quiz-tip svg {
  width: 16px;
  height: 16px;
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
    padding: 16px;
  }
  
  .progress-bar {
    margin-bottom: 24px;
  }
  
  .question-number {
    margin-bottom: 16px;
  }
  
  .current {
    font-size: 28px;
  }
  
  .question-card {
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 16px;
  }
  
  .question-text {
    font-size: 16px;
    line-height: 1.7;
    margin: 0 0 20px;
  }
  
  .question-text::before,
  .question-text::after {
    font-size: 20px;
  }
  
  .options-list {
    gap: 10px;
  }
  
  .option-btn {
    padding: 14px;
    border-radius: 10px;
  }
  
  .option-letter {
    width: 26px;
    height: 26px;
    font-size: 12px;
  }
  
  .option-text {
    font-size: 14px;
    line-height: 1.6;
  }
  
  .nav-buttons {
    gap: 10px;
  }
  
  .nav-btn {
    padding: 14px 20px;
    font-size: 15px;
  }
  
  .quiz-tip {
    font-size: 12px;
    margin-top: 16px;
  }
}

@media (max-width: 480px) {
  .question-card {
    padding: 16px;
  }
  
  .question-text {
    font-size: 15px;
  }
  
  .option-btn {
    padding: 12px;
  }
  
  .option-text {
    font-size: 14px;
  }
  
  .nav-btn {
    padding: 12px 16px;
  }
}
</style>