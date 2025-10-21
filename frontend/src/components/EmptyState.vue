<script setup>
const props = defineProps({
  title: { type: String, default: '暂无统计信息记录' },
  description: { type: String, default: '' },
  icon: { type: String, default: '📊' },
})
</script>

<template>
  <div class="empty-container">
    <div class="empty-icon">{{ icon }}</div>
    <h3 class="empty-title">{{ title }}</h3>
    <p class="empty-description">{{ description }}</p>
    <slot />
  </div>
</template>

<style scoped>
.empty-container { padding: 3rem; text-align: center; }
.empty-icon { font-size: 4rem; margin-bottom: 1rem; }
.empty-title { font-size: 1.5rem; font-weight: 600; color: #111827; margin-bottom: 0.5rem; }
.empty-description { color: #6b7280; margin-bottom: 1.5rem; }
</style>
