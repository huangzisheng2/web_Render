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
  timeout: 120000, // 120秒超时（AI分析可能较慢）
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
 * 提交用户反馈（多维度评分）
 * @param {Object} data - 反馈数据 {rating_overall, rating_design, rating_content, rating_helpful, feedback_text}
 * @returns {Promise}
 */
export const submitFeedback = (data) => {
  return api.post('/api/feedback', data)
}

/**
 * 流式八字分析 - 使用SSE
 * @param {Object} data - 出生信息
 * @param {Object} callbacks - 回调函数 {onStage, onContent, onDone, onError}
 * @returns {Function} 返回关闭连接的函数
 */
export const analyzeBaziStream = (data, callbacks) => {
  const BASE_URL = import.meta.env.PROD 
    ? 'https://bazi-talent-api.onrender.com'
    : ''
  
  // 使用fetch + ReadableStream 实现SSE流式读取
  // 原生EventSource不支持POST，所以使用fetch方案
  const controller = new AbortController()
  
  fetch(`${BASE_URL}/api/analyze-stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
    signal: controller.signal
  }).then(async (response) => {
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      
      // 解析SSE事件
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''
      
      for (const line of lines) {
        const event = parseSSEEvent(line)
        if (event) {
          handleSSEEvent(event, callbacks)
        }
      }
    }
    
    // 处理最后的数据
    if (buffer) {
      const event = parseSSEEvent(buffer)
      if (event) {
        handleSSEEvent(event, callbacks)
      }
    }
  }).catch((error) => {
    if (callbacks.onError) {
      callbacks.onError(error.message || '网络错误')
    }
  })
  
  // 返回关闭函数
  return () => controller.abort()
}

// 解析SSE事件
function parseSSEEvent(raw) {
  const lines = raw.trim().split('\n')
  let event = null
  let data = null
  
  for (const line of lines) {
    if (line.startsWith('event:')) {
      event = line.slice(6).trim()
    } else if (line.startsWith('data:')) {
      data = line.slice(5).trim()
    }
  }
  
  if (event && data) {
    try {
      return { event, data: JSON.parse(data) }
    } catch (e) {
      return { event, data }
    }
  }
  return null
}

// 处理SSE事件
function handleSSEEvent({ event, data }, callbacks) {
  switch (event) {
    case 'stage':
      if (callbacks.onStage) callbacks.onStage(data)
      break
    case 'content':
      if (callbacks.onContent) callbacks.onContent(data.chunk)
      break
    case 'done':
      if (callbacks.onDone) callbacks.onDone(data)
      break
    case 'error':
      if (callbacks.onError) callbacks.onError(data.error)
      break
  }
}

export default api
