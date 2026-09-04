<script setup lang="ts">
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import Button from 'primevue/button'
import Tag from 'primevue/tag'

import BaseCard from '@/components/base/BaseCard.vue'
import BaseDataTable from '@/components/base/BaseDataTable.vue'
import BasePageHeader from '@/components/base/BasePageHeader.vue'
import BaseToolbar from '@/components/base/BaseToolbar.vue'

import UniversityFormDialog from '@/modules/organization/UniversityFormDialog.vue'

import {
  universitiesApi,
} from '@/modules/organization/api'

import type {
  University,
  UniversityPayload,
} from '@/modules/organization/types'

import {
  useCrudList,
} from '@/composables/useCrudList'

import {
  useAppConfirm,
} from '@/composables/useAppConfirm'

import {
  useAppToast,
} from '@/composables/useAppToast'

import {
  usePermissions,
} from '@/composables/usePermissions'

import type {
  CrudColumn,
} from '@/types/crud'

import type {
  FieldErrors,
} from '@/types/validation'

import {
  normalizeApiError,
} from '@/utils/api-errors'

const toast =
  useAppToast()

const {
  confirmDelete,
} = useAppConfirm()

const {
  can,
} = usePermissions()

const selectedUniversity =
  ref<University | null>(null)

const formVisible =
  ref(false)

const saving =
  ref(false)

const fieldErrors =
  ref<FieldErrors>({})

const nonFieldErrors =
  ref<string[]>([])

const generalFormError =
  ref('')

const canCreate =
  computed(() =>
    can(
      'organizations.add_university',
    ),
  )

const canEdit =
  computed(() =>
    can(
      'organizations.change_university',
    ),
  )

const canDelete =
  computed(() =>
    can(
      'organizations.delete_university',
    ),
  )

const columns =
  computed<
    CrudColumn<University>[]
  >(() => [
    {
      field: 'code',
      header: 'Код',
      sortable: true,
      width: '8rem',
    },

    {
      field: 'display_name',
      header: 'ВУЗ',
      sortable: true,
      sortField: 'name_ru',
      minWidth: '20rem',
    },

    {
      field: 'display_short_name',
      header: 'Краткое название',
      minWidth: '14rem',
    },

    {
      field: 'faculties_count',
      header: 'Факультетов',
      width: '10rem',
      align: 'center',
    },

    {
      field: 'is_active',
      header: 'Статус',
      bodySlot: 'status',
      width: '9rem',
      align: 'center',
    },
  ])

const {
  items,
  totalRecords,
  loading,
  error,

  query,
  searchInput,
  first,

  load,
  refresh,

  handlePage,
  handleSort,
} = useCrudList<University>(
  (params) =>
    universitiesApi.list(
      params,
    ),
  {
    initialPageSize: 20,
    initialOrdering:
      'sort_order,name_ru',
  },
)

function clearFormErrors(): void {
  fieldErrors.value = {}
  nonFieldErrors.value = []
  generalFormError.value = ''
}

function openCreate(): void {
  selectedUniversity.value = null
  clearFormErrors()
  formVisible.value = true
}

function openEdit(
  university: University,
): void {
  selectedUniversity.value =
    university

  clearFormErrors()
  formVisible.value = true
}

async function saveUniversity(
  payload: UniversityPayload,
): Promise<void> {
  saving.value = true
  clearFormErrors()

  try {
    if (selectedUniversity.value) {
      await universitiesApi.update(
        selectedUniversity.value.id,
        payload,
      )

      toast.success(
        'Успешно',
        'ВУЗ обновлён',
      )
    } else {
      await universitiesApi.create(
        payload,
      )

      toast.success(
        'Успешно',
        'ВУЗ создан',
      )
    }

    formVisible.value = false
    selectedUniversity.value = null

    await refresh()
  } catch (saveError) {
    const normalized =
      normalizeApiError(
        saveError,
        'Не удалось сохранить ВУЗ',
      )

    fieldErrors.value =
      normalized.fieldErrors

    nonFieldErrors.value =
      normalized.nonFieldErrors

    generalFormError.value =
      normalized.message
  } finally {
    saving.value = false
  }
}

function archiveUniversity(
  university: University,
): void {
  confirmDelete({
    header:
      'Архивирование ВУЗа',

    message:
      `Архивировать ВУЗ «${university.display_name}»?`,

    accept: async () => {
      try {
        await universitiesApi.remove(
          university.id,
        )

        toast.success(
          'Успешно',
          'ВУЗ архивирован',
        )

        await refresh()
      } catch (archiveError) {
        const normalized =
          normalizeApiError(
            archiveError,
            'Не удалось архивировать ВУЗ',
          )

        toast.error(
          'Ошибка',
          normalized.message,
        )
      }
    },
  })
}

onMounted(async () => {
  await load()
})
</script>

<template>
  <div class="organization-list">
    <BasePageHeader
      title="ВУЗ"
      description="Справочник высших образовательных учреждений"
      icon="pi pi-building"
    >
      <template #actions>
        <Button
          v-if="canCreate"
          label="Добавить ВУЗ"
          icon="pi pi-plus"
          @click="openCreate"
        />
      </template>
    </BasePageHeader>

    <BaseToolbar
      v-model:search="searchInput"
      :show-search="true"
      :show-create="false"
      :show-reset="false"
      :loading="loading"
      @refresh="refresh"
    />

    <BaseCard :padding="false">
      <BaseDataTable
        :value="items"
        :columns="columns"
        :loading="loading"
        :error="error"
        :first="first"
        :rows="query.pageSize"
        :total-records="totalRecords"
        show-row-actions
        @page="handlePage"
        @sort="handleSort"
        @retry="refresh"
      >
        <template #status="{ row }">
          <Tag
            :value="
              row.is_active
                ? 'Активен'
                : 'Неактивен'
            "
            :severity="
              row.is_active
                ? 'success'
                : 'secondary'
            "
          />
        </template>

        <template #actions="{ row }">
          <Button
            v-if="canEdit"
            v-tooltip.bottom="'Редактировать'"
            icon="pi pi-pencil"
            text
            rounded
            @click.stop="
              openEdit(row)
            "
          />

          <Button
            v-if="
              canDelete &&
              !row.is_archived
            "
            v-tooltip.bottom="'Архивировать'"
            icon="pi pi-box"
            severity="danger"
            text
            rounded
            @click.stop="
              archiveUniversity(row)
            "
          />
        </template>
      </BaseDataTable>
    </BaseCard>

    <UniversityFormDialog
      v-model="formVisible"
      :university="
        selectedUniversity
      "
      :loading="saving"
      :field-errors="
        fieldErrors
      "
      :non-field-errors="
        nonFieldErrors
      "
      :general-error="
        generalFormError
      "
      @submit="saveUniversity"
    />
  </div>
</template>

<style scoped>
.organization-list {
  display: grid;
  gap: 1rem;
}
</style>
