<script setup>
import { ref, onMounted, watch, computed, onBeforeUnmount } from 'vue'
import { initChart, baseGrid, axisCurrencyFormatter, currencyFormatter, responsiveResize } from '../../utils/charts'

const props = defineProps({
  data: { type: Array, default: () => [] }, // expects GrossVsNetMonthly
  title: { type: String, default: '瀑布图：应发 -> 扣除 -> 实际到手' },
  note: { type: String, default: '' },
})

const el = ref(null)
let chart
let cleanupResize

const totals = computed(() => {
  const gross = props.data.reduce((s, p) => s + (p.gross_income || 0), 0)
  const net = props.data.reduce((s, p) => s + (p.net_income || 0), 0)
  const ded = Math.max(gross - net, 0)
  return { gross, net, ded }
})

function render() {
  if (!el.value) return
  if (!chart) chart = initChart(el.value)
  const { gross, net, ded } = totals.value
  const data = [gross, -ded, net]

  chart.setOption({
    grid: baseGrid(),
    xAxis: { type: 'category', data: ['应发工资', '扣除', '实际到手金额'] },
    yAxis: { type: 'value', axisLabel: { formatter: axisCurrencyFormatter } },
    series: [
      {
        type: 'bar',
        data,
        itemStyle: {
          color: (params) => {
            if (params.dataIndex === 1) return '#F56C6C'
            if (params.dataIndex === 2) return '#67C23A'
            return '#409EFF'
          },
        },
        label: {
          show: true,
          position: 'top',
          formatter: (p) => currencyFormatter(Math.abs(p.value)),
        },
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
    <div class="chart" ref="el" style="height: 320px; width: 100%"></div>
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
