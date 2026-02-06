<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import api from '../utils/axios'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowLeft, Settings } from 'lucide-vue-next'

import SalaryStatsCards from '../components/salary/SalaryStatsCards.vue'
import SalaryFilter from '../components/salary/SalaryFilter.vue'
import SalaryTable from '../components/salary/SalaryTable.vue'
import SalaryFormDialog from '../components/salary/SalaryFormDialog.vue'
import PageContainer from '../components/PageContainer.vue'

const route = useRoute()
const router = useRouter()
const personId = ref(Number(route.params.personId))
const personName = ref('')
const list = ref([])
const filteredList = ref([])
const dialogVisible = ref(false)
const loading = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const editingData = ref(null)

const filterYear = ref(null)
const filterMonth = ref(null)

const customFields = ref([])

const stats = computed(() => {
  if (filteredList.value.length === 0) return { total: 0, average: 0, latest: 0 }

  const total = filteredList.value.reduce((sum, item) => sum + (item.actual_take_home || 0), 0)
  const average = total / filteredList.value.length
  const latest = filteredList.value.length > 0 ? (filteredList.value[0].actual_take_home || 0) : 0

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
    const { data: fieldsData } = await api.get('/salary-fields/')
    customFields.value = fieldsData

    const { data } = await api.get('/salaries/', { params: { person_id: personId.value } })
    list.value = data

    const { data: persons } = await api.get('/persons/')
    const person = persons.find(p => p.id === personId.value)
    personName.value = person ? person.name : `人员 ${personId.value}`
  } catch {
    ElMessage.error('加载工资记录失败')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEditing.value = false
  editingId.value = null
  editingData.value = null
  dialogVisible.value = true
}

function openEdit(salary) {
  isEditing.value = true
  editingId.value = salary.id
  editingData.value = salary
  dialogVisible.value = true
}

async function handleSubmit(formData) {
  if (formData.base_salary < 0) {
    ElMessage.warning('基础工资不能为负数')
    return
  }

  try {
    if (isEditing.value) {
      const { data } = await api.put(`/salaries/${editingId.value}`, formData)
      const index = list.value.findIndex(item => item.id === editingId.value)
      if (index !== -1) {
        list.value[index] = data
      }
      ElMessage.success('工资记录更新成功')
    } else {
      await api.post(`/salaries/${personId.value}`, formData)
      ElMessage.success('工资记录添加成功')
    }
    // Reload data to get computed fields like actual_take_home
    await load()
    dialogVisible.value = false
  } catch (error) {
    if (error.response) {
      ElMessage.error(`操作失败: ${error.response.data.detail || '服务器错误'}`)
    } else {
      ElMessage.error('操作工资记录失败，请检查网络连接')
    }
  }
}

async function handleDelete(salary) {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${salary.year}年${salary.month}月 的工资记录吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await api.delete(`/salaries/${salary.id}`)
    ElMessage.success('删除成功')
    await load()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function clearFilters() {
  filterYear.value = null
  filterMonth.value = null
}

function goBack() {
  router.push('/persons')
}

function goToFieldSettings() {
  router.push('/salary-fields')
}

watch(() => route.params.personId, (v) => {
  personId.value = Number(v)
  load()
})

onMounted(load)
</script>

<template>
  <PageContainer>
    <!-- Header -->
    <header class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">
          <ArrowLeft :size="16" />
          <span>返回</span>
        </button>
        <div class="header-title">
          <h1>{{ personName }}</h1>
          <p class="header-subtitle">工资记录管理</p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="goToFieldSettings">
          <Settings :size="16" />
          <span>字段管理</span>
        </button>
        <button class="btn btn-primary" @click="openCreate">
          <Plus :size="16" />
          <span>添加记录</span>
        </button>
      </div>
    </header>

    <!-- Stats Cards -->
    <SalaryStatsCards :stats="stats" />

    <!-- Filter -->
    <SalaryFilter
      v-model:model-year="filterYear"
      v-model:model-month="filterMonth"
      :year-options="yearOptions"
      @clear="clearFilters"
    />

    <!-- Table -->
    <SalaryTable
      :salaries="filteredList"
      :loading="loading"
      @edit="openEdit"
      @delete="handleDelete"
    />

    <!-- Form Dialog -->
    <SalaryFormDialog
      v-model:visible="dialogVisible"
      :is-editing="isEditing"
      :initial-data="editingData"
      :custom-fields="customFields"
      @submit="handleSubmit"
      @manage-fields="goToFieldSettings"
    />
  </PageContainer>
</template>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2.5rem;
  gap: 1rem;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  background: transparent;
  border: 1px solid #e5e0dc;
  border-radius: 8px;
  color: #6b6560;
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s ease;
  width: fit-content;
}

.back-btn:hover {
  background: #faf5f3;
  color: #2d2a26;
  border-color: #d5d0cc;
}

.header-title h1 {
  font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
  font-size: 1.875rem;
  font-weight: 500;
  color: #2d2a26;
  margin: 0;
  letter-spacing: -0.02em;
}

.header-subtitle {
  font-size: 0.9375rem;
  color: #6b6560;
  margin: 0.25rem 0 0 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-primary {
  background: #da7756;
  border: 1px solid #da7756;
  color: white;
}

.btn-primary:hover {
  background: #c4684a;
  border-color: #c4684a;
}

.btn-secondary {
  background: white;
  border: 1px solid #e5e0dc;
  color: #2d2a26;
}

.btn-secondary:hover {
  background: #faf5f3;
  border-color: #d5d0cc;
}

@media (max-width: 768px) {
  .page-container {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .btn {
    flex: 1;
    justify-content: center;
  }
}
</style>
