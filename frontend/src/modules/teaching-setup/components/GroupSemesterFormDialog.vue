<script setup lang="ts">
import Checkbox from 'primevue/checkbox'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'

import {
  computed,
  reactive,
  watch,
} from 'vue'

import {
  useI18n,
} from 'vue-i18n'

import BaseDialog from '@/components/base/BaseDialog.vue'
import BaseFormActions from '@/components/base/BaseFormActions.vue'
import BaseFormField from '@/components/base/BaseFormField.vue'

import FormValidationSummary from '@/components/forms/FormValidationSummary.vue'

import type {
  AcademicYearLookup,
  CurriculumLookup,
  GroupCurriculumAssignment,
  GroupSemester,
  GroupSemesterPayload,
  GroupSemesterStatus,
  SelectOption,
  StudentGroupLookup,
} from '@/modules/teaching-setup/types'

import type {
  FieldErrors,
} from '@/types/validation'

import {
  getFieldError,
} from '@/utils/api-errors'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props = withDefaults(
  defineProps<{
    record?: GroupSemester | null

    groupCurricula:
      GroupCurriculumAssignment[]

    curricula:
      CurriculumLookup[]

    studentGroups:
      StudentGroupLookup[]

    academicYears:
      AcademicYearLookup[]

    loading?: boolean

    fieldErrors?: FieldErrors

    nonFieldErrors?: string[]

    generalError?: string
  }>(),
  {
    record: null,

    loading: false,

    fieldErrors: () => ({}),

    nonFieldErrors: () => [],

    generalError: '',
  },
)

const emit = defineEmits<{
  submit: [
    payload:
      GroupSemesterPayload,
  ]
}>()

const { t } =
  useI18n()

const form =
  reactive({
    group_curriculum:
      null as number | null,

    academic_year:
      null as number | null,

    semester_number:
      null as number | null,

    weeks_count: 15,

    students_count: 0,

    subgroup_count: 1,

    status: 'planned' as GroupSemesterStatus,

    is_active: true,

    notes: '',
  })

const localErrors =
  reactive<
    Record<string, string>
  >({})

const title =
  computed(
    () =>
      props.record
        ? t(
            'teachingSetup.groupSemesters.editTitle',
          )
        : t(
            'teachingSetup.groupSemesters.createTitle',
          ),
  )

const selectedAssignment =
  computed(
    () =>
      props.groupCurricula.find(
        (item) =>
          item.id ===
          form.group_curriculum,
      ) ?? null,
  )

const selectedAcademicYear =
  computed(
    () =>
      props.academicYears.find(
        (item) =>
          item.id ===
          form.academic_year,
      ) ?? null,
  )

const selectedCurriculum =
  computed(
    () => {
      const assignment =
        selectedAssignment.value

      if (!assignment) {
        return null
      }

      return (
        props.curricula.find(
          (curriculum) =>
            curriculum.id ===
            assignment.curriculum,
        ) ?? null
      )
    },
  )

const selectedStudentGroup =
  computed(
    () => {
      const assignment =
        selectedAssignment.value

      if (!assignment) {
        return null
      }

      return (
        props.studentGroups.find(
          (group) =>
            group.id ===
            assignment.student_group,
        ) ?? null
      )
    },
  )

const groupCurriculumOptions =
  computed<
    SelectOption<number>[]
  >(() =>
    props.groupCurricula
      .filter(
        (assignment) =>
          assignment.is_active &&
          !assignment.is_archived,
      )
      .map(
        (assignment) => ({
          value:
            assignment.id,

          label:
            `${assignment.student_group_code} → ${assignment.curriculum_code}`,

          description:
            `${assignment.study_program_name} · ${assignment.study_form_name}`,
        }),
      ),
  )

const academicYearOptions =
  computed<
    SelectOption<number>[]
  >(() =>
    props.academicYears
      .filter(
        (year) =>
          !year.is_archived,
      )
      .map(
        (year) => ({
          value:
            year.id,

          label:
            year.name,

          description:
            year.is_current
              ? t(
                  'teachingSetup.currentYear',
                )
              : year.is_closed
                ? t(
                    'teachingSetup.closedYear',
                  )
                : '',
        }),
      ),
  )

/**
 * Семестры ограничиваются выбранным
 * учебным годом назначения плана.
 *
 * Например:
 * начало обучения 2024/2025
 *
 * 2024/2025 -> 1, 2
 * 2025/2026 -> 3, 4
 * 2026/2027 -> 5, 6
 */
const semesterNumberOptions =
  computed<
    SelectOption<number>[]
  >(() => {
    const assignment =
      selectedAssignment.value

    const academicYear =
      selectedAcademicYear.value

    const curriculum =
      selectedCurriculum.value

    if (
      !assignment ||
      !academicYear ||
      !curriculum
    ) {
      return []
    }

    const startYear =
      props.academicYears.find(
        (item) =>
          item.id ===
          assignment.start_academic_year,
      )

    if (!startYear) {
      return []
    }

    const yearIndex =
      academicYear.start_year -
      startYear.start_year

    if (yearIndex < 0) {
      return []
    }

    const firstSemester =
      yearIndex * 2 + 1

    const semestersCount =
      Number(
        curriculum.semesters_count ??
        0,
      )

    return [
      firstSemester,
      firstSemester + 1,
    ]
      .filter(
        (semesterNumber) =>
          semesterNumber <=
          semestersCount,
      )
      .map(
        (semesterNumber) => {
          const season =
            semesterNumber % 2 === 1
              ? t(
                  'teachingSetup.seasons.autumn',
                )
              : t(
                  'teachingSetup.seasons.spring',
                )

          return {
            value:
              semesterNumber,

            label:
              t(
                'teachingSetup.groupSemesters.semesterOption',
                {
                  semester:
                    semesterNumber,

                  season,
                },
              ),
          }
        },
      )
  })

const statusOptions =
  computed<
    SelectOption<GroupSemesterStatus>[]
  >(() => [
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
  for (
    const key
    of Object.keys(
      localErrors,
    )
  ) {
    delete localErrors[
      key
    ]
  }
}

function resetForm(): void {
  form.group_curriculum =
    null

  form.academic_year =
    props.academicYears.find(
      (year) =>
        year.is_current,
    )?.id ?? null

  form.semester_number =
    null

  form.weeks_count =
    15

  form.students_count =
    0

  form.subgroup_count =
    1

  form.status =
    'planned'

  form.is_active =
    true

  form.notes = ''

  clearErrors()
}

function fillForm(
  record: GroupSemester,
): void {
  form.group_curriculum =
    record.group_curriculum

  form.academic_year =
    record.academic_year

  form.semester_number =
    record.semester_number

  form.weeks_count = record.weeks_count ?? 15

  form.students_count =
    record.students_count

  form.subgroup_count =
    record.subgroup_count

  form.status =
    record.status

  form.is_active =
    record.is_active

  form.notes =
    record.notes

  clearErrors()
}

function fieldError(
  field: string,
): string {
  return (
    localErrors[field] ||
    getFieldError(
      props.fieldErrors,
      field,
    )
  )
}

function validate(): boolean {
  clearErrors()

  if (!form.group_curriculum) {
    localErrors.group_curriculum =
      t(
        'teachingSetup.groupSemesters.validation.assignmentRequired',
      )
  }

  if (!form.academic_year) {
    localErrors.academic_year =
      t(
        'teachingSetup.groupSemesters.validation.yearRequired',
      )
  }

  if (!form.semester_number) {
    localErrors.semester_number =
      t(
        'teachingSetup.groupSemesters.validation.semesterNumberRequired',
      )
  }

  if (
    form.weeks_count < 1 ||
    form.weeks_count > 30
  ) {
    localErrors.weeks_count =
      t(
        'teachingSetup.groupSemesters.validation.weeksCount',
      )
  }

  if (
    form.students_count < 0 ||
    form.students_count > 1000
  ) {
    localErrors.students_count =
      t(
        'teachingSetup.groupSemesters.validation.students',
      )
  }

  if (
    form.subgroup_count < 1 ||
    form.subgroup_count > 100
  ) {
    localErrors.subgroup_count =
      t(
        'teachingSetup.groupSemesters.validation.subgroups',
      )
  }

  return (
    Object.keys(
      localErrors,
    ).length === 0
  )
}

function submit(): void {
  if (!validate()) {
    return
  }

  if (
    !form.group_curriculum ||
    !form.academic_year ||
    !form.semester_number
  ) {
    return
  }

  emit(
    'submit',
    {
      group_curriculum:
        form.group_curriculum,

      academic_year:
        form.academic_year,

      semester_number:
        form.semester_number,

      weeks_count:
        form.weeks_count,

      students_count:
        form.students_count,

      subgroup_count:
        form.subgroup_count,

      status:
        form.status,

      is_active:
        form.is_active,

      notes:
        form.notes.trim(),
    },
  )
}

watch(
  () =>
    form.group_curriculum,
  () => {
    if (props.record) {
      return
    }

    form.semester_number =
      null

    const group =
      selectedStudentGroup.value

    if (group) {
      form.students_count =
        group.student_count

      form.subgroup_count =
        group.subgroup_count
    }
  },
)

watch(
  () =>
    form.academic_year,
  () => {
    if (props.record) {
      return
    }

    if (!form.semester_number) {
      return
    }

    const valid =
      semesterNumberOptions.value
        .some(
          (option) =>
            option.value ===
            form.semester_number,
        )

    if (!valid) {
      form.semester_number =
        null
    }
  },
)

watch(
  semesterNumberOptions,
  (
    options,
  ) => {
    if (
      props.record ||
      form.semester_number ||
      options.length !== 1
    ) {
      return
    }

    const first =
      options[0]

    if (first) {
      form.semester_number =
        first.value
    }
  },
)

watch(
  () =>
    visible.value,
  (
    isVisible,
  ) => {
    if (!isVisible) {
      return
    }

    if (props.record) {
      fillForm(
        props.record,
      )
    } else {
      resetForm()
    }
  },
)
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="title"
    width="60rem"
    :loading="loading"
  >
    <FormValidationSummary
      :field-errors="
        fieldErrors
      "
      :non-field-errors="
        nonFieldErrors
      "
      :general-error="
        generalError
      "
    />

    <form
      class="
        group-semester-form
      "
      novalidate
      @submit.prevent="
        submit
      "
    >
      <div
        class="
          group-semester-form__grid
        "
      >
        <BaseFormField
          class="
            group-semester-form__wide
          "
          :label="
            t(
              'teachingSetup.groupSemesters.fields.assignment',
            )
          "
          name="
            group_curriculum
          "
          required
          :error="
            fieldError(
              'group_curriculum',
            )
          "
        >
          <Select
            v-model="
              form.group_curriculum
            "
            :options="
              groupCurriculumOptions
            "
            option-label="label"
            option-value="value"
            filter
            class="w-full"
            :disabled="
              loading
            "
          >
            <template
              #option="
                { option }
              "
            >
              <div
                class="
                  select-option
                "
              >
                <strong>
                  {{
                    option.label
                  }}
                </strong>

                <small
                  v-if="
                    option.description
                  "
                >
                  {{
                    option.description
                  }}
                </small>
              </div>
            </template>
          </Select>
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'teachingSetup.groupSemesters.fields.academicYear',
            )
          "
          name="
            academic_year
          "
          required
          :error="
            fieldError(
              'academic_year',
            )
          "
        >
          <Select
            v-model="
              form.academic_year
            "
            :options="
              academicYearOptions
            "
            option-label="label"
            option-value="value"
            class="w-full"
            :disabled="
              loading ||
              !form.group_curriculum
            "
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'teachingSetup.groupSemesters.fields.semesterNumber',
            )
          "
          name="
            semester_number
          "
          required
          :error="
            fieldError(
              'semester_number',
            )
          "
        >
          <Select
            v-model="
              form.semester_number
            "
            :options="
              semesterNumberOptions
            "
            option-label="label"
            option-value="value"
            class="w-full"
            :disabled="
              loading ||
              !form.group_curriculum ||
              !form.academic_year
            "
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'teachingSetup.groupSemesters.fields.weeksCount',
            )
          "
          name="
            weeks_count
          "
          required
          :error="
            fieldError(
              'weeks_count',
            )
          "
        >
          <InputNumber
            v-model="
              form.weeks_count
            "
            :min="1"
            :max="30"
            :use-grouping="
              false
            "
            class="w-full"
            input-class="
              w-full
            "
            :disabled="
              loading
            "
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'teachingSetup.groupSemesters.fields.status',
            )
          "
          name="status"
          required
        >
          <Select
            v-model="
              form.status
            "
            :options="
              statusOptions
            "
            option-label="label"
            option-value="value"
            class="w-full"
            :disabled="
              loading
            "
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'teachingSetup.groupSemesters.fields.studentsCount',
            )
          "
          name="
            students_count
          "
          required
          :error="
            fieldError(
              'students_count',
            )
          "
        >
          <InputNumber
            v-model="
              form.students_count
            "
            :min="0"
            :max="1000"
            :use-grouping="
              false
            "
            class="w-full"
            input-class="
              w-full
            "
            :disabled="
              loading
            "
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'teachingSetup.groupSemesters.fields.subgroupCount',
            )
          "
          name="
            subgroup_count
          "
          required
          :error="
            fieldError(
              'subgroup_count',
            )
          "
        >
          <InputNumber
            v-model="
              form.subgroup_count
            "
            :min="1"
            :max="100"
            :use-grouping="
              false
            "
            class="w-full"
            input-class="
              w-full
            "
            :disabled="
              loading
            "
          />
        </BaseFormField>
      </div>

      <BaseFormField
        :label="
          t(
            'teachingSetup.common.notes',
          )
        "
        name="notes"
        :error="
          fieldError(
            'notes',
          )
        "
      >
        <Textarea
          v-model="
            form.notes
          "
          rows="4"
          auto-resize
          class="w-full"
          :disabled="
            loading
          "
        />
      </BaseFormField>

      <label
        class="
          group-semester-form__active
        "
      >
        <Checkbox
          v-model="
            form.is_active
          "
          binary
          :disabled="
            loading
          "
        />

        <span>
          {{
            t(
              'teachingSetup.common.active',
            )
          }}
        </span>
      </label>
    </form>

    <template #footer>
      <BaseFormActions
        :loading="
          loading
        "
        @cancel="
          visible = false
        "
        @submit="
          submit
        "
      />
    </template>
  </BaseDialog>
</template>

<style scoped>
.group-semester-form {
  display: grid;
  gap: 1rem;
}

.group-semester-form__grid {
  display: grid;

  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );

  gap: 1rem;
}

.group-semester-form__wide {
  grid-column:
    1 / -1;
}

.group-semester-form__active {
  display: flex;

  width: fit-content;

  align-items: center;

  gap: 0.5rem;

  font-size: 0.82rem;
  font-weight: 600;
}

.select-option {
  display: grid;
  gap: 0.15rem;
}

.select-option small {
  color:
    var(
      --app-text-muted,
      #6b7280
    );

  font-size: 0.7rem;
}

@media (
  max-width: 767px
) {
  .group-semester-form__grid {
    grid-template-columns:
      1fr;
  }

  .group-semester-form__wide {
    grid-column: auto;
  }
}
</style>
