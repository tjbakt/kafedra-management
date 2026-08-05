<script setup lang="ts">
import Breadcrumb from 'primevue/breadcrumb'
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const home = {
  icon: 'pi pi-home',
  command: () => router.push('/'),
}

const items = computed(() => {
  const breadcrumbs = route.meta.breadcrumb

  if (!Array.isArray(breadcrumbs)) {
    return []
  }

  return breadcrumbs.map((item) => ({
    ...item,
    command: item.route ? () => router.push(item.route) : undefined,
  }))
})
</script>

<template>
  <Breadcrumb v-if="items.length" :home="home" :model="items" class="app-breadcrumb" />
</template>

<style scoped>
.app-breadcrumb {
  margin-bottom: 1rem;
  padding: 0;
  border: 0;
  background: transparent;
}
</style>
