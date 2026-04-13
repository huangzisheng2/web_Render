import axios from 'axios'

// API 基础 URL
// 本地开发使用代理，生产环境使用 Render 服务地址
const BASE_URL = import.meta.env.PROD 
  ? 'https://bazi-talent-api.onrender.com'  // Render 服务地址
  : ''

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000, // 120秒超时（AI分析可能较慢）
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
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
    if (error.response) {
      return Promise.reject(new Error(error.response.data?.error || '服务器错误'))
    }
    return Promise.reject(new Error('网络错误'))
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
