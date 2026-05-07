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
 * 日柱特质总结（前端原生，不依赖AI）
 * 描述性格特质、行为习惯和思维模式，使用现代心理学语言
 */
export const DAY_COLUMN_SUMMARIES = {
  '甲': {
    male: '你天生具有开拓者的气质和领导者的担当。做决策时果断有力，习惯站在全局视角思考问题，擅长在混乱中建立秩序。思维模式偏向战略性，喜欢从宏观入手再层层拆解。行为上积极主动，不畏惧挑战，但偶尔会因过于自信而忽略细节。适合在需要魄力和方向感的角色中发挥天赋。',
    female: '你如青松般坚韧，外表柔和但内心自有定见。思维具有穿透力，能一眼看透问题的本质。做决定前习惯深思熟虑，但一旦确定目标就会坚定不移地推进。在团队中你往往扮演稳定军心的角色，不张扬却不可或缺。行为上注重原则和底线，有一种让人信赖的力量。'
  },
  '乙': {
    male: '你像藤蔓一样灵活，拥有极强的适应能力和变通智慧。思维发散且富有创造力，能从不同角度找到解决方案。习惯在复杂关系中游刃有余，善于借力使力。行为上温和而不失韧性，不喜欢正面冲突但总能绕到目标背后。你的核心优势是灵活应变和人际协调能力。',
    female: '你如兰花般温婉灵动，拥有细腻的情感感知力和敏锐的观察力。思维跳跃富有想象力，擅长把零散的信息编织成完整的画面。行为上温和体贴，善解人意，总能在别人需要时给予恰到好处的支持。你的独特之处在于用柔软的方式推动改变，春风化雨般影响周围的人。'
  },
  '丙': {
    male: '你像太阳一样热情奔放，自带感染力。思维活跃且开放，习惯边做边想，在行动中不断调整优化。拥有强烈的表现欲和分享欲，喜欢站在舞台中央。行为上大方慷慨，乐于助人，但偶尔会因热情过度而透支精力。你最大的天赋是用你的光和热去点燃他人。',
    female: '你如暖阳般温暖明亮，身边的人总能感受到你的积极能量。思维敏捷且富有创造力，习惯多线并行推进事情。在社交中你游刃有余，是天生的氛围营造者。行为上热情大方，乐于助人，有很强的号召力和感染力。你的独特之处在于能用乐观和行动力感染身边的人。'
  },
  '丁': {
    male: '你如烛光般内敛而深刻，拥有敏锐的洞察力和细腻的心思。习惯深度思考，倾向于在做之前把每个细节都推演清楚。思维周密且富有逻辑，擅长发现别人忽略的盲点。行为上低调务实，不喜欢浮夸，但总能在关键时刻给出精准的判断。你的核心优势是深度思考和精益求精。',
    female: '你如星光般温柔而恒久，拥有细腻的感知力和持久的专注力。思维缜密且富有条理，习惯把复杂问题分解成可控的小步骤。行为上内敛沉稳，默默付出不求关注，但你的成果总会被人看见。你的独特之处在于用耐心和细致把事情做到极致，在平凡中创造不凡。'
  },
  '戊': {
    male: '你如高山般稳重可靠，是团队中值得信赖的中流砥柱。思维偏重务实，习惯用经验判断而非直觉决策。做事讲究节奏和分寸，从不急于求成。行为上包容大度，能扛住压力，给人十足的安全感。你的核心优势是稳定性和承载能力，是那种「把事情交给你就放心了」的人。',
    female: '你如大地般包容宽厚，拥有强大的接纳力和持久的耐力。思维务实稳健，习惯从实际出发分析问题。在关系中你扮演支持者的角色，总能给人踏实的感觉。行为上不急不躁，用自己的节奏把事情一件件做好。你的独特之处在于用稳定和坚持赢得信任，让身边的人感到安心。'
  },
  '己': {
    male: '你如田园般温和敦厚，拥有细腻的感受力和服务精神。思维注重实践，习惯从具体经验中提炼规律。善于观察他人的需求，总能在别人开口之前就伸出援手。行为上谦逊低调，不喜欢出风头，但你润物细无声的关怀让别人离不开你。你的核心优势是细腻的服务意识和务实精神。',
    female: '你如春泥般细腻温柔，拥有独特的美感和创造力。思维感性且富有诗意，习惯用情感连接来理解世界。行为上体贴入微，注重细节和品质，总能把平凡的事情做得有温度。你的独特之处在于用细腻的感知把生活和工作都经营得有声有色。'
  },
  '庚': {
    male: '你如利剑般刚毅果敢，拥有强大的执行力和决断力。思维直来直去，追求效率和结果，不喜欢拐弯抹角。行为上雷厉风行，说到做到，讲义气重承诺。在压力下反而能爆发出更强的战斗力。你的核心优势是果断执行和在逆境中破局的能力。',
    female: '你如寒梅般傲骨铮铮，独立而坚韧。思维清晰直接，习惯直击问题核心，不喜欢拖泥带水。行为上自立自强，有自己的原则和底线，不随波逐流。在人群中你自带气场，不需要刻意表现就能让人记住。你的独特之处是独立自主和在压力下依然保持冷静。'
  },
  '辛': {
    male: '你如美玉般温润精致，拥有独特的品味和审美能力。思维细腻且追求完美，习惯在细节中打磨出精品。行为上有自己的节奏和标准，不轻易妥协。你对品质有着天生的敏感度，能在别人忽视的地方发现价值。你的核心优势是审美能力和对完美的执着追求。',
    female: '你如珍珠般晶莹剔透，气质出众且品味一流。思维精致且有层次感，习惯从美和体验的角度理解事物。行为上有自己独特的风格，不盲从潮流，而是创造潮流。你的独特之处在于用审美和品位为周围的一切增添光彩。'
  },
  '壬': {
    male: '你如江河般奔腾不息，拥有广阔的胸怀和远大的志向。思维开阔且富有远见，习惯从长期视角规划人生。喜欢探索未知领域，对新事物充满好奇。行为上不拘小节，善于整合资源和人脉，天生具备领导潜质。你的核心优势是远见卓识和资源整合能力。',
    female: '你如大海般深沉包容，拥有深邃的智慧和洞察力。思维广阔且富有哲学气质，习惯思考深层次的人性和规律。在人际中你包容大度，能理解不同角度的观点。行为上大气从容，不纠缠于细枝末节。你的独特之处在于用智慧和格局为他人提供方向的指引。'
  },
  '癸': {
    male: '你如清泉般清澈纯净，思维敏捷且灵感不断。习惯在安静的环境中深度思考，灵感常常在不经意间涌现。行为上看似随和但有自己的原则，对新事物接受度高，学习能力强。你的核心优势是快速学习和灵感的创造力。',
    female: '你如雨露般润物无声，善解人意且温柔体贴。思维灵动富有创造力，习惯用直觉和感受来理解世界。行为上细腻周到，总能察觉别人隐藏的情绪和需求。你的独特之处在于用温柔的方式治愈和滋养身边的人，是那种润物细无声的存在。'
  }
}

/**
 * 获取日柱特质总结（前端原生，不调用API或AI）
 * @param {string} dayMaster - 天干
 * @param {string} gender - 性别
 * @returns {string} 日柱特质描述文本
 */
export function getDayColumnSummary(dayMaster, gender) {
  const summaries = DAY_COLUMN_SUMMARIES[dayMaster]
  if (!summaries) return ''
  const isMale = (gender === 'male' || gender === '男')
  return summaries[isMale ? 'male' : 'female'] || ''
}

// 五行对应元素符号
export const ELEMENT_SYMBOLS = {
  '木': { symbol: '🌲', name: '木' },
  '火': { symbol: '🔥', name: '火' },
  '土': { symbol: '⛰️', name: '土' },
  '金': { symbol: '⚔️', name: '金' },
  '水': { symbol: '💧', name: '水' }
}
