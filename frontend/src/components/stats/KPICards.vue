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
      const colors = ['#da7756', '#5a8a6e', '#c9a227', '#c4684a'];
      return colors[index % colors.length];
    },
    getIcon(index) {
      const icons = ['💰', '📈', '💵', '📊'];
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
  border: 1px solid #e5e0dc;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.kpi-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 3px;
  background: var(--gradient);
}

.kpi-card:hover {
  border-color: #d5d0cc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.kpi-icon {
  font-size: 24px;
  margin-right: 14px;
  opacity: 0.9;
}

.kpi-content {
  flex: 1;
}

.kpi-label {
  font-size: 13px;
  color: #6b6560;
  font-weight: 450;
  margin-top: 2px;
}

.kpi-value {
  font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
  font-size: 18px;
  font-weight: 500;
  color: #2d2a26;
}

@media (max-width: 992px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 576px) {
  .kpi-grid { grid-template-columns: 1fr; }
}
</style>
