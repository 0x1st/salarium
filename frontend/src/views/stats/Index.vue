<script setup>
import { ref, onMounted, watch, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import { useStatsStore } from '../../store/stats'
import { useUserStore } from '../../store/user'

const tabs = [
  { name: 'stats-net', label: '实际到手金额', path: '/stats/net' },
  { name: 'stats-composition', label: '构成', path: '/stats/composition' },
  { name: 'stats-deductions', label: '扣除', path: '/stats/deductions' },
  { name: 'stats-cumulative', label: '累计', path: '/stats/cumulative' },
  { name: 'stats-table', label: '表格', path: '/stats/table' },
]

const route = useRoute()
const router = useRouter()
const stats = useStatsStore()
const user = useUserStore()

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
  if (route.name) activeTab.value = route.name
  const handler = () => stats.refreshAll()
  window.addEventListener('stats:invalidate', handler)
  _removeInvalidateListener = () => window.removeEventListener('stats:invalidate', handler)
})

onBeforeUnmount(() => {
  if (_removeInvalidateListener) _removeInvalidateListener()
})

watch(() => route.name, (n) => { if (n) { activeTab.value = n; setTimeout(() => window.dispatchEvent(new Event('resize')), 0) } })

function onTabClick(tab) {
  const t = tabs.find(t => t.name === tab.paneName)
  if (t) {
    router.push(t.path)
    setTimeout(() => window.dispatchEvent(new Event('resize')), 0)
  }
}
</script>

<template>
  <div class="stats-page">
    <header class="page-header">
      <div class="page-header__meta">
        <h2 class="title">统计分析</h2>
        <p class="sub">数据统计分析</p>
      </div>

      <div class="page-header__toolbar">
        <el-form class="toolbar-filters" :inline="true" size="small">
          <el-form-item class="toolbar-field">
            <el-select
              v-model="personFilter"
              placeholder="人员"
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
              placeholder="月份"
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
        </el-form>

        <div class="toolbar-actions">
          <el-button
            size="small"
            type="primary"
            plain
            aria-label="刷新"
            class="toolbar-refresh"
            :loading="stats.isRefreshing"
            @click="stats.refreshAll()"
          >
            <el-icon>
              <Refresh />
            </el-icon>
            <span class="btn-text">刷新</span>
          </el-button>
        </div>
      </div>
    </header>

    <el-tabs v-model="activeTab" @tab-click="onTabClick">
      <el-tab-pane v-for="t in tabs" :key="t.name" :label="t.label" :name="t.name" />
    </el-tabs>

    <router-view />
  </div>
</template>

<style scoped>
.stats-page {
  --stats-spacing: 16px;
  --stats-toolbar-gap: 8px;
  --stats-filter-max-width: 240px;
  --stats-filter-min-width: 160px;
  --stats-title-size: 28px;
  --stats-subtitle-size: 16px;
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: auto;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: var(--stats-spacing);
  margin-bottom: var(--stats-spacing);
}

.page-header__meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.title {
  margin: 0;
  font-size: var(--stats-title-size);
  font-weight: 700;
  color: #2c3e50;
  line-height: 1.2;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sub {
  margin: 0;
  color: #7f8c8d;
  font-size: var(--stats-subtitle-size);
}

.page-header__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--stats-toolbar-gap);
}

.toolbar-filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--stats-toolbar-gap);
  margin: 0;
}

.toolbar-field {
  margin: 0;
}

.toolbar-field :deep(.el-select),
.toolbar-field :deep(.el-input-number) {
  min-width: var(--stats-filter-min-width);
  max-width: var(--stats-filter-max-width);
  width: 100%;
}

.toolbar-field :deep(.el-input-number) {
  display: flex;
}

.toolbar-field :deep(.el-input-number .el-input__inner) {
  text-align: left;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: var(--stats-toolbar-gap);
  margin-left: auto;
}

.toolbar-refresh {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.toolbar-refresh :deep(.el-icon) {
  font-size: 16px;
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

@media (max-width: 960px) {
  .stats-page {
    --stats-filter-max-width: 220px;
  }
}

@media (max-width: 768px) {
  .page-header__toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .toolbar-field :deep(.el-select),
  .toolbar-field :deep(.el-input-number) {
    max-width: 100%;
    flex: 1 1 auto;
  }
}

@media (max-width: 520px) {
  .toolbar-refresh .btn-text {
    display: none;
  }

  .toolbar-refresh {
    justify-content: center;
    min-width: 36px;
    padding: 0 10px;
  }
}
</style>
