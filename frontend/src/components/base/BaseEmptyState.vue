<script setup lang="ts">
withDefaults(
  defineProps<{
    icon?: string
    title?: string
    description?: string
  }>(),
  {
    icon: 'pi pi-inbox',
    title: 'Данные отсутствуют',
    description: 'Для отображения пока нет доступных данных.',
  },
)
</script>

<template>
  <div class="empty-state">
    <span class="empty-state__icon">
      <i :class="icon" />
    </span>

    <h3>{{ title }}</h3>
    <p>{{ description }}</p>

    <div v-if="$slots.actions" class="empty-state__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<style scoped>
.empty-state {
  display: grid;
  min-height: 16rem;
  place-content: center;
  justify-items: center;
  padding: 2rem;
  text-align: center;
}

.empty-state__icon {
  display: grid;
  width: 4rem;
  height: 4rem;
  place-items: center;
  border-radius: 50%;
  background: var(--app-hover-bg);
  color: var(--app-text-muted);
}

.empty-state__icon i {
  font-size: 1.6rem;
}

.empty-state h3 {
  margin: 1rem 0 0.35rem;
  font-size: 1rem;
}

.empty-state p {
  max-width: 26rem;
  margin: 0;
  color: var(--app-text-muted);
  font-size: 0.82rem;
  line-height: 1.5;
}

.empty-state__actions {
  margin-top: 1rem;
}
</style>
