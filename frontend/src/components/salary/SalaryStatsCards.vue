<script setup>
import { DollarSign, TrendingUp, Award } from 'lucide-vue-next'

defineProps({
  stats: {
    type: Object,
    required: true
  }
})

function formatCurrency(amount) {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY'
  }).format(amount || 0)
}
</script>

<template>
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-icon stat-icon-primary">
        <DollarSign :size="20" />
      </div>
      <div class="stat-content">
        <span class="stat-label">累计实发工资</span>
        <span class="stat-value">{{ formatCurrency(stats.total) }}</span>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-icon stat-icon-success">
        <TrendingUp :size="20" />
      </div>
      <div class="stat-content">
        <span class="stat-label">平均实发工资</span>
        <span class="stat-value">{{ formatCurrency(stats.average) }}</span>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-icon stat-icon-warning">
        <Award :size="20" />
      </div>
      <div class="stat-content">
        <span class="stat-label">最近实发工资</span>
        <span class="stat-value">{{ formatCurrency(stats.latest) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.2s ease;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon-primary {
  background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
  color: white;
}

.stat-icon-success {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  color: white;
}

.stat-icon-warning {
  background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
  color: white;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  letter-spacing: -0.02em;
}
</style>
