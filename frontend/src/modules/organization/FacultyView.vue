<script setup lang="ts">
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import Button from 'primevue/button'
import Select from 'primevue/select'
import Tag from 'primevue/tag'

import BaseCard from '@/components/base/BaseCard.vue'
import BaseDataTable from '@/components/base/BaseDataTable.vue'
import BasePageHeader from '@/components/base/BasePageHeader.vue'
import BaseToolbar from '@/components/base/BaseToolbar.vue'

import FacultyFormDialog from '@/modules/organization/FacultyFormDialog.vue'

import {
  facultiesApi,
  getUniversityOptions,
} from '@/modules/organization/api'

import type {
  Faculty,
  FacultyPayload,
  UniversityOption,
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

const universities =
  ref<UniversityOption[]>([])

const selectedUniversity =
  ref<number | null>(null)

const selectedFaculty =
  ref<Faculty | null>(null)

const formVisible =
  ref(false)

const saving =
  ref(false)

const lookupsLoading =
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
      'organizations.add_faculty',
    ),
  )

const canEdit =
  computed(() =>
    can(
      'organizations.change_faculty',
    ),
  )

const canDelete =
  computed(() =>
    can(
      'organizations.delete_faculty',
    ),
  )

const columns =
  computed<
    CrudColumn<Faculty>[]
  >(() => [
    {
      field: 'code',
      header: 'Код',
      sortable: true,
      width: '8rem',
    },

    {
      field: 'display_name',
      header: 'Факультет',
      sortable: true,
      sortField: 'name_ru',
      minWidth: '20rem',
    },

    {
      field: 'university_name',
      header: 'ВУЗ',
      minWidth: '18rem',
    },

    {
      field: 'faculty_type',
      header: 'Тип',
      bodySlot: 'type',
      width: '14rem',
    },

    {
      field: 'dean_name',
      header: 'Руководитель',
      minWidth: '15rem',
    },

    {
      field: 'departments_count',
      header: 'Кафедр',
      width: '9rem',
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

const universityFilterOptions =
  computed(() => [
    {
      value: null,
      label: 'Все ВУЗы',
    },

    ...universities.value.map(
      (university) => ({
        value: university.id,
        label:
          university.display_name,
      }),
    ),
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

  setFilter,
} = useCrudList<Faculty>(
  (params) =>
    facultiesApi.list(
      params,
    ),
  {
    initialPageSize: 20,
    initialOrdering:
      'sort_order,name_ru',
  },
)

async function loadUniversities(): Promise<void> {
  lookupsLoading.value = true

  try {
    const response =
      await getUniversityOptions()

    universities.value =
      response.results
  } catch (lookupError) {
    const normalized =
      normalizeApiError(
        lookupError,
        'Не удалось загрузить список ВУЗов',
      )

    toast.error(
      'Ошибка',
      normalized.message,
    )
  } finally {
    lookupsLoading.value = false
  }
}

async function applyUniversityFilter(): Promise<void> {
  setFilter(
    'university',
    selectedUniversity.value,
  )

  await load()
}

function clearFormErrors(): void {
  fieldErrors.value = {}
  nonFieldErrors.value = []
  generalFormError.value = ''
}

function openCreate(): void {
  selectedFaculty.value = null

  clearFormErrors()

  formVisible.value = true
}

function openEdit(
  faculty: Faculty,
): void {
  selectedFaculty.value =
    faculty

  clearFormErrors()

  formVisible.value = true
}

async function saveFaculty(
  payload: FacultyPayload,
): Promise<void> {
  saving.value = true
  clearFormErrors()

  try {
    if (selectedFaculty.value) {
      await facultiesApi.update(
        selectedFaculty.value.id,
        payload,
      )

      toast.success(
        'Успешно',
        'Факультет обновлён',
      )
    } else {
      await facultiesApi.create(
        payload,
      )

      toast.success(
        'Успешно',
        'Факультет создан',
      )
    }

    formVisible.value = false
    selectedFaculty.value = null

    await refresh()
  } catch (saveError) {
    const normalized =
      normalizeApiError(
        saveError,
        'Не удалось сохранить факультет',
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

function archiveFaculty(
  faculty: Faculty,
): void {
  confirmDelete({
    header:
      'Архивирование факультета',

    message:
      `Архивировать факультет «${faculty.display_name}»?`,

    accept: async () => {
      try {
        await facultiesApi.remove(
          faculty.id,
        )

        toast.success(
          'Успешно',
          'Факультет архивирован',
        )

        await refresh()
      } catch (archiveError) {
        const normalized =
          normalizeApiError(
            archiveError,
            'Не удалось архивировать факультет',
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
  await Promise.all([
    load(),
    loadUniversities(),
  ])
})
</script>

<template>
  <div class="organization-list">
    <BasePageHeader
      title="Факультеты"
      description="Факультеты и учебные отделения ВУЗов"
      icon="pi pi-building-columns"
    >
      <template #actions>
        <Button
          v-if="canCreate"
          label="Добавить факультет"
          icon="pi pi-plus"
          :disabled="lookupsLoading"
          @click="openCreate"
        />
      </template>
    </BasePageHeader>

    <BaseToolbar
      v-model:search="searchInput"
      :show-search="true"
      :show-create="false"
      :show-reset="false"
      :loading="
        loading ||
        lookupsLoading
      "
      @refresh="refresh"
    >
      <template #center>
        <Select
          v-model="
            selectedUniversity
          "
          :options="
            universityFilterOptions
          "
          option-label="label"
          option-value="value"
          placeholder="Все ВУЗы"
          class="university-filter"
          :disabled="
            lookupsLoading
          "
          @change="
            applyUniversityFilter
          "
        />
      </template>
    </BaseToolbar>

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
        <template #type="{ row }">
          <Tag
            :value="
              row.faculty_type ===
              'magistracy'
                ? 'Магистратура'
                : 'Обычный факультет'
            "
            :severity="
              row.faculty_type ===
              'magistracy'
                ? 'info'
                : 'secondary'
            "
          />
        </template>

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
              archiveFaculty(row)
            "
          />
        </template>
      </BaseDataTable>
    </BaseCard>

    <FacultyFormDialog
      v-model="formVisible"
      :faculty="selectedFaculty"
      :universities="universities"
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
      @submit="saveFaculty"
    />
  </div>
</template>

<style scoped>
.organization-list {
  display: grid;
  gap: 1rem;
}

.university-filter {
  width: 18rem;
}

@media (max-width: 767px) {
  .university-filter {
    width: 100%;
  }
}
</style>
