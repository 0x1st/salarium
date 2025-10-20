<script setup>
import { ref, onMounted, watch, computed, onBeforeUnmount } from 'vue'
import { initChart, baseGrid, gradient, currencyFormatter, responsiveResize } from '../../utils/charts'

const props = defineProps({
  data: { type: Array, default: () => [] }, // IncomeComposition[]
})

const el = ref(null)
let chart
let cleanupResize

const summary = computed(() => {
  // Aggregate across list
  const agg = { base: 0, perf: 0, allow: 0, benefits: 0, other: 0 }
  for (const r of props.data) {
    agg.base += r.base_salary || 0
    agg.perf += r.performance_salary || 0
    const allow = (r.high_temp_allowance || 0) + (r.low_temp_allowance || 0) + (r.computer_allowance || 0)
    agg.allow += allow
    agg.benefits += r.non_cash_benefits || 0
    agg.other += r.other_income || 0
  }
  return agg
})

function render() {
  if (!el.value) return
  if (!chart) chart = initChart(el.value)

  const s = summary.value
  const seriesData = [
    { value: s.base, name: '基本工资' },
    { value: s.perf, name: '绩效工资' },
    { value: s.allow, name: '补贴' },
    { value: s.benefits, name: '福利' },
    { value: s.other, name: '其他收入' },
  ]

  chart.setOption({
    title: { text: '收入构成环图', left: 'center' },
    tooltip: {
      trigger: 'item',
      formatter: (p) => `${p.name}: ${currencyFormatter(p.value)} (${p.percent}%)`,
    },
    legend: { orient: 'vertical', left: 10, top: 'middle' },
    series: [
      {
        type: 'pie',
        name: '构成',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        data: seriesData,
        label: { formatter: '{b}: {d}%' },
      },
    ],
  })
}

onMounted(() => { render(); cleanupResize = responsiveResize(chart) })
watch(() => props.data, render)

onBeforeUnmount(() => { cleanupResize && cleanupResize(); chart && chart.dispose && chart.dispose() })
</script>

<template>
  <div class="chart" ref="el" style="height: 360px; width: 100%"></div>
</template>
