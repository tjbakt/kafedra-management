<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Button from 'primevue/button'

import BaseCard from '@/components/base/BaseCard.vue'
import BaseEmptyState from '@/components/base/BaseEmptyState.vue'
import BasePageHeader from '@/components/base/BasePageHeader.vue'
import { useAppToast } from '@/composables/useAppToast'

const route = useRoute()
const toast = useAppToast()

const title = computed(() => String(route.meta.title || 'Раздел'))
const description = computed(() =>
  String(
    route.meta.description || 'Интерфейс данного раздела будет реализован на следующих этапах.',
  ),
)
const icon = computed(() => String(route.meta.icon || 'pi pi-folder'))
</script>

<template>
  <div>
    <BasePageHeader :title="title" :description="description" :icon="icon">
      <template #actions>
        <Button
          label="Создать"
          icon="pi pi-plus"
          @click="
            toast.info(
              'Демонстрационный режим',
              'Форма создания будет добавлена на этапе реализации CRUD.',
            )
          "
        />
      </template>
    </BasePageHeader>

    <BaseCard>
      <BaseEmptyState
        :icon="icon"
        title="Модуль подготовлен"
        description="Маршрут, layout и базовые компоненты подключены. CRUD-интерфейс будет реализован на соответствующем этапе."
      >
        <template #actions>
          <Button
            label="Вернуться на главную"
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
