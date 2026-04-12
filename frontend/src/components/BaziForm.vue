<template>
  <div class="form-container">
    <form @submit.prevent="onSubmit" class="bazi-form">
      <!-- 姓名输入 -->
      <div class="form-group">
        <label class="form-label">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          您的姓名
        </label>
        <input 
          v-model="form.name"
          type="text"
          class="form-input"
          placeholder="请输入姓名"
          required
        />
      </div>

      <!-- 性别选择 -->
      <div class="form-group">
        <label class="form-label">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 16v-4M12 8h.01"/>
          </svg>
          性别
        </label>
        <div class="gender-selector">
          <label 
            class="gender-option"
            :class="{ active: form.gender === 'male' }"
          >
            <input 
              v-model="form.gender"
              type="radio"
              value="male"
              class="gender-input"
            />
            <span class="gender-icon">👨</span>
            <span class="gender-text">男</span>
          </label>
          <label 
            class="gender-option"
            :class="{ active: form.gender === 'female' }"
          >
            <input 
              v-model="form.gender"
              type="radio"
              value="female"
              class="gender-input"
            />
            <span class="gender-icon">👩</span>
            <span class="gender-text">女</span>
          </label>
        </div>
      </div>

      <!-- 快速文本输入 -->
      <div class="form-group">
        <label class="form-label">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          快速输入（可选）
        </label>
        <div class="quick-input-wrapper">
          <input
            v-model="quickInput"
            type="text"
            class="form-input quick-input"
            placeholder="如: 199806141600 (年月日时分)"
            @blur="parseQuickInput"
          />
          <button type="button" class="quick-parse-btn" @click="parseQuickInput">
            解析
          </button>
        </div>
        <p class="form-tip">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          支持格式: 200001011200(含时辰) 或 20000101(无时辰)
        </p>
      </div>

      <!-- 出生日期与时间 -->
      <div class="form-group">
        <label class="form-label">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          出生日期与时间
        </label>
        <div class="datetime-wrapper">
          <div class="date-picker-trigger" @click="showDatePicker = true">
            <span class="date-display" :class="{ placeholder: !dateText }">
              {{ dateText || '请选择日期' }}
            </span>
            <svg class="calendar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <div class="time-picker-trigger" @click="showTimePicker = true">
            <span class="time-display" :class="{ placeholder: !timeText }">
              {{ timeText || '时辰' }}
            </span>
            <svg class="clock-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
        </div>
        <div class="time-actions">
          <button type="button" class="time-action-btn unknown" @click="setUnknownTime">
            时辰未知
          </button>
        </div>
      </div>

      <!-- 出生地点 -->
      <div class="form-group">
        <label class="form-label">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
          出生地点
        </label>
        <div class="location-selectors">
          <div class="location-trigger" @click="showProvincePicker = true">
            <span :class="{ placeholder: !form.province }">
              {{ form.province || '选择省份' }}
            </span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </div>
          <div 
            class="location-trigger" 
            :class="{ disabled: !form.province }"
            @click="form.province && (showCityPicker = true)"
          >
            <span :class="{ placeholder: !form.city }">
              {{ form.city || '选择城市' }}
            </span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- 提交按钮 -->
      <button 
        type="submit" 
        class="submit-btn"
        :disabled="loading"
      >
        <span v-if="!loading" class="btn-content">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 16v-4M12 8h.01"/>
          </svg>
          开始分析
        </span>
        <span v-else class="btn-loading">
          <span class="loading-spinner"></span>
          分析中...
        </span>
      </button>
    </form>

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
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showDatePicker = false">取消</button>
            <button class="btn-confirm" @click="confirmDate">确定</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 时间选择弹窗 -->
    <Transition name="modal">
      <div v-if="showTimePicker" class="modal-overlay" @click.self="showTimePicker = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>选择出生时间</h3>
            <button class="modal-close" @click="showTimePicker = false">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          <div class="picker-body">
            <div class="time-presets">
              <button class="preset-btn unknown" @click="selectUnknownTime">
                时辰未知
              </button>
            </div>
            <div class="shichen-grid">
              <button 
                v-for="(shichen, index) in shichenList" 
                :key="index"
                class="shichen-btn"
                :class="{ active: tempTime.shichen === index }"
                @click="selectShichen(index)"
              >
                <span class="shichen-name">{{ shichen.name }}</span>
                <span class="shichen-time">{{ shichen.time }}</span>
              </button>
            </div>
            <div class="minute-input">
              <label>具体分钟（可选）</label>
              <input 
                v-model.number="tempTime.minute"
                type="number"
                min="0"
                max="59"
                placeholder="0-59"
              />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showTimePicker = false">取消</button>
            <button class="btn-confirm" @click="confirmTime">确定</button>
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
              <svg v-if="form.province === province" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
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
              <svg v-if="form.city === city" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
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

const props = defineProps({
  loading: Boolean
})

const emit = defineEmits(['submit'])

// 表单数据
const form = ref({
  name: '',
  gender: 'male',
  year: new Date().getFullYear() - 25,
  month: 1,
  day: 1,
  hour: null,
  minute: 0,
  province: '',
  city: ''
})

// 快速输入
const quickInput = ref('')

// 弹窗状态
const showDatePicker = ref(false)
const showTimePicker = ref(false)
const showProvincePicker = ref(false)
const showCityPicker = ref(false)

// 临时选择数据
const tempDate = reactive({
  year: form.value.year,
  month: form.value.month,
  day: form.value.day
})

const tempTime = reactive({
  shichen: 0,
  minute: 0
})

// 年份选项（1900-今年）
const currentYear = new Date().getFullYear()
const yearOptions = Array.from({ length: currentYear - 1899 }, (_, i) => currentYear - i)

// 月份天数
const daysInMonth = computed(() => {
  return new Date(tempDate.year, tempDate.month, 0).getDate()
})

// 日期显示
const dateText = computed(() => {
  return `${form.value.year}年${form.value.month}月${form.value.day}日`
})

// 时间显示
const timeText = computed(() => {
  if (form.value.hour === null) return '时辰未知'
  const shichen = shichenList.find(s => s.hour === form.value.hour)
  if (shichen) {
    return `${shichen.name} (${shichen.time})`
  }
  return `${form.value.hour.toString().padStart(2, '0')}:${form.value.minute.toString().padStart(2, '0')}`
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

// 省份列表
const provinceList = computed(() => Object.keys(cityData))

// 城市列表
const cityList = computed(() => {
  return form.value.province ? cityData[form.value.province] || [] : []
})

// 确认日期
const confirmDate = () => {
  form.value.year = tempDate.year
  form.value.month = tempDate.month
  form.value.day = tempDate.day
  showDatePicker.value = false
}

// 快速解析输入
const parseQuickInput = () => {
  const input = quickInput.value.trim()
  if (!input) return

  // 清理输入（只保留数字）
  const digits = input.replace(/\D/g, '')

  if (digits.length === 8) {
    // 格式: YYYYMMDD (无时辰)
    form.value.year = parseInt(digits.substring(0, 4))
    form.value.month = parseInt(digits.substring(4, 6))
    form.value.day = parseInt(digits.substring(6, 8))
    form.value.hour = null
    form.value.minute = 0
    // 更新临时日期
    tempDate.year = form.value.year
    tempDate.month = form.value.month
    tempDate.day = form.value.day
    // 清空快速输入框表示成功
    quickInput.value = ''
  } else if (digits.length === 10) {
    // 格式: YYYYMMDDHH (有时辰，无分钟)
    form.value.year = parseInt(digits.substring(0, 4))
    form.value.month = parseInt(digits.substring(4, 6))
    form.value.day = parseInt(digits.substring(6, 8))
    form.value.hour = parseInt(digits.substring(8, 10))
    form.value.minute = 0
    tempDate.year = form.value.year
    tempDate.month = form.value.month
    tempDate.day = form.value.day
    // 找到对应的时辰索引
    const shichenIndex = shichenList.findIndex(s => s.hour === form.value.hour)
    if (shichenIndex >= 0) {
      tempTime.shichen = shichenIndex
    }
    quickInput.value = ''
  } else if (digits.length === 12) {
    // 格式: YYYYMMDDHHmm (有时辰和分钟)
    form.value.year = parseInt(digits.substring(0, 4))
    form.value.month = parseInt(digits.substring(4, 6))
    form.value.day = parseInt(digits.substring(6, 8))
    form.value.hour = parseInt(digits.substring(8, 10))
    form.value.minute = parseInt(digits.substring(10, 12))
    tempDate.year = form.value.year
    tempDate.month = form.value.month
    tempDate.day = form.value.day
    const shichenIndex = shichenList.findIndex(s => s.hour === form.value.hour)
    if (shichenIndex >= 0) {
      tempTime.shichen = shichenIndex
    }
    tempTime.minute = form.value.minute
    quickInput.value = ''
  } else {
    alert('请输入正确格式: 19980614 或 1998061416 或 199806141600')
    return
  }
}

// 设置未知时间
const setUnknownTime = () => {
  form.value.hour = null
  form.value.minute = 0
}

// 选择时辰
const selectShichen = (index) => {
  tempTime.shichen = index
  tempTime.minute = 0
}

// 选择未知时间
const selectUnknownTime = () => {
  form.value.hour = null
  form.value.minute = 0
  showTimePicker.value = false
}

// 确认时间
const confirmTime = () => {
  const shichen = shichenList[tempTime.shichen]
  if (shichen) {
    form.value.hour = shichen.hour
    form.value.minute = tempTime.minute
  }
  showTimePicker.value = false
}

// 选择省份
const selectProvince = (province) => {
  form.value.province = province
  form.value.city = ''
  showProvincePicker.value = false
  showCityPicker.value = true
}

// 选择城市
const selectCity = (city) => {
  form.value.city = city
  showCityPicker.value = false
}

// 提交表单
const onSubmit = () => {
  // 如果没有选择城市，使用默认值
  if (!form.value.province || !form.value.city) {
    if (!form.value.province) form.value.province = '北京市'
    if (!form.value.city) form.value.city = '北京市'
  }
  
  emit('submit', { ...form.value })
}
</script>

<style scoped>
.form-container {
  background: white;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}

.bazi-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 表单组 */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.form-label svg {
  width: 18px;
  height: 18px;
  color: #667eea;
}

/* 输入框 */
.form-input {
  padding: 14px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 15px;
  transition: all 0.3s;
  background: #fafafa;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input::placeholder {
  color: #9ca3af;
}

/* 性别选择 */
.gender-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.gender-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 20px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
}

.gender-option:hover {
  border-color: #d1d5db;
}

.gender-option.active {
  border-color: #667eea;
  background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
}

.gender-input {
  display: none;
}

.gender-icon {
  font-size: 32px;
}

.gender-text {
  font-size: 15px;
  font-weight: 600;
  color: #374151;
}

/* 快速输入 */
.quick-input-wrapper {
  display: flex;
  gap: 8px;
}

.quick-input {
  flex: 1;
}

.quick-parse-btn {
  padding: 14px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.quick-parse-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

/* 日期时间组合 */
.datetime-wrapper {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 8px;
}

.date-picker-trigger,
.time-picker-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
}

.date-picker-trigger:hover,
.time-picker-trigger:hover {
  border-color: #d1d5db;
  background: white;
}

.date-display,
.time-display {
  font-size: 15px;
  color: #111827;
}

.date-display.placeholder,
.time-display.placeholder {
  color: #9ca3af;
}

.calendar-icon,
.clock-icon {
  width: 20px;
  height: 20px;
  color: #9ca3af;
  flex-shrink: 0;
}

.time-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.time-action-btn {
  flex: 1;
  padding: 10px;
  border: 2px dashed #d1d5db;
  border-radius: 10px;
  background: #f9fafb;
  color: #6b7280;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.time-action-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: #eef2ff;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.form-tip svg {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

/* 地点选择 */
.location-selectors {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.location-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
  font-size: 15px;
}

.location-trigger:hover:not(.disabled) {
  border-color: #d1d5db;
  background: white;
}

.location-trigger.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.location-trigger span.placeholder {
  color: #9ca3af;
}

.location-trigger svg {
  width: 16px;
  height: 16px;
  color: #9ca3af;
}

/* 提交按钮 */
.submit-btn {
  margin-top: 8px;
  padding: 16px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-content svg {
  width: 20px;
  height: 20px;
}

.btn-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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
  max-height: 80vh;
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
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: #111827;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f3f4f6;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #e5e7eb;
  color: #374151;
}

.modal-close svg {
  width: 18px;
  height: 18px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel,
.btn-confirm {
  flex: 1;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-confirm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-confirm:hover {
  opacity: 0.9;
}

/* 选择器主体 */
.picker-body {
  padding: 16px 20px;
  overflow-y: auto;
  max-height: 400px;
}

.picker-columns {
  display: flex;
  gap: 12px;
}

.picker-column {
  flex: 1;
  text-align: center;
}

.column-label {
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 8px;
}

.column-options {
  max-height: 280px;
  overflow-y: auto;
}

.column-option {
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 15px;
  color: #374151;
  transition: all 0.2s;
}

.column-option:hover {
  background: #f3f4f6;
}

.column-option.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

/* 时辰选择 */
.time-presets {
  margin-bottom: 16px;
}

.preset-btn {
  width: 100%;
  padding: 12px;
  border: 2px dashed #d1d5db;
  border-radius: 10px;
  background: #f9fafb;
  color: #6b7280;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: #eef2ff;
}

.shichen-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.shichen-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 10px 6px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.shichen-btn:hover {
  border-color: #d1d5db;
  background: #f9fafb;
}

.shichen-btn.active {
  border-color: #667eea;
  background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
}

.shichen-name {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.shichen-time {
  font-size: 11px;
  color: #9ca3af;
}

.minute-input {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.minute-input label {
  font-size: 13px;
  color: #6b7280;
}

.minute-input input {
  padding: 12px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 15px;
  text-align: center;
}

.minute-input input:focus {
  outline: none;
  border-color: #667eea;
}

/* 列表选择器 */
.list-picker {
  padding: 8px 0;
}

.list-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  cursor: pointer;
  font-size: 15px;
  color: #374151;
  transition: all 0.2s;
}

.list-option:hover {
  background: #f9fafb;
}

.list-option.active {
  color: #667eea;
  font-weight: 600;
  background: #eef2ff;
}

.list-option svg {
  width: 18px;
  height: 18px;
}

/* 弹窗过渡 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: translateY(20px);
}

/* 响应式 */
@media (max-width: 480px) {
  .form-container {
    padding: 20px;
    border-radius: 16px;
  }

  .location-selectors {
    grid-template-columns: 1fr;
  }

  .shichen-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .datetime-wrapper {
    grid-template-columns: 1fr;
  }

  .quick-input-wrapper {
    flex-direction: column;
  }

  .quick-parse-btn {
    width: 100%;
  }
}
</style>