<template>
  <div class="app">
    <!-- 顶部导航 -->
    <header class="app-header">
      <div class="header-content">
        <div class="logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 6v6l4 2"/>
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
          </svg>
          <span class="logo-text">天赋命理</span>
        </div>
        <p class="header-subtitle">八字格局 · 性格分析 · 天赋发掘</p>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 输入表单 -->
      <Transition name="fade" mode="out-in">
        <div v-if="!result" class="form-wrapper" key="form">
          <div class="form-intro">
            <h1 class="intro-title">探索您的天赋与性格</h1>
            <p class="intro-desc">
              基于传统八字命理，结合 AI 智能分析<br>
              揭示您的性格特质、天赋优势与发展方向
            </p>
          </div>
          <BaziForm 
            @submit="handleAnalyze"
            :loading="loading"
          />
        </div>
        
        <!-- 结果展示 -->
        <ResultDisplay
          v-else
          key="result"
          :result="result"
          :ai-analyzing="aiAnalyzing"
          @reset="handleReset"
          @download="handleDownload"
          @analyze-ai="handleAIAnalyze"
          :downloading="downloading"
        />
      </Transition>
    </main>

    <!-- 底部信息 -->
    <footer class="app-footer">
      <p class="footer-text">基于《渊海子平》《三命通会》等经典命理著作</p>
      <p class="footer-copyright">© 2026 天赋命理分析系统</p>
    </footer>

    <!-- Toast 提示 -->
    <div v-if="toast.show" class="toast" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import BaziForm from './components/BaziForm.vue'
import ResultDisplay from './components/ResultDisplay.vue'
import { analyzeBazi, analyzeAI, downloadReport } from './api/bazi'

const loading = ref(false)
const downloading = ref(false)
const aiAnalyzing = ref(false)
const result = ref(null)

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
  loading.value = true
  
  try {
    const response = await analyzeBazi(formData)
    
    if (response.success) {
      result.value = response.data
      showToast('分析完成')
      // 滚动到顶部
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } else {
      showToast(response.error || '分析失败', 'error')
    }
  } catch (error) {
    console.error('分析错误:', error)
    showToast('网络错误，请稍后重试', 'error')
  } finally {
    loading.value = false
  }
}

// 重置表单
const handleReset = () => {
  result.value = null
  aiAnalyzing.value = false
  window.scrollTo({ top: 0, behavior: 'smooth' })
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
    const { jsPDF } = await import('jspdf')
    
    // 只获取AI报告内容
    const aiReport = result.value?.ai_report
    if (!aiReport) {
      showToast('AI报告尚未生成', 'error')
      return
    }
    
    showToast('正在生成 PDF...')
    
    const pdf = new jsPDF('p', 'mm', 'a4')
    const userName = result.value.user_info?.name || '匿名'
    
    // 设置中文字体（使用内置的helvetica，中文会显示为乱码，需要特殊处理）
    pdf.setFont('helvetica')
    
    // 标题
    pdf.setFontSize(20)
    pdf.text('八字天赋与性格分析报告', 105, 20, { align: 'center' })
    
    // 分隔线
    pdf.setDrawColor(102, 126, 234)
    pdf.line(20, 25, 190, 25)
    
    // 用户信息
    pdf.setFontSize(12)
    pdf.text(`姓名：${userName}`, 20, 35)
    pdf.text(`性别：${result.value.user_info?.gender || '未知'}`, 20, 42)
    
    // AI报告标题
    pdf.setFontSize(14)
    pdf.setTextColor(102, 126, 234)
    pdf.text('【AI 分析报告】', 20, 55)
    pdf.setTextColor(0, 0, 0)
    pdf.setFontSize(11)
    
    // 处理AI报告文本（简单处理Markdown）
    let content = aiReport
      .replace(/### /g, '')
      .replace(/## /g, '')
      .replace(/# /g, '')
      .replace(/\*\*/g, '')
      .replace(/\*/g, '  * ')
    
    // 分页添加文本
    const lines = pdf.splitTextToSize(content, 170)
    let y = 65
    
    for (let i = 0; i < lines.length; i++) {
      if (y > 280) {
        pdf.addPage()
        y = 20
      }
      pdf.text(lines[i], 20, y)
      y += 6
    }
    
    // 页脚
    const now = new Date().toLocaleString('zh-CN')
    pdf.setFontSize(9)
    pdf.setTextColor(128, 128, 128)
    pdf.text('本报告由 AI 生成，仅供参考', 105, 290, { align: 'center' })
    pdf.text(`生成时间：${now}`, 105, 295, { align: 'center' })
    
    pdf.save(`八字分析报告_${userName}.pdf`)
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
  display: flex;
  flex-direction: column;
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