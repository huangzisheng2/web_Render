import { createApp } from 'vue'
import App from './App.vue'
import './styles/index.css'

// 检测调试模式
const urlParams = new URLSearchParams(window.location.search)
const isDebugMode = urlParams.get('debug') === 'true'

// 将调试模式状态附加到全局属性
const app = createApp(App)
app.config.globalProperties.$isDebug = isDebugMode

// 同时导出供其他模块使用
export { isDebugMode }

app.mount('#app')