/**
 * 五行颜色配置
 * 用于八字天干地支的五行颜色显示
 */

// 天干五行归属
export const GAN_WUXING = {
  '甲': '木', '乙': '木',
  '丙': '火', '丁': '火',
  '戊': '土', '己': '土',
  '庚': '金', '辛': '金',
  '壬': '水', '癸': '水'
}

// 地支五行归属
export const ZHI_WUXING = {
  '寅': '木', '卯': '木',
  '巳': '火', '午': '火',
  '辰': '土', '戌': '土', '丑': '土', '未': '土',
  '申': '金', '酉': '金',
  '子': '水', '亥': '水'
}

// 五行颜色配置（现代风格）
export const WUXING_COLORS = {
  '木': {
    primary: '#22c55e',      // 绿色
    light: '#dcfce7',        // 浅绿背景
    dark: '#15803d',         // 深绿
    gradient: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
    text: '#ffffff'
  },
  '火': {
    primary: '#ef4444',      // 红色
    light: '#fee2e2',        // 浅红背景
    dark: '#b91c1c',         // 深红
    gradient: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
    text: '#ffffff'
  },
  '土': {
    primary: '#d97706',      // 琥珀色/土黄色
    light: '#fef3c7',        // 浅黄背景
    dark: '#92400e',         // 深黄
    gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    text: '#ffffff'
  },
  '金': {
    primary: '#eab308',      // 金黄色
    light: '#fef9c3',        // 浅金背景
    dark: '#a16207',         // 深金
    gradient: 'linear-gradient(135deg, #facc15 0%, #eab308 100%)',
    text: '#000000'
  },
  '水': {
    primary: '#3b82f6',      // 蓝色
    light: '#dbeafe',        // 浅蓝背景
    dark: '#1d4ed8',         // 深蓝
    gradient: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    text: '#ffffff'
  }
}

// 十神颜色配置
export const SHISHEN_COLORS = {
  '比肩': '#22c55e',
  '劫财': '#16a34a',
  '食神': '#eab308',
  '伤官': '#ca8a04',
  '偏财': '#f97316',
  '正财': '#ea580c',
  '七杀': '#dc2626',
  '正官': '#b91c1c',
  '偏印': '#3b82f6',
  '正印': '#1d4ed8'
}

/**
 * 获取天干的五行属性
 * @param {string} gan - 天干
 * @returns {string} 五行属性
 */
export function getGanWuxing(gan) {
  return GAN_WUXING[gan] || '未知'
}

/**
 * 获取地支的五行属性
 * @param {string} zhi - 地支
 * @returns {string} 五行属性
 */
export function getZhiWuxing(zhi) {
  return ZHI_WUXING[zhi] || '未知'
}

/**
 * 获取天干的五行颜色配置
 * @param {string} gan - 天干
 * @returns {object} 颜色配置对象
 */
export function getGanColor(gan) {
  const wuxing = getGanWuxing(gan)
  return WUXING_COLORS[wuxing] || WUXING_COLORS['木']
}

/**
 * 获取地支的五行颜色配置
 * @param {string} zhi - 地支
 * @returns {object} 颜色配置对象
 */
export function getZhiColor(zhi) {
  const wuxing = getZhiWuxing(zhi)
  return WUXING_COLORS[wuxing] || WUXING_COLORS['木']
}

/**
 * 获取五行的颜色配置
 * @param {string} wuxing - 五行名称
 * @returns {object} 颜色配置对象
 */
export function getWuxingColor(wuxing) {
  return WUXING_COLORS[wuxing] || WUXING_COLORS['木']
}

/**
 * 获取十神的颜色
 * @param {string} shishen - 十神名称
 * @returns {string} 颜色值
 */
export function getShishenColor(shishen) {
  return SHISHEN_COLORS[shishen] || '#666666'
}

/**
 * 四柱位置配置
 */
export const PILLAR_POSITIONS = {
  'year': { name: '年柱', position: 'top' },
  'month': { name: '月柱', position: 'right' },
  'day': { name: '日柱', position: 'center' },
  'time': { name: '时柱', position: 'left' }
}

export default {
  GAN_WUXING,
  ZHI_WUXING,
  WUXING_COLORS,
  SHISHEN_COLORS,
  getGanWuxing,
  getZhiWuxing,
  getGanColor,
  getZhiColor,
  getWuxingColor,
  getShishenColor,
  PILLAR_POSITIONS
}