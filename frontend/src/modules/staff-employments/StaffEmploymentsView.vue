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

import StaffEmploymentDetailsDialog from '@/modules/staff-employments/components/StaffEmploymentDetailsDialog.vue'
import StaffEmploymentFormDialog from '@/modules/staff-employments/components/StaffEmploymentFormDialog.vue'

import {
  getDepartmentsLookup,
  getPositionsLookup,
  getStaffMembersLookup,
  staffEmploymentsApi,
} from '@/modules/staff-employments/api'

import type {
  DepartmentLookup,
  EmploymentType,
  SelectOption,
  StaffEmployment,
  StaffEmploymentPayload,
  StaffMemberLookup,
  StaffPositionLookup,
} from '@/modules/staff-employments/types'

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

import {
  useLocaleStore,
} from '@/stores/locale'

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

const toast =
  useAppToast()

const {
  confirmDelete,
} = useAppConfirm()

const {
  can,
} = usePermissions()

const selectedEmployment =
  ref<StaffEmployment | null>(
    null,
  )

const formVisible =
  ref(false)

const detailsVisible =
  ref(false)

const saving =
  ref(false)

const lookupsLoading =
  ref(false)

const staffMembers =
  ref<StaffMemberLookup[]>([])

const departments =
  ref<DepartmentLookup[]>([])

const positions =
  ref<StaffPositionLookup[]>([])

const selectedDepartment =
  ref<number | null>(null)

const selectedPosition =
  ref<number | null>(null)

const selectedType =
  ref<EmploymentType | null>(
    null,
  )

const selectedActive =
  ref<boolean | null>(null)

const selectedPrimary =
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
      'staff.add_staffemployment',
    ),
)

const canEdit = computed(
  () =>
    can(
      'staff.change_staffemployment',
    ),
)

const canDelete = computed(
  () =>
    can(
      'staff.delete_staffemployment',
    ),
)

function localizedName(
  ru: string | null | undefined,
  uz: string | null | undefined,
): string {
  if (localeStore.locale === 'uz') {
    return (
      uz?.trim() ||
      ru?.trim() ||
      '—'
    )
  }

  return (
    ru?.trim() ||
    uz?.trim() ||
    '—'
  )
}

function employmentTypeLabel(
  value: EmploymentType,
): string {
  const keys:
    Record<
      EmploymentType,
      string
    > = {
      primary:
        'staffEmployments.types.primary',

      internal_part_time:
        'staffEmployments.types.internalPartTime',

      external_part_time:
        'staffEmployments.types.externalPartTime',

      hourly:
        'staffEmployments.types.hourly',
    }

  return t(keys[value])
}

const departmentFilterOptions =
  computed<SelectOption<
    number | null
  >[]>(() => [
    {
      value: null,

      label:
        t(
          'staffEmployments.allDepartments',
        ),
    },

    ...departments.value.map(
      (department) => ({
        value:
          department.id,

        label:
          localizedName(
            department.name_ru,
            department.name_uz,
          ),
      }),
    ),
  ])

const positionFilterOptions =
  computed<SelectOption<
    number | null
  >[]>(() => [
    {
      value: null,

      label:
        t(
          'staffEmployments.allPositions',
        ),
    },

    ...positions.value.map(
      (position) => ({
        value:
          position.id,

        label:
          localizedName(
            position.name_ru,
            position.name_uz,
          ),
      }),
    ),
  ])

const typeFilterOptions =
  computed<SelectOption<
    EmploymentType | null
  >[]>(() => [
    {
      value: null,

      label:
        t(
          'staffEmployments.allTypes',
        ),
    },

    {
      value: 'primary',

      label:
        t(
          'staffEmployments.types.primary',
        ),
    },

    {
      value:
        'internal_part_time',

      label:
        t(
          'staffEmployments.types.internalPartTime',
        ),
    },

    {
      value:
        'external_part_time',

      label:
        t(
          'staffEmployments.types.externalPartTime',
        ),
    },

    {
      value: 'hourly',

      label:
        t(
          'staffEmployments.types.hourly',
        ),
    },
  ])

const statusOptions =
  computed(() => [
    {
      label:
        t(
          'staffEmployments.allStatuses',
        ),
      value: null,
    },

    {
      label:
        t(
          'staffEmployments.active',
        ),
      value: true,
    },

    {
      label:
        t(
          'staffEmployments.inactive',
        ),
      value: false,
    },
  ])

const primaryOptions =
  computed(() => [
    {
      label:
        t(
          'staffEmployments.allAssignments',
        ),
      value: null,
    },

    {
      label:
        t(
          'staffEmployments.primaryOnly',
        ),
      value: true,
    },

    {
      label:
        t(
          'staffEmployments.additionalOnly',
        ),
      value: false,
    },
  ])

const columns =
  computed<
    CrudColumn<StaffEmployment>[]
  >(() => [
    {
      field:
        'staff_member_name',

      header:
        t(
          'staffEmployments.fields.staffMember',
        ),

      sortable: true,

      sortField:
        'staff_member__last_name',

      minWidth:
        '17rem',
    },

    {
      field:
        'department_name',

      header:
        t(
          'staffEmployments.fields.department',
        ),

      minWidth:
        '14rem',
    },

    {
      field:
        'position_name',

      header:
        t(
          'staffEmployments.fields.position',
        ),

      minWidth:
        '12rem',
    },

    {
      field:
        'employment_type',

      header:
        t(
          'staffEmployments.fields.employmentType',
        ),

      bodySlot: 'type',

      minWidth:
        '13rem',
    },

    {
      field: 'rate',

      header:
        t(
          'staffEmployments.fields.rate',
        ),

      sortable: true,

      width: '7rem',

      align: 'center',
    },

    {
      field:
        'start_date',

      header:
        t(
          'staffEmployments.fields.startDate',
        ),

      sortable: true,

      bodySlot: 'startDate',

      minWidth:
        '9rem',
    },

    {
      field:
        'is_primary',

      header:
        t(
          'staffEmployments.fields.primary',
        ),

      bodySlot: 'primary',

      width: '8rem',

      align: 'center',
    },

    {
      field:
        'is_active',

      header:
        t(
          'staffEmployments.fields.status',
        ),

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
} = useCrudList<StaffEmployment>(
  (params) =>
    staffEmploymentsApi.list(
      params,
    ),

  {
    initialPageSize: 20,

    initialOrdering:
      'staff_member__last_name,-is_primary,-start_date',
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
      staffResponse,
      departmentsResponse,
      positionsResponse,
    ] = await Promise.all([
      getStaffMembersLookup(),
      getDepartmentsLookup(),
      getPositionsLookup(),
    ])

    staffMembers.value =
      staffResponse.results

    departments.value =
      departmentsResponse.results

    positions.value =
      positionsResponse.results
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
  selectedEmployment.value =
    null

  clearFormErrors()

  formVisible.value = true
}

function openView(
  employment: StaffEmployment,
): void {
  selectedEmployment.value =
    employment

  detailsVisible.value = true
}

function openEdit(
  employment: StaffEmployment,
): void {
  selectedEmployment.value =
    employment

  clearFormErrors()

  formVisible.value = true
}

async function saveEmployment(
  payload: StaffEmploymentPayload,
): Promise<void> {
  saving.value = true

  clearFormErrors()

  try {
    if (
      selectedEmployment.value
    ) {
      await staffEmploymentsApi.update(
        selectedEmployment.value.id,
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.updated'),
      )
    } else {
      await staffEmploymentsApi.create(
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.created'),
      )
    }

    formVisible.value = false

    selectedEmployment.value =
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

function archiveEmployment(
  employment: StaffEmployment,
): void {
  confirmDelete({
    header:
      t(
        'staffEmployments.archiveTitle',
      ),

    message:
      t(
        'staffEmployments.archiveConfirm',
        {
          name:
            employment.staff_member_name,
        },
      ),

    accept: async () => {
      try {
        await staffEmploymentsApi.remove(
          employment.id,
        )

        toast.success(
          t('common.success'),

          t(
            'staffEmployments.archived',
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

async function applyDepartmentFilter(): Promise<void> {
  setFilter(
    'department',
    selectedDepartment.value,
  )

  await load()
}

async function applyPositionFilter(): Promise<void> {
  setFilter(
    'position',
    selectedPosition.value,
  )

  await load()
}

async function applyTypeFilter(): Promise<void> {
  setFilter(
    'employment_type',
    selectedType.value,
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

async function applyPrimaryFilter(): Promise<void> {
  setFilter(
    'is_primary',
    selectedPrimary.value,
  )

  await load()
}

async function resetFilters(): Promise<void> {
  selectedDepartment.value =
    null

  selectedPosition.value =
    null

  selectedType.value =
    null

  selectedActive.value =
    null

  selectedPrimary.value =
    null

  clearFilters()

  await reset()
}

function formatDate(
  value: string,
): string {
  return new Intl.DateTimeFormat(
    undefined,
    {
      dateStyle: 'medium',
    },
  ).format(
    new Date(
      `${value}T00:00:00`,
    ),
  )
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
      staff-employments-page
    "
  >
    <BasePageHeader
      :title="
        t(
          'staffEmployments.title',
        )
      "
      :description="
        t(
          'staffEmployments.description',
        )
      "
      icon="pi pi-briefcase"
    >
      <template #actions>
        <Button
          v-if="canCreate"
          :label="
            t(
              'staffEmployments.create',
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
          'staffEmployments.searchPlaceholder',
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
            selectedDepartment
          "
          :options="
            departmentFilterOptions
          "
          option-label="label"
          option-value="value"
          class="
            employment-filter
          "
          filter
          @change="
            applyDepartmentFilter
          "
        />

        <Select
          v-model="
            selectedPosition
          "
          :options="
            positionFilterOptions
          "
          option-label="label"
          option-value="value"
          class="
            employment-filter
          "
          filter
          @change="
            applyPositionFilter
          "
        />

        <Select
          v-model="
            selectedType
          "
          :options="
            typeFilterOptions
          "
          option-label="label"
          option-value="value"
          class="
            employment-filter
          "
          @change="
            applyTypeFilter
          "
        />

        <Select
          v-model="
            selectedPrimary
          "
          :options="
            primaryOptions
          "
          option-label="label"
          option-value="value"
          class="
            employment-filter
          "
          @change="
            applyPrimaryFilter
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
            employment-filter
          "
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
        @row-click="
          openView
        "
      >
        <template
          #type="{ row }"
        >
          {{
            employmentTypeLabel(
              row.employment_type,
            )
          }}
        </template>

        <template
          #startDate="{ row }"
        >
          {{
            formatDate(
              row.start_date,
            )
          }}
        </template>

        <template
          #primary="{ row }"
        >
          <Tag
            :value="
              row.is_primary
                ? t('common.yes')
                : t('common.no')
            "
            :severity="
              row.is_primary
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
                    'staffEmployments.active',
                  )
                : t(
                    'staffEmployments.inactive',
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
                'staffEmployments.archive',
              )
            "
            icon="pi pi-box"
            severity="danger"
            text
            rounded
            @click.stop="
              archiveEmployment(
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
                'staffEmployments.create',
              )
            "
            icon="pi pi-plus"
            @click="openCreate"
          />
        </template>
      </BaseDataTable>
    </BaseCard>

    <StaffEmploymentFormDialog
      v-model="formVisible"
      :employment="
        selectedEmployment
      "
      :staff-members="
        staffMembers
      "
      :departments="
        departments
      "
      :positions="
        positions
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
        saveEmployment
      "
    />

    <StaffEmploymentDetailsDialog
      v-model="
        detailsVisible
      "
      :employment="
        selectedEmployment
      "
    />
  </div>
</template>

<style scoped>
.staff-employments-page {
  display: grid;
  gap: 1rem;
}

.employment-filter {
  width: 13rem;
}

@media (max-width: 1199px) {
  .employment-filter {
    width: 100%;
  }
}
</style>
