<template>
  <div class="step-form-page">
    <!-- 头部 -->
    <div class="form-header">
      <button class="back-btn" @click="$emit('back')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="form-title">填写出生信息</h1>
      <div class="placeholder"></div>
    </div>

    <!-- 表单内容 -->
    <div class="form-content">
      <!-- 姓名 -->
      <div class="form-card">
        <label class="card-label">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          姓名
        </label>
        <input
          v-model="form.name"
          type="text"
          class="name-input"
          placeholder="请输入姓名"
          maxlength="10"
        />
      </div>

      <!-- 性别 -->
      <div class="form-card compact">
        <label class="card-label">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 16v-4M12 8h.01"/>
          </svg>
          性别
        </label>
        <div class="gender-options">
          <button
            class="gender-btn"
            :class="{ active: form.gender === 'male' }"
            @click="form.gender = 'male'"
          >
            <span class="gender-icon male">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="10" cy="14" r="5"/>
                <path d="M19 5l-6 6M19 5v4M19 5h-4"/>
              </svg>
            </span>
            <span>男生</span>
          </button>
          <button
            class="gender-btn"
            :class="{ active: form.gender === 'female' }"
            @click="form.gender = 'female'"
          >
            <span class="gender-icon female">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="12" cy="9" r="5"/>
                <path d="M12 14v7M9 18h6"/>
              </svg>
            </span>
            <span>女生</span>
          </button>
        </div>
      </div>

      <!-- 出生日期时间 -->
      <div class="form-card">
        <label class="card-label">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          出生日期时间
        </label>
        
        <!-- 日期时间选择器触发区 -->
        <div class="datetime-trigger" @click="openDatePicker">
          <div class="datetime-display">
            <template v-if="form.hour === null">
              {{ form.year }}年{{ form.month }}月{{ form.day }}日
              <span class="unknown-tag">时辰未知</span>
            </template>
            <template v-else>
              {{ form.year }}年{{ form.month }}月{{ form.day }}日
              {{ form.hour }}时（{{ getShichenName(form.hour) }}）
              {{ form.minute }}分
            </template>
          </div>
          <svg class="edit-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </div>
      </div>

      <!-- 出生地点 -->
      <div class="form-card">
        <label class="card-label">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
          出生地点
          <span class="optional">（可选）</span>
        </label>
        
        <!-- 地点选择触发区 -->
        <div class="location-trigger" @click="openLocationPicker">
          <div class="location-display">
            <template v-if="form.province && form.city">
              {{ form.province }} {{ form.city }}
            </template>
            <template v-else>
              <span class="placeholder">点击选择出生地点</span>
            </template>
          </div>
          <svg class="edit-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </div>

        <p class="location-hint">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          选择城市可使用真太阳时计算，让结果更准确
        </p>
      </div>
    </div>

    <!-- 底部提交按钮 -->
    <div class="form-footer">
      <div class="accuracy-hint">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 16v-4M12 8h.01"/>
        </svg>
        <span>信息填写越准确，分析结果越准确，请认真填写</span>
      </div>
      <button 
        class="submit-btn"
        :disabled="!canSubmit"
        @click="submit"
      >
        开始分析
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </button>
      <p class="disclaimer">本测试为成长娱乐参考，非科学诊断</p>
    </div>

    <!-- 地点选择弹窗 -->
    <Transition name="modal">
      <div v-if="showLocationPicker" class="modal-overlay picker-modal-overlay" @click.self="closeLocationPicker">
        <div class="modal-content">
          <div class="modal-header">
            <h3>选择出生地点</h3>
            <button class="modal-close" @click="closeLocationPicker">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          
          <!-- 文本搜索区域 -->
          <div class="location-search-section">
            <div class="location-search-input-wrapper">
              <input
                v-model="cityInput"
                type="text"
                class="location-search-input"
                placeholder="输入城市名快速搜索"
                @input="onCityInput"
                @keydown.enter="handleLocationEnter"
              />
              <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/>
                <path d="M21 21l-4.35-4.35"/>
              </svg>
            </div>
            
            <!-- 搜索结果 -->
            <div v-if="cityInput.trim() && filteredCities.length > 0" class="location-search-results">
              <div
                v-for="item in filteredCities"
                :key="item.city"
                class="location-result-item"
                @click="selectLocationFromPicker(item)"
              >
                <span class="result-city">{{ item.city }}</span>
                <span class="result-province">{{ item.province }}</span>
              </div>
            </div>
            <div v-else-if="cityInput.trim() && filteredCities.length === 0" class="no-results">
              未找到匹配的城市
            </div>
          </div>
          
          <!-- 滚轮选择区域 -->
          <div class="location-picker-body" v-if="!cityInput.trim()">
            <div class="location-picker-columns">
              <!-- 省份列 -->
              <div class="location-picker-column">
                <div class="location-column-label">省份</div>
                <div class="location-column-options">
                  <div
                    v-for="province in provinceList"
                    :key="province"
                    class="location-column-option"
                    :class="{ active: tempLocation.province === province }"
                    @click="selectProvince(province)"
                  >
                    {{ province }}
                  </div>
                </div>
              </div>
              
              <!-- 城市列 -->
              <div class="location-picker-column">
                <div class="location-column-label">城市</div>
                <div class="location-column-options">
                  <div
                    v-for="city in cityListForSelectedProvince"
                    :key="city"
                    class="location-column-option"
                    :class="{ active: tempLocation.city === city }"
                    @click="selectCity(city)"
                  >
                    {{ city }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="modal-footer">
            <button class="btn-skip" @click="skipLocation">跳过</button>
            <button class="btn-confirm" @click="confirmLocation" :disabled="!tempLocation.city">确定</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 日期时间选择弹窗 - iOS适配优化版 -->
    <Transition name="modal">
      <div v-if="showDatePicker" class="modal-overlay picker-modal-overlay" @click.self="closeDatePicker">
        <div class="modal-content">
          <div class="modal-header">
            <h3>选择出生日期时间</h3>
            <button class="modal-close" @click="closeDatePicker">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          
          <!-- iOS原生日期输入（iOS设备优先使用） -->
          <div v-if="isIOS" class="ios-date-inputs">
            <div class="ios-input-group">
              <label>出生日期</label>
              <input 
                type="date" 
                v-model="iosDateString"
                class="ios-date-picker"
                :max="maxDate"
                :min="minDate"
              />
            </div>
            <div class="ios-input-group">
              <label>出生时间</label>
              <input 
                type="time" 
                v-model="iosTimeString"
                class="ios-time-picker"
              />
            </div>
          </div>
          
          <!-- 快速输入区域（非iOS设备显示） - 无文字标签 -->
          <div v-else class="quick-input-section compact">
            <input
              v-model="quickDateInput"
              type="text"
              inputmode="numeric"
              class="quick-input"
              placeholder="输入数字串，如：200008151230"
              @input="handleQuickDateInput"
              @keydown.enter="confirmDateTime"
            />
          </div>

          <!-- 滚轮选择区域 - 紧凑版 -->
          <div class="picker-body compact">
            <div class="picker-columns">
              <!-- 年 -->
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
              
              <!-- 月 -->
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
              
              <!-- 日 -->
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
              
              <!-- 时 -->
              <div class="picker-column">
                <div class="column-label">时</div>
                <div class="column-options">
                  <div
                    v-for="hour in 24"
                    :key="hour - 1"
                    class="column-option"
                    :class="{ active: tempDate.hour === hour - 1 }"
                    @click="tempDate.hour = hour - 1"
                  >
                    {{ hour - 1 }}
                  </div>
                </div>
              </div>
              
              <!-- 分 -->
              <div class="picker-column narrow">
                <div class="column-label">分</div>
                <div class="column-options">
                  <div
                    v-for="minute in [0, 10, 20, 30, 40, 50]"
                    :key="minute"
                    class="column-option"
                    :class="{ active: tempDate.minute === minute }"
                    @click="tempDate.minute = minute"
                  >
                    {{ minute }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="modal-footer">
            <button class="btn-unknown" @click="selectUnknownTimeInModal">时辰未知</button>
            <button class="btn-confirm" @click="confirmDateTime">确定</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, reactive, watch } from 'vue'
import { cityData } from '../data/cities'

const props = defineProps({
  initialData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['submit', 'back'])

// 检测是否为 iOS 设备
const isIOS = computed(() => {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera
  return /iphone|ipad|ipod/i.test(userAgent.toLowerCase())
})

// 检测是否为 Android 设备
const isAndroid = computed(() => {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera
  return /android/i.test(userAgent.toLowerCase())
})

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

// 如果有初始数据，恢复表单
if (props.initialData) {
  form.value = { ...form.value, ...props.initialData }
}

// iOS 日期时间字符串
const iosDateString = ref('2000-01-01')
const iosTimeString = ref('12:00')

// 同步 iOS 日期时间到临时数据
watch(iosDateString, (newVal) => {
  if (newVal) {
    const [year, month, day] = newVal.split('-').map(Number)
    tempDate.year = year
    tempDate.month = month
    tempDate.day = day
  }
})

watch(iosTimeString, (newVal) => {
  if (newVal) {
    const [hour, minute] = newVal.split(':').map(Number)
    tempDate.hour = hour
    tempDate.minute = minute
  }
})

// 城市输入
const cityInput = ref('')
const showCitySuggestions = ref(false)

// 弹窗控制
const showDatePicker = ref(false)
const showLocationPicker = ref(false)

// 临时地点数据
const tempLocation = reactive({
  province: '',
  city: ''
})

// 临时日期数据
const tempDate = reactive({
  year: 2000,
  month: 1,
  day: 1,
  hour: 12,
  minute: 0
})

// 快速输入
const quickDateInput = ref('')

// 年份选项
const yearOptions = Array.from({ length: 125 }, (_, i) => 2025 - i)

// 日期范围限制
const maxDate = '2025-12-31'
const minDate = '1900-01-01'

// 计算属性
const daysInMonth = computed(() => {
  return new Date(tempDate.year, tempDate.month, 0).getDate()
})

const canSubmit = computed(() => {
  return form.value.name.trim().length > 0 && form.value.gender
})

// 城市建议列表
const citySuggestions = computed(() => {
  if (!cityInput.value.trim()) return []
  
  const input = cityInput.value.trim().toLowerCase()
  const suggestions = []
  
  for (const [province, cities] of Object.entries(cityData)) {
    for (const city of cities) {
      if (city.toLowerCase().includes(input) || province.toLowerCase().includes(input)) {
        suggestions.push({ province, city })
        if (suggestions.length >= 5) break
      }
    }
    if (suggestions.length >= 5) break
  }
  
  return suggestions
})

// 地点选择器相关计算属性和方法
const provinceList = computed(() => {
  return Object.keys(cityData)
})

const cityListForSelectedProvince = computed(() => {
  if (!tempLocation.province) return []
  return cityData[tempLocation.province] || []
})

const filteredCities = computed(() => {
  if (!cityInput.value.trim()) return []
  
  const input = cityInput.value.trim().toLowerCase()
  const results = []
  
  for (const [province, cities] of Object.entries(cityData)) {
    for (const city of cities) {
      if (city.toLowerCase().includes(input) || province.toLowerCase().includes(input)) {
        results.push({ province, city })
        if (results.length >= 10) break
      }
    }
    if (results.length >= 10) break
  }
  
  return results
})

// 打开日期选择器
const openDatePicker = () => {
  // 同步当前表单值到临时数据
  tempDate.year = form.value.year
  tempDate.month = form.value.month
  tempDate.day = form.value.day
  tempDate.hour = form.value.hour !== null ? form.value.hour : 12
  tempDate.minute = form.value.minute
  
  // 同步到 iOS 输入
  iosDateString.value = `${tempDate.year}-${String(tempDate.month).padStart(2, '0')}-${String(tempDate.day).padStart(2, '0')}`
  iosTimeString.value = `${String(tempDate.hour).padStart(2, '0')}:${String(tempDate.minute).padStart(2, '0')}`
  
  showDatePicker.value = true
}

// 关闭日期选择器
const closeDatePicker = () => {
  showDatePicker.value = false
  quickDateInput.value = ''
}

// 打开地点选择器
const openLocationPicker = () => {
  // 同步当前表单值到临时数据
  if (form.value.province && form.value.city) {
    tempLocation.province = form.value.province
    tempLocation.city = form.value.city
  }
  showLocationPicker.value = true
}

// 关闭地点选择器
const closeLocationPicker = () => {
  showLocationPicker.value = false
  cityInput.value = ''
}

// 处理地点输入回车
const handleLocationEnter = () => {
  if (filteredCities.value.length > 0) {
    // 选择第一个结果
    selectLocationFromPicker(filteredCities.value[0])
  }
}

const selectProvince = (province) => {
  tempLocation.province = province
  tempLocation.city = ''
}

const selectCity = (city) => {
  tempLocation.city = city
}

const selectLocationFromPicker = (item) => {
  tempLocation.province = item.province
  tempLocation.city = item.city
  confirmLocation()
}

const skipLocation = () => {
  form.value.province = ''
  form.value.city = ''
  cityInput.value = ''
  tempLocation.province = ''
  tempLocation.city = ''
  showLocationPicker.value = false
}

const confirmLocation = () => {
  if (tempLocation.city) {
    form.value.province = tempLocation.province
    form.value.city = tempLocation.city
    cityInput.value = tempLocation.city
  }
  showLocationPicker.value = false
}

// 获取时辰名称
const getShichenName = (hour) => {
  const shichenList = [
    { name: '子时', hour: 0 }, { name: '丑时', hour: 1 },
    { name: '寅时', hour: 3 }, { name: '卯时', hour: 5 },
    { name: '辰时', hour: 7 }, { name: '巳时', hour: 9 },
    { name: '午时', hour: 11 }, { name: '未时', hour: 13 },
    { name: '申时', hour: 15 }, { name: '酉时', hour: 17 },
    { name: '戌时', hour: 19 }, { name: '亥时', hour: 21 }
  ]
  
  for (let i = shichenList.length - 1; i >= 0; i--) {
    if (hour >= shichenList[i].hour) {
      return shichenList[i].name
    }
  }
  return '子时'
}

const onCityInput = () => {
  showCitySuggestions.value = true
}

const selectCitySuggestion = (item) => {
  form.value.province = item.province
  form.value.city = item.city
  cityInput.value = item.city
  showCitySuggestions.value = false
}

const clearLocation = () => {
  form.value.province = ''
  form.value.city = ''
  cityInput.value = ''
}

const selectUnknownTimeInModal = () => {
  form.value.hour = null
  form.value.minute = 0
  closeDatePicker()
}

const confirmDateTime = () => {
  form.value.year = tempDate.year
  form.value.month = tempDate.month
  form.value.day = tempDate.day
  form.value.hour = tempDate.hour
  form.value.minute = tempDate.minute
  closeDatePicker()
}

// 处理快速日期输入
const handleQuickDateInput = () => {
  const input = quickDateInput.value.trim().replace(/\D/g, '')
  
  if (input.length === 8) {
    const year = parseInt(input.substring(0, 4))
    const month = parseInt(input.substring(4, 6))
    const day = parseInt(input.substring(6, 8))
    
    if (validateDate(year, month, day)) {
      tempDate.year = year
      tempDate.month = month
      tempDate.day = day
      tempDate.hour = 12
      tempDate.minute = 0
    }
  } else if (input.length === 10) {
    const year = parseInt(input.substring(0, 4))
    const month = parseInt(input.substring(4, 6))
    const day = parseInt(input.substring(6, 8))
    const hour = parseInt(input.substring(8, 10))
    
    if (validateDate(year, month, day, hour)) {
      tempDate.year = year
      tempDate.month = month
      tempDate.day = day
      tempDate.hour = hour
      tempDate.minute = 0
    }
  } else if (input.length === 12) {
    const year = parseInt(input.substring(0, 4))
    const month = parseInt(input.substring(4, 6))
    const day = parseInt(input.substring(6, 8))
    const hour = parseInt(input.substring(8, 10))
    const minute = parseInt(input.substring(10, 12))
    
    if (validateDate(year, month, day, hour, minute)) {
      tempDate.year = year
      tempDate.month = month
      tempDate.day = day
      tempDate.hour = hour
      tempDate.minute = minute
    }
  }
}

// 验证日期有效性
const validateDate = (year, month, day, hour = null, minute = null) => {
  if (year < 1900 || year > 2100) return false
  if (month < 1 || month > 12) return false
  
  const maxDay = new Date(year, month, 0).getDate()
  if (day < 1 || day > maxDay) return false
  
  if (hour !== null && (hour < 0 || hour > 23)) return false
  if (minute !== null && (minute < 0 || minute > 59)) return false
  
  return true
}

const submit = () => {
  emit('submit', { ...form.value })
}
</script>

<style scoped>
/* 设备检测样式 - 电脑端 */
@media (min-width: 1024px) {
  .step-form-page {
    max-width: 560px;
    margin: 0 auto;
    box-shadow: 0 0 40px rgba(0, 0, 0, 0.1);
  }
  
  .form-header {
    padding: 20px 32px;
  }
  
  .form-content {
    max-width: 480px;
    padding: 32px 24px;
  }
  
  .form-card {
    padding: 20px 24px;
    margin-bottom: 16px;
  }
  
  .card-label {
    font-size: 14px;
    margin-bottom: 12px;
  }
  
  .card-label svg {
    width: 16px;
    max-width: 16px;
    min-width: 16px;
  }
  
  .name-input {
    padding: 14px 16px;
    font-size: 15px;
  }
  
  .gender-options {
    gap: 12px;
  }
  
  .gender-btn {
    padding: 14px 16px;
    gap: 8px;
  }
  
  .gender-icon {
    width: 24px;
    height: 24px;
  }
  
  .datetime-trigger,
  .location-trigger {
    padding: 14px 16px;
  }
  
  .datetime-display,
  .location-display {
    font-size: 15px;
  }
  
  .location-hint {
    font-size: 12px;
    margin-top: 10px;
  }
  
  .form-footer {
    padding: 20px;
  }
  
  .accuracy-hint {
    padding: 12px 16px;
    margin-bottom: 16px;
    font-size: 13px;
  }
  
  .submit-btn {
    padding: 14px 24px;
    font-size: 16px;
  }
}

.step-form-page {
  min-height: 100vh;
  min-height: 100dvh;
  background: linear-gradient(180deg, #F0F9FF 0%, #FDFCF8 50%, #F0FFF4 100%);
  display: flex;
  flex-direction: column;
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
}

/* 头部 */
.form-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2vh 5vw;
  background: white;
  border-bottom: 1px solid rgba(142, 197, 252, 0.2);
  flex-shrink: 0;
}

.back-btn {
  width: 10vw;
  height: 10vw;
  max-width: 40px;
  max-height: 40px;
  min-width: 36px;
  min-height: 36px;
  border: none;
  background: #F7FAFC;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #F0F9FF;
}

.back-btn svg {
  width: 50%;
  height: 50%;
  color: #718096;
}

.form-title {
  font-size: clamp(1rem, 4vw, 1.0625rem);
  font-weight: 600;
  color: #4A5568;
  margin: 0;
}

.placeholder {
  width: 10vw;
  max-width: 40px;
  min-width: 36px;
}

/* 表单内容 */
.form-content {
  flex: 1;
  padding: 3vh 5vw;
  display: flex;
  flex-direction: column;
  gap: 2.5vh;
  max-width: 100%;
  margin: 0 auto;
  width: 100%;
  max-width: 520px;
  overflow-y: auto;
}

/* 卡片样式 */
.form-card {
  background: white;
  border-radius: 16px;
  padding: 3vh 4vw;
  box-shadow: 0 2px 12px rgba(142, 197, 252, 0.08);
  border: 1px solid rgba(142, 197, 252, 0.15);
}

.form-card.compact {
  padding: 2.5vh 4vw;
}

.card-label {
  display: flex;
  align-items: center;
  gap: 2vw;
  font-size: clamp(0.875rem, 3.5vw, 0.9375rem);
  font-weight: 600;
  color: #4A5568;
  margin-bottom: 2vh;
}

.card-label svg {
  width: 5vw;
  max-width: 18px;
  min-width: 16px;
  height: auto;
  color: #8EC5FC;
}

.optional {
  font-size: clamp(0.75rem, 3vw, 0.8125rem);
  color: #A0AEC0;
  font-weight: normal;
}

/* 姓名输入 */
.name-input {
  width: 100%;
  padding: 2vh 4vw;
  font-size: clamp(1rem, 4vw, 1.0625rem);
  border: 2px solid #E2E8F0;
  border-radius: 12px;
  transition: all 0.2s;
  color: #4A5568;
}

.name-input:focus {
  outline: none;
  border-color: #8EC5FC;
  box-shadow: 0 0 0 4px rgba(142, 197, 252, 0.15);
}

.name-input::placeholder {
  color: #A0AEC0;
}

/* 性别选择 */
.gender-options {
  display: flex;
  gap: 3vw;
}

.gender-btn {
  flex: 1;
  padding: 2vh 3vw;
  background: #F7FAFC;
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.2vh;
  transition: all 0.2s;
  font-size: clamp(0.875rem, 3.5vw, 0.9375rem);
  color: #718096;
}

.gender-btn:hover {
  background: #F0F9FF;
}

.gender-btn.active {
  border-color: #8EC5FC;
  background: linear-gradient(135deg, #F0F9FF 0%, #F0FFF4 100%);
  color: #4A5568;
}

.gender-icon {
  width: 6vw;
  height: 6vw;
  max-width: 26px;
  max-height: 26px;
  min-width: 22px;
  min-height: 22px;
}

.gender-icon svg {
  width: 100%;
  height: 100%;
}

.gender-icon.male svg {
  color: #8EC5FC;
}

.gender-icon.female svg {
  color: #F472B6;
}

.gender-btn.active .gender-icon.male svg {
  color: #3B82F6;
}

.gender-btn.active .gender-icon.female svg {
  color: #EC4899;
}

/* 日期时间显示 */
.datetime-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2vh 4vw;
  background: #F7FAFC;
  border: 2px solid #E2E8F0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.datetime-trigger:hover {
  border-color: #8EC5FC;
}

.datetime-display {
  font-size: clamp(0.9375rem, 4vw, 1rem);
  color: #4A5568;
  line-height: 1.6;
}

.unknown-tag {
  display: inline-block;
  padding: 0.8vh 2.5vw;
  background: linear-gradient(135deg, #F0F9FF 0%, #F0FFF4 100%);
  color: #8EC5FC;
  font-size: clamp(0.6875rem, 3vw, 0.75rem);
  border-radius: 20px;
  margin-left: 2vw;
  font-weight: 500;
}

.edit-icon {
  width: 5vw;
  max-width: 20px;
  min-width: 18px;
  height: auto;
  color: #A0AEC0;
  flex-shrink: 0;
}

/* 地点选择触发 */
.location-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2vh 4vw;
  background: #F7FAFC;
  border: 2px solid #E2E8F0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.location-trigger:hover {
  border-color: #8EC5FC;
}

.location-display {
  font-size: clamp(0.9375rem, 4vw, 1rem);
  color: #4A5568;
}

.location-display .placeholder {
  color: #A0AEC0;
}

/* 地点提示 */
.location-hint {
  margin: 1.5vh 0 0;
  font-size: clamp(0.75rem, 3vw, 0.8125rem);
  color: #A0AEC0;
  display: flex;
  align-items: center;
  gap: 1.5vw;
}

.location-hint svg {
  width: 4vw;
  max-width: 14px;
  min-width: 12px;
  height: auto;
  flex-shrink: 0;
}

/* 底部 */
.form-footer {
  padding: 3vh 5vw;
  background: white;
  border-top: 1px solid rgba(142, 197, 252, 0.2);
  flex-shrink: 0;
}

.accuracy-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2vw;
  padding: 2vh 3vw;
  background: linear-gradient(135deg, #F0F9FF 0%, #F0FFF4 100%);
  border-radius: 10px;
  margin-bottom: 2.5vh;
  font-size: clamp(0.8125rem, 3.5vw, 0.875rem);
  color: #4A5568;
}

.accuracy-hint svg {
  width: 4.5vw;
  max-width: 16px;
  min-width: 14px;
  height: auto;
  color: #8EC5FC;
  flex-shrink: 0;
}

.submit-btn {
  width: 100%;
  padding: 2.5vh 6vw;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: clamp(1.0625rem, 4.5vw, 1.125rem);
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2vw;
  box-shadow: 0 4px 16px rgba(142, 197, 252, 0.3);
  transition: all 0.3s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(142, 197, 252, 0.4);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-btn svg {
  width: 5.5vw;
  max-width: 20px;
  min-width: 18px;
  height: auto;
}

.disclaimer {
  text-align: center;
  margin: 2vh 0 0;
  font-size: clamp(0.75rem, 3vw, 0.8125rem);
  color: #A0AEC0;
}

/* 弹窗样式 - 统一位置在顶部 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(74, 85, 104, 0.5);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  z-index: 1000;
  padding: 8vh 3vw 2vh;
  padding-bottom: max(2vh, env(safe-area-inset-bottom));
}

.modal-overlay.picker-modal-overlay {
  align-items: flex-start;
  padding-top: 10vh;
}

.modal-content {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-width: 400px;
  max-height: 75vh;
  display: flex;
  flex-direction: column;
  animation: slideDown 0.3s ease;
  box-shadow: 0 -4px 24px rgba(142, 197, 252, 0.2);
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
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
  padding: 2.5vh 5vw;
  border-bottom: 1px solid #F0F0F0;
  flex-shrink: 0;
}

.modal-header h3 {
  margin: 0;
  font-size: clamp(1rem, 4vw, 1.0625rem);
  font-weight: 600;
  color: #4A5568;
}

.modal-close {
  width: 9vw;
  height: 9vw;
  max-width: 32px;
  max-height: 32px;
  min-width: 28px;
  min-height: 28px;
  border: none;
  background: #F7FAFC;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: #F0F9FF;
}

.modal-close svg {
  width: 60%;
  height: 60%;
  color: #718096;
}

/* iOS 日期输入样式 */
.ios-date-inputs {
  padding: 2vh 5vw;
  border-bottom: 1px solid #F0F0F0;
}

.ios-input-group {
  margin-bottom: 2vh;
}

.ios-input-group:last-child {
  margin-bottom: 0;
}

.ios-input-group label {
  display: block;
  font-size: clamp(0.8125rem, 3.5vw, 0.875rem);
  font-weight: 600;
  color: #4A5568;
  margin-bottom: 1vh;
}

.ios-date-picker,
.ios-time-picker {
  width: 100%;
  padding: 2vh 4vw;
  font-size: clamp(1rem, 4vw, 1.0625rem);
  border: 2px solid #E2E8F0;
  border-radius: 12px;
  background: white;
  color: #4A5568;
  -webkit-appearance: none;
  appearance: none;
}

.ios-date-picker:focus,
.ios-time-picker:focus {
  outline: none;
  border-color: #8EC5FC;
  box-shadow: 0 0 0 4px rgba(142, 197, 252, 0.15);
}

/* 快速输入区域 - 更紧凑 */
.quick-input-section {
  padding: 1.5vh 5vw;
  border-bottom: 1px solid #F0F0F0;
  background: linear-gradient(135deg, #F0F9FF 0%, #F0FFF4 100%);
}

.quick-input-section.compact {
  padding: 1.2vh 5vw;
}

.quick-input-label {
  display: block;
  font-size: clamp(0.8125rem, 3.5vw, 0.875rem);
  font-weight: 600;
  color: #4A5568;
  margin-bottom: 1.5vh;
}

.quick-input {
  width: 100%;
  padding: 1.8vh 4vw;
  font-size: clamp(1rem, 4.5vw, 1.125rem);
  border: 2px solid #E2E8F0;
  border-radius: 12px;
  transition: all 0.2s;
  color: #4A5568;
  text-align: center;
  letter-spacing: 2px;
  font-family: monospace;
}

.quick-input:focus {
  outline: none;
  border-color: #8EC5FC;
  box-shadow: 0 0 0 4px rgba(142, 197, 252, 0.15);
}

.quick-input::placeholder {
  color: #A0AEC0;
  letter-spacing: 0;
  font-size: clamp(0.8125rem, 3.5vw, 0.875rem);
  font-family: inherit;
}

/* 滚轮选择区域 - 紧凑版 */
.picker-body {
  padding: 1.5vh 4vw;
  flex: 1;
  overflow: hidden;
}

.picker-body.compact {
  padding: 1vh 3vw;
}

.picker-columns {
  display: flex;
  gap: 2vw;
  height: 32vh;
  max-height: 260px;
  min-height: 180px;
}

.picker-body.compact .picker-columns {
  height: 28vh;
  max-height: 220px;
  min-height: 160px;
}

.picker-column {
  flex: 1;
  text-align: center;
}

.picker-column.narrow {
  flex: 0.7;
}

.column-label {
  font-size: clamp(0.75rem, 3vw, 0.8125rem);
  color: #A0AEC0;
  margin-bottom: 1vh;
  font-weight: 500;
}

.column-options {
  height: calc(100% - 2.5vh);
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.column-option {
  padding: 1.2vh 1vw;
  font-size: clamp(0.875rem, 3.8vw, 0.9375rem);
  color: #4A5568;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
}

.column-option:hover {
  background: #F0F9FF;
}

.column-option.active {
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  font-weight: 600;
}

/* 弹窗底部 */
.modal-footer {
  display: flex;
  gap: 3vw;
  padding: 2vh 5vw;
  border-top: 1px solid #F0F0F0;
  flex-shrink: 0;
}

.btn-unknown,
.btn-confirm,
.btn-skip {
  flex: 1;
  padding: 2vh 4vw;
  border-radius: 12px;
  font-size: clamp(0.9375rem, 4vw, 1rem);
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-unknown,
.btn-skip {
  background: #F7FAFC;
  color: #718096;
}

.btn-unknown:hover,
.btn-skip:hover {
  background: #F0F9FF;
}

.btn-confirm {
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
}

.btn-confirm:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(142, 197, 252, 0.3);
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 地点选择弹窗样式 */
.location-search-section {
  padding: 2vh 5vw;
  border-bottom: 1px solid #F0F0F0;
  background: #F7FAFC;
}

.location-search-input-wrapper {
  position: relative;
}

.location-search-input {
  width: 100%;
  padding: 1.8vh 10vw 1.8vh 4vw;
  font-size: clamp(0.9375rem, 4vw, 1rem);
  border: 2px solid #E2E8F0;
  border-radius: 12px;
  transition: all 0.2s;
  color: #4A5568;
}

.location-search-input:focus {
  outline: none;
  border-color: #8EC5FC;
  box-shadow: 0 0 0 4px rgba(142, 197, 252, 0.15);
}

.search-icon {
  position: absolute;
  right: 3vw;
  top: 50%;
  transform: translateY(-50%);
  width: 5vw;
  max-width: 18px;
  min-width: 16px;
  height: auto;
  color: #A0AEC0;
}

.location-search-results {
  margin-top: 1.5vh;
  max-height: 18vh;
  overflow-y: auto;
  background: white;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
}

.location-result-item {
  padding: 1.8vh 4vw;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #F0F0F0;
}

.location-result-item:last-child {
  border-bottom: none;
}

.location-result-item:hover {
  background: #F0F9FF;
}

.result-city {
  font-size: clamp(0.9375rem, 4vw, 1rem);
  color: #4A5568;
  font-weight: 500;
}

.result-province {
  font-size: clamp(0.75rem, 3vw, 0.8125rem);
  color: #A0AEC0;
}

.no-results {
  text-align: center;
  padding: 3vh 4vw;
  color: #A0AEC0;
  font-size: clamp(0.875rem, 4vw, 0.9375rem);
}

.location-picker-body {
  padding: 2vh 4vw;
  flex: 1;
  overflow: hidden;
}

.location-picker-columns {
  display: flex;
  gap: 3vw;
  height: 28vh;
  max-height: 240px;
}

.location-picker-column {
  flex: 1;
  text-align: center;
}

.location-column-label {
  font-size: clamp(0.75rem, 3vw, 0.8125rem);
  color: #A0AEC0;
  margin-bottom: 1vh;
  font-weight: 500;
}

.location-column-options {
  height: calc(100% - 2.5vh);
  overflow-y: auto;
  background: #F7FAFC;
  border-radius: 12px;
  padding: 1.5vh 2vw;
  -webkit-overflow-scrolling: touch;
}

.location-column-option {
  padding: 1.5vh 2vw;
  font-size: clamp(0.875rem, 3.8vw, 0.9375rem);
  color: #4A5568;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
  margin-bottom: 0.5vh;
}

.location-column-option:last-child {
  margin-bottom: 0;
}

.location-column-option:hover {
  background: #F0F9FF;
}

.location-column-option.active {
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  font-weight: 600;
}

/* 过渡动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

/* 响应式 */
@media (max-width: 480px) {
  .form-content {
    padding: 2.5vh 4vw;
    gap: 2vh;
  }
  
  .form-card {
    padding: 2.5vh 4vw;
    border-radius: 14px;
  }
  
  .form-card.compact {
    padding: 2vh 4vw;
  }
  
  .picker-columns {
    gap: 1.5vw;
  }
  
  .column-option {
    padding: 1vh 0.5vw;
  }
  
  .modal-footer {
    gap: 2.5vw;
  }
  
  .gender-icon {
    width: 5.5vw;
    height: 5.5vw;
  }
  
  .gender-btn {
    padding: 1.8vh 3vw;
    gap: 1vh;
  }
}

@media (max-height: 600px) and (orientation: landscape) {
  .form-content {
    padding: 2vh 4vw;
  }
  
  .form-card {
    padding: 2vh 3vw;
  }
  
  .picker-columns {
    height: 22vh;
    max-height: 180px;
  }
  
  .modal-overlay.picker-modal-overlay {
    padding-top: 5vh;
  }
}

/* 适配 iOS 安全区 */
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .modal-overlay {
    padding-bottom: max(2vh, env(safe-area-inset-bottom));
  }
}
</style>
