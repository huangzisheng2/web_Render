<template>
  <div class="landing-page">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>
    
    <!-- 主内容区 -->
    <div class="content-wrapper">
      <!-- Logo区域 -->
      <div class="logo-section">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 6v6l4 2"/>
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
          </svg>
        </div>
        <h1 class="main-title">先天天赋探索</h1>
        <p class="subtitle">融合东方智慧分析独特潜能</p>
      </div>
      
      <!-- 介绍卡片 -->
      <div class="intro-card">
        <div class="feature-list">
          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
              </svg>
            </div>
            <div class="feature-text">
              <h3>了解你的天赋优势</h3>
              <p>通过传统命理智慧，发现你与生俱来的潜能</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
            </div>
            <div class="feature-text">
              <h3>探索适合的发展方向</h3>
              <p>找到与你性格特质相匹配的成长路径</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
              </svg>
            </div>
            <div class="feature-text">
              <h3>获得个性化建议</h3>
              <p>AI智能分析，为你提供专属的成长指南</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 免责声明 -->
      <div class="disclaimer">
        <p>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
          </svg>
          本测试为成长娱乐参考，非科学诊断
        </p>
        <p>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          不收集敏感信息，数据仅临时使用
        </p>
      </div>
      
      <!-- 开始按钮 -->
      <button class="start-btn" @click="$emit('start')">
        <span>开始探索</span>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
defineEmits(['start'])
</script>

<style scoped>
.landing-page {
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
  opacity: 0.15;
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
  bottom: 10%;
  left: -10%;
}

.circle-3 {
  width: 30vw;
  height: 30vw;
  max-width: 150px;
  max-height: 150px;
  background: linear-gradient(135deg, #DDBEA9 0%, #E8D5C4 100%);
  bottom: 20%;
  right: 5%;
}

/* 内容区 */
.content-wrapper {
  max-width: 90vw;
  width: 100%;
  max-width: 400px;
  text-align: center;
  z-index: 1;
  padding: 4vh 0;
}

/* Logo区域 */
.logo-section {
  margin-bottom: 4vh;
}

.logo-icon {
  width: 20vw;
  height: 20vw;
  max-width: 88px;
  max-height: 88px;
  min-width: 72px;
  min-height: 72px;
  margin: 0 auto 3vh;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(142, 197, 252, 0.4);
  animation: breathe 3s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { box-shadow: 0 8px 24px rgba(142, 197, 252, 0.4); }
  50% { box-shadow: 0 8px 32px rgba(142, 197, 252, 0.6); }
}

.logo-icon svg {
  width: 50%;
  height: 50%;
  color: white;
}

.main-title {
  font-size: clamp(1.5rem, 6.5vw, 1.75rem);
  font-weight: 700;
  color: #4A5568;
  margin: 0 0 1vh;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: clamp(0.9375rem, 4vw, 1rem);
  color: #718096;
  margin: 0;
}

/* 介绍卡片 */
.intro-card {
  background: white;
  border-radius: 20px;
  padding: 4vh 5vw;
  margin-bottom: 3vh;
  box-shadow: 0 4px 16px rgba(142, 197, 252, 0.1);
  border: 1px solid rgba(142, 197, 252, 0.2);
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 3vh;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 4vw;
  text-align: left;
}

.feature-icon {
  width: 12vw;
  height: 12vw;
  max-width: 48px;
  max-height: 48px;
  min-width: 40px;
  min-height: 40px;
  background: linear-gradient(135deg, #F0F9FF 0%, #F0FFF4 100%);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid rgba(142, 197, 252, 0.3);
}

.feature-icon svg {
  width: 50%;
  height: 50%;
  color: #8EC5FC;
}

.feature-text h3 {
  font-size: clamp(0.9375rem, 4vw, 1rem);
  font-weight: 600;
  color: #4A5568;
  margin: 0 0 1vh;
}

.feature-text p {
  font-size: clamp(0.8125rem, 3.5vw, 0.875rem);
  color: #718096;
  margin: 0;
  line-height: 1.5;
}

/* 免责声明 */
.disclaimer {
  margin-bottom: 4vh;
  padding: 2vh 4vw;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(142, 197, 252, 0.2);
}

.disclaimer p {
  font-size: clamp(0.6875rem, 3vw, 0.75rem);
  color: #718096;
  margin: 1vh 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5vw;
}

.disclaimer p:first-child {
  margin-top: 0;
}

.disclaimer p:last-child {
  margin-bottom: 0;
}

.disclaimer p svg {
  width: 3.5vw;
  max-width: 14px;
  min-width: 12px;
  height: auto;
  color: #A8E6CF;
  flex-shrink: 0;
}

/* 开始按钮 */
.start-btn {
  width: 100%;
  padding: 2.8vh 8vw;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: clamp(1.0625rem, 4.5vw, 1.125rem);
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2.5vw;
  box-shadow: 0 6px 20px rgba(142, 197, 252, 0.4);
  transition: all 0.3s ease;
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(142, 197, 252, 0.5);
}

.start-btn:active {
  transform: translateY(0);
}

.start-btn svg {
  width: 5vw;
  max-width: 20px;
  min-width: 18px;
  height: auto;
}

/* 响应式 */
@media (max-width: 480px) {
  .intro-card {
    padding: 3vh 4vw;
  }
  
  .feature-list {
    gap: 2.5vh;
  }
  
  .disclaimer {
    padding: 1.8vh 3vw;
  }
}

/* 电脑端 */
@media (min-width: 1024px) {
  .landing-page {
    max-width: 480px;
    margin: 0 auto;
    box-shadow: 0 0 40px rgba(0, 0, 0, 0.1);
  }
  
  .content-wrapper {
    max-width: 400px;
    padding: 40px 20px;
  }
  
  .logo-icon {
    width: 72px;
    height: 72px;
    margin-bottom: 20px;
  }
  
  .main-title {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .intro-card {
    padding: 24px;
    margin-bottom: 20px;
  }
  
  .feature-icon {
    width: 44px;
    height: 44px;
  }
  
  .feature-text h3 {
    font-size: 15px;
  }
  
  .feature-text p {
    font-size: 13px;
  }
  
  .disclaimer {
    padding: 16px;
    margin-bottom: 24px;
  }
  
  .start-btn {
    padding: 16px 32px;
    font-size: 16px;
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  .content-wrapper {
    max-width: 440px;
  }
}

/* 横屏适配 */
@media (max-height: 600px) and (orientation: landscape) {
  .landing-page {
    padding-top: 2vh;
    padding-bottom: 2vh;
  }
  
  .content-wrapper {
    padding: 2vh 0;
  }
  
  .logo-section {
    margin-bottom: 2.5vh;
  }
  
  .logo-icon {
    margin-bottom: 2vh;
  }
  
  .intro-card {
    padding: 2.5vh 4vw;
    margin-bottom: 2.5vh;
  }
  
  .feature-list {
    gap: 2vh;
  }
  
  .disclaimer {
    margin-bottom: 2.5vh;
  }
}
</style>
