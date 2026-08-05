<script setup lang="ts">
defineProps<{
  title: string
  description?: string
  icon?: string
}>()
</script>

<template>
  <header class="page-header">
    <div class="page-header__main">
      <span v-if="icon" class="page-header__icon">
        <i :class="icon" />
      </span>

      <div>
        <h1>{{ title }}</h1>
        <p v-if="description">{{ description }}</p>
      </div>
    </div>

    <div v-if="$slots.actions" class="page-header__actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.page-header__main {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.page-header__icon {
  display: grid;
  width: 2.75rem;
  height: 2.75rem;
  flex: 0 0 2.75rem;
  place-items: center;
  border-radius: 0.8rem;
  background: color-mix(in srgb, var(--app-primary) 12%, transparent);
  color: var(--app-primary);
}

.page-header h1 {
  margin: 0;
  font-size: clamp(1.3rem, 2vw, 1.7rem);
  line-height: 1.2;
}

.page-header p {
  max-width: 52rem;
  margin: 0.35rem 0 0;
  color: var(--app-text-muted);
  font-size: 0.84rem;
  line-height: 1.5;
}

.page-header__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
}

@media (max-width: 767px) {
  .page-header {
    flex-direction: column;
  }

  .page-header__actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
