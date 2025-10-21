<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { initChart, baseGrid, monthsToLabels, axisCurrencyFormatter, gradient, palette, currencyFormatter, responsiveResize } from '../../utils/charts'

const props = defineProps({
  data: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  title: { type: String, default: '实际到手金额月度趋势' },
  note: { type: String, default: '' },
})

const el = ref(null)
let chart
let cleanupResize

function render() {
  if (!el.value) return
  if (!chart) chart = initChart(el.value)
  const points = props.data || []
  const labels = monthsToLabels(points)
  const values = points.map(p => p.net_income)

  chart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (v) => currencyFormatter(v) },
    grid: baseGrid(),
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value', axisLabel: { formatter: axisCurrencyFormatter } },
    series: [
      {
        name: '实际到手金额',
        type: 'line',
        smooth: true,
        data: values,
        symbol: 'circle',
        areaStyle: { color: gradient('#67C23A', '#A3E09E') },
        lineStyle: { color: palette.green, width: 2 },
      },
    ],
  })
}

onMounted(() => {
  render()
  cleanupResize = responsiveResize(chart)
})
watch(() => props.data, render)

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
