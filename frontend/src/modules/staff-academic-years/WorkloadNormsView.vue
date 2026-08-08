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

import BaseCard from '@/components/base/BaseCard.vue'
import BaseDataTable from '@/components/base/BaseDataTable.vue'
import BasePageHeader from '@/components/base/BasePageHeader.vue'
import BaseToolbar from '@/components/base/BaseToolbar.vue'

import WorkloadNormFormDialog from '@/modules/staff-academic-years/components/WorkloadNormFormDialog.vue'

import {
  getAcademicYears,
  workloadNormsApi,
} from '@/modules/staff-academic-years/api'

import type {
  AcademicYearOption,
  WorkloadNorm,
  WorkloadNormPayload,
} from '@/modules/staff-academic-years/types'

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

const toast =
  useAppToast()

const {
  confirmDelete,
} = useAppConfirm()

const {
  can,
} = usePermissions()

const academicYears =
  ref<AcademicYearOption[]>([])

const selectedNorm =
  ref<WorkloadNorm | null>(null)

const selectedAcademicYear =
  ref<number | null>(null)

const selectedActive =
  ref<boolean | null>(null)

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

const canCreate = computed(
  () =>
    can(
      'staff.add_workloadnorm',
    ),
)

const canEdit = computed(
  () =>
    can(
      'staff.change_workloadnorm',
    ),
)

const canDelete = computed(
  () =>
    can(
      'staff.delete_workloadnorm',
    ),
)

const yearOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'workloadNorms.allYears',
        ),
    },

    ...academicYears.value.map(
      (year) => ({
        value: year.id,
        label: year.name,
      }),
    ),
  ])

const statusOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'workloadNorms.allStatuses',
        ),
    },

    {
      value: true,

      label:
        t(
          'workloadNorms.active',
        ),
    },

    {
      value: false,

      label:
        t(
          'workloadNorms.inactive',
        ),
    },
  ])

const columns =
  computed<
    CrudColumn<WorkloadNorm>[]
  >(() => [
    {
      field:
        'academic_year_name',

      header:
        t(
          'workloadNorms.fields.academicYear',
        ),

      sortable: true,

      sortField:
        'academic_year__start_year',

      minWidth: '10rem',
    },

    {
      field: 'rate',

      header:
        t(
          'workloadNorms.fields.rate',
        ),

      sortable: true,

      width: '8rem',
    },

    {
      field:
        'has_academic_degree',

      header:
        t(
          'workloadNorms.fields.hasDegree',
        ),

      bodySlot: 'degree',

      width: '11rem',
    },

    {
      field:
        'has_academic_title',

      header:
        t(
          'workloadNorms.fields.hasTitle',
        ),

      bodySlot: 'title',

      width: '11rem',
    },

    {
      field:
        'annual_hours',

      header:
        t(
          'workloadNorms.fields.annualHours',
        ),

      sortable: true,

      width: '11rem',
    },

    {
      field:
        'is_active',

      header:
        t(
          'workloadNorms.fields.status',
        ),

      bodySlot: 'status',

      width: '8rem',
    },
  ])

const {
  items,
  totalRecords,
  loading,
  error,

  query,
  first,

  load,
  refresh,
  reset,

  handlePage,
  handleSort,

  setFilter,
  clearFilters,
} = useCrudList<WorkloadNorm>(
  (params) =>
    workloadNormsApi.list(
      params,
    ),

  {
    initialPageSize: 20,

    initialOrdering:
      '-academic_year__start_year,-rate',
  },
)

function clearFormErrors(): void {
  fieldErrors.value = {}

  nonFieldErrors.value = []

  generalFormError.value = ''
}

async function loadYears(): Promise<void> {
  try {
    const response =
      await getAcademicYears()

    academicYears.value =
      response.results
  } catch (lookupError) {
    const normalized =
      normalizeApiError(
        lookupError,
      )

    toast.error(
      t('common.error'),
      normalized.message,
    )
  }
}

function openCreate(): void {
  selectedNorm.value = null

  clearFormErrors()

  formVisible.value = true
}

function openEdit(
  norm: WorkloadNorm,
): void {
  selectedNorm.value = norm

  clearFormErrors()

  formVisible.value = true
}

async function saveNorm(
  payload: WorkloadNormPayload,
): Promise<void> {
  saving.value = true

  clearFormErrors()

  try {
    if (selectedNorm.value) {
      await workloadNormsApi.update(
        selectedNorm.value.id,
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.updated'),
      )
    } else {
      await workloadNormsApi.create(
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.created'),
      )
    }

    formVisible.value = false

    selectedNorm.value = null

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

function archiveNorm(
  norm: WorkloadNorm,
): void {
  confirmDelete({
    header:
      t(
        'workloadNorms.archiveTitle',
      ),

    message:
      t(
        'workloadNorms.archiveConfirm',
        {
          year:
            norm.academic_year_name,

          rate:
            norm.rate,
        },
      ),

    accept: async () => {
      try {
        await workloadNormsApi.remove(
          norm.id,
        )

        toast.success(
          t('common.success'),

          t(
            'workloadNorms.archived',
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

async function applyYearFilter(): Promise<void> {
  setFilter(
    'academic_year',
    selectedAcademicYear.value,
  )

  await load()
}

async function applyStatusFilter(): Promise<void> {
  setFilter(
    'is_active',
    selectedActive.value,
  )

  await load()
}

async function resetFilters(): Promise<void> {
  selectedAcademicYear.value =
    null

  selectedActive.value =
    null

  clearFilters()

  await reset()
}

onMounted(async () => {
  await Promise.all([
    load(),
    loadYears(),
  ])
})
</script>

<template>
  <div
    class="
      workload-norms-page
    "
  >
    <BasePageHeader
      :title="
        t(
          'workloadNorms.title',
        )
      "
      :description="
        t(
          'workloadNorms.description',
        )
      "
      icon="pi pi-chart-bar"
    >
      <template #actions>
        <Button
          v-if="canCreate"
          :label="
            t(
              'workloadNorms.create',
            )
          "
          icon="pi pi-plus"
          @click="openCreate"
        />
      </template>
    </BasePageHeader>

    <BaseToolbar
      :show-search="false"
      :show-create="false"
      :show-reset="true"
      :loading="loading"
      @refresh="refresh"
      @reset="
        resetFilters
      "
    >
      <template #center>
        <Select
          v-model="
            selectedAcademicYear
          "
          :options="
            yearOptions
          "
          option-label="label"
          option-value="value"
          class="norm-filter"
          @change="
            applyYearFilter
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
          class="norm-filter"
          @change="
            applyStatusFilter
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
      >
        <template
          #degree="{ row }"
        >
          <Tag
            :value="
              row.has_academic_degree
                ? t('common.yes')
                : t('common.no')
            "
            :severity="
              row.has_academic_degree
                ? 'success'
                : 'secondary'
            "
          />
        </template>

        <template
          #title="{ row }"
        >
          <Tag
            :value="
              row.has_academic_title
                ? t('common.yes')
                : t('common.no')
            "
            :severity="
              row.has_academic_title
                ? 'success'
                : 'secondary'
            "
          />
        </template>

        <template
          #status="{ row }"
        >
          <Tag
            :value="
              row.is_active
                ? t(
                    'workloadNorms.active',
                  )
                : t(
                    'workloadNorms.inactive',
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
                'workloadNorms.archive',
              )
            "
            icon="pi pi-box"
            severity="danger"
            text
            rounded
            @click.stop="
              archiveNorm(row)
            "
          />
        </template>
      </BaseDataTable>
    </BaseCard>

    <WorkloadNormFormDialog
      v-model="formVisible"
      :norm="selectedNorm"
      :academic-years="
        academicYears
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
      @submit="saveNorm"
    />
  </div>
</template>

<style scoped>
.workload-norms-page {
  display: grid;
  gap: 1rem;
}

.norm-filter {
  width: 14rem;
}

@media (max-width: 767px) {
  .norm-filter {
    width: 100%;
  }
}
</style>
