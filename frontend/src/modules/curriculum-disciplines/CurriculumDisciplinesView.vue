<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Tag from 'primevue/tag'

import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  useRoute,
  useRouter,
} from 'vue-router'

import {
  useI18n,
} from 'vue-i18n'

import BaseCard from '@/components/base/BaseCard.vue'
import BaseDialog from '@/components/base/BaseDialog.vue'
import BaseDataTable from '@/components/base/BaseDataTable.vue'
import BasePageHeader from '@/components/base/BasePageHeader.vue'
import BaseToolbar from '@/components/base/BaseToolbar.vue'

import CurriculumDisciplineFormDialog from '@/modules/curriculum-disciplines/components/CurriculumDisciplineFormDialog.vue'
import CurriculumWorkloadPanel from '@/modules/curriculum-disciplines/components/CurriculumWorkloadPanel.vue'

import {
  curriculumDisciplinesApi,
  getCurriculum,
  getDepartments,
  getDisciplines,
  getStudyProgram,
} from '@/modules/curriculum-disciplines/api'

import type {
  Curriculum,
} from '@/modules/curricula/types'

import type {
  DepartmentLookup,
  Discipline,
} from '@/modules/curriculum-references/types'

import type {
  StudyProgram,
} from '@/modules/study-programs/types'

import type {
  CurriculumComponentType,
  CurriculumControlForm,
  CurriculumDiscipline,
  CurriculumDisciplinePayload,
  SelectOption,
} from '@/modules/curriculum-disciplines/types'

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

const route =
  useRoute()

const router =
  useRouter()

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

const curriculumId =
  Number(
    route.params.curriculumId,
  )

const curriculum =
  ref<Curriculum | null>(
    null,
  )

const studyProgram =
  ref<StudyProgram | null>(
    null,
  )

const disciplines =
  ref<Discipline[]>([])

const departments =
  ref<DepartmentLookup[]>([])

const selectedRecord =
  ref<
    CurriculumDiscipline | null
  >(null)

const formVisible =
  ref(false)

const workloadDialogVisible =
  ref(false)

const workloadDiscipline =
  ref<
    CurriculumDiscipline | null
  >(null)

const saving =
  ref(false)

const metadataLoading =
  ref(false)

const metadataError =
  ref('')

const selectedSemester =
  ref<number | null>(null)

const selectedComponentType =
  ref<
    CurriculumComponentType | null
  >(null)

const selectedControlForm =
  ref<
    CurriculumControlForm | null
  >(null)

const selectedActive =
  ref<boolean | null>(null)

const fieldErrors =
  ref<FieldErrors>({})

const nonFieldErrors =
  ref<string[]>([])

const generalFormError =
  ref('')

const canCreate =
  computed(
    () =>
      can(
        'curriculum.add_curriculumdiscipline',
      ),
  )

const canEdit =
  computed(
    () =>
      can(
        'curriculum.change_curriculumdiscipline',
      ),
  )

const canDelete =
  computed(
    () =>
      can(
        'curriculum.delete_curriculumdiscipline',
      ),
  )

const canViewWorkloads =
  computed(
    () =>
      can(
        'curriculum.view_curriculumworkload',
      ),
  )

const semesterOptions =
  computed<
    SelectOption<
      number | null
    >[]
  >(() => {
    const count =
      curriculum.value
        ?.semesters_count ?? 0

    return [
      {
        value: null,

        label:
          t(
            'curriculumDisciplines.filters.allSemesters',
          ),
      },

      ...Array.from(
        {
          length: count,
        },

        (_, index) => {
          const semester =
            index + 1

          return {
            value:
              semester,

            label:
              t(
                'curriculumDisciplines.semesterOption',
                {
                  semester,

                  season:
                    semester %
                      2 ===
                    1
                      ? t(
                          'curriculumDisciplines.seasons.autumn',
                        )
                      : t(
                          'curriculumDisciplines.seasons.spring',
                        ),
                },
              ),
          }
        },
      ),
    ]
  })

const componentTypeOptions =
  computed<
    SelectOption<
      CurriculumComponentType | null
    >[]
  >(() => [
    {
      value: null,

      label:
        t(
          'curriculumDisciplines.filters.allComponentTypes',
        ),
    },

    {
      value: 'required',

      label:
        t(
          'curriculumDisciplines.componentTypes.required',
        ),
    },

    {
      value: 'elective',

      label:
        t(
          'curriculumDisciplines.componentTypes.elective',
        ),
    },

    {
      value: 'optional',

      label:
        t(
          'curriculumDisciplines.componentTypes.optional',
        ),
    },
  ])

const controlFormOptions =
  computed<
    SelectOption<
      CurriculumControlForm | null
    >[]
  >(() => [
    {
      value: null,

      label:
        t(
          'curriculumDisciplines.filters.allControlForms',
        ),
    },

    {
      value: 'none',

      label:
        t(
          'curriculumDisciplines.controlForms.none',
        ),
    },

    {
      value: 'exam',

      label:
        t(
          'curriculumDisciplines.controlForms.exam',
        ),
    },

    {
      value: 'credit',

      label:
        t(
          'curriculumDisciplines.controlForms.credit',
        ),
    },

    {
      value:
        'graded_credit',

      label:
        t(
          'curriculumDisciplines.controlForms.gradedCredit',
        ),
    },

    {
      value:
        'course_work',

      label:
        t(
          'curriculumDisciplines.controlForms.courseWork',
        ),
    },

    {
      value:
        'course_project',

      label:
        t(
          'curriculumDisciplines.controlForms.courseProject',
        ),
    },
  ])

const activeOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'curriculumDisciplines.filters.allStatuses',
        ),
    },

    {
      value: true,

      label:
        t(
          'curriculumDisciplines.active',
        ),
    },

    {
      value: false,

      label:
        t(
          'curriculumDisciplines.inactive',
        ),
    },
  ])

function seasonLabel(
  semester: number,
): string {
  return semester %
    2 ===
    1
    ? t(
        'curriculumDisciplines.seasons.autumn',
      )
    : t(
        'curriculumDisciplines.seasons.spring',
      )
}

function componentTypeLabel(
  value:
    CurriculumComponentType,
): string {
  return t(
    `curriculumDisciplines.componentTypes.${value}`,
  )
}

function controlFormLabel(
  value:
    CurriculumControlForm,
): string {
  const keyMap:
    Record<
      CurriculumControlForm,
      string
    > = {
      none: 'none',

      exam: 'exam',

      credit: 'credit',

      graded_credit:
        'gradedCredit',

      course_work:
        'courseWork',

      course_project:
        'courseProject',
    }

  return t(
    `curriculumDisciplines.controlForms.${keyMap[value]}`,
  )
}

function componentSeverity(
  value:
    CurriculumComponentType,
):
  | 'success'
  | 'info'
  | 'secondary' {
  if (value === 'required') {
    return 'success'
  }

  if (value === 'elective') {
    return 'info'
  }

  return 'secondary'
}

const columns =
  computed<
    CrudColumn<
      CurriculumDiscipline
    >[]
  >(() => [
    {
      field:
        'semester_number',

      header:
        t(
          'curriculumDisciplines.fields.semester',
        ),

      sortable: true,

      width: '8rem',

      align: 'center',

      bodySlot:
        'semester',
    },

    {
      field:
        'discipline_name',

      header:
        t(
          'curriculumDisciplines.fields.discipline',
        ),

      sortable: true,

      sortField:
        'discipline__name_ru',

      minWidth: '18rem',

      bodySlot:
        'discipline',
    },

    {
      field:
        'teaching_department_name',

      header:
        t(
          'curriculumDisciplines.fields.department',
        ),

      minWidth: '14rem',
    },

    {
      field:
        'component_type',

      header:
        t(
          'curriculumDisciplines.fields.componentType',
        ),

      bodySlot:
        'componentType',

      minWidth: '11rem',
    },

    {
      field:
        'control_form',

      header:
        t(
          'curriculumDisciplines.fields.controlForm',
        ),

      bodySlot:
        'controlForm',

      minWidth: '11rem',
    },

    {
      field: 'credits',

      header:
        t(
          'curriculumDisciplines.fields.credits',
        ),

      sortable: true,

      width: '7rem',

      align: 'center',
    },

    {
      field:
        'total_academic_hours',

      header:
        t(
          'curriculumDisciplines.fields.totalHoursShort',
        ),

      sortable: true,

      width: '8rem',

      align: 'center',
    },

    {
      field:
        'independent_hours',

      header:
        t(
          'curriculumDisciplines.fields.independentHoursShort',
        ),

      width: '8rem',

      align: 'center',
    },

    {
      field:
        'planned_contact_hours',

      header:
        t(
          'curriculumDisciplines.fields.plannedContactHoursShort',
        ),

      width: '8rem',

      align: 'center',

      bodySlot:
        'contactHours',
    },

    {
      field:
        'is_active',

      header:
        t(
          'curriculumDisciplines.fields.status',
        ),

      width: '8rem',

      align: 'center',

      bodySlot:
        'status',
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
    CurriculumDiscipline
  >(
    (params) =>
      curriculumDisciplinesApi.list(
        {
          ...params,

          curriculum:
            curriculumId,
        },
      ),

    {
      initialPageSize: 50,

      initialOrdering:
        'semester_number,discipline__name_ru',
    },
  )

function clearFormErrors(): void {
  fieldErrors.value = {}

  nonFieldErrors.value = []

  generalFormError.value =
    ''
}

async function loadMetadata(): Promise<void> {
  metadataLoading.value =
    true

  metadataError.value = ''

  try {
    const currentCurriculum =
      await getCurriculum(
        curriculumId,
      )

    curriculum.value =
      currentCurriculum

    const [
      program,
      disciplineResponse,
      departmentResponse,
    ] = await Promise.all([
      getStudyProgram(
        currentCurriculum
          .study_program,
      ),

      getDisciplines(),

      getDepartments(),
    ])

    studyProgram.value =
      program

    disciplines.value =
      disciplineResponse.results

    departments.value =
      departmentResponse.results
  } catch (loadError) {
    const normalized =
      normalizeApiError(
        loadError,
        t('crud.loadError'),
      )

    metadataError.value =
      normalized.message

    toast.error(
      t('common.error'),
      normalized.message,
    )
  } finally {
    metadataLoading.value =
      false
  }
}

function openCreate(): void {
  if (!curriculum.value) {
    return
  }

  selectedRecord.value =
    null

  clearFormErrors()

  formVisible.value =
    true
}

function openEdit(
  record:
    CurriculumDiscipline,
): void {
  selectedRecord.value =
    record

  clearFormErrors()

  formVisible.value =
    true
}

function openWorkloads(
  record:
    CurriculumDiscipline,
): void {
  workloadDiscipline.value =
    record

  workloadDialogVisible.value =
    true
}

async function handleWorkloadChanged(): Promise<void> {
  await refresh()

  if (
    !workloadDiscipline.value
  ) {
    return
  }

  const refreshed =
    items.value.find(
      (item) =>
        item.id ===
        workloadDiscipline.value
          ?.id,
    )

  if (refreshed) {
    workloadDiscipline.value =
      refreshed
  }
}

async function saveRecord(
  payload:
    CurriculumDisciplinePayload,
): Promise<void> {
  saving.value = true

  clearFormErrors()

  try {
    if (
      selectedRecord.value
    ) {
      await curriculumDisciplinesApi
        .update(
          selectedRecord.value.id,

          payload,
        )

      toast.success(
        t('common.success'),
        t('crud.updated'),
      )
    } else {
      await curriculumDisciplinesApi
        .create(payload)

      toast.success(
        t('common.success'),
        t('crud.created'),
      )
    }

    formVisible.value =
      false

    selectedRecord.value =
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

function archiveRecord(
  record:
    CurriculumDiscipline,
): void {
  confirmDelete({
    header:
      t(
        'curriculumDisciplines.archiveTitle',
      ),

    message:
      t(
        'curriculumDisciplines.archiveConfirm',
        {
          discipline:
            record.discipline_name,

          semester:
            record.semester_number,
        },
      ),

    accept: async () => {
      try {
        await curriculumDisciplinesApi
          .remove(record.id)

        toast.success(
          t('common.success'),

          t(
            'curriculumDisciplines.archived',
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

async function applySemesterFilter(): Promise<void> {
  setFilter(
    'semester_number',
    selectedSemester.value,
  )

  await load()
}

async function applyComponentTypeFilter(): Promise<void> {
  setFilter(
    'component_type',
    selectedComponentType.value,
  )

  await load()
}

async function applyControlFormFilter(): Promise<void> {
  setFilter(
    'control_form',
    selectedControlForm.value,
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
  selectedSemester.value =
    null

  selectedComponentType.value =
    null

  selectedControlForm.value =
    null

  selectedActive.value =
    null

  clearFilters()

  await reset()
}

function goBack(): void {
  void router.push({
    name: 'curricula',
  })
}

onMounted(
  async () => {
    if (
      !Number.isInteger(
        curriculumId,
      ) ||
      curriculumId <= 0
    ) {
      metadataError.value =
        t(
          'curriculumDisciplines.invalidCurriculum',
        )

      return
    }

    await Promise.all([
      load(),
      loadMetadata(),
    ])
  },
)
</script>

<template>
  <div
    class="
      curriculum-disciplines-page
    "
  >
    <BasePageHeader
      :title="
        curriculum
          ? `${t(
              'curriculumDisciplines.title',
            )}: ${curriculum.code}`
          : t(
              'curriculumDisciplines.title',
            )
      "
      :description="
        curriculum
          ? `${curriculum.study_program_code} — ${curriculum.study_program_name} · ${curriculum.study_form_name} · ${curriculum.effective_academic_year_name}`
          : t(
              'curriculumDisciplines.description',
            )
      "
      icon="pi pi-table"
    >
      <template #actions>
        <Button
          :label="
            t(
              'curriculumDisciplines.backToCurricula',
            )
          "
          icon="pi pi-arrow-left"
          severity="secondary"
          outlined
          @click="goBack"
        />

        <Button
          v-if="
            canCreate &&
            curriculum
          "
          :label="
            t(
              'curriculumDisciplines.create',
            )
          "
          icon="pi pi-plus"
          @click="openCreate"
        />
      </template>
    </BasePageHeader>

    <Message
      v-if="metadataError"
      severity="error"
      :closable="false"
    >
      {{ metadataError }}
    </Message>

    <BaseCard
      v-if="curriculum"
    >
      <div
        class="
          curriculum-summary
        "
      >
        <div>
          <span>
            {{
              t(
                'curriculumDisciplines.summary.plan',
              )
            }}
          </span>

          <strong>
            {{ curriculum.code }}
          </strong>
        </div>

        <div>
          <span>
            {{
              t(
                'curriculumDisciplines.summary.version',
              )
            }}
          </span>

          <strong>
            {{
              curriculum.version
            }}
          </strong>
        </div>

        <div>
          <span>
            {{
              t(
                'curriculumDisciplines.summary.semesters',
              )
            }}
          </span>

          <strong>
            {{
              curriculum.semesters_count ??
              '—'
            }}
          </strong>
        </div>

        <div>
          <span>
            {{
              t(
                'curriculumDisciplines.summary.disciplines',
              )
            }}
          </span>

          <strong>
            {{ totalRecords }}
          </strong>
        </div>
      </div>
    </BaseCard>

    <BaseToolbar
      v-if="curriculum"
      v-model:search="
        searchInput
      "
      :show-create="false"
      :show-reset="true"
      :loading="
        loading ||
        metadataLoading
      "
      :search-placeholder="
        t(
          'curriculumDisciplines.searchPlaceholder',
        )
      "
      @refresh="refresh"
      @reset="resetFilters"
    >
      <template #center>
        <Select
          v-model="
            selectedSemester
          "
          :options="
            semesterOptions
          "
          option-label="label"
          option-value="value"
          class="
            matrix-filter
          "
          @change="
            applySemesterFilter
          "
        />

        <Select
          v-model="
            selectedComponentType
          "
          :options="
            componentTypeOptions
          "
          option-label="label"
          option-value="value"
          class="
            matrix-filter
          "
          @change="
            applyComponentTypeFilter
          "
        />

        <Select
          v-model="
            selectedControlForm
          "
          :options="
            controlFormOptions
          "
          option-label="label"
          option-value="value"
          class="
            matrix-filter
          "
          @change="
            applyControlFormFilter
          "
        />

        <Select
          v-model="
            selectedActive
          "
          :options="
            activeOptions
          "
          option-label="label"
          option-value="value"
          class="
            matrix-filter
            matrix-filter--status
          "
          @change="
            applyStatusFilter
          "
        />
      </template>
    </BaseToolbar>

    <BaseCard
      v-if="curriculum"
      :padding="false"
    >
      <BaseDataTable
        :value="items"
        :columns="columns"
        :loading="
          loading ||
          metadataLoading
        "
        :error="error"
        :first="first"
        :rows="
          query.pageSize
        "
        :total-records="
          totalRecords
        "
        show-row-actions
        @page="handlePage"
        @sort="handleSort"
        @retry="refresh"
      >
        <template
          #semester="{ row }"
        >
          <div
            class="
              semester-cell
            "
          >
            <strong>
              {{
                t(
                  'curriculumDisciplines.semesterNumber',
                  {
                    semester:
                      row.semester_number,
                  },
                )
              }}
            </strong>

            <small>
              {{
                seasonLabel(
                  row.semester_number,
                )
              }}
            </small>
          </div>
        </template>

        <template
          #discipline="{ row }"
        >
          <div
            class="
              discipline-cell
            "
          >
            <strong>
              {{
                row.discipline_code
              }}
            </strong>

            <span>
              {{
                row.discipline_name
              }}
            </span>
          </div>
        </template>

        <template
          #componentType="{ row }"
        >
          <Tag
            :value="
              componentTypeLabel(
                row.component_type,
              )
            "
            :severity="
              componentSeverity(
                row.component_type,
              )
            "
          />
        </template>

        <template
          #controlForm="{ row }"
        >
          {{
            controlFormLabel(
              row.control_form,
            )
          }}
        </template>

        <template
          #contactHours="{ row }"
        >
          <Tag
            :value="
              row.planned_contact_hours
            "
            severity="info"
          />
        </template>

        <template
          #status="{ row }"
        >
          <Tag
            :value="
              row.is_active
                ? t(
                    'curriculumDisciplines.active',
                  )
                : t(
                    'curriculumDisciplines.inactive',
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
      canViewWorkloads
    "
            v-tooltip.bottom="
      t(
        'curriculumDisciplines.workloads',
      )
    "
            icon="pi pi-clock"
            severity="info"
            text
            rounded
            @click.stop="
      openWorkloads(row)
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
        'curriculumDisciplines.archive',
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

        <template
          #emptyActions
        >
          <Button
            v-if="canCreate"
            :label="
              t(
                'curriculumDisciplines.create',
              )
            "
            icon="pi pi-plus"
            @click="openCreate"
          />
        </template>
      </BaseDataTable>
    </BaseCard>

    <CurriculumDisciplineFormDialog
      v-if="
        curriculum &&
        studyProgram
      "
      v-model="formVisible"
      :curriculum="
        curriculum
      "
      :study-program="
        studyProgram
      "
      :record="
        selectedRecord
      "
      :disciplines="
        disciplines
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
        saveRecord
      "
    />

    <BaseDialog
      v-model="
    workloadDialogVisible
  "
      :title="
    workloadDiscipline
      ? `${t(
          'curriculumWorkloads.title',
        )}: ${workloadDiscipline.discipline_code}`
      : t(
          'curriculumWorkloads.title',
        )
  "
      width="70rem"
    >
      <CurriculumWorkloadPanel
        v-if="
      workloadDiscipline
    "
        :key="
      workloadDiscipline.id
    "
        :discipline="
      workloadDiscipline
    "
        @changed="
      handleWorkloadChanged
    "
      />
    </BaseDialog>

  </div>
</template>

<style scoped>
.curriculum-disciplines-page {
  display: grid;
  gap: 1rem;
}

.curriculum-summary {
  display: grid;
  grid-template-columns:
    repeat(
      4,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.curriculum-summary > div {
  display: grid;
  gap: 0.25rem;
}

.curriculum-summary span {
  color:
    var(--app-text-muted);
  font-size: 0.72rem;
}

.curriculum-summary strong {
  font-size: 1rem;
}

.matrix-filter {
  width: 14rem;
}

.matrix-filter--status {
  width: 10rem;
}

.semester-cell,
.discipline-cell {
  display: grid;
  gap: 0.1rem;
}

.semester-cell strong,
.discipline-cell strong {
  font-size: 0.76rem;
}

.semester-cell small {
  color:
    var(--app-text-muted);
  font-size: 0.68rem;
}

.discipline-cell span {
  font-size: 0.82rem;
}

@media (max-width: 991px) {
  .curriculum-summary {
    grid-template-columns:
      repeat(
        2,
        minmax(0, 1fr)
      );
  }

  .matrix-filter,
  .matrix-filter--status {
    width: 100%;
  }
}

@media (max-width: 575px) {
  .curriculum-summary {
    grid-template-columns:
      1fr;
  }
}
</style>
