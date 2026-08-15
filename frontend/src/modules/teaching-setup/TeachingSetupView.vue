<script setup lang="ts">
import Button from 'primevue/button'
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

import GroupCurriculumFormDialog from '@/modules/teaching-setup/components/GroupCurriculumFormDialog.vue'
import GroupSemesterFormDialog from '@/modules/teaching-setup/components/GroupSemesterFormDialog.vue'

import {
  getAcademicSemesters,
  getAcademicYears,
  getCurricula,
  getStudentGroups,
  groupCurriculaApi,
  groupSemestersApi,
} from '@/modules/teaching-setup/api'

import type {
  AcademicSemesterLookup,
  AcademicYearLookup,
  CurriculumLookup,
  GroupCurriculumAssignment,
  GroupCurriculumPayload,
  GroupSemester,
  GroupSemesterPayload,
  GroupSemesterStatus,
  StudentGroupLookup,
} from '@/modules/teaching-setup/types'

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
  ref('curricula')

const studentGroups =
  ref<StudentGroupLookup[]>([])

const curricula =
  ref<CurriculumLookup[]>([])

const academicYears =
  ref<AcademicYearLookup[]>([])

const academicSemesters =
  ref<AcademicSemesterLookup[]>([])

const lookupLoading =
  ref(false)

const selectedAssignment =
  ref<GroupCurriculumAssignment | null>(
    null,
  )

const selectedSemester =
  ref<GroupSemester | null>(
    null,
  )

const assignmentDialog =
  ref(false)

const semesterDialog =
  ref(false)

const saving =
  ref(false)

const fieldErrors =
  ref<FieldErrors>({})

const nonFieldErrors =
  ref<string[]>([])

const generalError =
  ref('')

const selectedAssignmentYear =
  ref<number | null>(null)

const selectedPrimary =
  ref<boolean | null>(null)

const selectedAssignmentActive =
  ref<boolean | null>(null)

const selectedSemesterYear =
  ref<number | null>(null)

const selectedSemesterStatus =
  ref<GroupSemesterStatus | null>(
    null,
  )

const selectedSemesterActive =
  ref<boolean | null>(null)

const canCreateAssignment =
  computed(
    () =>
      can(
        'teaching.add_groupcurriculumassignment',
      ),
  )

const canEditAssignment =
  computed(
    () =>
      can(
        'teaching.change_groupcurriculumassignment',
      ),
  )

const canDeleteAssignment =
  computed(
    () =>
      can(
        'teaching.delete_groupcurriculumassignment',
      ),
  )

const canCreateSemester =
  computed(
    () =>
      can(
        'teaching.add_groupsemester',
      ),
  )

const canEditSemester =
  computed(
    () =>
      can(
        'teaching.change_groupsemester',
      ),
  )

const canDeleteSemester =
  computed(
    () =>
      can(
        'teaching.delete_groupsemester',
      ),
  )

const assignmentColumns =
  computed<
    CrudColumn<GroupCurriculumAssignment>[]
  >(() => [
    {
      field:
        'student_group_code',

      header:
        t(
          'teachingSetup.groupCurricula.fields.group',
        ),

      sortable: true,

      sortField:
        'student_group__code',

      minWidth: '9rem',
    },

    {
      field:
        'curriculum_code',

      header:
        t(
          'teachingSetup.groupCurricula.fields.curriculum',
        ),

      minWidth: '12rem',
    },

    {
      field:
        'study_program_name',

      header:
        t(
          'teachingSetup.groupCurricula.fields.studyProgram',
        ),

      minWidth: '16rem',
    },

    {
      field:
        'study_form_name',

      header:
        t(
          'teachingSetup.groupCurricula.fields.studyForm',
        ),

      minWidth: '10rem',
    },

    {
      field:
        'start_academic_year_name',

      header:
        t(
          'teachingSetup.groupCurricula.fields.startYear',
        ),

      sortable: true,

      sortField:
        'start_academic_year__start_year',

      width: '10rem',
    },

    {
      field:
        'end_academic_year_name',

      header:
        t(
          'teachingSetup.groupCurricula.fields.endYear',
        ),

      bodySlot:
        'assignmentEndYear',

      width: '10rem',
    },

    {
      field:
        'is_primary',

      header:
        t(
          'teachingSetup.groupCurricula.fields.primary',
        ),

      bodySlot:
        'assignmentPrimary',

      width: '8rem',
    },

    {
      field:
        'is_active',

      header:
        t(
          'teachingSetup.common.status',
        ),

      bodySlot:
        'assignmentStatus',

      width: '8rem',
    },
  ])

const semesterColumns =
  computed<
    CrudColumn<GroupSemester>[]
  >(() => [
    {
      field:
        'student_group_code',

      header:
        t(
          'teachingSetup.groupSemesters.fields.group',
        ),

      minWidth: '9rem',
    },

    {
      field:
        'curriculum_code',

      header:
        t(
          'teachingSetup.groupSemesters.fields.curriculum',
        ),

      minWidth: '11rem',
    },

    {
      field:
        'academic_year_name',

      header:
        t(
          'teachingSetup.groupSemesters.fields.academicYear',
        ),

      sortable: true,

      sortField:
        'academic_year__start_year',

      width: '10rem',
    },

    {
      field:
        'semester_number',

      header:
        t(
          'teachingSetup.groupSemesters.fields.semesterNumber',
        ),

      sortable: true,

      bodySlot:
        'semesterNumber',

      width: '10rem',
    },

    {
      field:
        'academic_semester_name',

      header:
        t(
          'teachingSetup.groupSemesters.fields.academicSemester',
        ),

      minWidth: '10rem',
    },

    {
      field:
        'students_count',

      header:
        t(
          'teachingSetup.groupSemesters.fields.studentsCountShort',
        ),

      sortable: true,

      width: '8rem',

      align: 'center',
    },

    {
      field:
        'subgroup_count',

      header:
        t(
          'teachingSetup.groupSemesters.fields.subgroupCountShort',
        ),

      width: '8rem',

      align: 'center',
    },

    {
      field: 'status',

      header:
        t(
          'teachingSetup.groupSemesters.fields.status',
        ),

      bodySlot:
        'semesterStatus',

      width: '10rem',
    },

    {
      field:
        'is_active',

      header:
        t(
          'teachingSetup.common.active',
        ),

      bodySlot:
        'semesterActive',

      width: '8rem',
    },
  ])

const assignments =
  useCrudList<GroupCurriculumAssignment>(
    (params) =>
      groupCurriculaApi.list(
        params,
      ),

    {
      initialPageSize: 20,

      initialOrdering:
        '-start_academic_year__start_year,student_group__code',
    },
  )

const semesters =
  useCrudList<GroupSemester>(
    (params) =>
      groupSemestersApi.list(
        params,
      ),

    {
      initialPageSize: 20,

      initialOrdering:
        '-academic_year__start_year,semester_number',
    },
  )

const yearOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'teachingSetup.filters.allYears',
        ),
    },

    ...academicYears.value.map(
      (year) => ({
        value: year.id,

        label: year.name,
      }),
    ),
  ])

const booleanOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'teachingSetup.filters.all',
        ),
    },

    {
      value: true,

      label:
        t('common.yes'),
    },

    {
      value: false,

      label:
        t('common.no'),
    },
  ])

const activityOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'teachingSetup.filters.allStatuses',
        ),
    },

    {
      value: true,

      label:
        t(
          'teachingSetup.common.active',
        ),
    },

    {
      value: false,

      label:
        t(
          'teachingSetup.common.inactive',
        ),
    },
  ])

const semesterStatusOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'teachingSetup.filters.allStatuses',
        ),
    },

    {
      value: 'planned',

      label:
        t(
          'teachingSetup.groupSemesters.statuses.planned',
        ),
    },

    {
      value: 'active',

      label:
        t(
          'teachingSetup.groupSemesters.statuses.active',
        ),
    },

    {
      value: 'completed',

      label:
        t(
          'teachingSetup.groupSemesters.statuses.completed',
        ),
    },

    {
      value: 'cancelled',

      label:
        t(
          'teachingSetup.groupSemesters.statuses.cancelled',
        ),
    },
  ])

function clearErrors(): void {
  fieldErrors.value = {}

  nonFieldErrors.value = []

  generalError.value = ''
}

async function loadLookups(): Promise<void> {
  lookupLoading.value =
    true

  try {
    const [
      groupsResponse,
      curriculaResponse,
      yearsResponse,
      semestersResponse,
    ] = await Promise.all([
      getStudentGroups(),
      getCurricula(),
      getAcademicYears(),
      getAcademicSemesters(),
    ])

    studentGroups.value =
      groupsResponse.results

    curricula.value =
      curriculaResponse.results

    academicYears.value =
      yearsResponse.results

    academicSemesters.value =
      semestersResponse.results
  } catch (error) {
    const normalized =
      normalizeApiError(
        error,
        t('crud.loadError'),
      )

    toast.error(
      t('common.error'),
      normalized.message,
    )
  } finally {
    lookupLoading.value =
      false
  }
}

function openCreateAssignment(): void {
  selectedAssignment.value =
    null

  clearErrors()

  assignmentDialog.value =
    true
}

function openEditAssignment(
  record:
    GroupCurriculumAssignment,
): void {
  selectedAssignment.value =
    record

  clearErrors()

  assignmentDialog.value =
    true
}

async function saveAssignment(
  payload:
    GroupCurriculumPayload,
): Promise<void> {
  saving.value = true

  clearErrors()

  try {
    if (
      selectedAssignment.value
    ) {
      await groupCurriculaApi.update(
        selectedAssignment.value.id,
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.updated'),
      )
    } else {
      await groupCurriculaApi.create(
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.created'),
      )
    }

    assignmentDialog.value =
      false

    selectedAssignment.value =
      null

    await assignments.refresh()

    /*
     * GroupSemester form должен сразу
     * видеть новую связь группы и плана.
     */
    const response =
      await groupCurriculaApi.list({
        page_size: 500,
        is_active: true,
      })

    groupCurriculaLookup.value =
      response.results
  } catch (error) {
    const normalized =
      normalizeApiError(
        error,
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

const groupCurriculaLookup =
  ref<GroupCurriculumAssignment[]>(
    [],
  )

async function loadAssignmentLookup(): Promise<void> {
  try {
    const response =
      await groupCurriculaApi.list({
        page_size: 500,
        is_active: true,
      })

    groupCurriculaLookup.value =
      response.results
  } catch (error) {
    const normalized =
      normalizeApiError(error)

    toast.error(
      t('common.error'),
      normalized.message,
    )
  }
}

function archiveAssignment(
  record:
    GroupCurriculumAssignment,
): void {
  confirmDelete({
    header:
      t(
        'teachingSetup.groupCurricula.archiveTitle',
      ),

    message:
      t(
        'teachingSetup.groupCurricula.archiveConfirm',
        {
          group:
            record.student_group_code,

          curriculum:
            record.curriculum_code,
        },
      ),

    accept: async () => {
      try {
        await groupCurriculaApi.remove(
          record.id,
        )

        await Promise.all([
          assignments.refresh(),
          loadAssignmentLookup(),
        ])

        toast.success(
          t('common.success'),
          t(
            'teachingSetup.groupCurricula.archived',
          ),
        )
      } catch (error) {
        toast.error(
          t('common.error'),

          normalizeApiError(
            error,
          ).message,
        )
      }
    },
  })
}

function openCreateSemester(): void {
  selectedSemester.value =
    null

  clearErrors()

  semesterDialog.value =
    true
}

function openEditSemester(
  record: GroupSemester,
): void {
  selectedSemester.value =
    record

  clearErrors()

  semesterDialog.value =
    true
}

async function saveSemester(
  payload:
    GroupSemesterPayload,
): Promise<void> {
  saving.value = true

  clearErrors()

  try {
    if (
      selectedSemester.value
    ) {
      await groupSemestersApi.update(
        selectedSemester.value.id,
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.updated'),
      )
    } else {
      await groupSemestersApi.create(
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.created'),
      )
    }

    semesterDialog.value =
      false

    selectedSemester.value =
      null

    await semesters.refresh()
  } catch (error) {
    const normalized =
      normalizeApiError(
        error,
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

function archiveSemester(
  record: GroupSemester,
): void {
  confirmDelete({
    header:
      t(
        'teachingSetup.groupSemesters.archiveTitle',
      ),

    message:
      t(
        'teachingSetup.groupSemesters.archiveConfirm',
        {
          group:
            record.student_group_code,

          semester:
            record.semester_number,
        },
      ),

    accept: async () => {
      try {
        await groupSemestersApi.remove(
          record.id,
        )

        await semesters.refresh()

        toast.success(
          t('common.success'),
          t(
            'teachingSetup.groupSemesters.archived',
          ),
        )
      } catch (error) {
        toast.error(
          t('common.error'),

          normalizeApiError(
            error,
          ).message,
        )
      }
    },
  })
}

function semesterStatusSeverity(
  status: GroupSemesterStatus,
):
  | 'success'
  | 'info'
  | 'secondary'
  | 'danger' {
  if (status === 'active') {
    return 'success'
  }

  if (status === 'planned') {
    return 'info'
  }

  if (status === 'cancelled') {
    return 'danger'
  }

  return 'secondary'
}

async function applyAssignmentYear(): Promise<void> {
  assignments.setFilter(
    'start_academic_year',
    selectedAssignmentYear.value,
  )

  await assignments.load()
}

async function applyPrimary(): Promise<void> {
  assignments.setFilter(
    'is_primary',
    selectedPrimary.value,
  )

  await assignments.load()
}

async function applyAssignmentActive(): Promise<void> {
  assignments.setFilter(
    'is_active',
    selectedAssignmentActive.value,
  )

  await assignments.load()
}

async function resetAssignmentFilters(): Promise<void> {
  selectedAssignmentYear.value =
    null

  selectedPrimary.value =
    null

  selectedAssignmentActive.value =
    null

  assignments.clearFilters()

  await assignments.reset()
}

async function applySemesterYear(): Promise<void> {
  semesters.setFilter(
    'academic_year',
    selectedSemesterYear.value,
  )

  await semesters.load()
}

async function applySemesterStatus(): Promise<void> {
  semesters.setFilter(
    'status',
    selectedSemesterStatus.value,
  )

  await semesters.load()
}

async function applySemesterActive(): Promise<void> {
  semesters.setFilter(
    'is_active',
    selectedSemesterActive.value,
  )

  await semesters.load()
}

async function resetSemesterFilters(): Promise<void> {
  selectedSemesterYear.value =
    null

  selectedSemesterStatus.value =
    null

  selectedSemesterActive.value =
    null

  semesters.clearFilters()

  await semesters.reset()
}

onMounted(
  async () => {
    await Promise.all([
      assignments.load(),
      semesters.load(),
      loadLookups(),
      loadAssignmentLookup(),
    ])
  },
)
</script>

<template>
  <div
    class="teaching-setup-page"
  >
    <BasePageHeader
      :title="
        t(
          'teachingSetup.title',
        )
      "
      :description="
        t(
          'teachingSetup.description',
        )
      "
      icon="pi pi-sitemap"
    />

    <Tabs
      v-model:value="
        activeTab
      "
    >
      <TabList>
        <Tab value="curricula">
          {{
            t(
              'teachingSetup.tabs.groupCurricula',
            )
          }}
        </Tab>

        <Tab value="semesters">
          {{
            t(
              'teachingSetup.tabs.groupSemesters',
            )
          }}
        </Tab>
      </TabList>

      <TabPanels>
        <TabPanel value="curricula">
          <div
            class="
              teaching-setup-page__panel
            "
          >
            <BaseToolbar
              v-model:search="
                assignments
                  .searchInput.value
              "
              :show-create="false"
              :show-reset="true"
              :loading="
                assignments.loading.value ||
                lookupLoading
              "
              :search-placeholder="
                t(
                  'teachingSetup.groupCurricula.searchPlaceholder',
                )
              "
              @refresh="
                assignments.refresh
              "
              @reset="
                resetAssignmentFilters
              "
            >
              <template #start>
                <Button
                  v-if="
                    canCreateAssignment
                  "
                  :label="
                    t(
                      'teachingSetup.groupCurricula.create',
                    )
                  "
                  icon="pi pi-plus"
                  @click="
                    openCreateAssignment
                  "
                />
              </template>

              <template #center>
                <Select
                  v-model="
                    selectedAssignmentYear
                  "
                  :options="
                    yearOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="setup-filter"
                  @change="
                    applyAssignmentYear
                  "
                />

                <Select
                  v-model="
                    selectedPrimary
                  "
                  :options="
                    booleanOptions
                  "
                  option-label="label"
                  option-value="value"
                  :placeholder="
                    t(
                      'teachingSetup.filters.primary',
                    )
                  "
                  class="setup-filter"
                  @change="
                    applyPrimary
                  "
                />

                <Select
                  v-model="
                    selectedAssignmentActive
                  "
                  :options="
                    activityOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="setup-filter"
                  @change="
                    applyAssignmentActive
                  "
                />
              </template>
            </BaseToolbar>

            <BaseCard
              :padding="false"
            >
              <BaseDataTable
                :value="
                  assignments
                    .items.value
                "
                :columns="
                  assignmentColumns
                "
                :loading="
                  assignments
                    .loading.value
                "
                :error="
                  assignments
                    .error.value
                "
                :first="
                  assignments
                    .first.value
                "
                :rows="
                  assignments
                    .query.value
                    .pageSize
                "
                :total-records="
                  assignments
                    .totalRecords
                    .value
                "
                show-row-actions
                @page="
                  assignments
                    .handlePage
                "
                @sort="
                  assignments
                    .handleSort
                "
                @retry="
                  assignments.refresh
                "
              >
                <template
                  #assignmentEndYear="{ row }"
                >
                  {{
                    row.end_academic_year_name ||
                    '—'
                  }}
                </template>

                <template
                  #assignmentPrimary="{ row }"
                >
                  <Tag
                    :value="
                      row.is_primary
                        ? t('common.yes')
                        : t('common.no')
                    "
                    :severity="
                      row.is_primary
                        ? 'info'
                        : 'secondary'
                    "
                  />
                </template>

                <template
                  #assignmentStatus="{ row }"
                >
                  <Tag
                    :value="
                      row.is_active
                        ? t(
                            'teachingSetup.common.active',
                          )
                        : t(
                            'teachingSetup.common.inactive',
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
                      canEditAssignment
                    "
                    icon="pi pi-pencil"
                    text
                    rounded
                    @click.stop="
                      openEditAssignment(
                        row,
                      )
                    "
                  />

                  <Button
                    v-if="
                      canDeleteAssignment
                    "
                    icon="pi pi-box"
                    severity="danger"
                    text
                    rounded
                    @click.stop="
                      archiveAssignment(
                        row,
                      )
                    "
                  />
                </template>
              </BaseDataTable>
            </BaseCard>
          </div>
        </TabPanel>

        <TabPanel value="semesters">
          <div
            class="
              teaching-setup-page__panel
            "
          >
            <BaseToolbar
              v-model:search="
                semesters
                  .searchInput.value
              "
              :show-create="false"
              :show-reset="true"
              :loading="
                semesters.loading.value ||
                lookupLoading
              "
              :search-placeholder="
                t(
                  'teachingSetup.groupSemesters.searchPlaceholder',
                )
              "
              @refresh="
                semesters.refresh
              "
              @reset="
                resetSemesterFilters
              "
            >
              <template #start>
                <Button
                  v-if="
                    canCreateSemester
                  "
                  :label="
                    t(
                      'teachingSetup.groupSemesters.create',
                    )
                  "
                  icon="pi pi-plus"
                  @click="
                    openCreateSemester
                  "
                />
              </template>

              <template #center>
                <Select
                  v-model="
                    selectedSemesterYear
                  "
                  :options="
                    yearOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="setup-filter"
                  @change="
                    applySemesterYear
                  "
                />

                <Select
                  v-model="
                    selectedSemesterStatus
                  "
                  :options="
                    semesterStatusOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="setup-filter"
                  @change="
                    applySemesterStatus
                  "
                />

                <Select
                  v-model="
                    selectedSemesterActive
                  "
                  :options="
                    activityOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="setup-filter"
                  @change="
                    applySemesterActive
                  "
                />
              </template>
            </BaseToolbar>

            <BaseCard
              :padding="false"
            >
              <BaseDataTable
                :value="
                  semesters.items.value
                "
                :columns="
                  semesterColumns
                "
                :loading="
                  semesters
                    .loading.value
                "
                :error="
                  semesters
                    .error.value
                "
                :first="
                  semesters
                    .first.value
                "
                :rows="
                  semesters
                    .query.value
                    .pageSize
                "
                :total-records="
                  semesters
                    .totalRecords
                    .value
                "
                show-row-actions
                @page="
                  semesters
                    .handlePage
                "
                @sort="
                  semesters
                    .handleSort
                "
                @retry="
                  semesters.refresh
                "
              >
                <template
                  #semesterNumber="{ row }"
                >
                  <div
                    class="
                      semester-cell
                    "
                  >
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
                              'teachingSetup.seasons.autumn',
                            )
                          : t(
                              'teachingSetup.seasons.spring',
                            )
                      }}
                    </small>
                  </div>
                </template>

                <template
                  #semesterStatus="{ row }"
                >
                  <Tag
                    :value="
                      t(
                        `teachingSetup.groupSemesters.statuses.${row.status}`,
                      )
                    "
                    :severity="
                      semesterStatusSeverity(
                        row.status,
                      )
                    "
                  />
                </template>

                <template
                  #semesterActive="{ row }"
                >
                  <Tag
                    :value="
                      row.is_active
                        ? t('common.yes')
                        : t('common.no')
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
                      canEditSemester
                    "
                    icon="pi pi-pencil"
                    text
                    rounded
                    @click.stop="
                      openEditSemester(
                        row,
                      )
                    "
                  />

                  <Button
                    v-if="
                      canDeleteSemester
                    "
                    icon="pi pi-box"
                    severity="danger"
                    text
                    rounded
                    @click.stop="
                      archiveSemester(
                        row,
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

    <GroupCurriculumFormDialog
      v-model="
        assignmentDialog
      "
      :record="
        selectedAssignment
      "
      :student-groups="
        studentGroups
      "
      :curricula="
        curricula
      "
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
        generalError
      "
      @submit="
        saveAssignment
      "
    />

    <GroupSemesterFormDialog
      v-model="
        semesterDialog
      "
      :record="
        selectedSemester
      "
      :group-curricula="
        groupCurriculaLookup
      "
      :curricula="
        curricula
      "
      :student-groups="
        studentGroups
      "
      :academic-years="
        academicYears
      "
      :academic-semesters="
        academicSemesters
      "
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
        saveSemester
      "
    />
  </div>
</template>

<style scoped>
.teaching-setup-page {
  display: grid;
  gap: 1rem;
}

.teaching-setup-page__panel {
  display: grid;
  gap: 1rem;
}

.setup-filter {
  width: 14rem;
}

.semester-cell {
  display: grid;
  gap: 0.1rem;
  text-align: center;
}

.semester-cell small {
  color:
    var(--app-text-muted);
  font-size: 0.68rem;
}

:deep(.p-tabpanels) {
  padding:
    1rem 0 0;
}

@media (max-width: 991px) {
  .setup-filter {
    width: 100%;
  }
}
</style>
