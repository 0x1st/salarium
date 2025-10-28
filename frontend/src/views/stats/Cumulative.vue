<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useStatsStore } from '../../store/stats'
import CumulativeContribChart from '../../components/stats/CumulativeContribChart.vue'
import EmptyState from '../../components/EmptyState.vue'

const stats = useStatsStore()
const data = ref(null)
const loading = ref(false)
const error = ref(null)

const hasData = computed(() => Array.isArray(data.value?.points) && data.value.points.length > 0)

async function load() {
  if (!stats.personId) return
  loading.value = true
  error.value = null
  try { data.value = await stats.loadContributionsCumulative() } catch (e) { error.value = e } finally { loading.value = false }
}

onMounted(load)
// Reload when filters change
watch(() => [stats.personId, stats.year, stats.month], () => { stats.invalidate(); load() }, { deep: true })
// Reload on external invalidation
watch(() => stats.refreshToken, () => { load() })
</script>

<template>
  <div>
    <el-alert v-if="!stats.personId" title="请选择人员以查看累计曲线" type="info" show-icon />

    <div v-else>
      <div v-if="loading" style="padding: 16px"><el-skeleton :rows="6" animated /></div>
      <div v-else-if="error" class="empty"><p>加载失败，请重试</p><el-button type="primary" @click="load">重试</el-button></div>
      <EmptyState v-else-if="!hasData" />
      <el-card v-else shadow="hover">
        <CumulativeContribChart :points="data?.points || []" :title="(data?.person_name || '') + ' 累计曲线'" />
      </el-card>
    </div>
  </div>
</template>

<style scoped>
:deep(.el-card) {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

:deep(.el-card:hover) {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}
</style>
