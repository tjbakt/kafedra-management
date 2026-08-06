<script setup lang="ts">
import AppConfirmDialog from '@/components/feedback/AppConfirmDialog.vue'
import AppLocaleSynchronizer from '@/components/feedback/AppLocaleSynchronizer.vue'
import AppToast from '@/components/feedback/AppToast.vue'
</script>

<template>
  <RouterView />

  <AppLocaleSynchronizer />
  <AppToast />
  <AppConfirmDialog />
</template>
