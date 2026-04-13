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
      <div class="form-card">
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
            <span class="gender-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="8" r="5"/>
                <path d="M12 13v8M9 18h6"/>
              </svg>
            </span>
            <span>男生</span>
          </button>
          <button
            class="gender-btn"
            :class="{ active: form.gender === 'female' }"
            @click="form.gender = 'female'"
          >
            <span class="gender-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="8" r="5"/>
                <path d="M12 13v8M9 16h6"/>
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
        <div class="datetime-trigger" @click="showDatePicker = true">
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

        <!-- 时辰未知按钮 -->
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
        
        <!-- 城市输入 -->
        <div class="city-input-wrapper">
          <input
            v-model="cityInput"
            type="text"
            class="city-input"
            placeholder="输入城市名自动匹配"
            @input="onCityInput"
            @focus="showCitySuggestions = true"
          />
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
          </svg>
          
          <!-- 城市建议列表 -->
          <div v-if="showCitySuggestions && citySuggestions.length > 0" class="city-suggestions">
            <div
              v-for="item in citySuggestions"
              :key="item.city"
              class="suggestion-item"
              @click="selectCitySuggestion(item)"
            >
              <span class="city-name">{{ item.city }}</span>
              <span class="province-name">{{ item.province }}</span>
            </div>
          </div>
        </div>

        <!-- 已选地点显示 -->
        <div v-if="form.province && form.city" class="selected-location">
          <span class="location-tag">
            {{ form.province }} {{ form.city }}
            <button class="clear-btn" @click="clearLocation">×</button>
          </span>
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

    <!-- 日期时间选择弹窗 -->
    <Transition name="modal">
      <div v-if="showDatePicker" class="modal-overlay" @click.self="showDatePicker = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>选择出生日期时间</h3>
            <button class="modal-close" @click="showDatePicker = false">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          
          <div class="picker-body">
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
import { ref, computed, reactive } from 'vue'
import { cityData } from '../data/cities'

const emit = defineEmits(['submit', 'back'])

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

// 城市输入
const cityInput = ref('')
const showCitySuggestions = ref(false)

// 弹窗控制
const showDatePicker = ref(false)

// 临时日期数据
const tempDate = reactive({
  year: 2000,
  month: 1,
  day: 1,
  hour: 12,
  minute: 0
})

// 年份选项
const yearOptions = Array.from({ length: 125 }, (_, i) => 2025 - i)

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

// 方法
const setUnknownTime = () => {
  form.value.hour = null
  form.value.minute = 0
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
  showDatePicker.value = false
}

const confirmDateTime = () => {
  form.value.year = tempDate.year
  form.value.month = tempDate.month
  form.value.day = tempDate.day
  form.value.hour = tempDate.hour
  form.value.minute = tempDate.minute
  showDatePicker.value = false
}

const submit = () => {
  emit('submit', { ...form.value })
}
</script>

<style scoped>
.step-form-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #F0F9FF 0%, #FDFCF8 50%, #F0FFF4 100%);
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
  border-bottom: 1px solid rgba(142, 197, 252, 0.2);
}

.back-btn {
  width: 40px;
  height: 40px;
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
  width: 20px;
  height: 20px;
  color: #718096;
}

.form-title {
  font-size: 17px;
  font-weight: 600;
  color: #4A5568;
  margin: 0;
}

.placeholder {
  width: 40px;
}

/* 表单内容 */
.form-content {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 480px;
  margin: 0 auto;
  width: 100%;
}

/* 卡片样式 */
.form-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(142, 197, 252, 0.08);
  border: 1px solid rgba(142, 197, 252, 0.15);
}

.card-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #4A5568;
  margin-bottom: 16px;
}

.card-label svg {
  width: 18px;
  height: 18px;
  color: #8EC5FC;
}

.optional {
  font-size: 12px;
  color: #A0AEC0;
  font-weight: normal;
}

/* 姓名输入 */
.name-input {
  width: 100%;
  padding: 14px 16px;
  font-size: 16px;
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
  gap: 12px;
}

.gender-btn {
  flex: 1;
  padding: 16px;
  background: #F7FAFC;
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  font-size: 14px;
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
  width: 32px;
  height: 32px;
}

.gender-icon svg {
  width: 100%;
  height: 100%;
  color: #8EC5FC;
}

/* 日期时间显示 */
.datetime-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
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
  font-size: 15px;
  color: #4A5568;
  line-height: 1.6;
}

.unknown-tag {
  display: inline-block;
  padding: 4px 10px;
  background: linear-gradient(135deg, #F0F9FF 0%, #F0FFF4 100%);
  color: #8EC5FC;
  font-size: 12px;
  border-radius: 20px;
  margin-left: 8px;
  font-weight: 500;
}

.edit-icon {
  width: 20px;
  height: 20px;
  color: #A0AEC0;
}

/* 时辰未知按钮 */
.unknown-time-btn {
  width: 100%;
  margin-top: 12px;
  padding: 12px;
  background: transparent;
  border: 2px dashed #E2E8F0;
  border-radius: 10px;
  color: #A0AEC0;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s;
}

.unknown-time-btn svg {
  width: 16px;
  height: 16px;
}

.unknown-time-btn:hover {
  border-color: #8EC5FC;
  color: #8EC5FC;
}

.unknown-time-btn.active {
  border-color: #8EC5FC;
  color: #8EC5FC;
  background: linear-gradient(135deg, #F0F9FF 0%, #F0FFF4 100%);
}

/* 城市输入 */
.city-input-wrapper {
  position: relative;
}

.city-input {
  width: 100%;
  padding: 14px 40px 14px 16px;
  font-size: 15px;
  border: 2px solid #E2E8F0;
  border-radius: 12px;
  transition: all 0.2s;
  color: #4A5568;
}

.city-input:focus {
  outline: none;
  border-color: #8EC5FC;
  box-shadow: 0 0 0 4px rgba(142, 197, 252, 0.15);
}

.city-input::placeholder {
  color: #A0AEC0;
}

.search-icon {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: #A0AEC0;
}

/* 城市建议列表 */
.city-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(142, 197, 252, 0.15);
  z-index: 100;
  overflow: hidden;
  border: 1px solid rgba(142, 197, 252, 0.2);
}

.suggestion-item {
  padding: 14px 16px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #F0F0F0;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover {
  background: #F0F9FF;
}

.city-name {
  font-size: 15px;
  color: #4A5568;
}

.province-name {
  font-size: 13px;
  color: #A0AEC0;
}

/* 已选地点 */
.selected-location {
  margin-top: 12px;
}

.location-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: linear-gradient(135deg, #F0F9FF 0%, #F0FFF4 100%);
  color: #4A5568;
  font-size: 14px;
  border-radius: 20px;
  border: 1px solid rgba(142, 197, 252, 0.3);
}

.clear-btn {
  width: 18px;
  height: 18px;
  border: none;
  background: rgba(142, 197, 252, 0.3);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #718096;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: rgba(142, 197, 252, 0.5);
}

.location-hint {
  margin: 12px 0 0;
  font-size: 12px;
  color: #A0AEC0;
  display: flex;
  align-items: center;
  gap: 4px;
}

.location-hint svg {
  width: 14px;
  height: 14px;
}

/* 底部 */
.form-footer {
  padding: 20px;
  background: white;
  border-top: 1px solid rgba(142, 197, 252, 0.2);
}

.submit-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
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
  width: 20px;
  height: 20px;
}

.disclaimer {
  text-align: center;
  margin: 12px 0 0;
  font-size: 12px;
  color: #A0AEC0;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(74, 85, 104, 0.5);
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
  box-shadow: 0 -4px 24px rgba(142, 197, 252, 0.2);
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
  padding: 16px 20px;
  border-bottom: 1px solid #F0F0F0;
}

.modal-header h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: #4A5568;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #F7FAFC;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #F0F9FF;
}

.modal-close svg {
  width: 18px;
  height: 18px;
  color: #718096;
}

.picker-body {
  padding: 16px;
}

.picker-columns {
  display: flex;
  gap: 8px;
  height: 220px;
}

.picker-column {
  flex: 1;
  text-align: center;
}

.picker-column.narrow {
  flex: 0.7;
}

.column-label {
  font-size: 13px;
  color: #A0AEC0;
  margin-bottom: 8px;
  font-weight: 500;
}

.column-options {
  height: 190px;
  overflow-y: auto;
}

.column-option {
  padding: 10px 4px;
  font-size: 15px;
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

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #F0F0F0;
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
  transition: all 0.2s;
}

.btn-unknown {
  background: #F7FAFC;
  color: #718096;
}

.btn-unknown:hover {
  background: #F0F9FF;
}

.btn-confirm {
  background: linear-gradient(135deg, #8EC5FC 0%, #A8E6CF 100%);
  color: white;
}

.btn-confirm:hover {
  box-shadow: 0 4px 12px rgba(142, 197, 252, 0.3);
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
</style>