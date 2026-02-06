<script setup>
import { ref, computed } from 'vue'
import { Calendar, Edit, Trash2 } from 'lucide-vue-next'
import { formatCurrency as formatCurrencyUtil } from '../../utils/number'

const props = defineProps({
  salaries: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['edit', 'delete'])

function formatCurrency(amount) {
  return formatCurrencyUtil(amount, { decimals: 2 })
}

function computeCustomIncome(salary) {
  if (!salary.custom_fields) return 0
  return Object.values(salary.custom_fields).reduce((sum, val) => sum + (val > 0 ? val : 0), 0)
}

// Table styles matching stats table
const headerCellStyle = { background: '#faf5f3', padding: '12px 16px', color: '#2d2a26', fontWeight: 600, fontSize: '13px' }
const cellStyle = { padding: '14px 16px', fontSize: '14px' }

const tableData = computed(() => {
  return props.salaries.map(s => ({
    ...s,
    customIncome: computeCustomIncome(s)
  }))
})
</script>

<template>
  <div class="salary-table-container">
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="salaries.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
        </svg>
      </div>
      <h3>暂无工资记录</h3>
      <p>点击上方按钮添加第一条记录</p>
    </div>

    <div v-else class="table-scroll-x">
      <el-table
        :data="tableData"
        border
        stripe
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        :default-sort="{ prop: 'year', order: 'descending' }"
      >
        <el-table-column label="时间" width="140" min-width="140" fixed sortable="sort">
          <template #default="{ row }">
            <div class="date-cell">
              <Calendar :size="14" class="date-icon" />
              <span>{{ row.year }}/{{ String(row.month).padStart(2, '0') }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="base_salary" label="基本工资" width="150" min-width="130" sortable="custom" align="right">
          <template #default="{ row }">{{ formatCurrency(row.base_salary) }}</template>
        </el-table-column>

        <el-table-column prop="performance_salary" label="绩效工资" width="150" min-width="130" sortable="custom" align="right">
          <template #default="{ row }">{{ formatCurrency(row.performance_salary) }}</template>
        </el-table-column>

        <el-table-column prop="customIncome" label="自定义收入" width="150" min-width="130" sortable align="right">
          <template #default="{ row }">
            <span class="text-muted">{{ formatCurrency(row.customIncome) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="total_income" label="总收入" width="150" min-width="130" sortable="custom" align="right" class-name="highlight-col">
          <template #default="{ row }">{{ formatCurrency(row.total_income) }}</template>
        </el-table-column>

        <el-table-column prop="total_deductions" label="五险一金" width="150" min-width="130" sortable="custom" align="right">
          <template #default="{ row }">
            <span class="text-danger">-{{ formatCurrency(row.total_deductions) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="tax" label="个税" width="130" min-width="120" sortable="custom" align="right">
          <template #default="{ row }">
            <span class="text-danger">-{{ formatCurrency(row.tax) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="actual_take_home" label="实际到手" width="160" min-width="140" sortable="custom" align="right" class-name="highlight-strong">
          <template #default="{ row }">
            <span class="text-success font-semibold">{{ formatCurrency(row.actual_take_home) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="110" min-width="110" fixed align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <button
                class="action-btn action-btn-edit"
                @click="emit('edit', row)"
                title="编辑"
              >
                <Edit :size="14" />
              </button>
              <button
                class="action-btn action-btn-delete"
                @click="emit('delete', row)"
                title="删除"
              >
                <Trash2 :size="14" />
              </button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.salary-table-container {
  background: white;
  border: 1px solid #e5e0dc;
  border-radius: 12px;
  overflow: hidden;
}

.loading-state,
.empty-state {
  padding: 4rem 2rem;
  text-align: center;
  color: #6b6560;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f5f3f1;
  border-top-color: #da7756;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  color: #d5d0cc;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
  font-size: 1.125rem;
  font-weight: 500;
  color: #2d2a26;
  margin-bottom: 0.5rem;
}

.empty-state p {
  font-size: 0.875rem;
}

.table-scroll-x {
  overflow-x: auto;
  width: 100%;
  min-width: 0;
}

:deep(.el-table) {
  border-radius: 8px;
  min-width: max-content;
}

:deep(.el-table th) {
  background: #faf5f3;
}

:deep(.el-table .cell) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.el-table .highlight-col) .cell {
  background: rgba(218, 119, 86, 0.08);
  font-weight: 600;
}

:deep(.el-table .highlight-strong) .cell {
  background: rgba(90, 138, 110, 0.1);
  font-weight: 700;
  color: #5a8a6e;
}

:deep(.el-table__body tr:hover > td) {
  background: #faf5f3 !important;
}

.date-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-icon {
  color: #9a9590;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.action-btn {
  padding: 0.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn-edit {
  background: #f5e6e0;
  color: #da7756;
}

.action-btn-edit:hover {
  background: #f0dcd4;
}

.action-btn-delete {
  background: #f5e6e0;
  color: #c45c5c;
}

.action-btn-delete:hover {
  background: #f0dcd4;
}

.text-muted {
  color: #9a9590;
}

.text-danger {
  color: #c45c5c;
}

.text-success {
  color: #5a8a6e;
}

.font-semibold {
  font-weight: 600;
}
</style>
