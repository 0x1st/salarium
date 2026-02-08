<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useStatsStore } from '../../store/stats'
import PieBreakdown from '../../components/stats/PieBreakdown.vue'
import EmptyState from '../../components/EmptyState.vue'
import { hasStatsData } from '../../utils/stats'
import { formatCurrency } from '../../utils/number'

const stats = useStatsStore()
const info = ref({ summary: [], monthly: [] })
const loading = ref(false)
const error = ref(null)

const hasData = computed(() => hasStatsData(info.value))

const insuranceKeys = new Map([
  ['养老保险', 'pension_insurance'],
  ['医疗保险', 'medical_insurance'],
  ['失业保险', 'unemployment_insurance'],
  ['大病互助保险', 'critical_illness_insurance'],
  ['企业年金', 'enterprise_annuity'],
  ['住房公积金', 'housing_fund'],
])

const insuranceRows = computed(() => {
  const totals = new Map()
  for (const item of info.value.summary || []) {
    const key = insuranceKeys.get(item.category)
    if (!key) continue
    totals.set(item.category, (totals.get(item.category) || 0) + (item.amount || 0))
  }
  const rows = []
  for (const [label, amount] of totals.entries()) {
    if (!amount) continue
    rows.push({ key: label, label, amount })
  }
  const total = rows.reduce((s, r) => s + r.amount, 0)
  return rows.map(r => ({
    ...r,
    percent: total ? (r.amount / total) : 0,
  }))
})

const insuranceTotal = computed(() => insuranceRows.value.reduce((s, r) => s + r.amount, 0))

function formatPercent(value) {
  if (!Number.isFinite(value)) return '—'
  return `${(value * 100).toFixed(1)}%`
}

async function load() {
  loading.value = true
  error.value = null
  try {
    info.value = await stats.loadDeductionsBreakdown()
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
      <div class="section">
        <div class="section-title">五险一金构成</div>
        <div class="breakdown-grid">
          <div class="breakdown-card">
            <div class="card-title">金额与比例</div>
            <div class="rows">
              <div v-for="row in insuranceRows" :key="row.key" class="row">
                <span class="row-label">{{ row.label }}</span>
                <span class="row-value">{{ formatCurrency(row.amount) }}</span>
                <span class="row-percent">{{ formatPercent(row.percent) }}</span>
              </div>
              <div class="row total">
                <span class="row-label">五险一金合计</span>
                <span class="row-value">{{ formatCurrency(insuranceTotal) }}</span>
                <span class="row-percent">100%</span>
              </div>
            </div>
          </div>
          <div class="breakdown-card">
            <PieBreakdown title="五险一金构成" :data="insuranceRows.map(r => ({ label: r.label, value: r.amount }))" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
