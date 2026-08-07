<script setup lang="ts">
import Button from 'primevue/button'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

const router = useRouter()
const { t } = useI18n()

function goBack(): void {
  if (window.history.length > 1) {
    router.back()
    return
  }

  void router.push('/')
}
</script>

<template>
  <div class="forbidden-page">
    <div class="forbidden-page__code">
      403
    </div>

    <span class="forbidden-page__icon">
      <i class="pi pi-lock" />
    </span>

    <h1>
      {{ t('errors.forbiddenTitle') }}
    </h1>

    <p>
      {{ t('errors.forbiddenDescription') }}
    </p>

    <div class="forbidden-page__actions">
      <Button
        :label="t('common.back')"
        icon="pi pi-arrow-left"
        severity="secondary"
        outlined
        @click="goBack"
      />

      <Button
        :label="t('modules.returnHome')"
        icon="pi pi-home"
        as="router-link"
        to="/"
      />
    </div>
  </div>
</template>

<style scoped>
.forbidden-page {
  display: grid;
  min-height: 100vh;
  place-content: center;
  justify-items: center;
  padding: 2rem;
  text-align: center;
}

.forbidden-page__code {
  color: color-mix(
    in srgb,
    var(--app-danger) 10%,
    transparent
  );
  font-size: clamp(
    7rem,
    24vw,
    14rem
  );
  font-weight: 800;
  line-height: 0.8;
}

.forbidden-page__icon {
  display: grid;
  width: 4rem;
  height: 4rem;
  margin-top: -2rem;
  place-items: center;
  border-radius: 50%;
  background: var(--app-danger);
  color: white;
  box-shadow: var(--app-shadow);
}

.forbidden-page__icon i {
  font-size: 1.5rem;
}

.forbidden-page h1 {
  margin: 1.5rem 0 0.5rem;
}

.forbidden-page p {
  max-width: 36rem;
  margin: 0 0 1.5rem;
  color: var(--app-text-muted);
  line-height: 1.6;
}

.forbidden-page__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.75rem;
}
</style>
