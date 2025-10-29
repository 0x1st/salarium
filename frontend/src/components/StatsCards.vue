<script setup>
defineProps({
  cards: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})
</script>

<template>
  <div class="stats-cards" v-loading="loading">
    <div 
      v-for="(card, index) in cards" 
      :key="index"
      class="stat-card"
      :class="card.gradient"
    >
      <div class="stat-icon">{{ card.icon }}</div>
      <div class="stat-content">
        <div class="stat-value">{{ card.value }}</div>
        <div class="stat-label">{{ card.label }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
  min-height: 116px;
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
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
  font-weight: 500;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }
  
  .stat-card {
    padding: 20px;
  }
}

@media (max-width: 480px) {
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
}
</style>
