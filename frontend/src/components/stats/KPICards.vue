<script setup>
const props = defineProps({
  items: {
    type: Array,
    default: () => [], // [{ label, value, color }]
  },
})
</script>

<template>
  <div class="kpi-grid">
    <div v-for="(item, i) in items" :key="i" class="kpi-card" :style="{ '--gradient': getGradient(i, item.color) }">
      <div class="kpi-icon">{{ getIcon(i) }}</div>
      <div class="kpi-content">
        <div class="kpi-value">{{ item.value }}</div>
        <div class="kpi-label">{{ item.label }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    getGradient(index, color) {
      const gradients = [
        'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
      ];
      return gradients[index % gradients.length];
    },
    getIcon(index) {
      const icons = ['💰', '📉', '💵', '📊'];
      return icons[index % icons.length];
    }
  }
}
</script>

<style scoped>
.kpi-grid { 
  display: grid; 
  grid-template-columns: repeat(3, 1fr); 
  gap: 16px; 
}

.kpi-card { 
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.kpi-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--gradient);
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.kpi-icon {
  font-size: 28px;
  margin-right: 14px;
  opacity: 0.85;
}

.kpi-content {
  flex: 1;
}

.kpi-label { 
  font-size: 13px; 
  color: #7f8c8d; 
  font-weight: 500;
  margin-top: 2px;
}

.kpi-value { 
  font-size: 20px; 
  font-weight: 700; 
  color: #2c3e50;
}

@media (max-width: 992px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 576px) {
  .kpi-grid { grid-template-columns: 1fr; }
}
</style>
