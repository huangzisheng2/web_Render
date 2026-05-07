/**
 * 十天干日主数据配置
 * 包含：Q版形象映射、特质配文、颜色主题等
 */

// 十天干列表
export const DAY_MASTERS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

// 日主特质配文（一句话概括，区分性别）
export const TRAIT_DESCRIPTIONS = {
  // 甲木 - 阳木，如大树参天
  '甲': {
    male: '如参天大树般正直挺拔，天生具有领导力与担当精神',
    female: '如青松翠柏般坚韧优雅，外柔内刚自有主张',
    color: '#22C55E', // 翠绿
    element: '木'
  },
  // 乙木 - 阴木，如花草藤蔓
  '乙': {
    male: '如藤蔓般灵活变通，善于适应环境且心思细腻',
    female: '如兰花般温婉灵动，聪慧过人且善解人意',
    color: '#4ADE80', // 嫩绿
    element: '木'
  },
  // 丙火 - 阳火，如太阳普照
  '丙': {
    male: '如烈日当空般热情奔放，光明磊落乐于奉献',
    female: '如暖阳般温暖明亮，热情大方人缘极佳',
    color: '#EF4444', // 正红
    element: '火'
  },
  // 丁火 - 阴火，如灯火烛光
  '丁': {
    male: '如烛光般内敛温和，心思缜密洞察力强',
    female: '如星光般温柔细腻，默默付出不求回报',
    color: '#F97316', // 橙红
    element: '火'
  },
  // 戊土 - 阳土，如高山厚土
  '戊': {
    male: '如高山般稳重可靠，值得信赖的守护者',
    female: '如大地般包容宽厚，给人安全感与温暖',
    color: '#D97706', // 土黄
    element: '土'
  },
  // 己土 - 阴土，如田园沃土
  '己': {
    male: '如田园般温和敦厚，善于滋养培育他人',
    female: '如春泥般细腻温柔，润物细无声的关怀',
    color: '#A3A3A3', // 灰土
    element: '土'
  },
  // 庚金 - 阳金，如刀剑斧钺
  '庚': {
    male: '如利剑般刚毅果敢，行事雷厉风行讲义气',
    female: '如寒梅般傲骨铮铮，独立自强不随波逐流',
    color: '#64748B', // 银灰（金属色）
    element: '金'
  },
  // 辛金 - 阴金，如珠宝玉石
  '辛': {
    male: '如美玉般温润精致，追求完美品味独特',
    female: '如珍珠般晶莹剔透，气质出众审美一流',
    color: '#94A3B8', // 浅银
    element: '金'
  },
  // 壬水 - 阳水，如江河湖海
  '壬': {
    male: '如江河般奔腾不息，胸怀宽广志向远大',
    female: '如大海般深沉包容，智慧深邃洞察人心',
    color: '#0EA5E9', // 海蓝
    element: '水'
  },
  // 癸水 - 阴水，如雨露甘霖
  '癸': {
    male: '如清泉般清澈纯净，思维敏捷灵感不断',
    female: '如雨露般滋润万物，善解人意温柔体贴',
    color: '#67E8F9', // 浅蓝
    element: '水'
  }
}

// 天干与五行映射
const GAN_ELEMENT_MAP = {
  '甲': '木', '乙': '木',
  '丙': '火', '丁': '火',
  '戊': '土', '己': '土',
  '庚': '金', '辛': '金',
  '壬': '水', '癸': '水'
}

/**
 * 获取Q版形象路径
 * @param {string} dayMaster - 天干（甲乙丙丁戊己庚辛壬癸）
 * @param {string} gender - 性别（male/female）
 * @returns {string} 图片路径
 */
export function getQVersionAvatar(dayMaster, gender) {
  const element = GAN_ELEMENT_MAP[dayMaster] || '木'
  const genderText = gender === 'male' ? '男' : '女'
  return `/q-avatar/${dayMaster}${element}${genderText}.png`
}

/**
 * 根据日主获取特质信息
 * @param {string} dayMaster - 天干
 * @param {string} gender - 性别
 * @returns {Object} 特质信息对象
 */
export function getDayMasterTrait(dayMaster, gender) {
  const trait = TRAIT_DESCRIPTIONS[dayMaster] || TRAIT_DESCRIPTIONS['甲']
  const isMale = gender === 'male' ? 'male' : 'female'
  return {
    ...trait,
    description: trait[isMale],
    dayMaster,
    gender: isMale
  }
}

// 五行对应元素符号
export const ELEMENT_SYMBOLS = {
  '木': { symbol: '🌲', name: '木' },
  '火': { symbol: '🔥', name: '火' },
  '土': { symbol: '⛰️', name: '土' },
  '金': { symbol: '⚔️', name: '金' },
  '水': { symbol: '💧', name: '水' }
}
