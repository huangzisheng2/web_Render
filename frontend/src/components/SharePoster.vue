<template>
  <div style="display:none"></div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { getQVersionAvatar, getFullAvatarUrl } from '../data/dayMasterData'

const props = defineProps({
  userInfo: { type: Object, default: () => ({}) },
  dayMaster: { type: String, default: '甲' },
  traitInfo: { type: Object, default: () => ({}) },
  talentTags: { type: Array, default: () => [] },
  traitDescription: { type: String, default: '' }
})

// 预加载 html2canvas
const html2canvasReady = ref(false)
let _html2canvasFn = null

onMounted(async () => {
  try {
    const mod = await import('html2canvas')
    _html2canvasFn = mod.default
    html2canvasReady.value = true
    console.log('[Share] html2canvas loaded')
  } catch (e) {
    console.error('[Share] html2canvas load failed:', e)
  }
})

const displayName = computed(() => props.userInfo?.name || '我')
const avatarUrl = computed(() => {
  return getQVersionAvatar(props.dayMaster, props.userInfo?.gender || 'male')
})
const avatarFullUrl = computed(() => {
  return getFullAvatarUrl(props.dayMaster, props.userInfo?.gender || 'male')
})
const displayTags = computed(() => {
  const tags = props.talentTags?.length ? props.talentTags : ['天赋探索者']
  return tags.slice(0, 5)
})
const tagEmojis = ['✨', '🌟', '💫', '🔥', '💎']

async function generateImage() {
  if (!_html2canvasFn) {
    console.error('[Share] html2canvas not loaded yet')
    return null
  }

  const container = document.createElement('div')
  container.style.cssText = [
    'position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);',
    'width:1080px;height:1440px;z-index:99999;',
    'background:linear-gradient(160deg,#F0F9FF 0%,#E8F4FD 25%,#FDFCF8 50%,#F0FFF4 75%,#E8FDF5 100%);',
    'display:flex;flex-direction:column;overflow:hidden;',
    'font-family:"PingFang SC","Microsoft YaHei","Helvetica Neue",Arial,sans-serif;',
    'box-shadow:0 0 0 9999px rgba(0,0,0,0.5);'
  ].join('')

  const tagHtml = displayTags.value.map((tag, i) => {
    const color = props.traitInfo.color || '#8EC5FC'
    return `<div style="display:inline-flex;align-items:center;gap:12px;padding:18px 28px;background:rgba(255,255,255,0.85);border-radius:16px;border-left:5px solid ${color};box-shadow:0 4px 16px rgba(0,0,0,0.04);"><span style="font-size:36px;line-height:1;">${tagEmojis[i] || '✨'}</span><span style="font-size:30px;font-weight:600;color:#2D3748;">${tag}</span></div>`
  }).join('')

  container.innerHTML = [
    `<div style="height:144px;display:flex;align-items:center;justify-content:center;gap:16px;padding:0 60px;"><span style="font-size:42px;font-weight:700;color:#1A202C;letter-spacing:2px;">${displayName.value}</span><span style="font-size:32px;font-weight:500;color:#718096;letter-spacing:4px;padding-left:20px;border-left:3px solid;border-image:linear-gradient(180deg,#8EC5FC,#A8E6CF) 1;">天赋档案</span></div>`,
    `<div style="flex:1;display:flex;align-items:center;justify-content:space-between;padding:40px 80px;"><div style="display:flex;flex-direction:column;gap:24px;flex:1;">${tagHtml}</div><div style="display:flex;flex-direction:column;align-items:center;gap:20px;margin-left:40px;"><img src="${avatarFullUrl.value}" crossorigin="anonymous" style="width:380px;height:420px;object-fit:contain;" onerror="this.style.display='none'" /><span style="font-size:32px;font-weight:600;color:#2D3748;padding:8px 24px;background:rgba(255,255,255,0.7);border-radius:20px;letter-spacing:2px;">${displayName.value}</span></div></div>`,
    `<div style="height:288px;display:flex;align-items:center;justify-content:space-between;padding:0 80px 40px;"><span style="flex:1;font-size:28px;line-height:1.6;color:#4A5568;padding-right:40px;">${props.traitDescription || ''}</span><div style="display:flex;flex-direction:column;align-items:center;gap:12px;"><img src="/qrcode.jpg" crossorigin="anonymous" style="width:140px;height:140px;border-radius:12px;border:3px solid rgba(142,197,252,0.3);" onerror="this.style.display='none'" /><span style="font-size:18px;color:#A0AEC0;white-space:nowrap;">扫码测测你的隐藏天赋</span></div></div>`
  ].join('')

  document.body.appendChild(container)

  try {
    await new Promise(resolve => setTimeout(resolve, 300))

    console.log('[Share] generating canvas...')
    const canvas = await _html2canvasFn(container, {
      width: 1080,
      height: 1440,
      scale: 1,
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#F0F9FF',
      logging: false,
      imageTimeout: 30000
    })
    console.log('[Share] canvas generated')

    const dataUrl = canvas.toDataURL('image/png')
    return dataUrl
  } catch (e) {
    console.error('[Share] html2canvas error:', e.message)
    return null
  } finally {
    if (container.parentNode) {
      document.body.removeChild(container)
    }
  }
}

defineExpose({ generateImage })
</script>
