<script setup lang="ts">
defineProps<{
  label: string
  name?: string
  required?: boolean
  error?: string
  hint?: string
}>()
</script>

<template>
  <div class="form-field" :class="{ 'form-field--invalid': error }">
    <label v-if="name" :for="name" class="form-field__label">
      {{ label }}
      <span v-if="required" aria-hidden="true">*</span>
    </label>

    <span v-else class="form-field__label">
      {{ label }}
      <span v-if="required" aria-hidden="true">*</span>
    </span>

    <slot />

    <small v-if="error" class="form-field__error">
      <i class="pi pi-exclamation-circle" />
      {{ error }}
    </small>

    <small v-else-if="hint" class="form-field__hint">
      {{ hint }}
    </small>
  </div>
</template>

<style scoped>
.form-field {
  display: grid;
  gap: 0.45rem;
}

.form-field__label {
  font-size: 0.8rem;
  font-weight: 600;
}

.form-field__label span {
  color: var(--app-danger);
}

.form-field__error {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: var(--app-danger);
  font-size: 0.73rem;
}

.form-field__hint {
  color: var(--app-text-muted);
  font-size: 0.73rem;
}
</style>
