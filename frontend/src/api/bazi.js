import axios from 'axios'

// API 基础 URL
// 本地开发使用代理，生产环境使用 Render 服务地址
const BASE_URL = import.meta.env.PROD 
  ? 'https://bazi-talent-api.onrender.com'  // Render 服务地址
  : ''

// 检测调试模式
const urlParams = new URLSearchParams(window.location.search)
const isDebugMode = urlParams.get('debug') === 'true'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 150000, // 150秒超时（热点网络可能较慢）
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求重试计数器
const retryMap = new WeakMap()
const MAX_RETRIES = 3

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    if (isDebugMode) {
      config.headers['X-Debug-Mode'] = 'true'
      console.log('[DEBUG] 已添加 X-Debug-Mode 请求头')
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 增加重试逻辑，兼容不稳定网络（如手机热点）
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error) => {
    const config = error.config
    if (!config) {
      return Promise.reject(error)
    }

    // 网络错误或5xx错误时重试
    const isNetworkError = !error.response
    const isServerError = error.response && error.response.status >= 500
    const retryCount = retryMap.get(config) || 0

    if ((isNetworkError || isServerError) && retryCount < MAX_RETRIES) {
      retryMap.set(config, retryCount + 1)
      console.log(`API 请求重试 (${retryCount + 1}/${MAX_RETRIES}):`, config.url)
      // 延迟重试，间隔递增（适配热点网络）
      await new Promise(resolve => setTimeout(resolve, 3000 * (retryCount + 1)))
      return api(config)
    }

    console.error('API Error:', error)
    if (error.response) {
      return Promise.reject(new Error(error.response.data?.error || '服务器错误'))
    }
    return Promise.reject(new Error('网络错误，请检查网络连接后重试'))
  }
)

/**
 * 服务器预热：发送轻量级请求唤醒 Render 休眠实例
 * 适用于手机热点等不稳定网络环境，避免冷启动超时
 * @returns {Promise<boolean>} 预热是否成功
 */
export const warmupServer = async () => {
  const warmupApi = axios.create({
    baseURL: BASE_URL,
    timeout: 120000, // 预热超时2分钟（冷启动最多30秒）
    headers: { 'Content-Type': 'application/json' }
  })
  let lastError = null
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      console.log(`服务器预热中... (第${attempt}次)`)
      await warmupApi.get('/api/cities')
      console.log('服务器预热成功 ✓')
      return true
    } catch (e) {
      lastError = e
      console.warn(`预热尝试${attempt}失败:`, e.message)
      if (attempt < 3) {
        await new Promise(r => setTimeout(r, 5000 * attempt))
      }
    }
  }
  console.warn('服务器预热未完全成功，继续尝试主请求:', lastError?.message)
  return false
}

/**
 * 八字分析
 * @param {Object} data - 出生信息
 * @returns {Promise}
 */
export const analyzeBazi = (data) => {
  return api.post('/api/analyze', data)
}

/**
 * 获取城市列表
 * @returns {Promise}
 */
export const getCities = () => {
  return api.get('/api/cities')
}

/**
 * AI 天赋分析
 * @param {Object} data - 包含 report_id 和 basic_result
 * @param {string} mode - 分析模式: "detail"(默认) / "deep_explore"
 * @returns {Promise}
 */
export const analyzeAI = (data, mode = 'detail') => {
  return api.post('/api/analyze-ai', { ...data, mode })
}

/**
 * 下载报告
 * @param {string} reportId - 报告ID
 * @returns {Promise}
 */
export const downloadReport = (reportId) => {
  return api.get(`/api/download/${reportId}`)
}

/**
 * 提交用户反馈（多维度评分）
 * @param {Object} data - 反馈数据 {rating_overall, rating_design, rating_content, rating_helpful, feedback_text}
 * @returns {Promise}
 */
export const submitFeedback = (data) => {
  return api.post('/api/feedback', data)
}

export default api
