<template>
  <div class="app">
    <!-- 主内容区 - 页面路由 -->
    <Transition name="fade" mode="out-in">
      <!-- 1. 引导启动页 -->
      <LandingPage 
        v-if="currentPage === 'landing'" 
        key="landing"
        @start="goToQuiz"
      />
      
      <!-- 2. 趣味答题页 -->
      <QuizPage 
        v-else-if="currentPage === 'quiz'" 
        key="quiz"
        @complete="goToForm"
      />
      
      <!-- 3. 信息填写页 -->
      <StepForm 
        v-else-if="currentPage === 'form'" 
        key="form"
        @submit="handleAnalyze"
      />
      
      <!-- 4. AI生成等待页 -->
      <LoadingPage 
        v-else-if="currentPage === 'loading'" 
        key="loading"
        :is-waking-up="isServerWakingUp"
      />
      
      <!-- 5. 结果展示页 -->
      <ResultDisplay
        v-else-if="currentPage === 'result'"
        key="result"
        :result="result"
        :ai-analyzing="aiAnalyzing"
        @reset="handleReset"
        @download="handleDownload"
        @analyze-ai="handleAIAnalyze"
        :downloading="downloading"
      />
    </Transition>

    <!-- Toast 提示 -->
    <div v-if="toast.show" class="toast" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<<<<<<< HEAD
/*
================================================================================
【用户模式 vs 调试模式 设计原则】

用户模式（默认，不带 ?debug=true）：
- 隐私优先：不返回任何原始命理数据（raw_data、bazi、analysis等）
- 简化流程：后端自动完成基础分析+AI分析，前端只接收 ai_report
- 前端展示：只显示AI报告文本 + PDF下载 + 用户反馈
- 数据流向：填写信息 → /api/analyze → 后端计算+AI分析 → 返回{ai_report}

调试模式（带 ?debug=true）：
- 完整数据：返回所有命理计算数据（raw_data、bazi、analysis等）
- 分步流程：后端基础分析 → 前端显示 → 手动触发AI分析
- 前端展示：显示完整命理图表 + AI报告 + 原始JSON调试面板
- 数据流向：填写信息 → /api/analyze → 返回完整数据 → /api/analyze-ai → AI报告

关键规则：
1. 用户模式绝不返回敏感计算数据，保护用户隐私
2. AI分析统一在后端完成，确保两种模式使用相同的提示词逻辑
3. 调试模式用于开发调试，用户模式用于生产环境
================================================================================
*/

import { ref, reactive, getCurrentInstance } from 'vue'
=======
<script setup>
import { ref, reactive } from 'vue'
>>>>>>> parent of 9751620 (优化)
import LandingPage from './components/LandingPage.vue'
import QuizPage from './components/QuizPage.vue'
import StepForm from './components/StepForm.vue'
import LoadingPage from './components/LoadingPage.vue'
import ResultDisplay from './components/ResultDisplay.vue'
import { analyzeBazi, analyzeAI, downloadReport } from './api/bazi'

// 页面路由状态
const currentPage = ref('landing') // landing, quiz, form, loading, result

const downloading = ref(false)
const aiAnalyzing = ref(false)
const result = ref(null)
const quizAnswers = ref([])
const isServerWakingUp = ref(false) // 服务器是否正在唤醒

// 页面导航
const goToQuiz = () => {
  currentPage.value = 'quiz'
}

const goToForm = (answers) => {
  quizAnswers.value = answers
  currentPage.value = 'form'
}

const goToLoading = () => {
  currentPage.value = 'loading'
}

const toast = reactive({
  show: false,
  message: '',
  type: 'success'
})

const showToast = (message, type = 'success') => {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => {
    toast.show = false
  }, 3000)
}

// Render 服务唤醒检查
const checkServerWakeUp = async () => {
  try {
    // 发送一个轻量级请求唤醒服务
    const response = await fetch('https://bazi-talent-api.onrender.com/')
    console.log('[服务器状态]', response.status)
    return true
  } catch (e) {
    console.warn('[服务器唤醒失败]', e)
    return false
  }
}

// 带重试的请求
const requestWithRetry = async (requestFn, maxRetries = 2) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      console.warn(`[请求重试 ${i + 1}/${maxRetries}]`, error.message)
      if (i === maxRetries - 1) throw error
      // 等待 3 秒后重试
      await new Promise(resolve => setTimeout(resolve, 3000))
    }
  }
}

// 执行分析
const handleAnalyze = async (formData) => {
  goToLoading()
  isServerWakingUp.value = false
  
  try {
<<<<<<< HEAD
    // 0. 先唤醒服务器（Render 免费版休眠问题）
    console.log('[步骤0] 检查服务器状态...')
    const isServerReady = await checkServerWakeUp()
    
    if (!isServerReady) {
      // 服务器可能在休眠，显示唤醒界面
      console.log('[步骤0] 服务器可能在休眠，显示唤醒界面...')
      isServerWakingUp.value = true
      
      // 等待 3 秒后重试
      await new Promise(resolve => setTimeout(resolve, 3000))
    }
    
    // 1. 执行基础八字分析（带重试）
    console.log('[步骤1] 执行基础分析...')
    isServerWakingUp.value = false
    const response = await requestWithRetry(() => analyzeBazi(formData), 3)
=======
    const response = await analyzeBazi(formData)
>>>>>>> parent of 9751620 (优化)
    
    if (response.success) {
      result.value = response.data
      currentPage.value = 'result'
      showToast('分析完成')
    } else {
      showToast(response.error || '分析失败', 'error')
      currentPage.value = 'form'
    }
<<<<<<< HEAD
    
    result.value = response.data
    
    // 2. 调试模式：需要手动触发AI分析（前端调用/api/analyze-ai）
    // 用户模式：后端已在/api/analyze中自动完成AI分析，只返回了{ai_report}
    if (isDebug) {
      console.log('[步骤2] 调试模式，等待用户手动触发AI分析')
    } else {
      console.log('[步骤2] 用户模式，后端已自动完成AI分析')
      console.log('[步骤2] ai_report长度:', result.value?.ai_report?.length || 0)
    }
    
    // 3. 显示结果页
    currentPage.value = 'result'
    showToast('分析完成')
    
=======
>>>>>>> parent of 9751620 (优化)
  } catch (error) {
    console.error('分析错误:', error)
    isServerWakingUp.value = false
    const errorMsg = error.message || '网络错误'
    if (errorMsg.includes('Network Error') || errorMsg.includes('network') || errorMsg.includes('唤醒')) {
      showToast('服务器正在唤醒，请刷新页面重试（约需30秒-2分钟）', 'error')
    } else {
      showToast(errorMsg, 'error')
    }
    currentPage.value = 'form'
  }
}

// 重置表单
const handleReset = () => {
  result.value = null
  aiAnalyzing.value = false
  quizAnswers.value = []
  currentPage.value = 'landing'
}

// AI 天赋分析
const handleAIAnalyze = async () => {
  if (!result.value?.report_id) {
    showToast('报告ID不存在', 'error')
    return
  }
  
  aiAnalyzing.value = true
  
  try {
    const response = await analyzeAI({
      report_id: result.value.report_id,
      basic_result: result.value
    })
    
    if (response.success) {
      result.value.ai_report = response.ai_report
      showToast('AI 分析完成')
    } else {
      showToast(response.error || 'AI 分析失败', 'error')
    }
  } catch (error) {
    console.error('AI 分析错误:', error)
    showToast('AI 分析失败，请稍后重试', 'error')
  } finally {
    aiAnalyzing.value = false
  }
}

// 下载报告
const handleDownload = async () => {
  if (!result.value?.report_id) {
    showToast('报告ID不存在', 'error')
    return
  }
  
  downloading.value = true
  
  try {
    // 方式1：后端生成 PDF
    const response = await downloadReport(result.value.report_id)
    
    if (response.success && response.download_url) {
      // 如果是 base64 PDF
      if (response.download_url.startsWith('data:')) {
        const link = document.createElement('a')
        link.href = response.download_url
        link.download = `八字分析报告_${result.value.user_info?.name || '匿名'}.pdf`
        link.click()
        showToast('下载开始')
      } else if (response.download_url.startsWith('html://')) {
        // 方式2：前端生成 PDF
        await generatePDF()
      }
    } else {
      // 备用：前端生成
      await generatePDF()
    }
  } catch (error) {
    console.error('下载错误:', error)
    // 备用方案
    await generatePDF()
  } finally {
    downloading.value = false
  }
}

// 前端生成 PDF（备用方案 - 仅AI报告）
const generatePDF = async () => {
  try {
    const aiReport = result.value?.ai_report
    if (!aiReport) {
      showToast('AI报告尚未生成', 'error')
      return
    }
    
    showToast('正在生成 PDF...')
    
    const userName = result.value.user_info?.name || '匿名'
    const gender = result.value.user_info?.gender || '未知'
    
    // 创建临时容器用于渲染PDF内容
    const container = document.createElement('div')
    container.style.cssText = `
      position: fixed;
      left: -9999px;
      top: 0;
      width: 595px;
      padding: 40px;
      background: white;
      font-family: "Microsoft YaHei", "SimHei", sans-serif;
    `
    
    // 转换Markdown为HTML
    const htmlContent = aiReport
      .replace(/### (.*)/g, '<h3 style="color:#4A5568;font-size:16px;margin:20px 0 10px;padding-bottom:8px;border-bottom:2px solid #8EC5FC;">$1</h3>')
      .replace(/## (.*)/g, '<h2 style="color:#4A5568;font-size:18px;margin:24px 0 12px;padding-bottom:10px;border-bottom:3px solid #8EC5FC;">$1</h2>')
      .replace(/# (.*)/g, '<h1 style="color:#4A5568;font-size:22px;margin:28px 0 16px;text-align:center;">$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong style="color:#4A5568;">$1</strong>')
      .replace(/\n/g, '<br>')
    
    container.innerHTML = `
      <div style="text-align:center;margin-bottom:30px;">
        <h1 style="font-size:24px;color:#4A5568;margin:0 0 8px;">${userName}天赋分析报告</h1>
        <p style="font-size:12px;color:#718096;margin:0;">性别：${gender}</p>
      </div>
      <div style="line-height:1.8;color:#4A5568;font-size:13px;">
        ${htmlContent}
      </div>
      <div style="margin-top:40px;padding-top:20px;border-top:1px solid #E2E8F0;text-align:center;font-size:10px;color:#A0AEC0;">
        <p>本报告由 AI 生成，仅供参考</p>
        <p>生成时间：${new Date().toLocaleString('zh-CN')}</p>
      </div>
    `
    
    document.body.appendChild(container)
    
    // 使用html2canvas渲染为图片
    const html2canvas = await import('html2canvas')
    const canvas = await html2canvas.default(container, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff'
    })
    
    document.body.removeChild(container)
    
    // 创建PDF
    const { jsPDF } = await import('jspdf')
    const pdf = new jsPDF('p', 'mm', 'a4')
    
    const imgData = canvas.toDataURL('image/png')
    const imgWidth = 210
    const pageHeight = 297
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    
    let heightLeft = imgHeight
    let position = 0
    
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight
    
    // 处理多页
    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
    }
    
    pdf.save(`${userName}天赋分析报告.pdf`)
    showToast('PDF 已生成')
  } catch (error) {
    console.error('PDF生成错误:', error)
    showToast('PDF生成失败', 'error')
  }
}
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f8fafc;
  color: #1e293b;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app {
  min-height: 100vh;
}

/* 顶部导航 */
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.header-content {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo svg {
  width: 32px;
  height: 32px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
}

.header-subtitle {
  font-size: 14px;
  opacity: 0.9;
}

/* 主内容区 */
.main-content {
  flex: 1;
  padding: 24px 20px;
}

.form-wrapper {
  max-width: 480px;
  margin: 0 auto;
}

.form-intro {
  text-align: center;
  margin-bottom: 32px;
}

.intro-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12px;
}

.intro-desc {
  font-size: 15px;
  color: #64748b;
  line-height: 1.8;
}

/* 底部 */
.app-footer {
  padding: 24px 20px;
  text-align: center;
  border-top: 1px solid #e2e8f0;
  background: white;
}

.footer-text {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.footer-copyright {
  font-size: 12px;
  color: #cbd5e1;
}

/* Toast 提示 */
.toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%) translateY(-100px);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: white;
  z-index: 1000;
  animation: slideDown 0.3s forwards, fadeOut 0.3s 2.7s forwards;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.toast.success {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.toast.error {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

@keyframes slideDown {
  to {
    transform: translateX(-50%) translateY(0);
  }
}

@keyframes fadeOut {
  to {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* 响应式 */
@media (max-width: 640px) {
  .app-header {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
  
  .logo-text {
    font-size: 18px;
  }
  
  .header-subtitle {
    font-size: 12px;
  }
  
  .main-content {
    padding: 20px 16px;
  }
  
  .intro-title {
    font-size: 24px;
  }
  
  .intro-desc {
    font-size: 14px;
  }
}
</style>