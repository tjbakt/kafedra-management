<script setup lang="ts">
import Checkbox from 'primevue/checkbox'
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
  GroupCurriculumPayload,
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
    record?: GroupCurriculumAssignment | null

    studentGroups: StudentGroupLookup[]
    curricula: CurriculumLookup[]
    academicYears: AcademicYearLookup[]

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
    payload: GroupCurriculumPayload,
  ]
}>()

const { t } = useI18n()

const form = reactive({
  student_group:
    null as number | null,

  curriculum:
    null as number | null,

  start_academic_year:
    null as number | null,

  end_academic_year:
    null as number | null,

  is_primary: true,

  is_active: true,

  notes: '',
})

const localErrors =
  reactive<Record<string, string>>({})

const title = computed(
  () =>
    props.record
      ? t(
          'teachingSetup.groupCurricula.editTitle',
        )
      : t(
          'teachingSetup.groupCurricula.createTitle',
        ),
)

const selectedGroup =
  computed(
    () =>
      props.studentGroups.find(
        (group) =>
          group.id ===
          form.student_group,
      ) ?? null,
  )

const groupOptions =
  computed<
    SelectOption<number>[]
  >(() => {
    const result =
      props.studentGroups
        .filter(
          (group) =>
            group.is_active &&
            !group.is_archived,
        )
        .map(
          (group) => ({
            value: group.id,

            label: group.code,

            description:
              `${group.study_program_name} · ${group.study_form_name}`,
          }),
        )

    if (
      props.record &&
      !result.some(
        (option) =>
          option.value ===
          props.record
            ?.student_group,
      )
    ) {
      result.unshift({
        value:
          props.record
            .student_group,

        label:
          props.record
            .student_group_code,

        description:
          `${props.record.study_program_name} · ${props.record.study_form_name}`,
      })
    }

    return result
  })

const curriculumOptions =
  computed<
    SelectOption<number>[]
  >(() => {
    const group =
      selectedGroup.value

    const result =
      props.curricula
        .filter(
          (curriculum) =>
            curriculum.is_active &&
            !curriculum.is_archived &&
            (
              !group ||
              (
                curriculum.study_program ===
                  group.study_program &&
                curriculum.study_form ===
                  group.study_form
              )
            ),
        )
        .map(
          (curriculum) => ({
            value:
              curriculum.id,

            label:
              `${curriculum.code} · v${curriculum.version}`,

            description:
              `${curriculum.study_program_name} · ${curriculum.study_form_name} · ${curriculum.effective_academic_year_name}`,
          }),
        )

    if (
      props.record &&
      !result.some(
        (option) =>
          option.value ===
          props.record
            ?.curriculum,
      )
    ) {
      result.unshift({
        value:
          props.record.curriculum,

        label:
          props.record
            .curriculum_code,

        description:
          `${props.record.study_program_name} · ${props.record.study_form_name}`,
      })
    }

    return result
  })

const yearOptions =
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
          value: year.id,

          label: year.name,

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

const endYearOptions =
  computed<
    SelectOption<number>[]
  >(() => {
    const startYear =
      props.academicYears.find(
        (year) =>
          year.id ===
          form.start_academic_year,
      )

    return props.academicYears
      .filter(
        (year) =>
          !year.is_archived &&
          (
            !startYear ||
            year.start_year >=
              startYear.start_year
          ),
      )
      .map(
        (year) => ({
          value: year.id,
          label: year.name,
        }),
      )
  })

function clearErrors(): void {
  for (
    const key of
    Object.keys(localErrors)
  ) {
    delete localErrors[key]
  }
}

function resetForm(): void {
  form.student_group = null

  form.curriculum = null

  form.start_academic_year =
    props.academicYears.find(
      (year) =>
        year.is_current,
    )?.id ?? null

  form.end_academic_year =
    null

  form.is_primary = true

  form.is_active = true

  form.notes = ''

  clearErrors()
}

function fillForm(
  record: GroupCurriculumAssignment,
): void {
  form.student_group =
    record.student_group

  form.curriculum =
    record.curriculum

  form.start_academic_year =
    record.start_academic_year

  form.end_academic_year =
    record.end_academic_year

  form.is_primary =
    record.is_primary

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

  if (!form.student_group) {
    localErrors.student_group =
      t(
        'teachingSetup.groupCurricula.validation.groupRequired',
      )
  }

  if (!form.curriculum) {
    localErrors.curriculum =
      t(
        'teachingSetup.groupCurricula.validation.curriculumRequired',
      )
  }

  if (
    !form.start_academic_year
  ) {
    localErrors.start_academic_year =
      t(
        'teachingSetup.groupCurricula.validation.startYearRequired',
      )
  }

  if (
    form.start_academic_year &&
    form.end_academic_year
  ) {
    const start =
      props.academicYears.find(
        (year) =>
          year.id ===
          form.start_academic_year,
      )

    const end =
      props.academicYears.find(
        (year) =>
          year.id ===
          form.end_academic_year,
      )

    if (
      start &&
      end &&
      end.start_year <
        start.start_year
    ) {
      localErrors.end_academic_year =
        t(
          'teachingSetup.groupCurricula.validation.endYear',
        )
    }
  }

  return (
    Object.keys(localErrors)
      .length === 0
  )
}

function submit(): void {
  if (!validate()) {
    return
  }

  if (
    !form.student_group ||
    !form.curriculum ||
    !form.start_academic_year
  ) {
    return
  }

  emit('submit', {
    student_group:
      form.student_group,

    curriculum:
      form.curriculum,

    start_academic_year:
      form.start_academic_year,

    end_academic_year:
      form.end_academic_year,

    is_primary:
      form.is_primary,

    is_active:
      form.is_active,

    notes:
      form.notes.trim(),
  })
}

watch(
  () => form.student_group,
  () => {
    if (!form.curriculum) {
      return
    }

    const valid =
      curriculumOptions.value
        .some(
          (option) =>
            option.value ===
            form.curriculum,
        )

    if (!valid) {
      form.curriculum =
        null
    }
  },
)

watch(
  () =>
    form.start_academic_year,
  () => {
    if (
      !form.end_academic_year
    ) {
      return
    }

    const valid =
      endYearOptions.value
        .some(
          (option) =>
            option.value ===
            form.end_academic_year,
        )

    if (!valid) {
      form.end_academic_year =
        null
    }
  },
)

watch(
  () => visible.value,
  (isVisible) => {
    if (!isVisible) {
      return
    }

    if (props.record) {
      fillForm(props.record)
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
    width="58rem"
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
        group-curriculum-form
      "
      novalidate
      @submit.prevent="submit"
    >
      <div
        class="
          group-curriculum-form__grid
        "
      >
        <BaseFormField
          :label="
            t(
              'teachingSetup.groupCurricula.fields.group',
            )
          "
          name="student_group"
          required
          :error="
            fieldError(
              'student_group',
            )
          "
        >
          <Select
            v-model="
              form.student_group
            "
            :options="
              groupOptions
            "
            option-label="label"
            option-value="value"
            filter
            class="w-full"
            :disabled="loading"
          >
            <template
              #option="{ option }"
            >
              <div
                class="select-option"
              >
                <strong>
                  {{ option.label }}
                </strong>

                <small>
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
              'teachingSetup.groupCurricula.fields.curriculum',
            )
          "
          name="curriculum"
          required
          :error="
            fieldError(
              'curriculum',
            )
          "
        >
          <Select
            v-model="
              form.curriculum
            "
            :options="
              curriculumOptions
            "
            option-label="label"
            option-value="value"
            filter
            class="w-full"
            :disabled="
              loading ||
              !form.student_group
            "
          >
            <template
              #option="{ option }"
            >
              <div
                class="select-option"
              >
                <strong>
                  {{ option.label }}
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
              'teachingSetup.groupCurricula.fields.startYear',
            )
          "
          name="
            start_academic_year
          "
          required
          :error="
            fieldError(
              'start_academic_year',
            )
          "
        >
          <Select
            v-model="
              form.start_academic_year
            "
            :options="
              yearOptions
            "
            option-label="label"
            option-value="value"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'teachingSetup.groupCurricula.fields.endYear',
            )
          "
          name="
            end_academic_year
          "
          :error="
            fieldError(
              'end_academic_year',
            )
          "
        >
          <Select
            v-model="
              form.end_academic_year
            "
            :options="
              endYearOptions
            "
            option-label="label"
            option-value="value"
            show-clear
            class="w-full"
            :disabled="
              loading ||
              !form.start_academic_year
            "
          />
        </BaseFormField>
      </div>

      <div
        class="
          group-curriculum-form__flags
        "
      >
        <label>
          <Checkbox
            v-model="
              form.is_primary
            "
            binary
            :disabled="loading"
          />

          <span>
            {{
              t(
                'teachingSetup.groupCurricula.fields.primary',
              )
            }}
          </span>
        </label>

        <label>
          <Checkbox
            v-model="
              form.is_active
            "
            binary
            :disabled="loading"
          />

          <span>
            {{
              t(
                'teachingSetup.common.active',
              )
            }}
          </span>
        </label>
      </div>

      <BaseFormField
        :label="
          t(
            'teachingSetup.common.notes',
          )
        "
        name="notes"
        :error="
          fieldError('notes')
        "
      >
        <Textarea
          v-model="
            form.notes
          "
          rows="4"
          auto-resize
          class="w-full"
          :disabled="loading"
        />
      </BaseFormField>
    </form>

    <template #footer>
      <BaseFormActions
        :loading="loading"
        @cancel="
          visible = false
        "
        @submit="submit"
      />
    </template>
  </BaseDialog>
</template>

<style scoped>
.group-curriculum-form {
  display: grid;
  gap: 1rem;
}

.group-curriculum-form__grid {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.group-curriculum-form__flags {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
}

.group-curriculum-form__flags label {
  display: flex;
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
    var(--app-text-muted);
  font-size: 0.7rem;
}

@media (max-width: 767px) {
  .group-curriculum-form__grid {
    grid-template-columns:
      1fr;
  }
}
</style>
