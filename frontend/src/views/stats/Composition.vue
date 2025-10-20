<script setup>
import { ref, onMounted, watch } from 'vue'
import { useStatsStore } from '../../store/stats'
import IncomeCompositionPie from '../../components/stats/IncomeCompositionPie.vue'
import StackedAreaIncome from '../../components/stats/StackedAreaIncome.vue'

const stats = useStatsStore()
const comp = ref([])
const loading = ref(false)
const error = ref(null)

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
  <div class="two-col">
    <el-card shadow="hover"><IncomeCompositionPie :data="comp" /></el-card>
    <el-card shadow="hover"><StackedAreaIncome :data="comp" /></el-card>

    <div v-if="!loading && error" class="empty">
      <p>加载失败，请重试</p>
      <el-button type="primary" @click="load">重试</el-button>
    </div>
  </div>
</template>

<style scoped>
.two-col { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
@media (max-width: 992px) {
  .two-col { grid-template-columns: 1fr; }
}
</style>
