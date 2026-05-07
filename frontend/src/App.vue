<template>
  <div class="app">
    <!-- 主内容区 - 页面路由 -->
    <Transition name="fade" mode="out-in">
      <!-- 1. 引导启动页 -->
      <LandingPage 
        v-if="currentPage === 'landing'" 
        key="landing"
        @start="goToIntro"
      />
      
      <!-- 2. 介绍页（新增） -->
      <IntroPage
        v-else-if="currentPage === 'intro'"
        key="intro"
        @next="goToForm"
      />
      
      <!-- 3. 信息填写页 -->
      <StepForm 
        v-else-if="currentPage === 'form'" 
        key="form"
        :initial-data="savedFormData"
        @submit="handleFormSubmit"
        @back="goToIntro"
      />
      
      <!-- 4. 趣味答题页（与报告生成并行） -->
      <QuizPage 
        v-else-if="currentPage === 'quiz'" 
        key="quiz"
        @complete="handleQuizComplete"
      />
      
      <!-- 5. AI生成等待页 -->
      <LoadingPage 
        v-else-if="currentPage === 'loading'" 
        key="loading"
        :report-ready="reportGenerationStatus === 'completed'"
        :analysis-stage="analysisStage"
        @continue="goToResult"
        @retry="handleReportRetry"
      />
      
      <!-- 6. 结果展示页（新架构：顶部导航 + 首页 + 简易/详细切换）-->
      <ReportPage
        v-else-if="currentPage === 'result'"
        key="result"
        :result="result"
        :downloading="downloading"
        :ai-analyzing="aiAnalyzing"
        @reset="handleReset"
      />
    </Transition>

    <!-- Toast 提示 -->
    <div v-if="toast.show" class="toast" :class="toast.type">
      {{ toast.message }}
    </div>
    
    <!-- 网络错误恢复提示 -->
    <div v-if="showErrorRecovery" class="error-recovery-toast">
      <div class="error-content">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <div class="error-text">
          <p>上次分析未完成</p>
          <span>点击继续分析</span>
        </div>
      </div>
      <div class="error-actions">
        <button class="cancel-btn" @click="handleCancelRecovery">
          取消
        </button>
        <button class="continue-btn" @click="handleContinueAnalysis">
          继续分析
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, getCurrentInstance, onMounted } from 'vue'
import LandingPage from './components/LandingPage.vue'
import IntroPage from './components/IntroPage.vue'
import QuizPage from './components/QuizPage.vue'
import StepForm from './components/StepForm.vue'
import LoadingPage from './components/LoadingPage.vue'
import ReportPage from './components/ReportPage.vue'
import { analyzeBazi, analyzeAI, downloadReport } from './api/bazi'
import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'

// 检测调试模式
const { appContext } = getCurrentInstance()
const isDebug = appContext.config.globalProperties.$isDebug || false

// ==================== 状态持久化（sessionStorage，刷新保留，关闭标签页清除） ====================
const SESSION_KEY = 'bazi_app_state'

const saveState = () => {
  try {
    const state = {
      currentPage: currentPage.value,
      reportGenerationStatus: reportGenerationStatus.value,
      analysisStage: analysisStage.value,
      result: result.value,
      savedFormData: savedFormData.value,
      pendingFormData: pendingFormData.value,
      quizAnswers: quizAnswers.value,
      aiAnalyzing: aiAnalyzing.value,
      timestamp: Date.now()
    }
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(state))
  } catch (e) {
    console.error('保存页面状态失败:', e)
  }
}

const restoreState = () => {
  try {
    const saved = sessionStorage.getItem(SESSION_KEY)
    if (!saved) return false
    const state = JSON.parse(saved)
    // 新用户或 landing 页面不恢复
    if (!state.currentPage || state.currentPage === 'landing') {
      sessionStorage.removeItem(SESSION_KEY)
      return false
    }
    currentPage.value = state.currentPage
    if (state.reportGenerationStatus) reportGenerationStatus.value = state.reportGenerationStatus
    if (state.analysisStage) analysisStage.value = state.analysisStage
    if (state.result) result.value = state.result
    if (state.savedFormData) savedFormData.value = state.savedFormData
    if (state.pendingFormData) pendingFormData.value = state.pendingFormData
    if (state.quizAnswers) quizAnswers.value = state.quizAnswers
    if (state.aiAnalyzing !== undefined) aiAnalyzing.value = state.aiAnalyzing
    console.log(`[恢复] 从 sessionStorage 恢复页面: ${state.currentPage}`)
    return true
  } catch (e) {
    console.error('恢复页面状态失败:', e)
    sessionStorage.removeItem(SESSION_KEY)
    return false
  }
}

const clearState = () => {
  try { sessionStorage.removeItem(SESSION_KEY) } catch (e) { /* ignore */ }
}

// ==================== 状态定义 ====================

// 页面路由状态
const currentPage = ref('landing') // landing, intro, form, quiz, loading, result

// 监听页面变化，滚动到顶部并保存状态
watch(currentPage, () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
  document.documentElement.scrollTop = 0
  document.body.scrollTop = 0
  saveState()
})

// 监听 result 变化自动保存
watch(result, (newVal) => {
  if (newVal) saveState()
})

// 报告生成状态
const reportGenerationStatus = ref('idle') // idle, generating, completed, error

// 分析阶段状态（用于LoadingPage进度显示）
const analysisStage = ref('data') // data, ai-parse, generating, returning, completed

// 保存的表单数据（用于失败恢复）
const savedFormData = ref(null)
const pendingFormData = ref(null)

// 显示错误恢复提示
const showErrorRecovery = ref(false)

const downloading = ref(false)
const aiAnalyzing = ref(false)
const result = ref(null)
const quizAnswers = ref([])

// 页面导航
const goToIntro = () => {
  currentPage.value = 'intro'
}

const goToForm = () => {
  currentPage.value = 'form'
}

const goToQuiz = () => {
  currentPage.value = 'quiz'
}

const goToLoading = () => {
  currentPage.value = 'loading'
}

const goToResult = () => {
  if (result.value) {
    currentPage.value = 'result'
  }
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

// 处理表单提交 - 新流程：提交后同时开始生成报告和答题
const handleFormSubmit = async (formData) => {
  // 保存表单数据
  savedFormData.value = { ...formData }
  pendingFormData.value = { ...formData }
  
  // 清除之前的错误恢复状态
  localStorage.removeItem('pendingAnalysis')
  
  // 开始并行处理：后台生成报告 + 用户答题
  reportGenerationStatus.value = 'generating'
  
  // 启动报告生成（不等待）
  startReportGeneration(formData)
  
  // 跳转到答题页面
  goToQuiz()
}

// 启动报告生成（后台）
const startReportGeneration = async (formData) => {
  // 阶段1：数据分析（立即开始）
  analysisStage.value = 'data'
  
  // 模拟阶段进度（因为后端是同步返回，前端模拟进度提升用户体验）
  const stageTimers = []
  
  // 阶段2：AI解析（5秒后）
  stageTimers.push(setTimeout(() => {
    if (reportGenerationStatus.value === 'generating') {
      analysisStage.value = 'ai-parse'
    }
  }, 5000))
  
  // 阶段3：生成报告（15秒后）
  stageTimers.push(setTimeout(() => {
    if (reportGenerationStatus.value === 'generating') {
      analysisStage.value = 'generating'
    }
  }, 15000))
  
  // 阶段4：返回结果（30秒后，如果还在等待）
  stageTimers.push(setTimeout(() => {
    if (reportGenerationStatus.value === 'generating') {
      analysisStage.value = 'returning'
    }
  }, 30000))
  
  try {
    const response = await analyzeBazi(formData)
    
    // 清除所有阶段定时器
    stageTimers.forEach(timer => clearTimeout(timer))
    
    if (!response.success) {
      console.error('报告生成失败:', response.error)
      reportGenerationStatus.value = 'error'
      analysisStage.value = 'data'
      // 保存错误状态到本地存储，用于恢复
      savePendingState(formData, 'error')
      return
    }
    
    result.value = response.data
    reportGenerationStatus.value = 'completed'
    analysisStage.value = 'completed'
    
    // 清除待处理状态
    localStorage.removeItem('pendingAnalysis')
    saveState() // 保存结果到 sessionStorage
    
    // 如果 AI 分析失败但基础分析成功，显示提示
    if (response.data?.ai_error) {
      console.warn('AI 分析失败:', response.data.ai_error)
      showToast('基础分析完成，AI 报告生成异常，可在结果页重试', 'info')
    }
    
  } catch (error) {
    // 清除所有阶段定时器
    stageTimers.forEach(timer => clearTimeout(timer))
    
    console.error('报告生成错误:', error)
    reportGenerationStatus.value = 'error'
    analysisStage.value = 'data'
    // 保存错误状态到本地存储，用于恢复
    savePendingState(formData, 'error')
    saveState()
  }
}

// 保存待处理状态到本地存储
const savePendingState = (formData, status) => {
  try {
    localStorage.setItem('pendingAnalysis', JSON.stringify({
      formData,
      status,
      timestamp: Date.now()
    }))
  } catch (e) {
    console.error('保存状态失败:', e)
  }
}

// 检查是否有待处理的分析
const checkPendingAnalysis = () => {
  try {
    const pending = localStorage.getItem('pendingAnalysis')
    if (pending) {
      const data = JSON.parse(pending)
      // 检查是否超过24小时
      if (Date.now() - data.timestamp < 24 * 60 * 60 * 1000) {
        savedFormData.value = data.formData
        pendingFormData.value = data.formData
        showErrorRecovery.value = true
        return true
      } else {
        localStorage.removeItem('pendingAnalysis')
      }
    }
  } catch (e) {
    console.error('检查待处理状态失败:', e)
  }
  return false
}

// 处理继续分析
const handleContinueAnalysis = async () => {
  showErrorRecovery.value = false
  
  if (pendingFormData.value) {
    // 跳转到 loading 页面并重新生成报告
    goToLoading()
    reportGenerationStatus.value = 'generating'
    
    try {
      const response = await analyzeBazi(pendingFormData.value)
      
      if (!response.success) {
        showToast(response.error || '分析失败', 'error')
        currentPage.value = 'form'
        return
      }
      
      result.value = response.data
      reportGenerationStatus.value = 'completed'
      currentPage.value = 'result'
      showToast('分析完成')
      
      // 清除待处理状态
      localStorage.removeItem('pendingAnalysis')
      
    } catch (error) {
      console.error('分析错误:', error)
      showToast('网络错误，请稍后重试', 'error')
      currentPage.value = 'form'
    }
  }
}

// 处理取消恢复
const handleCancelRecovery = () => {
  showErrorRecovery.value = false
  // 清除待处理状态
  localStorage.removeItem('pendingAnalysis')
  savedFormData.value = null
  pendingFormData.value = null
  showToast('已取消上次分析')
}

// 处理答题完成
const handleQuizComplete = (answers) => {
  quizAnswers.value = answers
  
  // 根据报告生成状态决定跳转到哪里
  if (reportGenerationStatus.value === 'completed' && result.value) {
    // 报告已生成，直接跳转结果页
    currentPage.value = 'result'
  } else {
    // 报告未生成或出错，跳转到 loading 页等待
    goToLoading()
  }
}

// 处理报告重试
const handleReportRetry = async () => {
  if (!pendingFormData.value) {
    showToast('无法获取表单数据，请重新填写', 'error')
    currentPage.value = 'form'
    return
  }
  
  showToast('正在重新分析...', 'info')
  reportGenerationStatus.value = 'generating'
  
  try {
    const response = await analyzeBazi(pendingFormData.value)
    
    if (!response.success) {
      console.error('报告重试失败:', response.error)
      showToast(response.error || '分析失败，请稍后重试', 'error')
      reportGenerationStatus.value = 'error'
      return
    }
    
    result.value = response.data
    reportGenerationStatus.value = 'completed'
    showToast('分析完成')
    
    // 清除待处理状态
    localStorage.removeItem('pendingAnalysis')
    saveState()
    
  } catch (error) {
    console.error('报告重试错误:', error)
    showToast('网络错误，请检查网络后重试', 'error')
    reportGenerationStatus.value = 'error'
  }
}

// 监听报告生成状态，如果在 loading 页面且报告完成，自动跳转
import { watch } from 'vue'
watch(() => reportGenerationStatus.value, (newStatus) => {
  if (newStatus === 'completed' && currentPage.value === 'loading' && result.value) {
    // 延迟一点点让用户看到完成状态
    setTimeout(() => {
      currentPage.value = 'result'
    }, 500)
  }
})

// 重置表单
const handleReset = () => {
  result.value = null
  aiAnalyzing.value = false
  quizAnswers.value = []
  reportGenerationStatus.value = 'idle'
  savedFormData.value = null
  pendingFormData.value = null
  localStorage.removeItem('pendingAnalysis')
  showErrorRecovery.value = false
  clearState()
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

// 检测是否为移动设备
const isMobileDevice = () => {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera
  return /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent.toLowerCase())
}

// 检测是否为 iOS 设备
const isIOSDevice = () => {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera
  return /iphone|ipad|ipod/i.test(userAgent.toLowerCase())
}

// 检测是否为鸿蒙系统
const isHarmonyOS = () => {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera
  // 鸿蒙3.0以下版本仍显示Android，需要额外检测
  const isHarmony = /harmony|harmonyos|openharmony/i.test(userAgent.toLowerCase())
  const isMaybeHarmony = /android.*hmscore|android.*harmony/i.test(userAgent.toLowerCase())
  return isHarmony || isMaybeHarmony
}

// 检测是否为微信环境
const isWechat = () => {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera
  return /micromessenger/i.test(userAgent.toLowerCase())
}

// 检测是否为QQ环境
const isQQ = () => {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera
  return /qq|qzone/i.test(userAgent.toLowerCase())
}

// 检测是否为QQ浏览器
const isQQBrowser = () => {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera
  return /mqqbrowser|qqbrowser/i.test(userAgent.toLowerCase())
}

// 下载报告
const handleDownload = async () => {
  if (!result.value?.report_id) {
    showToast('报告ID不存在', 'error')
    return
  }
  
  downloading.value = true
  
  try {
    const response = await downloadReport(result.value.report_id)
    
    if (response.success && response.download_url) {
      if (response.download_url.startsWith('data:')) {
        const link = document.createElement('a')
        link.href = response.download_url
        link.download = `天赋分析报告_${result.value.user_info?.name || '匿名'}.pdf`
        link.click()
        showToast('下载开始')
      } else if (response.download_url.startsWith('html://')) {
        await generatePDF()
      }
    } else {
      await generatePDF()
    }
  } catch (error) {
    console.error('下载错误:', error)
    await generatePDF()
  } finally {
    downloading.value = false
  }
}

// 处理导出PDF（从ReportPage接收）
const handleExportPdf = async ({ type, content, userName }) => {
  if (!content) {
    showToast('暂无内容可导出', 'error')
    return
  }
  await generatePDF(content, userName || result.value?.user_info?.name || '探索者')
}

// 前端生成 PDF（可指定内容）
const generatePDF = async (customContent, customName) => {
  try {
    const aiReport = customContent || result.value?.ai_report
    if (!aiReport) {
      showToast('AI报告尚未生成', 'error')
      return
    }
    
    showToast('正在生成 PDF...')
    
    const userName = customName || result.value.user_info?.name || '匿名'
    const gender = result.value.user_info?.gender || '未知'
    const isMobile = isMobileDevice()
    const isIOS = isIOSDevice()
    
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

    const canvas = await html2canvas(container, {
      scale: isMobile ? 1.5 : 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff',
      imageTimeout: 0,
      removeContainer: true
    })

    document.body.removeChild(container)

    const pdf = new jsPDF('p', 'mm', 'a4')
    
    const jpegQuality = isMobile ? 0.88 : 0.92
    const imgData = canvas.toDataURL('image/jpeg', jpegQuality)
    const imgWidth = 210
    const pageHeight = 297
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    
    let heightLeft = imgHeight
    let position = 0
    
    pdf.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight, undefined, 'MEDIUM')
    heightLeft -= pageHeight
    
    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight, undefined, 'MEDIUM')
      heightLeft -= pageHeight
    }
    
    const fileName = `${userName}天赋分析报告.pdf`
    const pdfBlob = pdf.output('blob')
    const pdfUrl = URL.createObjectURL(pdfBlob)
    
    // 平台检测
    const wechat = isWechat()
    const qq = isQQ()
    const qqBrowser = isQQBrowser()
    const harmony = isHarmonyOS()
    
    try {
      // 微信/QQ内置浏览器：使用新窗口打开预览
      if (wechat || qq) {
        // 尝试使用微信/QQ的分享预览功能
        const previewWindow = window.open('', '_blank')
        if (previewWindow) {
          previewWindow.document.write(`
            <html>
              <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>报告预览</title>
                <style>
                  body { 
                    margin: 0; 
                    padding: 20px; 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: #f5f5f5;
                  }
                  .container { 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                  }
                  .header { text-align: center; margin-bottom: 30px; }
                  .header h1 { color: #333; margin: 0 0 10px; }
                  .header p { color: #666; margin: 0; }
                  .content { line-height: 1.8; color: #333; }
                  .download-tip { 
                    margin-top: 30px; 
                    padding: 15px; 
                    background: #e3f2fd; 
                    border-radius: 8px;
                    text-align: center;
                    color: #1976d2;
                  }
                  @media print {
                    body { background: white; }
                    .download-tip { display: none; }
                  }
                </style>
              </head>
              <body>
                <div class="container">
                  <div class="header">
                    <h1>${userName}天赋分析报告</h1>
                    <p>性别：${gender}</p>
                  </div>
                  <div class="content">${container.innerHTML}</div>
                  <div class="download-tip">
                    <p>👆 点击右上角菜单，选择「在浏览器打开」后可下载PDF</p>
                  </div>
                </div>
              </body>
            </html>
          `)
          previewWindow.document.close()
          showToast('报告预览已打开')
        } else {
          showToast('请在浏览器中打开以下载报告', 'info')
        }
        return
      }
      
      // iOS设备（Safari/Chrome）
      if (isIOS) {
        // iOS Safari需要使用特殊的下载方式
        const reader = new FileReader()
        reader.onload = function(e) {
          const link = document.createElement('a')
          link.href = e.target.result
          link.download = fileName
          link.style.display = 'none'
          document.body.appendChild(link)
          link.click()
          setTimeout(() => {
            document.body.removeChild(link)
          }, 100)
        }
        reader.readAsDataURL(pdfBlob)
        showToast('PDF 已生成，请查看下载')
        return
      }
      
      // 鸿蒙系统
      if (harmony) {
        // 鸿蒙系统使用标准下载方式
        const link = document.createElement('a')
        link.href = pdfUrl
        link.download = fileName
        link.target = '_blank'
        document.body.appendChild(link)
        link.click()
        setTimeout(() => {
          document.body.removeChild(link)
          URL.revokeObjectURL(pdfUrl)
        }, 100)
        showToast('PDF 已生成')
        return
      }
      
      // Android/其他移动设备
      if (isMobile) {
        // QQ浏览器使用特殊处理
        if (qqBrowser) {
          const link = document.createElement('a')
          link.href = pdfUrl
          link.download = fileName
          link.target = '_blank'
          document.body.appendChild(link)
          link.click()
          setTimeout(() => {
            document.body.removeChild(link)
            URL.revokeObjectURL(pdfUrl)
          }, 100)
        } else {
          // 其他浏览器标准下载
          const link = document.createElement('a')
          link.href = pdfUrl
          link.download = fileName
          document.body.appendChild(link)
          link.click()
          setTimeout(() => {
            document.body.removeChild(link)
            URL.revokeObjectURL(pdfUrl)
          }, 100)
        }
        showToast('PDF 已生成')
        return
      }
      
      // 桌面浏览器
      pdf.save(fileName)
      showToast('PDF 已生成')
      
    } catch (downloadError) {
      console.error('PDF下载错误:', downloadError)
      // 降级方案：直接在新窗口打开
      window.open(pdfUrl, '_blank')
      showToast('请在新窗口中保存报告', 'info')
    }
  } catch (error) {
    console.error('PDF生成错误:', error)
    showToast('PDF生成失败，请重试', 'error')
  }
}

// 页面加载时：优先恢复 sessionStorage 状态，否则检查 pendingAnalysis
onMounted(() => {
  const restored = restoreState()
  if (!restored) {
    checkPendingAnalysis()
  }
})
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
  -webkit-text-size-adjust: 100%;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f8fafc;
  color: #1e293b;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* 适配刘海屏 */
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}

.app {
  min-height: 100vh;
  min-height: 100dvh;
}

/* Toast 提示 */
.toast {
  position: fixed;
  top: max(20px, env(safe-area-inset-top));
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

/* 错误恢复提示 */
.error-recovery-toast {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  border-radius: 16px;
  padding: 16px 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  z-index: 1001;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid #E2E8F0;
  animation: slideUp 0.4s ease;
  max-width: 90vw;
  width: auto;
}

.error-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.error-content svg {
  width: 24px;
  height: 24px;
  color: #F59E0B;
  flex-shrink: 0;
}

.error-text {
  text-align: left;
}

.error-text p {
  font-size: 15px;
  font-weight: 600;
  color: #4A5568;
  margin: 0 0 4px;
}

.error-text span {
  font-size: 13px;
  color: #718096;
}

.error-actions {
  display: flex;
  gap: 12px;
}

.cancel-btn {
  padding: 10px 20px;
  background: #F1F5F9;
  color: #64748B;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  background: #E2E8F0;
  color: #475569;
}

.continue-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.continue-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(142, 197, 252, 0.4);
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

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
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

/* 响应式 - 移动端优化 */
@media (max-width: 640px) {
  html {
    font-size: 15px;
  }
  
  .toast {
    padding: 10px 20px;
    font-size: 13px;
  }
  
  .error-recovery-toast {
    flex-direction: column;
    gap: 12px;
    padding: 16px;
  }
  
  .error-actions {
    width: 100%;
    flex-direction: column;
  }
  
  .cancel-btn,
  .continue-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  html {
    font-size: 14px;
  }
}
</style>
