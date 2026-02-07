<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useStatsStore } from '../../store/stats'
import IncomeCompositionPie from '../../components/stats/IncomeCompositionPie.vue'
import StackedAreaIncome from '../../components/stats/StackedAreaIncome.vue'
import EmptyState from '../../components/EmptyState.vue'
import { formatCurrency } from '../../utils/number'

const stats = useStatsStore()
const comp = ref([])
const loading = ref(false)
const error = ref(null)

const hasData = computed(() => (comp.value?.length || 0) > 0)

const summary = computed(() => {
  const agg = { base: 0, perf: 0, allow: 0, benefits: 0, other: 0 }
  for (const r of comp.value || []) {
    agg.base += r.base_salary || 0
    agg.perf += r.performance_salary || 0
    const allow = (r.high_temp_allowance || 0)
      + (r.low_temp_allowance || 0)
      + (r.meal_allowance || 0)
      + (r.computer_allowance || 0)
      + (r.communication_allowance || 0)
      + (r.comprehensive_allowance || 0)
    agg.allow += allow
    agg.benefits += r.non_cash_benefits || 0
    agg.other += r.other_income || 0
  }
  return agg
})

const totalIncome = computed(() => {
  const s = summary.value
  return s.base + s.perf + s.allow + s.benefits + s.other
})

const topMix = computed(() => {
  const s = summary.value
  const total = totalIncome.value || 1
  const rows = [
    { label: '基本工资', value: s.base },
    { label: '绩效工资', value: s.perf },
    { label: '补贴', value: s.allow },
    { label: '福利', value: s.benefits },
    { label: '其他收入', value: s.other },
  ]
  return rows
    .map(r => ({ ...r, share: r.value / total }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 3)
})

function formatPercent(value) {
  if (!Number.isFinite(value)) return '—'
  return `${(value * 100).toFixed(1)}%`
}

async function load() {
  loading.value = true
  error.value = null
  try {
    comp.value = await stats.loadIncomeComposition()
  } catch (e) { error.value = e } finally { loading.value = false }
}

onMounted(load)
// Reload when filters change
watch(() => [stats.personId, stats.year, stats.month], () => { stats.invalidate(); load() }, { deep: true })
// Reload when external invalidation occurs (e.g., salary CRUD elsewhere)
watch(() => stats.refreshToken, () => { load() })
</script>

<template>
  <div>
    <div v-if="loading" style="padding: 16px"><el-skeleton :rows="6" animated /></div>
    <div v-else-if="error" class="empty"><p>加载失败，请重试</p><el-button type="primary" @click="load">重试</el-button></div>
    <EmptyState v-else-if="!hasData" />
    <div v-else>
      <div class="section">
        <div class="section-title">结构概览</div>
        <div class="summary-grid">
          <div class="summary-card">
            <div class="summary-label">总收入</div>
            <div class="summary-value">{{ formatCurrency(totalIncome) }}</div>
            <div class="summary-note">选定范围合计</div>
          </div>
          <div class="summary-card">
            <div class="summary-label">补贴+福利占比</div>
            <div class="summary-value">
              {{ formatPercent(totalIncome ? ((summary.allow + summary.benefits) / totalIncome) : NaN) }}
            </div>
            <div class="summary-note">补贴/福利对收入贡献</div>
          </div>
          <div class="summary-card">
            <div class="summary-label">绩效占比</div>
            <div class="summary-value">
              {{ formatPercent(totalIncome ? (summary.perf / totalIncome) : NaN) }}
            </div>
            <div class="summary-note">绩效工资占比</div>
          </div>
          <div class="summary-card">
            <div class="summary-label">主导来源</div>
            <div class="summary-value">{{ topMix[0]?.label || '—' }}</div>
            <div class="summary-note">
              {{ topMix[0] ? formatPercent(topMix[0].share) : '—' }}
            </div>
          </div>
        </div>
        <div class="top-mix">
          <div v-for="item in topMix" :key="item.label" class="mix-row">
            <span class="mix-label">{{ item.label }}</span>
            <span class="mix-value">{{ formatCurrency(item.value) }}</span>
            <span class="mix-share">{{ formatPercent(item.share) }}</span>
          </div>
        </div>
      </div>

      <div class="two-col">
        <div class="section">
          <div class="section-title">收入构成</div>
          <el-card shadow="hover"><IncomeCompositionPie :data="comp" /></el-card>
        </div>
        <div class="section">
          <div class="section-title">收入趋势</div>
          <el-card shadow="hover"><StackedAreaIncome :data="comp" /></el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.summary-card {
  background: #fffdfb;
  border: 1px solid #e5e0dc;
  border-radius: 12px;
  padding: 14px 16px;
  display: grid;
  gap: 6px;
}

.summary-label {
  font-size: 0.8rem;
  color: #6b6560;
}

.summary-value {
  font-size: 1.05rem;
  font-weight: 600;
  color: #2d2a26;
}

.summary-note {
  font-size: 0.75rem;
  color: #9a9590;
}

.top-mix {
  display: grid;
  gap: 8px;
  margin-top: 12px;
}

.mix-row {
  display: grid;
  grid-template-columns: 1.4fr 1fr 0.6fr;
  gap: 8px;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid #f1ebe7;
  border-radius: 10px;
  background: #fff;
}

.mix-label {
  color: #6b6560;
  font-size: 0.875rem;
}

.mix-value {
  font-weight: 500;
  color: #2d2a26;
}

.mix-share {
  color: #9a9590;
  text-align: right;
  font-size: 0.85rem;
}

.two-col { 
  display: grid; 
  grid-template-columns: 1fr 1fr; 
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

.two-col :deep(.el-card) {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e5e0dc;
  box-shadow: none;
  transition: all 0.2s ease;
}

.two-col :deep(.el-card:hover) {
  border-color: #d5d0cc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.two-col :deep(.el-card__header) {
  padding: 18px 20px;
  border-bottom: 1px solid #e5e0dc;
}

.two-col :deep(.el-card__body) {
  padding: 20px;
}

@media (max-width: 992px) {
  .two-col { grid-template-columns: 1fr; }
  .summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 640px) {
  .summary-grid { grid-template-columns: 1fr; }
  .mix-row { grid-template-columns: 1fr; text-align: left; }
  .mix-share { text-align: left; }
}
</style>
