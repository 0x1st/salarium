<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { initChart, baseGrid, monthsToLabels, axisCurrencyFormatter, gradient, palette, currencyFormatter, responsiveResize } from '../../utils/charts'
import ChartCard from './ChartCard.vue'

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
        areaStyle: { color: gradient(palette.success, '#A3D4BE') },
        lineStyle: { color: palette.success, width: 2 },
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
  <ChartCard :title="title" :note="note">
    <div class="chart" ref="el" style="height: 320px; width: 100%"></div>
  </ChartCard>
</template>

<style scoped>
</style>
