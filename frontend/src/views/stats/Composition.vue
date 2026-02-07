<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useStatsStore } from '../../store/stats'
import IncomeCompositionPie from '../../components/stats/IncomeCompositionPie.vue'
import StackedAreaIncome from '../../components/stats/StackedAreaIncome.vue'
import EmptyState from '../../components/EmptyState.vue'

const stats = useStatsStore()
const comp = ref([])
const loading = ref(false)
const error = ref(null)

const hasData = computed(() => (comp.value?.length || 0) > 0)

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
    <div v-else class="two-col">
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
</template>

<style scoped>
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
}
</style>
