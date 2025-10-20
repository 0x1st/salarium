<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useUserStore } from '../store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Users, DollarSign, Trash2, Edit, User, TrendingUp, Calendar, Award } from 'lucide-vue-next'


const user = useUserStore()
const list = ref([])
const dialogVisible = ref(false)
const form = ref({ 
  name: '', 
  note: '',
  pension_history: 0,
  medical_history: 0,
  housing_fund_history: 0
})
const loading = ref(false)

const api = axios.create({
  baseURL: '/api',
  headers: { Authorization: `Bearer ${user.token}` },
})

// Computed properties for statistics
const currentMonth = computed(() => {
  const month = new Date().getMonth() + 1
  return `${month}月`
})

const completeProfileRate = computed(() => {
  if (list.value.length === 0) return '0%'
  const completeProfiles = list.value.filter(person => person.note && person.note.trim()).length
  const rate = Math.round((completeProfiles / list.value.length) * 100)
  return `${rate}%`
})

// Load persons data
async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/persons/')
    list.value = data
  } catch (error) {
    ElMessage.error('加载人员数据失败')
  } finally {
    loading.value = false
  }
}

// Open create person dialog
function openCreate() {
  form.value = { 
    name: '', 
    note: '',
    pension_history: 0,
    medical_history: 0,
    housing_fund_history: 0
  }
  dialogVisible.value = true
}

// Submit new person
async function submit() {
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入姓名')
    return
  }
  
  try {
    const { data } = await api.post('/persons/', form.value)
    list.value.push(data)
    dialogVisible.value = false
    ElMessage.success('添加人员成功')
  } catch (error) {
    ElMessage.error('添加人员失败')
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
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除人员失败')
    }
  }
}

onMounted(load)
</script>

<template>
  <div class="persons-container">
    <!-- Header Section -->
    <div class="persons-header">
      <div class="header-left">
        <h2 class="page-title">信息管理</h2>
        <p class="page-subtitle">管理用户信息</p>
      </div>
      <div class="header-controls">
        <el-button type="primary" @click="openCreate" class="add-button">
          <Plus class="button-icon" />
          添加用户
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-cards" v-loading="loading">
      <div class="stat-card gradient-orange">
        <div class="stat-icon">📅</div>
        <div class="stat-content">
          <div class="stat-value">{{ new Date().getFullYear() }}</div>
          <div class="stat-label">当前年份</div>
        </div>
      </div>

      <div class="stat-card gradient-orange">
        <div class="stat-icon">📅</div>
        <div class="stat-content">
          <div class="stat-value">{{ currentMonth }}</div>
          <div class="stat-label">当前月份</div>
        </div>
      </div>

      <div class="stat-card gradient-blue">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <div class="stat-value">{{ list.length }}</div>
          <div class="stat-label">总用户</div>
        </div>
      </div>
      <div class="stat-card gradient-green">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-value">{{ list.length > 0 ? '100%' : '0%' }}</div>
          <div class="stat-label">活跃率</div>
        </div>
      </div>
    </div>

    <!-- Persons List Section -->
    <el-card class="persons-list-card" shadow="hover" v-if="list.length > 0">
      <template #header>
        <div class="card-header">
          <span class="card-title">人员列表</span>
          <el-button @click="load" size="small" type="default">
            刷新
          </el-button>
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
        <el-button type="primary" size="large" @click="openCreate" class="empty-action">
          <Plus class="button-icon" />
          添加第一位用户
        </el-button>
      </div>
    </el-card>

    <!-- Add Person Dialog -->
    <el-dialog 
      v-model="dialogVisible" 
      title="添加人员" 
      width="500px"
      class="person-dialog"
    >
      <el-form :model="form" label-width="140px">
        <el-form-item label="姓名" required>
          <el-input 
            v-model="form.name" 
            placeholder="请输入姓名"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input 
            v-model="form.note" 
            type="textarea" 
            placeholder="请输入备注"
            :rows="3"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        <el-divider content-position="left">历史累计值（加入系统前）</el-divider>
        <el-form-item label="养老保险历史累计">
          <el-input-number 
            v-model="form.pension_history" 
            :min="0"
            :precision="2"
            :step="100"
            placeholder="输入加入系统前的累计金额"
            style="width: 100%"
          />
          <span style="color: #909399; font-size: 12px; margin-left: 8px;">元</span>
        </el-form-item>
        <el-form-item label="医疗保险历史累计">
          <el-input-number 
            v-model="form.medical_history" 
            :min="0"
            :precision="2"
            :step="100"
            placeholder="输入加入系统前的累计金额"
            style="width: 100%"
          />
          <span style="color: #909399; font-size: 12px; margin-left: 8px;">元</span>
        </el-form-item>
        <el-form-item label="住房公积金历史累计">
          <el-input-number 
            v-model="form.housing_fund_history" 
            :min="0"
            :precision="2"
            :step="100"
            placeholder="输入加入系统前的累计金额"
            style="width: 100%"
          />
          <span style="color: #909399; font-size: 12px; margin-left: 8px;">元</span>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submit">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.persons-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: auto;
}

.persons-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  padding: 0 4px;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.add-button {
  border-radius: 8px;
  padding: 12px 20px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.add-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(64, 158, 255, 0.3);
}

.button-icon {
  width: 16px;
  height: 16px;
  margin-right: 8px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--gradient);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.gradient-blue {
  --gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.gradient-green {
  --gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.gradient-orange {
  --gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.gradient-purple {
  --gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-icon {
  font-size: 32px;
  margin-right: 16px;
  opacity: 0.8;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
  font-weight: 500;
}

.persons-list-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.persons-list-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.persons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.person-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(102, 126, 234, 0.08);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  position: relative;
  overflow: hidden;
}

.person-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.person-card:hover {
  background: linear-gradient(135deg, #ffffff 0%, #f0f8ff 100%);
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.2);
}

.person-card:hover::before {
  opacity: 1;
}

.person-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
  position: relative;
}

.person-avatar::after {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.person-card:hover .person-avatar {
  transform: scale(1.05);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.person-card:hover .person-avatar::after {
  opacity: 0.2;
}

.avatar-icon {
  font-size: 28px;
  color: white;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.person-info {
  flex: 1;
  min-width: 0;
}

.person-name {
  font-size: 18px;
  font-weight: 600;
  color: #1a202c;
  margin: 0 0 6px 0;
  line-height: 1.3;
  letter-spacing: -0.025em;
  transition: color 0.3s ease;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.person-card:hover .person-name {
  color: #667eea;
}

.person-note {
  font-size: 14px;
  color: #718096;
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
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.person-card:hover .person-actions {
  opacity: 1;
}

.person-actions .el-button {
  border-radius: 8px !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  padding: 0 !important;
  margin: 0 !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  border: none !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
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
  font-weight: 500 !important;
}

.person-actions .el-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.person-actions .el-button--primary:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.person-actions .el-button--danger {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
}

.person-actions .el-button--danger:hover {
  background: linear-gradient(135deg, #ff5252 0%, #e53e3e 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
}

.person-actions .el-button .el-icon {
  margin-right: 4px;
}

.empty-state-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.empty-state-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
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

/* Responsive Design */
@media (max-width: 768px) {
  .persons-container {
    padding: 16px;
  }
  
  .persons-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .stats-cards {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .persons-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .person-card {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .page-subtitle {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .persons-container {
    padding: 12px;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-icon {
    font-size: 28px;
    margin-right: 12px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .person-card {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
  
  .person-info {
    text-align: center;
  }
}
</style>