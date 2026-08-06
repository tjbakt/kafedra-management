<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const currentYear = new Date().getFullYear()
const { t } = useI18n()
</script>

<template>
  <footer class="app-footer">
    <span>
      © {{ currentYear }} Kafedra Management.
      {{ t('app.allRightsReserved') }}
    </span>

    <span class="app-footer__status">
      <i class="pi pi-circle-fill" />
      {{ t('app.systemWorking') }}
    </span>
  </footer>
</template>

<style scoped>
.app-footer {
  display: flex;
  min-height: var(--app-footer-height);
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0 1.5rem;
  border-top: 1px solid var(--app-border-color);
  color: var(--app-text-muted);
  font-size: 0.75rem;
}

.app-footer__status {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.app-footer__status i {
  color: var(--app-success);
  font-size: 0.45rem;
}

@media (max-width: 575px) {
  .app-footer {
    justify-content: center;
    text-align: center;
  }

  .app-footer__status {
    display: none;
  }
}
</style>
