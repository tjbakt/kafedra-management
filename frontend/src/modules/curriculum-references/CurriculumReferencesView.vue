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

import DisciplineFormDialog from '@/modules/curriculum-references/components/DisciplineFormDialog.vue'
import WorkloadTypeFormDialog from '@/modules/curriculum-references/components/WorkloadTypeFormDialog.vue'

import {
  disciplinesApi,
  getDepartments,
  workloadTypesApi,
} from '@/modules/curriculum-references/api'

import type {
  CalculationMode,
  DepartmentLookup,
  Discipline,
  DisciplinePayload,
  SelectOption,
  WorkloadType,
  WorkloadTypePayload,
} from '@/modules/curriculum-references/types'

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
  ref('disciplines')

const departments =
  ref<DepartmentLookup[]>([])

const selectedDiscipline =
  ref<Discipline | null>(null)

const selectedWorkloadType =
  ref<WorkloadType | null>(null)

const disciplineDialogVisible =
  ref(false)

const workloadTypeDialogVisible =
  ref(false)

const saving =
  ref(false)

const lookupsLoading =
  ref(false)

const selectedDepartment =
  ref<number | null>(null)

const selectedDisciplineActive =
  ref<boolean | null>(null)

const selectedCalculationMode =
  ref<CalculationMode | null>(
    null,
  )

const selectedClassroom =
  ref<boolean | null>(null)

const selectedTeachingLoad =
  ref<boolean | null>(null)

const selectedWorkloadActive =
  ref<boolean | null>(null)

const fieldErrors =
  ref<FieldErrors>({})

const nonFieldErrors =
  ref<string[]>([])

const generalFormError =
  ref('')

const canCreateDiscipline =
  computed(
    () =>
      can(
        'curriculum.add_discipline',
      ),
  )

const canEditDiscipline =
  computed(
    () =>
      can(
        'curriculum.change_discipline',
      ),
  )

const canDeleteDiscipline =
  computed(
    () =>
      can(
        'curriculum.delete_discipline',
      ),
  )

const canCreateWorkloadType =
  computed(
    () =>
      can(
        'curriculum.add_workloadtype',
      ),
  )

const canEditWorkloadType =
  computed(
    () =>
      can(
        'curriculum.change_workloadtype',
      ),
  )

const canDeleteWorkloadType =
  computed(
    () =>
      can(
        'curriculum.delete_workloadtype',
      ),
  )

function localizedName(
  ru: string | null | undefined,
  uz: string | null | undefined,
): string {
  if (
    localeStore.locale === 'uz'
  ) {
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

function disciplineName(
  discipline: Discipline,
): string {
  return localizedName(
    discipline.name_ru,
    discipline.name_uz,
  )
}

function workloadTypeName(
  workloadType: WorkloadType,
): string {
  return localizedName(
    workloadType.name_ru,
    workloadType.name_uz,
  )
}

const booleanOptions =
  computed(() => [
    {
      value: null,
      label:
        t(
          'curriculumReferences.filters.all',
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

const statusOptions =
  computed(() => [
    {
      value: null,
      label:
        t(
          'curriculumReferences.filters.allStatuses',
        ),
    },
    {
      value: true,
      label:
        t(
          'curriculumReferences.common.active',
        ),
    },
    {
      value: false,
      label:
        t(
          'curriculumReferences.common.inactive',
        ),
    },
  ])

const departmentOptions =
  computed<
    SelectOption<number | null>[]
  >(() => [
    {
      value: null,

      label:
        t(
          'curriculumReferences.filters.allDepartments',
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

        description:
          department.faculty_name,
      }),
    ),
  ])

const calculationModeOptions =
  computed<
    SelectOption<
      CalculationMode | null
    >[]
  >(() => [
    {
      value: null,

      label:
        t(
          'curriculumReferences.filters.allCalculationModes',
        ),
    },
    {
      value: 'fixed',

      label:
        t(
          'curriculumReferences.workloadTypes.calculationModes.fixed',
        ),
    },
    {
      value: 'per_group',

      label:
        t(
          'curriculumReferences.workloadTypes.calculationModes.perGroup',
        ),
    },
    {
      value: 'per_subgroup',

      label:
        t(
          'curriculumReferences.workloadTypes.calculationModes.perSubgroup',
        ),
    },
    {
      value: 'per_student',

      label:
        t(
          'curriculumReferences.workloadTypes.calculationModes.perStudent',
        ),
    },
  ])

const disciplineColumns =
  computed<
    CrudColumn<Discipline>[]
  >(() => [
    {
      field: 'code',

      header:
        t(
          'curriculumReferences.disciplines.fields.code',
        ),

      sortable: true,

      minWidth: '9rem',
    },

    {
      field: 'display_name',

      header:
        t(
          'curriculumReferences.disciplines.fields.name',
        ),

      sortable: true,

      sortField:
        localeStore.locale ===
        'uz'
          ? 'name_uz'
          : 'name_ru',

      bodySlot: 'disciplineName',

      minWidth: '18rem',
    },

    {
      field:
        'default_department_name',

      header:
        t(
          'curriculumReferences.disciplines.fields.department',
        ),

      bodySlot:
        'disciplineDepartment',

      minWidth: '15rem',
    },

    {
      field: 'sort_order',

      header:
        t(
          'curriculumReferences.common.sortOrder',
        ),

      sortable: true,

      width: '8rem',
    },

    {
      field: 'is_active',

      header:
        t(
          'curriculumReferences.common.status',
        ),

      bodySlot:
        'disciplineStatus',

      width: '8rem',
    },
  ])

const workloadTypeColumns =
  computed<
    CrudColumn<WorkloadType>[]
  >(() => [
    {
      field: 'display_name',

      header:
        t(
          'curriculumReferences.workloadTypes.fields.name',
        ),

      bodySlot:
        'workloadTypeName',

      minWidth: '16rem',
    },

    {
      field:
        'calculation_mode',

      header:
        t(
          'curriculumReferences.workloadTypes.fields.calculationMode',
        ),

      bodySlot:
        'calculationMode',

      minWidth: '12rem',
    },

    {
      field:
        'report_category',

      header:
        t(
          'curriculumReferences.workloadTypes.fields.reportCategory',
        ),

      bodySlot:
        'reportCategory',

      minWidth: '14rem',
    },

    {
      field:
        'is_classroom',

      header:
        t(
          'curriculumReferences.workloadTypes.fields.classroom',
        ),

      bodySlot: 'classroom',

      width: '9rem',
    },

    {
      field:
        'is_teaching_load',

      header:
        t(
          'curriculumReferences.workloadTypes.fields.teachingLoad',
        ),

      bodySlot:
        'teachingLoad',

      width: '10rem',
    },

    {
      field: 'is_active',

      header:
        t(
          'curriculumReferences.common.status',
        ),

      bodySlot:
        'workloadStatus',

      width: '8rem',
    },
  ])

const disciplines =
  useCrudList<Discipline>(
    (params) =>
      disciplinesApi.list(
        params,
      ),
    {
      initialPageSize: 20,

      initialOrdering:
        'sort_order,name_ru',
    },
  )

const workloadTypes =
  useCrudList<WorkloadType>(
    (params) =>
      workloadTypesApi.list(
        params,
      ),
    {
      initialPageSize: 20,

      initialOrdering:
        'sort_order,name_ru',
    },
  )

function clearErrors(): void {
  fieldErrors.value = {}

  nonFieldErrors.value = []

  generalFormError.value = ''
}

async function loadDepartments(): Promise<void> {
  lookupsLoading.value = true

  try {
    const response =
      await getDepartments()

    departments.value =
      response.results
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
    lookupsLoading.value =
      false
  }
}

function openCreateDiscipline(): void {
  selectedDiscipline.value =
    null

  clearErrors()

  disciplineDialogVisible.value =
    true
}

function openEditDiscipline(
  discipline: Discipline,
): void {
  selectedDiscipline.value =
    discipline

  clearErrors()

  disciplineDialogVisible.value =
    true
}

async function saveDiscipline(
  payload: DisciplinePayload,
): Promise<void> {
  saving.value = true

  clearErrors()

  try {
    if (
      selectedDiscipline.value
    ) {
      await disciplinesApi.update(
        selectedDiscipline.value.id,
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.updated'),
      )
    } else {
      await disciplinesApi.create(
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.created'),
      )
    }

    disciplineDialogVisible.value =
      false

    selectedDiscipline.value =
      null

    await disciplines.refresh()
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

    generalFormError.value =
      normalized.message
  } finally {
    saving.value = false
  }
}

function archiveDiscipline(
  discipline: Discipline,
): void {
  confirmDelete({
    header:
      t(
        'curriculumReferences.disciplines.archiveTitle',
      ),

    message:
      t(
        'curriculumReferences.disciplines.archiveConfirm',
        {
          name:
            disciplineName(
              discipline,
            ),
        },
      ),

    accept: async () => {
      try {
        await disciplinesApi.remove(
          discipline.id,
        )

        await disciplines.refresh()

        toast.success(
          t('common.success'),
          t(
            'curriculumReferences.disciplines.archived',
          ),
        )
      } catch (error) {
        const normalized =
          normalizeApiError(
            error,
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

function openCreateWorkloadType(): void {
  selectedWorkloadType.value =
    null

  clearErrors()

  workloadTypeDialogVisible.value =
    true
}

function openEditWorkloadType(
  workloadType: WorkloadType,
): void {
  selectedWorkloadType.value =
    workloadType

  clearErrors()

  workloadTypeDialogVisible.value =
    true
}

async function saveWorkloadType(
  payload: WorkloadTypePayload,
): Promise<void> {
  saving.value = true

  clearErrors()

  try {
    if (
      selectedWorkloadType.value
    ) {
      await workloadTypesApi.update(
        selectedWorkloadType.value.id,
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.updated'),
      )
    } else {
      await workloadTypesApi.create(
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.created'),
      )
    }

    workloadTypeDialogVisible.value =
      false

    selectedWorkloadType.value =
      null

    await workloadTypes.refresh()
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

    generalFormError.value =
      normalized.message
  } finally {
    saving.value = false
  }
}

function archiveWorkloadType(
  workloadType: WorkloadType,
): void {
  confirmDelete({
    header:
      t(
        'curriculumReferences.workloadTypes.archiveTitle',
      ),

    message:
      t(
        'curriculumReferences.workloadTypes.archiveConfirm',
        {
          name:
            workloadTypeName(
              workloadType,
            ),
        },
      ),

    accept: async () => {
      try {
        await workloadTypesApi.remove(
          workloadType.id,
        )

        await workloadTypes.refresh()

        toast.success(
          t('common.success'),
          t(
            'curriculumReferences.workloadTypes.archived',
          ),
        )
      } catch (error) {
        const normalized =
          normalizeApiError(
            error,
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

async function applyDisciplineDepartment(): Promise<void> {
  disciplines.setFilter(
    'default_department',
    selectedDepartment.value,
  )

  await disciplines.load()
}

async function applyDisciplineStatus(): Promise<void> {
  disciplines.setFilter(
    'is_active',
    selectedDisciplineActive.value,
  )

  await disciplines.load()
}

async function resetDisciplineFilters(): Promise<void> {
  selectedDepartment.value =
    null

  selectedDisciplineActive.value =
    null

  disciplines.clearFilters()

  await disciplines.reset()
}

async function applyCalculationMode(): Promise<void> {
  workloadTypes.setFilter(
    'calculation_mode',
    selectedCalculationMode.value,
  )

  await workloadTypes.load()
}

async function applyClassroom(): Promise<void> {
  workloadTypes.setFilter(
    'is_classroom',
    selectedClassroom.value,
  )

  await workloadTypes.load()
}

async function applyTeachingLoad(): Promise<void> {
  workloadTypes.setFilter(
    'is_teaching_load',
    selectedTeachingLoad.value,
  )

  await workloadTypes.load()
}

async function applyWorkloadStatus(): Promise<void> {
  workloadTypes.setFilter(
    'is_active',
    selectedWorkloadActive.value,
  )

  await workloadTypes.load()
}

async function resetWorkloadFilters(): Promise<void> {
  selectedCalculationMode.value =
    null

  selectedClassroom.value =
    null

  selectedTeachingLoad.value =
    null

  selectedWorkloadActive.value =
    null

  workloadTypes.clearFilters()

  await workloadTypes.reset()
}

onMounted(async () => {
  await Promise.all([
    disciplines.load(),
    workloadTypes.load(),
    loadDepartments(),
  ])
})
</script>

<template>
  <div
    class="
      curriculum-references-page
    "
  >
    <BasePageHeader
      :title="
        t(
          'curriculumReferences.title',
        )
      "
      :description="
        t(
          'curriculumReferences.description',
        )
      "
      icon="pi pi-book"
    />

    <Tabs
      v-model:value="
        activeTab
      "
    >
      <TabList>
        <Tab value="disciplines">
          {{
            t(
              'curriculumReferences.tabs.disciplines',
            )
          }}
        </Tab>

        <Tab value="workload-types">
          {{
            t(
              'curriculumReferences.tabs.workloadTypes',
            )
          }}
        </Tab>
      </TabList>

      <TabPanels>
        <TabPanel value="disciplines">
          <div
            class="
              curriculum-references-page__panel
            "
          >
            <BaseToolbar
              v-model:search="
                disciplines.searchInput.value
              "
              :show-create="false"
              :show-reset="true"
              :loading="
                disciplines.loading.value ||
                lookupsLoading
              "
              :search-placeholder="
                t(
                  'curriculumReferences.disciplines.searchPlaceholder',
                )
              "
              @refresh="
                disciplines.refresh
              "
              @reset="
                resetDisciplineFilters
              "
            >
              <template #start>
                <Button
                  v-if="
                    canCreateDiscipline
                  "
                  :label="
                    t(
                      'curriculumReferences.disciplines.create',
                    )
                  "
                  icon="pi pi-plus"
                  @click="
                    openCreateDiscipline
                  "
                />
              </template>

              <template #center>
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
                  class="reference-filter"
                  @change="
                    applyDisciplineDepartment
                  "
                />

                <Select
                  v-model="
                    selectedDisciplineActive
                  "
                  :options="
                    statusOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="reference-filter"
                  @change="
                    applyDisciplineStatus
                  "
                />
              </template>
            </BaseToolbar>

            <BaseCard
              :padding="false"
            >
              <BaseDataTable
                :value="
                  disciplines.items.value
                "
                :columns="
                  disciplineColumns
                "
                :loading="
                  disciplines.loading.value
                "
                :error="
                  disciplines.error.value
                "
                :first="
                  disciplines.first.value
                "
                :rows="
                  disciplines.query.value
                    .pageSize
                "
                :total-records="
                  disciplines
                    .totalRecords
                    .value
                "
                show-row-actions
                @page="
                  disciplines.handlePage
                "
                @sort="
                  disciplines.handleSort
                "
                @retry="
                  disciplines.refresh
                "
              >
                <template
                  #disciplineName="{ row }"
                >
                  <strong>
                    {{
                      disciplineName(
                        row,
                      )
                    }}
                  </strong>
                </template>

                <template
                  #disciplineDepartment="{ row }"
                >
                  {{
                    row.default_department_name ||
                    '—'
                  }}
                </template>

                <template
                  #disciplineStatus="{ row }"
                >
                  <Tag
                    :value="
                      row.is_active
                        ? t(
                            'curriculumReferences.common.active',
                          )
                        : t(
                            'curriculumReferences.common.inactive',
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
                      canEditDiscipline
                    "
                    v-tooltip.bottom="
                      t('common.edit')
                    "
                    icon="pi pi-pencil"
                    text
                    rounded
                    @click.stop="
                      openEditDiscipline(
                        row,
                      )
                    "
                  />

                  <Button
                    v-if="
                      canDeleteDiscipline
                    "
                    v-tooltip.bottom="
                      t(
                        'curriculumReferences.common.archive',
                      )
                    "
                    icon="pi pi-box"
                    severity="danger"
                    text
                    rounded
                    @click.stop="
                      archiveDiscipline(
                        row,
                      )
                    "
                  />
                </template>
              </BaseDataTable>
            </BaseCard>
          </div>
        </TabPanel>

        <TabPanel value="workload-types">
          <div
            class="
              curriculum-references-page__panel
            "
          >
            <BaseToolbar
              v-model:search="
                workloadTypes
                  .searchInput.value
              "
              :show-create="false"
              :show-reset="true"
              :loading="
                workloadTypes.loading.value
              "
              :search-placeholder="
                t(
                  'curriculumReferences.workloadTypes.searchPlaceholder',
                )
              "
              @refresh="
                workloadTypes.refresh
              "
              @reset="
                resetWorkloadFilters
              "
            >
              <template #start>
                <Button
                  v-if="
                    canCreateWorkloadType
                  "
                  :label="
                    t(
                      'curriculumReferences.workloadTypes.create',
                    )
                  "
                  icon="pi pi-plus"
                  @click="
                    openCreateWorkloadType
                  "
                />
              </template>

              <template #center>
                <Select
                  v-model="
                    selectedCalculationMode
                  "
                  :options="
                    calculationModeOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="reference-filter"
                  @change="
                    applyCalculationMode
                  "
                />

                <Select
                  v-model="
                    selectedClassroom
                  "
                  :options="
                    booleanOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="reference-filter"
                  :placeholder="
                    t(
                      'curriculumReferences.filters.classroom',
                    )
                  "
                  @change="
                    applyClassroom
                  "
                />

                <Select
                  v-model="
                    selectedTeachingLoad
                  "
                  :options="
                    booleanOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="reference-filter"
                  :placeholder="
                    t(
                      'curriculumReferences.filters.teachingLoad',
                    )
                  "
                  @change="
                    applyTeachingLoad
                  "
                />

                <Select
                  v-model="
                    selectedWorkloadActive
                  "
                  :options="
                    statusOptions
                  "
                  option-label="label"
                  option-value="value"
                  class="reference-filter"
                  @change="
                    applyWorkloadStatus
                  "
                />
              </template>
            </BaseToolbar>

            <BaseCard
              :padding="false"
            >
              <BaseDataTable
                :value="
                  workloadTypes.items.value
                "
                :columns="
                  workloadTypeColumns
                "
                :loading="
                  workloadTypes.loading.value
                "
                :error="
                  workloadTypes.error.value
                "
                :first="
                  workloadTypes.first.value
                "
                :rows="
                  workloadTypes.query.value
                    .pageSize
                "
                :total-records="
                  workloadTypes
                    .totalRecords
                    .value
                "
                show-row-actions
                @page="
                  workloadTypes.handlePage
                "
                @sort="
                  workloadTypes.handleSort
                "
                @retry="
                  workloadTypes.refresh
                "
              >
                <template
                  #workloadTypeName="{ row }"
                >
                  {{
                    workloadTypeName(
                      row,
                    )
                  }}
                </template>

                <template
                  #calculationMode="{ row }"
                >
                  {{
                    t(
                      `curriculumReferences.workloadTypes.calculationModes.${{
                        fixed:
                          'fixed',
                        per_group:
                          'perGroup',
                        per_subgroup:
                          'perSubgroup',
                        per_student:
                          'perStudent',
                      }[row.calculation_mode]}`,
                    )
                  }}
                </template>

                <template
                  #reportCategory="{ row }"
                >
                  {{
                    row.report_category_name
                  }}
                </template>

                <template
                  #classroom="{ row }"
                >
                  <Tag
                    :value="
                      row.is_classroom
                        ? t('common.yes')
                        : t('common.no')
                    "
                    :severity="
                      row.is_classroom
                        ? 'info'
                        : 'secondary'
                    "
                  />
                </template>

                <template
                  #teachingLoad="{ row }"
                >
                  <Tag
                    :value="
                      row.is_teaching_load
                        ? t('common.yes')
                        : t('common.no')
                    "
                    :severity="
                      row.is_teaching_load
                        ? 'success'
                        : 'secondary'
                    "
                  />
                </template>

                <template
                  #workloadStatus="{ row }"
                >
                  <Tag
                    :value="
                      row.is_active
                        ? t(
                            'curriculumReferences.common.active',
                          )
                        : t(
                            'curriculumReferences.common.inactive',
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
                      canEditWorkloadType
                    "
                    v-tooltip.bottom="
                      t('common.edit')
                    "
                    icon="pi pi-pencil"
                    text
                    rounded
                    @click.stop="
                      openEditWorkloadType(
                        row,
                      )
                    "
                  />

                  <Button
                    v-if="
                      canDeleteWorkloadType
                    "
                    v-tooltip.bottom="
                      t(
                        'curriculumReferences.common.archive',
                      )
                    "
                    icon="pi pi-box"
                    severity="danger"
                    text
                    rounded
                    @click.stop="
                      archiveWorkloadType(
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

    <DisciplineFormDialog
      v-model="
        disciplineDialogVisible
      "
      :discipline="
        selectedDiscipline
      "
      :departments="
        departments
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
        saveDiscipline
      "
    />

    <WorkloadTypeFormDialog
      v-model="
        workloadTypeDialogVisible
      "
      :workload-type="
        selectedWorkloadType
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
        saveWorkloadType
      "
    />
  </div>
</template>

<style scoped>
.curriculum-references-page {
  display: grid;
  gap: 1rem;
}

.curriculum-references-page__panel {
  display: grid;
  gap: 1rem;
}

.reference-filter {
  width: 14rem;
}

:deep(.p-tabpanels) {
  padding: 1rem 0 0;
}

@media (max-width: 1199px) {
  .reference-filter {
    width: 100%;
  }
}
</style>
