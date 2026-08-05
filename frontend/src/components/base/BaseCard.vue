<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string
    subtitle?: string
    padding?: boolean
  }>(),
  {
    title: '',
    subtitle: '',
    padding: true,
  },
)
</script>

<template>
  <section class="base-card">
    <header v-if="title || subtitle || $slots.header || $slots.actions" class="base-card__header">
      <slot name="header">
        <div>
          <h2 v-if="title">{{ title }}</h2>
          <p v-if="subtitle">{{ subtitle }}</p>
        </div>
      </slot>

      <div v-if="$slots.actions" class="base-card__actions">
        <slot name="actions" />
      </div>
    </header>

    <div class="base-card__content" :class="{ 'base-card__content--padded': padding }">
      <slot />
    </div>

    <footer v-if="$slots.footer" class="base-card__footer">
      <slot name="footer" />
    </footer>
  </section>
</template>

<style scoped>
.base-card {
  border: 1px solid var(--app-border-color);
  border-radius: var(--app-radius-lg);
  background: var(--app-surface);
  box-shadow: var(--app-shadow-sm);
}

.base-card__header {
  display: flex;
  min-height: 4.25rem;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--app-border-color);
}

.base-card__header h2 {
  margin: 0;
  font-size: 1rem;
}

.base-card__header p {
  margin: 0.3rem 0 0;
  color: var(--app-text-muted);
  font-size: 0.78rem;
}

.base-card__actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.base-card__content--padded {
  padding: 1.25rem;
}

.base-card__footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--app-border-color);
}
</style>
