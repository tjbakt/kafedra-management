<script setup lang="ts">
import {
  onBeforeUnmount,
  onMounted,
} from 'vue'

import Toast from 'primevue/toast'

import {
  API_ERROR_TOAST_EVENT,
  type ApiErrorToastPayload,
} from '@/utils/api-error-toast'

import { useAppToast } from '@/composables/useAppToast'

const { showApiError, } = useAppToast()

function handleApiError(event: Event): void {
  const customEvent =
    event as CustomEvent<ApiErrorToastPayload>

  if (!customEvent.detail?.error) {
    return
  }

  showApiError(customEvent.detail)
}

onMounted(() => {
  window.addEventListener(
    API_ERROR_TOAST_EVENT,
    handleApiError,
  )
})

onBeforeUnmount(() => {
  window.removeEventListener(
    API_ERROR_TOAST_EVENT,
    handleApiError,
  )
})
</script>

<template>
  <Toast
    position="top-right"
    :style="{ width: 'min(32rem, calc(100vw - 2rem))', }"
  />
</template>
