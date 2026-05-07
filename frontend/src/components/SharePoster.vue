<template>
  <div style="display:none"></div>
</template>

<script setup>
import { computed } from 'vue'
import { getFullAvatarUrl } from '../data/dayMasterData'

const props = defineProps({
  userInfo: { type: Object, default: () => ({}) },
  dayMaster: { type: String, default: '甲' },
  traitInfo: { type: Object, default: () => ({}) },
  talentTags: { type: Array, default: () => [] },
  traitDescription: { type: String, default: '' }
})

const displayName = computed(() => props.userInfo?.name || '我')
const avatarFullUrl = computed(() => getFullAvatarUrl(props.dayMaster, props.userInfo?.gender || 'male'))
const displayTags = computed(() => {
  const tags = props.talentTags?.length ? props.talentTags : ['天赋探索者']
  return tags.slice(0, 5)
})

const W = 1080
const H = 1440

async function generateImage() {
  const canvas = document.createElement('canvas')
  canvas.width = W
  canvas.height = H
  const ctx = canvas.getContext('2d')

  // 1. 背景渐变
  const grad = ctx.createLinearGradient(0, 0, W, H)
  grad.addColorStop(0, '#F0F9FF')
  grad.addColorStop(0.25, '#E8F4FD')
  grad.addColorStop(0.5, '#FDFCF8')
  grad.addColorStop(0.75, '#F0FFF4')
  grad.addColorStop(1, '#E8FDF5')
  ctx.fillStyle = grad
  ctx.fillRect(0, 0, W, H)

  // 装饰大圆
  ctx.save()
  const g1 = ctx.createRadialGradient(W - 50, -50, 0, W - 50, -50, 250)
  g1.addColorStop(0, 'rgba(142,197,252,0.12)')
  g1.addColorStop(1, 'transparent')
  ctx.fillStyle = g1
  ctx.beginPath()
  ctx.arc(W - 50, -50, 250, 0, Math.PI * 2)
  ctx.fill()

  const g2 = ctx.createRadialGradient(-30, 900, 0, -30, 900, 220)
  g2.addColorStop(0, 'rgba(168,230,207,0.12)')
  g2.addColorStop(1, 'transparent')
  ctx.fillStyle = g2
  ctx.beginPath()
  ctx.arc(-30, 900, 220, 0, Math.PI * 2)
  ctx.fill()
  ctx.restore()

  // 2. 顶部：姓名 + 天赋档案
  ctx.textBaseline = 'middle'
  ctx.textAlign = 'center'

  const nameColor = '#1A202C'
  const titleColor = '#718096'
  ctx.font = 'bold 44px "PingFang SC","Microsoft YaHei",sans-serif'
  ctx.fillStyle = nameColor
  ctx.fillText(displayName.value, W / 2 - 10, 70)

  ctx.font = '500 32px "PingFang SC","Microsoft YaHei",sans-serif'
  ctx.fillStyle = titleColor
  ctx.fillText('天赋档案', W / 2 + 130, 70)

  // 分隔线
  ctx.save()
  const lineGrad = ctx.createLinearGradient(W / 2 + 90, 60, W / 2 + 92, 80)
  lineGrad.addColorStop(0, '#8EC5FC')
  lineGrad.addColorStop(1, '#A8E6CF')
  ctx.fillStyle = lineGrad
  ctx.fillRect(W / 2 + 92, 55, 3, 30)
  ctx.restore()

  // 3. 中间：左侧标签 + 右侧头像
  const tagColor = props.traitInfo.color || '#8EC5FC'
  const emojis = ['✨', '🌟', '💫', '🔥', '💎']
  const tags = displayTags.value
  const startY = 200
  const tagH = 82
  const gap = 22

  tags.forEach((tag, i) => {
    const y = startY + i * (tagH + gap)
    // 标签背景
    ctx.save()
    ctx.shadowColor = 'rgba(0,0,0,0.04)'
    ctx.shadowBlur = 12
    ctx.shadowOffsetY = 2
    ctx.fillStyle = 'rgba(255,255,255,0.88)'
    roundRect(ctx, 90, y, 480, tagH, 16)
    ctx.fill()
    ctx.restore()

    // 左边色条
    ctx.fillStyle = tagColor
    roundRect(ctx, 90, y, 5, tagH, [2, 0, 0, 2])
    ctx.fill()

    // emoji
    ctx.font = '36px sans-serif'
    ctx.textAlign = 'left'
    ctx.textBaseline = 'middle'
    ctx.fillText(emojis[i] || '✨', 120, y + tagH / 2)

    // 标签文字
    ctx.font = 'bold 30px "PingFang SC","Microsoft YaHei",sans-serif'
    ctx.fillStyle = '#2D3748'
    ctx.fillText(tag, 175, y + tagH / 2)
  })

  // 右侧头像（加载图片）
  const avatarImg = await loadImage(avatarFullUrl.value)
  if (avatarImg) {
    const avX = 660
    const avY = 200
    const avW = 340
    const avH = 400
    ctx.save()
    ctx.shadowColor = 'rgba(0,0,0,0.06)'
    ctx.shadowBlur = 20
    ctx.shadowOffsetY = 4
    ctx.drawImage(avatarImg, avX, avY, avW, avH)
    ctx.restore()
  }

  // 昵称标签
  const nickY = 618
  ctx.save()
  ctx.shadowColor = 'rgba(0,0,0,0.04)'
  ctx.shadowBlur = 8
  ctx.fillStyle = 'rgba(255,255,255,0.75)'
  roundRect(ctx, 720, nickY, 220, 50, 25)
  ctx.fill()
  ctx.restore()

  ctx.font = 'bold 30px "PingFang SC","Microsoft YaHei",sans-serif'
  ctx.fillStyle = '#2D3748'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(displayName.value, 830, nickY + 25)

  // 4. 底部：特质 + 二维码
  ctx.font = '400 28px "PingFang SC","Microsoft YaHei",sans-serif'
  ctx.fillStyle = '#4A5568'
  ctx.textAlign = 'left'
  ctx.textBaseline = 'middle'
  const desc = props.traitDescription || ''
  wrapText(ctx, desc, 90, 1280, 550, 42, 1.5)

  // 二维码
  const qrImg = await loadImage('/qrcode.jpg')  // dev 环境
  // GitHub Pages 部署时可能需要 ./qrcode.jpg
  let qrSrc = '/qrcode.jpg'
  if (import.meta.env.PROD) {
    qrSrc = window.location.pathname.replace(/\/[^/]*$/, '') + '/qrcode.jpg'
  }
  const qrFinalImg = qrImg || await loadImage(qrSrc)
  if (qrFinalImg) {
    const qrX = 780
    const qrY = 1220
    const qrSize = 140
    ctx.save()
    ctx.shadowColor = 'rgba(142,197,252,0.15)'
    ctx.shadowBlur = 8
    roundRect(ctx, qrX, qrY, qrSize, qrSize, 10)
    ctx.fillStyle = '#fff'
    ctx.fill()
    ctx.clip()
    ctx.drawImage(qrFinalImg, qrX, qrY, qrSize, qrSize)
    ctx.restore()
  }

  // 扫码文字
  ctx.font = '400 18px "PingFang SC","Microsoft YaHei",sans-serif'
  ctx.fillStyle = '#A0AEC0'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'top'
  ctx.fillText('扫码测测你的隐藏天赋', 850, 1370)

  return canvas.toDataURL('image/png')
}

// 工具函数
function roundRect(ctx, x, y, w, h, r) {
  if (!Array.isArray(r)) r = [r, r, r, r]
  ctx.beginPath()
  ctx.moveTo(x + r[0], y)
  ctx.lineTo(x + w - r[1], y)
  ctx.quadraticCurveTo(x + w, y, x + w, y + r[1])
  ctx.lineTo(x + w, y + h - r[2])
  ctx.quadraticCurveTo(x + w, y + h, x + w - r[2], y + h)
  ctx.lineTo(x + r[3], y + h)
  ctx.quadraticCurveTo(x, y + h, x, y + h - r[3])
  ctx.lineTo(x, y + r[0])
  ctx.quadraticCurveTo(x, y, x + r[0], y)
  ctx.closePath()
}

function loadImage(src) {
  return new Promise((resolve) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => resolve(img)
    img.onerror = () => resolve(null)
    img.src = src
  })
}

function wrapText(ctx, text, x, y, maxWidth, fontSize, lineHeight) {
  const chars = text.split('')
  let line = ''
  let lineY = y
  for (const ch of chars) {
    const testLine = line + ch
    const metrics = ctx.measureText(testLine)
    if (metrics.width > maxWidth && line.length > 0) {
      ctx.fillText(line, x, lineY)
      line = ch
      lineY += fontSize * lineHeight
    } else {
      line = testLine
    }
  }
  if (line) {
    ctx.fillText(line, x, lineY)
  }
}

defineExpose({ generateImage })
</script>
