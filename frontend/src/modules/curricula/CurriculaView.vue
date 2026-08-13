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

import CurriculumDetailsDialog from '@/modules/curricula/components/CurriculumDetailsDialog.vue'
import CurriculumFormDialog from '@/modules/curricula/components/CurriculumFormDialog.vue'

import {
  curriculaApi,
  getAcademicYears,
  getEducationDurations,
  getStudyForms,
  getStudyPrograms,
  getUniversities,
} from '@/modules/curricula/api'

import type {
  AcademicYearLookup,
  Curriculum,
  CurriculumPayload,
  CurriculumStatus,
  EducationDurationLookup,
  SelectOption,
  StudyFormLookup,
  StudyProgramLookup,
  UniversityLookup,
} from '@/modules/curricula/types'

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

const selectedCurriculum =
  ref<Curriculum | null>(
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

const studyPrograms =
  ref<StudyProgramLookup[]>([])

const studyForms =
  ref<StudyFormLookup[]>([])

const academicYears =
  ref<AcademicYearLookup[]>([])

const educationDurations =
  ref<EducationDurationLookup[]>([])

const universities =
  ref<UniversityLookup[]>([])

const selectedUniversity =
  ref<number | null>(null)

const selectedStudyProgram =
  ref<number | null>(null)

const selectedStudyForm =
  ref<number | null>(null)

const selectedAcademicYear =
  ref<number | null>(null)

const selectedStatus =
  ref<CurriculumStatus | null>(
    null,
  )

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
        'curriculum.add_curriculum',
      ),
  )

const canEdit =
  computed(
    () =>
      can(
        'curriculum.change_curriculum',
      ),
  )

const canDelete =
  computed(
    () =>
      can(
        'curriculum.delete_curriculum',
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

function statusLabel(
  status: CurriculumStatus,
): string {
  return t(
    `curricula.statuses.${status}`,
  )
}

function statusSeverity(
  status: CurriculumStatus,
):
  | 'success'
  | 'secondary'
  | 'warn' {
  if (status === 'approved') {
    return 'success'
  }

  if (status === 'archived') {
    return 'secondary'
  }

  return 'warn'
}

const universityOptions =
  computed<
    SelectOption<
      number | null
    >[]
  >(() => [
    {
      value: null,

      label:
        t(
          'curricula.filters.allUniversities',
        ),
    },

    ...universities.value.map(
      (university) => ({
        value:
          university.id,

        label:
          localizedName(
            university.name_ru,
            university.name_uz,
          ),
      }),
    ),
  ])

const programOptions =
  computed<
    SelectOption<
      number | null
    >[]
  >(() => {
    const programs =
      selectedUniversity.value
        ? studyPrograms.value.filter(
            (program) =>
              program.university ===
              selectedUniversity.value,
          )
        : studyPrograms.value

    return [
      {
        value: null,

        label:
          t(
            'curricula.filters.allPrograms',
          ),
      },

      ...programs.map(
        (program) => ({
          value:
            program.id,

          label:
            `${program.code} — ${
              localizedName(
                program.name_ru,
                program.name_uz,
              )
            }`,
        }),
      ),
    ]
  })

const studyFormOptions =
  computed<
    SelectOption<
      number | null
    >[]
  >(() => [
    {
      value: null,

      label:
        t(
          'curricula.filters.allStudyForms',
        ),
    },

    ...studyForms.value.map(
      (studyForm) => ({
        value:
          studyForm.id,

        label:
          localizedName(
            studyForm.name_ru,
            studyForm.name_uz,
          ),
      }),
    ),
  ])

const academicYearOptions =
  computed<
    SelectOption<
      number | null
    >[]
  >(() => [
    {
      value: null,

      label:
        t(
          'curricula.filters.allAcademicYears',
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
  computed<
    SelectOption<
      CurriculumStatus | null
    >[]
  >(() => [
    {
      value: null,

      label:
        t(
          'curricula.filters.allStatuses',
        ),
    },

    {
      value: 'draft',

      label:
        t(
          'curricula.statuses.draft',
        ),
    },

    {
      value: 'approved',

      label:
        t(
          'curricula.statuses.approved',
        ),
    },

    {
      value: 'archived',

      label:
        t(
          'curricula.statuses.archived',
        ),
    },
  ])

const activeOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'curricula.filters.allActivity',
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

const columns =
  computed<
    CrudColumn<Curriculum>[]
  >(() => [
    {
      field: 'code',

      header:
        t(
          'curricula.fields.code',
        ),

      sortable: true,

      minWidth: '10rem',
    },

    {
      field:
        'study_program_name',

      header:
        t(
          'curricula.fields.studyProgram',
        ),

      bodySlot:
        'studyProgram',

      minWidth: '18rem',
    },

    {
      field:
        'study_form_name',

      header:
        t(
          'curricula.fields.studyForm',
        ),

      minWidth: '10rem',
    },

    {
      field:
        'effective_academic_year_name',

      header:
        t(
          'curricula.fields.effectiveAcademicYear',
        ),

      sortable: true,

      sortField:
        'effective_academic_year__start_year',

      minWidth: '10rem',
    },

    {
      field: 'version',

      header:
        t(
          'curricula.fields.version',
        ),

      sortable: true,

      width: '7rem',

      align: 'center',
    },

    {
      field:
        'semesters_count',

      header:
        t(
          'curricula.fields.semestersCountShort',
        ),

      width: '7rem',

      align: 'center',
    },

    {
      field:
        'disciplines_count',

      header:
        t(
          'curricula.fields.disciplinesCountShort',
        ),

      width: '8rem',

      align: 'center',
    },

    {
      field: 'status',

      header:
        t(
          'curricula.fields.status',
        ),

      bodySlot: 'status',

      width: '9rem',

      align: 'center',
    },

    {
      field: 'is_active',

      header:
        t(
          'curricula.fields.active',
        ),

      bodySlot: 'active',

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
} = useCrudList<Curriculum>(
  (params) =>
    curriculaApi.list(
      params,
    ),

  {
    initialPageSize: 20,

    initialOrdering:
      '-effective_academic_year__start_year,study_program__code,-version',
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
      programsResponse,
      formsResponse,
      yearsResponse,
      durationsResponse,
      universitiesResponse,
    ] = await Promise.all([
      getStudyPrograms(),
      getStudyForms(),
      getAcademicYears(),
      getEducationDurations(),
      getUniversities(),
    ])

    studyPrograms.value =
      programsResponse.results

    studyForms.value =
      formsResponse.results

    academicYears.value =
      yearsResponse.results

    educationDurations.value =
      durationsResponse.results

    universities.value =
      universitiesResponse.results
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
    lookupsLoading.value =
      false
  }
}

function openCreate(): void {
  selectedCurriculum.value =
    null

  clearFormErrors()

  formVisible.value = true
}

function openView(
  curriculum: Curriculum,
): void {
  selectedCurriculum.value =
    curriculum

  detailsVisible.value =
    true
}

function openEdit(
  curriculum: Curriculum,
): void {
  selectedCurriculum.value =
    curriculum

  clearFormErrors()

  formVisible.value = true
}

async function saveCurriculum(
  payload: CurriculumPayload,
): Promise<void> {
  saving.value = true

  clearFormErrors()

  try {
    if (
      selectedCurriculum.value
    ) {
      await curriculaApi.update(
        selectedCurriculum.value.id,
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.updated'),
      )
    } else {
      await curriculaApi.create(
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.created'),
      )
    }

    formVisible.value =
      false

    selectedCurriculum.value =
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

function archiveCurriculum(
  curriculum: Curriculum,
): void {
  confirmDelete({
    header:
      t(
        'curricula.archiveTitle',
      ),

    message:
      t(
        'curricula.archiveConfirm',
        {
          code:
            curriculum.code,
        },
      ),

    accept: async () => {
      try {
        await curriculaApi.remove(
          curriculum.id,
        )

        toast.success(
          t('common.success'),
          t(
            'curricula.archived',
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

async function applyUniversityFilter(): Promise<void> {
  setFilter(
    'university',
    selectedUniversity.value,
  )

  selectedStudyProgram.value =
    null

  setFilter(
    'study_program',
    undefined,
  )

  await load()
}

async function applyProgramFilter(): Promise<void> {
  setFilter(
    'study_program',
    selectedStudyProgram.value,
  )

  await load()
}

async function applyStudyFormFilter(): Promise<void> {
  setFilter(
    'study_form',
    selectedStudyForm.value,
  )

  await load()
}

async function applyAcademicYearFilter(): Promise<void> {
  setFilter(
    'effective_academic_year',
    selectedAcademicYear.value,
  )

  await load()
}

async function applyStatusFilter(): Promise<void> {
  setFilter(
    'status',
    selectedStatus.value,
  )

  await load()
}

async function applyActiveFilter(): Promise<void> {
  setFilter(
    'is_active',
    selectedActive.value,
  )

  await load()
}

async function resetFilters(): Promise<void> {
  selectedUniversity.value =
    null

  selectedStudyProgram.value =
    null

  selectedStudyForm.value =
    null

  selectedAcademicYear.value =
    null

  selectedStatus.value =
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
    class="curricula-page"
  >
    <BasePageHeader
      :title="
        t('curricula.title')
      "
      :description="
        t(
          'curricula.description',
        )
      "
      icon="pi pi-list-check"
    >
      <template #actions>
        <Button
          v-if="canCreate"
          :label="
            t(
              'curricula.create',
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
          'curricula.searchPlaceholder',
        )
      "
      @refresh="refresh"
      @reset="resetFilters"
    >
      <template #center>
        <Select
          v-model="
            selectedUniversity
          "
          :options="
            universityOptions
          "
          option-label="label"
          option-value="value"
          filter
          class="
            curriculum-filter
          "
          @change="
            applyUniversityFilter
          "
        />

        <Select
          v-model="
            selectedStudyProgram
          "
          :options="
            programOptions
          "
          option-label="label"
          option-value="value"
          filter
          class="
            curriculum-filter
          "
          @change="
            applyProgramFilter
          "
        />

        <Select
          v-model="
            selectedStudyForm
          "
          :options="
            studyFormOptions
          "
          option-label="label"
          option-value="value"
          class="
            curriculum-filter
          "
          @change="
            applyStudyFormFilter
          "
        />

        <Select
          v-model="
            selectedAcademicYear
          "
          :options="
            academicYearOptions
          "
          option-label="label"
          option-value="value"
          class="
            curriculum-filter
          "
          @change="
            applyAcademicYearFilter
          "
        />

        <Select
          v-model="
            selectedStatus
          "
          :options="
            statusOptions
          "
          option-label="label"
          option-value="value"
          class="
            curriculum-filter
            curriculum-filter--small
          "
          @change="
            applyStatusFilter
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
            curriculum-filter
            curriculum-filter--small
          "
          @change="
            applyActiveFilter
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
          #studyProgram="{ row }"
        >
          <div
            class="
              curriculum-program
            "
          >
            <strong>
              {{
                row.study_program_code
              }}
            </strong>

            <span>
              {{
                row.study_program_name
              }}
            </span>

            <small>
              {{
                row.education_level_name
              }}
            </small>
          </div>
        </template>

        <template
          #status="{ row }"
        >
          <Tag
            :value="
              statusLabel(
                row.status,
              )
            "
            :severity="
              statusSeverity(
                row.status,
              )
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
                'curricula.archive',
              )
            "
            icon="pi pi-box"
            severity="danger"
            text
            rounded
            @click.stop="
              archiveCurriculum(
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
                'curricula.create',
              )
            "
            icon="pi pi-plus"
            @click="openCreate"
          />
        </template>
      </BaseDataTable>
    </BaseCard>

    <CurriculumFormDialog
      v-model="formVisible"
      :curriculum="
        selectedCurriculum
      "
      :study-programs="
        studyPrograms
      "
      :study-forms="
        studyForms
      "
      :academic-years="
        academicYears
      "
      :education-durations="
        educationDurations
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
        saveCurriculum
      "
    />

    <CurriculumDetailsDialog
      v-model="
        detailsVisible
      "
      :curriculum="
        selectedCurriculum
      "
    />
  </div>
</template>

<style scoped>
.curricula-page {
  display: grid;
  gap: 1rem;
}

.curriculum-filter {
  width: 13rem;
}

.curriculum-filter--small {
  width: 10rem;
}

.curriculum-program {
  display: grid;
  gap: 0.1rem;
}

.curriculum-program strong {
  font-size: 0.75rem;
}

.curriculum-program span {
  font-size: 0.82rem;
}

.curriculum-program small {
  color:
    var(--app-text-muted);
  font-size: 0.68rem;
}

@media (max-width: 1199px) {
  .curriculum-filter,
  .curriculum-filter--small {
    width: 100%;
  }
}
</style>
