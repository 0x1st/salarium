<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useStatsStore } from '../../store/stats'
import { formatCurrency, formatPercent } from '../../utils/number'

const stats = useStatsStore()
const monthly = ref([])
const annual = ref([])
const loading = ref(false)
const error = ref(null)

const hasData = computed(() => (monthly.value?.length || 0) > 0 || (annual.value?.length || 0) > 0)

async function load() {
  loading.value = true
  error.value = null
  try {
    monthly.value = await stats.loadMonthlyTable()
    annual.value = await stats.loadAnnualTable()
  } catch (e) { error.value = e } finally { loading.value = false }
}

function exportCSV() {
  const headers = [
    '姓名','年份','月份',
    // income
    '基本工资','绩效工资','高温补贴','低温补贴','电脑补贴','餐补','中秋福利','端午福利','春节福利','其他收入','福利合计','收入合计',
    // deductions
    '养老保险','医疗保险','失业保险','大病互助保险','企业年金','住房公积金','其他扣除','扣除合计','个税',
    // totals
    '实际到手金额','备注'
  ]
  const rows = monthly.value.map(r => [
    r.person_name, r.year, r.month,
    r.base_salary, r.performance_salary, r.high_temp_allowance, r.low_temp_allowance, r.computer_allowance, r.meal_allowance, r.mid_autumn_benefit, r.dragon_boat_benefit, r.spring_festival_benefit, r.other_income, r.benefits_total, r.income_total,
    r.pension_insurance, r.medical_insurance, r.unemployment_insurance, r.critical_illness_insurance, r.enterprise_annuity, r.housing_fund, r.other_deductions, r.deductions_total, r.tax,
    r.actual_take_home, r.note || ''
  ])
  const csv = [headers, ...rows].map(r => r.map(v => (typeof v === 'string' ? '"' + v.replace(/"/g,'""') + '"' : v)).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `月度明细_${stats.year}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(load)
// Reload when filters change
watch(() => [stats.personId, stats.year, stats.range], () => { stats.invalidate(); load() }, { deep: true })
// Reload on external invalidation
watch(() => stats.refreshToken, () => { load() })
</script>

<template>
  <div class="tables">
    <!-- Loading -->
    <div v-if="loading" style="padding: 16px">
      <el-skeleton :rows="6" animated />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="empty">
      <p>加载失败，请重试</p>
      <el-button type="primary" @click="load">重试</el-button>
    </div>

    <!-- Empty State -->
    <div v-else-if="!hasData" class="empty-container">
      <div class="empty-icon">📊</div>
      <h3 class="empty-title">暂无统计信息记录</h3>
      <p class="empty-description">当前筛选条件下没有可显示的数据</p>
    </div>

    <!-- Tables -->
    <template v-else>
      <el-card shadow="hover" style="margin-bottom: 16px" v-if="monthly.length > 0">
        <template #header>
          <div class="card-header">
            <span class="card-title">月度明细表</span>
            <div>
              <el-button type="primary" @click="exportCSV">导出 CSV</el-button>
            </div>
          </div>
        </template>

        <el-table :data="monthly" border stripe height="420">
          <el-table-column prop="person_name" label="姓名" width="120" fixed />
          <el-table-column prop="year" label="年份" width="90" sortable />
          <el-table-column prop="month" label="月份" width="90" sortable />

          <!-- income fields -->
          <el-table-column prop="base_salary" label="基本工资" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.base_salary) }}</template>
          </el-table-column>
          <el-table-column prop="performance_salary" label="绩效工资" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.performance_salary) }}</template>
          </el-table-column>
          <el-table-column prop="high_temp_allowance" label="高温补贴" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.high_temp_allowance) }}</template>
          </el-table-column>
          <el-table-column prop="low_temp_allowance" label="低温补贴" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.low_temp_allowance) }}</template>
          </el-table-column>
          <el-table-column prop="computer_allowance" label="电脑补贴" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.computer_allowance) }}</template>
          </el-table-column>
          <el-table-column prop="meal_allowance" label="餐补" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.meal_allowance) }}</template>
          </el-table-column>
          <el-table-column prop="mid_autumn_benefit" label="中秋福利" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.mid_autumn_benefit) }}</template>
          </el-table-column>
          <el-table-column prop="dragon_boat_benefit" label="端午福利" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.dragon_boat_benefit) }}</template>
          </el-table-column>
          <el-table-column prop="spring_festival_benefit" label="春节福利" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.spring_festival_benefit) }}</template>
          </el-table-column>
          <el-table-column prop="other_income" label="其他收入" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.other_income) }}</template>
          </el-table-column>

          <!-- deduction fields -->
          <el-table-column prop="pension_insurance" label="养老保险" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.pension_insurance) }}</template>
          </el-table-column>
          <el-table-column prop="medical_insurance" label="医疗保险" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.medical_insurance) }}</template>
          </el-table-column>
          <el-table-column prop="unemployment_insurance" label="失业保险" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.unemployment_insurance) }}</template>
          </el-table-column>
          <el-table-column prop="critical_illness_insurance" label="大病互助保险" width="140" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.critical_illness_insurance) }}</template>
          </el-table-column>
          <el-table-column prop="enterprise_annuity" label="企业年金" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.enterprise_annuity) }}</template>
          </el-table-column>
          <el-table-column prop="housing_fund" label="住房公积金" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.housing_fund) }}</template>
          </el-table-column>
          <el-table-column prop="other_deductions" label="其他扣除" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.other_deductions) }}</template>
          </el-table-column>

          <!-- totals -->
          <el-table-column prop="benefits_total" label="福利合计" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.benefits_total) }}</template>
          </el-table-column>
          <el-table-column prop="income_total" label="收入合计" width="140" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.income_total) }}</template>
          </el-table-column>
          <el-table-column prop="deductions_total" label="扣除合计" width="140" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.deductions_total) }}</template>
          </el-table-column>
          <el-table-column prop="tax" label="个税" width="120" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.tax) }}</template>
          </el-table-column>
          <el-table-column prop="actual_take_home" label="实际到手金额" width="160" sortable align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.actual_take_home) }}</template>
          </el-table-column>
          <el-table-column prop="note" label="备注" min-width="160" show-overflow-tooltip />
        </el-table>
      </el-card>

      <el-card shadow="hover" v-if="annual.length > 0">
        <template #header>
          <div class="card-header">
            <span class="card-title">年度汇总表</span>
          </div>
        </template>

        <el-table :data="annual" border stripe>
          <el-table-column prop="person_name" label="姓名" width="120" />

          <!-- income totals -->
          <el-table-column prop="base_salary_total" label="基本工资" width="120" align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.base_salary_total) }}</template>
          </el-table-column>
          <el-table-column prop="performance_salary_total" label="绩效工资" width="120" align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.performance_salary_total) }}</template>
          </el-table-column>
          <el-table-column prop="high_temp_allowance_total" label="高温补贴" width="120" align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.high_temp_allowance_total) }}</template>
          </el-table-column>
          <el-table-column prop="low_temp_allowance_total" label="低温补贴" width="120" align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.low_temp_allowance_total) }}</template>
          </el-table-column>
          <el-table-column prop="computer_allowance_total" label="电脑补贴" width="120" align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.computer_allowance_total) }}</template>
          </el-table-column>
          <el-table-column prop="meal_allowance_total" label="餐补" width="120" align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.meal_allowance_total) }}</template>
          </el-table-column>
          <el-table-column prop="mid_autumn_benefit_total" label="中秋福利" width="120" align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.mid_autumn_benefit_total) }}</template>
          </el-table-column>
          <el-table-column prop="dragon_boat_benefit_total" label="端午福利" width="120" align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.dragon_boat_benefit_total) }}</template>
          </el-table-column>
          <el-table-column prop="spring_festival_benefit_total" label="春节福利" width="120" align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.spring_festival_benefit_total) }}</template>
          </el-table-column>
          <el-table-column prop="other_income_total" label="其他收入" width="120" align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.other_income_total) }}</template>
          </el-table-column>

          <!-- deduction totals -->
          <el-table-column prop="pension_insurance_total" label="养老保险" width="120" align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.pension_insurance_total) }}</template>
          </el-table-column>
          <el-table-column prop="medical_insurance_total" label="医疗保险" width="120" align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.medical_insurance_total) }}</template>
          </el-table-column>
          <el-table-column prop="unemployment_insurance_total" label="失业保险" width="120" align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.unemployment_insurance_total) }}</template>
          </el-table-column>
          <el-table-column prop="critical_illness_insurance_total" label="大病互助保险" width="140" align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.critical_illness_insurance_total) }}</template>
          </el-table-column>
          <el-table-column prop="enterprise_annuity_total" label="企业年金" width="120" align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.enterprise_annuity_total) }}</template>
          </el-table-column>
          <el-table-column prop="housing_fund_total" label="住房公积金" width="120" align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.housing_fund_total) }}</template>
          </el-table-column>
          <el-table-column prop="other_deductions_total" label="其他扣除" width="120" align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.other_deductions_total) }}</template>
          </el-table-column>

          <!-- totals -->
          <el-table-column prop="benefits_total" label="福利合计" width="140" align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.benefits_total) }}</template>
          </el-table-column>
          <el-table-column prop="income_total" label="收入合计" width="140" align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.income_total) }}</template>
          </el-table-column>
          <el-table-column prop="deductions_total" label="扣除合计" width="140" align="right" show-overflow-tooltip>
            <template #default="{ row }">-{{ formatCurrency(row.deductions_total) }}</template>
          </el-table-column>
          <el-table-column prop="actual_take_home_total" label="实际到手金额" width="160" align="right" show-overflow-tooltip>
            <template #default="{ row }">{{ formatCurrency(row.actual_take_home_total) }}</template>
          </el-table-column>
          <el-table-column prop="yoy_growth" label="增长率" width="120" sortable align="right">
            <template #default="{ row }">{{ formatPercent(row.yoy_growth, { decimals: 1 }) }}</template>
          </el-table-column>
        </el-table>
      </el-card>
    </template>
  </div>
</template>

<style scoped>
.card-header { display:flex; justify-content: space-between; align-items:center }
.card-title { font-weight: 600 }

/* Empty state reused style (aligned with Salaries/Persons) */
.empty-container { padding: 3rem; text-align: center; }
.empty-icon { font-size: 4rem; margin-bottom: 1rem; }
.empty-title { font-size: 1.5rem; font-weight: 600; color: #111827; margin-bottom: 0.5rem; }
.empty-description { color: #6b7280; margin-bottom: 1.5rem; }
</style>
