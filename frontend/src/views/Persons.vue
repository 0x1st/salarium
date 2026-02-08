<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../utils/axios'
import { useStatsStore } from '../store/stats'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, DollarSign, Trash2, Edit, User, TrendingUp, X, RefreshCw } from 'lucide-vue-next'
import PageContainer from '../components/PageContainer.vue'
import PageHeader from '../components/PageHeader.vue'
import StatsCards from '../components/StatsCards.vue'

const statsStore = useStatsStore()
const list = ref([])
const dialogVisible = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const form = ref({ 
  name: '', 
  note: '',
  pension_history: 0,
  medical_history: 0,
  housing_fund_history: 0
})
const loading = ref(false)

// Computed properties for statistics
const currentMonth = computed(() => {
  const month = new Date().getMonth() + 1
  return `${month}月`
})

// Stats cards configuration
const statsCardsData = computed(() => [
  { icon: '📅', value: new Date().getFullYear().toString(), label: '当前年份', gradient: 'gradient-orange' },
  { icon: '📅', value: currentMonth.value, label: '当前月份', gradient: 'gradient-orange' },
  { icon: '👥', value: list.value.length.toString(), label: '总用户', gradient: 'gradient-blue' },
  { icon: '✅', value: list.value.length > 0 ? '100%' : '0%', label: '活跃率', gradient: 'gradient-green' }
])

// Load persons data
async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/persons/')
    list.value = data
  } catch {
    ElMessage.error('加载人员数据失败')
  } finally {
    loading.value = false
  }
}

// Open create person dialog
function openCreate() {
  isEditing.value = false
  editingId.value = null
  form.value = { 
    name: '', 
    note: '',
    pension_history: 0,
    medical_history: 0,
    housing_fund_history: 0
  }
  dialogVisible.value = true
}

// Open edit dialog
function openEdit(person) {
  isEditing.value = true
  editingId.value = person.id
  form.value = {
    name: person.name || '',
    note: person.note || '',
    pension_history: Number(person.pension_history || 0),
    medical_history: Number(person.medical_history || 0),
    housing_fund_history: Number(person.housing_fund_history || 0),
  }
  dialogVisible.value = true
}

// Submit create/update person
async function submit() {
  const name = (form.value.name || '').trim()
  if (!name) {
    ElMessage.warning('请输入姓名')
    return
  }
  if (name.length > 64) {
    ElMessage.warning('姓名长度不能超过64个字符')
    return
  }
  if (form.value.note && form.value.note.length > 255) {
    ElMessage.warning('备注长度不能超过255个字符')
    return
  }

  try {
    if (isEditing.value) {
      const { data } = await api.put(`/persons/${editingId.value}`, form.value)
      const idx = list.value.findIndex(i => i.id === editingId.value)
      if (idx !== -1) list.value[idx] = data
      dialogVisible.value = false
      isEditing.value = false
      editingId.value = null
      await load()
      ElMessage.success('更新人员成功')
    } else {
      const { data } = await api.post('/persons/', form.value)
      list.value.push(data)
      dialogVisible.value = false
      await load()
      ElMessage.success('添加人员成功')
    }
    statsStore.invalidate()
  } catch (error) {
    const detail = error?.response?.data?.detail
    let msg = isEditing.value ? '更新人员失败' : '添加人员失败'
    if (typeof detail === 'string') msg = detail
    else if (Array.isArray(detail) && detail.length) msg = detail[0]?.msg || msg
    ElMessage.error(msg)
  }
}

// Remove person
async function remove(id, name) {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${name} 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await api.delete(`/persons/${id}`)
    list.value = list.value.filter(i => i.id !== id)
    ElMessage.success('删除人员成功')
    statsStore.invalidate()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除人员失败')
    }
  }
}

onMounted(load)
</script>

<template>
  <PageContainer>
    <!-- Header Section -->
    <PageHeader title="信息管理" subtitle="管理用户信息">
      <template #controls>
        <button class="btn btn-primary add-button" @click="openCreate">
          <Plus class="button-icon" />
          添加用户
        </button>
      </template>
    </PageHeader>

    <!-- Statistics Cards -->
    <StatsCards :cards="statsCardsData" :loading="loading" />

    <!-- Persons List Section -->
    <el-card class="persons-list-card" shadow="hover" v-if="list.length > 0">
      <template #header>
        <div class="card-header">
          <span class="card-title">用户信息</span>
          <button class="btn-refresh" @click="load">
            <RefreshCw :size="14" />
            刷新
          </button>
        </div>
      </template>
      
      <div class="persons-grid">
        <div 
          v-for="person in list" 
          :key="person.id" 
          class="person-card"
        >
          <div class="person-avatar">
            <div class="avatar-icon">👤</div>
          </div>
          <div class="person-info">
            <h3 class="person-name">{{ person.name }}</h3>
            <p class="person-note" v-if="person.note">{{ person.note }}</p>
            <p class="person-note" v-else>暂无备注</p>
          </div>
          <div class="person-actions">
            <el-button 
              type="primary" 
              size="small" 
              @click="$router.push(`/salaries/${person.id}`)"
              :icon="DollarSign"
            >
              工资管理
            </el-button>
            <el-button 
              type="default" 
              size="small" 
              @click="openEdit(person)"
              :icon="Edit"
            >
              编辑
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="remove(person.id, person.name)"
              :icon="Trash2"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Empty State -->
    <el-card class="empty-state-card" shadow="hover" v-if="list.length === 0 && !loading">
      <div class="empty-container">
        <div class="empty-icon">👥</div>
        <h3 class="empty-title">暂无用户信息</h3>
        <p class="empty-description">
          还没有添加任何用户，点击下面的按钮开始添加
        </p>
        <button type="button" class="btn btn-primary btn-large" @click="openCreate">
          <Plus :size="16" />
          添加第一位用户
        </button>
      </div>
    </el-card>

    <!-- Add/Edit Person Dialog -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="dialogVisible" class="modal-overlay">
          <div class="modal-container">
            <div class="modal-header">
              <h2>{{ isEditing ? '编辑人员' : '添加人员' }}</h2>
              <button class="close-btn" @click="dialogVisible = false">
                <X :size="18" />
              </button>
            </div>

            <form @submit.prevent="submit" class="modal-body">
              <!-- 基本信息 -->
              <div class="form-section">
                <div class="section-header">
                  <User :size="18" class="section-icon" />
                  <h3>基本信息</h3>
                </div>
                <div class="form-grid">
                  <div class="form-group">
                    <label>姓名 *</label>
                    <input
                      v-model="form.name"
                      type="text"
                      placeholder="请输入姓名"
                      maxlength="64"
                      required
                    />
                  </div>
                </div>
                <div class="form-group">
                  <label>备注</label>
                  <textarea
                    v-model="form.note"
                    placeholder="请输入备注（可选）"
                    rows="2"
                    maxlength="255"
                  ></textarea>
                </div>
              </div>

              <!-- 历史累计值 -->
              <div class="form-section">
                <div class="section-header">
                  <TrendingUp :size="18" class="section-icon" />
                  <h3>历史累计值（加入系统前）</h3>
                </div>
                <div class="form-grid form-grid-3">
                  <div class="form-group">
                    <label>养老保险</label>
                    <div class="input-with-unit">
                      <input v-model.number="form.pension_history" type="number" step="0.01" min="0" placeholder="0" />
                      <span class="input-unit">元</span>
                    </div>
                  </div>
                  <div class="form-group">
                    <label>医疗保险</label>
                    <div class="input-with-unit">
                      <input v-model.number="form.medical_history" type="number" step="0.01" min="0" placeholder="0" />
                      <span class="input-unit">元</span>
                    </div>
                  </div>
                  <div class="form-group">
                    <label>住房公积金</label>
                    <div class="input-with-unit">
                      <input v-model.number="form.housing_fund_history" type="number" step="0.01" min="0" placeholder="0" />
                      <span class="input-unit">元</span>
                    </div>
                  </div>
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
  </PageContainer>
</template>

<style scoped>
.persons-list-card {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e5e0dc;
  box-shadow: none;
  margin-bottom: 24px;
  transition: all 0.2s ease;
}

.persons-list-card:hover {
  border-color: #d5d0cc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}


/* 移除卡片标题下方的分割线 */
.persons-list-card :deep(.el-card__header) {
  border-bottom: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;
}

.card-title {
  font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
  font-size: 18px;
  font-weight: 500;
  color: #2d2a26;
}

/* 统一刷新按钮样式 */
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
}

.btn-refresh:hover {
  background: #ebe8e5;
  border-color: #d5d0cc;
  color: #2d2a26;
}

.persons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.person-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.2s ease;
  border: 1px solid #e5e0dc;
  position: relative;
  overflow: hidden;
}

.person-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 3px;
  background: #da7756;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.person-card:hover {
  border-color: #d5d0cc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.person-card:hover::before {
  opacity: 1;
}

.person-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #da7756;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.person-avatar:hover {
  transform: rotate(0deg);
}

.person-avatar:focus {
  outline: none;
}

.person-avatar .avatar-icon {
  width: 28px;
  height: 28px;
}

.person-info {
  flex: 1;
  min-width: 0;
}

.person-name {
  font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
  font-size: 17px;
  font-weight: 500;
  color: #2d2a26;
  margin: 0 0 6px 0;
  line-height: 1.3;
  letter-spacing: -0.01em;
  transition: color 0.2s ease;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.person-card:hover .person-name {
  color: #da7756;
}

.person-note {
  font-size: 14px;
  color: #6b6560;
  margin: 0;
  font-weight: 400;
  line-height: 1.4;
  word-wrap: break-word;
  overflow-wrap: break-word;
  max-height: 2.8em;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.person-actions {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  opacity: 0.85;
  transition: opacity 0.2s ease;
}

.person-card:hover .person-actions {
  opacity: 1;
}

.person-actions .el-button {
  border-radius: 8px !important;
  font-weight: 450 !important;
  font-size: 13px !important;
  padding: 0 !important;
  margin: 0 !important;
  transition: all 0.2s ease !important;
  border: none !important;
  box-shadow: none !important;
  width: 110px !important;
  height: 36px !important;
  min-width: 110px !important;
  max-width: 110px !important;
  min-height: 36px !important;
  max-height: 36px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  flex-shrink: 0 !important;
  line-height: 1 !important;
  text-align: center !important;
}

.person-actions .el-button span {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 100% !important;
  height: 100% !important;
  font-size: 13px !important;
  font-weight: 450 !important;
}

.person-actions .el-button--primary {
  background: #da7756;
  color: white;
}

.person-actions .el-button--primary:hover {
  background: #c4684a;
  box-shadow: 0 2px 6px rgba(218, 119, 86, 0.25) !important;
}

.person-actions .el-button--danger {
  background: #c45c5c;
  color: white;
}

.person-actions .el-button--danger:hover {
  background: #b04f4f;
  box-shadow: 0 2px 6px rgba(196, 92, 92, 0.25) !important;
}

.person-actions .el-button .el-icon {
  margin-right: 4px;
}

.empty-state-card {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e5e0dc;
  box-shadow: none;
  margin-bottom: 24px;
  transition: all 0.2s ease;
}

.empty-state-card:hover {
  border-color: #d5d0cc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.empty-container {
  padding: 3rem;
  text-align: center;
}

.empty-icon {
  font-size: 3.5rem;
  margin-bottom: 1rem;
  opacity: 0.8;
}

.empty-title {
  font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
  font-size: 1.375rem;
  font-weight: 500;
  color: #2d2a26;
  margin-bottom: 0.5rem;
}

.empty-description {
  color: #6b6560;
  margin-bottom: 1.5rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .persons-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .person-card {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .person-card {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }

  .person-info {
    text-align: center;
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
  max-width: 540px;
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

.section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.section-icon {
  color: #da7756;
}

.section-header h3 {
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

.form-grid-3 {
  grid-template-columns: repeat(3, 1fr);
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
.form-group textarea:hover {
  border-color: #d5d0cc;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #da7756;
  background: white;
  box-shadow: 0 0 0 2px rgba(218, 119, 86, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 60px;
  font-family: inherit;
}

.input-with-unit {
  position: relative;
  display: flex;
  align-items: center;
}

.input-with-unit input {
  width: 100%;
  padding-right: 2.5rem;
}

.input-unit {
  position: absolute;
  right: 0.875rem;
  font-size: 0.75rem;
  color: #9a9590;
  pointer-events: none;
}

/* Buttons */
.button-icon {
  width: 16px;
  height: 16px;
}

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

.btn-large {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
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
  .form-grid,
  .form-grid-3 {
    grid-template-columns: 1fr;
  }

  .modal-container {
    max-height: 100vh;
    border-radius: 0;
  }
}
</style>
