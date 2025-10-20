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
    <div v-for="(item, i) in items" :key="i" class="kpi-card" :style="{ borderColor: item.color || '#e5e7eb' }">
      <div class="kpi-label">{{ item.label }}</div>
      <div class="kpi-value">{{ item.value }}</div>
    </div>
  </div>
</template>

<style scoped>
.kpi-grid { display:grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.kpi-card { background:#fff; border:1px solid; border-radius:12px; padding:14px 16px; box-shadow:0 1px 2px rgba(0,0,0,0.04); }
.kpi-label { font-size: 12px; color:#64748b; }
.kpi-value { font-size: 18px; font-weight: 700; color:#111827; margin-top: 6px; }
@media (max-width: 992px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 576px) {
  .kpi-grid { grid-template-columns: 1fr; }
}
</style>
