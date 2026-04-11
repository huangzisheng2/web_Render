<template>
  <div class="energy-charts-container">
    <!-- 标题区 -->
    <div class="section-header">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 6v6l4 2"/>
        </svg>
      </div>
      <div class="header-content">
        <h3 class="header-title">能量分析</h3>
        <p class="header-subtitle">五行与十神能量分布可视化</p>
      </div>
    </div>

    <!-- 图表切换标签 -->
    <div class="chart-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.key"
        class="tab-btn"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 五行能量饼图 -->
      <div v-show="activeTab === 'wuxing'" class="chart-card">
        <div class="chart-title">原局五行能量占比</div>
        <div ref="wuxingChart" class="chart-container"></div>
        <div class="chart-legend">
          <div 
            v-for="(item, index) in wuxingData" 
            :key="index"
            class="legend-item"
          >
            <span class="legend-dot" :style="{ background: item.color }"></span>
            <span class="legend-name">{{ item.name }}</span>
            <span class="legend-value">{{ item.value.toFixed(1) }}</span>
            <span class="legend-percent">({{ getPercent(item.value, wuxingTotal) }}%)</span>
          </div>
        </div>
      </div>

      <!-- 十神能量饼图 -->
      <div v-show="activeTab === 'shishen'" class="chart-card">
        <div class="chart-title">原局十神能量占比</div>
        <div ref="shishenChart" class="chart-container"></div>
        <div class="chart-legend">
          <div 
            v-for="(item, index) in shishenData" 
            :key="index"
            class="legend-item"
          >
            <span class="legend-dot" :style="{ background: item.color }"></span>
            <span class="legend-name">{{ item.name }}</span>
            <span class="legend-value">{{ item.value.toFixed(1) }}</span>
            <span class="legend-percent">({{ getPercent(item.value, shishenTotal) }}%)</span>
          </div>
        </div>
      </div>

      <!-- 大运影响 -->
      <div v-show="activeTab === 'dayun'" class="chart-card">
        <div class="chart-title">大运流年作用后能量变化</div>
        <div ref="dayunChart" class="chart-container"></div>
        <div class="dayun-info" v-if="dayunData">
          <div class="info-item">
            <span class="info-label">当前大运：</span>
            <span class="info-value">{{ dayunData.ganzhi || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">能量变化：</span>
            <span class="info-value" :class="dayunData.trend">
              {{ dayunData.trend === 'up' ? '↑ 增强' : dayunData.trend === 'down' ? '↓ 减弱' : '→ 平稳' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 能量分析总结 -->
    <div class="energy-summary">
      <div class="summary-title">能量分析总结</div>
      <div class="summary-content">
        <div class="summary-item">
          <span class="summary-label">最强五行：</span>
          <span class="summary-value" :style="{ color: strongestWuxing.color }">
            {{ strongestWuxing.name }} ({{ strongestWuxing.value.toFixed(1) }})
          </span>
        </div>
        <div class="summary-item">
          <span class="summary-label">最强十神：</span>
          <span class="summary-value" :style="{ color: strongestShishen.color }">
            {{ strongestShishen.name }} ({{ strongestShishen.value.toFixed(1) }})
          </span>
        </div>
        <div class="summary-item">
          <span class="summary-label">五行平衡：</span>
          <span class="summary-value" :class="balanceStatus.class">
            {{ balanceStatus.text }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { getWuxingColor, getShishenColor } from '../utils/wuxing'

const props = defineProps({
  wuxingEnergy: {
    type: Object,
    default: () => ({})
  },
  shishenEnergy: {
    type: Object,
    default: () => ({})
  },
  dayunEnergy: {
    type: Object,
    default: () => null
  }
})

const activeTab = ref('wuxing')
const tabs = [
  { key: 'wuxing', label: '五行能量' },
  { key: 'shishen', label: '十神能量' },
  { key: 'dayun', label: '大运影响' }
]

// 图表引用
const wuxingChart = ref(null)
const shishenChart = ref(null)
const dayunChart = ref(null)
let charts = {}

// 五行数据
const wuxingData = computed(() => {
  const data = props.wuxingEnergy || {}
  return Object.entries(data)
    .map(([name, value]) => ({
      name,
      value: Number(value) || 0,
      color: getWuxingColor(name).primary
    }))
    .sort((a, b) => b.value - a.value)
})

const wuxingTotal = computed(() => {
  return wuxingData.value.reduce((sum, item) => sum + item.value, 0)
})

// 十神数据
const shishenData = computed(() => {
  const data = props.shishenEnergy || {}
  return Object.entries(data)
    .map(([name, value]) => ({
      name,
      value: Number(value) || 0,
      color: getShishenColor(name)
    }))
    .sort((a, b) => b.value - a.value)
})

const shishenTotal = computed(() => {
  return shishenData.value.reduce((sum, item) => sum + item.value, 0)
})

// 大运数据
const dayunData = computed(() => {
  return props.dayunEnergy
})

// 最强五行
const strongestWuxing = computed(() => {
  return wuxingData.value[0] || { name: '-', value: 0, color: '#999' }
})

// 最强十神
const strongestShishen = computed(() => {
  return shishenData.value[0] || { name: '-', value: 0, color: '#999' }
})

// 平衡状态
const balanceStatus = computed(() => {
  const values = wuxingData.value.map(item => item.value)
  if (values.length < 2) return { text: '数据不足', class: '' }
  
  const max = Math.max(...values)
  const min = Math.min(...values)
  const ratio = max / (min || 1)
  
  if (ratio < 2) return { text: '相对平衡', class: 'balanced' }
  if (ratio < 3) return { text: '略有偏颇', class: 'slight' }
  return { text: '严重失衡', class: 'imbalanced' }
})

// 计算百分比
const getPercent = (value, total) => {
  if (!total) return 0
  return ((value / total) * 100).toFixed(1)
}

// 初始化图表
const initCharts = async () => {
  try {
    const echarts = await import('echarts')
    
    // 五行饼图
    if (wuxingChart.value) {
      charts.wuxing = echarts.init(wuxingChart.value)
      updateWuxingChart()
    }
    
    // 十神饼图
    if (shishenChart.value) {
      charts.shishen = echarts.init(shishenChart.value)
      updateShishenChart()
    }
    
    // 大运图表
    if (dayunChart.value && dayunData.value) {
      charts.dayun = echarts.init(dayunChart.value)
      updateDayunChart()
    }
  } catch (error) {
    console.log('ECharts not available, using fallback display')
  }
}

// 更新五行图表
const updateWuxingChart = () => {
  if (!charts.wuxing) return
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: wuxingData.value.map(item => ({
        name: item.name,
        value: item.value,
        itemStyle: { color: item.color }
      }))
    }]
  }
  
  charts.wuxing.setOption(option)
}

// 更新十神图表
const updateShishenChart = () => {
  if (!charts.shishen) return
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: shishenData.value.map(item => ({
        name: item.name,
        value: item.value,
        itemStyle: { color: item.color }
      }))
    }]
  }
  
  charts.shishen.setOption(option)
}

// 更新大运图表
const updateDayunChart = () => {
  if (!charts.dayun || !dayunData.value) return
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    radar: {
      indicator: wuxingData.value.map(item => ({
        name: item.name,
        max: Math.max(...wuxingData.value.map(i => i.value)) * 1.2
      }))
    },
    series: [{
      type: 'radar',
      data: [
        {
          value: wuxingData.value.map(item => item.value),
          name: '原局',
          itemStyle: { color: '#94a3b8' },
          areaStyle: { opacity: 0.2 }
        },
        {
          value: wuxingData.value.map(item => item.value * (1 + (Math.random() * 0.4 - 0.2))),
          name: '大运影响',
          itemStyle: { color: '#667eea' },
          areaStyle: { opacity: 0.3 }
        }
      ]
    }]
  }
  
  charts.dayun.setOption(option)
}

// 监听数据变化
watch(() => props.wuxingEnergy, () => {
  nextTick(() => updateWuxingChart())
}, { deep: true })

watch(() => props.shishenEnergy, () => {
  nextTick(() => updateShishenChart())
}, { deep: true })

watch(() => activeTab.value, (newTab) => {
  nextTick(() => {
    if (newTab === 'wuxing') updateWuxingChart()
    if (newTab === 'shishen') updateShishenChart()
    if (newTab === 'dayun') updateDayunChart()
  })
})

// 窗口大小变化
const handleResize = () => {
  Object.values(charts).forEach(chart => chart?.resize())
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  Object.values(charts).forEach(chart => chart?.dispose())
})
</script>

<style scoped>
.energy-charts-container {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* 标题区 */
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.header-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.header-icon svg {
  width: 22px;
  height: 22px;
}

.header-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.header-subtitle {
  margin: 4px 0 0;
  font-size: 13px;
  color: #64748b;
}

/* 标签切换 */
.chart-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  padding: 4px;
  background: #f1f5f9;
  border-radius: 10px;
}

.tab-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.tab-btn:hover {
  color: #475569;
}

.tab-btn.active {
  background: white;
  color: #667eea;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* 图表卡片 */
.chart-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
}

.chart-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  text-align: center;
  margin-bottom: 16px;
}

.chart-container {
  width: 100%;
  height: 240px;
}

/* 图例 */
.chart-legend {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-name {
  color: #475569;
  font-weight: 500;
}

.legend-value {
  color: #1e293b;
  font-weight: 600;
}

.legend-percent {
  color: #94a3b8;
}

/* 大运信息 */
.dayun-info {
  margin-top: 16px;
  padding: 16px;
  background: white;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: 13px;
  color: #64748b;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.info-value.up {
  color: #22c55e;
}

.info-value.down {
  color: #ef4444;
}

/* 能量总结 */
.energy-summary {
  margin-top: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.summary-title {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 12px;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.summary-label {
  color: #64748b;
}

.summary-value {
  font-weight: 600;
}

.summary-value.balanced {
  color: #22c55e;
}

.summary-value.slight {
  color: #f59e0b;
}

.summary-value.imbalanced {
  color: #ef4444;
}

/* 响应式 */
@media (max-width: 480px) {
  .chart-legend {
    grid-template-columns: 1fr;
  }
}
</style>