<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useStatsStore } from '../../store/stats'
import NetIncomeChart from '../../components/stats/NetIncomeChart.vue'
import GrossVsNetBar from '../../components/stats/GrossVsNetBar.vue'
import WaterfallChart from '../../components/stats/WaterfallChart.vue'
import KPICards from '../../components/stats/KPICards.vue'
import EmptyState from '../../components/EmptyState.vue'
import { formatCurrency } from '../../utils/number'

const stats = useStatsStore()
const net = ref([])
const gvn = ref([])
const loading = ref(false)
const error = ref(null)

const hasData = computed(() => (net.value?.length || 0) > 0 || (gvn.value?.length || 0) > 0)

async function load() {
  loading.value = true
  error.value = null
  try {
    net.value = await stats.loadMonthlyNetIncome()
    gvn.value = await stats.loadGrossVsNetMonthly()
  } catch (e) {
    error.value = e
  } finally { loading.value = false }
}

onMounted(() => { load() })
// Reload when filters change
watch(() => [stats.personId, stats.year, stats.month], () => { stats.invalidate(); load() }, { deep: true })
// Reload when external invalidation occurs (e.g., salary CRUD elsewhere)
watch(() => stats.refreshToken, () => { load() })
</script>

<template>
  <div class="net-grid">
    <div v-if="loading" style="padding: 16px"><el-skeleton :rows="6" animated /></div>
    <div v-else-if="error" class="empty"><p>加载失败，请重试</p><el-button type="primary" @click="load">重试</el-button></div>
    <EmptyState v-else-if="!hasData" />
    <template v-else>
      <el-card shadow="hover">
        <KPICards :items="[
          { label: '应发工资', value: formatCurrency(gvn.reduce((s,p)=> s + (p.gross_income||0), 0)), color: '#409EFF' },
          { label: '扣除', value: formatCurrency(Math.max(gvn.reduce((s,p)=> s + (p.gross_income||0), 0) - gvn.reduce((s,p)=> s + (p.net_income||0), 0), 0)), color: '#F56C6C' },
          { label: '实际到手金额', value: formatCurrency(gvn.reduce((s,p)=> s + (p.net_income||0), 0)), color: '#67C23A' }
        ]" />
      </el-card>

      <el-card shadow="hover">
        <NetIncomeChart :data="net" />
      </el-card>

      <div class="two-col">
        <el-card shadow="hover"><GrossVsNetBar :data="gvn" /></el-card>
        <el-card shadow="hover"><WaterfallChart :data="gvn" /></el-card>
      </div>
    </template>
  </div>
</template>

<style scoped>
.net-grid { 
  display: grid; 
  grid-template-columns: 1fr; 
  gap: 20px; 
}

.net-grid :deep(.el-card) {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.net-grid :deep(.el-card:hover) {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.two-col { 
  display: grid; 
  grid-template-columns: 1fr 1fr; 
  gap: 20px; 
}

@media (max-width: 992px) {
  .two-col { grid-template-columns: 1fr; }
}
</style>
