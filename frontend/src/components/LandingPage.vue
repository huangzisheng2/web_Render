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
        <h1 class="main-title">青少年天赋探索</h1>
        <p class="subtitle">发现你的独特潜能</p>
      </div>
      
      <!-- 介绍卡片 -->
      <div class="intro-card">
        <div class="feature-list">
          <div class="feature-item">
            <div class="feature-icon">🎯</div>
            <div class="feature-text">
              <h3>了解你的天赋优势</h3>
              <p>通过传统命理智慧，发现你与生俱来的潜能</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">🌟</div>
            <div class="feature-text">
              <h3>探索适合的发展方向</h3>
              <p>找到与你性格特质相匹配的成长路径</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">💡</div>
            <div class="feature-text">
              <h3>获得个性化建议</h3>
              <p>AI智能分析，为你提供专属的成长指南</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 免责声明 -->
      <div class="disclaimer">
        <p>📌 本测试为成长娱乐参考，非科学诊断</p>
        <p>🔒 不收集敏感信息，数据仅临时使用</p>
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
  background: linear-gradient(135deg, #e8f4f8 0%, #f5f0e8 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
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
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #7dd3c0 0%, #a8d5ba 100%);
  top: -100px;
  right: -100px;
}

.circle-2 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #87ceeb 0%, #b8d4e3 100%);
  bottom: 10%;
  left: -50px;
}

.circle-3 {
  width: 150px;
  height: 150px;
  background: linear-gradient(135deg, #f5deb3 0%, #fae5c3 100%);
  bottom: 20%;
  right: 10%;
}

/* 内容区 */
.content-wrapper {
  max-width: 400px;
  width: 100%;
  text-align: center;
  z-index: 1;
}

/* Logo区域 */
.logo-section {
  margin-bottom: 32px;
}

.logo-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #7dd3c0 0%, #5fb3a3 100%);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(125, 211, 192, 0.3);
}

.logo-icon svg {
  width: 40px;
  height: 40px;
  color: white;
}

.main-title {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
}

/* 介绍卡片 */
.intro-card {
  background: white;
  border-radius: 20px;
  padding: 28px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  text-align: left;
}

.feature-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #f5f0e8 0%, #e8f4f8 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.feature-text h3 {
  font-size: 15px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 4px;
}

.feature-text p {
  font-size: 13px;
  color: #95a5a6;
  margin: 0;
  line-height: 1.5;
}

/* 免责声明 */
.disclaimer {
  margin-bottom: 28px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  border: 1px solid rgba(125, 211, 192, 0.2);
}

.disclaimer p {
  font-size: 12px;
  color: #7f8c8d;
  margin: 4px 0;
}

/* 开始按钮 */
.start-btn {
  width: 100%;
  padding: 18px 32px;
  background: linear-gradient(135deg, #7dd3c0 0%, #5fb3a3 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 6px 20px rgba(125, 211, 192, 0.4);
  transition: all 0.3s ease;
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(125, 211, 192, 0.5);
}

.start-btn:active {
  transform: translateY(0);
}

.start-btn svg {
  width: 20px;
  height: 20px;
}

/* 响应式 */
@media (max-width: 480px) {
  .main-title {
    font-size: 24px;
  }
  
  .intro-card {
    padding: 20px;
  }
  
  .feature-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  
  .feature-text h3 {
    font-size: 14px;
  }
  
  .feature-text p {
    font-size: 12px;
  }
}
</style>