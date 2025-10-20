<script setup>
import { ref, onMounted, watch, computed, onBeforeUnmount } from 'vue'
import { initChart, baseGrid, axisCurrencyFormatter, gradient, currencyFormatter, responsiveResize } from '../../utils/charts'

const props = defineProps({
  data: { type: Array, default: () => [] }, // expects GrossVsNetMonthly
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
    title: { text: '瀑布图：应发 -> 扣除 -> 实际到手', left: 'center' },
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
  <div class="chart" ref="el" style="height: 320px; width: 100%"></div>
</template>
