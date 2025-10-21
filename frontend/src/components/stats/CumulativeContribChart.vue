<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { initChart, baseGrid, monthsToLabels, axisCurrencyFormatter, currencyFormatter, responsiveResize } from '../../utils/charts'

const props = defineProps({
  points: { type: Array, default: () => [] },
})

const el = ref(null)
let chart
let cleanupResize

function render() {
  if (!el.value) return
  if (!chart) chart = initChart(el.value)
  const labels = props.points.map(p => `${p.month}月`)

  chart.setOption({
    title: { text: '养老/医疗/公积金累计曲线', left: 'center' },
    tooltip: { trigger: 'axis', valueFormatter: (v) => currencyFormatter(v) },
    legend: { top: 8 },
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
  <div class="chart" ref="el" style="height: 360px; width: 100%"></div>
</template>
