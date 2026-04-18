<template>
  <div class="intro-page">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>
    
    <!-- 主内容区 -->
    <div class="content-wrapper">
      <!-- 顶部标题 -->
      <div class="header-section">
        <div class="header-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z"/>
            <path d="M12 6v6l4 2"/>
          </svg>
        </div>
        <h1 class="main-title">探索未知的自己</h1>
        <p class="subtitle">一次深度自我认知的旅程</p>
      </div>
      
      <!-- 介绍卡片列表 -->
      <div class="intro-cards">
        <!-- 卡片1：天赋测试的意义 -->
        <div class="intro-card">
          <div class="card-icon blue">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
          </div>
          <div class="card-content">
            <h3>发现你的独特天赋</h3>
            <p>每个人都有与生俱来的潜能和优势。通过天赋测试，你可以更清晰地认识自己，找到那些被你忽视或未被发掘的才能。</p>
          </div>
        </div>
        
        <!-- 卡片2：自我探索的价值 -->
        <div class="intro-card">
          <div class="card-icon green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              <path d="M9 12l2 2 4-4"/>
            </svg>
          </div>
          <div class="card-content">
            <h3>自我探索的重要性</h3>
            <p>了解自己是一切成长的起点。当你真正认识自己的性格特质、行为模式和内在需求时，你才能做出更适合自己的选择。</p>
          </div>
        </div>
        
        <!-- 卡片3：认识自己的益处 -->
        <div class="intro-card">
          <div class="card-icon purple">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <div class="card-content">
            <h3>认识自己的益处</h3>
            <p>认识自己可以帮助你：找到适合的发展方向、改善人际关系、提升职业满意度、做出更明智的人生决策。</p>
          </div>
        </div>
        
        <!-- 卡片4：东方智慧的融合 -->
        <div class="intro-card">
          <div class="card-icon orange">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
          </div>
          <div class="card-content">
            <h3>传统智慧 + 现代 AI</h3>
            <p>本测试融合东方传统智慧与人工智能技术，通过分析你的出生信息，为你提供个性化的天赋解读和成长建议。</p>
          </div>
        </div>
      </div>
      
      <!-- 流程说明 -->
      <div class="process-section">
        <h3 class="process-title">测试流程</h3>
        <div class="process-steps">
          <div class="process-step">
            <div class="step-number">1</div>
            <span>填写信息</span>
          </div>
          <div class="step-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </div>
          <div class="process-step">
            <div class="step-number">2</div>
            <span>趣味答题</span>
          </div>
          <div class="step-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </div>
          <div class="process-step">
            <div class="step-number">3</div>
            <span>获取报告</span>
          </div>
        </div>
      </div>
      
      <!-- 底部按钮 -->
      <div class="action-section">
        <button class="next-btn" @click="$emit('next')">
          <span>下一步</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </button>
        <p class="hint-text">仅需 2-3 分钟，即可获得你的专属报告</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineEmits(['next'])
</script>

<style scoped>
.intro-page {
  min-height: 100vh;
  min-height: 100dvh; /* 适配刘海屏 */
  background: linear-gradient(180deg, #F0F9FF 0%, #FDFCF8 50%, #F0FFF4 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: env(safe-area-inset-top) 5vw env(safe-area-inset-bottom); /* 安全区适配 */
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.12;
}

.circle-1 {
  width: 60vw;
  height: 60vw;
  max-width: 300px;
  max-height: 300px;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  top: -10%;
  right: -15%;
}

.circle-2 {
  width: 40vw;
  height: 40vw;
  max-width: 200px;
  max-height: 200px;
  background: linear-gradient(135deg, #A8E6CF 0%, #DCEDC1 100%);
  bottom: 15%;
  left: -10%;
}

.circle-3 {
  width: 30vw;
  height: 30vw;
  max-width: 150px;
  max-height: 150px;
  background: linear-gradient(135deg, #DDBEA9 0%, #E8D5C4 100%);
  bottom: 25%;
  right: 5%;
}

/* 内容区 */
.content-wrapper {
  max-width: 90vw;
  width: 100%;
  max-width: 480px;
  text-align: center;
  z-index: 1;
  padding: 4vh 0;
}

/* 顶部标题 */
.header-section {
  margin-bottom: 4vh;
}

.header-icon {
  width: 16vw;
  height: 16vw;
  max-width: 72px;
  max-height: 72px;
  min-width: 56px;
  min-height: 56px;
  margin: 0 auto 2vh;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  border-radius: 24%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(142, 197, 252, 0.4);
}

.header-icon svg {
  width: 50%;
  height: 50%;
  color: white;
}

.main-title {
  font-size: clamp(1.5rem, 6vw, 1.75rem);
  font-weight: 700;
  color: #4A5568;
  margin: 0 0 1vh;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: clamp(0.875rem, 3.5vw, 1rem);
  color: #718096;
  margin: 0;
}

/* 介绍卡片 */
.intro-cards {
  display: flex;
  flex-direction: column;
  gap: 2vh;
  margin-bottom: 4vh;
}

.intro-card {
  background: white;
  border-radius: 16px;
  padding: 3vh 4vw;
  display: flex;
  align-items: flex-start;
  gap: 3vw;
  text-align: left;
  box-shadow: 0 4px 16px rgba(142, 197, 252, 0.1);
  border: 1px solid rgba(142, 197, 252, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.intro-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(142, 197, 252, 0.15);
}

.card-icon {
  width: 12vw;
  height: 12vw;
  max-width: 48px;
  max-height: 48px;
  min-width: 40px;
  min-height: 40px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-icon svg {
  width: 55%;
  height: 55%;
  color: white;
}

.card-icon.blue {
  background: linear-gradient(135deg, #8EC5FC 0%, #6B9BD0 100%);
}

.card-icon.green {
  background: linear-gradient(135deg, #A8E6CF 0%, #7BC8A0 100%);
}

.card-icon.purple {
  background: linear-gradient(135deg, #C9B1FF 0%, #A78BFA 100%);
}

.card-icon.orange {
  background: linear-gradient(135deg, #FFD3A5 0%, #FD9853 100%);
}

.card-content {
  flex: 1;
}

.card-content h3 {
  font-size: clamp(0.9375rem, 4vw, 1rem);
  font-weight: 600;
  color: #4A5568;
  margin: 0 0 1vh;
}

.card-content p {
  font-size: clamp(0.8125rem, 3.5vw, 0.875rem);
  color: #718096;
  margin: 0;
  line-height: 1.6;
}

/* 流程说明 */
.process-section {
  margin-bottom: 4vh;
  padding: 3vh 4vw;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 16px;
  border: 1px solid rgba(142, 197, 252, 0.2);
}

.process-title {
  font-size: clamp(0.875rem, 3.5vw, 1rem);
  font-weight: 600;
  color: #4A5568;
  margin: 0 0 2vh;
}

.process-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2vw;
  flex-wrap: wrap;
}

.process-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1vh;
}

.step-number {
  width: 10vw;
  height: 10vw;
  max-width: 40px;
  max-height: 40px;
  min-width: 32px;
  min-height: 32px;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: clamp(0.875rem, 3.5vw, 1rem);
  font-weight: 700;
  color: white;
}

.process-step span {
  font-size: clamp(0.75rem, 3vw, 0.8125rem);
  color: #718096;
  font-weight: 500;
}

.step-arrow {
  width: 5vw;
  max-width: 20px;
  min-width: 16px;
  color: #A0AEC0;
}

.step-arrow svg {
  width: 100%;
  height: 100%;
}

/* 底部按钮 */
.action-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2vh;
}

.next-btn {
  width: 100%;
  max-width: 320px;
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
  box-shadow: 0 6px 20px rgba(142, 197, 252, 0.4);
  transition: all 0.3s ease;
}

.next-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(142, 197, 252, 0.5);
}

.next-btn:active {
  transform: translateY(0);
}

.next-btn svg {
  width: 5vw;
  max-width: 20px;
  min-width: 18px;
  height: auto;
}

.hint-text {
  font-size: clamp(0.75rem, 3vw, 0.8125rem);
  color: #A0AEC0;
  margin: 0;
}

/* 响应式优化 */
@media (max-width: 480px) {
  .intro-card {
    padding: 2.5vh 4vw;
  }
  
  .process-section {
    padding: 2.5vh 3vw;
  }
  
  .process-steps {
    gap: 3vw;
  }
}

/* 电脑端 */
@media (min-width: 1024px) {
  .intro-page {
    max-width: 600px;
    margin: 0 auto;
    box-shadow: 0 0 40px rgba(0, 0, 0, 0.1);
  }
  
  .content-wrapper {
    max-width: 520px;
    padding: 48px 32px;
  }
  
  .header-icon {
    width: 64px;
    height: 64px;
    margin-bottom: 16px;
  }
  
  .main-title {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .header-section {
    margin-bottom: 24px;
  }
  
  .intro-cards {
    gap: 16px;
    margin-bottom: 24px;
  }
  
  .intro-card {
    padding: 16px 20px;
  }
  
  .card-icon {
    width: 44px;
    height: 44px;
  }
  
  .card-content h3 {
    font-size: 15px;
  }
  
  .card-content p {
    font-size: 13px;
  }
  
  .process-section {
    padding: 16px 20px;
    margin-bottom: 24px;
  }
  
  .next-btn {
    padding: 16px 32px;
    font-size: 16px;
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  .content-wrapper {
    max-width: 520px;
  }
  
  .intro-cards {
    gap: 2.5vh;
  }
}

/* 横屏适配 */
@media (max-height: 600px) and (orientation: landscape) {
  .intro-page {
    padding-top: 2vh;
    padding-bottom: 2vh;
  }
  
  .content-wrapper {
    padding: 2vh 0;
  }
  
  .header-section {
    margin-bottom: 2vh;
  }
  
  .intro-cards {
    gap: 1.5vh;
    margin-bottom: 2vh;
  }
  
  .intro-card {
    padding: 2vh 3vw;
  }
  
  .process-section {
    margin-bottom: 2vh;
    padding: 2vh 3vw;
  }
}

/* 适配灵动岛/刘海屏 */
@supports (padding-top: env(safe-area-inset-top)) {
  .intro-page {
    padding-top: max(env(safe-area-inset-top), 2vh);
    padding-bottom: max(env(safe-area-inset-bottom), 2vh);
  }
}
</style>
