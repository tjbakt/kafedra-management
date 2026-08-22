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

import TeachingStreamFormDialog from '@/modules/teaching-workload/components/TeachingStreamFormDialog.vue'
import TeachingStreamGroupsDialog from '@/modules/teaching-workload/components/TeachingStreamGroupsDialog.vue'

import {
  calculateAllStreams,
  calculateStream,
  createTeachingStreamsBulk,
  getAcademicYears,
  getCurricula,
  getGroupSemesters,
  teachingStreamsApi,
} from '@/modules/teaching-workload/api'

import type {
  AcademicYearLookup,
  CurriculumLookup,
  GroupSemester,
  SelectOption,
  TeachingStream,
  TeachingStreamBulkPayload,
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

const academicYears =
  ref<AcademicYearLookup[]>([])

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

const selectedStreamStatus =
  ref<TeachingStreamStatus | null>(
    null,
  )

const selectedStreamActive =
  ref<boolean | null>(null)

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
      curriculaResponse,
      groupSemestersResponse,
    ] = await Promise.all([
      getAcademicYears(),
      getCurricula(),
      getGroupSemesters(),
    ])
    academicYears.value = yearsResponse.results
    curricula.value = curriculaResponse.results
    groupSemesters.value = groupSemestersResponse.results
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
    TeachingStreamBulkPayload,
): Promise<void> {
  saving.value = true

  clearErrors()

  try {
    if (
      selectedStream.value
    ) {
      const semesterNumber =
        payload.semester_numbers[0]

      if (!semesterNumber) {
        return
      }

      const updatePayload:
        TeachingStreamPayload =
        {
          academic_year:
            payload.academic_year,

          curriculum:
            payload.curriculum,

          semester_number:
            semesterNumber,

          code:
            payload.code,

          name:
            payload.name,

          status:
            payload.status,

          is_active:
            payload.is_active,

          notes:
            payload.notes,
        }

      await teachingStreamsApi.update(
        selectedStream.value.id,
        updatePayload,
      )

      toast.success(
        t('common.success'),
        t('crud.updated'),
      )
    } else {
      await createTeachingStreamsBulk(
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.created'),
      )
    }

    streamDialog.value =
      false

    selectedStream.value =
      null

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
    saving.value =
      false
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

    await streams.refresh()
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

    await streams.refresh()
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

async function applyStreamYear(): Promise<void> {
  streams.setFilter(
    'academic_year',
    selectedStreamYear.value,
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

  selectedStreamStatus.value =
    null

  selectedStreamActive.value =
    null

  streams.clearFilters()

  await streams.reset()
}

onMounted(
  async () => {
    await Promise.all([
      streams.load(),
      loadLookups(),
    ])
  },
)
</script>

<template>
  <div class="teaching-workload-page" >

    <BasePageHeader
      :title="t('teachingWorkload.title')"
      :description="t('teachingWorkload.description')"
      icon="pi pi-chart-bar"
    />

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
          :columns="
            streamColumns
          "
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
            #streamStatus="
              { row }
            "
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
            #streamActive="
              { row }
            "
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
            #actions="
              { row }
            "
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
              v-if="
                canCalculate
              "
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
                t(
                  'common.edit',
                )
              "
              icon="
                pi pi-pencil
              "
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
              icon="
                pi pi-box
              "
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

    <TeachingStreamFormDialog
      v-model="streamDialog"
      :record="selectedStream"
      :academic-years="academicYears"
      :curricula="curricula"
      :group-semesters="groupSemesters"
      :loading="saving"
      :field-errors="fieldErrors"
      :non-field-errors="nonFieldErrors"
      :general-error="generalError"
      @submit="saveStream"
    />
    <TeachingStreamGroupsDialog
      v-model="groupsDialog"
      :stream="selectedStream"
      :group-semesters="groupSemesters"
      @changed="handleGroupsChanged"
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

@media (max-width: 991px) {
  .workload-filter {
    width: 100%;
  }
}
</style>
