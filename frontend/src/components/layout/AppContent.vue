<script setup lang="ts">
import AppBreadcrumb from '@/components/layout/AppBreadcrumb.vue'
</script>

<template>
  <main class="app-content">
    <AppBreadcrumb />

    <div class="app-content__inner">
      <slot />
    </div>
  </main>
</template>

<style scoped>
.app-content {
  min-height: calc(100vh - var(--app-header-height) - var(--app-footer-height));
  padding: 1.25rem 1.5rem 2rem;
}

.app-content__inner {
  width: 100%;
  max-width: 1800px;
  margin: 0 auto;
}

@media (max-width: 767px) {
  .app-content {
    padding: 1rem;
  }
}
</style>
