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
const MAX_RETRIES = 2

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
      // 延迟重试，避免立即重发
      await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)))
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
