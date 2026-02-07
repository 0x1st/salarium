<script setup>
import { ref, onMounted, watch, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { RefreshCw } from 'lucide-vue-next'
import { useStatsStore } from '../../store/stats'
import PageContainer from '../../components/PageContainer.vue'
import PageHeader from '../../components/PageHeader.vue'

const tabs = [
  { name: 'stats-net', label: '概览', path: '/stats/net' },
  { name: 'stats-composition', label: '收入构成', path: '/stats/composition' },
  { name: 'stats-category', label: '分类汇总', path: '/stats/category' },
  { name: 'stats-deductions', label: '扣除分析', path: '/stats/deductions' },
  { name: 'stats-cumulative', label: '累计贡献', path: '/stats/cumulative' },
  { name: 'stats-table', label: '明细表', path: '/stats/table' },
]

const route = useRoute()
const router = useRouter()
const stats = useStatsStore()

const activeTab = ref('stats-net')

const personFilter = computed({
  get: () => stats.personId,
  set: (value) => stats.setPerson(value ?? null),
})

const monthFilter = computed({
  get: () => stats.month,
  set: (value) => stats.setMonth(value ?? null),
})

let _removeInvalidateListener = null
onMounted(async () => {
  await stats.ensurePersons()
  // Set initial activeTab from route
  if (route.name) {
    activeTab.value = route.name
  }
  const handler = () => stats.refreshAll()
  window.addEventListener('stats:invalidate', handler)
  _removeInvalidateListener = () => window.removeEventListener('stats:invalidate', handler)
})

onBeforeUnmount(() => {
  if (_removeInvalidateListener) _removeInvalidateListener()
})

// Watch route changes and update activeTab
watch(() => route.name, (newName) => {
  if (newName && newName !== activeTab.value) {
    activeTab.value = newName
    setTimeout(() => window.dispatchEvent(new Event('resize')), 0)
  }
})

// Watch activeTab changes and navigate
watch(activeTab, (newTab) => {
  const targetTab = tabs.find(t => t.name === newTab)
  if (targetTab && route.path !== targetTab.path) {
    router.push(targetTab.path)
  }
})
</script>

<template>
  <PageContainer>
    <PageHeader title="统计分析" subtitle="数据统计分析">
      <template #controls>
        <el-form class="toolbar-filters" :inline="true" size="small">
          <el-form-item class="toolbar-field">
            <el-select
              v-model="personFilter"
              placeholder="请选择用户"
              class="filter-control"
              size="small"
              clearable
              filterable
              :loading="stats.loadingPersons"
            >
              <el-option
                v-for="p in stats.persons"
                :key="p.id"
                :label="p.name"
                :value="p.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item class="toolbar-field">
            <el-input-number
              v-model="stats.year"
              class="filter-control"
              size="small"
              :min="2000"
              :max="2100"
              controls-position="right"
            />
          </el-form-item>

          <el-form-item class="toolbar-field">
            <el-select
              v-model="monthFilter"
              placeholder="月"
              class="filter-control"
              size="small"
              clearable
            >
              <el-option
                v-for="m in 12"
                :key="m"
                :label="m + '月'"
                :value="m"
              />
            </el-select>
          </el-form-item>

          <button
            class="btn-refresh"
            :class="{ refreshing: stats.isRefreshing }"
            @click="stats.refreshAll()"
          >
            <RefreshCw :size="14" />
            <span>刷新</span>
          </button>
        </el-form>
      </template>
    </PageHeader>

    <el-tabs v-model="activeTab" class="stats-tabs">
      <el-tab-pane v-for="t in tabs" :key="t.name" :label="t.label" :name="t.name" />
    </el-tabs>

    <div class="stats-content">
      <router-view :key="$route.fullPath" />
    </div>
  </PageContainer>
</template>

<style scoped>
.stats-tabs {
  margin-bottom: 20px;
}

.stats-content {
  min-height: 400px;
}

.toolbar-filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0;
}

.toolbar-field {
  margin: 0;
}

.toolbar-field :deep(.el-select),
.toolbar-field :deep(.el-input-number) {
  min-width: 160px;
  max-width: 240px;
  width: 100%;
}

.toolbar-field :deep(.el-input-number) {
  display: flex;
}

.toolbar-field :deep(.el-input-number .el-input__inner) {
  text-align: left;
}

/* Refresh button styling */
.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  background: #f5f3f1;
  border: 1px solid #e5e0dc;
  border-radius: 8px;
  color: #6b6560;
  font-size: 0.8125rem;
  font-weight: 450;
  cursor: pointer;
  transition: all 0.2s ease;
  height: 32px;
}

.btn-refresh:hover {
  background: #ebe8e5;
  border-color: #d5d0cc;
  color: #2d2a26;
}

.btn-refresh svg {
  transition: transform 0.5s ease;
}

.btn-refresh.refreshing svg {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Input number controls styling */
.toolbar-filters :deep(.el-input-number__increase),
.toolbar-filters :deep(.el-input-number__decrease) {
  height: 16px !important;
  line-height: 16px !important;
  width: 20px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

/* Month selector width adjustment */
.toolbar-filters :deep(.el-select) {
  min-width: 80px !important;
}

.toolbar-filters :deep(.el-select__wrapper) {
  min-width: 80px !important;
}

.toolbar-filters :deep(.el-input-number__increase) {
  border-bottom: 1px solid var(--primary-color) !important;
}

.toolbar-filters :deep(.el-input-number__decrease) {
  border-top: 1px solid var(--primary-color) !important;
}

/* Remove focus outline from filter controls */
.toolbar-filters :deep(.el-select:focus),
.toolbar-filters :deep(.el-select:focus-visible),
.toolbar-filters :deep(.el-select.is-focus),
.toolbar-filters :deep(.el-select.is-active),
.toolbar-filters :deep(.el-input-number:focus),
.toolbar-filters :deep(.el-input-number:focus-visible),
.toolbar-filters :deep(.el-input-number.is-focus),
.toolbar-filters :deep(.el-input-number.is-active),
.toolbar-filters :deep(.el-date-picker:focus),
.toolbar-filters :deep(.el-date-picker:focus-visible),
.toolbar-filters :deep(.el-date-picker.is-focus),
.toolbar-filters :deep(.el-date-picker.is-active) {
  outline: none !important;
}

.toolbar-filters :deep(.el-select.is-focus .el-input__wrapper),
.toolbar-filters :deep(.el-select.is-active .el-input__wrapper),
.toolbar-filters :deep(.el-select:focus .el-input__wrapper),
.toolbar-filters :deep(.el-select:focus-visible .el-input__wrapper),
.toolbar-filters :deep(.el-input-number.is-focus .el-input__wrapper),
.toolbar-filters :deep(.el-input-number.is-active .el-input__wrapper),
.toolbar-filters :deep(.el-input-number:focus .el-input__wrapper),
.toolbar-filters :deep(.el-input-number:focus-visible .el-input__wrapper),
.toolbar-filters :deep(.el-date-picker.is-focus .el-input__wrapper),
.toolbar-filters :deep(.el-date-picker.is-active .el-input__wrapper),
.toolbar-filters :deep(.el-date-picker:focus .el-input__wrapper),
.toolbar-filters :deep(.el-date-picker:focus-visible .el-input__wrapper) {
  box-shadow: none !important;
}

/* Button-like style for filter controls to match toolbar button */
.toolbar-filters :deep(.el-select__wrapper),
.toolbar-filters :deep(.el-input__wrapper),
.toolbar-filters :deep(.el-date-editor .el-input__wrapper) {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0 12px;
  height: 32px;
  min-width: 80px;
  border: 1px solid var(--primary-color) !important;
  border-radius: 6px;
  background-color: #fff;
  color: var(--text-primary);
  box-shadow: none !important;
}

.toolbar-filters :deep(.el-select__wrapper:hover),
.toolbar-filters :deep(.el-input__wrapper:hover),
.toolbar-filters :deep(.el-date-editor .el-input__wrapper:hover) {
  border-color: var(--primary-hover) !important;
  background-color: #faf5f3;
}

.toolbar-filters :deep(.el-select__wrapper.is-focus),
.toolbar-filters :deep(.el-input__wrapper.is-focus),
.toolbar-filters :deep(.el-date-editor.is-focus .el-input__wrapper) {
  border-color: var(--primary-color) !important;
  box-shadow: none !important;
}

.toolbar-filters :deep(.el-select__suffix .el-select__icon),
.toolbar-filters :deep(.el-select__suffix .el-select__caret) {
  color: var(--primary-color);
}

.toolbar-filters :deep(.el-input__inner) {
  font-size: 14px;
  height: 30px;
  line-height: 30px;
}

.toolbar-filters :deep(.el-select__selected-item .el-select__placeholder),
.toolbar-filters :deep(.el-select__placeholder) {
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .toolbar-field :deep(.el-select),
  .toolbar-field :deep(.el-input-number) {
    max-width: 100%;
    flex: 1 1 auto;
  }
}

@media (max-width: 520px) {
  .btn-refresh span {
    display: none;
  }

  .btn-refresh {
    justify-content: center;
    min-width: 36px;
    padding: 0.5rem;
  }
}
</style>
