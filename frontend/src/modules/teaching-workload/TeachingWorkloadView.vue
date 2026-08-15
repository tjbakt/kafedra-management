<script setup lang="ts">
import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'
import Select from 'primevue/select'
import Tab from 'primevue/tab'
import TabList from 'primevue/tablist'
import TabPanel from 'primevue/tabpanel'
import TabPanels from 'primevue/tabpanels'
import Tabs from 'primevue/tabs'
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

import TeachingStreamFormDialog from '@/modules/teaching-workload/components/TeachingStreamFormDialog.vue'
import TeachingStreamGroupsDialog from '@/modules/teaching-workload/components/TeachingStreamGroupsDialog.vue'

import {
  calculateAllStreams,
  calculateStream,
  getAcademicSemesters,
  getAcademicYears,
  getCurricula,
  getGroupSemesters,
  getPlannedWorkloadSummary,
  plannedWorkloadsApi,
  teachingStreamsApi,
} from '@/modules/teaching-workload/api'

import type {
  AcademicSemesterLookup,
  AcademicYearLookup,
  CurriculumLookup,
  GroupSemester,
  PlannedWorkload,
  PlannedWorkloadSummary,
  SelectOption,
  TeachingStream,
  TeachingStreamPayload,
  TeachingStreamStatus,
} from '@/modules/teaching-workload/types'

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

const activeTab =
  ref('streams')

const academicYears =
  ref<AcademicYearLookup[]>([])

const academicSemesters =
  ref<AcademicSemesterLookup[]>([])

const curricula =
  ref<CurriculumLookup[]>([])

const groupSemesters =
  ref<GroupSemester[]>([])

const lookupLoading =
  ref(false)

const selectedStream =
  ref<TeachingStream | null>(
    null,
  )

const streamDialog =
  ref(false)

const groupsDialog =
  ref(false)

const saving =
  ref(false)

const calculatingId =
  ref<number | null>(null)

const calculatingAll =
  ref(false)

const fieldErrors =
  ref<FieldErrors>({})

const nonFieldErrors =
  ref<string[]>([])

const generalError =
  ref('')

const selectedStreamYear =
  ref<number | null>(null)

const selectedStreamSemester =
  ref<number | null>(null)

const selectedStreamStatus =
  ref<TeachingStreamStatus | null>(
    null,
  )

const selectedStreamActive =
  ref<boolean | null>(null)

const selectedPlannedYear =
  ref<number | null>(null)

const selectedPlannedSemester =
  ref<number | null>(null)

const selectedPlannedStatus =
  ref<string | null>(null)

const selectedFullyDistributed =
  ref<boolean | null>(null)

const summary =
  ref<PlannedWorkloadSummary | null>(
    null,
  )

const canCreateStream =
  computed(
    () =>
      can(
        'teaching.add_teachingstream',
      ),
  )

const canEditStream =
  computed(
    () =>
      can(
        'teaching.change_teachingstream',
      ),
  )

const canDeleteStream =
  computed(
    () =>
      can(
        'teaching.delete_teachingstream',
      ),
  )

const canManageStreamGroups =
  computed(
    () =>
      can(
        'teaching.add_teachingstreamgroup',
      ) ||
      can(
        'teaching.change_teachingstreamgroup',
      ) ||
      can(
        'teaching.delete_teachingstreamgroup',
      ),
  )

const canCalculate =
  computed(
    () =>
      can(
        'teaching.change_teachingstream',
      ),
  )

const yearOptions =
  computed<
    SelectOption<
      number | null
    >[]
  >(() => [
    {
      value: null,

      label:
        t(
          'teachingWorkload.filters.allYears',
        ),
    },

    ...academicYears.value.map(
      (year) => ({
        value: year.id,
        label: year.name,
      }),
    ),
  ])

function semesterFilterOptions(
  year:
    number | null,
): SelectOption<
  number | null
>[] {
  return [
    {
      value: null,

      label:
        t(
          'teachingWorkload.filters.allSemesters',
        ),
    },

    ...academicSemesters.value
      .filter(
        (semester) =>
          !year ||
          semester.academic_year ===
            year,
      )
      .map(
        (semester) => ({
          value:
            semester.id,

          label:
            `${semester.academic_year_name} — ${semester.season_name}`,
        }),
      ),
  ]
}

const streamSemesterOptions =
  computed(
    () =>
      semesterFilterOptions(
        selectedStreamYear.value,
      ),
  )

const plannedSemesterOptions =
  computed(
    () =>
      semesterFilterOptions(
        selectedPlannedYear.value,
      ),
  )

const streamStatusOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'teachingWorkload.filters.allStatuses',
        ),
    },

    {
      value: 'draft',

      label:
        t(
          'teachingWorkload.streams.statuses.draft',
        ),
    },

    {
      value:
        'calculated',

      label:
        t(
          'teachingWorkload.streams.statuses.calculated',
        ),
    },

    {
      value: 'approved',

      label:
        t(
          'teachingWorkload.streams.statuses.approved',
        ),
    },

    {
      value:
        'cancelled',

      label:
        t(
          'teachingWorkload.streams.statuses.cancelled',
        ),
    },
  ])

const plannedStatusOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'teachingWorkload.filters.allStatuses',
        ),
    },

    ...[
      'calculated',
      'approved',
      'partially_distributed',
      'distributed',
      'cancelled',
    ].map(
      (status) => ({
        value: status,

        label:
          t(
            `teachingWorkload.planned.statuses.${status}`,
          ),
      }),
    ),
  ])

const activityOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'teachingWorkload.filters.allActivity',
        ),
    },

    {
      value: true,

      label:
        t(
          'teachingWorkload.common.active',
        ),
    },

    {
      value: false,

      label:
        t(
          'teachingWorkload.common.inactive',
        ),
    },
  ])

const distributedOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'teachingWorkload.filters.allDistribution',
        ),
    },

    {
      value: true,

      label:
        t(
          'teachingWorkload.filters.fullyDistributed',
        ),
    },

    {
      value: false,

      label:
        t(
          'teachingWorkload.filters.notFullyDistributed',
        ),
    },
  ])

const streamColumns =
  computed<CrudColumn<TeachingStream>[]>(()=> [
    {
      field: 'code',
      header: t( 'teachingWorkload.streams.fields.code',),
      sortable: true,
    },
    {
      field: 'name',
      header: t('teachingWorkload.streams.fields.name',),
    },
    {
      field: 'curriculum_code',
      header: t('teachingWorkload.streams.fields.curriculum',),
    },
    {
      field: 'study_program_name',
      header: t('teachingWorkload.streams.fields.studyProgram',),
    },

    {
      field:
        'semester_number',

      header:
        t(
          'teachingWorkload.streams.fields.semesterNumber',
        ),

      align: 'center',
    },

    {
      field:
        'academic_semester_name',

      header:
        t(
          'teachingWorkload.streams.fields.academicSemester',
        ),
    },

    {
      field:
        'groups_count',

      header:
        t(
          'teachingWorkload.streams.fields.groups',
        ),

      align: 'center',
    },

    {
      field:
        'students_count',

      header:
        t(
          'teachingWorkload.streams.fields.students',
        ),

      align: 'center',
    },

    {
      field:
        'planned_workloads_count',

      header:
        t(
          'teachingWorkload.streams.fields.positions',
        ),

      align: 'center',
    },

    {
      field:
        'total_planned_hours',

      header:
        t(
          'teachingWorkload.streams.fields.totalHours',
        ),

      align: 'center',
    },

    {
      field: 'status',

      header:
        t(
          'teachingWorkload.streams.fields.status',
        ),

      bodySlot:
        'streamStatus',
    },
  ])

const plannedColumns =
  computed<
    CrudColumn<PlannedWorkload>[]
  >(() => [
    {
      field:
        'teaching_stream_code',

      header:
        t(
          'teachingWorkload.planned.fields.stream',
        ),

      minWidth: '10rem',
    },

    {
      field:
        'discipline_name',

      header:
        t(
          'teachingWorkload.planned.fields.discipline',
        ),

      minWidth: '15rem',
    },

    {
      field:
        'workload_type_name',

      header:
        t(
          'teachingWorkload.planned.fields.workloadType',
        ),

      minWidth: '12rem',
    },

    {
      field:
        'base_hours',

      header:
        t(
          'teachingWorkload.planned.fields.baseHours',
        ),

      width: '8rem',

      align: 'center',
    },

    {
      field:
        'calculation_quantity',

      header:
        t(
          'teachingWorkload.planned.fields.quantity',
        ),

      width: '8rem',

      align: 'center',
    },

    {
      field:
        'total_hours',

      header:
        t(
          'teachingWorkload.planned.fields.totalHours',
        ),

      sortable: true,

      width: '9rem',

      align: 'center',
    },

    {
      field:
        'remaining_hours',

      header:
        t(
          'teachingWorkload.planned.fields.remainingHours',
        ),

      width: '9rem',

      align: 'center',
    },

    {
      field:
        'distribution_percent',

      header:
        t(
          'teachingWorkload.planned.fields.distribution',
        ),

      bodySlot:
        'distribution',

      minWidth: '11rem',
    },

    {
      field: 'status',

      header:
        t(
          'teachingWorkload.planned.fields.status',
        ),

      bodySlot:
        'plannedStatus',

      minWidth: '10rem',
    },
  ])

const streams =
  useCrudList<TeachingStream>(
    (params) =>
      teachingStreamsApi.list(
        params,
      ),

    {
      initialPageSize: 20,

      initialOrdering:
        '-academic_year__start_year,code',
    },
  )

const planned =
  useCrudList<PlannedWorkload>(
    (params) =>
      plannedWorkloadsApi.list(
        params,
      ),

    {
      initialPageSize: 20,

      initialOrdering:
        '-academic_year__start_year,calculated_at',
    },
  )

function clearErrors(): void {
  fieldErrors.value = {}

  nonFieldErrors.value = []

  generalError.value = ''
}

async function loadLookups(): Promise<void> {
  lookupLoading.value = true

  try {
    const [
      yearsResponse,
      semestersResponse,
      // disciplinesResponse,
      // workloadsResponse,
      curriculaResponse,
      groupSemestersResponse,
    ] = await Promise.all([
      getAcademicYears(),
      getAcademicSemesters(),
      getCurricula(),
      getGroupSemesters(),
    ])

    academicYears.value =
      yearsResponse.results

    academicSemesters.value =
      semestersResponse.results

    curricula.value =
      curriculaResponse.results

    groupSemesters.value =
      groupSemestersResponse.results
  } catch (loadError) {
    const normalized =
      normalizeApiError(
        loadError,
        t('crud.loadError'),
      )

    toast.error(
      t('common.error'),
      normalized.message,
    )
  } finally {
    lookupLoading.value = false
  }
}

async function loadSummary(): Promise<void> {
  try {
    summary.value =
      await getPlannedWorkloadSummary({
        academic_year:
          selectedPlannedYear.value ??
          undefined,

        academic_semester:
          selectedPlannedSemester.value ??
          undefined,

        status:
          selectedPlannedStatus.value ??
          undefined,

        is_fully_distributed:
          selectedFullyDistributed.value ??
          undefined,
      })
  } catch {
    summary.value = null
  }
}

function openCreateStream(): void {
  selectedStream.value =
    null

  clearErrors()

  streamDialog.value =
    true
}

function openEditStream(
  record: TeachingStream,
): void {
  selectedStream.value =
    record

  clearErrors()

  streamDialog.value =
    true
}

function openGroups(
  record: TeachingStream,
): void {
  selectedStream.value =
    record

  groupsDialog.value =
    true
}

async function saveStream(
  payload:
    TeachingStreamPayload,
): Promise<void> {
  saving.value = true

  clearErrors()

  try {
    if (
      selectedStream.value
    ) {
      await teachingStreamsApi.update(
        selectedStream.value.id,
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.updated'),
      )
    } else {
      await teachingStreamsApi.create(
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.created'),
      )
    }

    streamDialog.value = false

    selectedStream.value = null

    await streams.refresh()
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

async function handleGroupsChanged(): Promise<void> {
  await streams.refresh()

  if (
    !selectedStream.value
  ) {
    return
  }

  const refreshed =
    streams.items.value.find(
      (item) =>
        item.id ===
        selectedStream.value?.id,
    )

  if (refreshed) {
    selectedStream.value =
      refreshed
  }
}

function archiveStream(
  record: TeachingStream,
): void {
  confirmDelete({
    header:
      t(
        'teachingWorkload.streams.archiveTitle',
      ),

    message:
      t(
        'teachingWorkload.streams.archiveConfirm',
        {
          code:
            record.code,
        },
      ),

    accept:
      async () => {
        try {
          await teachingStreamsApi.remove(
            record.id,
          )

          await streams.refresh()

          toast.success(
            t('common.success'),

            t(
              'teachingWorkload.streams.archived',
            ),
          )
        } catch (
          archiveError
        ) {
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

async function calculateOne(
  record: TeachingStream,
): Promise<void> {
  calculatingId.value =
    record.id

  try {
    const result =
      await calculateStream(
        record.id,
      )

    toast.success(
      t('common.success'),
      result.detail,
    )

    await Promise.all([
      streams.refresh(),
      planned.refresh(),
      loadSummary(),
    ])
  } catch (calculateError) {
    toast.error(
      t('common.error'),

      normalizeApiError(
        calculateError,
        t(
          'teachingWorkload.calculateError',
        ),
      ).message,
    )
  } finally {
    calculatingId.value =
      null
  }
}

async function calculateAll(): Promise<void> {
  calculatingAll.value =
    true

  try {
    const result =
      await calculateAllStreams({
        academic_year:
          selectedStreamYear.value ??
          undefined,

        academic_semester:
          selectedStreamSemester.value ??
          undefined,

        status:
          selectedStreamStatus.value ??
          undefined,

        is_active:
          selectedStreamActive.value ??
          undefined,
      })

    if (
      result.errors_count
    ) {
      toast.error(
        t(
          'teachingWorkload.calculatePartialTitle',
        ),

        t(
          'teachingWorkload.calculatePartial',
          {
            calculated:
              result.calculated_count,

            errors:
              result.errors_count,
          },
        ),
      )
    } else {
      toast.success(
        t('common.success'),

        t(
          'teachingWorkload.calculateAllSuccess',
          {
            count:
              result.calculated_count,
          },
        ),
      )
    }

    await Promise.all([
      streams.refresh(),
      planned.refresh(),
      loadSummary(),
    ])
  } catch (calculateError) {
    toast.error(
      t('common.error'),

      normalizeApiError(
        calculateError,
        t(
          'teachingWorkload.calculateError',
        ),
      ).message,
    )
  } finally {
    calculatingAll.value =
      false
  }
}

function streamStatusSeverity(
  status: TeachingStreamStatus,
):
  | 'success'
  | 'info'
  | 'secondary'
  | 'danger' {
  if (status === 'approved') {
    return 'success'
  }

  if (status === 'calculated') {
    return 'info'
  }

  if (status === 'cancelled') {
    return 'danger'
  }

  return 'secondary'
}

function plannedStatusSeverity(
  status: string,
):
  | 'success'
  | 'info'
  | 'warn'
  | 'secondary'
  | 'danger' {
  if (
    status === 'distributed'
  ) {
    return 'success'
  }

  if (
    status ===
    'partially_distributed'
  ) {
    return 'warn'
  }

  if (
    status === 'approved'
  ) {
    return 'info'
  }

  if (
    status === 'cancelled'
  ) {
    return 'danger'
  }

  return 'secondary'
}

function asNumber(
  value:
    string | number | null | undefined,
): number {
  const result =
    Number(value ?? 0)

  return Number.isFinite(
    result,
  )
    ? result
    : 0
}

async function applyStreamYear(): Promise<void> {
  streams.setFilter(
    'academic_year',
    selectedStreamYear.value,
  )

  selectedStreamSemester.value =
    null

  streams.setFilter(
    'academic_semester',
    undefined,
  )

  await streams.load()
}

async function applyStreamSemester(): Promise<void> {
  streams.setFilter(
    'academic_semester',
    selectedStreamSemester.value,
  )

  await streams.load()
}

async function applyStreamStatus(): Promise<void> {
  streams.setFilter(
    'status',
    selectedStreamStatus.value,
  )

  await streams.load()
}

async function applyStreamActive(): Promise<void> {
  streams.setFilter(
    'is_active',
    selectedStreamActive.value,
  )

  await streams.load()
}

async function resetStreamFilters(): Promise<void> {
  selectedStreamYear.value =
    null

  selectedStreamSemester.value =
    null

  selectedStreamStatus.value =
    null

  selectedStreamActive.value =
    null

  streams.clearFilters()

  await streams.reset()
}

async function applyPlannedFilters(): Promise<void> {
  planned.setFilter(
    'academic_year',
    selectedPlannedYear.value,
  )

  planned.setFilter(
    'academic_semester',
    selectedPlannedSemester.value,
  )

  planned.setFilter(
    'status',
    selectedPlannedStatus.value,
  )

  planned.setFilter(
    'is_fully_distributed',
    selectedFullyDistributed.value,
  )

  await Promise.all([
    planned.load(),
    loadSummary(),
  ])
}

async function changePlannedYear(): Promise<void> {
  selectedPlannedSemester.value =
    null

  await applyPlannedFilters()
}

async function resetPlannedFilters(): Promise<void> {
  selectedPlannedYear.value =
    null

  selectedPlannedSemester.value =
    null

  selectedPlannedStatus.value =
    null

  selectedFullyDistributed.value =
    null

  planned.clearFilters()

  await Promise.all([
    planned.reset(),
    loadSummary(),
  ])
}

onMounted(
  async () => {
    await Promise.all([
      streams.load(),
      planned.load(),
      loadLookups(),
      loadSummary(),
    ])
  },
)
</script>

<template>
  <div
    class="
      teaching-workload-page
    "
  >
    <BasePageHeader
      :title="
        t(
          'teachingWorkload.title',
        )
      "
      :description="
        t(
          'teachingWorkload.description',
        )
      "
      icon="pi pi-chart-bar"
    />

    <Tabs
      v-model:value="
        activeTab
      "
    >
      <TabList>
        <Tab value="streams">
          {{
            t(
              'teachingWorkload.tabs.streams',
            )
          }}
        </Tab>

        <Tab value="planned">
          {{
            t(
              'teachingWorkload.tabs.planned',
            )
          }}
        </Tab>
      </TabList>

      <TabPanels>
        <TabPanel value="streams">
          <div
            class="
              teaching-workload-page__panel
            "
          >
            <BaseToolbar
              v-model:search="
                streams.searchInput.value
              "
              :show-create="false"
              :show-reset="true"
              :loading="
                streams.loading.value ||
                lookupLoading
              "
              :search-placeholder="
                t(
                  'teachingWorkload.streams.searchPlaceholder',
                )
              "
              @refresh="
                streams.refresh
              "
              @reset="
                resetStreamFilters
              "
            >
              <template #start>
                <Button
                  v-if="
                    canCreateStream
                  "
                  :label="
                    t(
                      'teachingWorkload.streams.create',
                    )
                  "
                  icon="pi pi-plus"
                  @click="
                    openCreateStream
                  "
                />

                <Button
                  v-if="
                    canCalculate
                  "
                  :label="
                    t(
                      'teachingWorkload.calculateAll',
                    )
                  "
                  icon="
                    pi pi-calculator
                  "
                  severity="info"
                  :loading="
                    calculatingAll
                  "
                  @click="
                    calculateAll
                  "
                />
              </template>

              <template #center>
                <Select
                  v-model="
                    selectedStreamYear
                  "
                  :options="
                    yearOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="
                    workload-filter
                  "
                  @change="
                    applyStreamYear
                  "
                />

                <Select
                  v-model="
                    selectedStreamSemester
                  "
                  :options="
                    streamSemesterOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="
                    workload-filter
                  "
                  @change="
                    applyStreamSemester
                  "
                />

                <Select
                  v-model="
                    selectedStreamStatus
                  "
                  :options="
                    streamStatusOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="
                    workload-filter
                  "
                  @change="
                    applyStreamStatus
                  "
                />

                <Select
                  v-model="
                    selectedStreamActive
                  "
                  :options="
                    activityOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="
                    workload-filter
                  "
                  @change="
                    applyStreamActive
                  "
                />
              </template>
            </BaseToolbar>

            <BaseCard
              :padding="false"
            >
              <BaseDataTable
                :value="
                  streams.items.value
                "
                :columns="streamColumns"
                :loading="
                  streams.loading.value
                "
                :error="
                  streams.error.value
                "
                :first="
                  streams.first.value
                "
                :rows="
                  streams.query.value
                    .pageSize
                "
                :total-records="
                  streams
                    .totalRecords.value
                "
                show-row-actions
                @page="
                  streams.handlePage
                "
                @sort="
                  streams.handleSort
                "
                @retry="
                  streams.refresh
                "
              >
                <template
                  #streamStatus="{ row }"
                >
                  <Tag
                    :value="
                      t(
                        `teachingWorkload.streams.statuses.${row.status}`,
                      )
                    "
                    :severity="
                      streamStatusSeverity(
                        row.status,
                      )
                    "
                  />
                </template>

                <template
                  #streamActive="{ row }"
                >
                  <Tag
                    :value="
                      row.is_active
                        ? t(
                            'teachingWorkload.common.active',
                          )
                        : t(
                            'teachingWorkload.common.inactive',
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
                    v-if="
                      canManageStreamGroups
                    "
                    v-tooltip.bottom="
                      t(
                        'teachingWorkload.streamGroups.title',
                      )
                    "
                    icon="pi pi-users"
                    severity="info"
                    text
                    rounded
                    @click.stop="
                      openGroups(row)
                    "
                  />

                  <Button
                    v-if="canCalculate"
                    v-tooltip.bottom="
                      t(
                        'teachingWorkload.calculate',
                      )
                    "
                    icon="
                      pi pi-calculator
                    "
                    severity="success"
                    text
                    rounded
                    :loading="
                      calculatingId ===
                      row.id
                    "
                    @click.stop="
                      calculateOne(row)
                    "
                  />

                  <Button
                    v-if="
                      canEditStream
                    "
                    v-tooltip.bottom="
                      t('common.edit')
                    "
                    icon="pi pi-pencil"
                    text
                    rounded
                    @click.stop="
                      openEditStream(row)
                    "
                  />

                  <Button
                    v-if="
                      canDeleteStream
                    "
                    v-tooltip.bottom="
                      t(
                        'teachingWorkload.common.archive',
                      )
                    "
                    icon="pi pi-box"
                    severity="danger"
                    text
                    rounded
                    @click.stop="
                      archiveStream(row)
                    "
                  />
                </template>
              </BaseDataTable>
            </BaseCard>
          </div>
        </TabPanel>

        <TabPanel value="planned">
          <div
            class="
              teaching-workload-page__panel
            "
          >
            <div
              class="
                workload-summary
              "
            >
              <BaseCard>
                <div
                  class="
                    workload-summary__item
                  "
                >
                  <span>
                    {{
                      t(
                        'teachingWorkload.planned.summary.totalHours',
                      )
                    }}
                  </span>

                  <strong>
                    {{
                      asNumber(
                        summary
                          ?.total_hours,
                      ).toFixed(2)
                    }}
                  </strong>
                </div>
              </BaseCard>

              <BaseCard>
                <div
                  class="
                    workload-summary__item
                  "
                >
                  <span>
                    {{
                      t(
                        'teachingWorkload.planned.summary.records',
                      )
                    }}
                  </span>

                  <strong>
                    {{
                      planned
                        .totalRecords
                        .value
                    }}
                  </strong>
                </div>
              </BaseCard>
            </div>

            <BaseToolbar
              v-model:search="
                planned.searchInput.value
              "
              :show-create="false"
              :show-reset="true"
              :loading="
                planned.loading.value
              "
              :search-placeholder="
                t(
                  'teachingWorkload.planned.searchPlaceholder',
                )
              "
              @refresh="
                planned.refresh
              "
              @reset="
                resetPlannedFilters
              "
            >
              <template #center>
                <Select
                  v-model="
                    selectedPlannedYear
                  "
                  :options="
                    yearOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="
                    workload-filter
                  "
                  @change="
                    changePlannedYear
                  "
                />

                <Select
                  v-model="
                    selectedPlannedSemester
                  "
                  :options="
                    plannedSemesterOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="
                    workload-filter
                  "
                  @change="
                    applyPlannedFilters
                  "
                />

                <Select
                  v-model="
                    selectedPlannedStatus
                  "
                  :options="
                    plannedStatusOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="
                    workload-filter
                  "
                  @change="
                    applyPlannedFilters
                  "
                />

                <Select
                  v-model="
                    selectedFullyDistributed
                  "
                  :options="
                    distributedOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="
                    workload-filter
                  "
                  @change="
                    applyPlannedFilters
                  "
                />
              </template>
            </BaseToolbar>

            <BaseCard
              :padding="false"
            >
              <BaseDataTable
                :value="
                  planned.items.value
                "
                :columns="
                  plannedColumns
                "
                :loading="
                  planned.loading.value
                "
                :error="
                  planned.error.value
                "
                :first="
                  planned.first.value
                "
                :rows="
                  planned.query.value
                    .pageSize
                "
                :total-records="
                  planned
                    .totalRecords.value
                "
                @page="
                  planned.handlePage
                "
                @sort="
                  planned.handleSort
                "
                @retry="
                  planned.refresh
                "
              >
                <template
                  #distribution="{ row }"
                >
                  <div
                    class="
                      distribution-cell
                    "
                  >
                    <ProgressBar
                      :value="
                        Math.min(
                          100,
                          asNumber(
                            row.distribution_percent,
                          ),
                        )
                      "
                    />

                    <small>
                      {{
                        asNumber(
                          row.distributed_hours,
                        ).toFixed(2)
                      }}
                      /
                      {{
                        asNumber(
                          row.total_hours,
                        ).toFixed(2)
                      }}
                    </small>
                  </div>
                </template>

                <template
                  #plannedStatus="{ row }"
                >
                  <Tag
                    :value="
                      t(
                        `teachingWorkload.planned.statuses.${row.status}`,
                      )
                    "
                    :severity="
                      plannedStatusSeverity(
                        row.status,
                      )
                    "
                  />
                </template>
              </BaseDataTable>
            </BaseCard>
          </div>
        </TabPanel>
      </TabPanels>
    </Tabs>

    <TeachingStreamFormDialog
      v-model="
        streamDialog
      "
      :record="
        selectedStream
      "
      :academic-years="
        academicYears
      "
      :academic-semesters="academicSemesters"
      :curricula="curricula"
      :loading="saving"
      :field-errors="
        fieldErrors
      "
      :non-field-errors="
        nonFieldErrors
      "
      :general-error="
        generalError
      "
      @submit="
        saveStream
      "
    />

    <TeachingStreamGroupsDialog
      v-model="
        groupsDialog
      "
      :stream="
        selectedStream
      "
      :group-semesters="
        groupSemesters
      "
      @changed="
        handleGroupsChanged
      "
    />
  </div>
</template>

<style scoped>
.teaching-workload-page,
.teaching-workload-page__panel {
  display: grid;
  gap: 1rem;
}

.workload-filter {
  width: 13rem;
}

.workload-summary {
  display: grid;

  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );

  gap: 1rem;
}

.workload-summary__item {
  display: grid;
  gap: 0.25rem;
}

.workload-summary__item span {
  color:
    var(--app-text-muted);

  font-size: 0.72rem;
}

.workload-summary__item strong {
  font-size: 1.25rem;
}

.distribution-cell {
  display: grid;
  gap: 0.2rem;

  min-width: 10rem;
}

.distribution-cell small {
  color:
    var(--app-text-muted);

  text-align: center;

  font-size: 0.68rem;
}

:deep(.p-tabpanels) {
  padding: 1rem 0 0;
}

@media (max-width: 991px) {
  .workload-filter {
    width: 100%;
  }

  .workload-summary {
    grid-template-columns: 1fr;
  }
}
</style>
