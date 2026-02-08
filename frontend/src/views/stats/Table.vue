<template>
  <div class="table-empty">
    <div class="empty-icon">
      <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M4 4h16v16H4z" />
        <path d="M8 8h8M8 12h8M8 16h8" />
      </svg>
    </div>
    <div class="empty-title">明细表已移除</div>
    <div class="empty-sub">该模块内容已清空，如需恢复可再添加。</div>
  </div>
</template>

<style scoped>
.table-empty {
  min-height: 320px;
  display: grid;
  place-items: center;
  text-align: center;
  gap: 10px;
  color: #6b6560;
  border: 1px solid #e5e0dc;
  border-radius: 12px;
  background: #fffdfb;
  padding: 32px;
}

.empty-icon {
  color: #c9bdb4;
}

.empty-title {
  font-size: 1rem;
  font-weight: 600;
  color: #2d2a26;
}

.empty-sub {
  font-size: 0.875rem;
}
</style>
