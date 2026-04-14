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

<script setup>
import { ref, reactive, getCurrentInstance } from 'vue'
import LandingPage from './components/LandingPage.vue'
import QuizPage from './components/QuizPage.vue'
import StepForm from './components/StepForm.vue'
import LoadingPage from './components/LoadingPage.vue'
import ResultDisplay from './components/ResultDisplay.vue'
import { analyzeBazi, analyzeAI, downloadReport } from './api/bazi'

// 检测调试模式
const { appContext } = getCurrentInstance()
const isDebug = appContext.config.globalProperties.$isDebug || false

// 页面路由状态
const currentPage = ref('landing') // landing, quiz, form, loading, result

const downloading = ref(false)
const aiAnalyzing = ref(false)
const result = ref(null)
const quizAnswers = ref([])

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

// 执行分析
const handleAnalyze = async (formData) => {
  goToLoading()
  
  try {
    // 调用 /api/analyze
    // 用户模式：后端自动执行 Step 4 + Step 5，返回包含 ai_report 的完整结果
    // 调试模式：后端只执行 Step 4，返回基础数据
    const response = await analyzeBazi(formData)
    
    if (!response.success) {
      showToast(response.error || '分析失败', 'error')
      currentPage.value = 'form'
      return
    }
    
    result.value = response.data
    
    // 显示结果页
    currentPage.value = 'result'
    showToast('分析完成')
    
  } catch (error) {
    console.error('分析错误:', error)
    showToast('网络错误，请稍后重试', 'error')
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

// 前端生成 PDF（优化版 - 减小文件大小）
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
    
    // 使用html2canvas渲染为图片（平衡清晰度与文件大小）
    const html2canvas = await import('html2canvas')
    const canvas = await html2canvas.default(container, {
      scale: 2,  // 提高分辨率保证清晰度
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff',
      imageTimeout: 0,
      removeContainer: true
    })
    
    document.body.removeChild(container)
    
    // 创建PDF
    const { jsPDF } = await import('jspdf')
    const pdf = new jsPDF('p', 'mm', 'a4')
    
    // 使用 JPEG 格式，质量 0.92（清晰度优先，控制在10MB以下）
    const imgData = canvas.toDataURL('image/jpeg', 0.92)
    const imgWidth = 210
    const pageHeight = 297
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    
    let heightLeft = imgHeight
    let position = 0
    
    // 添加图片（使用 MEDIUM 压缩平衡质量与大小）
    pdf.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight, undefined, 'MEDIUM')
    heightLeft -= pageHeight
    
    // 处理多页
    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight, undefined, 'MEDIUM')
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