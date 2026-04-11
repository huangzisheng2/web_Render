<template>
  <div class="bazi-pillars-container">
    <!-- 标题区 -->
    <div class="pillars-header">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7" rx="1"/>
          <rect x="14" y="3" width="7" height="7" rx="1"/>
          <rect x="14" y="14" width="7" height="7" rx="1"/>
          <rect x="3" y="14" width="7" height="7" rx="1"/>
        </svg>
      </div>
      <div class="header-content">
        <h3 class="header-title">四柱排盘</h3>
        <p class="header-subtitle">年柱 · 月柱 · 日柱 · 时柱</p>
      </div>
    </div>
    
    <!-- 四柱卡片 -->
    <div class="pillars-grid">
      <div 
        v-for="(pillar, index) in pillarData" 
        :key="index"
        class="pillar-card"
        :class="{ 'center-pillar': pillar.position === 'center' }"
      >
        <!-- 柱位标签 -->
        <div class="pillar-position">{{ pillar.label }}</div>
        
        <!-- 天干 -->
        <div 
          class="pillar-gan"
          :style="{ 
            background: getGanColor(pillar.gan).gradient,
            color: getGanColor(pillar.gan).text
          }"
        >
          <span class="character">{{ pillar.gan }}</span>
          <span class="wuxing-badge">{{ getGanWuxing(pillar.gan) }}</span>
        </div>
        
        <!-- 地支 -->
        <div 
          class="pillar-zhi"
          :style="{ 
            background: getZhiColor(pillar.zhi).light,
            borderColor: getZhiColor(pillar.zhi).primary
          }"
        >
          <span class="character" :style="{ color: getZhiColor(pillar.zhi).dark }">
            {{ pillar.zhi }}
          </span>
          <span class="wuxing-badge" :style="{ 
            background: getZhiColor(pillar.zhi).primary,
            color: getZhiColor(pillar.zhi).text
          }">
            {{ getZhiWuxing(pillar.zhi) }}
          </span>
        </div>
        
        <!-- 藏干信息 -->
        <div class="canggan-info" v-if="pillar.canggan && pillar.canggan.length > 0">
          <div class="canggan-label">藏干</div>
          <div class="canggan-list">
            <span 
              v-for="(cg, cgIndex) in pillar.canggan" 
              :key="cgIndex"
              class="canggan-item"
              :style="{ 
                background: getGanColor(cg).light,
                color: getGanColor(cg).dark
              }"
            >
              {{ cg }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 十神信息 -->
    <div class="shishen-section" v-if="shishenData">
      <div class="shishen-title">十神配置</div>
      <div class="shishen-grid">
        <div 
          v-for="(item, index) in shishenList" 
          :key="index"
          class="shishen-item"
        >
          <span class="shishen-position">{{ item.position }}</span>
          <span 
            class="shishen-name"
            :style="{ color: getShishenColor(item.name) }"
          >
            {{ item.name }}
          </span>
        </div>
      </div>
    </div>
    
    <!-- 日主信息 -->
    <div class="day-master-section" v-if="dayMaster">
      <div class="day-master-card">
        <div class="day-master-label">日主</div>
        <div 
          class="day-master-value"
          :style="{ 
            background: getGanColor(dayMaster).gradient,
            color: getGanColor(dayMaster).text
          }"
        >
          {{ dayMaster }}
        </div>
        <div class="day-master-wuxing" :style="{ color: getGanColor(dayMaster).primary }">
          {{ getGanWuxing(dayMaster) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  getGanWuxing, 
  getZhiWuxing, 
  getGanColor, 
  getZhiColor,
  getShishenColor 
} from '../utils/wuxing'

const props = defineProps({
  bazi: {
    type: Object,
    required: true
  },
  shishen: {
    type: Object,
    default: () => ({})
  },
  dayMaster: {
    type: String,
    default: ''
  }
})

// 四柱数据
const pillarData = computed(() => {
  const bazi = props.bazi || {}
  return [
    { 
      label: '年柱', 
      position: 'top',
      gan: bazi.year_gan || '', 
      zhi: bazi.year_zhi || '',
      canggan: bazi.year_canggan || []
    },
    { 
      label: '月柱', 
      position: 'left',
      gan: bazi.month_gan || '', 
      zhi: bazi.month_zhi || '',
      canggan: bazi.month_canggan || []
    },
    { 
      label: '日柱', 
      position: 'center',
      gan: bazi.day_gan || '', 
      zhi: bazi.day_zhi || '',
      canggan: bazi.day_canggan || []
    },
    { 
      label: '时柱', 
      position: 'right',
      gan: bazi.time_gan || '', 
      zhi: bazi.time_zhi || '',
      canggan: bazi.time_canggan || []
    }
  ]
})

// 十神列表
const shishenList = computed(() => {
  const shishen = props.shishen || {}
  return [
    { position: '年干', name: shishen.year_gan || '-' },
    { position: '月干', name: shishen.month_gan || '-' },
    { position: '时干', name: shishen.time_gan || '-' },
    { position: '年支', name: shishen.year_zhi || '-' },
    { position: '月支', name: shishen.month_zhi || '-' },
    { position: '日支', name: shishen.day_zhi || '-' },
    { position: '时支', name: shishen.time_zhi || '-' }
  ]
})
</script>

<style scoped>
.bazi-pillars-container {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* 标题区 */
.pillars-header {
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
  width: 24px;
  height: 24px;
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

/* 四柱网格 */
.pillars-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.pillar-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px 8px;
  background: white;
  border-radius: 12px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.pillar-card.center-pillar {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #fffbeb 0%, #ffffff 100%);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.15);
}

.pillar-position {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 天干 */
.pillar-gan {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative;
}

.pillar-gan .character {
  font-size: 24px;
  font-weight: 700;
  line-height: 1;
}

/* 地支 */
.pillar-zhi {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px solid;
  position: relative;
}

.pillar-zhi .character {
  font-size: 22px;
  font-weight: 600;
  line-height: 1;
}

.wuxing-badge {
  position: absolute;
  bottom: -6px;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 600;
  white-space: nowrap;
}

.pillar-gan .wuxing-badge {
  background: rgba(255, 255, 255, 0.25);
  color: inherit;
}

/* 藏干信息 */
.canggan-info {
  margin-top: 8px;
  text-align: center;
}

.canggan-label {
  font-size: 10px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.canggan-list {
  display: flex;
  gap: 4px;
  justify-content: center;
}

.canggan-item {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

/* 十神区 */
.shishen-section {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  margin-top: 16px;
}

.shishen-title {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 12px;
  text-align: center;
}

.shishen-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.shishen-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px;
  background: white;
  border-radius: 8px;
}

.shishen-position {
  font-size: 11px;
  color: #94a3b8;
}

.shishen-name {
  font-size: 13px;
  font-weight: 600;
}

/* 日主区 */
.day-master-section {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.day-master-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  padding: 12px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.day-master-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.day-master-value {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.day-master-wuxing {
  font-size: 14px;
  font-weight: 600;
}

/* 响应式 */
@media (max-width: 480px) {
  .pillars-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  
  .shishen-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .pillar-gan,
  .pillar-zhi {
    width: 48px;
    height: 48px;
  }
  
  .pillar-gan .character {
    font-size: 20px;
  }
  
  .pillar-zhi .character {
    font-size: 18px;
  }
}
</style>