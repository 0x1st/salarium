<script setup>
defineProps({
  minHeight: {
    type: String,
    default: 'calc(100vh - 180px)'
  }
})
</script>

<template>
  <div class="page-container" :style="{ minHeight }">
    <slot />
  </div>
</template>

<style scoped>
.page-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  transition: opacity 0.25s ease, transform 0.25s ease;
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .page-container {
    padding: 12px;
  }
}
</style>
