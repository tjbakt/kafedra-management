<script setup lang="ts">
import Button from 'primevue/button'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import InputText from 'primevue/inputtext'
import Toolbar from 'primevue/toolbar'

import { useI18n } from 'vue-i18n'

const search = defineModel<string>(
  'search',
  {
    default: '',
  },
)

withDefaults(
  defineProps<{
    showSearch?: boolean
    showCreate?: boolean
    showRefresh?: boolean
    showReset?: boolean

    createLabel?: string
    searchPlaceholder?: string

    loading?: boolean
    disabled?: boolean
  }>(),
  {
    showSearch: true,
    showCreate: true,
    showRefresh: true,
    showReset: false,

    createLabel: '',
    searchPlaceholder: '',

    loading: false,
    disabled: false,
  },
)

const emit = defineEmits<{
  create: []
  refresh: []
  reset: []
}>()

const { t } = useI18n()
</script>

<template>
  <Toolbar class="base-toolbar">
    <template #start>
      <div class="base-toolbar__group">
        <Button
          v-if="showCreate"
          :label="
            createLabel ||
            t('common.create')
          "
          icon="pi pi-plus"
          :disabled="
            disabled || loading
          "
          @click="emit('create')"
        />

        <slot name="start" />
      </div>
    </template>

    <template #center>
      <div
        v-if="
          showSearch ||
          $slots.center
        "
        class="base-toolbar__center"
      >
        <IconField
          v-if="showSearch"
          class="base-toolbar__search"
        >
          <InputIcon>
            <i class="pi pi-search" />
          </InputIcon>

          <InputText
            v-model="search"
            :placeholder="
              searchPlaceholder ||
              t('common.search')
            "
            :disabled="disabled"
            class="w-full"
          />
        </IconField>

        <slot name="center" />
      </div>
    </template>

    <template #end>
      <div class="base-toolbar__group">
        <slot name="end" />

        <Button
          v-if="showReset"
          v-tooltip.bottom="
            t('common.reset')
          "
          icon="pi pi-filter-slash"
          severity="secondary"
          outlined
          :disabled="
            disabled || loading
          "
          :aria-label="
            t('common.reset')
          "
          @click="emit('reset')"
        />

        <Button
          v-if="showRefresh"
          v-tooltip.bottom="
            t('common.refresh')
          "
          icon="pi pi-refresh"
          severity="secondary"
          outlined
          :loading="loading"
          :disabled="disabled"
          :aria-label="
            t('common.refresh')
          "
          @click="emit('refresh')"
        />
      </div>
    </template>
  </Toolbar>
</template>

<style scoped>
.base-toolbar {
  border:
    1px solid
    var(--app-border-color);
  border-radius:
    var(--app-radius-lg);
  background:
    var(--app-surface);
}

.base-toolbar__group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.base-toolbar__center {
  display: flex;
  width: min(30rem, 100%);
  align-items: center;
  gap: 0.5rem;
}

.base-toolbar__search {
  width: 100%;
}

@media (max-width: 767px) {
  .base-toolbar {
    padding: 0.75rem;
  }

  .base-toolbar__center {
    width: 100%;
  }
}
</style>
