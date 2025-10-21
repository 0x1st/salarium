<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { initChart, baseGrid, axisCurrencyFormatter, currencyFormatter, responsiveResize } from '../../utils/charts'

const props = defineProps({
  points: { type: Array, default: () => [] },
  title: { type: String, default: '养老/医疗/公积金累计曲线' },
  note: { type: String, default: '' },
})

const el = ref(null)
let chart
let cleanupResize

function render() {
  if (!el.value) return
  if (!chart) chart = initChart(el.value)
  const labels = props.points.map(p => `${p.month}月`)

  chart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (v) => currencyFormatter(v) },
    legend: { bottom: 8 },
    grid: baseGrid(),
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value', axisLabel: { formatter: axisCurrencyFormatter } },
    series: [
      { name: '养老累计', type: 'line', smooth: true, data: props.points.map(p => p.pension_cumulative) },
      { name: '医疗累计', type: 'line', smooth: true, data: props.points.map(p => p.medical_cumulative) },
      { name: '公积金累计', type: 'line', smooth: true, data: props.points.map(p => p.housing_fund_cumulative) },
    ],
  })
}

onMounted(() => { render(); cleanupResize = responsiveResize(chart) })
watch(() => props.points, render)

onBeforeUnmount(() => { cleanupResize && cleanupResize(); chart && chart.dispose && chart.dispose() })
</script>

<template>
  <div>
    <div class="chart" ref="el" style="height: 360px; width: 100%"></div>
    <div class="chart-footer">
      <div class="chart-title">{{ title }}</div>
      <div v-if="note" class="chart-note">{{ note }}</div>
    </div>
  </div>
</template>

<style scoped>
.chart-footer { display:flex; gap:8px; align-items:center; justify-content: center; padding: 8px 0 4px; color:#475569; flex-wrap: wrap }
.chart-title { font-weight: 600 }
.chart-note { font-size:12px; color:#94a3b8 }
</style>
