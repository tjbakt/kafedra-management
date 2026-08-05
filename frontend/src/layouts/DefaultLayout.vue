<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'

import AppContent from '@/components/layout/AppContent.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import { useLayoutStore } from '@/stores/layout'

const layoutStore = useLayoutStore()

onMounted(() => {
  layoutStore.initializeTheme()
  window.addEventListener('resize', layoutStore.handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', layoutStore.handleResize)
})
</script>

<template>
  <div class="app-layout" :class="{ 'layout-collapsed': layoutStore.sidebarCollapsed }">
    <AppSidebar />
    <AppHeader />

    <div class="app-layout__main">
      <AppContent>
        <RouterView />
      </AppContent>

      <AppFooter />
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: var(--app-background);
}

.app-layout__main {
  min-height: 100vh;
  padding-top: var(--app-header-height);
  margin-left: var(--app-sidebar-width);
  transition: margin-left var(--app-transition);
}

.layout-collapsed .app-layout__main {
  margin-left: var(--app-sidebar-collapsed-width);
}

@media (max-width: 991px) {
  .app-layout__main,
  .layout-collapsed .app-layout__main {
    margin-left: 0;
  }
}
</style>
