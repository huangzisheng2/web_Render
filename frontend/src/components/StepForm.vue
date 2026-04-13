<template>
  <div class="step-form-page">
    <!-- 顶部导航 -->
    <div class="form-header">
      <button v-if="currentStep > 0" class="back-btn" @click="prevStep">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="form-title">填写出生信息</h1>
      <div class="step-indicator">
        <span class="current">{{ currentStep + 1 }}</span>
        <span class="total">/ {{ totalSteps }}</span>
      </div>
    </div>
    
    <!-- 进度条 -->
    <div class="progress-bar">
      <div class="progress-fill" :style="{ width: ((currentStep + 1) / totalSteps) * 100 + '%' }"></div>
    </div>
    
    <!-- 表单内容 -->
    <div class="form-content">
      <!-- 步骤1: 姓名 -->
      <transition name="slide" mode="out-in">
        <div v-if="currentStep === 0" class="step-content" key="step0">
          <div class="step-icon">👋</div>
          <h2 class="step-title">你好，请告诉我你的名字</h2>
          <p class="step-desc">这将出现在你的专属报告中</p>
          
          <div class="input-wrapper">
            <input
              v-model="form.name"
              type="text"
              class="name-input"
              placeholder="请输入姓名"
              maxlength="10"
              @keyup.enter="nextStep"
            />
            <span class="input-hint">{{ form.name.length }}/10</span>
          </div>
        </div>
        
        <!-- 步骤2: 性别 -->
        <div v-else-if="currentStep === 1" class="step-content" key="step1">
          <div class="step-icon">⚥</div>
          <h2 class="step-title">你的性别是？</h2>
          <p class="step-desc">不同性别的命理分析有所不同</p>
          
          <div class="gender-options">
            <button
              class="gender-card"
              :class="{ active: form.gender === 'male' }"
              @click="selectGender('male')"
            >
              <span class="gender-emoji">👦</span>
              <span class="gender-label">男生</span>
            </button>
            <button
              class="gender-card"
              :class="{ active: form.gender === 'female' }"
              @click="selectGender('female')"
            >
              <span class="gender-emoji">👧</span>
              <span class="gender-label">女生</span>
            </button>
          </div>
        </div>
        
        <!-- 步骤3: 出生日期 -->
        <div v-else-if="currentStep === 2" class="step-content" key="step2">
          <div class="step-icon">📅</div>
          <h2 class="step-title">你的出生日期是？</h2>
          <p class="step-desc">请准确填写，这将影响分析结果</p>
          
          <!-- 快速输入 -->
          <div class="quick-input-section">
            <input
              v-model="quickInput"
              type="text"
              class="quick-input"
              placeholder="快速输入: 200001011200"
              @blur="parseQuickInput"
            />
            <button class="parse-btn" @click="parseQuickInput">解析</button>
          </div>
          <p class="quick-hint">支持格式: 年月日时分 或 年月日</p>
          
          <!-- 日期选择 -->
          <div class="datetime-picker" @click="showDatePicker = true">
            <div class="picker-display">
              <span v-if="!dateText" class="placeholder">点击选择日期</span>
              <span v-else>{{ dateText }}</span>
            </div>
            <svg class="picker-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          
          <!-- 时辰未知选项 -->
          <button 
            class="unknown-time-btn"
            :class="{ active: form.hour === null }"
            @click="setUnknownTime"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            时辰未知
          </button>
        </div>
        
        <!-- 步骤4: 出生地点 -->
        <div v-else-if="currentStep === 3" class="step-content" key="step3">
          <div class="step-icon">📍</div>
          <h2 class="step-title">你的出生地点是？</h2>
          <p class="step-desc">用于计算真太阳时，让结果更准确</p>
          
          <!-- 省份选择 -->
          <div class="location-section">
            <div class="location-label">省份</div>
            <div class="location-picker" @click="showProvincePicker = true">
              <span :class="{ placeholder: !form.province }">
                {{ form.province || '选择省份' }}
              </span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </div>
          </div>
          
          <!-- 城市选择 -->
          <div class="location-section" v-if="form.province">
            <div class="location-label">城市</div>
            <div class="location-picker" @click="showCityPicker = true">
              <span :class="{ placeholder: !form.city }">
                {{ form.city || '选择城市' }}
              </span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </div>
          </div>
          
          <!-- 跳过选项 -->
          <button class="skip-btn" @click="skipLocation">
            暂不选择，使用标准时间
          </button>
        </div>
        
        <!-- 步骤5: 确认 -->
        <div v-else-if="currentStep === 4" class="step-content" key="step4">
          <div class="step-icon">✅</div>
          <h2 class="step-title">确认信息</h2>
          <p class="step-desc">请检查以下信息是否正确</p>
          
          <div class="info-summary">
            <div class="info-item">
              <span class="info-label">姓名</span>
              <span class="info-value">{{ form.name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">性别</span>
              <span class="info-value">{{ form.gender === 'male' ? '男' : '女' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">出生日期</span>
              <span class="info-value">{{ dateText || '未选择' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">出生地点</span>
              <span class="info-value">{{ locationText || '未选择' }}</span>
            </div>
          </div>
        </div>
      </transition>
    </div>
    
    <!-- 底部按钮 -->
    <div class="form-footer">
      <button 
        class="next-btn"
        :disabled="!canProceed"
        @click="currentStep === totalSteps - 1 ? submit() : nextStep()"
      >
        {{ currentStep === totalSteps - 1 ? '开始分析' : '下一步' }}
        <svg v-if="currentStep < totalSteps - 1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
      </button>
    </div>
    
    <!-- 日期选择弹窗 -->
    <Transition name="modal">
      <div v-if="showDatePicker" class="modal-overlay" @click.self="showDatePicker = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>选择出生日期</h3>
            <button class="modal-close" @click="showDatePicker = false">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          <div class="picker-body">
            <div class="picker-columns">
              <div class="picker-column">
                <div class="column-label">年</div>
                <div class="column-options">
                  <div 
                    v-for="year in yearOptions" 
                    :key="year"
                    class="column-option"
                    :class="{ active: tempDate.year === year }"
                    @click="tempDate.year = year"
                  >
                    {{ year }}
                  </div>
                </div>
              </div>
              <div class="picker-column">
                <div class="column-label">月</div>
                <div class="column-options">
                  <div 
                    v-for="month in 12" 
                    :key="month"
                    class="column-option"
                    :class="{ active: tempDate.month === month }"
                    @click="tempDate.month = month"
                  >
                    {{ month }}
                  </div>
                </div>
              </div>
              <div class="picker-column">
                <div class="column-label">日</div>
                <div class="column-options">
                  <div 
                    v-for="day in daysInMonth" 
                    :key="day"
                    class="column-option"
                    :class="{ active: tempDate.day === day }"
                    @click="tempDate.day = day"
                  >
                    {{ day }}
                  </div>
                </div>
              </div>
              <div class="picker-column">
                <div class="column-label">时</div>
                <div class="column-options">
                  <div 
                    v-for="(shichen, idx) in shichenList" 
                    :key="idx"
                    class="column-option"
                    :class="{ active: tempDate.hour === shichen.hour }"
                    @click="tempDate.hour = shichen.hour"
                  >
                    {{ shichen.name }}
                  </div>
                </div>
              </div>
            </div>
            <div class="minute-input">
              <label>分钟（可选）</label>
              <input 
                v-model.number="tempDate.minute"
                type="number"
                min="0"
                max="59"
                placeholder="0-59"
              />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-unknown" @click="selectUnknownTime">时辰未知</button>
            <button class="btn-confirm" @click="confirmDate">确定</button>
          </div>
        </div>
      </div>
    </Transition>
    
    <!-- 省份选择弹窗 -->
    <Transition name="modal">
      <div v-if="showProvincePicker" class="modal-overlay" @click.self="showProvincePicker = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>选择省份</h3>
            <button class="modal-close" @click="showProvincePicker = false">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          <div class="picker-body list-picker">
            <div 
              v-for="province in provinceList" 
              :key="province"
              class="list-option"
              :class="{ active: form.province === province }"
              @click="selectProvince(province)"
            >
              {{ province }}
            </div>
          </div>
        </div>
      </div>
    </Transition>
    
    <!-- 城市选择弹窗 -->
    <Transition name="modal">
      <div v-if="showCityPicker" class="modal-overlay" @click.self="showCityPicker = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>选择城市</h3>
            <button class="modal-close" @click="showCityPicker = false">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          <div class="picker-body list-picker">
            <div 
              v-for="city in cityList" 
              :key="city"
              class="list-option"
              :class="{ active: form.city === city }"
              @click="selectCity(city)"
            >
              {{ city }}
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { cityData } from '../data/cities'

const emit = defineEmits(['submit'])

// 表单数据
const form = ref({
  name: '',
  gender: 'male',
  year: 2000,
  month: 1,
  day: 1,
  hour: 12,
  minute: 0,
  province: '',
  city: ''
})

// 步骤控制
const currentStep = ref(0)
const totalSteps = 5

// 弹窗控制
const showDatePicker = ref(false)
const showProvincePicker = ref(false)
const showCityPicker = ref(false)

// 临时数据
const tempDate = reactive({
  year: 2000,
  month: 1,
  day: 1,
  hour: 12,
  minute: 0
})

const quickInput = ref('')

// 计算属性
const yearOptions = Array.from({ length: 125 }, (_, i) => 2025 - i)

const daysInMonth = computed(() => {
  return new Date(tempDate.year, tempDate.month, 0).getDate()
})

const dateText = computed(() => {
  if (form.value.hour === null) {
    return `${form.value.year}年${form.value.month}月${form.value.day}日（时辰未知）`
  }
  const shichen = shichenList.find(s => s.hour === form.value.hour)
  const timeStr = shichen ? `${shichen.name}(${shichen.time})` : `${form.value.hour}时`
  return `${form.value.year}年${form.value.month}月${form.value.day}日 ${timeStr}`
})

const locationText = computed(() => {
  if (form.value.province && form.value.city) {
    return `${form.value.province} ${form.value.city}`
  }
  return ''
})

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 0: return form.value.name.trim().length > 0
    case 1: return !!form.value.gender
    case 2: return true // 日期有默认值
    case 3: return true // 地点可选
    case 4: return true
    default: return false
  }
})

const provinceList = computed(() => Object.keys(cityData))

const cityList = computed(() => {
  return form.value.province ? cityData[form.value.province] || [] : []
})

// 时辰列表
const shichenList = [
  { name: '子时', time: '23:00-01:00', hour: 0 },
  { name: '丑时', time: '01:00-03:00', hour: 1 },
  { name: '寅时', time: '03:00-05:00', hour: 3 },
  { name: '卯时', time: '05:00-07:00', hour: 5 },
  { name: '辰时', time: '07:00-09:00', hour: 7 },
  { name: '巳时', time: '09:00-11:00', hour: 9 },
  { name: '午时', time: '11:00-13:00', hour: 11 },
  { name: '未时', time: '13:00-15:00', hour: 13 },
  { name: '申时', time: '15:00-17:00', hour: 15 },
  { name: '酉时', time: '17:00-19:00', hour: 17 },
  { name: '戌时', time: '19:00-21:00', hour: 19 },
  { name: '亥时', time: '21:00-23:00', hour: 21 }
]

// 方法
const nextStep = () => {
  if (currentStep.value < totalSteps - 1) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const selectGender = (gender) => {
  form.value.gender = gender
  nextStep()
}

const setUnknownTime = () => {
  form.value.hour = null
  form.value.minute = 0
}

const selectUnknownTime = () => {
  tempDate.hour = null
  confirmDate()
}

const confirmDate = () => {
  form.value.year = tempDate.year
  form.value.month = tempDate.month
  form.value.day = tempDate.day
  form.value.hour = tempDate.hour
  form.value.minute = tempDate.minute
  showDatePicker.value = false
}

const selectProvince = (province) => {
  form.value.province = province
  form.value.city = ''
  showProvincePicker.value = false
  showCityPicker.value = true
}

const selectCity = (city) => {
  form.value.city = city
  showCityPicker.value = false
}

const skipLocation = () => {
  form.value.province = ''
  form.value.city = ''
  nextStep()
}

const parseQuickInput = () => {
  const input = quickInput.value.trim()
  if (!input) return

  const digits = input.replace(/\D/g, '')

  if (digits.length === 8) {
    form.value.year = parseInt(digits.substring(0, 4))
    form.value.month = parseInt(digits.substring(4, 6))
    form.value.day = parseInt(digits.substring(6, 8))
    form.value.hour = 12
    form.value.minute = 0
    quickInput.value = ''
  } else if (digits.length >= 10) {
    form.value.year = parseInt(digits.substring(0, 4))
    form.value.month = parseInt(digits.substring(4, 6))
    form.value.day = parseInt(digits.substring(6, 8))
    form.value.hour = parseInt(digits.substring(8, 10))
    form.value.minute = digits.length >= 12 ? parseInt(digits.substring(10, 12)) : 0
    quickInput.value = ''
  }
}

const submit = () => {
  emit('submit', { ...form.value })
}
</script>

<style scoped>
.step-form-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #e8f4f8 0%, #f5f0e8 100%);
  display: flex;
  flex-direction: column;
}

/* 头部 */
.form-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.back-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: #f5f5f5;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-btn svg {
  width: 20px;
  height: 20px;
  color: #666;
}

.form-title {
  font-size: 17px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.step-indicator {
  font-size: 14px;
  color: #95a5a6;
}

.step-indicator .current {
  color: #7dd3c0;
  font-weight: 600;
}

/* 进度条 */
.progress-bar {
  height: 3px;
  background: #e0e0e0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #7dd3c0 0%, #5fb3a3 100%);
  transition: width 0.3s ease;
}

/* 表单内容 */
.form-content {
  flex: 1;
  padding: 32px 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-width: 400px;
  margin: 0 auto;
  width: 100%;
}

.step-content {
  text-align: center;
}

.step-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.step-title {
  font-size: 22px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px;
}

.step-desc {
  font-size: 14px;
  color: #95a5a6;
  margin: 0 0 32px;
}

/* 姓名输入 */
.input-wrapper {
  position: relative;
}

.name-input {
  width: 100%;
  padding: 18px 20px;
  font-size: 18px;
  border: 2px solid #e0e0e0;
  border-radius: 16px;
  text-align: center;
  transition: all 0.3s ease;
}

.name-input:focus {
  outline: none;
  border-color: #7dd3c0;
}

.input-hint {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  color: #95a5a6;
}

/* 性别选择 */
.gender-options {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.gender-card {
  flex: 1;
  max-width: 140px;
  padding: 32px 20px;
  background: white;
  border: 2px solid transparent;
  border-radius: 20px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.gender-card:hover {
  border-color: #7dd3c0;
}

.gender-card.active {
  border-color: #7dd3c0;
  background: linear-gradient(135deg, #e8f4f8 0%, #d4ede6 100%);
}

.gender-emoji {
  font-size: 48px;
}

.gender-label {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

/* 日期选择 */
.quick-input-section {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.quick-input {
  flex: 1;
  padding: 14px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 15px;
}

.parse-btn {
  padding: 14px 20px;
  background: #7dd3c0;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.quick-hint {
  font-size: 12px;
  color: #95a5a6;
  margin: 0 0 20px;
}

.datetime-picker {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 16px;
  cursor: pointer;
  margin-bottom: 12px;
}

.datetime-picker .placeholder {
  color: #95a5a6;
}

.picker-icon {
  width: 24px;
  height: 24px;
  color: #7dd3c0;
}

.unknown-time-btn {
  width: 100%;
  padding: 14px;
  background: transparent;
  border: 2px dashed #d0d0d0;
  border-radius: 12px;
  color: #95a5a6;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.unknown-time-btn svg {
  width: 18px;
  height: 18px;
}

.unknown-time-btn.active {
  border-color: #7dd3c0;
  color: #7dd3c0;
  background: #e8f4f8;
}

/* 地点选择 */
.location-section {
  margin-bottom: 16px;
}

.location-label {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 8px;
  text-align: left;
}

.location-picker {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 16px;
  cursor: pointer;
}

.location-picker .placeholder {
  color: #95a5a6;
}

.location-picker svg {
  width: 20px;
  height: 20px;
  color: #95a5a6;
}

.skip-btn {
  width: 100%;
  padding: 14px;
  background: transparent;
  border: none;
  color: #95a5a6;
  font-size: 14px;
  cursor: pointer;
  text-decoration: underline;
}

/* 信息确认 */
.info-summary {
  background: white;
  border-radius: 16px;
  padding: 20px;
  text-align: left;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 14px;
  color: #7f8c8d;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

/* 底部按钮 */
.form-footer {
  padding: 20px;
  background: white;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.next-btn {
  width: 100%;
  padding: 18px;
  background: linear-gradient(135deg, #7dd3c0 0%, #5fb3a3 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 16px rgba(125, 211, 192, 0.3);
  transition: all 0.3s ease;
}

.next-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(125, 211, 192, 0.4);
}

.next-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.next-btn svg {
  width: 20px;
  height: 20px;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-width: 400px;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f5f5f5;
  border-radius: 8px;
  cursor: pointer;
}

.modal-close svg {
  width: 18px;
  height: 18px;
}

.picker-body {
  padding: 16px;
  overflow-y: auto;
}

.picker-columns {
  display: flex;
  gap: 8px;
  height: 200px;
}

.picker-column {
  flex: 1;
  text-align: center;
}

.column-label {
  font-size: 13px;
  color: #95a5a6;
  margin-bottom: 8px;
}

.column-options {
  height: 170px;
  overflow-y: auto;
}

.column-option {
  padding: 10px;
  font-size: 15px;
  color: #2c3e50;
  cursor: pointer;
  border-radius: 8px;
}

.column-option.active {
  background: #7dd3c0;
  color: white;
}

.minute-input {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.minute-input label {
  display: block;
  font-size: 13px;
  color: #95a5a6;
  margin-bottom: 8px;
}

.minute-input input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  text-align: center;
  font-size: 16px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
}

.btn-unknown,
.btn-confirm {
  flex: 1;
  padding: 14px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

.btn-unknown {
  background: #f5f5f5;
  color: #666;
}

.btn-confirm {
  background: #7dd3c0;
  color: white;
}

/* 列表选择器 */
.list-picker {
  max-height: 300px;
}

.list-option {
  padding: 16px 20px;
  font-size: 15px;
  color: #2c3e50;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
}

.list-option:last-child {
  border-bottom: none;
}

.list-option.active {
  color: #7dd3c0;
  font-weight: 600;
  background: #e8f4f8;
}

/* 过渡动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>