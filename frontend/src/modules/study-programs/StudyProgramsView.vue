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

import StudyProgramDetailsDialog from '@/modules/study-programs/components/StudyProgramDetailsDialog.vue'
import StudyProgramFormDialog from '@/modules/study-programs/components/StudyProgramFormDialog.vue'

import {
  getDepartments,
  getEducationLevels,
  getUniversities,
  studyProgramsApi,
} from '@/modules/study-programs/api'

import type {
  DepartmentLookup,
  EducationLevelLookup,
  SelectOption,
  StudyProgram,
  StudyProgramPayload,
  UniversityLookup,
} from '@/modules/study-programs/types'

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

const selectedStudyProgram =
  ref<StudyProgram | null>(
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

const universities =
  ref<UniversityLookup[]>([])

const educationLevels =
  ref<EducationLevelLookup[]>([])

const departments =
  ref<DepartmentLookup[]>([])

const selectedUniversity =
  ref<number | null>(null)

const selectedEducationLevel =
  ref<number | null>(null)

const selectedDepartment =
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
      'academics.add_studyprogram',
    ),
)

const canEdit = computed(
  () =>
    can(
      'academics.change_studyprogram',
    ),
)

const canDelete = computed(
  () =>
    can(
      'academics.delete_studyprogram',
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

function getStudyProgramName(
  record: StudyProgram,
): string {
  return localizedName(
    record.name_ru,
    record.name_uz,
  )
}

const universityFilterOptions =
  computed<
    SelectOption<
      number | null
    >[]
  >(() => [
    {
      value: null,

      label:
        t(
          'studyPrograms.allUniversities',
        ),
    },

    ...universities.value.map(
      (item) => ({
        value: item.id,

        label:
          localizedName(
            item.name_ru,
            item.name_uz,
          ),
      }),
    ),
  ])

const educationLevelFilterOptions =
  computed<
    SelectOption<
      number | null
    >[]
  >(() => [
    {
      value: null,

      label:
        t(
          'studyPrograms.allEducationLevels',
        ),
    },

    ...educationLevels.value.map(
      (item) => ({
        value: item.id,

        label:
          localizedName(
            item.name_ru,
            item.name_uz,
          ),
      }),
    ),
  ])

const departmentFilterOptions =
  computed<
    SelectOption<
      number | null
    >[]
  >(() => {
    const source =
      selectedUniversity.value
        ? departments.value.filter(
            (item) =>
              item.university ===
              selectedUniversity.value,
          )
        : departments.value

    return [
      {
        value: null,

        label:
          t(
            'studyPrograms.allDepartments',
          ),
      },

      ...source.map(
        (item) => ({
          value: item.id,

          label:
            localizedName(
              item.name_ru,
              item.name_uz,
            ),

          description:
            item.faculty_name,
        }),
      ),
    ]
  })

const statusOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'studyPrograms.allStatuses',
        ),
    },

    {
      value: true,

      label:
        t(
          'studyPrograms.active',
        ),
    },

    {
      value: false,

      label:
        t(
          'studyPrograms.inactive',
        ),
    },
  ])

const columns =
  computed<
    CrudColumn<StudyProgram>[]
  >(() => [
    {
      field: 'code',

      header:
        t(
          'studyPrograms.fields.code',
        ),

      sortable: true,

      minWidth: '9rem',
    },

    {
      field:
        'display_name',

      header:
        t(
          'studyPrograms.fields.name',
        ),

      sortable: true,

      sortField:
        localeStore.locale ===
        'uz'
          ? 'name_uz'
          : 'name_ru',

      bodySlot:
        'studyProgramName',

      minWidth: '18rem',
    },

    {
      field:
        'education_level_name',

      header:
        t(
          'studyPrograms.fields.educationLevel',
        ),

      minWidth: '11rem',
    },

    {
      field:
        'profiling_faculty_name',

      header:
        t(
          'studyPrograms.fields.profilingFaculty',
        ),

      minWidth: '13rem',
    },

    {
      field:
        'profiling_department_name',

      header:
        t(
          'studyPrograms.fields.profilingDepartment',
        ),

      minWidth: '14rem',
    },

    {
      field:
        'is_active',

      header:
        t(
          'studyPrograms.fields.status',
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
} = useCrudList<StudyProgram>(
  (params) =>
    studyProgramsApi.list(
      params,
    ),

  {
    initialPageSize: 20,

    initialOrdering:
      'sort_order,code',
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
      universityResponse,
      levelResponse,
      departmentResponse,
    ] = await Promise.all([
      getUniversities(),
      getEducationLevels(),
      getDepartments(),
    ])

    universities.value =
      universityResponse.results

    educationLevels.value =
      levelResponse.results

    departments.value =
      departmentResponse.results
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
  selectedStudyProgram.value =
    null

  clearFormErrors()

  formVisible.value = true
}

function openView(
  record: StudyProgram,
): void {
  selectedStudyProgram.value =
    record

  detailsVisible.value = true
}

function openEdit(
  record: StudyProgram,
): void {
  selectedStudyProgram.value =
    record

  clearFormErrors()

  formVisible.value = true
}

async function saveStudyProgram(
  payload: StudyProgramPayload,
): Promise<void> {
  saving.value = true

  clearFormErrors()

  try {
    if (
      selectedStudyProgram.value
    ) {
      await studyProgramsApi.update(
        selectedStudyProgram.value.id,
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.updated'),
      )
    } else {
      await studyProgramsApi.create(
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.created'),
      )
    }

    formVisible.value = false

    selectedStudyProgram.value =
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

function archiveStudyProgram(
  record: StudyProgram,
): void {
  confirmDelete({
    header:
      t(
        'studyPrograms.archiveTitle',
      ),

    message:
      t(
        'studyPrograms.archiveConfirm',
        {
          name:
            getStudyProgramName(
              record,
            ),
        },
      ),

    accept: async () => {
      try {
        await studyProgramsApi.remove(
          record.id,
        )

        toast.success(
          t('common.success'),

          t(
            'studyPrograms.archived',
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

  selectedDepartment.value =
    null

  setFilter(
    'profiling_department',
    undefined,
  )

  await load()
}

async function applyEducationLevelFilter(): Promise<void> {
  setFilter(
    'education_level',
    selectedEducationLevel.value,
  )

  await load()
}

async function applyDepartmentFilter(): Promise<void> {
  setFilter(
    'profiling_department',
    selectedDepartment.value,
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
  selectedUniversity.value =
    null

  selectedEducationLevel.value =
    null

  selectedDepartment.value =
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
    class="study-programs-page"
  >
    <BasePageHeader
      :title="
        t(
          'studyPrograms.title',
        )
      "
      :description="
        t(
          'studyPrograms.description',
        )
      "
      icon="pi pi-book"
    >
      <template #actions>
        <Button
          v-if="canCreate"
          :label="
            t(
              'studyPrograms.create',
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
          'studyPrograms.searchPlaceholder',
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
            selectedUniversity
          "
          :options="
            universityFilterOptions
          "
          option-label="label"
          option-value="value"
          filter
          class="
            study-program-filter
          "
          @change="
            applyUniversityFilter
          "
        />

        <Select
          v-model="
            selectedEducationLevel
          "
          :options="
            educationLevelFilterOptions
          "
          option-label="label"
          option-value="value"
          class="
            study-program-filter
          "
          @change="
            applyEducationLevelFilter
          "
        />

        <Select
          v-model="
            selectedDepartment
          "
          :options="
            departmentFilterOptions
          "
          option-label="label"
          option-value="value"
          filter
          class="
            study-program-filter
          "
          @change="
            applyDepartmentFilter
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
            study-program-filter
            study-program-filter--status
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
          #studyProgramName="{ row }"
        >
          {{
            getStudyProgramName(
              row,
            )
          }}
        </template>

        <template
          #status="{ row }"
        >
          <Tag
            :value="
              row.is_active
                ? t(
                    'studyPrograms.active',
                  )
                : t(
                    'studyPrograms.inactive',
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
                'studyPrograms.archive',
              )
            "
            icon="pi pi-box"
            severity="danger"
            text
            rounded
            @click.stop="
              archiveStudyProgram(
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
                'studyPrograms.create',
              )
            "
            icon="pi pi-plus"
            @click="openCreate"
          />
        </template>
      </BaseDataTable>
    </BaseCard>

    <StudyProgramFormDialog
      v-model="formVisible"
      :study-program="
        selectedStudyProgram
      "
      :universities="
        universities
      "
      :education-levels="
        educationLevels
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
        saveStudyProgram
      "
    />

    <StudyProgramDetailsDialog
      v-model="
        detailsVisible
      "
      :study-program="
        selectedStudyProgram
      "
    />
  </div>
</template>

<style scoped>
.study-programs-page {
  display: grid;
  gap: 1rem;
}

.study-program-filter {
  width: 14rem;
}

.study-program-filter--status {
  width: 11rem;
}

@media (max-width: 1199px) {
  .study-program-filter,
  .study-program-filter--status {
    width: 100%;
  }
}
</style>
