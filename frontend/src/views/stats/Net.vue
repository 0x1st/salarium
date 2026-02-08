<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useStatsStore } from '../../store/stats'
import NetIncomeChart from '../../components/stats/NetIncomeChart.vue'
import GrossVsNetBar from '../../components/stats/GrossVsNetBar.vue'
import WaterfallChart from '../../components/stats/WaterfallChart.vue'
import KPICards from '../../components/stats/KPICards.vue'
import EmptyState from '../../components/EmptyState.vue'
import { formatCurrency } from '../../utils/number'

const stats = useStatsStore()
const net = ref([])
const gvn = ref([])
const monthly = ref([])
const loading = ref(false)
const error = ref(null)

const hasData = computed(() => (net.value?.length || 0) > 0 || (gvn.value?.length || 0) > 0)

const totals = computed(() => {
  const agg = {
    gross: 0,
    net: 0,
    takeHome: 0,
    tax: 0,
    insurance: 0,
    allowances: 0,
    nonCash: 0,
    months: new Set(),
  }
  for (const r of monthly.value || []) {
    agg.gross += r.gross_income || 0
    agg.net += r.net_income || 0
    agg.takeHome += r.actual_take_home || 0
    agg.tax += r.tax || 0
    agg.insurance += r.insurance_total || 0
    agg.allowances += r.allowances_total || 0
    agg.nonCash += r.non_cash_benefits || 0
    if (r.year && r.month) agg.months.add(`${r.year}-${r.month}`)
  }
  return { ...agg, months: agg.months.size }
})

function formatPercent(value) {
  if (!Number.isFinite(value)) return '—'
  return `${(value * 100).toFixed(1)}%`
}

async function load() {
  loading.value = true
  error.value = null
  try {
    net.value = await stats.loadMonthlyNetIncome()
    gvn.value = await stats.loadGrossVsNetMonthly()
    monthly.value = await stats.loadMonthlyStats()
  } catch (e) {
    error.value = e
  } finally { loading.value = false }
}

onMounted(() => { load() })
// Reload when filters change
watch(() => [stats.personId, stats.year, stats.month], () => { stats.invalidate(); load() }, { deep: true })
// Reload when external invalidation occurs (e.g., salary CRUD elsewhere)
watch(() => stats.refreshToken, () => { load() })
</script>

<template>
  <div class="net-grid">
    <div v-if="loading" style="padding: 16px"><el-skeleton :rows="6" animated /></div>
    <div v-else-if="error" class="empty"><p>加载失败，请重试</p><el-button type="primary" @click="load">重试</el-button></div>
    <EmptyState v-else-if="!hasData" />
    <template v-else>
      <section class="section">
        <div class="section-title">核心指标</div>
        <el-card shadow="hover">
          <KPICards class="kpi-compact" :items="[
            { label: '应发合计', value: formatCurrency(totals.gross), color: '#da7756' },
            { label: '实际到手', value: formatCurrency(totals.takeHome), color: '#5a8a6e' },
            { label: '五险一金', value: formatCurrency(totals.insurance), color: '#c9a227' },
            { label: '非现金福利', value: formatCurrency(totals.nonCash), color: '#7c6f64' },
            { label: '到手率', value: formatPercent(totals.gross ? (totals.takeHome / totals.gross) : NaN), color: '#5a8a6e' },
            { label: '税负率', value: formatPercent(totals.gross ? (totals.tax / totals.gross) : NaN), color: '#c45c5c' },
            { label: '五险一金占比', value: formatPercent(totals.gross ? (totals.insurance / totals.gross) : NaN), color: '#c9a227' },
            { label: '月均到手', value: formatCurrency(totals.months ? (totals.takeHome / totals.months) : 0), color: '#5a8a6e' }
          ]" />
        </el-card>
      </section>

      <section class="section">
        <div class="section-title">趋势</div>
        <el-card shadow="hover">
          <NetIncomeChart :data="net" />
        </el-card>
      </section>

      <section class="section">
        <div class="section-title">结构对比</div>
        <div class="two-col">
          <el-card shadow="hover"><GrossVsNetBar :data="gvn" /></el-card>
          <el-card shadow="hover"><WaterfallChart :data="gvn" /></el-card>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.net-grid { 
  display: grid; 
  grid-template-columns: 1fr; 
  gap: 24px; 
  min-height: 400px;
}

.section {
  display: grid;
  gap: 12px;
}

.section-title {
  font-size: 0.875rem;
  color: #6b6560;
  font-weight: 500;
}

.kpi-compact :deep(.kpi-grid) {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.net-grid :deep(.el-card) {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e5e0dc;
  box-shadow: none;
  transition: all 0.2s ease;
}

.net-grid :deep(.el-card:hover) {
  border-color: #d5d0cc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.net-grid :deep(.el-card__header) {
  padding: 18px 20px;
  border-bottom: 1px solid #e5e0dc;
}

.net-grid :deep(.el-card__body) {
  padding: 20px;
}

.two-col { 
  display: grid; 
  grid-template-columns: 1fr 1fr; 
  gap: 24px; 
}

@media (max-width: 992px) {
  .two-col { grid-template-columns: 1fr; }
  .kpi-compact :deep(.kpi-grid) {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .kpi-compact :deep(.kpi-grid) {
    grid-template-columns: 1fr;
  }
}
</style>
