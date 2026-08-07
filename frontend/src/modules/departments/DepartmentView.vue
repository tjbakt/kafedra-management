<script setup lang="ts">
import Button from 'primevue/button'
import Select from 'primevue/select'
import Tag from 'primevue/tag'

import {
  computed,
  onMounted,
  ref,
} from 'vue'

import { useI18n } from 'vue-i18n'
import { useLocaleStore } from '@/stores/locale'

import BaseCard from '@/components/base/BaseCard.vue'
import BaseDataTable from '@/components/base/BaseDataTable.vue'
import BasePageHeader from '@/components/base/BasePageHeader.vue'
import BaseToolbar from '@/components/base/BaseToolbar.vue'

import DepartmentDetailsDialog from '@/modules/departments/components/DepartmentDetailsDialog.vue'
import DepartmentFormDialog from '@/modules/departments/components/DepartmentFormDialog.vue'

import {
  departmentsApi,
  getFacultyOptions,
  getUniversityOptions,
} from '@/modules/departments/api'

import type {
  Department,
  DepartmentPayload,
  FacultyOption,
  UniversityOption,
} from '@/modules/departments/types'

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

const { t } = useI18n()
const localeStore = useLocaleStore()
const toast = useAppToast()

const {
  confirmDelete,
} = useAppConfirm()

const {
  can,
} = usePermissions()

const selectedDepartment =
  ref<Department | null>(
    null,
  )

const formVisible =
  ref(false)

const detailsVisible =
  ref(false)

const saving =
  ref(false)

const universities =
  ref<UniversityOption[]>([])

const faculties =
  ref<FacultyOption[]>([])

const lookupsLoading =
  ref(false)

const selectedUniversity =
  ref<number | null>(null)

const selectedFaculty =
  ref<number | null>(null)

const selectedActive =
  ref<boolean | null>(null)

const fieldErrors =
  ref<FieldErrors>({})

const nonFieldErrors =
  ref<string[]>([])

const generalFormError =
  ref('')

const canCreate = computed(
  () =>
    can(
      'organizations.add_department',
    ),
)

const canEdit = computed(
  () =>
    can(
      'organizations.change_department',
    ),
)

const canDelete = computed(
  () =>
    can(
      'organizations.delete_department',
    ),
)

const statusOptions =
  computed(() => [
    {
      label:
        t(
          'departments.allStatuses',
        ),
      value: null,
    },
    {
      label:
        t(
          'departments.active',
        ),
      value: true,
    },
    {
      label:
        t(
          'departments.inactive',
        ),
      value: false,
    },
  ])

const universityOptions =
  computed(() => [
    {
      id: null,
      display_name:
        t(
          'departments.allUniversities',
        ),
    },
    ...universities.value,
  ])

const facultyOptions =
  computed(() => {
    const source =
      selectedUniversity.value
        ? faculties.value.filter(
            (faculty) =>
              faculty.university ===
              selectedUniversity.value,
          )
        : faculties.value

    return [
      {
        id: null,
        display_name:
          t(
            'departments.allFaculties',
          ),
      },
      ...source,
    ]
  })

const columns =
  computed<
    CrudColumn<Department>[]
  >(() => [
    {
      field: 'code',
      header:
        t(
          'departments.fields.code',
        ),
      sortable: true,
      minWidth: '8rem',
    },
    {
      field: 'display_name',

      header:
        t(
          'departments.fields.name',
        ),

      sortable: true,

      sortField:
        localeStore.locale ===
        'uz'
          ? 'name_uz'
          : 'name_ru',

      minWidth: '16rem',
    },
    {
      field: 'faculty_name',
      header:
        t(
          'departments.fields.faculty',
        ),
      minWidth: '14rem',
    },
    {
      field: 'head_name',
      header:
        t(
          'departments.fields.head',
        ),
      minWidth: '13rem',
    },
    {
      field: 'room',
      header:
        t(
          'departments.fields.room',
        ),
      minWidth: '8rem',
    },
    {
      field: 'is_active',
      header:
        t(
          'departments.fields.status',
        ),
      sortable: false,
      bodySlot: 'status',
      width: '8rem',
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
  reset,

  handlePage,
  handleSort,

  setFilter,
  clearFilters,
} = useCrudList<Department>(
  (params) =>
    departmentsApi.list(
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

async function loadLookups(): Promise<void> {
  lookupsLoading.value = true

  try {
    const [
      universityResponse,
      facultyResponse,
    ] = await Promise.all([
      getUniversityOptions(),
      getFacultyOptions(),
    ])

    universities.value =
      universityResponse.results

    faculties.value =
      facultyResponse.results
  } catch (lookupError) {
    const normalized =
      normalizeApiError(
        lookupError,
        t(
          'crud.loadError',
        ),
      )

    toast.error(
      t('common.error'),
      normalized.message,
    )
  } finally {
    lookupsLoading.value = false
  }
}

function openCreate(): void {
  selectedDepartment.value =
    null

  clearFormErrors()

  formVisible.value = true
}

function openView(
  department: Department,
): void {
  selectedDepartment.value =
    department

  detailsVisible.value = true
}

function openEdit(
  department: Department,
): void {
  selectedDepartment.value =
    department

  clearFormErrors()

  formVisible.value = true
}

async function saveDepartment(
  payload: DepartmentPayload,
): Promise<void> {
  saving.value = true
  clearFormErrors()

  try {
    if (
      selectedDepartment.value
    ) {
      await departmentsApi.update(
        selectedDepartment.value.id,
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.updated'),
      )
    } else {
      await departmentsApi.create(
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.created'),
      )
    }

    formVisible.value = false
    selectedDepartment.value =
      null

    await refresh()
  } catch (saveError) {
    const normalized =
      normalizeApiError(
        saveError,
        t('crud.saveError'),
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

function archiveDepartment(
  department: Department,
): void {
  confirmDelete({
    header:
      t(
        'departments.archiveTitle',
      ),

    message:
      t(
        'departments.archiveConfirm',
        {
          name:
            department.display_name,
        },
      ),

    accept: async () => {
      try {
        await departmentsApi.remove(
          department.id,
        )

        toast.success(
          t('common.success'),
          t(
            'departments.archived',
          ),
        )

        await refresh()
      } catch (archiveError) {
        const normalized =
          normalizeApiError(
            archiveError,
            t(
              'crud.deleteError',
            ),
          )

        toast.error(
          t('common.error'),
          normalized.message,
        )
      }
    },
  })
}

async function applyUniversityFilter(): Promise<void> {
  setFilter(
    'university',
    selectedUniversity.value,
  )

  selectedFaculty.value =
    null

  setFilter(
    'faculty',
    undefined,
  )

  await load()
}

async function applyFacultyFilter(): Promise<void> {
  setFilter(
    'faculty',
    selectedFaculty.value,
  )

  await load()
}

async function applyActiveFilter(): Promise<void> {
  setFilter(
    'is_active',
    selectedActive.value,
  )

  await load()
}

async function resetFilters(): Promise<void> {
  selectedUniversity.value =
    null

  selectedFaculty.value =
    null

  selectedActive.value =
    null

  clearFilters()

  await reset()
}

onMounted(async () => {
  await Promise.all([
    load(),
    loadLookups(),
  ])
})
</script>

<template>
  <div
    class="departments-page"
  >
    <BasePageHeader
      :title="
        t(
          'departments.title',
        )
      "
      :description="
        t(
          'departments.description',
        )
      "
      icon="pi pi-building"
    >
      <template #actions>
        <Button
          v-if="canCreate"
          :label="
            t(
              'departments.create',
            )
          "
          icon="pi pi-plus"
          @click="openCreate"
        />
      </template>
    </BasePageHeader>

    <BaseToolbar
      v-model:search="
        searchInput
      "
      :show-create="false"
      :show-reset="true"
      :loading="
        loading ||
        lookupsLoading
      "
      :search-placeholder="
        t(
          'departments.searchPlaceholder',
        )
      "
      @refresh="refresh"
      @reset="
        resetFilters
      "
    >
      <template #center>
        <Select
          v-model="
            selectedUniversity
          "
          :options="
            universityOptions
          "
          option-label="
            display_name
          "
          option-value="id"
          class="
            department-filter
          "
          :placeholder="
            t(
              'departments.allUniversities',
            )
          "
          :loading="
            lookupsLoading
          "
          filter
          @change="
            applyUniversityFilter
          "
        />

        <Select
          v-model="
            selectedFaculty
          "
          :options="
            facultyOptions
          "
          option-label="
            display_name
          "
          option-value="id"
          class="
            department-filter
          "
          :placeholder="
            t(
              'departments.allFaculties',
            )
          "
          :loading="
            lookupsLoading
          "
          filter
          @change="
            applyFacultyFilter
          "
        />

        <Select
          v-model="
            selectedActive
          "
          :options="
            statusOptions
          "
          option-label="label"
          option-value="value"
          class="
            department-filter
            department-filter--status
          "
          @change="
            applyActiveFilter
          "
        />
      </template>
    </BaseToolbar>

    <BaseCard
      :padding="false"
    >
      <BaseDataTable
        :value="items"
        :columns="columns"
        :loading="loading"
        :error="error"
        :first="first"
        :rows="
          query.pageSize
        "
        :total-records="
          totalRecords
        "
        show-row-actions
        @page="
          handlePage
        "
        @sort="
          handleSort
        "
        @retry="refresh"
        @row-click="
          openView
        "
      >
        <template
          #status="{ row }"
        >
          <Tag
            :value="
              row.is_active
                ? t(
                    'departments.active',
                  )
                : t(
                    'departments.inactive',
                  )
            "
            :severity="
              row.is_active
                ? 'success'
                : 'secondary'
            "
          />
        </template>

        <template
          #actions="{ row }"
        >
          <Button
            v-tooltip.bottom="
              t('common.view')
            "
            icon="pi pi-eye"
            severity="secondary"
            text
            rounded
            @click.stop="
              openView(row)
            "
          />

          <Button
            v-if="canEdit"
            v-tooltip.bottom="
              t('common.edit')
            "
            icon="pi pi-pencil"
            text
            rounded
            @click.stop="
              openEdit(row)
            "
          />

          <Button
            v-if="canDelete"
            v-tooltip.bottom="
              t(
                'departments.archive',
              )
            "
            icon="pi pi-box"
            severity="danger"
            text
            rounded
            @click.stop="
              archiveDepartment(
                row,
              )
            "
          />
        </template>

        <template
          #emptyActions
        >
          <Button
            v-if="canCreate"
            :label="
              t(
                'departments.create',
              )
            "
            icon="pi pi-plus"
            @click="openCreate"
          />
        </template>
      </BaseDataTable>
    </BaseCard>

    <DepartmentFormDialog
      v-model="formVisible"
      :department="
        selectedDepartment
      "
      :faculties="
        faculties
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
      @submit="
        saveDepartment
      "
    />

    <DepartmentDetailsDialog
      v-model="
        detailsVisible
      "
      :department="
        selectedDepartment
      "
    />
  </div>
</template>

<style scoped>
.departments-page {
  display: grid;
  gap: 1rem;
}

.department-filter {
  width: 13rem;
}

.department-filter--status {
  width: 10rem;
}

@media (max-width: 991px) {
  .department-filter,
  .department-filter--status {
    width: 100%;
  }
}
</style>
