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
watch(() => [stats.personId, stats.year, stats.range], () => { stats.invalidateCache(); load() }, { deep: true })
</script>

<template>
  <div>
    <div v-if="loading" style="padding: 16px"><el-skeleton :rows="6" animated /></div>
    <div v-else-if="error" class="empty"><p>加载失败，请重试</p><el-button type="primary" @click="load">重试</el-button></div>
    <EmptyState v-else-if="!hasData" />
    <div v-else class="two-col">
      <el-card shadow="hover"><IncomeCompositionPie :data="comp" /></el-card>
      <el-card shadow="hover"><StackedAreaIncome :data="comp" /></el-card>
    </div>
  </div>
</template>

<style scoped>
.two-col { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
@media (max-width: 992px) {
  .two-col { grid-template-columns: 1fr; }
}
</style>
