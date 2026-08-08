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

import BulkStaffAcademicYearDialog from '@/modules/staff-academic-years/components/BulkStaffAcademicYearDialog.vue'
import StaffAcademicYearFormDialog from '@/modules/staff-academic-years/components/StaffAcademicYearFormDialog.vue'

import {
  createMissingStaffRecords,
  getAcademicDegrees,
  getAcademicTitles,
  getAcademicYears,
  getDepartments,
  getEmployments,
  staffAcademicYearsApi,
} from '@/modules/staff-academic-years/api'

import type {
  AcademicDegreeLookup,
  AcademicTitleLookup,
  AcademicYearOption,
  BulkCreatePayload,
  DepartmentLookup,
  EmploymentLookup,
  StaffAcademicYearPayload,
  StaffAcademicYearRecord,
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

const selectedRecord =
  ref<StaffAcademicYearRecord | null>(
    null,
  )

const formVisible =
  ref(false)

const bulkVisible =
  ref(false)

const saving =
  ref(false)

const bulkLoading =
  ref(false)

const lookupsLoading =
  ref(false)

const academicYears =
  ref<AcademicYearOption[]>([])

const employments =
  ref<EmploymentLookup[]>([])

const departments =
  ref<DepartmentLookup[]>([])

const academicDegrees =
  ref<AcademicDegreeLookup[]>([])

const academicTitles =
  ref<AcademicTitleLookup[]>([])

const selectedAcademicYear =
  ref<number | null>(null)

const selectedDepartment =
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
      'staff.add_staffemploymentacademicyear',
    ),
)

const canEdit = computed(
  () =>
    can(
      'staff.change_staffemploymentacademicyear',
    ),
)

const canDelete = computed(
  () =>
    can(
      'staff.delete_staffemploymentacademicyear',
    ),
)

const academicYearOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'staffAcademicYears.allYears',
        ),
    },

    ...academicYears.value.map(
      (year) => ({
        value: year.id,
        label: year.name,
      }),
    ),
  ])

const departmentOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'staffAcademicYears.allDepartments',
        ),
    },

    ...departments.value.map(
      (item) => ({
        value: item.id,
        label:
          item.display_name ||
          item.name_ru,
      }),
    ),
  ])

const statusOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'staffAcademicYears.allStatuses',
        ),
    },

    {
      value: true,

      label:
        t(
          'staffAcademicYears.active',
        ),
    },

    {
      value: false,

      label:
        t(
          'staffAcademicYears.inactive',
        ),
    },
  ])

const columns =
  computed<
    CrudColumn<StaffAcademicYearRecord>[]
  >(() => [
    {
      field:
        'academic_year_name',

      header:
        t(
          'staffAcademicYears.fields.academicYear',
        ),

      sortable: true,

      sortField:
        'academic_year__start_year',

      minWidth: '9rem',
    },

    {
      field:
        'staff_member_name',

      header:
        t(
          'staffAcademicYears.fields.staffMember',
        ),

      sortable: true,

      sortField:
        'staff_employment__staff_member__last_name',

      minWidth: '17rem',
    },

    {
      field:
        'department_name',

      header:
        t(
          'staffAcademicYears.fields.department',
        ),

      minWidth: '13rem',
    },

    {
      field:
        'position_name',

      header:
        t(
          'staffAcademicYears.fields.position',
        ),

      minWidth: '11rem',
    },

    {
      field: 'rate',

      header:
        t(
          'staffAcademicYears.fields.rate',
        ),

      sortable: true,

      width: '7rem',
    },

    {
      field:
        'academic_degree_name',

      header:
        t(
          'staffAcademicYears.fields.academicDegree',
        ),

      bodySlot: 'degree',

      minWidth: '11rem',
    },

    {
      field:
        'academic_title_name',

      header:
        t(
          'staffAcademicYears.fields.academicTitle',
        ),

      bodySlot: 'title',

      minWidth: '11rem',
    },

    {
      field:
        'recommended_annual_hours',

      header:
        t(
          'staffAcademicYears.fields.recommendedHours',
        ),

      bodySlot:
        'recommendedHours',

      width: '10rem',

      align: 'center',
    },

    {
      field:
        'is_active',

      header:
        t(
          'staffAcademicYears.fields.status',
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
  searchInput,
  first,

  load,
  refresh,
  reset,

  handlePage,
  handleSort,

  setFilter,
  clearFilters,
} =
  useCrudList<
    StaffAcademicYearRecord
  >(
    (params) =>
      staffAcademicYearsApi.list(
        params,
      ),

    {
      initialPageSize: 20,

      initialOrdering:
        '-academic_year__start_year,staff_employment__staff_member__last_name',
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
      years,
      employmentResponse,
      departmentResponse,
      degreeResponse,
      titleResponse,
    ] = await Promise.all([
      getAcademicYears(),
      getEmployments(),
      getDepartments(),
      getAcademicDegrees(),
      getAcademicTitles(),
    ])

    academicYears.value =
      years.results

    employments.value =
      employmentResponse.results

    departments.value =
      departmentResponse.results

    academicDegrees.value =
      degreeResponse.results

    academicTitles.value =
      titleResponse.results
  } catch (lookupError) {
    const normalized =
      normalizeApiError(
        lookupError,
        t('crud.loadError'),
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
  selectedRecord.value = null
  clearFormErrors()

  formVisible.value = true
}

function openEdit(
  record: StaffAcademicYearRecord,
): void {
  selectedRecord.value =
    record

  clearFormErrors()

  formVisible.value = true
}

async function saveRecord(
  payload: StaffAcademicYearPayload,
): Promise<void> {
  saving.value = true

  clearFormErrors()

  try {
    if (selectedRecord.value) {
      await staffAcademicYearsApi.update(
        selectedRecord.value.id,
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.updated'),
      )
    } else {
      await staffAcademicYearsApi.create(
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.created'),
      )
    }

    formVisible.value = false

    selectedRecord.value = null

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

function archiveRecord(
  record: StaffAcademicYearRecord,
): void {
  confirmDelete({
    header:
      t(
        'staffAcademicYears.archiveTitle',
      ),

    message:
      t(
        'staffAcademicYears.archiveConfirm',
        {
          name:
            record.staff_member_name,

          year:
            record.academic_year_name,
        },
      ),

    accept: async () => {
      try {
        await staffAcademicYearsApi.remove(
          record.id,
        )

        toast.success(
          t('common.success'),
          t(
            'staffAcademicYears.archived',
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

async function runBulkCreate(
  payload: BulkCreatePayload,
): Promise<void> {
  bulkLoading.value = true

  try {
    const result =
      await createMissingStaffRecords(
        payload,
      )

    bulkVisible.value = false

    toast.success(
      t(
        'staffAcademicYears.bulkCompleted',
      ),

      t(
        'staffAcademicYears.bulkResult',
        {
          created:
            result.created,

          restored:
            result.restored,

          skipped:
            result.skipped,

          missing:
            result.missing,
        },
      ),
    )

    await refresh()
  } catch (bulkError) {
    const normalized =
      normalizeApiError(
        bulkError,
      )

    toast.error(
      t('common.error'),
      normalized.message,
    )
  } finally {
    bulkLoading.value = false
  }
}

async function applyYearFilter(): Promise<void> {
  setFilter(
    'academic_year',
    selectedAcademicYear.value,
  )

  await load()
}

async function applyDepartmentFilter(): Promise<void> {
  setFilter(
    'department',
    selectedDepartment.value,
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

  selectedDepartment.value =
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
    class="
      staff-academic-years-page
    "
  >
    <BasePageHeader
      :title="
        t(
          'staffAcademicYears.title',
        )
      "
      :description="
        t(
          'staffAcademicYears.description',
        )
      "
      icon="pi pi-calendar-clock"
    >
      <template #actions>
        <Button
          v-if="canCreate"
          :label="
            t(
              'staffAcademicYears.bulkCreate',
            )
          "
          icon="pi pi-bolt"
          severity="secondary"
          outlined
          @click="
            bulkVisible = true
          "
        />

        <Button
          v-if="canCreate"
          :label="
            t(
              'staffAcademicYears.create',
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
          'staffAcademicYears.searchPlaceholder',
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
            selectedAcademicYear
          "
          :options="
            academicYearOptions
          "
          option-label="label"
          option-value="value"
          class="record-filter"
          @change="
            applyYearFilter
          "
        />

        <Select
          v-model="
            selectedDepartment
          "
          :options="
            departmentOptions
          "
          option-label="label"
          option-value="value"
          filter
          class="record-filter"
          @change="
            applyDepartmentFilter
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
          class="record-filter"
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
          {{
            row.academic_degree_name ||
            '—'
          }}
        </template>

        <template
          #title="{ row }"
        >
          {{
            row.academic_title_name ||
            '—'
          }}
        </template>

        <template
          #recommendedHours="{ row }"
        >
          <Tag
            v-if="
              row.recommended_annual_hours
            "
            :value="
              `${row.recommended_annual_hours} ч.`
            "
            severity="info"
          />

          <span v-else>—</span>
        </template>

        <template
          #status="{ row }"
        >
          <Tag
            :value="
              row.is_active
                ? t(
                    'staffAcademicYears.active',
                  )
                : t(
                    'staffAcademicYears.inactive',
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
                'staffAcademicYears.archive',
              )
            "
            icon="pi pi-box"
            severity="danger"
            text
            rounded
            @click.stop="
              archiveRecord(row)
            "
          />
        </template>
      </BaseDataTable>
    </BaseCard>

    <StaffAcademicYearFormDialog
      v-model="formVisible"
      :record="
        selectedRecord
      "
      :academic-years="
        academicYears
      "
      :employments="
        employments
      "
      :academic-degrees="
        academicDegrees
      "
      :academic-titles="
        academicTitles
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
      @submit="saveRecord"
    />

    <BulkStaffAcademicYearDialog
      v-model="bulkVisible"
      :academic-years="
        academicYears
      "
      :departments="
        departments
      "
      :loading="
        bulkLoading
      "
      @submit="
        runBulkCreate
      "
    />
  </div>
</template>

<style scoped>
.staff-academic-years-page {
  display: grid;
  gap: 1rem;
}

.record-filter {
  width: 14rem;
}

@media (max-width: 991px) {
  .record-filter {
    width: 100%;
  }
}
</style>
