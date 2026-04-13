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
              <span class="option-letter">{{ ['A', 'B', 'C'][idx] }}</span>
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
    <p class="quiz-tip">💡 没有标准答案，凭直觉选择最符合你的选项</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['complete'])

// 趣味测试题目
const questions = [
  {
    text: '闲下来时，你更喜欢：',
    options: ['对着天空发呆瞎想', '拆解小物件研究', '找朋友聊天玩耍']
  },
  {
    text: '朋友找你吐槽时，你更会：',
    options: ['帮TA出主意想办法', '安静听TA说完', '带TA去做点开心的事']
  },
  {
    text: '看到一幅抽象画，你的第一反应是：',
    options: ['猜作者想表达什么', '自己编个小故事', '关注色彩搭配好不好看']
  },
  {
    text: '学习新技能时，你更在意：',
    options: ['学会后的成就感', '学习过程好不好玩', '能不能马上用起来']
  },
  {
    text: '遇到难题时，你通常：',
    options: ['硬磕到底直到解决', '换个轻松的方式绕开', '找人一起讨论']
  },
  {
    text: '你更喜欢哪种周末安排：',
    options: ['一个人静静看书', '和好朋友聚会', '尝试新的活动或运动']
  }
]

const currentIndex = ref(0)
const answers = ref([])

const currentQuestion = computed(() => questions[currentIndex.value])
const progress = computed(() => ((currentIndex.value + 1) / questions.length) * 100)

const selectOption = (idx) => {
  answers.value[currentIndex.value] = idx
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
  background: linear-gradient(135deg, #e8f4f8 0%, #f5f0e8 100%);
  padding: 20px;
  display: flex;
  flex-direction: column;
}

/* 进度条 */
.progress-bar {
  width: 100%;
  height: 4px;
  background: rgba(125, 211, 192, 0.2);
  border-radius: 2px;
  margin-bottom: 32px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #7dd3c0 0%, #5fb3a3 100%);
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
  color: #7dd3c0;
}

.total {
  font-size: 16px;
  color: #95a5a6;
}

/* 问题卡片 */
.question-card {
  background: white;
  border-radius: 20px;
  padding: 28px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  flex: 1;
}

.question-text {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 24px;
  line-height: 1.6;
}

/* 选项列表 */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.option-btn:hover {
  background: #e8f4f8;
  border-color: #7dd3c0;
}

.option-btn.selected {
  background: linear-gradient(135deg, #e8f4f8 0%, #d4ede6 100%);
  border-color: #7dd3c0;
}

.option-letter {
  width: 32px;
  height: 32px;
  background: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #7dd3c0;
  font-size: 14px;
  flex-shrink: 0;
}

.option-btn.selected .option-letter {
  background: #7dd3c0;
  color: white;
}

.option-text {
  font-size: 15px;
  color: #2c3e50;
  line-height: 1.5;
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
  color: #7f8c8d;
  border: 2px solid #e0e0e0;
}

.nav-btn.prev:hover {
  border-color: #7dd3c0;
  color: #7dd3c0;
}

.nav-btn.next,
.nav-btn.submit {
  background: linear-gradient(135deg, #7dd3c0 0%, #5fb3a3 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(125, 211, 192, 0.3);
}

.nav-btn.next:hover,
.nav-btn.submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(125, 211, 192, 0.4);
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
  color: #95a5a6;
  margin-top: 20px;
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

/* 响应式 */
@media (max-width: 480px) {
  .question-card {
    padding: 20px;
  }
  
  .question-text {
    font-size: 16px;
  }
  
  .option-text {
    font-size: 14px;
  }
}
</style>