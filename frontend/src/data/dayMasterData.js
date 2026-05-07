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

// 天干拼音映射（用于ASCII文件名）
const GAN_PINYIN_MAP = {
  '甲': 'jia', '乙': 'yi',
  '丙': 'bing', '丁': 'ding',
  '戊': 'wu', '己': 'ji',
  '庚': 'geng', '辛': 'xin',
  '壬': 'ren', '癸': 'gui'
}

// 五行拼音映射
const ELEMENT_PINYIN_MAP = {
  '木': 'mu', '火': 'huo',
  '土': 'tu', '金': 'jin',
  '水': 'shui'
}

// Vite 基准路径（开发环境为 '/'，生产环境为 base 配置值如 './'）
const BASE_URL = import.meta.env.BASE_URL || '/'

/**
 * 获取Q版形象路径（使用 Vite BASE_URL 确保部署子路径下也正确）
 * @param {string} dayMaster - 天干（甲乙丙丁戊己庚辛壬癸）
 * @param {string} gender - 性别（支持 'male'/'female' 或 '男'/'女'）
 * @returns {string} 图片路径
 */
export function getQVersionAvatar(dayMaster, gender) {
  const ganPinyin = GAN_PINYIN_MAP[dayMaster] || 'jia'
  const element = GAN_ELEMENT_MAP[dayMaster] || '木'
  const elementPinyin = ELEMENT_PINYIN_MAP[element] || 'mu'
  const genderText = (gender === 'male' || gender === '男') ? 'm' : 'f'
  return `${BASE_URL}q-avatar/${ganPinyin}_${elementPinyin}_${genderText}.png`
}

/**
 * 获取完整 Q版形象 URL（兼容 Vite dev + 部署子路径）
 */
export function getFullAvatarUrl(dayMaster, gender) {
  const path = getQVersionAvatar(dayMaster, gender)
  // Vite dev 环境：path 为 /q-avatar/xxx.png，直接 origin + path
  if (!path.startsWith('./')) {
    return `${window.location.origin}${path}`
  }
  // 生产环境下（base='./'）：path 为 ./q-avatar/xxx.png
  // 从当前页面 URL 提取子路径前缀
  let basePath = window.location.pathname
  // 去掉末尾文件名（如 index.html）保留目录路径
  const lastSlash = basePath.lastIndexOf('/')
  if (lastSlash > 0) {
    basePath = basePath.substring(0, lastSlash)
  } else if (lastSlash === 0) {
    basePath = ''
  }
  const cleanOrigin = window.location.origin.replace(/\/+$/, '')
  const cleanBase = basePath.replace(/\/+$/, '')
  return `${cleanOrigin}${cleanBase}/${path.slice(2)}`
}

/**
 * 根据日主获取特质信息
 * @param {string} dayMaster - 天干
 * @param {string} gender - 性别
 * @returns {Object} 特质信息对象
 */
export function getDayMasterTrait(dayMaster, gender) {
  const trait = TRAIT_DESCRIPTIONS[dayMaster] || TRAIT_DESCRIPTIONS['甲']
  const isMale = (gender === 'male' || gender === '男')
  return {
    ...trait,
    description: trait[isMale ? 'male' : 'female'],
    dayMaster,
    gender: isMale ? 'male' : 'female'
  }
}

/**
 * 六十日柱特质关键词（前端原生，不依赖AI）
 * 每个日柱2~6字，描述性格特质/行为习惯/思维模式
 */
export const DAY_PILLAR_SUMMARIES = {
  '甲子': '灵秀仁厚，内蕴傲骨',
  '甲戌': '稳重善积，内怀孤明',
  '甲申': '逆境英才，智略深沉',
  '甲午': '明快开创，锋芒毕露',
  '甲辰': '敦厚包容，龙潜于渊',
  '甲寅': '刚健自强，虎啸山林',
  '乙丑': '坚毅谋深，金藏于矿',
  '乙卯': '柔韧独立，秀木临风',
  '乙巳': '灵动善变，才华横溢',
  '乙未': '温厚善营，秀外慧中',
  '乙酉': '刚烈锐进，绝处逢生',
  '乙亥': '温良仁爱，依水而兴',
  '丙寅': '热情开拓，旭日东升',
  '丙子': '外明内敛，水火相济',
  '丙戌': '稳重务实，厚德载物',
  '丙申': '智谋理财，慧眼识金',
  '丙午': '豪迈奔放，烈日当空',
  '丙辰': '圆融练达，光华内蕴',
  '丁未': '细腻文雅，静水流深',
  '丁酉': '精明务实，金水相涵',
  '丁亥': '温和守正，暗室逢灯',
  '丁丑': '沉稳多谋，寒梅待春',
  '丁卯': '敏感深邃，幽兰独芳',
  '丁巳': '热情锐意，燎原之火',
  '戊辰': '敦厚稳重，山峦叠嶂',
  '戊寅': '威猛开拓，虎跃深谷',
  '戊子': '务实内敛，水润厚土',
  '戊戌': '刚健守成，孤峰独秀',
  '戊申': '乐观善艺，金石之声',
  '戊午': '热情仁厚，霞光满天',
  '己丑': '精明持重，美玉藏石',
  '己卯': '坚韧负重，逆水行舟',
  '己巳': '聪慧刚强，火土相生',
  '己未': '温和守信，厚土载物',
  '己酉': '优雅善创，珠圆玉润',
  '己亥': '远见务实，静水流深',
  '庚子': '锐意创新，金水相激',
  '庚寅': '纵横阔达，虎啸生风',
  '庚辰': '谋略深沉，龙隐深渊',
  '庚午': '威严守正，烈火炼金',
  '庚申': '刚健果决，金刚怒目',
  '庚戌': '沉稳刚毅，宝刀藏鞘',
  '辛丑': '内秀中和，金润湿土',
  '辛卯': '敏锐逐利，风拂玉树',
  '辛巳': '机变严谨，火炼真金',
  '辛未': '谋定后动，沙里淘金',
  '辛酉': '独立傲然，金凤独立',
  '辛亥': '潇洒奔放，水泄银辉',
  '壬辰': '气魄雄浑，龙归大海',
  '壬申': '智谋深远，水泄银河',
  '壬子': '浩荡不羁，汪洋之水',
  '壬午': '圆融多情，水火既济',
  '壬寅': '乐天多才，水木清华',
  '壬戌': '沉稳霸气，海纳百川',
  '癸丑': '隐忍深沉，寒潭蓄势',
  '癸卯': '清秀出尘，空谷幽兰',
  '癸巳': '慧中秀外，水滴石穿',
  '癸未': '坚韧机变，枯木逢春',
  '癸酉': '深邃奇崛，月映寒潭',
  '癸亥': '磅礴大气，巨浪滔天'
}

/**
 * 获取日柱特质关键词（前端原生，不调用API或AI）
 * @param {string} dayPillar - 日柱全称，如"甲子"
 * @returns {string} 日柱特质关键词
 */
export function getDayColumnSummary(dayPillar) {
  return DAY_PILLAR_SUMMARIES[dayPillar] || ''
}

// 五行对应元素符号
export const ELEMENT_SYMBOLS = {
  '木': { symbol: '🌲', name: '木' },
  '火': { symbol: '🔥', name: '火' },
  '土': { symbol: '⛰️', name: '土' },
  '金': { symbol: '⚔️', name: '金' },
  '水': { symbol: '💧', name: '水' }
}
