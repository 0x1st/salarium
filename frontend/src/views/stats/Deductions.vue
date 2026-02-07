<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useStatsStore } from '../../store/stats'
import DeductionsBreakdown from '../../components/stats/DeductionsBreakdown.vue'
import EmptyState from '../../components/EmptyState.vue'
import { hasStatsData } from '../../utils/stats'
import { formatCurrency } from '../../utils/number'

const stats = useStatsStore()
const info = ref({ summary: [], monthly: [] })
const loading = ref(false)
const error = ref(null)

const hasData = computed(() => hasStatsData(info.value))

const labelMap = {
  pension_insurance: '养老保险',
  medical_insurance: '医疗保险',
  unemployment_insurance: '失业保险',
  critical_illness_insurance: '大病互助保险',
  enterprise_annuity: '企业年金',
  housing_fund: '住房公积金',
  other_deductions: '其他扣除',
  labor_union_fee: '工会',
  performance_deduction: '绩效扣除',
}

const totalDeduction = computed(() => (info.value.summary || []).reduce((s, i) => s + (i.amount || 0), 0))

const topItem = computed(() => {
  const items = [...(info.value.summary || [])]
  items.sort((a, b) => (b.amount || 0) - (a.amount || 0))
  return items[0] || null
})

const avgMonthly = computed(() => {
  const months = info.value.monthly?.length || 0
  if (!months) return 0
  const total = info.value.monthly.reduce((s, m) => s + (m.total || 0), 0)
  return total / months
})

async function load() {
  loading.value = true
  error.value = null
  try {
    info.value = await stats.loadDeductionsBreakdown()
  } catch (e) { error.value = e } finally { loading.value = false }
}

onMounted(load)
// Reload on filter changes
watch(() => [stats.personId, stats.year, stats.month], () => { stats.invalidate(); load() }, { deep: true })
// Reload when external modules invalidate stats (e.g., after salary CRUD)
watch(() => stats.refreshToken, () => { load() })
</script>

<template>
  <div>
    <div v-if="loading" style="padding: 16px"><el-skeleton :rows="6" animated /></div>
    <div v-else-if="error" class="empty"><p>加载失败，请重试</p><el-button type="primary" @click="load">重试</el-button></div>
    <EmptyState v-else-if="!hasData" />
    <div v-else class="section">
      <div class="section-title">扣除概览</div>
      <div class="summary-grid">
        <div class="summary-card">
          <div class="summary-label">扣除合计</div>
          <div class="summary-value">{{ formatCurrency(totalDeduction) }}</div>
          <div class="summary-note">选定范围合计</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">月均扣除</div>
          <div class="summary-value">{{ formatCurrency(avgMonthly) }}</div>
          <div class="summary-note">按有记录月份</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">最高扣除项</div>
          <div class="summary-value">{{ topItem ? (labelMap[topItem.category] || topItem.category) : '—' }}</div>
          <div class="summary-note">{{ topItem ? formatCurrency(topItem.amount) : '—' }}</div>
        </div>
      </div>
      <div class="section-title" style="margin-top: 12px;">扣除结构</div>
      <el-card shadow="hover">
        <DeductionsBreakdown :summary="info.summary" :monthly="info.monthly" />
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
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

:deep(.el-card) {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e5e0dc;
  box-shadow: none;
  transition: all 0.2s ease;
  min-height: 400px;
}

:deep(.el-card:hover) {
  border-color: #d5d0cc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

:deep(.el-card__header) {
  padding: 18px 20px;
  border-bottom: 1px solid #e5e0dc;
}

:deep(.el-card__body) {
  padding: 20px;
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

@media (max-width: 900px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
