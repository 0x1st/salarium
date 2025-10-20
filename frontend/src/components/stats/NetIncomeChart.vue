<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { initChart, baseGrid, monthsToLabels, axisCurrencyFormatter, gradient, palette, currencyFormatter, responsiveResize } from '../../utils/charts'

const props = defineProps({
  data: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
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
    title: { text: '实际到手金额月度趋势', left: 'center' },
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
  <div class="chart" ref="el" style="height: 360px; width: 100%"></div>
</template>
