import * as echarts from 'echarts'
import { formatCurrency } from './number'

// Register a unified theme for all charts
const theme = {
  color: ['#409EFF', '#67C23A', '#E6A23C', '#8e44ad', '#1abc9c', '#F56C6C', '#909399'],
  textStyle: {
    fontFamily: 'Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, "Noto Sans", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif',
    fontSize: 12,
    color: '#334155',
  },
  grid: { left: '3%', right: '3%', bottom: '8%', top: '12%', containLabel: true },
  tooltip: {
    backgroundColor: 'rgba(17,24,39,0.9)',
    borderWidth: 0,
    textStyle: { color: '#fff', fontSize: 12 },
    extraCssText: 'box-shadow:0 6px 18px rgba(0,0,0,0.2); border-radius:8px; padding:10px 12px;',
  },
  legend: {
    top: 28,
    textStyle: { color: '#475569' },
  },
  categoryAxis: {
    axisLine: { lineStyle: { color: '#e2e8f0' } },
    axisTick: { alignWithLabel: true, lineStyle: { color: '#e2e8f0' } },
    axisLabel: { color: '#64748b' },
    splitLine: { show: false },
  },
  valueAxis: {
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#64748b' },
    splitLine: { lineStyle: { color: '#e5e7eb', type: 'dashed' } },
  },
}

if (!echarts.themes || !echarts.themes.salarium) {
  echarts.registerTheme('salarium', theme)
}

export function initChart(el) {
  if (!el) return null
  return echarts.init(el, 'salarium')
}

export function baseGrid() {
  return { left: '3%', right: '3%', bottom: '8%', top: '12%', containLabel: true }
}

export function currencyFormatter(val) {
  return formatCurrency(val, { decimals: 2 })
}

export function axisCurrencyFormatter(value) {
  return formatCurrency(value, { decimals: 2 })
}

export function monthsToLabels(points) {
  return points.map(p => `${p.month}月`)
}

export function responsiveResize(instance) {
  if (!instance) return () => {}
  const handler = () => instance.resize()
  window.addEventListener('resize', handler)
  return () => window.removeEventListener('resize', handler)
}

export const palette = {
  primary: '#409EFF',
  success: '#67C23A',
  warning: '#E6A23C',
  danger: '#F56C6C',
  info: '#909399',
  blue: '#409EFF',
  green: '#67C23A',
  orange: '#E6A23C',
  purple: '#8e44ad',
  teal: '#1abc9c',
}

export function gradient(color1, color2) {
  return new echarts.graphic.LinearGradient(0, 0, 0, 1, [
    { offset: 0, color: color1 },
    { offset: 1, color: color2 },
  ])
}
