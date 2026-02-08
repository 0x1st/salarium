<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useStatsStore } from '../../store/stats'
import PieBreakdown from '../../components/stats/PieBreakdown.vue'
import EmptyState from '../../components/EmptyState.vue'
import { formatCurrency } from '../../utils/number'

const stats = useStatsStore()
const comp = ref([])
const monthly = ref([])
const loading = ref(false)
const error = ref(null)

const hasData = computed(() => (comp.value?.length || 0) > 0)

function sumAllowances(row) {
  return (row.high_temp_allowance || 0)
    + (row.low_temp_allowance || 0)
    + (row.meal_allowance || 0)
    + (row.computer_allowance || 0)
    + (row.communication_allowance || 0)
    + (row.comprehensive_allowance || 0)
}

const takeHomeRows = computed(() => {
  const totals = { base: 0, perf: 0, allow: 0, other: 0 }
  const index = new Map()
  for (const m of monthly.value || []) {
    const key = `${m.person_id}-${m.year}-${m.month}`
    index.set(key, m)
  }
  for (const r of comp.value || []) {
    const key = `${r.person_id}-${r.year}-${r.month}`
    const m = index.get(key)
    const cashIncome = (r.base_salary || 0) + (r.performance_salary || 0) + sumAllowances(r) + (r.other_income || 0)
    const gross = m?.gross_income || cashIncome
    const takeHome = m?.actual_take_home || 0
    const ratio = gross ? (takeHome / gross) : 0
    totals.base += (r.base_salary || 0) * ratio
    totals.perf += (r.performance_salary || 0) * ratio
    totals.allow += sumAllowances(r) * ratio
    totals.other += (r.other_income || 0) * ratio
  }
  const total = totals.base + totals.perf + totals.allow + totals.other
  const rows = [
    { key: 'base', label: '基本工资', amount: totals.base },
    { key: 'perf', label: '绩效工资', amount: totals.perf },
    { key: 'allow', label: '补贴', amount: totals.allow },
    { key: 'other', label: '其他收入', amount: totals.other },
  ].filter(r => r.amount !== 0)
  return rows.map(r => ({
    ...r,
    percent: total ? (r.amount / total) : 0,
  }))
})

const takeHomeTotal = computed(() => takeHomeRows.value.reduce((s, r) => s + r.amount, 0))

const nonCashRows = computed(() => {
  const totals = new Map()
  const add = (key, label, amount) => {
    if (!amount) return
    totals.set(key, { label, amount: (totals.get(key)?.amount || 0) + amount })
  }
  for (const r of comp.value || []) {
    add('mid_autumn', '中秋福利', r.mid_autumn_benefit || 0)
    add('dragon_boat', '端午福利', r.dragon_boat_benefit || 0)
    add('spring_festival', '春节福利', r.spring_festival_benefit || 0)
    for (const item of r.custom_non_cash_items || []) {
      if (!item || !item.amount) continue
      add(item.key || item.label, item.label || item.key, item.amount || 0)
    }
  }
  const rows = Array.from(totals.entries()).map(([key, v]) => ({
    key,
    label: v.label || key,
    amount: v.amount,
  }))
  const total = rows.reduce((s, r) => s + r.amount, 0)
  return rows.map(r => ({
    ...r,
    percent: total ? (r.amount / total) : 0,
  }))
})

const nonCashTotal = computed(() => nonCashRows.value.reduce((s, r) => s + r.amount, 0))

function formatPercent(value) {
  if (!Number.isFinite(value)) return '—'
  return `${(value * 100).toFixed(1)}%`
}

async function load() {
  loading.value = true
  error.value = null
  try {
    comp.value = await stats.loadIncomeComposition()
    monthly.value = await stats.loadMonthlyStats()
  } catch (e) { error.value = e } finally { loading.value = false }
}

onMounted(load)
watch(() => [stats.personId, stats.year, stats.month], () => { stats.invalidate(); load() }, { deep: true })
watch(() => stats.refreshToken, () => { load() })
</script>

<template>
  <div>
    <div v-if="loading" style="padding: 16px"><el-skeleton :rows="6" animated /></div>
    <div v-else-if="error" class="empty"><p>加载失败，请重试</p><el-button type="primary" @click="load">重试</el-button></div>
    <EmptyState v-else-if="!hasData" />
    <div v-else>
      <div class="section-stack">
        <div class="section">
          <div class="section-title">到手构成</div>
          <div class="breakdown-grid">
            <div class="breakdown-card">
              <div class="card-title">金额与比例</div>
              <div class="rows">
                <div v-for="row in takeHomeRows" :key="row.key" class="row">
                  <span class="row-label">{{ row.label }}</span>
                  <span class="row-value">{{ formatCurrency(row.amount) }}</span>
                  <span class="row-percent">{{ formatPercent(row.percent) }}</span>
                </div>
                <div class="row total">
                  <span class="row-label">实际到手</span>
                  <span class="row-value">{{ formatCurrency(takeHomeTotal) }}</span>
                  <span class="row-percent">100%</span>
                </div>
              </div>
            </div>
            <div class="breakdown-card">
              <PieBreakdown title="到手构成" :data="takeHomeRows.map(r => ({ label: r.label, value: r.amount }))" />
            </div>
          </div>
        </div>

        <div class="section">
          <div class="section-title">非现金构成</div>
          <div class="breakdown-grid">
            <div class="breakdown-card">
              <div class="card-title">金额与比例</div>
              <div class="rows">
                <div v-for="row in nonCashRows" :key="row.key" class="row">
                  <span class="row-label">{{ row.label }}</span>
                  <span class="row-value">{{ formatCurrency(row.amount) }}</span>
                  <span class="row-percent">{{ formatPercent(row.percent) }}</span>
                </div>
                <div class="row total">
                  <span class="row-label">非现金福利</span>
                  <span class="row-value">{{ formatCurrency(nonCashTotal) }}</span>
                  <span class="row-percent">100%</span>
                </div>
              </div>
            </div>
            <div class="breakdown-card">
              <PieBreakdown title="非现金构成" :data="nonCashRows.map(r => ({ label: r.label, value: r.amount }))" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.section-stack {
  display: grid;
  gap: 24px;
}
.breakdown-grid {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 24px;
}

.breakdown-card {
  background: #fffdfb;
  border: 1px solid #e5e0dc;
  border-radius: 12px;
  padding: 16px;
  display: grid;
  gap: 12px;
}

.card-title {
  font-size: 0.875rem;
  color: #6b6560;
  font-weight: 500;
}

.rows {
  display: grid;
  gap: 8px;
}

.row {
  display: grid;
  grid-template-columns: 1.4fr 1fr 0.6fr;
  gap: 8px;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid #f1ebe7;
  border-radius: 10px;
  background: #fff;
}

.row.total {
  background: #f8f2ee;
  border-color: #e5e0dc;
  font-weight: 600;
}

.row-label {
  color: #6b6560;
  font-size: 0.875rem;
}

.row-value {
  font-weight: 500;
  color: #2d2a26;
}

.row-percent {
  color: #9a9590;
  text-align: right;
  font-size: 0.85rem;
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

@media (max-width: 992px) {
  .breakdown-grid { grid-template-columns: 1fr; }
}

@media (max-width: 640px) {
  .row { grid-template-columns: 1fr; text-align: left; }
  .row-percent { text-align: left; }
}
</style>
