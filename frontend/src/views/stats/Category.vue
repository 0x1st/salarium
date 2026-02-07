<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useStatsStore } from '../../store/stats'
import EmptyState from '../../components/EmptyState.vue'
import { formatCurrency } from '../../utils/number'

const stats = useStatsStore()
const info = ref({ income: [], deduction: [], total_income: 0, total_deduction: 0 })
const loading = ref(false)
const error = ref(null)

const hasData = computed(() => {
  return (info.value.income?.length || 0) > 0 || (info.value.deduction?.length || 0) > 0
})

async function load() {
  loading.value = true
  error.value = null
  try {
    info.value = await stats.loadCategorySummary()
  } catch (e) {
    error.value = e
  } finally {
    loading.value = false
  }
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
    <div v-else class="category-grid">
      <div class="section">
        <div class="section-title">收入分类</div>
        <el-card shadow="hover">
        <template #header>
          <div class="card-title">收入分类</div>
          <div class="card-total">合计 {{ formatCurrency(info.total_income || 0) }}</div>
        </template>
        <div class="list">
          <div v-for="item in info.income" :key="item.category" class="row">
            <div class="row-label">{{ item.label }}</div>
            <div class="row-value">{{ formatCurrency(item.amount) }}</div>
          </div>
        </div>
        </el-card>
      </div>

      <div class="section">
        <div class="section-title">扣除分类</div>
        <el-card shadow="hover">
        <template #header>
          <div class="card-title">扣除分类</div>
          <div class="card-total">合计 {{ formatCurrency(info.total_deduction || 0) }}</div>
        </template>
        <div class="list">
          <div v-for="item in info.deduction" :key="item.category" class="row">
            <div class="row-label">{{ item.label }}</div>
            <div class="row-value">{{ formatCurrency(item.amount) }}</div>
          </div>
        </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<style scoped>
.category-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
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

.list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid #f1ebe7;
  background: #fffdfb;
  padding: 10px 12px;
  border-radius: 10px;
}

.row-label {
  color: #6b6560;
  font-size: 0.875rem;
}

.row-value {
  font-weight: 500;
  color: #2d2a26;
}

.card-title {
  font-weight: 500;
}

.card-total {
  font-size: 0.875rem;
  color: #6b6560;
}

@media (max-width: 900px) {
  .category-grid {
    grid-template-columns: 1fr;
  }
}
</style>
