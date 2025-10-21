<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useStatsStore } from '../../store/stats'
import DeductionsBreakdown from '../../components/stats/DeductionsBreakdown.vue'
import EmptyState from '../../components/EmptyState.vue'

const stats = useStatsStore()
const info = ref({ summary: [], monthly: [] })
const loading = ref(false)
const error = ref(null)

const hasData = computed(() => (info.value?.summary?.length || 0) > 0 || (info.value?.monthly?.length || 0) > 0)

async function load() {
  loading.value = true
  error.value = null
  try {
    info.value = await stats.loadDeductionsBreakdown()
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
    <el-card v-else shadow="hover">
      <DeductionsBreakdown :summary="info.summary" :monthly="info.monthly" />
    </el-card>
  </div>
</template>
