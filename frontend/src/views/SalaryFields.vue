<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../utils/axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Settings,
  DollarSign,
  MinusCircle,
  Edit,
  Trash2,
  ArrowLeft,
  X,
  Tag
} from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const router = useRouter()
const fields = ref([])
const categories = ref({ income: [], deduction: [] })
const dialogVisible = ref(false)
const loading = ref(false)
const isEditing = ref(false)
const editingId = ref(null)

const form = ref({
  name: '',
  field_key: '',
  field_type: 'income',
  category: '',
  is_non_cash: false,
  display_order: 0,
})

const incomeFields = computed(() => fields.value.filter(f => f.field_type === 'income'))
const deductionFields = computed(() => fields.value.filter(f => f.field_type === 'deduction'))

const categoryOptions = computed(() => {
  return categories.value[form.value.field_type] || []
})

async function loadCategories() {
  try {
    const { data } = await api.get('/salary-fields/categories')
    categories.value = data
  } catch {
    ElMessage.error('加载类别失败')
  }
}

async function loadFields() {
  loading.value = true
  try {
    const { data } = await api.get('/salary-fields/', { params: { include_inactive: false } })
    fields.value = data
  } catch {
    ElMessage.error('加载字段失败')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEditing.value = false
  editingId.value = null
  form.value = {
    name: '',
    field_key: '',
    field_type: 'income',
    category: categories.value.income[0]?.key || '',
    is_non_cash: false,
    display_order: fields.value.length,
  }
  dialogVisible.value = true
}

function openEdit(field) {
  isEditing.value = true
  editingId.value = field.id
  form.value = {
    name: field.name,
    field_key: field.field_key,
    field_type: field.field_type,
    category: field.category,
    is_non_cash: field.is_non_cash,
    display_order: field.display_order,
  }
  dialogVisible.value = true
}

function generateFieldKey() {
  if (!form.value.name || isEditing.value) return
  const pinyin = form.value.name
    .toLowerCase()
    .replace(/[\u4e00-\u9fa5]/g, '')
    .replace(/[^a-z0-9]/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_|_$/g, '')
  if (pinyin) {
    form.value.field_key = pinyin
  } else {
    form.value.field_key = 'custom_' + Date.now()
  }
}

async function submit() {
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入字段名称')
    return
  }
  if (!form.value.field_key.trim()) {
    ElMessage.warning('请输入字段标识')
    return
  }
  if (!form.value.category) {
    ElMessage.warning('请选择计算类别')
    return
  }

  try {
    if (isEditing.value) {
      const { data } = await api.put(`/salary-fields/${editingId.value}`, {
        name: form.value.name,
        category: form.value.category,
        is_non_cash: form.value.is_non_cash,
        display_order: form.value.display_order,
      })
      const index = fields.value.findIndex(f => f.id === editingId.value)
      if (index !== -1) {
        fields.value[index] = data
      }
      ElMessage.success('字段更新成功')
    } else {
      const { data } = await api.post('/salary-fields/', form.value)
      fields.value.push(data)
      ElMessage.success('字段创建成功')
    }
    dialogVisible.value = false
  } catch (error) {
    const detail = error.response?.data?.detail || '操作失败'
    ElMessage.error(detail)
  }
}

async function remove(field) {
  try {
    await ElMessageBox.confirm(
      `确定要删除字段 "${field.name}" 吗？已有的工资记录中该字段的数据将被保留但不再显示。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await api.delete(`/salary-fields/${field.id}`)
    fields.value = fields.value.filter(f => f.id !== field.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function getCategoryLabel(categoryKey, fieldType) {
  const cats = categories.value[fieldType] || []
  const cat = cats.find(c => c.key === categoryKey)
  return cat ? cat.label : categoryKey
}

function goBack() {
  router.push('/persons')
}

onMounted(() => {
  loadCategories()
  loadFields()
})
</script>

<template>
  <div class="fields-container">
    <div class="page-header">
      <div class="header-content">
        <div class="header-nav">
          <button class="back-btn" @click="goBack">
            <ArrowLeft class="back-icon" />
            返回人员列表
          </button>
        </div>
        <div class="header-title">
          <Settings class="title-icon" />
          <div>
            <h1>自定义工资字段</h1>
            <p class="header-subtitle">管理收入和扣款的自定义字段</p>
          </div>
        </div>
      </div>
      <button class="btn btn-primary btn-create" @click="openCreate">
        <Plus class="button-icon" />
        添加字段
      </button>
    </div>

    <div class="fields-grid">
      <div class="field-section">
        <div class="section-header">
          <DollarSign class="section-icon income" />
          <h2>收入字段</h2>
          <span class="field-count">{{ incomeFields.length }} 个</span>
        </div>
        <div class="field-list">
          <div v-if="incomeFields.length === 0" class="empty-state">
            <p>暂无自定义收入字段</p>
          </div>
          <div v-for="field in incomeFields" :key="field.id" class="field-card">
            <div class="field-info">
              <div class="field-name">{{ field.name }}</div>
              <div class="field-meta">
                <span class="field-key">{{ field.field_key }}</span>
                <span class="field-category">{{ getCategoryLabel(field.category, 'income') }}</span>
                <span v-if="field.is_non_cash" class="field-tag non-cash">非现金</span>
              </div>
            </div>
            <div class="field-actions">
              <button class="action-btn btn-edit" @click="openEdit(field)" title="编辑">
                <Edit class="action-icon" />
              </button>
              <button class="action-btn btn-delete" @click="remove(field)" title="删除">
                <Trash2 class="action-icon" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="field-section">
        <div class="section-header">
          <MinusCircle class="section-icon deduction" />
          <h2>扣款字段</h2>
          <span class="field-count">{{ deductionFields.length }} 个</span>
        </div>
        <div class="field-list">
          <div v-if="deductionFields.length === 0" class="empty-state">
            <p>暂无自定义扣款字段</p>
          </div>
          <div v-for="field in deductionFields" :key="field.id" class="field-card">
            <div class="field-info">
              <div class="field-name">{{ field.name }}</div>
              <div class="field-meta">
                <span class="field-key">{{ field.field_key }}</span>
                <span class="field-category">{{ getCategoryLabel(field.category, 'deduction') }}</span>
              </div>
            </div>
            <div class="field-actions">
              <button class="action-btn btn-edit" @click="openEdit(field)" title="编辑">
                <Edit class="action-icon" />
              </button>
              <button class="action-btn btn-delete" @click="remove(field)" title="删除">
                <Trash2 class="action-icon" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Field Dialog -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="dialogVisible" class="modal-overlay">
          <div class="modal-container">
            <div class="modal-header">
              <h2>{{ isEditing ? '编辑字段' : '添加字段' }}</h2>
              <button class="close-btn" @click="dialogVisible = false">
                <X :size="18" />
              </button>
            </div>

            <form @submit.prevent="submit" class="modal-body">
              <!-- 基本信息 -->
              <div class="form-section">
                <div class="section-header">
                  <Tag :size="18" class="section-icon" />
                  <h3>基本信息</h3>
                </div>
                <div class="form-group">
                  <label>字段名称 *</label>
                  <input
                    v-model="form.name"
                    type="text"
                    placeholder="如：春节补贴"
                    @blur="generateFieldKey"
                    required
                  />
                </div>
                <div class="form-group">
                  <label>字段标识 *</label>
                  <input
                    v-model="form.field_key"
                    type="text"
                    placeholder="如：spring_bonus"
                    :disabled="isEditing"
                    pattern="^[a-z][a-z0-9_]*$"
                    required
                  />
                  <p class="form-hint">只能包含小写字母、数字和下划线，以字母开头</p>
                </div>
              </div>

              <!-- 字段类型 -->
              <div class="form-section">
                <div class="section-header">
                  <Settings :size="18" class="section-icon" />
                  <h3>字段设置</h3>
                </div>
                <div class="form-grid">
                  <div class="form-group">
                    <label>字段类型 *</label>
                    <select v-model="form.field_type" :disabled="isEditing">
                      <option value="income">收入</option>
                      <option value="deduction">扣款</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>计算类别 *</label>
                    <select v-model="form.category">
                      <option v-for="cat in categoryOptions" :key="cat.key" :value="cat.key">
                        {{ cat.label }}
                      </option>
                    </select>
                    <p class="form-hint">决定该字段在统计图表中的归类方式</p>
                  </div>
                </div>
                <div class="form-group" v-if="form.field_type === 'income'">
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="form.is_non_cash" />
                    <span>非现金福利（不计入实际到手）</span>
                  </label>
                </div>
                <div class="form-group">
                  <label>显示顺序</label>
                  <input v-model.number="form.display_order" type="number" min="0" />
                </div>
              </div>
            </form>

            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="dialogVisible = false">取消</button>
              <button type="button" class="btn btn-primary" @click="submit">保存</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.fields-container {
  padding: 1.5rem;
  max-width: 1200px;
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
  border: 1px solid #e5e0dc;
  border-radius: 8px;
  color: #6b6560;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: #faf5f3;
  color: #2d2a26;
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
  color: #da7756;
}

.header-title h1 {
  font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
  font-size: 2rem;
  font-weight: 500;
  color: #2d2a26;
  margin: 0;
}

.header-subtitle {
  color: #6b6560;
  font-size: 1rem;
  margin: 0.25rem 0 0 0;
}

.fields-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}

.field-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 1.5rem;
  background: #faf5f3;
  border-bottom: 1px solid #e5e0dc;
}

.section-icon {
  width: 24px;
  height: 24px;
}

.section-icon.income {
  color: #5a8a6e;
}

.section-icon.deduction {
  color: #c45c5c;
}

.section-header h2 {
  font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
  font-size: 1.125rem;
  font-weight: 500;
  color: #2d2a26;
  margin: 0;
  flex: 1;
}

.field-count {
  font-size: 0.875rem;
  color: #6b6560;
  background: #f5f3f1;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
}

.field-list {
  padding: 1rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #9a9590;
}

.field-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: #faf5f3;
  border-radius: 8px;
  margin-bottom: 0.75rem;
}

.field-card:last-child {
  margin-bottom: 0;
}

.field-info {
  flex: 1;
}

.field-name {
  font-weight: 500;
  color: #2d2a26;
  margin-bottom: 0.25rem;
}

.field-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.75rem;
}

.field-key {
  color: #6b6560;
  font-family: monospace;
  background: #f5f3f1;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
}

.field-category {
  color: #da7756;
}

.field-tag {
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.field-tag.non-cash {
  background: #fef3c7;
  color: #92400e;
}

.field-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-edit {
  background: #f5e6e0;
  color: #da7756;
}

.btn-edit:hover {
  background: #f0dcd4;
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
  background: #da7756;
  color: white;
}

.btn-primary:hover {
  background: #c4684a;
}

.btn-secondary {
  background: #f5f3f1;
  color: #2d2a26;
}

.btn-secondary:hover {
  background: #ebe8e5;
}

.button-icon {
  width: 16px;
  height: 16px;
}

.field-form {
  padding: 0.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 450;
  color: #2d2a26;
  margin-bottom: 0.5rem;
}

.form-control {
  width: 100%;
  padding: 0.625rem;
  border: 1px solid #e5e0dc;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
  background: #fdfcfb;
}

.form-control:focus {
  outline: none;
  border-color: #da7756;
  box-shadow: 0 0 0 3px rgba(218, 119, 86, 0.1);
}

.form-control:disabled {
  background: #f5f3f1;
  cursor: not-allowed;
}

.form-hint {
  font-size: 0.75rem;
  color: #9a9590;
  margin-top: 0.25rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.form-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e0dc;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }

  .fields-grid {
    grid-template-columns: 1fr;
  }
}

/* ============================================
   Custom Modal - Claude/Anthropic Style
   ============================================ */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e0dc;
}

.modal-header h2 {
  font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
  font-size: 1.25rem;
  font-weight: 500;
  color: #2d2a26;
  margin: 0;
}

.close-btn {
  padding: 0.5rem;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #6b6560;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #f5f3f1;
  color: #2d2a26;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.25rem 2rem;
  border-top: 1px solid #e5e0dc;
}

/* Form Sections */
.form-section {
  margin-bottom: 2rem;
}

.form-section:last-child {
  margin-bottom: 0;
}

/* Form Sections */
.form-section {
  margin-bottom: 2rem;
}

.form-section:last-child {
  margin-bottom: 0;
}

/* Modal-specific section header (no background) */
.modal-body .section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  background: transparent;
  border: none;
  padding: 0;
}

.modal-body .section-header .section-icon {
  color: #da7756;
}

.modal-body .section-header h3 {
  font-size: 0.9375rem;
  font-weight: 500;
  color: #2d2a26;
  margin: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-group label {
  font-size: 0.8125rem;
  font-weight: 450;
  color: #6b6560;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.625rem 0.875rem;
  border: 1px solid #e5e0dc;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  background: #fdfcfb;
  color: #2d2a26;
}

.form-group input:hover,
.form-group select:hover,
.form-group textarea:hover {
  border-color: #d5d0cc;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #da7756;
  background: white;
  box-shadow: 0 0 0 2px rgba(218, 119, 86, 0.1);
}

.form-group input:disabled,
.form-group select:disabled {
  background: #f5f3f1;
  cursor: not-allowed;
  opacity: 0.6;
}

.form-group textarea {
  resize: vertical;
  min-height: 60px;
  font-family: inherit;
}

.form-hint {
  font-size: 0.75rem;
  color: #9a9590;
  margin-top: -0.125rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #2d2a26;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #da7756;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-secondary {
  background: #f5f3f1;
  color: #2d2a26;
}

.btn-secondary:hover {
  background: #ebe8e5;
}

.btn-primary {
  background: #da7756;
  color: white;
}

.btn-primary:hover {
  background: #c4684a;
}

/* Modal transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.96);
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .modal-container {
    max-height: 100vh;
    border-radius: 0;
  }
}
</style>
