<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { initChart, currencyFormatter, responsiveResize } from '../../utils/charts'
import ChartCard from './ChartCard.vue'

const props = defineProps({
  title: { type: String, default: '' },
  data: { type: Array, default: () => [] },
})

const el = ref(null)
let chart
let cleanupResize

function render() {
  if (!el.value) return
  if (!chart) chart = initChart(el.value)
  const seriesData = (props.data || [])
    .filter(d => d && d.value)
    .map(d => ({ name: d.label, value: d.value }))

  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (p) => `${p.name}: ${currencyFormatter(p.value)} (${p.percent}%)`,
    },
    legend: { bottom: 8, left: 'center' },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        data: seriesData,
        label: { formatter: '{b}: {d}%' },
      },
    ],
  })
}

onMounted(() => { render(); cleanupResize = responsiveResize(chart) })
watch(() => props.data, render, { deep: true })

onBeforeUnmount(() => { cleanupResize && cleanupResize(); chart && chart.dispose && chart.dispose() })
</script>

<template>
  <ChartCard :title="title">
    <div class="chart" ref="el" style="height: 320px; width: 100%"></div>
  </ChartCard>
</template>

<style scoped>
</style>
