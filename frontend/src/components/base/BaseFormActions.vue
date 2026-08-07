<script setup lang="ts">
import Button from 'primevue/button'
import { useI18n } from 'vue-i18n'

withDefaults(
  defineProps<{
    loading?: boolean
    disabled?: boolean

    saveLabel?: string
    cancelLabel?: string

    submitIcon?: string

    showCancel?: boolean
  }>(),
  {
    loading: false,
    disabled: false,

    saveLabel: '',
    cancelLabel: '',

    submitIcon: 'pi pi-check',

    showCancel: true,
  },
)

const emit = defineEmits<{
  submit: []
  cancel: []
}>()

const { t } = useI18n()
</script>

<template>
  <div class="base-form-actions">
    <slot name="start" />

    <div
      class="base-form-actions__buttons"
    >
      <Button
        v-if="showCancel"
        type="button"
        :label="
          cancelLabel ||
          t('common.cancel')
        "
        severity="secondary"
        outlined
        :disabled="loading"
        @click="emit('cancel')"
      />

      <Button
        type="button"
        :label="
          saveLabel ||
          t('common.save')
        "
        :icon="submitIcon"
        :loading="loading"
        :disabled="
          disabled || loading
        "
        @click="emit('submit')"
      />
    </div>
  </div>
</template>

<style scoped>
.base-form-actions {
  display: flex;
  align-items: center;
  justify-content:
    space-between;
  gap: 1rem;
}

.base-form-actions__buttons {
  display: flex;
  margin-left: auto;
  flex-wrap: wrap;
  gap: 0.5rem;
}

@media (max-width: 575px) {
  .base-form-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .base-form-actions__buttons {
    width: 100%;
    margin-left: 0;
  }

  .base-form-actions__buttons
    :deep(.p-button) {
    flex: 1;
  }
}
</style>
