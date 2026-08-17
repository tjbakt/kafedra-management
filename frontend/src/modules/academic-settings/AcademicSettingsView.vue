<script setup lang="ts">
import Button from 'primevue/button'
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

import AcademicSemesterDialog from '@/modules/academic-settings/components/AcademicSemesterDialog.vue'
import AcademicYearDialog from '@/modules/academic-settings/components/AcademicYearDialog.vue'
import AcademicYearStatusDialog from '@/modules/academic-settings/components/AcademicYearStatusDialog.vue'
import AcademicWorkloadNormsForm from '@/modules/academic-settings/components/AcademicWorkloadNormsForm.vue'
import EducationDurationDialog from '@/modules/academic-settings/components/EducationDurationDialog.vue'
import LocalizedReferenceDialog from '@/modules/academic-settings/components/LocalizedReferenceDialog.vue'

import {
  academicSemestersApi,
  academicYearsApi,
  closeAcademicYear,
  educationDurationsApi,
  educationLevelsApi,
  getAllAcademicYears,
  getAllEducationLevels,
  getAllStudyForms,
  reopenAcademicYear,
  studyFormsApi,
} from '@/modules/academic-settings/api'

import type {
  AcademicSemester,
  AcademicSemesterPayload,
  AcademicYear,
  AcademicYearPayload,
  EducationDuration,
  EducationDurationPayload,
  EducationLevel,
  EducationLevelPayload,
  StudyForm,
  StudyFormPayload,
} from '@/modules/academic-settings/types'

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

const localeStore =
  useLocaleStore()

const toast =
  useAppToast()

const {
  confirmDelete,
} = useAppConfirm()

const {
  can,
} = usePermissions()

const activeTab =
  ref('years')

const lookupsYears =
  ref<AcademicYear[]>([])

const lookupLevels =
  ref<EducationLevel[]>([])

const lookupForms =
  ref<StudyForm[]>([])

const selectedYear =
  ref<AcademicYear | null>(null)

const selectedLevel =
  ref<EducationLevel | null>(null)

const selectedStudyForm =
  ref<StudyForm | null>(null)

const selectedDuration =
  ref<EducationDuration | null>(null)

const selectedSemester =
  ref<AcademicSemester | null>(null)

const yearDialog =
  ref(false)

const levelDialog =
  ref(false)

const formDialog =
  ref(false)

const durationDialog =
  ref(false)

const semesterDialog =
  ref(false)

const statusDialog =
  ref(false)

const statusOperation =
  ref<'close' | 'reopen'>(
    'close',
  )

const saving =
  ref(false)

const fieldErrors =
  ref<FieldErrors>({})

const nonFieldErrors =
  ref<string[]>([])

const generalError =
  ref('')

const canManageYears =
  computed(
    () =>
      can(
        'academics.change_academicyear',
      ),
  )

function localizedName(
  record:
    | EducationLevel
    | StudyForm,
): string {
  if (
    localeStore.locale === 'uz'
  ) {
    return (
      record.name_uz ||
      record.name_ru
    )
  }

  return (
    record.name_ru ||
    record.name_uz
  )
}

function clearErrors(): void {
  fieldErrors.value = {}
  nonFieldErrors.value = []
  generalError.value = ''
}

const yearColumns =
  computed<
    CrudColumn<AcademicYear>[]
  >(() => [
    {
      field: 'name',
      header:
        t(
          'academicSettings.academicYears.fields.name',
        ),
      sortable: true,
      sortField: 'start_year',
    },

    {
      field: 'status',
      header:
        t(
          'academicSettings.academicYears.fields.status',
        ),
      bodySlot: 'yearStatus',
    },

    {
      field: 'is_current',
      header:
        t(
          'academicSettings.academicYears.fields.current',
        ),
      bodySlot: 'yearCurrent',
    },

    {
      field: 'is_active',
      header:
        t(
          'academicSettings.common.active',
        ),
      bodySlot: 'yearActive',
    },
  ])

const referenceColumns =
  computed<
    CrudColumn<
      EducationLevel | StudyForm
    >[]
  >(() => [
    {
      field: 'code',
      header:
        t(
          'academicSettings.common.code',
        ),
      sortable: true,
    },

    {
      field: 'display_name',
      header:
        t(
          'academicSettings.common.name',
        ),
      bodySlot:
        'localizedName',
    },

    {
      field: 'sort_order',
      header:
        t(
          'academicSettings.common.sortOrder',
        ),
      sortable: true,
    },

    {
      field: 'is_active',
      header:
        t(
          'academicSettings.common.active',
        ),
      bodySlot: 'active',
    },
  ])

const durationColumns =
  computed<
    CrudColumn<EducationDuration>[]
  >(() => [
    {
      field:
        'education_level_name',

      header:
        t(
          'academicSettings.educationDurations.fields.level',
        ),
    },

    {
      field:
        'study_form_name',

      header:
        t(
          'academicSettings.educationDurations.fields.studyForm',
        ),
    },

    {
      field:
        'semesters_count',

      header:
        t(
          'academicSettings.educationDurations.fields.semesters',
        ),

      sortable: true,
    },

    {
      field:
        'duration_months',

      header:
        t(
          'academicSettings.educationDurations.fields.months',
        ),

      sortable: true,
    },

    {
      field: 'is_active',

      header:
        t(
          'academicSettings.common.active',
        ),

      bodySlot: 'active',
    },
  ])

const semesterColumns =
  computed<
    CrudColumn<AcademicSemester>[]
  >(() => [
    {
      field:
        'academic_year_name',

      header:
        t(
          'academicSettings.semesters.fields.academicYear',
        ),
    },

    {
      field: 'season',

      header:
        t(
          'academicSettings.semesters.fields.season',
        ),

      bodySlot: 'season',
    },

    {
      field:
        'start_date',

      header:
        t(
          'academicSettings.semesters.fields.startDate',
        ),

      sortable: true,
    },

    {
      field:
        'end_date',

      header:
        t(
          'academicSettings.semesters.fields.endDate',
        ),

      sortable: true,
    },

    {
      field:
        'is_current',

      header:
        t(
          'academicSettings.semesters.fields.current',
        ),

      bodySlot:
        'semesterCurrent',
    },

    {
      field:
        'is_active',

      header:
        t(
          'academicSettings.common.active',
        ),

      bodySlot: 'active',
    },
  ])

const years =
  useCrudList<AcademicYear>(
    (params) =>
      academicYearsApi.list(
        params,
      ),
    {
      initialPageSize: 20,
      initialOrdering:
        '-start_year',
    },
  )

const levels =
  useCrudList<EducationLevel>(
    (params) =>
      educationLevelsApi.list(
        params,
      ),
    {
      initialPageSize: 20,
      initialOrdering:
        'sort_order,name_ru',
    },
  )

const forms =
  useCrudList<StudyForm>(
    (params) =>
      studyFormsApi.list(params),
    {
      initialPageSize: 20,
      initialOrdering:
        'sort_order,name_ru',
    },
  )

const durations =
  useCrudList<EducationDuration>(
    (params) =>
      educationDurationsApi.list(
        params,
      ),
    {
      initialPageSize: 20,
    },
  )

const semesters =
  useCrudList<AcademicSemester>(
    (params) =>
      academicSemestersApi.list(
        params,
      ),
    {
      initialPageSize: 20,
      initialOrdering:
        '-start_date',
    },
  )

async function refreshLookups(): Promise<void> {
  const [
    yearResponse,
    levelResponse,
    formResponse,
  ] = await Promise.all([
    getAllAcademicYears(),
    getAllEducationLevels(),
    getAllStudyForms(),
  ])

  lookupsYears.value =
    yearResponse.results

  lookupLevels.value =
    levelResponse.results

  lookupForms.value =
    formResponse.results
}

function setFormError(
  error: unknown,
): void {
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
}

async function saveYear(
  payload: AcademicYearPayload,
): Promise<void> {
  saving.value = true
  clearErrors()

  try {
    if (selectedYear.value) {
      await academicYearsApi.update(
        selectedYear.value.id,
        payload,
      )
    } else {
      await academicYearsApi.create(
        payload,
      )
    }

    yearDialog.value = false

    await Promise.all([
      years.refresh(),
      refreshLookups(),
    ])

    toast.success(
      t('common.success'),
      selectedYear.value
        ? t('crud.updated')
        : t('crud.created'),
    )
  } catch (error) {
    setFormError(error)
  } finally {
    saving.value = false
  }
}

async function saveLevel(
  payload: {
    code: string
    name_ru: string
    name_uz: string
    is_active: boolean
    sort_order: number
  },
): Promise<void> {
  saving.value = true

  try {
    if (selectedLevel.value) {
      await educationLevelsApi.update(
        selectedLevel.value.id,
        payload as EducationLevelPayload,
      )
    } else {
      await educationLevelsApi.create(
        payload as EducationLevelPayload,
      )
    }

    levelDialog.value = false

    await Promise.all([
      levels.refresh(),
      refreshLookups(),
    ])
  } catch (error) {
    toast.error(
      t('common.error'),
      normalizeApiError(error)
        .message,
    )
  } finally {
    saving.value = false
  }
}

async function saveStudyForm(
  payload: {
    code: string
    name_ru: string
    name_uz: string
    is_active: boolean
    sort_order: number
  },
): Promise<void> {
  saving.value = true

  try {
    if (
      selectedStudyForm.value
    ) {
      await studyFormsApi.update(
        selectedStudyForm.value.id,
        payload as StudyFormPayload,
      )
    } else {
      await studyFormsApi.create(
        payload as StudyFormPayload,
      )
    }

    formDialog.value = false

    await Promise.all([
      forms.refresh(),
      refreshLookups(),
    ])
  } catch (error) {
    toast.error(
      t('common.error'),
      normalizeApiError(error)
        .message,
    )
  } finally {
    saving.value = false
  }
}

async function saveDuration(
  payload: EducationDurationPayload,
): Promise<void> {
  saving.value = true

  try {
    if (
      selectedDuration.value
    ) {
      await educationDurationsApi.update(
        selectedDuration.value.id,
        payload,
      )
    } else {
      await educationDurationsApi.create(
        payload,
      )
    }

    durationDialog.value = false

    await durations.refresh()
  } catch (error) {
    toast.error(
      t('common.error'),
      normalizeApiError(error)
        .message,
    )
  } finally {
    saving.value = false
  }
}

async function saveSemester(
  payload: AcademicSemesterPayload,
): Promise<void> {
  saving.value = true

  try {
    if (
      selectedSemester.value
    ) {
      await academicSemestersApi.update(
        selectedSemester.value.id,
        payload,
      )
    } else {
      await academicSemestersApi.create(
        payload,
      )
    }

    semesterDialog.value = false

    await semesters.refresh()
  } catch (error) {
    toast.error(
      t('common.error'),
      normalizeApiError(error)
        .message,
    )
  } finally {
    saving.value = false
  }
}

function archive<
  T extends {
    id: number
  },
>(
  api: {
    remove:
      (
        id: number,
      ) => Promise<unknown>
  },
  record: T,
  refresh: () => Promise<void>,
): void {
  confirmDelete({
    header:
      t('crud.deleteTitle'),

    message:
      t(
        'academicSettings.archiveConfirm',
      ),

    accept: async () => {
      try {
        await api.remove(
          record.id,
        )

        await refresh()

        await refreshLookups()

        toast.success(
          t('common.success'),
          t('crud.deleted'),
        )
      } catch (error) {
        toast.error(
          t('common.error'),
          normalizeApiError(error)
            .message,
        )
      }
    },
  })
}

async function executeYearStatus(
  value: string,
): Promise<void> {
  if (!selectedYear.value) {
    return
  }

  saving.value = true

  try {
    if (
      statusOperation.value ===
      'close'
    ) {
      await closeAcademicYear(
        selectedYear.value.id,
        value,
      )
    } else {
      await reopenAcademicYear(
        selectedYear.value.id,
        value,
      )
    }

    statusDialog.value =
      false

    await Promise.all([
      years.refresh(),
      refreshLookups(),
    ])

    toast.success(
      t('common.success'),
      t(
        'academicSettings.academicYears.operationSuccess',
      ),
    )
  } catch (error) {
    toast.error(
      t('common.error'),
      normalizeApiError(error)
        .message,
    )
  } finally {
    saving.value = false
  }
}

function openClose(
  year: AcademicYear,
): void {
  selectedYear.value = year
  statusOperation.value =
    'close'

  statusDialog.value = true
}

function openReopen(
  year: AcademicYear,
): void {
  selectedYear.value = year
  statusOperation.value =
    'reopen'

  statusDialog.value = true
}

function seasonLabel(
  value: string,
): string {
  return value === 'autumn'
    ? t(
        'academicSettings.semesters.seasons.autumn',
      )
    : t(
        'academicSettings.semesters.seasons.spring',
      )
}

onMounted(async () => {
  await Promise.all([
    years.load(),
    levels.load(),
    forms.load(),
    durations.load(),
    semesters.load(),
    refreshLookups(),
  ])
})
</script>

<template>
  <div
    class="
      academic-settings-page
    "
  >
    <BasePageHeader
      :title="
        t(
          'academicSettings.title',
        )
      "
      :description="
        t(
          'academicSettings.description',
        )
      "
      icon="pi pi-graduation-cap"
    />

    <Tabs
      v-model:value="
        activeTab
      "
    >
      <TabList>
        <Tab value="years">
          {{
            t(
              'academicSettings.tabs.years',
            )
          }}
        </Tab>

        <Tab value="levels">
          {{
            t(
              'academicSettings.tabs.levels',
            )
          }}
        </Tab>

        <Tab value="forms">
          {{
            t(
              'academicSettings.tabs.forms',
            )
          }}
        </Tab>

        <Tab value="durations">
          {{
            t(
              'academicSettings.tabs.durations',
            )
          }}
        </Tab>

        <Tab value="semesters">
          {{
            t('academicSettings.tabs.semesters',)
          }}
        </Tab>
        <Tab value="workload-norms">
          {{
            t('academicSettings.tabs.workloadNorms',)
          }}
        </Tab>
      </TabList>

      <TabPanels>
        <TabPanel value="years">
          <BaseToolbar
            v-model:search="
              years.searchInput.value
            "
            :show-create="false"
            :loading="
              years.loading.value
            "
            @refresh="
              years.refresh
            "
          >
            <template #start>
              <Button
                v-can="
                  'academics.add_academicyear'
                "
                :label="
                  t('common.create')
                "
                icon="pi pi-plus"
                @click="
                  selectedYear = null;
                  clearErrors();
                  yearDialog = true
                "
              />
            </template>
          </BaseToolbar>

          <BaseCard
            :padding="false"
          >
            <BaseDataTable
              :value="
                years.items.value
              "
              :columns="
                yearColumns
              "
              :loading="
                years.loading.value
              "
              :error="
                years.error.value
              "
              :first="
                years.first.value
              "
              :rows="
                years.query.value
                  .pageSize
              "
              :total-records="
                years.totalRecords.value
              "
              show-row-actions
              @page="
                years.handlePage
              "
              @sort="
                years.handleSort
              "
              @retry="
                years.refresh
              "
            >
              <template
                #yearStatus="{ row }"
              >
                <Tag
                  :value="
                    row.is_closed
                      ? t(
                          'academicSettings.academicYears.closed',
                        )
                      : t(
                          'academicSettings.academicYears.open',
                        )
                  "
                  :severity="
                    row.is_closed
                      ? 'secondary'
                      : 'success'
                  "
                />
              </template>

              <template
                #yearCurrent="{ row }"
              >
                <Tag
                  :value="
                    row.is_current
                      ? t('common.yes')
                      : t('common.no')
                  "
                  :severity="
                    row.is_current
                      ? 'info'
                      : 'secondary'
                  "
                />
              </template>

              <template
                #yearActive="{ row }"
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
                    canManageYears &&
                    !row.is_closed
                  "
                  icon="pi pi-pencil"
                  text
                  rounded
                  @click.stop="
                    selectedYear = row;
                    clearErrors();
                    yearDialog = true
                  "
                />

                <Button
                  v-if="
                    canManageYears &&
                    !row.is_closed
                  "
                  v-tooltip.bottom="
                    t(
                      'academicSettings.academicYears.close',
                    )
                  "
                  icon="pi pi-lock"
                  severity="warn"
                  text
                  rounded
                  @click.stop="
                    openClose(row)
                  "
                />

                <Button
                  v-if="
                    canManageYears &&
                    row.is_closed
                  "
                  v-tooltip.bottom="
                    t(
                      'academicSettings.academicYears.reopen',
                    )
                  "
                  icon="pi pi-lock-open"
                  severity="info"
                  text
                  rounded
                  @click.stop="
                    openReopen(row)
                  "
                />
              </template>
            </BaseDataTable>
          </BaseCard>
        </TabPanel>

        <TabPanel value="levels">
          <BaseToolbar
            v-model:search="
              levels.searchInput.value
            "
            :show-create="false"
            :loading="
              levels.loading.value
            "
            @refresh="
              levels.refresh
            "
          >
            <template #start>
              <Button
                v-can="
                  'academics.add_educationlevel'
                "
                :label="
                  t('common.create')
                "
                icon="pi pi-plus"
                @click="
                  selectedLevel = null;
                  levelDialog = true
                "
              />
            </template>
          </BaseToolbar>

          <BaseCard
            :padding="false"
          >
            <BaseDataTable
              :value="
                levels.items.value
              "
              :columns="
                referenceColumns
              "
              :loading="
                levels.loading.value
              "
              :error="
                levels.error.value
              "
              :first="
                levels.first.value
              "
              :rows="
                levels.query.value
                  .pageSize
              "
              :total-records="
                levels.totalRecords.value
              "
              show-row-actions
              @page="
                levels.handlePage
              "
              @sort="
                levels.handleSort
              "
              @retry="
                levels.refresh
              "
            >
              <template
                #localizedName="{ row }"
              >
                {{
                  localizedName(row)
                }}
              </template>

              <template
                #active="{ row }"
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
                  v-can="
                    'academics.change_educationlevel'
                  "
                  icon="pi pi-pencil"
                  text
                  rounded
                  @click.stop="
                    selectedLevel = row;
                    levelDialog = true
                  "
                />

                <Button
                  v-can="
                    'academics.delete_educationlevel'
                  "
                  icon="pi pi-box"
                  severity="danger"
                  text
                  rounded
                  @click.stop="
                    archive(
                      educationLevelsApi,
                      row,
                      levels.refresh,
                    )
                  "
                />
              </template>
            </BaseDataTable>
          </BaseCard>
        </TabPanel>

        <TabPanel value="forms">
          <BaseToolbar
            v-model:search="
              forms.searchInput.value
            "
            :show-create="false"
            :loading="
              forms.loading.value
            "
            @refresh="
              forms.refresh
            "
          >
            <template #start>
              <Button
                v-can="
                  'academics.add_studyform'
                "
                :label="
                  t('common.create')
                "
                icon="pi pi-plus"
                @click="
                  selectedStudyForm = null;
                  formDialog = true
                "
              />
            </template>
          </BaseToolbar>

          <BaseCard
            :padding="false"
          >
            <BaseDataTable
              :value="
                forms.items.value
              "
              :columns="
                referenceColumns
              "
              :loading="
                forms.loading.value
              "
              :error="
                forms.error.value
              "
              :first="
                forms.first.value
              "
              :rows="
                forms.query.value
                  .pageSize
              "
              :total-records="
                forms.totalRecords.value
              "
              show-row-actions
              @page="
                forms.handlePage
              "
              @sort="
                forms.handleSort
              "
              @retry="
                forms.refresh
              "
            >
              <template
                #localizedName="{ row }"
              >
                {{
                  localizedName(row)
                }}
              </template>

              <template
                #active="{ row }"
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
                  v-can="
                    'academics.change_studyform'
                  "
                  icon="pi pi-pencil"
                  text
                  rounded
                  @click.stop="
                    selectedStudyForm = row;
                    formDialog = true
                  "
                />

                <Button
                  v-can="
                    'academics.delete_studyform'
                  "
                  icon="pi pi-box"
                  severity="danger"
                  text
                  rounded
                  @click.stop="
                    archive(
                      studyFormsApi,
                      row,
                      forms.refresh,
                    )
                  "
                />
              </template>
            </BaseDataTable>
          </BaseCard>
        </TabPanel>

        <TabPanel value="durations">
          <BaseToolbar
            :show-search="false"
            :show-create="false"
            :loading="
              durations.loading.value
            "
            @refresh="
              durations.refresh
            "
          >
            <template #start>
              <Button
                v-can="
                  'academics.add_educationduration'
                "
                :label="
                  t('common.create')
                "
                icon="pi pi-plus"
                @click="
                  selectedDuration = null;
                  durationDialog = true
                "
              />
            </template>
          </BaseToolbar>

          <BaseCard
            :padding="false"
          >
            <BaseDataTable
              :value="
                durations.items.value
              "
              :columns="
                durationColumns
              "
              :loading="
                durations.loading.value
              "
              :error="
                durations.error.value
              "
              :first="
                durations.first.value
              "
              :rows="
                durations.query.value
                  .pageSize
              "
              :total-records="
                durations.totalRecords.value
              "
              show-row-actions
              @page="
                durations.handlePage
              "
              @sort="
                durations.handleSort
              "
              @retry="
                durations.refresh
              "
            >
              <template
                #active="{ row }"
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
                  v-can="
                    'academics.change_educationduration'
                  "
                  icon="pi pi-pencil"
                  text
                  rounded
                  @click.stop="
                    selectedDuration = row;
                    durationDialog = true
                  "
                />

                <Button
                  v-can="
                    'academics.delete_educationduration'
                  "
                  icon="pi pi-box"
                  severity="danger"
                  text
                  rounded
                  @click.stop="
                    archive(
                      educationDurationsApi,
                      row,
                      durations.refresh,
                    )
                  "
                />
              </template>
            </BaseDataTable>
          </BaseCard>
        </TabPanel>

        <TabPanel value="semesters">
          <BaseToolbar
            :show-search="false"
            :show-create="false"
            :loading="
              semesters.loading.value
            "
            @refresh="
              semesters.refresh
            "
          >
            <template #start>
              <Button
                v-can="
                  'academics.add_academicsemester'
                "
                :label="
                  t('common.create')
                "
                icon="pi pi-plus"
                @click="
                  selectedSemester = null;
                  semesterDialog = true
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
                semesters.loading.value
              "
              :error="
                semesters.error.value
              "
              :first="
                semesters.first.value
              "
              :rows="
                semesters.query.value
                  .pageSize
              "
              :total-records="
                semesters.totalRecords.value
              "
              show-row-actions
              @page="
                semesters.handlePage
              "
              @sort="
                semesters.handleSort
              "
              @retry="
                semesters.refresh
              "
            >
              <template
                #season="{ row }"
              >
                {{
                  seasonLabel(
                    row.season,
                  )
                }}
              </template>

              <template
                #semesterCurrent="{ row }"
              >
                <Tag
                  :value="
                    row.is_current
                      ? t('common.yes')
                      : t('common.no')
                  "
                  :severity="
                    row.is_current
                      ? 'info'
                      : 'secondary'
                  "
                />
              </template>

              <template
                #active="{ row }"
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
                  v-can="
                    'academics.change_academicsemester'
                  "
                  icon="pi pi-pencil"
                  text
                  rounded
                  @click.stop="
                    selectedSemester = row;
                    semesterDialog = true
                  "
                />

                <Button
                  v-can="
                    'academics.delete_academicsemester'
                  "
                  icon="pi pi-box"
                  severity="danger"
                  text
                  rounded
                  @click.stop="
                    archive(
                      academicSemestersApi,
                      row,
                      semesters.refresh,
                    )
                  "
                />
              </template>
            </BaseDataTable>
          </BaseCard>
        </TabPanel>

        <TabPanel value="workload-norms">
          <AcademicWorkloadNormsForm/>
        </TabPanel>

      </TabPanels>
    </Tabs>

    <AcademicYearDialog
      v-model="yearDialog"
      :academic-year="
        selectedYear
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
      @submit="saveYear"
    />

    <AcademicYearStatusDialog
      v-model="statusDialog"
      :academic-year="
        selectedYear
      "
      :operation="
        statusOperation
      "
      :loading="saving"
      @submit="
        executeYearStatus
      "
    />

    <LocalizedReferenceDialog
      v-model="levelDialog"
      kind="education-level"
      :record="
        selectedLevel
      "
      :loading="saving"
      @submit="saveLevel"
    />

    <LocalizedReferenceDialog
      v-model="formDialog"
      kind="study-form"
      :record="
        selectedStudyForm
      "
      :loading="saving"
      @submit="
        saveStudyForm
      "
    />

    <EducationDurationDialog
      v-model="durationDialog"
      :record="
        selectedDuration
      "
      :education-levels="
        lookupLevels
      "
      :study-forms="
        lookupForms
      "
      :loading="saving"
      @submit="
        saveDuration
      "
    />

    <AcademicSemesterDialog
      v-model="semesterDialog"
      :record="
        selectedSemester
      "
      :academic-years="
        lookupsYears
      "
      :loading="saving"
      @submit="
        saveSemester
      "
    />
  </div>
</template>

<style scoped>
.academic-settings-page {
  display: grid;
  gap: 1rem;
}

:deep(.p-tabpanels) {
  padding:
    1rem 0 0;
}

:deep(.p-tabpanel) {
  display: grid;
  gap: 1rem;
}
</style>
