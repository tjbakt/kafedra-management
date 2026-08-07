<script setup lang="ts">
import ProgressSpinner from 'primevue/progressspinner'

import { useI18n } from 'vue-i18n'

withDefaults(
  defineProps<{
    text?: string
    minHeight?: string
  }>(),
  {
    text: '',
    minHeight: '14rem',
  },
)

const { t } = useI18n()
</script>

<template>
  <div
    class="base-loading-state"
    :style="{
      minHeight,
    }"
  >
    <ProgressSpinner
      style="width: 2.5rem; height: 2.5rem;"
      :stroke-width="4"
    />

    <span>
      {{
        text ||
        t('common.loading')
      }}
    </span>
  </div>
</template>

<style scoped>
.base-loading-state {
  display: grid;
  place-content: center;
  justify-items: center;
  gap: 0.75rem;
  color:
    var(--app-text-muted);
  font-size: 0.8rem;
}
</style>
