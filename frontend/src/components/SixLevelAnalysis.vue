<template>
  <div class="six-level-container">
    <!-- 标题区 -->
    <div class="section-header">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z"/>
          <path d="M2 17l10 5 10-5"/>
          <path d="M2 12l10 5 10-5"/>
        </svg>
      </div>
      <div class="header-content">
        <h3 class="header-title">六级论级分析</h3>
        <p class="header-subtitle">基于《渊海子平》《三命通会》经典命理体系</p>
      </div>
    </div>

    <!-- 六级折叠面板 -->
    <div class="level-panels">
      <div 
        v-for="(level, index) in levelData" 
        :key="index"
        class="level-panel"
        :class="{ 'expanded': expandedLevels[index] }"
      >
        <!-- 面板头部 -->
        <div 
          class="panel-header"
          @click="toggleLevel(index)"
        >
          <div class="level-badge" :style="{ background: level.color }">
            {{ level.number }}
          </div>
          <div class="level-info">
            <div class="level-title">{{ level.title }}</div>
            <div class="level-desc">{{ level.subtitle }}</div>
          </div>
          <div class="expand-icon" :class="{ 'rotated': expandedLevels[index] }">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </div>
        </div>

        <!-- 面板内容 -->
        <div v-show="expandedLevels[index]" class="panel-content">
          <!-- 第一论级：月令与格局 -->
          <template v-if="index === 0">
            <div class="content-grid">
              <div class="info-card">
                <div class="info-label">月令</div>
                <div class="info-value highlight">{{ levelData[0].data.yueling || '未知' }}</div>
              </div>
              <div class="info-card">
                <div class="info-label">主要格局</div>
                <div class="info-value highlight">{{ levelData[0].data.mainPattern || '未知' }}</div>
              </div>
              <div class="info-card">
                <div class="info-label">身强身弱</div>
                <div class="info-value" :class="strengthClass">
                  {{ levelData[0].data.strength || '未知' }}
                </div>
              </div>
              <div class="info-card">
                <div class="info-label">日主</div>
                <div class="info-value">{{ levelData[0].data.dayMaster || '未知' }}</div>
              </div>
            </div>
            <!-- 五行旺相 -->
            <div class="wuxing-wangxiang-section" v-if="levelData[0].data.wuxingWangxiang">
              <div class="subsection-title">五行旺相</div>
              <div class="wangxiang-text">{{ levelData[0].data.wuxingWangxiang }}</div>
              <div class="wangxiang-tags">
                <span 
                  v-for="(status, wx) in levelData[0].data.wuxingWangxiangObj" 
                  :key="wx"
                  class="wangxiang-tag"
                  :style="{ background: getWuxingColor(wx).gradient, color: 'white' }"
                >
                  {{ wx }}: {{ status }}
                </span>
              </div>
            </div>
            <!-- 格局详情 -->
            <div v-if="levelData[0].data.gejuDefinition" class="geju-detail">
              <div class="subsection-title">格局定义</div>
              <div class="detail-text">{{ levelData[0].data.gejuDefinition }}</div>
            </div>
            <div v-if="levelData[0].data.gejuCondition" class="geju-detail">
              <div class="subsection-title">格局条件</div>
              <div class="detail-text">{{ levelData[0].data.gejuCondition }}</div>
            </div>
            <div v-if="levelData[0].data.gejuLikeDislike" class="geju-detail">
              <div class="subsection-title">格局喜忌</div>
              <div class="detail-text">{{ levelData[0].data.gejuLikeDislike }}</div>
            </div>
          </template>

          <!-- 第二论级：地支关系 -->
          <template v-if="index === 1">
            <div class="relations-grid">
              <div
                v-for="(items, type) in levelData[1].data"
                :key="type"
                class="relation-card"
                v-show="items && items.length > 0"
              >
                <div class="relation-type">{{ type }}</div>
                <div class="relation-items">
                  <span
                    v-for="(item, idx) in items"
                    :key="idx"
                    class="relation-tag"
                  >
                    {{ item }}
                  </span>
                </div>
              </div>
            </div>
            <div v-if="!hasAnyRelation(levelData[1].data)" class="no-data">
              无特殊地支关系
            </div>
          </template>

          <!-- 第三论级：天干关系 -->
          <template v-if="index === 2">
            <div class="gan-relations">
              <div class="relation-section" v-if="levelData[2].data.wuhe && levelData[2].data.wuhe.length > 0">
                <div class="subsection-title">天干五合</div>
                <div class="relation-list">
                  <div 
                    v-for="(item, idx) in levelData[2].data.wuhe" 
                    :key="idx"
                    class="relation-item"
                  >
                    <span class="gan-pair">{{ item }}</span>
                  </div>
                </div>
              </div>
              <div class="relation-section" v-if="levelData[2].data.xiangke && levelData[2].data.xiangke.length > 0">
                <div class="subsection-title">天干相克</div>
                <div class="relation-list">
                  <div 
                    v-for="(item, idx) in levelData[2].data.xiangke" 
                    :key="idx"
                    class="relation-item"
                  >
                    <span class="gan-pair">{{ item }}</span>
                  </div>
                </div>
              </div>
              <div class="relation-section" v-if="levelData[2].data.xiangchong && levelData[2].data.xiangchong.length > 0">
                <div class="subsection-title">天干相冲</div>
                <div class="relation-list">
                  <div 
                    v-for="(item, idx) in levelData[2].data.xiangchong" 
                    :key="idx"
                    class="relation-item"
                  >
                    <span class="gan-pair">{{ item }}</span>
                  </div>
                </div>
              </div>
              <div class="relation-section" v-if="levelData[2].data.huaqi">
                <div class="subsection-title">化气判定</div>
                <div class="relation-list">
                  <div class="relation-item">
                    <span class="gan-pair">{{ levelData[2].data.huaqi }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="!hasGanRelation(levelData[2].data)" class="no-data">
              无特殊天干关系
            </div>
          </template>

          <!-- 第四论级：干支关系 -->
          <template v-if="index === 3">
            <div class="ganzhi-relations">
              <div class="relation-section" v-if="levelData[3].data.gaitou && levelData[3].data.gaitou.length > 0">
                <div class="subsection-title">盖头</div>
                <div class="relation-list">
                  <div 
                    v-for="(item, idx) in levelData[3].data.gaitou" 
                    :key="idx"
                    class="relation-item"
                  >
                    <span class="gan-pair">{{ item }}</span>
                  </div>
                </div>
              </div>
              <div class="relation-section" v-if="levelData[3].data.jiejiao && levelData[3].data.jiejiao.length > 0">
                <div class="subsection-title">截脚</div>
                <div class="relation-list">
                  <div 
                    v-for="(item, idx) in levelData[3].data.jiejiao" 
                    :key="idx"
                    class="relation-item"
                  >
                    <span class="gan-pair">{{ item }}</span>
                  </div>
                </div>
              </div>
              <div class="relation-section" v-if="levelData[3].data.fuyin && levelData[3].data.fuyin.length > 0">
                <div class="subsection-title">伏吟</div>
                <div class="relation-list">
                  <div 
                    v-for="(item, idx) in levelData[3].data.fuyin" 
                    :key="idx"
                    class="relation-item"
                  >
                    <span class="gan-pair">{{ item }}</span>
                  </div>
                </div>
              </div>
              <div class="relation-section" v-if="levelData[3].data.fanyin && levelData[3].data.fanyin.length > 0">
                <div class="subsection-title">反吟</div>
                <div class="relation-list">
                  <div 
                    v-for="(item, idx) in levelData[3].data.fanyin" 
                    :key="idx"
                    class="relation-item"
                  >
                    <span class="gan-pair">{{ item }}</span>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <!-- 第五论级：定喜忌 -->
          <template v-if="index === 4">
            <div class="yonggod-grid">
              <div class="yonggod-card yong">
                <div class="yonggod-label">用神</div>
                <div class="yonggod-value">{{ formatYongShen(levelData[4].data.yongshen) }}</div>
                <div class="yonggod-desc">最需要补足的五行</div>
              </div>
              <div class="yonggod-card xi">
                <div class="yonggod-label">喜神</div>
                <div class="yonggod-value">{{ formatYongShen(levelData[4].data.xishen) }}</div>
                <div class="yonggod-desc">对命局有帮助的五行</div>
              </div>
              <div class="yonggod-card ji">
                <div class="yonggod-label">忌神</div>
                <div class="yonggod-value">{{ formatYongShen(levelData[4].data.jishen) }}</div>
                <div class="yonggod-desc">需要避免的五行</div>
              </div>
              <div class="yonggod-card tiaohou" v-if="levelData[4].data.tiaohou">
                <div class="yonggod-label">调候用神</div>
                <div class="yonggod-value">{{ levelData[4].data.tiaohou }}</div>
                <div class="yonggod-desc">调节气候所需</div>
              </div>
            </div>
            <!-- 成长建议 -->
            <div v-if="levelData[4].data.growthAdvice" class="growth-advice">
              <div class="subsection-title">成长建议</div>
              <div class="advice-content" v-html="formatAdvice(levelData[4].data.growthAdvice)"></div>
            </div>
            <!-- 十二长生 -->
            <div v-if="levelData[4].data.shierChangsheng && Object.keys(levelData[4].data.shierChangsheng).length > 0" class="shier-changsheng">
              <div class="subsection-title">十二长生</div>
              <div class="pillars-status">
                <div v-for="(status, pillar) in levelData[4].data.shierChangsheng" :key="pillar" class="pillar-status">
                  <span class="pillar-name">{{ pillar }}</span>
                  <span class="status-value">{{ formatChangSheng(status) }}</span>
                </div>
              </div>
            </div>
            <!-- 纳音 -->
            <div v-if="levelData[4].data.nayin && Object.keys(levelData[4].data.nayin).length > 0" class="nayin-section">
              <div class="subsection-title">纳音五行</div>
              <div class="pillars-nayin">
                <div v-for="(nayin, pillar) in levelData[4].data.nayin" :key="pillar" class="pillar-nayin">
                  <span class="pillar-name">{{ pillar }}</span>
                  <span class="nayin-value">{{ nayin }}</span>
                </div>
              </div>
            </div>
            <!-- 神煞信息 -->
            <div v-if="levelData[4].data.shensha && Object.keys(levelData[4].data.shensha).length > 0" class="shensha-section">
              <div class="subsection-title">神煞信息</div>
              <div class="shensha-by-pillar">
                <div v-for="(shenshaList, pillar) in levelData[4].data.shensha" :key="pillar" class="shensha-pillar">
                  <div class="shensha-pillar-name">{{ pillar }}</div>
                  <div class="shensha-pillar-tags">
                    <span v-for="(shensha, idx) in (Array.isArray(shenshaList) ? shenshaList : [])" :key="idx" class="shensha-tag">
                      {{ shensha }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <!-- 第六论级：大运流年 -->
          <template v-if="index === 5">
            <!-- 起运信息 -->
            <div v-if="levelData[5].data.qiyunInfo" class="qiyun-info">
              <div class="subsection-title">起运计算</div>
              <div class="qiyun-detail">
                <div v-if="levelData[5].data.qiyunInfo.起运岁数" class="qiyun-item">
                  <span class="qiyun-label">起运岁数:</span>
                  <span class="qiyun-value">{{ levelData[5].data.qiyunInfo.起运岁数 }}</span>
                </div>
                <div v-if="levelData[5].data.qiyunInfo.起运年份" class="qiyun-item">
                  <span class="qiyun-label">起运年份:</span>
                  <span class="qiyun-value">{{ levelData[5].data.qiyunInfo.起运年份 }}</span>
                </div>
              </div>
            </div>
            <!-- 大运列表 -->
            <div v-if="levelData[5].data.dayunList && levelData[5].data.dayunList.length > 0" class="dayun-list-section">
              <div class="subsection-title">大运列表</div>
              <div class="dayun-list">
                <div v-for="(dayun, idx) in levelData[5].data.dayunList.slice(0, 8)" :key="idx" class="dayun-item">
                  <span class="dayun-ganzhi">{{ dayun.干支 || dayun }}</span>
                  <span class="dayun-years">{{ dayun.年份范围 || dayun }}</span>
                </div>
              </div>
            </div>
            <div class="dayun-liunian">
              <div class="current-dayun" v-if="levelData[5].data.currentDayun">
                <div class="subsection-title">当前大运</div>
                <div class="dayun-card">
                  <div class="dayun-ganzhi">{{ levelData[5].data.currentDayun.干支 }}</div>
                  <div class="dayun-range" v-if="levelData[5].data.currentDayun.年份范围">{{ levelData[5].data.currentDayun.年份范围 }}</div>
                  <div class="dayun-effect" v-if="levelData[5].data.currentDayun.effect">{{ levelData[5].data.currentDayun.effect }}</div>
                </div>
              </div>
              <div class="liunian-section" v-if="levelData[5].data.liunian">
                <div class="subsection-title">流年影响</div>
                <div class="liunian-card">
                  <div class="liunian-year">{{ new Date().getFullYear() }}年</div>
                  <div class="liunian-ganzhi">{{ levelData[5].data.liunian.干支 }}</div>
                  <div class="liunian-effect" v-if="levelData[5].data.liunian.effect">{{ levelData[5].data.liunian.effect }}</div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getWuxingColor } from '../utils/wuxing'

const props = defineProps({
  analysisData: {
    type: Object,
    default: () => ({})
  }
})

// 展开状态
const expandedLevels = ref([true, false, false, false, false, false])

const toggleLevel = (index) => {
  expandedLevels.value[index] = !expandedLevels.value[index]
}

// 身强身弱样式
const strengthClass = computed(() => {
  const strength = props.analysisData?.第一论级_月令与格局?.身强身弱
  if (strength?.includes('强')) return 'strong'
  if (strength?.includes('弱')) return 'weak'
  return ''
})

// 格式化用神显示
const formatYongShen = (val) => {
  if (!val) return '无'
  if (Array.isArray(val)) {
    return val.join('、') || '无'
  }
  return val
}

// 格式化十二长生显示
const formatChangSheng = (status) => {
  if (!status) return ''
  if (typeof status === 'object') {
    const parts = []
    if (status.星运) parts.push(`星运:${status.星运}`)
    if (status.自坐) parts.push(`自坐:${status.自坐}`)
    return parts.join(' ')
  }
  return status
}

// 解析五行旺相字符串为对象
const parseWuxingWangxiang = (str) => {
  if (!str || typeof str !== 'string') return {}
  const result = {}
  const parts = str.split(',')
  parts.forEach(part => {
    const match = part.trim().match(/(\S+)(\S+)/)
    if (match) {
      result[match[1]] = match[2]
    }
  })
  return result
}

// 六级数据
const levelData = computed(() => {
  const raw = props.analysisData || {}

  // 调试：打印原始数据结构
  console.log('Raw analysisData:', raw)

  // 第一论级数据
  const firstLevel = raw.第一论级_月令与格局 || {}
  
  return [
    {
      number: '一',
      title: '月令与格局',
      subtitle: '判断五行强弱、确定主格局',
      color: '#22c55e',
      data: {
        yueling: raw.第一论级_月令与格局?.月令,
        mainPattern: raw.第一论级_月令与格局?.主要格局 || raw.格局综合判定?.主格局,
        strength: raw.第一论级_月令与格局?.身强身弱,
        dayMaster: raw.第一论级_月令与格局?.日主,
        wuxingStrength: raw.第一论级_月令与格局?.五行旺相,
        gejuDefinition: raw.第一论级_月令与格局?.格局定义,
        gejuCondition: raw.第一论级_月令与格局?.格局条件,
        gejuLikeDislike: raw.第一论级_月令与格局?.格局喜忌
      }
    },
    {
      number: '二',
      title: '地支关系',
      subtitle: '三会、三合、六合、刑冲破害',
      color: '#3b82f6',
      data: {
        '三会': raw.第二论级_地支关系?.三会 || [],
        '拱会': raw.第二论级_地支关系?.拱会 || [],
        '三合': raw.第二论级_地支关系?.三合 || [],
        '半合': raw.第二论级_地支关系?.半合 || [],
        '拱合': raw.第二论级_地支关系?.拱合 || [],
        '六合': raw.第二论级_地支关系?.六合 || [],
        '六破': raw.第二论级_地支关系?.六破 || [],
        '六害': raw.第二论级_地支关系?.六害 || [],
        '三刑': raw.第二论级_地支关系?.三刑 || [],
        '六冲': raw.第二论级_地支关系?.六冲 || [],
        '自刑': raw.第二论级_地支关系?.自刑 || [],
        '地支暗合': raw.第二论级_地支关系?.地支暗合 || []
      }
    },
    {
      number: '三',
      title: '天干关系',
      subtitle: '天干五合、生克制化',
      color: '#f59e0b',
      data: {
        wuhe: raw.第三论级_天干关系?.天干五合 || raw.第三论级_天干关系?.五合 || [],
        xiangke: raw.第三论级_天干关系?.天干相克 || raw.第三论级_天干关系?.相克 || [],
        xiangchong: raw.第三论级_天干关系?.天干相冲 || [],
        huaqi: raw.第三论级_天干关系?.化气判定 || raw.第三论级_天干关系?.化气
      }
    },
    {
      number: '四',
      title: '干支关系',
      subtitle: '盖头、截脚、伏吟、反吟',
      color: '#8b5cf6',
      data: {
        gaitou: raw.第四论级_天干与地支的关系?.盖头 || [],
        jiejiao: raw.第四论级_天干与地支的关系?.截脚 || [],
        fuyin: raw.第四论级_天干与地支的关系?.伏吟 || [],
        fanyin: raw.第四论级_天干与地支的关系?.反吟 || []
      }
    },
    {
      number: '五',
      title: '定喜忌',
      subtitle: '用神、喜神、忌神、神煞',
      color: '#ef4444',
      data: {
        yongshen: raw.第五论级_定喜忌?.用神,
        xishen: raw.第五论级_定喜忌?.喜神,
        jishen: raw.第五论级_定喜忌?.忌神,
        tiaohou: raw.第五论级_定喜忌?.调候用神,
        growthAdvice: raw.第五论级_定喜忌?.成长建议 || raw.第五论级_定喜忌?.建议,
        shensha: raw.第五论级_辅助信息?.神煞 || {},
        shierChangsheng: raw.第五论级_辅助信息?.十二长生,
        nayin: raw.第五论级_辅助信息?.纳音
      }
    },
    {
      number: '六',
      title: '大运流年',
      subtitle: '岁运影响分析',
      color: '#06b6d4',
      data: {
        qiyunInfo: raw.起运计算过程,
        currentDayun: raw.第六论级_大运流年?.当前大运,
        liunian: raw.第六论级_大运流年?.流年,
        dayunList: raw.大运表 || []
      }
    }
  ]
})

// 五行百分比计算
const maxWuxing = computed(() => {
  const values = Object.values(levelData.value[0].data.wuxingStrength || {})
  return Math.max(...values, 1)
})

const getWuxingPercent = (value) => {
  return (value / maxWuxing.value) * 100
}

// 格式化成长建议
const formatAdvice = (advice) => {
  if (!advice) return ''
  // 将换行符转换为HTML换行
  return advice.replace(/\n/g, '<br>')
}

// 检查是否有地支关系
const hasAnyRelation = (data) => {
  return Object.values(data).some(items => items && items.length > 0)
}

// 检查是否有天干关系
const hasGanRelation = (data) => {
  return (data.wuhe && data.wuhe.length > 0) ||
         (data.xiangke && data.xiangke.length > 0) ||
         (data.xiangchong && data.xiangchong.length > 0) ||
         data.huaqi
}
</script>

<style scoped>
.six-level-container {
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

/* 面板 */
.level-panels {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.level-panel {
  border-radius: 12px;
  background: #f8fafc;
  overflow: hidden;
  transition: all 0.3s ease;
}

.level-panel.expanded {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.panel-header:hover {
  background: rgba(0, 0, 0, 0.02);
}

.level-badge {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.level-info {
  flex: 1;
}

.level-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.level-desc {
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

.expand-icon {
  width: 24px;
  height: 24px;
  color: #94a3b8;
  transition: transform 0.3s;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

.expand-icon svg {
  width: 100%;
  height: 100%;
}

/* 面板内容 */
.panel-content {
  padding: 0 16px 16px;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 内容网格 */
.content-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-card {
  background: #f8fafc;
  padding: 12px;
  border-radius: 10px;
  text-align: center;
}

.info-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.info-value {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.info-value.highlight {
  color: #667eea;
}

.info-value.strong {
  color: #22c55e;
}

.info-value.weak {
  color: #ef4444;
}

/* 五行旺相 */
.wuxing-wangxiang-section {
  margin-top: 16px;
}

.wangxiang-text {
  font-size: 14px;
  color: #475569;
  margin-bottom: 10px;
  padding: 10px;
  background: #f8fafc;
  border-radius: 8px;
}

.wangxiang-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.wangxiang-tag {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

/* 五行进度条 */
.subsection-title {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin: 16px 0 12px;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.wuxing-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.wuxing-bar-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bar-name {
  width: 40px;
  font-size: 14px;
  font-weight: 600;
}

.bar-track {
  flex: 1;
  height: 10px;
  background: #e2e8f0;
  border-radius: 5px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.5s ease;
}

.bar-value {
  width: 50px;
  text-align: right;
  font-size: 13px;
  color: #64748b;
}

/* 格局详情 */
.geju-detail {
  margin-top: 12px;
}

.detail-text {
  font-size: 13px;
  line-height: 1.6;
  color: #475569;
  background: #f8fafc;
  padding: 12px;
  border-radius: 8px;
}

/* 关系网格 */
.relations-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.relation-card {
  background: #f8fafc;
  padding: 12px;
  border-radius: 10px;
}

.relation-type {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
  font-weight: 500;
}

.relation-items {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.relation-tag {
  font-size: 12px;
  padding: 4px 8px;
  background: white;
  border-radius: 6px;
  color: #475569;
  border: 1px solid #e2e8f0;
}

/* 天干关系 */
.gan-relations,
.ganzhi-relations {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.relation-section {
  background: #f8fafc;
  padding: 12px;
  border-radius: 10px;
}

.relation-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.relation-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: white;
  border-radius: 8px;
  font-size: 13px;
}

.gan-pair {
  font-weight: 600;
  color: #1e293b;
}

.he-result {
  color: #22c55e;
  font-weight: 500;
}

/* 喜忌 */
.yonggod-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.yonggod-card {
  padding: 12px;
  border-radius: 10px;
  text-align: center;
}

.yonggod-card.yong {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
}

.yonggod-card.xi {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
}

.yonggod-card.ji {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
}

.yonggod-card.tiaohou {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
}

.yonggod-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.yonggod-value {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.yonggod-desc {
  font-size: 11px;
  color: #64748b;
}

/* 成长建议 */
.growth-advice {
  margin-top: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 10px;
}

.advice-content {
  font-size: 13px;
  line-height: 1.8;
  color: #374151;
}

/* 十二长生 */
.shier-changsheng {
  margin-top: 16px;
}

.pillars-status {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.pillar-status {
  display: flex;
  justify-content: space-between;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.pillar-name {
  font-size: 13px;
  color: #64748b;
}

.status-value {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

/* 纳音 */
.nayin-section {
  margin-top: 16px;
}

.pillars-nayin {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.pillar-nayin {
  display: flex;
  justify-content: space-between;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.nayin-value {
  font-size: 13px;
  font-weight: 600;
  color: #667eea;
}

/* 神煞 */
.shensha-section {
  margin-top: 16px;
}

.shensha-by-pillar {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.shensha-pillar {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px;
  background: #f8fafc;
  border-radius: 10px;
}

.shensha-pillar-name {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  min-width: 50px;
}

.shensha-pillar-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.shensha-tag {
  font-size: 12px;
  padding: 4px 10px;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #4338ca;
  border-radius: 20px;
  font-weight: 500;
}

/* 起运信息 */
.qiyun-info {
  margin-bottom: 16px;
}

.qiyun-detail {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.qiyun-item {
  display: flex;
  gap: 12px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.qiyun-label {
  font-size: 13px;
  color: #64748b;
  min-width: 70px;
}

.qiyun-value {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

/* 大运列表 */
.dayun-list-section {
  margin-bottom: 16px;
}

.dayun-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.dayun-item {
  display: flex;
  flex-direction: column;
  padding: 10px;
  background: #f8fafc;
  border-radius: 8px;
  text-align: center;
}

.dayun-ganzhi {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.dayun-years {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

/* 无数据提示 */
.no-data {
  text-align: center;
  padding: 20px;
  color: #94a3b8;
  font-size: 14px;
  background: #f8fafc;
  border-radius: 10px;
  margin-top: 10px;
}

/* 大运流年 */
.dayun-liunian {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dayun-card,
.liunian-card {
  background: #f8fafc;
  padding: 16px;
  border-radius: 10px;
  text-align: center;
}

.dayun-ganzhi,
.liunian-ganzhi {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.dayun-range,
.liunian-year {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.dayun-effect,
.liunian-effect {
  font-size: 13px;
  color: #475569;
  line-height: 1.6;
}

/* 响应式 */
@media (max-width: 480px) {
  .content-grid,
  .relations-grid,
  .yonggod-grid,
  .pillars-status,
  .pillars-nayin,
  .dayun-list {
    grid-template-columns: 1fr;
  }

  .shensha-pillar {
    flex-direction: column;
    gap: 8px;
  }
}
</style>