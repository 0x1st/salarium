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

const netSeries = computed(() => {
  const points = [...(net.value || [])]
  points.sort((a, b) => (a.year - b.year) || (a.month - b.month))
  return points
})

const bestMonth = computed(() => {
  if (!netSeries.value.length) return null
  return netSeries.value.reduce((best, cur) => (cur.net_income > best.net_income ? cur : best))
})

const worstMonth = computed(() => {
  if (!netSeries.value.length) return null
  return netSeries.value.reduce((worst, cur) => (cur.net_income < worst.net_income ? cur : worst))
})

const momChange = computed(() => {
  const s = netSeries.value
  if (s.length < 2) return null
  const last = s[s.length - 1]
  const prev = s[s.length - 2]
  return {
    amount: (last.net_income || 0) - (prev.net_income || 0),
    latest: last,
  }
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
          <KPICards :items="[
            { label: '应发合计', value: formatCurrency(totals.gross), color: '#da7756' },
            { label: '实际到手', value: formatCurrency(totals.takeHome), color: '#5a8a6e' },
            { label: '税费合计', value: formatCurrency(totals.tax), color: '#c45c5c' },
            { label: '五险一金', value: formatCurrency(totals.insurance), color: '#c9a227' },
            { label: '补贴合计', value: formatCurrency(totals.allowances), color: '#b77a55' },
            { label: '非现金福利', value: formatCurrency(totals.nonCash), color: '#7c6f64' }
          ]" />
        </el-card>
      </section>

      <section class="section">
        <div class="section-title">效率与波动</div>
        <div class="insight-grid">
          <div class="insight-card">
            <div class="insight-label">到手率</div>
            <div class="insight-value">{{ formatPercent(totals.gross ? (totals.takeHome / totals.gross) : NaN) }}</div>
            <div class="insight-note">实际到手 / 应发</div>
          </div>
          <div class="insight-card">
            <div class="insight-label">税负率</div>
            <div class="insight-value">{{ formatPercent(totals.gross ? (totals.tax / totals.gross) : NaN) }}</div>
            <div class="insight-note">税费 / 应发</div>
          </div>
          <div class="insight-card">
            <div class="insight-label">五险一金占比</div>
            <div class="insight-value">{{ formatPercent(totals.gross ? (totals.insurance / totals.gross) : NaN) }}</div>
            <div class="insight-note">社保公积金 / 应发</div>
          </div>
          <div class="insight-card">
            <div class="insight-label">月均到手</div>
            <div class="insight-value">{{ formatCurrency(totals.months ? (totals.takeHome / totals.months) : 0) }}</div>
            <div class="insight-note">按有记录月份计算</div>
          </div>
        </div>
        <div class="insight-list">
          <div class="insight-row">
            <span class="insight-label">最高月份</span>
            <span class="insight-value">
              {{ bestMonth ? `${bestMonth.year}-${String(bestMonth.month).padStart(2, '0')} · ${formatCurrency(bestMonth.net_income)}` : '—' }}
            </span>
          </div>
          <div class="insight-row">
            <span class="insight-label">最低月份</span>
            <span class="insight-value">
              {{ worstMonth ? `${worstMonth.year}-${String(worstMonth.month).padStart(2, '0')} · ${formatCurrency(worstMonth.net_income)}` : '—' }}
            </span>
          </div>
          <div class="insight-row">
            <span class="insight-label">最近环比</span>
            <span class="insight-value">
              {{ momChange ? `${momChange.latest.year}-${String(momChange.latest.month).padStart(2, '0')} · ${formatCurrency(momChange.amount)}` : '—' }}
            </span>
          </div>
        </div>
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

.insight-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.insight-card {
  background: #fffdfb;
  border: 1px solid #e5e0dc;
  border-radius: 12px;
  padding: 14px 16px;
  display: grid;
  gap: 6px;
}

.insight-label {
  font-size: 0.8rem;
  color: #6b6560;
}

.insight-value {
  font-size: 1.05rem;
  font-weight: 600;
  color: #2d2a26;
}

.insight-note {
  font-size: 0.75rem;
  color: #9a9590;
}

.insight-list {
  margin-top: 12px;
  display: grid;
  gap: 8px;
}

.insight-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: #fff;
  border: 1px solid #f1ebe7;
  border-radius: 10px;
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
  .insight-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 640px) {
  .insight-grid { grid-template-columns: 1fr; }
}
</style>
