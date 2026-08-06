<script setup lang="ts">
import Button from 'primevue/button'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="not-found">
    <div class="not-found__code">404</div>

    <span class="not-found__icon">
      <i class="pi pi-search" />
    </span>

    <h1>{{ t('errors.notFoundTitle') }}</h1>

    <p>
      {{ t('errors.notFoundDescription') }}
    </p>

    <Button
      :label="t('modules.returnHome')"
      icon="pi pi-home"
      as="router-link"
      to="/"
    />
  </div>
</template>

<style scoped>
.not-found {
  display: grid;
  min-height: 100vh;
  place-content: center;
  justify-items: center;
  padding: 2rem;
  text-align: center;
}

.not-found__code {
  color: color-mix(
    in srgb,
    var(--app-primary) 10%,
    transparent
  );
  font-size: clamp(7rem, 24vw, 14rem);
  font-weight: 800;
  line-height: 0.8;
}

.not-found__icon {
  display: grid;
  width: 4rem;
  height: 4rem;
  margin-top: -2rem;
  place-items: center;
  border-radius: 50%;
  background: var(--app-primary);
  color: white;
  box-shadow: var(--app-shadow);
}

.not-found__icon i {
  font-size: 1.5rem;
}

.not-found h1 {
  margin: 1.5rem 0 0.5rem;
}

.not-found p {
  max-width: 32rem;
  margin: 0 0 1.5rem;
  color: var(--app-text-muted);
}
</style>
