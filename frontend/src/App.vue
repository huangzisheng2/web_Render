<template>
  <div class="app">
    <NavBar 
      title="天赋性格测评系统" 
      fixed
    />
    
    <div class="content">
      <!-- 输入表单 -->
      <BaziForm 
        v-if="!result" 
        @submit="handleAnalyze"
        :loading="loading"
      />
      
      <!-- 结果展示 -->
      <ResultDisplay
        v-else
        :result="result"
        @reset="handleReset"
        @download="handleDownload"
        :downloading="downloading"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Toast } from 'vant'
import BaziForm from './components/BaziForm.vue'
import ResultDisplay from './components/ResultDisplay.vue'
import { analyzeBazi, downloadReport } from './api/bazi'

const loading = ref(false)
const downloading = ref(false)
const result = ref(null)

// 执行分析
const handleAnalyze = async (formData) => {
  loading.value = true
  
  try {
    const response = await analyzeBazi(formData)
    
    if (response.success) {
      result.value = response.data
      Toast.success('分析完成')
    } else {
      Toast.fail(response.error || '分析失败')
    }
  } catch (error) {
    console.error('分析错误:', error)
    Toast.fail('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 重置表单
const handleReset = () => {
  result.value = null
}

// 下载报告
const handleDownload = async () => {
  if (!result.value?.report_id) {
    Toast.fail('报告ID不存在')
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
        Toast.success('下载开始')
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

// 前端生成 PDF（备用方案）
const generatePDF = async () => {
  try {
    const html2canvas = (await import('html2canvas')).default
    const { jsPDF } = await import('jspdf')
    
    const element = document.querySelector('.result-container')
    if (!element) {
      Toast.fail('找不到报告内容')
      return
    }
    
    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
      logging: false
    })
    
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    
    const imgWidth = 210
    const pageHeight = 297
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    let heightLeft = imgHeight
    let position = 0
    
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight
    
    while (heightLeft >= 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
    }
    
    pdf.save(`八字分析报告_${result.value.user_info?.name || '匿名'}.pdf`)
    Toast.success('PDF已生成')
  } catch (error) {
    console.error('PDF生成错误:', error)
    Toast.fail('PDF生成失败')
  }
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: #f5f5f5;
}

.content {
  padding-top: 46px;
  padding-bottom: 20px;
}
</style>
