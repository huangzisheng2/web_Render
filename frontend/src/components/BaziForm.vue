<template>
  <div class="form-container">
    <div class="form-header">
      <h2>输入出生信息</h2>
      <p class="subtitle">获取您的专属天赋性格分析报告</p>
    </div>
    
    <Form @submit="onSubmit">
      <!-- 姓名 -->
      <CellGroup inset class="form-group">
        <Field
          v-model="form.name"
          name="name"
          label="姓名"
          placeholder="请输入姓名"
          :rules="[{ required: true, message: '请输入姓名' }]"
        />
      </CellGroup>
      
      <!-- 性别 -->
      <CellGroup inset class="form-group">
        <Cell title="性别" class="gender-cell">
          <template #right-icon>
            <RadioGroup v-model="form.gender" direction="horizontal">
              <Radio name="male">男</Radio>
              <Radio name="female">女</Radio>
            </RadioGroup>
          </template>
        </Cell>
      </CellGroup>
      
      <!-- 出生日期 -->
      <CellGroup inset class="form-group">
        <Cell 
          title="出生日期" 
          :value="dateText || '请选择日期'"
          :class="{ 'placeholder': !dateText }"
          is-link
          @click="showDatePicker = true"
        />
      </CellGroup>
      
      <!-- 出生时间 -->
      <CellGroup inset class="form-group">
        <Cell 
          title="出生时间" 
          :value="timeText"
          is-link
          @click="showTimePicker = true"
        />
        <div class="time-tip">
          <Icon name="info-o" size="14" />
          <span>不知道时间可选择"未知"，时柱将按未提供处理</span>
        </div>
      </CellGroup>
      
      <!-- 出生地 -->
      <CellGroup inset class="form-group">
        <Cell 
          title="省份" 
          :value="form.province || '请选择省份'"
          :class="{ 'placeholder': !form.province }"
          is-link
          @click="showProvincePicker = true"
        />
        <Cell 
          v-if="form.province"
          title="城市" 
          :value="form.city || '请选择城市'"
          :class="{ 'placeholder': !form.city }"
          is-link
          @click="showCityPicker = true"
        />
      </CellGroup>
      
      <!-- 提交按钮 -->
      <div class="submit-btn">
        <Button 
          round 
          block 
          type="primary" 
          native-type="submit"
          :loading="loading"
          size="large"
        >
          开始分析
        </Button>
      </div>
    </Form>
    
    <!-- 日期选择器 -->
    <Popup v-model:show="showDatePicker" position="bottom">
      <DatetimePicker
        v-model="dateValue"
        type="date"
        title="选择出生日期"
        :min-date="minDate"
        :max-date="maxDate"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </Popup>
    
    <!-- 时间选择器 -->
    <Popup v-model:show="showTimePicker" position="bottom">
      <div class="time-picker-header">
        <span>选择出生时间</span>
        <Button size="small" type="primary" @click="onTimeUnknown">未知</Button>
      </div>
      <DatetimePicker
        v-model="timeValue"
        type="time"
        title="选择出生时间"
        @confirm="onTimeConfirm"
        @cancel="showTimePicker = false"
      />
    </Popup>
    
    <!-- 省份选择器 -->
    <Popup v-model:show="showProvincePicker" position="bottom">
      <Picker
        :columns="provinceColumns"
        title="选择省份"
        @confirm="onProvinceConfirm"
        @cancel="showProvincePicker = false"
      />
    </Popup>
    
    <!-- 城市选择器 -->
    <Popup v-model:show="showCityPicker" position="bottom">
      <Picker
        :columns="cityColumns"
        title="选择城市"
        @confirm="onCityConfirm"
        @cancel="showCityPicker = false"
      />
    </Popup>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
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

// 日期选择
const showDatePicker = ref(false)
const minDate = new Date(1900, 0, 1)
const maxDate = new Date()
const dateValue = ref(new Date(form.value.year, form.value.month - 1, form.value.day))

const dateText = computed(() => {
  return `${form.value.year}年${form.value.month}月${form.value.day}日`
})

const onDateConfirm = (value) => {
  form.value.year = value.getFullYear()
  form.value.month = value.getMonth() + 1
  form.value.day = value.getDate()
  showDatePicker.value = false
}

// 时间选择
const showTimePicker = ref(false)
const timeValue = ref(new Date(2020, 0, 1, 12, 0))

const timeText = computed(() => {
  if (form.value.hour === null) return '未知'
  return `${form.value.hour.toString().padStart(2, '0')}:${form.value.minute.toString().padStart(2, '0')}`
})

const onTimeConfirm = (value) => {
  const [hours, minutes] = value.split(':').map(Number)
  form.value.hour = hours
  form.value.minute = minutes
  showTimePicker.value = false
}

const onTimeUnknown = () => {
  form.value.hour = null
  form.value.minute = 0
  showTimePicker.value = false
}

// 省市选择
const showProvincePicker = ref(false)
const showCityPicker = ref(false)

const provinceColumns = computed(() => {
  return Object.keys(cityData).map(province => ({
    text: province,
    value: province
  }))
})

const cityColumns = computed(() => {
  if (!form.value.province) return []
  const cities = cityData[form.value.province] || []
  return cities.map(city => ({
    text: city,
    value: city
  }))
})

const onProvinceConfirm = ({ selectedOptions }) => {
  form.value.province = selectedOptions[0].value
  form.value.city = ''
  showProvincePicker.value = false
}

const onCityConfirm = ({ selectedOptions }) => {
  form.value.city = selectedOptions[0].value
  showCityPicker.value = false
}

// 提交
const onSubmit = () => {
  if (!form.value.province || !form.value.city) {
    // 如果没有选择城市，使用默认值
    if (!form.value.province) form.value.province = '北京市'
    if (!form.value.city) form.value.city = '北京市'
  }
  
  emit('submit', { ...form.value })
}
</script>

<style scoped>
.form-container {
  padding: 16px;
}

.form-header {
  text-align: center;
  margin-bottom: 24px;
}

.form-header h2 {
  margin: 0 0 8px;
  font-size: 24px;
  color: #333;
}

.subtitle {
  margin: 0;
  color: #999;
  font-size: 14px;
}

.form-group {
  margin-bottom: 12px;
}

.gender-cell :deep(.van-cell__value) {
  flex: 2;
}

.placeholder {
  color: #999;
}

.time-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  color: #999;
  font-size: 12px;
  background: #f5f5f5;
}

.time-picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
}

.submit-btn {
  margin-top: 32px;
  padding: 0 16px;
}
</style>
