<template>
  <div class="debug-container">
    <div class="debug-header">
      <h3>🔧 调试面板 - 原始数据查看</h3>
      <button class="toggle-btn" @click="showDebug = !showDebug">
        {{ showDebug ? '收起' : '展开' }}
      </button>
    </div>
    
    <div v-if="showDebug" class="debug-content">
      <div class="debug-tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>
      
      <div class="debug-panel">
        <pre v-if="activeData && activeTab !== 'ai_prompt'">{{ JSON.stringify(activeData, null, 2) }}</pre>
        <pre v-else-if="activeTab === 'ai_prompt' && activeData" class="ai-prompt">{{ activeData }}</pre>
        <p v-else class="no-data">暂无数据</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  rawData: {
    type: Object,
    default: () => ({})
  },
  aiPrompt: {
    type: String,
    default: ''
  }
})

const showDebug = ref(true)
const activeTab = ref('all')

const tabs = [
  { key: 'all', label: '全部数据' },
  { key: 'basic', label: '基础信息综合分析' },
  { key: 'mingpan', label: '命盘综合信息分析' },
  { key: 'level1', label: '第一论级' },
  { key: 'level2', label: '第二论级' },
  { key: 'level3', label: '第三论级' },
  { key: 'level4', label: '第四论级' },
  { key: 'level5', label: '第五论级' },
  { key: 'level6', label: '第六论级' },
  { key: 'ai_prompt', label: 'AI分析提示词' },
]

const activeData = computed(() => {
  const data = props.rawData || {}
  switch (activeTab.value) {
    case 'all':
      return data
    case 'basic':
      return data['基础信息综合分析']
    case 'mingpan':
      return data['命盘综合信息分析']
    case 'level1':
      return data['第一论级_月令与格局']
    case 'level2':
      return data['第二论级_地支关系']
    case 'level3':
      return data['第三论级_天干关系']
    case 'level4':
      return data['第四论级_天干与地支的关系']
    case 'level5':
      return {
        '定喜忌': data['第五论级_定喜忌'],
        '辅助信息': data['第五论级_辅助信息']
      }
    case 'level6':
      return data['第六论级_大运流年']
    case 'ai_prompt':
      return props.aiPrompt || '暂无AI分析提示词'
    default:
      return data
  }
})
</script>

<style scoped>
.debug-container {
  margin: 20px 0;
  border: 2px dashed #667eea;
  border-radius: 12px;
  background: #f8fafc;
  overflow: hidden;
}

.debug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.debug-header h3 {
  margin: 0;
  font-size: 16px;
}

.toggle-btn {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.toggle-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.debug-content {
  padding: 16px;
}

.debug-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.debug-tabs button {
  padding: 8px 12px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: #475569;
  transition: all 0.2s;
}

.debug-tabs button:hover {
  background: #f1f5f9;
}

.debug-tabs button.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.debug-panel {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  max-height: 600px;
  overflow: auto;
}

.debug-panel pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #334155;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.no-data {
  color: #94a3b8;
  text-align: center;
  padding: 40px;
}

.ai-prompt {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.8;
  color: #334155;
  font-family: 'Monaco', 'Menlo', 'Consolas', 'Microsoft YaHei', sans-serif;
}
</style>
