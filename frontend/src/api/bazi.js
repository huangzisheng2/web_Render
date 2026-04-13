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
  timeout: 180000, // 180秒超时（Render 免费版唤醒+AI分析可能较慢）
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 根据调试模式添加请求头
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    // 调试模式下添加 X-Debug-Mode 请求头
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

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    if (error.code === 'ECONNABORTED') {
      return Promise.reject(new Error('请求超时，服务器可能正在唤醒，请稍后再试'))
    }
    if (error.response) {
      return Promise.reject(new Error(error.response.data?.error || '服务器错误'))
    }
    if (error.message?.includes('Network Error')) {
      return Promise.reject(new Error('网络连接失败，服务器可能正在唤醒（约需30秒-2分钟）'))
    }
    return Promise.reject(new Error(error.message || '网络错误'))
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
 * @returns {Promise}
 */
export const analyzeAI = (data) => {
  return api.post('/api/analyze-ai', data)
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
 * 提交用户反馈
 * @param {Object} data - 反馈数据 {rating, feedback_text, experience_type}
 * @returns {Promise}
 */
export const submitFeedback = (data) => {
  return api.post('/api/feedback', data)
}

export default api
