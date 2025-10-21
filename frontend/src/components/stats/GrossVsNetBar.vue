<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { initChart, baseGrid, monthsToLabels, axisCurrencyFormatter, gradient, currencyFormatter, responsiveResize } from '../../utils/charts'

const props = defineProps({
  data: { type: Array, default: () => [] },
  title: { type: String, default: '应发 vs 实际到手' },
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
  const gross = points.map(p => p.gross_income)
  const net = points.map(p => p.net_income)

  chart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (v) => currencyFormatter(v) },
    legend: { data: ['应发工资', '实际到手金额'], bottom: 8 },
    grid: baseGrid(),
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value', axisLabel: { formatter: axisCurrencyFormatter } },
    series: [
      {
        name: '应发工资',
        type: 'bar',
        stack: 'income',
        data: gross,
        itemStyle: { color: gradient('#409EFF', '#66b1ff') },
        barWidth: '40%',
      },
      {
        name: '实际到手金额',
        type: 'bar',
        stack: 'income',
        data: net,
        itemStyle: { color: gradient('#67C23A', '#A3E09E') },
        barWidth: '40%',
      },
    ],
  })
}

onMounted(() => { render(); cleanupResize = responsiveResize(chart) })
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
