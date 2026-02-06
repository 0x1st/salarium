<script setup>
const props = defineProps({
  title: { type: String, default: '' },
  note: { type: String, default: '' },
})
</script>

<template>
  <div class="chart-card">
    <div v-if="$slots.header" class="chart-header">
      <slot name="header" />
    </div>
    <div class="chart-body">
      <slot />
    </div>
    <div v-if="title || note" class="chart-footer">
      <div class="chart-title" :title="title">{{ title }}</div>
      <div v-if="note" class="chart-note">{{ note }}</div>
    </div>
  </div>
</template>

<style scoped>
.chart-card {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 8px 0;
}

.chart-body {
  width: 100%;
}

.chart-footer {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
  padding: 12px 0 4px;
  color: #2d2a26;
  flex-wrap: nowrap;
}

.chart-title {
  font-weight: 500;
  font-size: 15px;
  font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
  color: #2d2a26;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.chart-note {
  font-size: 13px;
  color: #6b6560;
  white-space: nowrap;
}
</style>
