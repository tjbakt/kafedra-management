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

import StudentGroupDetailsDialog from '@/modules/student-groups/components/StudentGroupDetailsDialog.vue'
import StudentGroupFormDialog from '@/modules/student-groups/components/StudentGroupFormDialog.vue'

import {
  getAcademicYears,
  getEducationDurations,
  getFaculties,
  getStudyForms,
  getStudyPrograms,
  studentGroupsApi,
} from '@/modules/student-groups/api'

import type {
  AcademicYearLookup,
  EducationDurationLookup,
  FacultyLookup,
  SelectOption,
  StudentGroup,
  StudentGroupPayload,
  StudyFormLookup,
  StudyProgramLookup,
} from '@/modules/student-groups/types'

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

const selectedGroup =
  ref<StudentGroup | null>(
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

const academicYears =
  ref<AcademicYearLookup[]>([])

const faculties =
  ref<FacultyLookup[]>([])

const studyPrograms =
  ref<StudyProgramLookup[]>([])

const studyForms =
  ref<StudyFormLookup[]>([])

const educationDurations =
  ref<EducationDurationLookup[]>([])

const selectedAdmissionYear =
  ref<number | null>(null)

const selectedFaculty =
  ref<number | null>(null)

const selectedProgram =
  ref<number | null>(null)

const selectedStudyForm =
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
      'academics.add_studentgroup',
    ),
)

const canEdit = computed(
  () =>
    can(
      'academics.change_studentgroup',
    ),
)

const canDelete = computed(
  () =>
    can(
      'academics.delete_studentgroup',
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

const yearOptions =
  computed<
    SelectOption<number | null>[]
  >(() => [
    {
      value: null,

      label:
        t(
          'studentGroups.allAdmissionYears',
        ),
    },

    ...academicYears.value.map(
      (year) => ({
        value: year.id,
        label: year.name,
      }),
    ),
  ])

const facultyOptions =
  computed<
    SelectOption<number | null>[]
  >(() => [
    {
      value: null,

      label:
        t(
          'studentGroups.allFaculties',
        ),
    },

    ...faculties.value.map(
      (faculty) => ({
        value: faculty.id,

        label:
          localizedName(
            faculty.name_ru,
            faculty.name_uz,
          ),
      }),
    ),
  ])

const programOptions =
  computed<
    SelectOption<number | null>[]
  >(() => [
    {
      value: null,

      label:
        t(
          'studentGroups.allPrograms',
        ),
    },

    ...studyPrograms.value.map(
      (program) => ({
        value: program.id,

        label:
          `${program.code} — ${
            localizedName(
              program.name_ru,
              program.name_uz,
            )
          }`,
      }),
    ),
  ])

const studyFormOptions =
  computed<
    SelectOption<number | null>[]
  >(() => [
    {
      value: null,

      label:
        t(
          'studentGroups.allStudyForms',
        ),
    },

    ...studyForms.value.map(
      (studyForm) => ({
        value: studyForm.id,

        label:
          localizedName(
            studyForm.name_ru,
            studyForm.name_uz,
          ),
      }),
    ),
  ])

const statusOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'studentGroups.allStatuses',
        ),
    },

    {
      value: true,

      label:
        t(
          'studentGroups.active',
        ),
    },

    {
      value: false,

      label:
        t(
          'studentGroups.inactive',
        ),
    },
  ])

const columns =
  computed<
    CrudColumn<StudentGroup>[]
  >(() => [
    {
      field: 'code',

      header:
        t(
          'studentGroups.fields.code',
        ),

      sortable: true,

      minWidth: '9rem',
    },

    {
      field:
        'admission_academic_year_name',

      header:
        t(
          'studentGroups.fields.admissionYear',
        ),

      sortable: true,

      sortField:
        'academic_year_admission__start_year',

      minWidth: '9rem',
    },

    {
      field:
        'faculty_name',

      header:
        t(
          'studentGroups.fields.faculty',
        ),

      minWidth: '14rem',
    },

    {
      field:
        'study_program_name',

      header:
        t(
          'studentGroups.fields.studyProgram',
        ),

      minWidth: '17rem',
    },

    {
      field:
        'study_form_name',

      header:
        t(
          'studentGroups.fields.studyForm',
        ),

      minWidth: '10rem',
    },

    {
      field:
        'student_count',

      header:
        t(
          'studentGroups.fields.studentCount',
        ),

      sortable: true,

      width: '9rem',

      align: 'center',
    },

    {
      field:
        'subgroup_count',

      header:
        t(
          'studentGroups.fields.subgroupCount',
        ),

      width: '9rem',

      align: 'center',
    },

    {
      field:
        'is_active',

      header:
        t(
          'studentGroups.fields.status',
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
} = useCrudList<StudentGroup>(
  (params) =>
    studentGroupsApi.list(
      params,
    ),

  {
    initialPageSize: 20,

    initialOrdering:
      '-academic_year_admission__start_year,code',
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
      yearsResponse,
      facultiesResponse,
      programsResponse,
      formsResponse,
      durationsResponse,
    ] = await Promise.all([
      getAcademicYears(),
      getFaculties(),
      getStudyPrograms(),
      getStudyForms(),
      getEducationDurations(),
    ])

    academicYears.value =
      yearsResponse.results

    faculties.value =
      facultiesResponse.results

    studyPrograms.value =
      programsResponse.results

    studyForms.value =
      formsResponse.results

    educationDurations.value =
      durationsResponse.results
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
  selectedGroup.value = null

  clearFormErrors()

  formVisible.value = true
}

function openView(
  group: StudentGroup,
): void {
  selectedGroup.value =
    group

  detailsVisible.value = true
}

function openEdit(
  group: StudentGroup,
): void {
  selectedGroup.value =
    group

  clearFormErrors()

  formVisible.value = true
}

async function saveGroup(
  payload: StudentGroupPayload,
): Promise<void> {
  saving.value = true

  clearFormErrors()

  try {
    if (selectedGroup.value) {
      await studentGroupsApi.update(
        selectedGroup.value.id,
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.updated'),
      )
    } else {
      await studentGroupsApi.create(
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.created'),
      )
    }

    formVisible.value = false

    selectedGroup.value = null

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

function archiveGroup(
  group: StudentGroup,
): void {
  confirmDelete({
    header:
      t(
        'studentGroups.archiveTitle',
      ),

    message:
      t(
        'studentGroups.archiveConfirm',
        {
          code:
            group.code,
        },
      ),

    accept: async () => {
      try {
        await studentGroupsApi.remove(
          group.id,
        )

        toast.success(
          t('common.success'),

          t(
            'studentGroups.archived',
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

async function applyAdmissionYearFilter(): Promise<void> {
  setFilter(
    'academic_year_admission',
    selectedAdmissionYear.value,
  )

  await load()
}

async function applyFacultyFilter(): Promise<void> {
  setFilter(
    'faculty',
    selectedFaculty.value,
  )

  await load()
}

async function applyProgramFilter(): Promise<void> {
  setFilter(
    'study_program',
    selectedProgram.value,
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

async function applyStatusFilter(): Promise<void> {
  setFilter(
    'is_active',
    selectedActive.value,
  )

  await load()
}

async function resetFilters(): Promise<void> {
  selectedAdmissionYear.value =
    null

  selectedFaculty.value =
    null

  selectedProgram.value =
    null

  selectedStudyForm.value =
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
    class="student-groups-page"
  >
    <BasePageHeader
      :title="
        t(
          'studentGroups.title',
        )
      "
      :description="
        t(
          'studentGroups.description',
        )
      "
      icon="pi pi-users"
    >
      <template #actions>
        <Button
          v-if="canCreate"
          :label="
            t(
              'studentGroups.create',
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
          'studentGroups.searchPlaceholder',
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
            selectedAdmissionYear
          "
          :options="
            yearOptions
          "
          option-label="label"
          option-value="value"
          class="group-filter"
          @change="
            applyAdmissionYearFilter
          "
        />

        <Select
          v-model="
            selectedFaculty
          "
          :options="
            facultyOptions
          "
          option-label="label"
          option-value="value"
          filter
          class="group-filter"
          @change="
            applyFacultyFilter
          "
        />

        <Select
          v-model="
            selectedProgram
          "
          :options="
            programOptions
          "
          option-label="label"
          option-value="value"
          filter
          class="group-filter"
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
          class="group-filter"
          @change="
            applyStudyFormFilter
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
            group-filter
            group-filter--status
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
          #status="{ row }"
        >
          <Tag
            :value="
              row.is_active
                ? t(
                    'studentGroups.active',
                  )
                : t(
                    'studentGroups.inactive',
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
                'studentGroups.archive',
              )
            "
            icon="pi pi-box"
            severity="danger"
            text
            rounded
            @click.stop="
              archiveGroup(row)
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
                'studentGroups.create',
              )
            "
            icon="pi pi-plus"
            @click="openCreate"
          />
        </template>
      </BaseDataTable>
    </BaseCard>

    <StudentGroupFormDialog
      v-model="formVisible"
      :student-group="
        selectedGroup
      "
      :academic-years="
        academicYears
      "
      :faculties="
        faculties
      "
      :study-programs="
        studyPrograms
      "
      :study-forms="
        studyForms
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
      @submit="saveGroup"
    />

    <StudentGroupDetailsDialog
      v-model="
        detailsVisible
      "
      :student-group="
        selectedGroup
      "
    />
  </div>
</template>

<style scoped>
.student-groups-page {
  display: grid;
  gap: 1rem;
}

.group-filter {
  width: 13rem;
}

.group-filter--status {
  width: 10rem;
}

@media (max-width: 1199px) {
  .group-filter,
  .group-filter--status {
    width: 100%;
  }
}
</style>
