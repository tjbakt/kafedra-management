<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'

import BaseCard from '@/components/base/BaseCard.vue'
import BaseEmptyState from '@/components/base/BaseEmptyState.vue'
import BasePageHeader from '@/components/base/BasePageHeader.vue'
import { useAppToast } from '@/composables/useAppToast'

const route = useRoute()
const toast = useAppToast()
const { t } = useI18n()

const title = computed(() => {
  const titleKey = route.meta.titleKey

  return typeof titleKey === 'string'
    ? t(titleKey)
    : ''
})

const description = computed(() => {
  const descriptionKey =
    route.meta.descriptionKey

  return typeof descriptionKey === 'string'
    ? t(descriptionKey)
    : t('modules.preparedDescription')
})

const icon = computed(() =>
  String(route.meta.icon || 'pi pi-folder'),
)

function showCreateMessage(): void {
  toast.info(
    t('modules.demoMode'),
    t('modules.createLater'),
  )
}
</script>

<template>
  <div>
    <BasePageHeader
      :title="title"
      :description="description"
      :icon="icon"
    >
      <template #actions>
        <Button
          :label="t('common.create')"
          icon="pi pi-plus"
          @click="showCreateMessage"
        />
      </template>
    </BasePageHeader>

    <BaseCard>
      <BaseEmptyState
        :icon="icon"
        :title="t('modules.prepared')"
        :description="
          t('modules.preparedDescription')
        "
      >
        <template #actions>
          <Button
            :label="t('modules.returnHome')"
            icon="pi pi-home"
            severity="secondary"
            outlined
            as="router-link"
            to="/"
          />
        </template>
      </BaseEmptyState>
    </BaseCard>
  </div>
</template>
