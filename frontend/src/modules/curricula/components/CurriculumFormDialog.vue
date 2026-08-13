<script setup lang="ts">
import Checkbox from 'primevue/checkbox'
import DatePicker from 'primevue/datepicker'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
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

import {
  useLocaleStore,
} from '@/stores/locale'

import type {
  AcademicYearLookup,
  Curriculum,
  CurriculumPayload,
  CurriculumStatus,
  EducationDurationLookup,
  SelectOption,
  StudyFormLookup,
  StudyProgramLookup,
} from '@/modules/curricula/types'

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
    curriculum?: Curriculum | null

    studyPrograms: StudyProgramLookup[]
    studyForms: StudyFormLookup[]
    academicYears: AcademicYearLookup[]
    educationDurations: EducationDurationLookup[]

    loading?: boolean

    fieldErrors?: FieldErrors
    nonFieldErrors?: string[]
    generalError?: string
  }>(),
  {
    curriculum: null,

    loading: false,

    fieldErrors: () => ({}),
    nonFieldErrors: () => [],
    generalError: '',
  },
)

const emit = defineEmits<{
  submit: [
    payload: CurriculumPayload,
  ]
}>()

const { t } = useI18n()

const localeStore =
  useLocaleStore()

const form = reactive({
  code: '',

  version:
    1 as number | null,

  study_program:
    null as number | null,

  study_form:
    null as number | null,

  effective_academic_year:
    null as number | null,

  status:
    'draft' as CurriculumStatus,

  approved_at:
    null as Date | null,

  approval_document: '',

  is_active: true,

  notes: '',
})

const localErrors =
  reactive<Record<string, string>>({})

const dialogTitle = computed(
  () =>
    props.curriculum
      ? t(
          'curricula.editTitle',
        )
      : t(
          'curricula.createTitle',
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

const studyProgramOptions =
  computed<
    SelectOption<number>[]
  >(() => {
    const result =
      props.studyPrograms
        .filter(
          (program) =>
            program.is_active &&
            !program.is_archived,
        )
        .map((program) => ({
          value:
            program.id,

          label:
            `${program.code} — ${
              localizedName(
                program.name_ru,
                program.name_uz,
              )
            }`,

          description:
            program.education_level_name,
        }))

    if (
      props.curriculum &&
      !result.some(
        (option) =>
          option.value ===
          props.curriculum
            ?.study_program,
      )
    ) {
      result.unshift({
        value:
          props.curriculum
            .study_program,

        label:
          `${props.curriculum.study_program_code} — ${props.curriculum.study_program_name}`,

        description:
          props.curriculum
            .education_level_name,
      })
    }

    return result
  })

const selectedProgram =
  computed(
    () =>
      props.studyPrograms.find(
        (program) =>
          program.id ===
          form.study_program,
      ) ?? null,
  )

const availableDurations =
  computed(
    () => {
      const educationLevel =
        selectedProgram.value
          ?.education_level

      if (!educationLevel) {
        return []
      }

      return props.educationDurations.filter(
        (duration) =>
          duration.education_level ===
            educationLevel &&
          duration.is_active &&
          !duration.is_archived,
      )
    },
  )

const studyFormOptions =
  computed<
    SelectOption<number>[]
  >(() => {
    const allowedIds =
      new Set(
        availableDurations.value.map(
          (duration) =>
            duration.study_form,
        ),
      )

    const result =
      props.studyForms
        .filter(
          (studyForm) =>
            studyForm.is_active &&
            !studyForm.is_archived &&
            allowedIds.has(
              studyForm.id,
            ),
        )
        .map((studyForm) => ({
          value:
            studyForm.id,

          label:
            localizedName(
              studyForm.name_ru,
              studyForm.name_uz,
            ),

          description:
            studyForm.code,
        }))

    if (
      props.curriculum &&
      !result.some(
        (option) =>
          option.value ===
          props.curriculum
            ?.study_form,
      )
    ) {
      result.unshift({
        value: props.curriculum.study_form,
        label: props.curriculum.study_form_name,
        description: '',
      })
    }

    return result
  })

const selectedDuration =
  computed(
    () =>
      availableDurations.value.find(
        (duration) =>
          duration.study_form ===
          form.study_form,
      ) ?? null,
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
      .map((year) => ({
        value:
          year.id,

        label:
          year.name,

        description:
          year.is_current
            ? t(
                'curricula.currentAcademicYear',
              )
            : year.is_closed
              ? t(
                  'curricula.closedAcademicYear',
                )
              : '',
      })),
  )

const statusOptions =
  computed<
    SelectOption<CurriculumStatus>[]
  >(() => [
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

function parseDate(
  value: string | null,
): Date | null {
  if (!value) {
    return null
  }

  const [
    year,
    month,
    day,
  ] = value
    .split('-')
    .map(Number)

  return new Date(
    year!,
    month! - 1,
    day!,
  )
}

function serializeDate(
  value: Date | null,
): string | null {
  if (!value) {
    return null
  }

  const year =
    value.getFullYear()

  const month =
    String(
      value.getMonth() + 1,
    ).padStart(2, '0')

  const day =
    String(
      value.getDate(),
    ).padStart(2, '0')

  return `${year}-${month}-${day}`
}

function clearLocalErrors(): void {
  for (
    const key of
    Object.keys(localErrors)
  ) {
    delete localErrors[key]
  }
}

function resetForm(): void {
  form.code = ''

  form.version = 1

  form.study_program =
    null

  form.study_form =
    null

  form.effective_academic_year =
    null

  form.status =
    'draft'

  form.approved_at =
    null

  form.approval_document =
    ''

  form.is_active =
    true

  form.notes = ''

  clearLocalErrors()
}

function fillForm(
  curriculum: Curriculum,
): void {
  form.code =
    curriculum.code

  form.version =
    curriculum.version

  form.study_program =
    curriculum.study_program

  form.study_form =
    curriculum.study_form

  form.effective_academic_year =
    curriculum.effective_academic_year

  form.status =
    curriculum.status

  form.approved_at =
    parseDate(
      curriculum.approved_at,
    )

  form.approval_document =
    curriculum.approval_document

  form.is_active =
    curriculum.is_active

  form.notes =
    curriculum.notes

  clearLocalErrors()
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
  clearLocalErrors()

  if (!form.code.trim()) {
    localErrors.code =
      t(
        'curricula.validation.codeRequired',
      )
  }

  if (
    !form.version ||
    form.version < 1
  ) {
    localErrors.version =
      t(
        'curricula.validation.version',
      )
  }

  if (!form.study_program) {
    localErrors.study_program =
      t(
        'curricula.validation.programRequired',
      )
  }

  if (!form.study_form) {
    localErrors.study_form =
      t(
        'curricula.validation.studyFormRequired',
      )
  }

  if (
    !form.effective_academic_year
  ) {
    localErrors.effective_academic_year =
      t(
        'curricula.validation.academicYearRequired',
      )
  }

  if (
    form.status ===
      'approved' &&
    !form.approved_at
  ) {
    localErrors.approved_at =
      t(
        'curricula.validation.approvalDateRequired',
      )
  }

  if (
    form.study_program &&
    form.study_form &&
    !selectedDuration.value
  ) {
    localErrors.study_form =
      t(
        'curricula.validation.durationMissing',
      )
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
    !form.version ||
    !form.study_program ||
    !form.study_form ||
    !form.effective_academic_year
  ) {
    return
  }

  emit('submit', {
    code:
      form.code
        .trim()
        .toUpperCase(),

    version:
      form.version,

    study_program:
      form.study_program,

    study_form:
      form.study_form,

    effective_academic_year:
      form.effective_academic_year,

    status:
      form.status,

    approved_at:
      serializeDate(
        form.approved_at,
      ),

    approval_document:
      form.approval_document
        .trim(),

    is_active:
      form.is_active,

    notes:
      form.notes.trim(),
  })
}

watch(
  () => form.study_program,
  () => {
    if (!form.study_form) {
      return
    }

    if (
      !studyFormOptions.value.some(
        (option) =>
          option.value ===
          form.study_form,
      )
    ) {
      form.study_form =
        null
    }
  },
)

watch(
  () => form.status,
  (status) => {
    if (
      status !== 'approved'
    ) {
      /*
       * Дату специально не очищаем,
       * чтобы пользователь мог временно
       * сменить статус и вернуть его.
       */
      return
    }
  },
)

watch(
  () => visible.value,
  (isVisible) => {
    if (!isVisible) {
      return
    }

    if (props.curriculum) {
      fillForm(
        props.curriculum,
      )

      return
    }

    resetForm()
  },
)

watch(
  () => props.curriculum,
  (curriculum) => {
    if (
      visible.value &&
      curriculum
    ) {
      fillForm(
        curriculum,
      )
    }
  },
)
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="dialogTitle"
    width="62rem"
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
      class="curriculum-form"
      novalidate
      @submit.prevent="submit"
    >
      <section>
        <h3>
          {{
            t(
              'curricula.sections.general',
            )
          }}
        </h3>

        <div
          class="
            curriculum-form__grid
          "
        >
          <BaseFormField
            :label="
              t(
                'curricula.fields.code',
              )
            "
            name="code"
            required
            :error="
              fieldError('code')
            "
          >
            <InputText
              v-model="form.code"
              maxlength="100"
              class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'curricula.fields.version',
              )
            "
            name="version"
            required
            :error="
              fieldError(
                'version',
              )
            "
          >
            <InputNumber
              v-model="
                form.version
              "
              :min="1"
              :max="999"
              :use-grouping="false"
              class="w-full"
              input-class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            class="
              curriculum-form__wide
            "
            :label="
              t(
                'curricula.fields.studyProgram',
              )
            "
            name="study_program"
            required
            :error="
              fieldError(
                'study_program',
              )
            "
          >
            <Select
              v-model="
                form.study_program
              "
              :options="
                studyProgramOptions
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
                'curricula.fields.studyForm',
              )
            "
            name="study_form"
            required
            :error="
              fieldError(
                'study_form',
              )
            "
          >
            <Select
              v-model="
                form.study_form
              "
              :options="
                studyFormOptions
              "
              option-label="label"
              option-value="value"
              class="w-full"
              :disabled="
                loading ||
                !form.study_program
              "
              :empty-message="
                t(
                  'curricula.noStudyForms',
                )
              "
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'curricula.fields.effectiveAcademicYear',
              )
            "
            name="
              effective_academic_year
            "
            required
            :error="
              fieldError(
                'effective_academic_year',
              )
            "
          >
            <Select
              v-model="
                form.effective_academic_year
              "
              :options="
                academicYearOptions
              "
              option-label="label"
              option-value="value"
              class="w-full"
              :disabled="loading"
            />
          </BaseFormField>
        </div>
      </section>

      <Message
        v-if="
          selectedProgram &&
          selectedDuration
        "
        severity="info"
        :closable="false"
      >
        {{
          t(
            'curricula.durationInfo',
            {
              level:
                selectedProgram.education_level_name,

              months:
                selectedDuration.duration_months,

              semesters:
                selectedDuration.semesters_count,
            },
          )
        }}
      </Message>

      <section>
        <h3>
          {{
            t(
              'curricula.sections.approval',
            )
          }}
        </h3>

        <div
          class="
            curriculum-form__grid
          "
        >
          <BaseFormField
            :label="
              t(
                'curricula.fields.status',
              )
            "
            name="status"
            required
            :error="
              fieldError('status')
            "
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
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'curricula.fields.approvedAt',
              )
            "
            name="approved_at"
            :required="
              form.status ===
              'approved'
            "
            :error="
              fieldError(
                'approved_at',
              )
            "
          >
            <DatePicker
              v-model="
                form.approved_at
              "
              date-format="dd.mm.yy"
              show-icon
              show-button-bar
              class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            class="
              curriculum-form__wide
            "
            :label="
              t(
                'curricula.fields.approvalDocument',
              )
            "
            name="
              approval_document
            "
            :error="
              fieldError(
                'approval_document',
              )
            "
          >
            <InputText
              v-model="
                form.approval_document
              "
              maxlength="255"
              class="w-full"
              :disabled="loading"
            />
          </BaseFormField>
        </div>
      </section>

      <section>
        <BaseFormField
          :label="
            t(
              'curricula.fields.notes',
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

        <label
          class="
            curriculum-form__checkbox
          "
        >
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
                'curricula.fields.active',
              )
            }}
          </span>
        </label>
      </section>
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
.curriculum-form {
  display: grid;
  gap: 1.5rem;
}

.curriculum-form section {
  display: grid;
  gap: 1rem;
}

.curriculum-form h3 {
  margin: 0;
  padding-bottom: 0.5rem;
  border-bottom:
    1px solid
    var(--app-border-color);
  font-size: 0.9rem;
}

.curriculum-form__grid {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.curriculum-form__wide {
  grid-column: 1 / -1;
}

.curriculum-form__checkbox {
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
    var(--app-text-muted);
  font-size: 0.7rem;
}

@media (max-width: 767px) {
  .curriculum-form__grid {
    grid-template-columns:
      1fr;
  }

  .curriculum-form__wide {
    grid-column: auto;
  }
}
</style>
