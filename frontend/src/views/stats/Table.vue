<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useStatsStore } from '../../store/stats'
import { formatCurrency } from '../../utils/number'
import { Download } from 'lucide-vue-next'

const stats = useStatsStore()
const monthly = ref([])
const annualMonthly = ref([])
const loading = ref(false)
const error = ref(null)
const activeTab = ref('monthly')
const currentPage = ref(1)
const pageSize = ref(20)

const headerCellStyle = { background: '#f9fafb', padding: '12px 16px', color: '#374151', fontWeight: 600, fontSize: '13px' }
const cellStyle = { padding: '14px 16px', fontSize: '14px' }

const hasMonthlyData = computed(() => (monthly.value?.length || 0) > 0)
const hasAnnualData = computed(() => (filteredAnnualMonthly.value?.length || 0) > 0)
const totalMonthly = computed(() => monthly.value?.length || 0)
const paginatedMonthly = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return monthly.value.slice(start, end)
})

const filteredAnnualMonthly = computed(() => {
  if (!annualMonthly.value || annualMonthly.value.length === 0) return []
  
  return annualMonthly.value.filter(row => {
    return row.base_salary !== 0 ||
           row.performance_salary !== 0 ||
           row.high_temp_allowance !== 0 ||
           row.low_temp_allowance !== 0 ||
           row.computer_allowance !== 0 ||
           row.meal_allowance !== 0 ||
           row.mid_autumn_benefit !== 0 ||
           row.dragon_boat_benefit !== 0 ||
           row.spring_festival_benefit !== 0 ||
           row.other_income !== 0 ||
           row.pension_insurance !== 0 ||
           row.medical_insurance !== 0 ||
           row.unemployment_insurance !== 0 ||
           row.critical_illness_insurance !== 0 ||
           row.enterprise_annuity !== 0 ||
           row.housing_fund !== 0 ||
           row.other_deductions !== 0 ||
           row.income_total !== 0 ||
           row.deductions_total !== 0 ||
           row.benefits_total !== 0 ||
           row.actual_take_home !== 0
  })
})

const annualWithTotal = computed(() => {
  if (filteredAnnualMonthly.value.length === 0) return []
  
  const total = {
    month: '合计',
    base_salary: 0,
    performance_salary: 0,
    high_temp_allowance: 0,
    low_temp_allowance: 0,
    computer_allowance: 0,
    meal_allowance: 0,
    mid_autumn_benefit: 0,
    dragon_boat_benefit: 0,
    spring_festival_benefit: 0,
    other_income: 0,
    pension_insurance: 0,
    medical_insurance: 0,
    unemployment_insurance: 0,
    critical_illness_insurance: 0,
    enterprise_annuity: 0,
    housing_fund: 0,
    other_deductions: 0,
    income_total: 0,
    deductions_total: 0,
    benefits_total: 0,
    actual_take_home: 0,
  }
  
  filteredAnnualMonthly.value.forEach(row => {
    total.base_salary += row.base_salary
    total.performance_salary += row.performance_salary
    total.high_temp_allowance += row.high_temp_allowance
    total.low_temp_allowance += row.low_temp_allowance
    total.computer_allowance += row.computer_allowance
    total.meal_allowance += row.meal_allowance
    total.mid_autumn_benefit += row.mid_autumn_benefit
    total.dragon_boat_benefit += row.dragon_boat_benefit
    total.spring_festival_benefit += row.spring_festival_benefit
    total.other_income += row.other_income
    total.pension_insurance += row.pension_insurance
    total.medical_insurance += row.medical_insurance
    total.unemployment_insurance += row.unemployment_insurance
    total.critical_illness_insurance += row.critical_illness_insurance
    total.enterprise_annuity += row.enterprise_annuity
    total.housing_fund += row.housing_fund
    total.other_deductions += row.other_deductions
    total.income_total += row.income_total
    total.deductions_total += row.deductions_total
    total.benefits_total += row.benefits_total
    total.actual_take_home += row.actual_take_home
  })
  
  return [...filteredAnnualMonthly.value, total]
})

async function load() {
  loading.value = true
  error.value = null
  try {
    if (activeTab.value === 'monthly') {
      monthly.value = await stats.loadMonthlyTable()
      currentPage.value = 1
    } else {
      annualMonthly.value = await stats.loadAnnualMonthlyTable()
    }
  } catch (e) {
    error.value = e
  } finally {
    loading.value = false
  }
}

function exportCSV() {
  try {
    let csvContent = ''
    let filename = ''
    
    if (activeTab.value === 'monthly') {
      filename = `月度明细_${stats.year}.csv`
      
      const headers = [
        '姓名', '年份', '月份',
        '基本工资', '绩效工资', '高温补贴', '低温补贴', '电脑补贴', '餐补',
        '中秋福利', '端午福利', '春节福利', '其他收入',
        '养老保险', '医疗保险', '失业保险', '大病互助', '企业年金', '住房公积金', '其他扣除',
        '收入合计', '扣除合计', '福利合计', '实际到手'
      ]
      csvContent = headers.join(',') + '\n'
      
      monthly.value.forEach(row => {
        const values = [
          `"${row.person_name}"`,
          row.year,
          row.month,
          row.base_salary,
          row.performance_salary,
          row.high_temp_allowance,
          row.low_temp_allowance,
          row.computer_allowance,
          row.meal_allowance,
          row.mid_autumn_benefit,
          row.dragon_boat_benefit,
          row.spring_festival_benefit,
          row.other_income,
          row.pension_insurance,
          row.medical_insurance,
          row.unemployment_insurance,
          row.critical_illness_insurance,
          row.enterprise_annuity,
          row.housing_fund,
          row.other_deductions,
          row.income_total,
          row.deductions_total,
          row.benefits_total,
          row.actual_take_home
        ]
        csvContent += values.join(',') + '\n'
      })
    } else {
      filename = `年度汇总_${stats.year}.csv`
      
      const headers = [
        '月份',
        '基本工资', '绩效工资', '高温补贴', '低温补贴', '电脑补贴', '餐补',
        '中秋福利', '端午福利', '春节福利', '其他收入',
        '养老保险', '医疗保险', '失业保险', '大病互助', '企业年金', '住房公积金', '其他扣除',
        '收入合计', '扣除合计', '福利合计', '实际到手'
      ]
      csvContent = headers.join(',') + '\n'
      
      annualWithTotal.value.forEach(row => {
        const values = [
          row.month === '合计' ? '合计' : `${row.month}月`,
          row.base_salary,
          row.performance_salary,
          row.high_temp_allowance,
          row.low_temp_allowance,
          row.computer_allowance,
          row.meal_allowance,
          row.mid_autumn_benefit,
          row.dragon_boat_benefit,
          row.spring_festival_benefit,
          row.other_income,
          row.pension_insurance,
          row.medical_insurance,
          row.unemployment_insurance,
          row.critical_illness_insurance,
          row.enterprise_annuity,
          row.housing_fund,
          row.other_deductions,
          row.income_total,
          row.deductions_total,
          row.benefits_total,
          row.actual_take_home
        ]
        csvContent += values.join(',') + '\n'
      })
    }
    
    const BOM = '\uFEFF'
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.click()
    URL.revokeObjectURL(link.href)
  } catch (error) {
    console.error('Export failed:', error)
  }
}

function handlePageChange(page) {
  currentPage.value = page
}

function handleTabChange() {
  load()
}

onMounted(load)
watch(() => [stats.personId, stats.year, stats.month], () => { stats.invalidate(); load() }, { deep: true })
watch(() => stats.refreshToken, () => { load() })
</script>

<template>
  <div class="table-view">
    <!-- Tab Header with Export -->
    <div class="actions-bar">
      <div class="tabs-header">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'monthly' }"
          @click="activeTab = 'monthly'; handleTabChange()"
        >
          月度明细
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'annual' }"
          @click="activeTab = 'annual'; handleTabChange()"
        >
          年度汇总
        </button>
      </div>
      <el-button type="primary" @click="exportCSV" :disabled="loading || (!hasMonthlyData && !hasAnnualData)">
        <Download :size="16" style="margin-right: 6px;" />
        导出数据
      </el-button>
    </div>

    <!-- Loading -->
    <div v-if="loading" style="padding: 32px; text-align: center;">
      <el-skeleton :rows="6" animated />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="empty-container">
      <p>加载失败，请重试</p>
      <el-button type="primary" @click="load">重试</el-button>
    </div>

    <!-- Empty State -->
    <div v-else-if="activeTab === 'monthly' && !hasMonthlyData" class="empty-container">
      <div class="empty-icon">📊</div>
      <h3 class="empty-title">暂无统计信息记录</h3>
      <p class="empty-description">当前筛选条件下没有找到任何工资记录</p>
    </div>

    <div v-else-if="activeTab === 'annual' && !hasAnnualData" class="empty-container">
      <div class="empty-icon">📊</div>
      <h3 class="empty-title">暂无统计信息记录</h3>
      <p class="empty-description">{{ stats.year }}年还没有工资记录</p>
    </div>

    <!-- Monthly Details Table -->
    <el-card shadow="hover" v-else-if="activeTab === 'monthly' && hasMonthlyData">
      <div class="table-scroll-x">
        <el-table 
          :data="paginatedMonthly" 
          border 
          stripe 
          height="500" 
          table-layout="fixed" 
          :header-cell-style="headerCellStyle" 
          :cell-style="cellStyle"
        >
          <el-table-column prop="person_name" label="姓名" width="160" min-width="160" fixed show-overflow-tooltip />
          <el-table-column prop="year" label="年份" width="100" min-width="100" sortable align="center" />
          <el-table-column prop="month" label="月份" width="100" min-width="100" sortable align="center">
            <template #default="{ row }">{{ String(row.month).padStart(2, '0') }}</template>
          </el-table-column>

          <!-- Income fields -->
          <el-table-column prop="base_salary" label="基本工资" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.base_salary) }}</template>
          </el-table-column>
          <el-table-column prop="performance_salary" label="绩效工资" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.performance_salary) }}</template>
          </el-table-column>
          <el-table-column prop="high_temp_allowance" label="高温补贴" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.high_temp_allowance) }}</template>
          </el-table-column>
          <el-table-column prop="low_temp_allowance" label="低温补贴" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.low_temp_allowance) }}</template>
          </el-table-column>
          <el-table-column prop="computer_allowance" label="电脑补贴" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.computer_allowance) }}</template>
          </el-table-column>
          <el-table-column prop="meal_allowance" label="餐补" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.meal_allowance) }}</template>
          </el-table-column>
          <el-table-column prop="mid_autumn_benefit" label="中秋福利" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.mid_autumn_benefit) }}</template>
          </el-table-column>
          <el-table-column prop="dragon_boat_benefit" label="端午福利" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.dragon_boat_benefit) }}</template>
          </el-table-column>
          <el-table-column prop="spring_festival_benefit" label="春节福利" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.spring_festival_benefit) }}</template>
          </el-table-column>
          <el-table-column prop="other_income" label="其他收入" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.other_income) }}</template>
          </el-table-column>

          <!-- Deduction fields -->
          <el-table-column prop="pension_insurance" label="养老保险" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.pension_insurance) }}</template>
          </el-table-column>
          <el-table-column prop="medical_insurance" label="医疗保险" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.medical_insurance) }}</template>
          </el-table-column>
          <el-table-column prop="unemployment_insurance" label="失业保险" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.unemployment_insurance) }}</template>
          </el-table-column>
          <el-table-column prop="critical_illness_insurance" label="大病互助" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.critical_illness_insurance) }}</template>
          </el-table-column>
          <el-table-column prop="enterprise_annuity" label="企业年金" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.enterprise_annuity) }}</template>
          </el-table-column>
          <el-table-column prop="housing_fund" label="住房公积金" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.housing_fund) }}</template>
          </el-table-column>
          <el-table-column prop="other_deductions" label="其他扣除" width="140" min-width="120" sortable align="right">
            <template #default="{ row }">{{ formatCurrency(row.other_deductions) }}</template>
          </el-table-column>

          <!-- Totals -->
          <el-table-column prop="income_total" label="收入合计" width="150" min-width="140" sortable align="right" class-name="highlight-col">
            <template #default="{ row }">{{ formatCurrency(row.income_total) }}</template>
          </el-table-column>
          <el-table-column prop="deductions_total" label="扣除合计" width="150" min-width="140" sortable align="right" class-name="highlight-col">
            <template #default="{ row }">{{ formatCurrency(row.deductions_total) }}</template>
          </el-table-column>
          <el-table-column prop="benefits_total" label="福利合计" width="150" min-width="140" sortable align="right" class-name="highlight-col">
            <template #default="{ row }">{{ formatCurrency(row.benefits_total) }}</template>
          </el-table-column>
          <el-table-column prop="actual_take_home" label="实际到手" width="150" min-width="140" sortable align="right" class-name="highlight-strong">
            <template #default="{ row }">{{ formatCurrency(row.actual_take_home) }}</template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- Pagination -->
      <div class="pagination-wrapper" v-if="totalMonthly > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalMonthly"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Annual Summary Table -->
    <el-card shadow="hover" v-else-if="activeTab === 'annual' && hasAnnualData">
      <div class="table-scroll-x">
        <el-table 
          :data="annualWithTotal" 
          border 
          stripe 
          height="520" 
          table-layout="fixed" 
          :header-cell-style="headerCellStyle" 
          :cell-style="cellStyle"
          :row-class-name="({ row }) => row.month === '合计' ? 'total-row' : ''"
        >
          <el-table-column prop="month" label="月份" width="120" min-width="120" fixed align="center">
            <template #default="{ row }">
              <strong v-if="row.month === '合计'">{{ row.month }}</strong>
              <span v-else>{{ row.month }}月</span>
            </template>
          </el-table-column>

          <!-- Income fields -->
          <el-table-column prop="base_salary" label="基本工资" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.base_salary) }}</template>
          </el-table-column>
          <el-table-column prop="performance_salary" label="绩效工资" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.performance_salary) }}</template>
          </el-table-column>
          <el-table-column prop="high_temp_allowance" label="高温补贴" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.high_temp_allowance) }}</template>
          </el-table-column>
          <el-table-column prop="low_temp_allowance" label="低温补贴" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.low_temp_allowance) }}</template>
          </el-table-column>
          <el-table-column prop="computer_allowance" label="电脑补贴" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.computer_allowance) }}</template>
          </el-table-column>
          <el-table-column prop="meal_allowance" label="餐补" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.meal_allowance) }}</template>
          </el-table-column>
          <el-table-column prop="mid_autumn_benefit" label="中秋福利" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.mid_autumn_benefit) }}</template>
          </el-table-column>
          <el-table-column prop="dragon_boat_benefit" label="端午福利" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.dragon_boat_benefit) }}</template>
          </el-table-column>
          <el-table-column prop="spring_festival_benefit" label="春节福利" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.spring_festival_benefit) }}</template>
          </el-table-column>
          <el-table-column prop="other_income" label="其他收入" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.other_income) }}</template>
          </el-table-column>

          <!-- Deduction fields -->
          <el-table-column prop="pension_insurance" label="养老保险" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.pension_insurance) }}</template>
          </el-table-column>
          <el-table-column prop="medical_insurance" label="医疗保险" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.medical_insurance) }}</template>
          </el-table-column>
          <el-table-column prop="unemployment_insurance" label="失业保险" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.unemployment_insurance) }}</template>
          </el-table-column>
          <el-table-column prop="critical_illness_insurance" label="大病互助" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.critical_illness_insurance) }}</template>
          </el-table-column>
          <el-table-column prop="enterprise_annuity" label="企业年金" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.enterprise_annuity) }}</template>
          </el-table-column>
          <el-table-column prop="housing_fund" label="住房公积金" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.housing_fund) }}</template>
          </el-table-column>
          <el-table-column prop="other_deductions" label="其他扣除" width="140" min-width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.other_deductions) }}</template>
          </el-table-column>

          <!-- Totals -->
          <el-table-column prop="income_total" label="收入合计" width="150" min-width="140" align="right" class-name="highlight-col">
            <template #default="{ row }">{{ formatCurrency(row.income_total) }}</template>
          </el-table-column>
          <el-table-column prop="deductions_total" label="扣除合计" width="150" min-width="140" align="right" class-name="highlight-col">
            <template #default="{ row }">{{ formatCurrency(row.deductions_total) }}</template>
          </el-table-column>
          <el-table-column prop="benefits_total" label="福利合计" width="150" min-width="140" align="right" class-name="highlight-col">
            <template #default="{ row }">{{ formatCurrency(row.benefits_total) }}</template>
          </el-table-column>
          <el-table-column prop="actual_take_home" label="实际到手" width="150" min-width="140" align="right" class-name="highlight-strong">
            <template #default="{ row }">{{ formatCurrency(row.actual_take_home) }}</template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.table-view {
  min-height: 400px;
}

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

:deep(.el-card__header) {
  padding: 18px 20px;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-card__body) {
  padding: 20px;
}

.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
  flex-wrap: wrap;
}

.tabs-header {
  display: flex;
  gap: 8px;
  background: #f9fafb;
  padding: 4px;
  border-radius: 8px;
}

.tab-btn {
  padding: 8px 20px;
  border: none;
  background: transparent;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.tab-btn.active {
  background: white;
  color: #3b82f6;
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.table-scroll-x {
  overflow-x: auto;
  width: 100%;
  min-width: 0;
}

.pagination-wrapper {
  padding: 16px;
  display: flex;
  justify-content: center;
  border-top: 1px solid #e5e7eb;
}

:deep(.el-table) {
  border-radius: 8px;
  min-width: max-content;
}

:deep(.el-table th) {
  background: #f9fafb;
}

:deep(.el-table .cell) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.el-table .highlight-col) .cell {
  background: rgba(251, 191, 36, 0.08);
  font-weight: 600;
}

:deep(.el-table .highlight-strong) .cell {
  background: linear-gradient(135deg, rgba(5, 150, 105, 0.1) 0%, rgba(16, 185, 129, 0.15) 100%);
  font-weight: 700;
  color: #059669;
}

:deep(.el-table .total-row) {
  background: #f3f4f6;
  font-weight: 700;
}

:deep(.el-table .total-row) td {
  border-top: 2px solid #d1d5db;
}

.empty-container {
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.5rem;
}

.empty-description {
  color: #6b7280;
  margin-bottom: 1.5rem;
}

@media (max-width: 768px) {
  .actions-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .tabs-header {
    justify-content: space-around;
  }
  
  .tab-btn {
    flex: 1;
  }
}
</style>
