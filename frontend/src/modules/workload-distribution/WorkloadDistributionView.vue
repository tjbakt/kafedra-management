<script setup lang="ts">
import Button from 'primevue/button'
import Select from 'primevue/select'
import Tag from 'primevue/tag'

import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  useI18n,
} from 'vue-i18n'

import BaseCard from '@/components/base/BaseCard.vue'
import BaseDataTable from '@/components/base/BaseDataTable.vue'
import BasePageHeader from '@/components/base/BasePageHeader.vue'
import BaseToolbar from '@/components/base/BaseToolbar.vue'

import WorkloadDistributionFormDialog
  from '@/modules/workload-distribution/components/WorkloadDistributionFormDialog.vue'

import WorkloadDistributionReasonDialog
  from '@/modules/workload-distribution/components/WorkloadDistributionReasonDialog.vue'

import PlannedWorkloadDistributionTable
  from '@/modules/workload-distribution/components/PlannedWorkloadDistributionTable.vue'

import {
  approveDistribution,
  approveSelectedDistributions,
  cancelDistribution,
  cancelSelectedDistributions,
  getPlannedWorkloads,
  getStaffAcademicYearRecords,
  getStaffEmployments,
  restoreSelectedDistributions,
  returnDistributionToDraft,
  returnSelectedDistributionsToDraft,
  assignSelectedPlannedWorkloads,
  getTeacherWorkloadSummary,
  workloadDistributionsApi,
} from '@/modules/workload-distribution/api'

import type {
  StaffEmployment,
} from '@/modules/staff-employments/types'

import type {
  StaffAcademicYearRecord,
} from '@/modules/staff-academic-years/types'

import type {
  PlannedWorkload,
} from '@/modules/teaching-workload/types'

import type {
  WorkloadDistribution,
  WorkloadDistributionCreatePayload,
  WorkloadDistributionStatus,
  WorkloadDistributionUpdatePayload,
  BulkAssignPlannedWorkloadPayload,
} from '@/modules/workload-distribution/types'

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

import WorkloadBulkAssignDialog
  from '@/modules/workload-distribution/components/WorkloadBulkAssignDialog.vue'
import TeacherWorkloadSummaryTable
  from '@/modules/workload-distribution/components/TeacherWorkloadSummaryTable.vue'


const { t } =
  useI18n()

const toast =
  useAppToast()

const {
  confirmDelete,
} = useAppConfirm()

const {
  can,
} = usePermissions()

const teacherSummaries =
  ref<TeacherWorkloadSummary[]>([])

const teacherSummaryLoading =
  ref(false)

const plannedWorkloads =
  ref<PlannedWorkload[]>([])

const employments =
  ref<StaffEmployment[]>([])

const annualRecords =
  ref<StaffAcademicYearRecord[]>([])

const lookupLoading =
  ref(false)

const selectedRecord =
  ref<WorkloadDistribution | null>(
    null,
  )

const initialPlannedWorkloadId =
  ref<number | null>(
    null,
  )

const formVisible =
  ref(false)

const reasonVisible =
  ref(false)

const reasonAction =
  ref<
    'cancel' |
    'return-to-draft' |
    null
  >(null)

const saving =
  ref(false)

const actionLoading =
  ref(false)

const selectedDistributions =
  ref<
    WorkloadDistribution[]
  >([])

const selectedPlannedWorkloads =
  ref<
    PlannedWorkload[]
  >([])

const bulkAssignVisible =
  ref(false)

const bulkAssignLoading =
  ref(false)

const selectedPlannedHours =
  computed(
    () =>
      selectedPlannedWorkloads
        .value
        .reduce(
          (
            total,
            item,
          ) =>
            total +
            Number(
              item.remaining_hours,
            ),
          0,
        ),
  )

const selectedPlannedCompatible =
  computed(
    () => {
      if (
        selectedPlannedWorkloads
          .value
          .length === 0
      ) {
        return false
      }

      const years =
        new Set(
          selectedPlannedWorkloads
            .value
            .map(
              (item) =>
                item.academic_year,
            ),
        )

      const departments =
        new Set(
          selectedPlannedWorkloads
            .value
            .map(
              (item) =>
                item.teaching_department,
            ),
        )

      return (
        years.size === 1 &&
        departments.size === 1
      )
    },
  )

const bulkLoading =
  ref(false)

const bulkReasonVisible =
  ref(false)

const bulkReasonAction =
  ref<
    | 'cancel'
    | 'restore'
    | 'return-to-draft'
    | null
  >(null)

const fieldErrors =
  ref<FieldErrors>({})

const nonFieldErrors =
  ref<string[]>([])

const generalError =
  ref('')

const selectedYear =
  ref<number | null>(null)

const selectedSemester =
  ref<number | null>(null)

const selectedDepartment =
  ref<number | null>(null)

const selectedStatus =
  ref<
    WorkloadDistributionStatus | null
  >(null)

const canCreate =
  computed(
    () =>
      can(
        'workload.add_workloaddistribution',
      ),
  )

const canEdit =
  computed(
    () =>
      can(
        'workload.change_workloaddistribution',
      ),
  )

const canDelete =
  computed(
    () =>
      can(
        'workload.delete_workloaddistribution',
      ),
  )

const selectedCount =
  computed(
    () =>
      selectedDistributions
        .value
        .length,
  )

const selectedDraftIds =
  computed(
    () =>
      selectedDistributions
        .value
        .filter(
          (item) =>
            item.status ===
            'draft',
        )
        .map(
          (item) =>
            item.id,
        ),
  )

const selectedApprovedIds =
  computed(
    () =>
      selectedDistributions
        .value
        .filter(
          (item) =>
            item.status ===
            'approved',
        )
        .map(
          (item) =>
            item.id,
        ),
  )

const selectedCancelledIds =
  computed(
    () =>
      selectedDistributions
        .value
        .filter(
          (item) =>
            item.status ===
            'cancelled',
        )
        .map(
          (item) =>
            item.id,
        ),
  )

const selectedActiveIds =
  computed(
    () =>
      selectedDistributions
        .value
        .filter(
          (item) =>
            item.status !==
            'cancelled',
        )
        .map(
          (item) =>
            item.id,
        ),
  )

const years =
  computed(() => {
    const map =
      new Map<
        number,
        string
      >()

    for (
      const workload of
      plannedWorkloads.value
    ) {
      map.set(
        workload.academic_year,
        workload.academic_year_name,
      )
    }

    return [
      {
        value: null,
        label:
          t(
            'workloadDistribution.filters.allYears',
          ),
      },

      ...Array.from(
        map.entries(),
      ).map(
        ([value, label]) => ({
          value,
          label,
        }),
      ),
    ]
  })

const semesters =
  computed(() => {
    const values =
      new Set<number>()

    for (
      const workload
      of plannedWorkloads.value
    ) {
      if (
        selectedYear.value !==
          null &&
        workload.academic_year !==
          selectedYear.value
      ) {
        continue
      }

      values.add(
        workload.semester_number,
      )
    }

    return [
      {
        value: null,

        label:
          t(
            'workloadDistribution.filters.allSemesters',
          ),
      },

      ...Array
        .from(values)
        .sort(
          (a, b) =>
            a - b,
        )
        .map(
          (value) => ({
            value,

            label:
              `${value} — ${
                value % 2 === 1
                  ? t(
                      'workloadDistribution.seasons.autumn',
                    )
                  : t(
                      'workloadDistribution.seasons.spring',
                    )
              }`,
          }),
        ),
    ]
  })

const departments =
  computed(() => {
    const map =
      new Map<
        number,
        string
      >()

    for (
      const workload of
      plannedWorkloads.value
    ) {
      map.set(
        workload.teaching_department,
        workload.department_name,
      )
    }

    return [
      {
        value: null,
        label:
          t(
            'workloadDistribution.filters.allDepartments',
          ),
      },

      ...Array.from(
        map.entries(),
      ).map(
        ([value, label]) => ({
          value,
          label,
        }),
      ),
    ]
  })

const statuses =
  computed(() => [
    {
      value: null,

      label:
        t(
          'workloadDistribution.filters.allStatuses',
        ),
    },

    {
      value: 'draft',

      label:
        t(
          'workloadDistribution.statuses.draft',
        ),
    },

    {
      value: 'approved',

      label:
        t(
          'workloadDistribution.statuses.approved',
        ),
    },

    {
      value: 'cancelled',

      label:
        t(
          'workloadDistribution.statuses.cancelled',
        ),
    },
  ])

const visiblePlannedWorkloads =
  computed(
    () =>
      plannedWorkloads.value
        .filter(
          (item) => {
            if (
              selectedYear.value !==
                null &&
              item.academic_year !==
                selectedYear.value
            ) {
              return false
            }

            if (
              selectedDepartment.value !==
                null &&
              item.teaching_department !==
                selectedDepartment.value
            ) {
              return false
            }

            if (
              selectedSemester.value !==
                null &&
              item.semester_number !==
                selectedSemester.value
            ) {
              return false
            }

            return true
          },
        ),
  )

const bulkReasonTitle =
  computed(
    () => {
      if (
        bulkReasonAction.value ===
        'cancel'
      ) {
        return t(
          'workloadDistribution.bulk.cancelTitle',
        )
      }

      if (
        bulkReasonAction.value ===
        'restore'
      ) {
        return t(
          'workloadDistribution.bulk.restoreTitle',
        )
      }

      return t(
        'workloadDistribution.bulk.returnTitle',
      )
    },
  )

function statusSeverity(
  status:
    WorkloadDistributionStatus,
):
  | 'success'
  | 'secondary'
  | 'danger' {
  if (
    status === 'approved'
  ) {
    return 'success'
  }

  if (
    status === 'cancelled'
  ) {
    return 'danger'
  }

  return 'secondary'
}

const columns =
  computed<CrudColumn<WorkloadDistribution>[]>(() => [
    {
      field: 'curriculum_code',
      header:
        t(
          'workloadDistribution.fields.curriculum',
        ),
      minWidth: '10rem',
    },

    {
      field: 'semester_number',
      header:
        t(
          'workloadDistribution.fields.semester',
        ),
      minWidth: '7rem',
      bodySlot: 'semester',
    },

    {
      field: 'student_group_code',
      header:
        t(
          'workloadDistribution.fields.scope',
        ),
      minWidth: '10rem',
      bodySlot: 'scope',
    },

    {
      field: 'discipline_name',
      header:
        t(
          'workloadDistribution.fields.discipline',
        ),
      minWidth: '16rem',
    },

    {
      field: 'workload_type_name',
      header:
        t(
          'workloadDistribution.fields.workloadType',
        ),
      minWidth: '11rem',
    },

    {
      field: 'department_name',
      header:
        t(
          'workloadDistribution.fields.department',
        ),
      minWidth: '13rem',
    },

    {
      field: 'teacher_name',
      header:
        t(
          'workloadDistribution.fields.teacher',
        ),
      sortable: true,
      sortField: 'staff_employment__staff_member__last_name',
      minWidth: '15rem',
      bodySlot: 'teacher',
    },

    {
      field: 'allocated_hours',
      header:
        t(
          'workloadDistribution.fields.allocatedHours',
        ),
      sortable: true,
      width: '9rem',
      align: 'center',
    },

    {
      field: 'status',
      header:
        t(
          'workloadDistribution.fields.status',
        ),
      bodySlot: 'status',
      width: '10rem',
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
    WorkloadDistribution
  >(
    (params) =>
      workloadDistributionsApi
        .list(params),

    {
      initialPageSize: 20,

      initialOrdering:
        '-planned_workload__academic_year__start_year,staff_employment__staff_member__last_name',
    },
  )

function clearErrors(): void {
  fieldErrors.value = {}

  nonFieldErrors.value = []

  generalError.value = ''
}

async function loadTeacherSummaries():
  Promise<void> {
  if (
    !selectedAcademicYear.value ||
    !selectedDepartment.value
  ) {
    teacherSummaries.value =
      []

    return
  }

  teacherSummaryLoading.value =
    true

  try {
    teacherSummaries.value =
      await getTeacherWorkloadSummary(
        selectedAcademicYear.value,
        selectedDepartment.value,
      )
  } finally {
    teacherSummaryLoading.value =
      false
  }
}

async function changeYear(): Promise<void> {
  selectedSemester.value = null

  await applyFilters()
}

async function loadLookups(): Promise<void> {
  lookupLoading.value = true

  try {
    const [
      workloadsResponse,
      employmentsResponse,
      annualResponse,
    ] = await Promise.all([
      getPlannedWorkloads(),
      getStaffEmployments(),
      getStaffAcademicYearRecords(),
    ])

    plannedWorkloads.value =
      workloadsResponse.results

    employments.value =
      employmentsResponse.results

    annualRecords.value =
      annualResponse.results
  } catch (loadError) {
    toast.error(
      t('common.error'),

      normalizeApiError(
        loadError,
        t('crud.loadError'),
      ).message,
    )
  } finally {
    lookupLoading.value =
      false
  }
}

function openCreate(): void {
  selectedRecord.value = null
  initialPlannedWorkloadId.value = null
  clearErrors()
  formVisible.value = true
}

function openAssign(workload: PlannedWorkload,): void {
  if (
    !canCreate.value
  ) {
    return
  }

  if (
    Number(
      workload.remaining_hours,
    ) <= 0
  ) {
    return
  }

  selectedRecord.value = null
  initialPlannedWorkloadId.value = workload.id
  clearErrors()
  formVisible.value = true
}

function openEdit(
  record:
  WorkloadDistribution,
): void {
  if (
    record.status !== 'draft'
  ) {
    return
  }

  selectedRecord.value = record
  initialPlannedWorkloadId.value = null
  clearErrors()

  formVisible.value = true
}

async function createDistribution(
  payload:
    WorkloadDistributionCreatePayload,
): Promise<void> {
  saving.value = true

  clearErrors()

  try {
    await workloadDistributionsApi
      .create(payload)

    formVisible.value = false
    initialPlannedWorkloadId.value = null

    toast.success(
      t('common.success'),
      t('crud.created'),
    )

    await Promise.all([
      refresh(),
      loadLookups(),
      loadTeacherSummaries(),
    ])
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

    generalError.value =
      normalized.message
  } finally {
    saving.value = false
  }
}

async function updateDistribution(
  payload:
    WorkloadDistributionUpdatePayload,
): Promise<void> {
  if (!selectedRecord.value) {
    return
  }

  saving.value = true

  clearErrors()

  try {
    await workloadDistributionsApi
      .update(
        selectedRecord.value.id,
        payload,
      )

    formVisible.value =
      false

    selectedRecord.value =
      null

    toast.success(
      t('common.success'),
      t('crud.updated'),
    )

    await Promise.all([
      refresh(),
      loadLookups(),
      loadTeacherSummaries(),
    ])
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

    generalError.value =
      normalized.message
  } finally {
    saving.value = false
  }
}

function bulkResultCount(
  result:
    import(
      '@/modules/workload-distribution/types'
    ).BulkDistributionResult,
): number {
  return (
    result.approved_count ??
    result.cancelled_count ??
    result.restored_count ??
    result.returned_count ??
    0
  )
}

async function afterBulkAction(): Promise<void> {
  selectedDistributions.value =
    []

  await Promise.all([
    refresh(),
    loadLookups(),
    loadTeacherSummaries(),
  ])
}

function showBulkResult(
  result:
    import(
      '@/modules/workload-distribution/types'
    ).BulkDistributionResult,
): void {
  const successCount =
    bulkResultCount(
      result,
    )

  if (
    result.errors_count >
      0 ||
    result.unavailable_count >
      0
  ) {
    toast.info(
      t(
        'workloadDistribution.bulk.partialTitle',
      ),

      t(
        'workloadDistribution.bulk.partialResult',
        {
          success:
            successCount,

          errors:
            result.errors_count,

          unavailable:
            result.unavailable_count,
        },
      ),
    )

    return
  }

  toast.success(
    t('common.success'),

    t(
      'workloadDistribution.bulk.successResult',
      {
        count:
          successCount,
      },
    ),
  )
}

function openBulkAssign():
  void {
  if (
    !selectedPlannedWorkloads
      .value
      .length
  ) {
    return
  }

  if (
    !selectedPlannedCompatible
      .value
  ) {
    toast.info(
      t(
        'workloadDistribution.bulkAssign.incompatibleTitle',
      ),

      t(
        'workloadDistribution.bulkAssign.incompatible',
      ),
    )

    return
  }

  bulkAssignVisible.value =
    true
}

async function submitBulkAssign(
  payload:
    BulkAssignPlannedWorkloadPayload,
): Promise<void> {
  bulkAssignLoading.value =
    true

  try {
    const result =
      await assignSelectedPlannedWorkloads(
        payload,
      )

    bulkAssignVisible.value =
      false

    selectedPlannedWorkloads
      .value =
      []

    if (
      result.errors_count >
        0 ||
      result.unavailable_count >
        0
    ) {
      toast.info(
        t(
          'workloadDistribution.bulk.partialTitle',
        ),

        t(
          'workloadDistribution.bulkAssign.partialResult',
          {
            created:
              result.created_count,

            errors:
              result.errors_count,

            unavailable:
              result.unavailable_count,
          },
        ),
      )
    } else {
      toast.success(
        t(
          'common.success',
        ),

        t(
          'workloadDistribution.bulkAssign.success',
          {
            count:
              result.created_count,

            hours:
              result.allocated_hours,
          },
        ),
      )
    }

    await Promise.all([
      refresh(),
      loadLookups(),
      loadTeacherSummaries(),
    ])
  } catch (bulkError) {
    toast.error(
      t(
        'common.error',
      ),

      normalizeApiError(
        bulkError,
      ).message,
    )
  } finally {
    bulkAssignLoading.value =
      false
  }
}

async function approveSelected(): Promise<void> {
  const ids =
    selectedDraftIds.value

  if (!ids.length) {
    return
  }

  bulkLoading.value =
    true

  try {
    const result =
      await approveSelectedDistributions(
        ids,
      )

    showBulkResult(
      result,
    )

    await afterBulkAction()
  } catch (bulkError) {
    toast.error(
      t('common.error'),

      normalizeApiError(
        bulkError,
      ).message,
    )
  } finally {
    bulkLoading.value =
      false
  }
}

function openBulkReason(
  action:
    | 'cancel'
    | 'restore'
    | 'return-to-draft',
): void {
  if (
    selectedCount.value ===
    0
  ) {
    return
  }

  bulkReasonAction.value =
    action

  bulkReasonVisible.value =
    true
}

async function submitBulkReason(
  reason: string,
): Promise<void> {
  if (
    !bulkReasonAction.value
  ) {
    return
  }

  bulkLoading.value =
    true

  try {
    let result

    if (
      bulkReasonAction.value ===
      'cancel'
    ) {
      result =
        await cancelSelectedDistributions(
          selectedActiveIds.value,
          reason,
        )
    } else if (
      bulkReasonAction.value ===
      'restore'
    ) {
      result =
        await restoreSelectedDistributions(
          selectedCancelledIds.value,
          reason,
        )
    } else {
      result =
        await returnSelectedDistributionsToDraft(
          selectedApprovedIds.value,
          reason,
        )
    }

    bulkReasonVisible.value =
      false

    showBulkResult(
      result,
    )

    await afterBulkAction()
  } catch (bulkError) {
    toast.error(
      t('common.error'),

      normalizeApiError(
        bulkError,
      ).message,
    )
  } finally {
    bulkLoading.value =
      false
  }
}

async function approve(
  record:
    WorkloadDistribution,
): Promise<void> {
  actionLoading.value =
    true

  try {
    const response =
      await approveDistribution(
        record.id,
      )

    toast.success(
      t('common.success'),
      response.detail,
    )

    await Promise.all([
      refresh(),
      loadLookups(),
      loadTeacherSummaries(),
    ])
  } catch (actionError) {
    toast.error(
      t('common.error'),

      normalizeApiError(
        actionError,
      ).message,
    )
  } finally {
    actionLoading.value =
      false
  }
}

function openCancel(
  record:
    WorkloadDistribution,
): void {
  selectedRecord.value =
    record

  reasonAction.value =
    'cancel'

  reasonVisible.value =
    true
}

function openReturnToDraft(
  record:
    WorkloadDistribution,
): void {
  selectedRecord.value =
    record

  reasonAction.value =
    'return-to-draft'

  reasonVisible.value =
    true
}

async function submitReason(
  reason: string,
): Promise<void> {
  if (
    !selectedRecord.value ||
    !reasonAction.value
  ) {
    return
  }

  actionLoading.value =
    true

  try {
    const response =
      reasonAction.value ===
      'cancel'
        ? await cancelDistribution(
            selectedRecord.value.id,
            reason,
          )
        : await returnDistributionToDraft(
            selectedRecord.value.id,
            reason,
          )

    reasonVisible.value =
      false

    toast.success(
      t('common.success'),
      response.detail,
    )

    await Promise.all([
      refresh(),
      loadLookups(),
      loadTeacherSummaries(),
    ])
  } catch (actionError) {
    toast.error(
      t('common.error'),

      normalizeApiError(
        actionError,
      ).message,
    )
  } finally {
    actionLoading.value =
      false
  }
}

function archive(
  record:
    WorkloadDistribution,
): void {
  confirmDelete({
    header:
      t(
        'workloadDistribution.archiveTitle',
      ),

    message:
      t(
        'workloadDistribution.archiveConfirm',
        {
          teacher:
            record.teacher_name,
        },
      ),

    accept:
      async () => {
        try {
          await workloadDistributionsApi
            .remove(record.id)

          toast.success(
            t('common.success'),
            t(
              'workloadDistribution.archived',
            ),
          )

          await Promise.all([
            refresh(),
            loadLookups(),
            loadTeacherSummaries(),
          ])
        } catch (archiveError) {
          toast.error(
            t('common.error'),

            normalizeApiError(
              archiveError,
            ).message,
          )
        }
      },
  })
}

async function applyFilters(): Promise<void> {
  setFilter(
    'academic_year',
    selectedYear.value,
  )

  setFilter(
    'semester_number',
    selectedSemester.value,
  )

  setFilter(
    'teaching_department',
    selectedDepartment.value,
  )

  setFilter(
    'status',
    selectedStatus.value,
  )

  await load()
}

async function resetFilters(): Promise<void> {
  selectedYear.value = null
  selectedSemester.value = null
  selectedDepartment.value = null
  selectedStatus.value = null
  clearFilters()

  await reset()
}

onMounted(
  async () => {
    await Promise.all([
      load(),
      loadLookups(),
      loadTeacherSummaries(),
    ])
  },
)
</script>

<template>
  <div class="workload-distribution-page">
    <BasePageHeader
      :title="
        t(
          'workloadDistribution.title',
        )
      "
      :description="
        t(
          'workloadDistribution.description',
        )
      "
      icon="pi pi-user-edit"
    >
      <template #actions>
        <Button
          v-if="canCreate"
          :label="
            t(
              'workloadDistribution.create',
            )
          "
          icon="pi pi-plus"
          @click="openCreate"
        />
      </template>
    </BasePageHeader>

    <BaseToolbar
      v-model:search="searchInput"
      :show-create="false"
      :show-reset="true"
      :loading="loading || lookupLoading"
      :search-placeholder="
        t(
          'workloadDistribution.searchPlaceholder',
        )
      "
      @refresh="refresh"
      @reset="resetFilters"
    >
      <template #center>
        <Select
          v-model="selectedYear"
          :options="years"
          option-label="label"
          option-value="value"
          class="distribution-filter"
          @change="changeYear"
        />

        <Select
          v-model="selectedSemester"
          :options="semesters"
          option-label="label"
          option-value="value"
          class="distribution-filter"
          @change="applyFilters"
        />

        <Select
          v-model="selectedDepartment"
          :options="departments"
          option-label="label"
          option-value="value"
          filter
          class="distribution-filter"
          @change="applyFilters"
        />

        <Select
          v-model="
            selectedStatus
          "
          :options="statuses"
          option-label="label"
          option-value="value"
          class="
            distribution-filter
          "
          @change="
            applyFilters
          "
        />
      </template>
    </BaseToolbar>

    <BaseCard :padding="false">
      <PlannedWorkloadDistributionTable
        v-model:selection="selectedPlannedWorkloads"
        :items="visiblePlannedWorkloads"
        :loading="lookupLoading"
        :can-assign="canCreate"
        @assign="openAssign"
      />
    </BaseCard>

    <div
      v-if="selectedPlannedWorkloads.length > 0 "
      class="bulk-planned-actions"
    >
      <div>
        <strong>
          {{
            t(
              'workloadDistribution.bulkAssign.selected',
              {
                count: selectedPlannedWorkloads.length,
              },
            )
          }}
        </strong>

        <small>
          {{
            t(
              'workloadDistribution.bulkAssign.totalHours',
              {
                hours: selectedPlannedHours.toFixed(2),
              },
            )
          }}
        </small>
      </div>

      <div class="bulk-planned-actions__buttons">
        <Button
          :label="t('workloadDistribution.bulkAssign.assign',)"
          icon="pi pi-users"
          severity="success"
          :disabled="!selectedPlannedCompatible"
          @click="openBulkAssign"
        />

        <Button
          :label="t('workloadDistribution.bulk.clearSelection',)"
          icon="pi pi-times"
          severity="secondary"
          text
          @click="selectedPlannedWorkloads = []"
        />
      </div>
    </div>

    <div class="distribution-list-header ms-5">
      <h3>
        {{ t('workloadDistribution.distributions.title',) }}
      </h3>

      <small>
        {{ t('workloadDistribution.distributions.description',) }}
      </small>
    </div>

    <div v-if="selectedCount > 0" class="bulk-actions">
      <div class="bulk-actions__summary">
        <i class="pi pi-check-square" />
        <strong>
          {{
            t(
              'workloadDistribution.bulk.selected',
              {
                count:
                selectedCount,
              },
            )
          }}
        </strong>
      </div>

      <div class="bulk-actions__buttons" >
        <Button
          v-if="selectedDraftIds.length"
          :label="
            t(
              'workloadDistribution.bulk.approve',
              {
                count:
                  selectedDraftIds.length,
              },
            )
          "
          icon="pi pi-check"
          severity="success"
          size="small"
          :loading="bulkLoading"
          @click="approveSelected"
        />

        <Button
          v-if="selectedActiveIds.length"
          :label="
            t(
              'workloadDistribution.bulk.cancel',
              {
                count:
                  selectedActiveIds.length,
              },
            )
          "
          icon="pi pi-times"
          severity="danger"
          outlined
          size="small"
          :disabled="bulkLoading"
          @click="openBulkReason('cancel',)"
        />

        <Button
          v-if="selectedApprovedIds.length"
          :label="
              t(
                'workloadDistribution.bulk.returnToDraft',
                {
                  count:
                    selectedApprovedIds.length,
                },
              )
            "
          icon="pi pi-replay"
          severity="warn"
          outlined
          size="small"
          :disabled="bulkLoading"
          @click="openBulkReason('return-to-draft',)"
        />

        <Button
          v-if="selectedCancelledIds.length"
          :label="
            t(
              'workloadDistribution.bulk.restore',
              {
                count:
                  selectedCancelledIds.length,
              },
            )
          "
          icon="pi pi-refresh"
          severity="info"
          outlined
          size="small"
          :disabled="bulkLoading"
          @click="openBulkReason('restore',)"
        />

        <Button
          :label="
            t(
              'workloadDistribution.bulk.clearSelection',
            )
          "
          icon="pi pi-times-circle"
          severity="secondary"
          text
          size="small"
          @click="selectedDistributions = []"
        />
      </div>
    </div>

    <BaseCard :padding="false">
      <BaseDataTable
        v-model:selection="selectedDistributions"
        :value="items"
        :columns="columns"
        :loading="loading"
        :error="error"
        :first="first"
        :rows="query.pageSize"
        :total-records="totalRecords"
        selectable
        show-row-actions
        @page="handlePage"
        @sort="handleSort"
        @retry="refresh"
      >

        <template #semester="{ row }">
          <div class="distribution-semester">
            <strong>
              {{
                row.semester_number
              }}
            </strong>

            <small>
              {{
                row.season ===
                'autumn'
                  ? t(
                    'workloadDistribution.seasons.autumn',
                  )
                  : t(
                    'workloadDistribution.seasons.spring',
                  )
              }}
            </small>
          </div>
        </template>

        <template #scope="{ row }">
          <Tag
            v-if="row.workload_scope === 'stream' "
            :value="t('workloadDistribution.scope.stream',)"
            severity="info"
          />

          <Tag
            v-else
            :value="row.student_group_code ?? t('workloadDistribution.scope.group',)"
            severity="secondary"
          />
        </template>

        <template #teacher="{ row }">
          <div class="teacher-cell">
            <strong>
              {{
                row.teacher_name
              }}
            </strong>

            <small>
              {{
                row.position_name
              }}
              ·
              {{
                row.employment_rate
              }}
            </small>
          </div>
        </template>

        <template #status="{ row }">
          <Tag
            :value="
              t(
                `workloadDistribution.statuses.${row.status}`,
              )
            "
            :severity="statusSeverity(row.status,)"
          />
        </template>

        <template #actions="{ row }">
          <Button
            v-if="canEdit && row.status === 'draft' "
            v-tooltip.bottom="t('common.edit')"
            icon="pi pi-pencil"
            text
            rounded
            @click.stop="openEdit(row)"
          />

          <Button
            v-if="canEdit && row.status === 'draft' "
            v-tooltip.bottom="t('workloadDistribution.approve',)"
            icon="pi pi-check"
            severity="success"
            text
            rounded
            @click.stop="
              approve(row)
            "
          />

          <Button
            v-if="
              canEdit &&
              row.status !==
                'cancelled'
            "
            v-tooltip.bottom="
              t(
                'workloadDistribution.cancel',
              )
            "
            icon="pi pi-times"
            severity="warn"
            text
            rounded
            @click.stop="
              openCancel(row)
            "
          />

          <Button
            v-if="
              canEdit &&
              row.status !==
                'draft'
            "
            v-tooltip.bottom="
              t(
                'workloadDistribution.returnToDraft',
              )
            "
            icon="
              pi pi-undo
            "
            severity="secondary"
            text
            rounded
            @click.stop="
              openReturnToDraft(
                row,
              )
            "
          />

          <Button
            v-if="canDelete"
            v-tooltip.bottom="
              t(
                'workloadDistribution.archive',
              )
            "
            icon="pi pi-box"
            severity="danger"
            text
            rounded
            @click.stop="
              archive(row)
            "
          />
        </template>
      </BaseDataTable>
    </BaseCard>

    <BaseCard :title="t('workloadDistribution.teacherLoad.title',)">
      <TeacherWorkloadSummaryTable
        :items="teacherSummaries"
        :loading="teacherSummaryLoading"
      />
    </BaseCard>

    <WorkloadDistributionFormDialog
      v-model="formVisible"
      :record="selectedRecord"
      :initial-planned-workload-id="initialPlannedWorkloadId"
      :planned-workloads="plannedWorkloads"
      :employments="employments"
      :annual-records="annualRecords"
      :loading="saving"
      :field-errors="fieldErrors"
      :non-field-errors="nonFieldErrors"
      :general-error="generalError"
      @create="createDistribution"
      @update="updateDistribution"
    />

    <WorkloadDistributionReasonDialog
      v-model="reasonVisible"
      :title="
        reasonAction ===
        'cancel'
          ? t(
              'workloadDistribution.cancelTitle',
            )
          : t(
              'workloadDistribution.returnTitle',
            )
      "
      :loading="actionLoading"
      @submit="submitReason"
    />
    <WorkloadDistributionReasonDialog
      v-model="bulkReasonVisible"
      :title="bulkReasonTitle"
      :loading="bulkLoading"
      @submit="submitBulkReason"
    />

    <WorkloadBulkAssignDialog
      v-model="bulkAssignVisible"
      :workloads="selectedPlannedWorkloads"
      :employments="employments"
      :annual-records="annualRecords"
      :loading="bulkAssignLoading"
      @submit="submitBulkAssign"
    />

  </div>
</template>

<style scoped>
.distribution-semester {
  display: grid;
  gap: 0.1rem;
}

.distribution-semester small {
  color:
    var(--app-text-muted);

  font-size: 0.68rem;
}

.workload-distribution-page {
  display: grid;
  gap: 1rem;
}

.distribution-filter {
  width: 14rem;
}

.teacher-cell {
  display: grid;
  gap: 0.1rem;
}

.teacher-cell strong {
  font-size: 0.82rem;
}

.teacher-cell small {
  color:
    var(--app-text-muted);

  font-size: 0.7rem;
}

@media (max-width: 991px) {
  .distribution-filter {
    width: 100%;
  }
}

.distribution-list-header {
  display: grid;
  gap: 0.2rem;

  margin-top: 0.5rem;
}

.distribution-list-header h3 {
  margin: 0;

  font-size: 1rem;
}

.distribution-list-header small {
  color:
    var(--app-text-muted);

  font-size: 0.75rem;
}

.bulk-actions {
  display: flex;

  align-items: center;
  justify-content:
    space-between;

  gap: 1rem;

  padding: 0.75rem 1rem;

  border:
    1px solid
    var(--app-border-color);

  border-radius:
    var(--app-radius-md);

  background:
    var(--app-surface);
}

.bulk-actions__summary {
  display: flex;

  align-items: center;

  gap: 0.5rem;

  white-space: nowrap;
}

.bulk-actions__buttons {
  display: flex;

  align-items: center;
  justify-content:
    flex-end;

  flex-wrap: wrap;

  gap: 0.5rem;
}

@media (
  max-width: 900px
) {
  .bulk-actions {
    align-items:
      flex-start;

    flex-direction:
      column;
  }

  .bulk-actions__buttons {
    justify-content:
      flex-start;
  }
}

.bulk-planned-actions {
  display: flex;

  align-items: center;
  justify-content:
    space-between;

  gap: 1rem;

  margin-top: 0.75rem;

  padding:
    0.75rem
    1rem;

  border:
    1px solid
    var(--app-border-color);

  border-radius:
    var(--app-radius-md);

  background:
    var(--app-surface);
}

.bulk-planned-actions > div:first-child {
  display: grid;
  gap: 0.2rem;
}

.bulk-planned-actions small {
  color:
    var(--app-text-muted);
}

.bulk-planned-actions__buttons {
  display: flex;

  align-items: center;

  gap: 0.5rem;
}

@media (
  max-width: 800px
) {
  .bulk-planned-actions {
    align-items:
      flex-start;

    flex-direction:
      column;
  }

  .bulk-planned-actions__buttons {
    flex-wrap: wrap;
  }
}
</style>
