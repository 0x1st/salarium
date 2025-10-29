<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useStatsStore } from '../../store/stats'
import DeductionsBreakdown from '../../components/stats/DeductionsBreakdown.vue'
import EmptyState from '../../components/EmptyState.vue'
import { hasStatsData } from '../../utils/stats'

const stats = useStatsStore()
const info = ref({ summary: [], monthly: [] })
const loading = ref(false)
const error = ref(null)

const hasData = computed(() => hasStatsData(info.value))

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
    <el-card v-else shadow="hover">
      <DeductionsBreakdown :summary="info.summary" :monthly="info.monthly" />
    </el-card>
  </div>
</template>

<style scoped>
:deep(.el-card) {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  min-height: 400px;
}

:deep(.el-card:hover) {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

:deep(.el-card__header) {
  padding: 18px 20px;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>
