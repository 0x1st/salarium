<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import api from '../utils/axios'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  DollarSign, 
  Calendar, 
  TrendingUp, 
  Award, 
  Shield, 
  Calculator, 
  Trash2, 
  ArrowLeft,
  User,
  FileText,
  Edit,
  Filter
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const user = useUserStore()
const personId = ref(Number(route.params.personId))
const personName = ref('')
const list = ref([])
const filteredList = ref([])
const dialogVisible = ref(false)
const loading = ref(false)
const isEditing = ref(false)
const editingId = ref(null)

const filterYear = ref(null)
const filterMonth = ref(null)

const form = ref({
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1,
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
  tax: 0,
  note: '',
})


const stats = computed(() => {
  if (filteredList.value.length === 0) return { total: 0, average: 0, latest: 0 }
  
  const total = filteredList.value.reduce((sum, item) => sum + (item.net_income || 0), 0)
  const average = total / filteredList.value.length
  const latest = filteredList.value.length > 0 ? (filteredList.value[0].net_income || 0) : 0
  
  return { total, average, latest }
})

const yearOptions = computed(() => {
  const years = [...new Set(list.value.map(item => item.year))].sort((a, b) => b - a)
  return years
})

const filterData = () => {
  let filtered = [...list.value]
  
  if (filterYear.value) {
    filtered = filtered.filter(item => item.year === filterYear.value)
  }
  
  if (filterMonth.value) {
    filtered = filtered.filter(item => item.month === filterMonth.value)
  }
  
  filtered.sort((a, b) => {
    if (a.year !== b.year) return b.year - a.year
    return b.month - a.month
  })
  
  filteredList.value = filtered
}

watch([filterYear, filterMonth], filterData)
watch(list, filterData, { immediate: true })

async function load() {
  if (!personId.value) return
  loading.value = true
  try {
    const { data } = await api.get('/salaries/', { params: { person_id: personId.value } })
    list.value = data
    
    const { data: persons } = await api.get('/persons/')
    const person = persons.find(p => p.id === personId.value)
    personName.value = person ? person.name : `人员 ${personId.value}`
  } catch (error) {
    ElMessage.error('加载工资记录失败')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEditing.value = false
  editingId.value = null
  form.value = {
    year: new Date().getFullYear(),
    month: new Date().getMonth() + 1,
    base_salary: 0,
    performance_salary: 0,
    high_temp_allowance: 0,
    low_temp_allowance: 0,
    computer_allowance: 0,
    communication_allowance: 0,
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
    labor_union_fee: 0,
    tax: 0,
    note: '',
  }
  dialogVisible.value = true
}

function openEdit(salary) {
  isEditing.value = true
  editingId.value = salary.id
  form.value = {
    year: salary.year,
    month: salary.month,
    base_salary: salary.base_salary,
    performance_salary: salary.performance_salary,
    high_temp_allowance: salary.high_temp_allowance,
    low_temp_allowance: salary.low_temp_allowance,
    computer_allowance: salary.computer_allowance,
    communication_allowance: salary.communication_allowance,
    meal_allowance: salary.meal_allowance,
    mid_autumn_benefit: salary.mid_autumn_benefit,
    dragon_boat_benefit: salary.dragon_boat_benefit,
    spring_festival_benefit: salary.spring_festival_benefit,
    other_income: salary.other_income,
    pension_insurance: salary.pension_insurance,
    medical_insurance: salary.medical_insurance,
    unemployment_insurance: salary.unemployment_insurance,
    critical_illness_insurance: salary.critical_illness_insurance,
    enterprise_annuity: salary.enterprise_annuity,
    housing_fund: salary.housing_fund,
    other_deductions: salary.other_deductions,
    labor_union_fee: salary.labor_union_fee,
    tax: salary.tax,
    note: salary.note || '',
  }
  dialogVisible.value = true
}

async function submit() {
  if (form.value.base_salary < 0) {
    ElMessage.warning('基础工资不能为负数')
    return
  }
  
  try {
    if (isEditing.value) {
      const { data } = await api.put(`/salaries/${editingId.value}`, form.value)
      const index = list.value.findIndex(item => item.id === editingId.value)
      if (index !== -1) {
        list.value[index] = data
      }
      ElMessage.success('工资记录更新成功')
      window.dispatchEvent(new CustomEvent('stats:invalidate'))
    } else {
      const { data } = await api.post(`/salaries/${personId.value}`, form.value)
      list.value.push(data)
      ElMessage.success('工资记录添加成功')
      window.dispatchEvent(new CustomEvent('stats:invalidate'))
    }
    dialogVisible.value = false
  } catch (error) {
    console.error('操作工资记录失败:', error)
    if (error.response) {
      ElMessage.error(`操作失败: ${error.response.data.detail || '服务器错误'}`)
    } else {
      ElMessage.error('操作工资记录失败，请检查网络连接')
    }
  }
}

async function remove(id, yearMonth) {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${yearMonth} 的工资记录吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await api.delete(`/salaries/${id}`)
    list.value = list.value.filter(i => i.id !== id)
    ElMessage.success('删除成功')
    window.dispatchEvent(new CustomEvent('stats:invalidate'))
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY'
  }).format(amount || 0)
}

function goBack() {
  router.push('/persons')
}

function clearFilters() {
  filterYear.value = null
  filterMonth.value = null
}

watch(() => route.params.personId, (v) => { 
  personId.value = Number(v)
  load() 
})

onMounted(load)
</script>

<template>
  <div class="salaries-container">
    <div class="page-header">
      <div class="header-content">
        <div class="header-nav">
          <button class="back-btn" @click="goBack">
            <ArrowLeft class="back-icon" />
            返回人员列表
          </button>
        </div>
        <div class="header-title">
          <User class="title-icon" />
          <div>
            <h1>{{ personName }} - 工资记录</h1>
            <p class="header-subtitle">管理工资明细和历史记录</p>
          </div>
        </div>
      </div>
      <button class="btn btn-primary btn-create" @click="openCreate">
        <Plus class="button-icon" />
        添加工资记录
      </button>
    </div>

    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-icon stat-icon-total">
          <DollarSign />
        </div>
        <div class="stat-content">
          <div class="stat-label">累计实发工资</div>
          <div class="stat-value">{{ formatCurrency(stats.total) }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon-average">
          <TrendingUp />
        </div>
        <div class="stat-content">
          <div class="stat-label">平均实发工资</div>
          <div class="stat-value">{{ formatCurrency(stats.average) }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon-latest">
          <Award />
        </div>
        <div class="stat-content">
          <div class="stat-label">最近实发工资</div>
          <div class="stat-value">{{ formatCurrency(stats.latest) }}</div>
        </div>
      </div>
    </div>

    <div class="table-container">
      <div class="filter-section">
        <div class="filter-header">
          <Filter class="filter-icon" />
          <h3>筛选条件</h3>
        </div>
        <div class="filter-controls">
          <div class="filter-group">
            <label class="filter-label">年份</label>
            <select v-model="filterYear" class="filter-select">
              <option :value="null">全部年份</option>
              <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}年</option>
            </select>
          </div>
          <div class="filter-group">
            <label class="filter-label">月份</label>
            <select v-model="filterMonth" class="filter-select">
              <option :value="null">全部月份</option>
              <option v-for="m in 12" :key="m" :value="m">{{ m }}月</option>
            </select>
          </div>
          <button class="btn btn-secondary btn-clear" @click="clearFilters" v-if="filterYear || filterMonth">
            清除筛选
          </button>
        </div>
      </div>

      <div class="table-content">
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>
        
        <div v-else-if="filteredList.length === 0" class="empty-container">
          <div class="empty-content">
            <div class="empty-icon">💼</div>
            <h3 class="empty-title">暂无工资记录</h3>
            <p class="empty-description">
              {{ list.length === 0 ? '还没有添加任何工资记录，点击下面的按钮开始添加' : '当前筛选条件下没有找到匹配的记录' }}
            </p>
            <el-button 
              v-if="list.length === 0"
              type="primary" 
              size="large"
              @click="openCreate"
              class="empty-action"
            >
              <Plus class="button-icon" />
              添加工资记录
            </el-button>
            <el-button 
              v-else
              type="primary" 
              size="large"
              @click="clearFilters"
              class="empty-action"
            >
              清除筛选条件
            </el-button>
          </div>
        </div>
        
        <div v-else class="table-wrapper">
  <table class="salary-table">
    <thead>
      <tr>
        <th class="col-date" scope="col">时间</th>
        <th class="col-currency" scope="col">基本工资</th>
        <th class="col-currency" scope="col">绩效工资</th>
        <th class="col-currency" scope="col">福利补贴</th>
        <th class="col-currency" scope="col">通信补贴</th>
        <th class="col-currency" scope="col">总收入</th>
        <th class="col-currency" scope="col">五险一金</th>
        <th class="col-currency" scope="col">其他扣除</th>
        <th class="col-currency" scope="col">工会</th>
        <th class="col-currency" scope="col">个税</th>
        <th class="col-currency" scope="col">实发工资</th>
        <th class="col-currency highlight" scope="col">实际到手</th>
        <th class="col-actions" scope="col">操作</th>
      </tr>
    </thead>
            <tbody>
              <tr v-for="salary in filteredList" :key="salary.id" class="table-row">
                <td class="col-date">
                  <div class="date-cell">
                    <Calendar class="date-icon" />
                    <span>{{ salary.year }}/{{ salary.month.toString().padStart(2, '0') }}</span>
                  </div>
                </td>
                <td class="col-currency">{{ formatCurrency(salary.base_salary) }}</td>
                <td class="col-currency">{{ formatCurrency(salary.performance_salary) }}</td>
                <td class="col-currency">{{ formatCurrency(
                  salary.high_temp_allowance + 
                  salary.low_temp_allowance + 
                  salary.computer_allowance +
                  salary.meal_allowance + 
                  salary.mid_autumn_benefit + 
                  salary.dragon_boat_benefit + 
                  salary.spring_festival_benefit + 
                  salary.other_income
                ) }}</td>
                <td class="col-currency">{{ formatCurrency(salary.communication_allowance) }}</td>
                <td class="col-currency">{{ formatCurrency(salary.total_income) }}</td>
                <td class="col-currency text-danger">-{{ formatCurrency(
                  salary.pension_insurance + 
                  salary.medical_insurance + 
                  salary.unemployment_insurance + 
                  salary.critical_illness_insurance + 
                  salary.enterprise_annuity + 
                  salary.housing_fund
                ) }}</td>
                <td class="col-currency text-danger">-{{ formatCurrency(salary.other_deductions) }}</td>
                <td class="col-currency text-danger">-{{ formatCurrency(salary.labor_union_fee) }}</td>
                <td class="col-currency text-danger">-{{ formatCurrency(salary.tax) }}</td>
                <td class="col-currency net-income">{{ formatCurrency(salary.net_income) }}</td>
                <td class="col-currency actual-take-home highlight">{{ formatCurrency(salary.actual_take_home) }}</td>
                <td class="col-actions">
                  <div class="action-buttons">
                    <button 
                      class="action-btn btn-edit"
                      @click="openEdit(salary)"
                      title="编辑记录"
                    >
                      <Edit class="action-icon" />
                    </button>
                    <button 
                      class="action-btn btn-delete"
                      @click="remove(salary.id, `${salary.year}年${salary.month}月`)"
                      title="删除记录"
                    >
                      <Trash2 class="action-icon" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <el-dialog 
      v-model="dialogVisible" 
      :title="isEditing ? '编辑工资记录' : '添加工资记录'"
      width="800px"
      :close-on-click-modal="false"
    >
      <form @submit.prevent="submit" class="salary-form">
        <div class="form-section">
          <h3 class="section-title">
            <Calendar class="section-icon" />
            基本信息
          </h3>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">年份</label>
              <input v-model.number="form.year" type="number" class="form-control" min="2000" max="2100" />
            </div>
            <div class="form-group">
              <label class="form-label">月份</label>
              <input v-model.number="form.month" type="number" class="form-control" min="1" max="12" />
            </div>
          </div>
        </div>

        <div class="form-section">
          <h3 class="section-title">
            <DollarSign class="section-icon" />
            收入明细
          </h3>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">基本工资</label>
              <input v-model.number="form.base_salary" type="number" class="form-control" step="0.01" min="0" />
            </div>
            <div class="form-group">
              <label class="form-label">绩效工资</label>
              <input v-model.number="form.performance_salary" type="number" class="form-control" step="0.01" min="0" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">高温补贴</label>
              <input v-model.number="form.high_temp_allowance" type="number" class="form-control" step="0.01" min="0" />
            </div>
            <div class="form-group">
              <label class="form-label">低温补贴</label>
              <input v-model.number="form.low_temp_allowance" type="number" class="form-control" step="0.01" min="0" />
            </div>
          </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">电脑补贴</label>
            <input v-model.number="form.computer_allowance" type="number" class="form-control" step="0.01" min="0" />
          </div>
          <div class="form-group">
            <label class="form-label">餐补</label>
            <input v-model.number="form.meal_allowance" type="number" class="form-control" step="0.01" min="0" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">通信补贴</label>
            <input v-model.number="form.communication_allowance" type="number" class="form-control" step="0.01" min="0" />
          </div>
        </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">中秋福利</label>
              <input v-model.number="form.mid_autumn_benefit" type="number" class="form-control" step="0.01" min="0" />
            </div>
            <div class="form-group">
              <label class="form-label">端午福利</label>
              <input v-model.number="form.dragon_boat_benefit" type="number" class="form-control" step="0.01" min="0" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">春节福利</label>
              <input v-model.number="form.spring_festival_benefit" type="number" class="form-control" step="0.01" min="0" />
            </div>
            <div class="form-group">
              <label class="form-label">其他收入</label>
              <input v-model.number="form.other_income" type="number" class="form-control" step="0.01" min="0" />
            </div>
          </div>
        </div>

        <div class="form-section">
          <h3 class="section-title">
            <Shield class="section-icon" />
            扣除明细
          </h3>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">养老保险</label>
              <input v-model.number="form.pension_insurance" type="number" class="form-control" step="0.01" min="0" />
            </div>
            <div class="form-group">
              <label class="form-label">医疗保险</label>
              <input v-model.number="form.medical_insurance" type="number" class="form-control" step="0.01" min="0" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">失业保险</label>
              <input v-model.number="form.unemployment_insurance" type="number" class="form-control" step="0.01" min="0" />
            </div>
            <div class="form-group">
              <label class="form-label">大病互助保险</label>
              <input v-model.number="form.critical_illness_insurance" type="number" class="form-control" step="0.01" min="0" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">企业年金</label>
              <input v-model.number="form.enterprise_annuity" type="number" class="form-control" step="0.01" min="0" />
            </div>
            <div class="form-group">
              <label class="form-label">住房公积金</label>
              <input v-model.number="form.housing_fund" type="number" class="form-control" step="0.01" min="0" />
            </div>
          </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">其他扣除</label>
            <input v-model.number="form.other_deductions" type="number" class="form-control" step="0.01" min="0" />
          </div>
          <div class="form-group">
            <label class="form-label">工会</label>
            <input v-model.number="form.labor_union_fee" type="number" class="form-control" step="0.01" min="0" />
          </div>
        </div>
        </div>

        <div class="form-section">
          <h3 class="section-title">
            <Calculator class="section-icon" />
            税费
          </h3>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">个人所得税</label>
              <input v-model.number="form.tax" type="number" class="form-control" step="0.01" min="0" />
            </div>
          </div>
        </div>

        <div class="form-section">
          <h3 class="section-title">
            <FileText class="section-icon" />
            备注信息
          </h3>
          <div class="form-group">
            <label class="form-label">备注</label>
            <textarea 
              v-model="form.note" 
              class="form-control textarea" 
              placeholder="请输入备注信息（可选）"
              rows="3"
              maxlength="200"
            ></textarea>
          </div>
        </div>
      </form>
      
      <template #footer>
        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="dialogVisible = false">
            取消
          </button>
          <button class="btn btn-primary" @click="submit">
            保存记录
          </button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.salaries-container {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  gap: 1rem;
}

.header-content {
  flex: 1;
}

.header-nav {
  margin-bottom: 1rem;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  color: #6b7280;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: #f9fafb;
  color: #374151;
}

.back-icon {
  width: 16px;
  height: 16px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.title-icon {
  width: 32px;
  height: 32px;
  color: #3b82f6;
}

.header-title h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.header-subtitle {
  color: #6b7280;
  font-size: 1rem;
  margin: 0.25rem 0 0 0;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon-total {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.stat-icon-average {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-icon-latest {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
}

.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.filter-section {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.filter-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.filter-icon {
  width: 20px;
  height: 20px;
  color: #3b82f6;
}

.filter-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
  white-space: nowrap;
}

.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
  min-width: 120px;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.table-content {
  padding: 1.5rem;
}

.loading-container {
  text-align: center;
  padding: 3rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-container {
  padding: 3rem;
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

.table-wrapper {
  overflow-x: auto;
}

.salary-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.salary-table th {
  background: #f9fafb;
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
  border-bottom: 2px solid #e5e7eb;
}

.salary-table td {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  font-size: 0.875rem;
}

.salary-table td.col-currency,
.salary-table th.col-currency {
  padding-right: 1rem;
}

.col-currency {
  text-align: right;
  width: 140px;
}

.salary-table th.col-currency {
  text-align: right;
}

.col-date {
  width: 120px;
}

.col-actions {
  width: 100px;
  text-align: center;
}

.date-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-icon {
  width: 16px;
  height: 16px;
  color: #6b7280;
}

.text-danger {
  color: #dc2626;
}

.net-income {
  font-weight: 600;
  color: #10b981;
}

.actual-take-home {
  font-weight: 700;
  color: #059669 !important;
  font-size: 1.05em;
  background: linear-gradient(135deg, rgba(5, 150, 105, 0.1) 0%, rgba(16, 185, 129, 0.15) 100%);
}

.highlight {
  background: rgba(251, 191, 36, 0.08);
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.action-btn {
  padding: 0.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-edit {
  background: #eff6ff;
  color: #3b82f6;
}

.btn-edit:hover {
  background: #dbeafe;
}

.btn-delete {
  background: #fef2f2;
  color: #dc2626;
}

.btn-delete:hover {
  background: #fee2e2;
}

.action-icon {
  width: 16px;
  height: 16px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-create {
  white-space: nowrap;
}

.button-icon {
  width: 16px;
  height: 16px;
}

.salary-form {
  max-height: 60vh;
  overflow-y: auto;
  padding: 0.5rem;
}

.form-section {
  margin-bottom: 2rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e5e7eb;
}

.section-icon {
  width: 20px;
  height: 20px;
  color: #3b82f6;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.form-control {
  padding: 0.625rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

.form-control:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-control:disabled {
  background: #f3f4f6;
  cursor: not-allowed;
}

.form-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.textarea {
  resize: vertical;
  min-height: 80px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }

  .stats-section {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-select {
    width: 100%;
  }
}
</style>
