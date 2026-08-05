<script setup lang="ts">
import { onMounted } from 'vue'

import { useLayoutStore } from '@/stores/layout'

const layoutStore = useLayoutStore()

onMounted(() => {
  layoutStore.initializeTheme()
})
</script>

<template>
  <div class="auth-layout">
    <div class="auth-layout__background">
      <div class="auth-layout__decoration auth-layout__decoration--one" />
      <div class="auth-layout__decoration auth-layout__decoration--two" />
    </div>

    <main class="auth-layout__content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.auth-layout {
  position: relative;
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 1.5rem;
  overflow: hidden;
  background:
    radial-gradient(circle at 10% 20%, rgb(59 130 246 / 12%), transparent 35%),
    radial-gradient(circle at 90% 80%, rgb(14 165 233 / 12%), transparent 35%),
    var(--app-background);
}

.auth-layout__background {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.auth-layout__decoration {
  position: absolute;
  border-radius: 50%;
  filter: blur(2px);
}

.auth-layout__decoration--one {
  top: -8rem;
  left: -8rem;
  width: 24rem;
  height: 24rem;
  background: rgb(37 99 235 / 8%);
}

.auth-layout__decoration--two {
  right: -10rem;
  bottom: -10rem;
  width: 28rem;
  height: 28rem;
  background: rgb(14 165 233 / 8%);
}

.auth-layout__content {
  position: relative;
  z-index: 1;
  width: 100%;
}
</style>
