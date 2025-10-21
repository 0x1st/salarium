<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { initChart, baseGrid, axisCurrencyFormatter, currencyFormatter, responsiveResize } from '../../utils/charts'
import ChartCard from './ChartCard.vue'

const props = defineProps({
  data: { type: Array, default: () => [] }, // IncomeComposition[]
  title: { type: String, default: '各收入项分月堆叠面积' },
  note: { type: String, default: '' },
})

const el = ref(null)
let chart
let cleanupResize

function byMonth() {
  const map = new Map()
  for (const r of props.data) {
    const key = `${r.year}-${r.month}`
    if (!map.has(key)) {
      map.set(key, { year: r.year, month: r.month, base: 0, perf: 0, allow: 0 })
    }
    const v = map.get(key)
    v.base += r.base_salary || 0
    v.perf += r.performance_salary || 0
    v.allow += (r.high_temp_allowance || 0) + (r.low_temp_allowance || 0) + (r.meal_allowance || 0) + (r.computer_allowance || 0)
  }
  return Array.from(map.values()).sort((a, b) => (a.year - b.year) || (a.month - b.month))
}

function render() {
  if (!el.value) return
  if (!chart) chart = initChart(el.value)
  const rows = byMonth()

  chart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (v) => currencyFormatter(v) },
    legend: { bottom: 8, left: 'center' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: rows.map(r => `${r.month}月`) },
    yAxis: { type: 'value', axisLabel: { formatter: axisCurrencyFormatter } },
    series: [
      { name: '基本工资', type: 'line', stack: 'total', areaStyle: {}, data: rows.map(r => r.base) },
      { name: '绩效工资', type: 'line', stack: 'total', areaStyle: {}, data: rows.map(r => r.perf) },
      { name: '补贴', type: 'line', stack: 'total', areaStyle: {}, data: rows.map(r => r.allow) },
    ],
  })
}

onMounted(() => { render(); cleanupResize = responsiveResize(chart) })
watch(() => props.data, render)

onBeforeUnmount(() => { cleanupResize && cleanupResize(); chart && chart.dispose && chart.dispose() })
</script>

<template>
  <ChartCard :title="title" :note="note">
    <div class="chart" ref="el" style="height: 320px; width: 100%"></div>
  </ChartCard>
</template>

<style scoped>
</style>
