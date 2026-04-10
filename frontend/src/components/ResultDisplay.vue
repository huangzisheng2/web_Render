<template>
  <div class="result-container">
    <!-- 报告头部 -->
    <div class="report-header">
      <div class="user-info">
        <h2>{{ result.user_info?.name || '匿名' }} 的命理报告</h2>
        <p class="meta">
          {{ result.user_info?.gender }} · 
          {{ result.user_info?.birth_time?.original?.year }}年
          {{ result.user_info?.birth_time?.original?.month }}月
          {{ result.user_info?.birth_time?.original?.day }}日
          {{ result.user_info?.birth_time?.original?.hour !== null 
            ? result.user_info?.birth_time?.original?.hour + '时' 
            : '' }}
        </p>
      </div>
      <Tag type="primary" size="large" class="report-tag">已生成</Tag>
    </div>
    
    <!-- 四柱排盘 -->
    <Card class="section-card">
      <template #title>
        <div class="section-title">
          <Icon name="column" />
          <span>四柱排盘</span>
        </div>
      </template>
      <div class="bazi-pillars">
        <div class="pillar" v-for="(item, index) in pillarItems" :key="index">
          <div class="gan">{{ item.gan }}</div>
          <div class="zhi">{{ item.zhi }}</div>
          <div class="label">{{ item.label }}</div>
        </div>
      </div>
    </Card>
    
    <!-- 基本分析 -->
    <Card class="section-card">
      <template #title>
        <div class="section-title">
          <Icon name="chart-trending-o" />
          <span>基本分析</span>
        </div>
      </template>
      <div class="analysis-grid">
        <div class="analysis-item">
          <span class="label">身强身弱</span>
          <Tag :type="strengthType" size="medium">{{ result.analysis?.strength || '未知' }}</Tag>
        </div>
        <div class="analysis-item">
          <span class="label">主要格局</span>
          <span class="value highlight">{{ result.analysis?.main_pattern || '未知' }}</span>
        </div>
        <div class="analysis-item">
          <span class="label">日主</span>
          <span class="value">{{ result.bazi?.day_master }}</span>
        </div>
        <div class="analysis-item">
          <span class="label">月令</span>
          <span class="value">{{ result.bazi?.month_command }}</span>
        </div>
      </div>
    </Card>
    
    <!-- 五行能量 -->
    <Card class="section-card">
      <template #title>
        <div class="section-title">
          <Icon name="fire-o" />
          <span>五行能量</span>
        </div>
      </template>
      <div class="wuxing-list">
        <div class="wuxing-item" v-for="(value, name) in sortedWuxing" :key="name">
          <span class="name" :style="{ color: wuxingColors[name] }">{{ name }}</span>
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: getWuxingPercent(value) + '%', background: wuxingColors[name] }"
            ></div>
          </div>
          <span class="value">{{ value.toFixed(1) }}</span>
        </div>
      </div>
    </Card>
    
    <!-- AI 分析报告 -->
    <Card class="section-card ai-report-card">
      <template #title>
        <div class="section-title">
          <Icon name="chat-o" />
          <span>AI 分析报告</span>
        </div>
      </template>
      <div class="ai-content" v-html="formattedReport"></div>
    </Card>
    
    <!-- 操作按钮 -->
    <div class="action-buttons">
      <Button 
        round 
        block 
        type="primary" 
        :loading="downloading"
        @click="$emit('download')"
      >
        <Icon name="down" />
        下载 PDF 报告
      </Button>
      <Button 
        round 
        block 
        plain
        style="margin-top: 12px;"
        @click="$emit('reset')"
      >
        重新测试
      </Button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  result: {
    type: Object,
    required: true
  },
  downloading: Boolean
})

defineEmits(['reset', 'download'])

// 五行颜色
const wuxingColors = {
  '木': '#4CAF50',
  '火': '#FF5722',
  '土': '#795548',
  '金': '#FFC107',
  '水': '#2196F3'
}

// 四柱数据
const pillarItems = computed(() => {
  const bazi = props.result?.bazi || {}
  return [
    { 
      gan: bazi.year_pillar?.[0] || '', 
      zhi: bazi.year_pillar?.[1] || '', 
      label: '年柱' 
    },
    { 
      gan: bazi.month_pillar?.[0] || '', 
      zhi: bazi.month_pillar?.[1] || '', 
      label: '月柱' 
    },
    { 
      gan: bazi.day_pillar?.[0] || '', 
      zhi: bazi.day_pillar?.[1] || '', 
      label: '日柱' 
    },
    { 
      gan: bazi.time_pillar?.[0] || '', 
      zhi: bazi.time_pillar?.[1] || '', 
      label: '时柱' 
    },
  ]
})

// 身强身弱标签类型
const strengthType = computed(() => {
  const strength = props.result?.analysis?.strength
  if (strength?.includes('强')) return 'success'
  if (strength?.includes('弱')) return 'warning'
  return 'default'
})

// 排序后的五行
const sortedWuxing = computed(() => {
  const wuxing = props.result?.analysis?.wuxing_energy || {}
  return Object.fromEntries(
    Object.entries(wuxing).sort((a, b) => b[1] - a[1])
  )
})

// 五行百分比
const maxWuxing = computed(() => {
  const values = Object.values(props.result?.analysis?.wuxing_energy || {})
  return Math.max(...values, 1)
})

const getWuxingPercent = (value) => {
  return (value / maxWuxing.value) * 100
}

// 格式化的报告
const formattedReport = computed(() => {
  const report = props.result?.ai_report || ''
  // 将 markdown 风格的标题转换为 HTML
  return report
    .replace(/### (.*)/g, '<h4>$1</h4>')
    .replace(/## (.*)/g, '<h3>$1</h3>')
    .replace(/# (.*)/g, '<h2>$1</h2>')
    .replace(/\n/g, '<br>')
})
</script>

<style scoped>
.result-container {
  padding: 16px;
  background: #f5f5f5;
  min-height: 100vh;
}

.report-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 24px;
  color: white;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.user-info h2 {
  margin: 0 0 8px;
  font-size: 20px;
}

.user-info .meta {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}

.report-tag {
  background: rgba(255,255,255,0.2) !important;
  color: white !important;
}

.section-card {
  margin-bottom: 12px;
  border-radius: 8px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #333;
}

.bazi-pillars {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  text-align: center;
}

.pillar {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px 8px;
}

.gan {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.zhi {
  font-size: 20px;
  color: #666;
  margin: 4px 0;
}

.label {
  font-size: 12px;
  color: #999;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.analysis-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.analysis-item .label {
  font-size: 12px;
  color: #999;
}

.analysis-item .value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.analysis-item .value.highlight {
  color: #667eea;
  font-weight: 600;
}

.wuxing-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.wuxing-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.wuxing-item .name {
  width: 40px;
  font-weight: 600;
  font-size: 16px;
}

.progress-bar {
  flex: 1;
  height: 12px;
  background: #eee;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.5s ease;
}

.wuxing-item .value {
  width: 50px;
  text-align: right;
  font-size: 14px;
  color: #666;
}

.ai-report-card {
  background: linear-gradient(to bottom, #fff, #f8f9ff);
}

.ai-content {
  line-height: 1.8;
  color: #444;
  font-size: 14px;
}

.ai-content :deep(h2) {
  color: #667eea;
  font-size: 18px;
  margin: 20px 0 12px;
  border-bottom: 2px solid #e0e6ff;
  padding-bottom: 8px;
}

.ai-content :deep(h3) {
  color: #764ba2;
  font-size: 16px;
  margin: 16px 0 10px;
}

.ai-content :deep(h4) {
  color: #555;
  font-size: 15px;
  margin: 12px 0 8px;
  font-weight: 600;
}

.action-buttons {
  margin-top: 24px;
  padding: 0 8px;
}
</style>
