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

// 检测移动端
function isMobile() {
  return window.innerWidth < 768 || /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

async function generateImage() {
  const mobile = isMobile()
  // 移动端用 810×1080（0.75x），电脑端用 1080×1440
  const scale = mobile ? 0.75 : 1
  const W = Math.round(1080 * scale)
  const H = Math.round(1440 * scale)
  const S = scale // 缩放系数

  const canvas = document.createElement('canvas')
  canvas.width = W
  canvas.height = H
  const ctx = canvas.getContext('2d')

  // === 1. 背景渐变 ===
  const grad = ctx.createLinearGradient(0, 0, W, H)
  grad.addColorStop(0, '#F0F9FF')
  grad.addColorStop(0.25, '#E8F4FD')
  grad.addColorStop(0.5, '#FDFCF8')
  grad.addColorStop(0.75, '#F0FFF4')
  grad.addColorStop(1, '#E8FDF5')
  ctx.fillStyle = grad
  ctx.fillRect(0, 0, W, H)

  // 装饰圆
  ctx.save()
  const g1 = ctx.createRadialGradient(W - 30 * S, -20 * S, 0, W - 30 * S, -20 * S, 200 * S)
  g1.addColorStop(0, 'rgba(142,197,252,0.12)')
  g1.addColorStop(1, 'transparent')
  ctx.fillStyle = g1
  ctx.beginPath()
  ctx.arc(W - 30 * S, -20 * S, 200 * S, 0, Math.PI * 2)
  ctx.fill()
  ctx.restore()
  ctx.save()
  const g2 = ctx.createRadialGradient(-20 * S, H * 0.7, 0, -20 * S, H * 0.7, 180 * S)
  g2.addColorStop(0, 'rgba(168,230,207,0.12)')
  g2.addColorStop(1, 'transparent')
  ctx.fillStyle = g2
  ctx.beginPath()
  ctx.arc(-20 * S, H * 0.7, 180 * S, 0, Math.PI * 2)
  ctx.fill()
  ctx.restore()

  // === 2. 顶部 8%：姓名 + 天赋档案 ===
  ctx.textBaseline = 'middle'
  const topY = H * 0.04
  ctx.font = `bold ${36 * S}px "PingFang SC","Microsoft YaHei",sans-serif`
  ctx.textAlign = 'right'
  ctx.fillStyle = '#1A202C'
  const nameX = W * 0.47
  ctx.fillText(displayName.value, nameX, topY)

  // 竖线分隔
  ctx.fillStyle = 'rgba(142,197,252,0.5)'
  ctx.fillRect(nameX + 8 * S, topY - 12 * S, 2.5 * S, 24 * S)

  // 天赋档案
  ctx.font = `500 ${28 * S}px "PingFang SC","Microsoft YaHei",sans-serif`
  ctx.textAlign = 'left'
  ctx.fillStyle = '#718096'
  ctx.fillText('天赋档案', nameX + 16 * S, topY)

  // === 3. C位 72%：左侧标签 + 右侧头像 ===
  const centerStartY = H * 0.10
  const centerH = H * 0.72
  const tagColor = props.traitInfo.color || '#8EC5FC'
  const emojis = ['✨', '🌟', '💫', '🔥', '💎']
  const tags = displayTags.value

  // 左侧标签区域
  const tagStartX = W * 0.08
  const tagAreaW = W * 0.50
  const tagH = 70 * S
  const tagGap = 18 * S
  const totalTagsH = tags.length * tagH + (tags.length - 1) * tagGap
  const tagStartY = centerStartY + (centerH - totalTagsH) / 2

  tags.forEach((tag, i) => {
    const y = tagStartY + i * (tagH + tagGap)
    // 标签背景
    ctx.save()
    ctx.shadowColor = 'rgba(0,0,0,0.04)'
    ctx.shadowBlur = 10 * S
    ctx.shadowOffsetY = 2 * S
    ctx.fillStyle = 'rgba(255,255,255,0.9)'
    roundRect(ctx, tagStartX, y, tagAreaW, tagH, 12 * S)
    ctx.fill()
    ctx.restore()
    // 左边色条
    ctx.fillStyle = tagColor
    roundRect(ctx, tagStartX, y, 4 * S, tagH, [2 * S, 0, 0, 2 * S])
    ctx.fill()
    // emoji
    ctx.font = `${30 * S}px sans-serif`
    ctx.textAlign = 'left'
    ctx.textBaseline = 'middle'
    ctx.fillText(emojis[i] || '✨', tagStartX + 22 * S, y + tagH / 2)
    // 文字
    ctx.font = `bold ${24 * S}px "PingFang SC","Microsoft YaHei",sans-serif`
    ctx.fillStyle = '#2D3748'
    ctx.fillText(tag, tagStartX + 62 * S, y + tagH / 2)
  })

  // 右侧头像区域
  const avLeft = W * 0.62
  const avTop = centerStartY + centerH * 0.02
  const avW = W * 0.34
  const avH = H * 0.55

  const avatarImg = await loadImage(avatarFullUrl.value)
  if (avatarImg) {
    // 计算等比缩放
    const imgRatio = avatarImg.width / avatarImg.height
    let drawW = avW, drawH = avH
    if (imgRatio > drawW / drawH) {
      drawH = drawW / imgRatio
    } else {
      drawW = drawH * imgRatio
    }
    const drawX = avLeft + (avW - drawW) / 2
    const drawY = avTop + (avH - drawH) / 2 + H * 0.02

    ctx.save()
    // 圆形裁剪
    const cx = avLeft + avW / 2
    const cy = avTop + avH / 2
    const cr = Math.min(avW, avH) * 0.47
    ctx.beginPath()
    ctx.arc(cx, cy, cr, 0, Math.PI * 2)
    ctx.closePath()
    ctx.shadowColor = 'rgba(0,0,0,0.08)'
    ctx.shadowBlur = 24 * S
    ctx.shadowOffsetY = 4 * S
    ctx.fill()
    ctx.clip()
    ctx.drawImage(avatarImg, drawX, drawY, drawW, drawH)
    ctx.restore()
  }

  // 昵称标签（圆形下方）
  const nickY = avTop + avH + 10 * S
  ctx.save()
  ctx.shadowColor = 'rgba(0,0,0,0.03)'
  ctx.shadowBlur = 6 * S
  ctx.fillStyle = 'rgba(255,255,255,0.85)'
  const nickTextW = ctx.measureText(displayName.value).width + 36 * S
  roundRect(ctx, avLeft + (avW - nickTextW) / 2, nickY, nickTextW, 40 * S, 20 * S)
  ctx.fill()
  ctx.restore()
  ctx.font = `bold ${24 * S}px "PingFang SC","Microsoft YaHei",sans-serif`
  ctx.fillStyle = '#2D3748'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(displayName.value, avLeft + avW / 2, nickY + 20 * S)

  // === 4. 底部 20%：特质 + 二维码 ===
  const bottomY = H * 0.82
  const bottomH = H * 0.18

  // 特质文字
  ctx.font = `400 ${22 * S}px "PingFang SC","Microsoft YaHei",sans-serif`
  ctx.fillStyle = '#4A5568'
  ctx.textAlign = 'left'
  ctx.textBaseline = 'middle'
  const descX = W * 0.08
  const descW = W * 0.60
  const descY = bottomY + bottomH * 0.30
  wrapText(ctx, props.traitDescription || '', descX, descY, descW, 26 * S, 1.6)

  // 二维码区域
  const qrSize = 100 * S
  const qrX = W - qrSize - W * 0.08
  const qrY = bottomY + (bottomH - qrSize - 30 * S) / 2

  // 尝试加载二维码
  const qrUrl = import.meta.env.PROD
    ? window.location.pathname.replace(/\/[^/]*$/, '/') + 'qrcode.jpg'
    : '/qrcode.jpg'
  const qrImg = await loadImage(qrUrl)

  if (qrImg) {
    ctx.save()
    ctx.shadowColor = 'rgba(142,197,252,0.15)'
    ctx.shadowBlur = 8 * S
    ctx.fillStyle = '#fff'
    roundRect(ctx, qrX, qrY, qrSize, qrSize, 8 * S)
    ctx.fill()
    ctx.clip()
    ctx.drawImage(qrImg, qrX, qrY, qrSize, qrSize)
    ctx.restore()
  } else {
    // 二维码加载失败时画一个占位方块
    ctx.fillStyle = '#E2E8F0'
    roundRect(ctx, qrX, qrY, qrSize, qrSize, 8 * S)
    ctx.fill()
    ctx.fillStyle = '#94A3B8'
    ctx.font = `14 * S}px sans-serif`
    ctx.textAlign = 'center'
    ctx.fillText('QR', qrX + qrSize / 2, qrY + qrSize / 2)
  }

  // 扫码文字
  ctx.font = `400 ${14 * S}px "PingFang SC","Microsoft YaHei",sans-serif`
  ctx.fillStyle = '#A0AEC0'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'top'
  ctx.fillText('扫码测测你的隐藏天赋', qrX + qrSize / 2, qrY + qrSize + 8 * S)

  return canvas.toDataURL('image/png')
}

// === 工具函数 ===
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
  if (!text) return
  const chars = text.split('')
  let line = ''
  let lineY = y
  for (const ch of chars) {
    const testLine = line + ch
    if (ctx.measureText(testLine).width > maxWidth && line.length > 0) {
      ctx.fillText(line, x, lineY)
      line = ch
      lineY += fontSize * lineHeight
    } else {
      line = testLine
    }
  }
  if (line) ctx.fillText(line, x, lineY)
}

defineExpose({ generateImage })
</script>
