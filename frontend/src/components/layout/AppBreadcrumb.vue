<script setup lang="ts">
import Breadcrumb from 'primevue/breadcrumb'
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const home = computed(() => ({
  icon: 'pi pi-home',
  label: t('navigation.dashboard'),
  command: () => router.push('/'),
}))

const items = computed(() => {
  const breadcrumbKeys =
    route.meta.breadcrumbKeys

  if (!Array.isArray(breadcrumbKeys)) {
    return []
  }

  return breadcrumbKeys.map((key) => ({
    label: t(String(key)),
  }))
})
</script>

<template>
  <Breadcrumb
    v-if="items.length"
    :home="home"
    :model="items"
    class="app-breadcrumb"
  />
</template>

<style scoped>
.app-breadcrumb {
  margin-bottom: 1rem;
  padding: 0;
  border: 0;
  background: transparent;
}
</style>
