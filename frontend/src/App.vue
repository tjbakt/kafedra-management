<script setup lang="ts">
import AppConfirmDialog from '@/components/feedback/AppConfirmDialog.vue'
import AppToast from '@/components/feedback/AppToast.vue'
</script>

<template>
  <RouterView />

  <AppToast />
  <AppConfirmDialog />
</template>
