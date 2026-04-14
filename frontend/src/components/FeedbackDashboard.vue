<template>
  <div class="feedback-dashboard-container">
    <div class="dashboard-header">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
      </svg>
      <h3>用户反馈数据看板</h3>
    </div>
    
    <!-- 操作按钮 -->
    <div class="action-bar">
      <button @click="loadFeedbackStats" :disabled="loading" class="refresh-btn">
        <svg v-if="!loading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="23 4 23 10 17 10"/>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
        </svg>
        <svg v-else class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
        </svg>
        {{ loading ? '加载中...' : '刷新数据' }}
      </button>
      <button @click="exportFeedbackCSV" :disabled="exporting" class="export-btn">
        <svg v-if="!exporting" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        <svg v-else class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
        </svg>
        {{ exporting ? '导出中...' : '导出CSV' }}
      </button>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在加载反馈数据...</p>
    </div>
    
    <!-- 错误提示 -->
    <div v-else-if="error" class="error-message">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      <p>{{ error }}</p>
    </div>
    
    <!-- 数据展示 -->
    <div v-else-if="stats" class="dashboard-content">
      <!-- 统计摘要卡片 -->
      <div class="stats-cards">
        <div class="stat-card primary">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">总反馈数</div>
        </div>
        <div class="stat-card secondary">
          <div class="stat-value">{{ stats.avg_rating }}</div>
          <div class="stat-label">平均评分</div>
        </div>
        <div class="stat-card success">
          <div class="stat-value">{{ stats.rating_distribution['5'] || 0 }}</div>
          <div class="stat-label">五星好评</div>
        </div>
      </div>
      
      <!-- 星级分布 -->
      <div class="rating-distribution">
        <h4>星级分布</h4>
        <div class="rating-grid">
          <div v-for="star in 5" :key="star" class="rating-item">
            <div class="stars">{{ '★'.repeat(star) }}</div>
            <div class="count">{{ stats.rating_distribution[star] || 0 }}</div>
            <div class="label">{{ star }}星</div>
          </div>
        </div>
      </div>
      
      <!-- 评分分布图表 -->
      <div class="chart-section">
        <h4>评分分布图表</h4>
        <div class="chart-container">
          <canvas ref="chartCanvas"></canvas>
        </div>
      </div>
      
      <!-- 最新评论列表 -->
      <div class="comments-section">
        <h4>最新文字反馈 ({{ stats.recent_comments.length }}条)</h4>
        <div class="comments-list">
          <div v-if="stats.recent_comments.length === 0" class="no-comments">
            暂无文字反馈
          </div>
          <div 
            v-for="comment in stats.recent_comments" 
            :key="comment.id" 
            class="comment-item"
          >
            <div class="comment-header">
              <div class="comment-rating">
                <span v-for="n in (comment.ratings.overall || 0)" :key="n" class="star">★</span>
                <span v-if="!comment.ratings.overall" class="no-rating">未评分</span>
              </div>
              <div class="comment-time">{{ comment.created_at }}</div>
            </div>
            <div class="comment-text">
              {{ comment.comment || '无文字' }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div v-else class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      <p>点击"刷新数据"加载反馈统计</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import Chart from 'chart.js/auto'

const API_URL = import.meta.env.PROD 
  ? 'https://bazi-talent-api.onrender.com'
  : ''

const stats = ref(null)
const loading = ref(false)
const exporting = ref(false)
const error = ref(null)
const chartCanvas = ref(null)
let chartInstance = null

// 加载反馈统计数据
const loadFeedbackStats = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await fetch(`${API_URL}/admin/feedback/stats`, {
      headers: { 'X-Debug-Mode': 'true' }
    })
    
    if (response.status === 403) {
      error.value = '禁止访问：需要调试模式权限'
      return
    }
    
    const data = await response.json()
    
    if (data.success) {
      stats.value = data
      await nextTick()
      renderChart()
    } else {
      error.value = data.error || '加载失败'
    }
  } catch (err) {
    error.value = '网络错误：' + err.message
  } finally {
    loading.value = false
  }
}

// 渲染图表
const renderChart = () => {
  if (!chartCanvas.value || !stats.value) return
  
  if (chartInstance) {
    chartInstance.destroy()
  }
  
  const dist = stats.value.rating_distribution
  
  chartInstance = new Chart(chartCanvas.value, {
    type: 'bar',
    data: {
      labels: ['1星', '2星', '3星', '4星', '5星'],
      datasets: [{
        label: '反馈数量',
        data: [
          dist['1'] || 0,
          dist['2'] || 0,
          dist['3'] || 0,
          dist['4'] || 0,
          dist['5'] || 0
        ],
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',
          'rgba(249, 115, 22, 0.8)',
          'rgba(234, 179, 8, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)'
        ],
        borderColor: [
          'rgba(239, 68, 68, 1)',
          'rgba(249, 115, 22, 1)',
          'rgba(234, 179, 8, 1)',
          'rgba(34, 197, 94, 1)',
          'rgba(59, 130, 246, 1)'
        ],
        borderWidth: 1,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1 }
        }
      }
    }
  })
}

// 导出CSV
const exportFeedbackCSV = async () => {
  exporting.value = true
  
  try {
    const response = await fetch(`${API_URL}/admin/feedback/export`, {
      headers: { 'X-Debug-Mode': 'true' }
    })
    
    if (response.status === 403) {
      alert('❌ 禁止访问：需要调试模式权限')
      return
    }
    
    if (!response.ok) {
      throw new Error('导出失败')
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `feedback_${new Date().toISOString().slice(0,10)}.csv`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    
    alert('✅ CSV导出成功！')
  } catch (err) {
    alert('❌ 导出失败：' + err.message)
  } finally {
    exporting.value = false
  }
}

// 组件挂载时自动加载
onMounted(() => {
  loadFeedbackStats()
})
</script>

<style scoped>
.feedback-dashboard-container {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(142, 197, 252, 0.1);
  border: 1px solid rgba(142, 197, 252, 0.2);
}

.dashboard-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(142, 197, 252, 0.2);
}

.dashboard-header svg {
  width: 24px;
  height: 24px;
  color: #8EC5FC;
}

.dashboard-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #4A5568;
}

.action-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.action-bar button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.action-bar button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-btn {
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
}

.refresh-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(142, 197, 252, 0.4);
}

.export-btn {
  background: #F7FAFC;
  color: #4A5568;
  border: 2px solid #E2E8F0;
}

.export-btn:hover:not(:disabled) {
  border-color: #8EC5FC;
  color: #8EC5FC;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 40px;
  color: #718096;
}

.loading-state .spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #E2E8F0;
  border-top-color: #8EC5FC;
  border-radius: 50%;
  margin: 0 auto 16px;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #FED7D7;
  color: #C53030;
  border-radius: 10px;
  margin-bottom: 20px;
}

.error-message svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  padding: 20px;
  border-radius: 12px;
  text-align: center;
}

.stat-card.primary {
  background: linear-gradient(135deg, #8EC5FC 0%, #6BB3F9 100%);
  color: white;
}

.stat-card.secondary {
  background: linear-gradient(135deg, #A8E6CF 0%, #8DD4B0 100%);
  color: white;
}

.stat-card.success {
  background: linear-gradient(135deg, #F6E05E 0%, #ECC94B 100%);
  color: #744210;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.rating-distribution {
  margin-bottom: 24px;
}

.rating-distribution h4 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #4A5568;
}

.rating-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.rating-item {
  text-align: center;
  padding: 16px;
  background: #F7FAFC;
  border-radius: 10px;
}

.rating-item .stars {
  color: #F6E05E;
  font-size: 18px;
  margin-bottom: 8px;
}

.rating-item .count {
  font-size: 24px;
  font-weight: 700;
  color: #4A5568;
  margin-bottom: 4px;
}

.rating-item .label {
  font-size: 12px;
  color: #718096;
}

.chart-section {
  margin-bottom: 24px;
}

.chart-section h4 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #4A5568;
}

.chart-container {
  height: 250px;
  background: #F7FAFC;
  border-radius: 10px;
  padding: 16px;
}

.comments-section h4 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #4A5568;
}

.comments-list {
  max-height: 400px;
  overflow-y: auto;
}

.no-comments {
  text-align: center;
  padding: 40px;
  color: #A0AEC0;
}

.comment-item {
  padding: 16px;
  background: #F7FAFC;
  border-radius: 10px;
  margin-bottom: 12px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.comment-rating {
  display: flex;
  gap: 2px;
}

.comment-rating .star {
  color: #F6E05E;
  font-size: 14px;
}

.comment-rating .no-rating {
  color: #A0AEC0;
  font-size: 12px;
}

.comment-time {
  font-size: 12px;
  color: #A0AEC0;
}

.comment-text {
  font-size: 14px;
  color: #4A5568;
  line-height: 1.6;
}

@media (max-width: 640px) {
  .feedback-dashboard-container {
    padding: 16px;
  }
  
  .stats-cards {
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .stat-label {
    font-size: 12px;
  }
  
  .rating-grid {
    gap: 8px;
  }
  
  .rating-item {
    padding: 12px 8px;
  }
  
  .rating-item .stars {
    font-size: 14px;
  }
  
  .rating-item .count {
    font-size: 18px;
  }
}
</style>