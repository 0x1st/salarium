<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { initChart, baseGrid, monthsToLabels, axisCurrencyFormatter, gradient, currencyFormatter, responsiveResize } from '../../utils/charts'
import ChartCard from './ChartCard.vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  title: { type: String, default: '应发 vs 实际到手' },
  note: { type: String, default: '应发不包含餐补与三节福利' },
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
    legend: { data: ['应发工资', '实际到手金额'], bottom: 8, left: 'center' },
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
  <ChartCard :title="title" :note="note">
    <div class="chart" ref="el" style="height: 320px; width: 100%"></div>
  </ChartCard>
</template>

<style scoped>
</style>
