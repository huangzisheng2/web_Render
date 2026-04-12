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
            <!-- 五行强弱 -->
            <div class="wuxing-section" v-if="levelData[0].data.wuxingStrength">
              <div class="subsection-title">五行强弱分析</div>
              <div class="wuxing-bars">
                <div 
                  v-for="(value, name) in levelData[0].data.wuxingStrength" 
                  :key="name"
                  class="wuxing-bar-item"
                >
                  <span class="bar-name" :style="{ color: getWuxingColor(name).primary }">{{ name }}</span>
                  <div class="bar-track">
                    <div 
                      class="bar-fill"
                      :style="{ 
                        width: getWuxingPercent(value) + '%',
                        background: getWuxingColor(name).gradient
                      }"
                    ></div>
                  </div>
                  <span class="bar-value">{{ value }}</span>
                </div>
              </div>
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
            <!-- 地支关系详细描述 -->
            <div v-if="levelData[1].relationsDetail && levelData[1].relationsDetail.length > 0" class="relations-detail">
              <div class="subsection-title">关系详解</div>
              <div class="relation-detail-list">
                <div v-for="(detail, idx) in levelData[1].relationsDetail" :key="idx" class="relation-detail-item">
                  <div class="detail-title">{{ detail.name }}</div>
                  <div class="detail-concept" v-if="detail.核心概念">{{ detail.核心概念 }}</div>
                  <div class="detail-content" v-if="detail.命理组合">{{ detail.命理组合 }}</div>
                  <div class="detail-psychology" v-if="detail.心理特质">
                    <span class="detail-label">心理:</span> {{ detail.心理特质 }}
                  </div>
                  <div class="detail-advice" v-if="detail.成长建议">
                    <span class="detail-label">建议:</span> {{ detail.成长建议 }}
                  </div>
                </div>
              </div>
            </div>
          </template>

          <!-- 第三论级：天干关系 -->
          <template v-if="index === 2">
            <div class="gan-relations">
              <div class="relation-section" v-if="levelData[2].data.wuhe">
                <div class="subsection-title">天干五合</div>
                <div class="relation-list">
                  <div 
                    v-for="(item, idx) in levelData[2].data.wuhe" 
                    :key="idx"
                    class="relation-item"
                  >
                    <span class="gan-pair">{{ item.pair }}</span>
                    <span class="he-result">→ {{ item.result }}</span>
                  </div>
                </div>
              </div>
              <div class="relation-section" v-if="levelData[2].data.xiangke">
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
            </div>
          </template>

          <!-- 第四论级：特殊格局 -->
          <template v-if="index === 3">
            <div class="special-patterns">
              <div 
                v-for="(pattern, idx) in levelData[3].data.patterns" 
                :key="idx"
                class="pattern-card"
                :class="{ 'active': pattern.isActive }"
              >
                <div class="pattern-header">
                  <span class="pattern-name">{{ pattern.name }}</span>
                  <span class="pattern-status" :class="{ 'active': pattern.isActive }">
                    {{ pattern.isActive ? '符合' : '不符合' }}
                  </span>
                </div>
                <div class="pattern-desc" v-if="pattern.description">
                  {{ pattern.description }}
                </div>
              </div>
            </div>
          </template>

          <!-- 第五论级：定喜忌 -->
          <template v-if="index === 4">
            <div class="yonggod-grid">
              <div class="yonggod-card yong">
                <div class="yonggod-label">用神</div>
                <div class="yonggod-value">{{ levelData[4].data.yongshen || '无' }}</div>
                <div class="yonggod-desc">最需要补足的五行</div>
              </div>
              <div class="yonggod-card xi">
                <div class="yonggod-label">喜神</div>
                <div class="yonggod-value">{{ levelData[4].data.xishen || '无' }}</div>
                <div class="yonggod-desc">对命局有帮助的五行</div>
              </div>
              <div class="yonggod-card ji">
                <div class="yonggod-label">忌神</div>
                <div class="yonggod-value">{{ levelData[4].data.jishen || '无' }}</div>
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
            <div v-if="levelData[4].data.shierChangsheng" class="shier-changsheng">
              <div class="subsection-title">十二长生</div>
              <div class="pillars-status">
                <div v-for="(status, pillar) in levelData[4].data.shierChangsheng" :key="pillar" class="pillar-status">
                  <span class="pillar-name">{{ pillar }}</span>
                  <span class="status-value">{{ status }}</span>
                </div>
              </div>
            </div>
            <!-- 纳音 -->
            <div v-if="levelData[4].data.nayin" class="nayin-section">
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
                  <div class="dayun-ganzhi">{{ levelData[5].data.currentDayun.ganzhi || levelData[5].data.currentDayun.干支 }}</div>
                  <div class="dayun-range">{{ levelData[5].data.currentDayun.range || levelData[5].data.currentDayun.年份范围 }}</div>
                  <div class="dayun-effect" v-if="levelData[5].data.currentDayun.effect">{{ levelData[5].data.currentDayun.effect }}</div>
                </div>
              </div>
              <div class="liunian-section" v-if="levelData[5].data.liunian">
                <div class="subsection-title">流年影响</div>
                <div class="liunian-card">
                  <div class="liunian-year">{{ levelData[5].data.liunian.year || new Date().getFullYear() }}年</div>
                  <div class="liunian-ganzhi">{{ levelData[5].data.liunian.ganzhi || levelData[5].data.liunian.干支 }}</div>
                  <div class="liunian-effect" v-if="levelData[5].data.liunian.effect">{{ levelData[5].data.liunian.effect }}</div>
                </div>
              </div>
            </div>
            <!-- 五行能量影响 -->
            <div v-if="levelData[5].data.wuxingEffect" class="wuxing-effect">
              <div class="subsection-title">大运流年五行影响</div>
              <div class="effect-list">
                <div v-for="(effect, wx) in levelData[5].data.wuxingEffect" :key="wx" class="effect-item">
                  <span class="effect-name">{{ wx }}</span>
                  <span class="effect-change" :class="{ 'increase': effect.变化 > 0, 'decrease': effect.变化 < 0 }">
                    {{ effect.变化 > 0 ? '+' : '' }}{{ effect.变化 }}分
                  </span>
                  <span class="effect-result">→ {{ effect.大运流年后 }}分</span>
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

// 六级数据
const levelData = computed(() => {
  const raw = props.analysisData || {}

  // 处理地支关系详情
  const relationsDetail = []
  if (raw.天干地支作用关系) {
    Object.entries(raw.天干地支作用关系).forEach(([key, value]) => {
      if (value && typeof value === 'object') {
        relationsDetail.push({
          name: key,
          ...value
        })
      }
    })
  }

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
        wuxingStrength: raw.格局综合判定?.五行旺相 || raw.第一论级_月令与格局?.五行旺相,
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
      },
      relationsDetail: relationsDetail
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
        gaitou: raw.第四论级_干支关系?.盖头 || [],
        jiejiao: raw.第四论级_干支关系?.截脚 || [],
        fuyin: raw.第四论级_干支关系?.伏吟 || [],
        fanyin: raw.第四论级_干支关系?.反吟 || []
      }
    },
    {
      number: '五',
      title: '定喜忌',
      subtitle: '用神、喜神、忌神、神煞',
      color: '#ef4444',
      data: {
        yongshen: raw.第五论级_定喜忌?.用神 || raw.第五论级_定喜忌?.喜用神,
        xishen: raw.第五论级_定喜忌?.喜神,
        jishen: raw.第五论级_定喜忌?.忌神,
        tiaohou: raw.第五论级_定喜忌?.调候用神,
        tiaohouDesc: raw.第五论级_定喜忌?.调候说明,
        growthAdvice: raw.第五论级_定喜忌?.成长建议 || raw.第五论级_定喜忌?.建议,
        shensha: raw.第五论级_定喜忌?.神煞 || raw.第五论级_辅助信息?.神煞 || {},
        shierChangsheng: raw.第五论级_辅助信息?.十二长生,
        kongwang: raw.第五论级_辅助信息?.空亡,
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
        dayunList: raw.第六论级_大运流年?.大运列表,
        wuxingEffect: raw.第六论级_大运流年?.五行能量影响,
        shishenEffect: raw.第六论级_大运流年?.十神能量影响
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
.gan-relations {
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

/* 特殊格局 */
.special-patterns {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pattern-card {
  background: #f8fafc;
  padding: 12px;
  border-radius: 10px;
  border-left: 3px solid #cbd5e1;
}

.pattern-card.active {
  border-left-color: #8b5cf6;
  background: linear-gradient(90deg, #f5f3ff 0%, #ffffff 100%);
}

.pattern-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.pattern-name {
  font-weight: 600;
  color: #1e293b;
}

.pattern-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #e2e8f0;
  color: #64748b;
}

.pattern-status.active {
  background: #8b5cf6;
  color: white;
}

.pattern-desc {
  font-size: 12px;
  color: #64748b;
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
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.yonggod-desc {
  font-size: 11px;
  color: #64748b;
}

/* 神煞 */
.shensha-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.shensha-tag {
  font-size: 12px;
  padding: 4px 10px;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #4338ca;
  border-radius: 20px;
  font-weight: 500;
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

/* 关系详情 */
.relations-detail {
  margin-top: 16px;
}

.relation-detail-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.relation-detail-item {
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
}

.detail-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 6px;
}

.detail-concept {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.detail-content {
  font-size: 12px;
  color: #475569;
  margin-bottom: 6px;
}

.detail-psychology, .detail-advice {
  font-size: 12px;
  color: #475569;
  margin-top: 4px;
}

.detail-label {
  font-weight: 600;
  color: #667eea;
}

/* 五行能量影响 */
.wuxing-effect {
  margin-top: 16px;
}

.effect-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.effect-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.effect-name {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  min-width: 40px;
}

.effect-change {
  font-size: 13px;
  font-weight: 600;
}

.effect-change.increase {
  color: #22c55e;
}

.effect-change.decrease {
  color: #ef4444;
}

.effect-result {
  font-size: 13px;
  color: #64748b;
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

  .effect-item {
    flex-wrap: wrap;
  }
}
</style>