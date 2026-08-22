<script setup lang="ts">
import Checkbox from 'primevue/checkbox'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
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
  EducationDurationLookup,
  FacultyLookup,
  SelectOption,
  StudentGroup,
  StudentGroupPayload,
  StudyFormLookup,
  StudyProgramLookup,
} from '@/modules/student-groups/types'

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
    studentGroup?: StudentGroup | null

    academicYears: AcademicYearLookup[]
    faculties: FacultyLookup[]
    studyPrograms: StudyProgramLookup[]
    studyForms: StudyFormLookup[]
    educationDurations: EducationDurationLookup[]

    loading?: boolean

    fieldErrors?: FieldErrors
    nonFieldErrors?: string[]
    generalError?: string
  }>(),
  {
    studentGroup: null,

    loading: false,

    fieldErrors: () => ({}),
    nonFieldErrors: () => [],
    generalError: '',
  },
)

const emit = defineEmits<{
  submit: [
    payload: StudentGroupPayload,
  ]
}>()

const { t } = useI18n()

const localeStore =
  useLocaleStore()

const form = reactive({
  code: '',

  faculty:
    null as number | null,

  study_program:
    null as number | null,

  study_form:
    null as number | null,

  student_count: 0,
  subgroup_count: 1,

  is_active: true,

  notes: '',
})

const localErrors =
  reactive<Record<string, string>>({})

const dialogTitle = computed(
  () =>
    props.studentGroup
      ? t(
          'studentGroups.editTitle',
        )
      : t(
          'studentGroups.createTitle',
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

const selectedProgram =
  computed(
    () =>
      props.studyPrograms.find(
        (program) =>
          program.id ===
          form.study_program,
      ) ?? null,
  )

const facultyOptions =
  computed<
    SelectOption<number>[]
  >(() => {
    const universityId =
      selectedProgram.value
        ?.university

    const result =
      props.faculties
        .filter(
          (faculty) =>
            faculty.is_active &&
            !faculty.is_archived &&
            (
              !universityId ||
              faculty.university ===
                universityId
            ),
        )
        .map((faculty) => ({
          value: faculty.id,

          label:
            localizedName(
              faculty.name_ru,
              faculty.name_uz,
            ),

          description:
            faculty.university_name,
        }))

    if (
      props.studentGroup &&
      !result.some(
        (item) =>
          item.value ===
          props.studentGroup?.faculty,
      )
    ) {
      result.unshift({
        value:
          props.studentGroup.faculty,

        label:
          props.studentGroup
            .faculty_name,

        description: '',
      })
    }

    return result
  })

const studyProgramOptions =
  computed<
    SelectOption<number>[]
  >(() => {
    /*
     * Если факультет уже выбран,
     * программы ограничиваются
     * университетом этого факультета.
     */
    const faculty =
      props.faculties.find(
        (item) =>
          item.id ===
          form.faculty,
      )

    const universityId =
      faculty?.university

    const result =
      props.studyPrograms
        .filter(
          (program) =>
            program.is_active &&
            !program.is_archived &&
            (
              !universityId ||
              program.university ===
                universityId
            ),
        )
        .map((program) => ({
          value: program.id,

          label:
            `${program.code} — ${
              localizedName(
                program.name_ru,
                program.name_uz,
              )
            }`,

          description:
            program.profiling_department_name,
        }))

    if (
      props.studentGroup &&
      !result.some(
        (item) =>
          item.value ===
          props.studentGroup
            ?.study_program,
      )
    ) {
      result.unshift({
        value:
          props.studentGroup
            .study_program,

        label:
          props.studentGroup
            .study_program_name,

        description:
          props.studentGroup
            .profiling_department_name,
      })
    }

    return result
  })

/*
 * Форма обучения разрешена только если
 * для уровня выбранного направления
 * существует EducationDuration.
 */
const studyFormOptions =
  computed<
    SelectOption<number>[]
  >(() => {
    const educationLevelId =
      selectedProgram.value
        ?.education_level

    if (!educationLevelId) {
      return []
    }

    const allowedFormIds =
      new Set(
        props.educationDurations
          .filter(
            (duration) =>
              duration.is_active &&
              !duration.is_archived &&
              duration.education_level ===
                educationLevelId,
          )
          .map(
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
            allowedFormIds.has(
              studyForm.id,
            ),
        )
        .map((studyForm) => ({
          value: studyForm.id,

          label:
            localizedName(
              studyForm.name_ru,
              studyForm.name_uz,
            ),

          description:
            studyForm.code,
        }))

    if (
      props.studentGroup &&
      !result.some(
        (item) =>
          item.value ===
          props.studentGroup
            ?.study_form,
      )
    ) {
      result.unshift({
        value:
          props.studentGroup
            .study_form,

        label:
          props.studentGroup
            .study_form_name,

        description: '',
      })
    }

    return result
  })

const selectedDuration =
  computed(
    () => {
      if (
        !selectedProgram.value ||
        !form.study_form
      ) {
        return null
      }

      return (
        props.educationDurations.find(
          (duration) =>
            duration.education_level ===
              selectedProgram.value
                ?.education_level &&
            duration.study_form ===
              form.study_form &&
            duration.is_active &&
            !duration.is_archived,
        ) ?? null
      )
    },
  )

function clearLocalErrors(): void {
  Object.keys(localErrors).forEach(
    (key) => {
      delete localErrors[key]
    },
  )
}

function resetForm(): void {
  form.code = ''

  form.faculty = null
  form.study_program = null
  form.study_form = null

  form.student_count = 0
  form.subgroup_count = 1

  form.is_active = true

  form.notes = ''

  clearLocalErrors()
}

function fillForm(
  record: StudentGroup,
): void {
  form.code =
    record.code

  form.faculty =
    record.faculty

  form.study_program =
    record.study_program

  form.study_form =
    record.study_form

  form.student_count =
    record.student_count

  form.subgroup_count =
    record.subgroup_count

  form.is_active =
    record.is_active

  form.notes =
    record.notes

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
        'studentGroups.validation.codeRequired',
      )
  }

  if (!form.faculty) {
    localErrors.faculty =
      t(
        'studentGroups.validation.facultyRequired',
      )
  }

  if (!form.study_program) {
    localErrors.study_program =
      t(
        'studentGroups.validation.programRequired',
      )
  }

  if (!form.study_form) {
    localErrors.study_form =
      t(
        'studentGroups.validation.studyFormRequired',
      )
  }

  if (
    form.student_count < 0 ||
    form.student_count > 1000
  ) {
    localErrors.student_count =
      t(
        'studentGroups.validation.studentCountRange',
      )
  }

  if (
    form.subgroup_count < 1 ||
    form.subgroup_count > 20
  ) {
    localErrors.subgroup_count =
      t(
        'studentGroups.validation.subgroupCountRange',
      )
  }

  if (
    form.faculty &&
    form.study_program
  ) {
    const faculty =
      props.faculties.find(
        (item) =>
          item.id ===
          form.faculty,
      )

    const program =
      props.studyPrograms.find(
        (item) =>
          item.id ===
          form.study_program,
      )

    if (
      faculty &&
      program &&
      faculty.university !==
        program.university
    ) {
      localErrors.faculty =
        t(
          'studentGroups.validation.universityMismatch',
        )
    }
  }

  if (
    form.study_program &&
    form.study_form &&
    !selectedDuration.value
  ) {
    localErrors.study_form =
      t(
        'studentGroups.validation.durationMissing',
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
    !form.faculty ||
    !form.study_program ||
    !form.study_form
  ) {
    return
  }

  emit('submit', {
    code:
      form.code
        .trim()
        .toUpperCase(),

    faculty:
      form.faculty,

    study_program:
      form.study_program,

    study_form:
      form.study_form,

    student_count:
      form.student_count,

    subgroup_count:
      form.subgroup_count,

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

    const allowed =
      studyFormOptions.value.some(
        (option) =>
          option.value ===
          form.study_form,
      )

    if (!allowed) {
      form.study_form = null
    }
  },
)

watch(
  () => visible.value,
  (isVisible) => {
    if (!isVisible) {
      return
    }

    if (props.studentGroup) {
      fillForm(
        props.studentGroup,
      )

      return
    }

    resetForm()
  },
)

watch(
  () => props.studentGroup,
  (record) => {
    if (
      visible.value &&
      record
    ) {
      fillForm(record)
    }
  },
)
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="dialogTitle"
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
      class="student-group-form"
      novalidate
      @submit.prevent="submit"
    >
      <section>
        <h3>
          {{
            t(
              'studentGroups.sections.general',
            )
          }}
        </h3>

        <div
          class="
            student-group-form__grid
          "
        >
          <BaseFormField
            :label="
              t(
                'studentGroups.fields.code',
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
              maxlength="50"
              class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'studentGroups.fields.admissionYear',
              )
            "
            name="
              academic_year_admission
            "
            required
            :error="
              fieldError(
                'academic_year_admission',
              )
            "
          >
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'studentGroups.fields.graduationYear',
              )
            "
            name="
              graduation_academic_year
            "
            :error="
              fieldError(
                'graduation_academic_year',
              )
            "
          >

          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'studentGroups.fields.faculty',
              )
            "
            name="faculty"
            required
            :error="
              fieldError('faculty')
            "
          >
            <Select
              v-model="
                form.faculty
              "
              :options="
                facultyOptions
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
                'studentGroups.fields.studyProgram',
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
                'studentGroups.fields.studyForm',
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
                  'studentGroups.noAvailableStudyForms',
                )
              "
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'studentGroups.fields.studentCount',
              )
            "
            name="student_count"
            required
            :error="
              fieldError(
                'student_count',
              )
            "
          >
            <InputNumber
              v-model="
                form.student_count
              "
              :min="0"
              :max="1000"
              :use-grouping="false"
              class="w-full"
              input-class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'studentGroups.fields.subgroupCount',
              )
            "
            name="subgroup_count"
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
              :max="20"
              :use-grouping="false"
              class="w-full"
              input-class="w-full"
              :disabled="loading"
            />
          </BaseFormField>
        </div>
      </section>

      <section
        v-if="
          selectedProgram
        "
        class="
          student-group-form__info
        "
      >
        <h3>
          {{
            t(
              'studentGroups.sections.programInfo',
            )
          }}
        </h3>

        <div>
          <span>
            {{
              t(
                'studentGroups.fields.educationLevel',
              )
            }}
          </span>

          <strong>
            {{
              selectedProgram
                .education_level_name
            }}
          </strong>
        </div>

        <div>
          <span>
            {{
              t(
                'studentGroups.fields.profilingDepartment',
              )
            }}
          </span>

          <strong>
            {{
              selectedProgram
                .profiling_department_name
            }}
          </strong>
        </div>

        <div
          v-if="
            selectedDuration
          "
        >
          <span>
            {{
              t(
                'studentGroups.fields.duration',
              )
            }}
          </span>

          <strong>
            {{
              t(
                'studentGroups.durationValue',
                {
                  months:
                    selectedDuration.duration_months,

                  semesters:
                    selectedDuration.semesters_count,
                },
              )
            }}
          </strong>
        </div>
      </section>

      <section>
        <BaseFormField
          :label="
            t(
              'studentGroups.fields.notes',
            )
          "
          name="notes"
          :error="
            fieldError('notes')
          "
        >
          <Textarea
            v-model="form.notes"
            rows="4"
            auto-resize
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <label
          class="
            student-group-form__checkbox
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
                'studentGroups.fields.active',
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
.student-group-form {
  display: grid;
  gap: 1.5rem;
}

.student-group-form section {
  display: grid;
  gap: 1rem;
}

.student-group-form h3 {
  margin: 0;
  padding-bottom: 0.5rem;
  border-bottom:
    1px solid
    var(--app-border-color);
  font-size: 0.9rem;
}

.student-group-form__grid {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.student-group-form__info {
  padding: 1rem;
  border:
    1px solid
    var(--app-border-color);
  border-radius:
    var(--app-radius);
}

.student-group-form__info > div {
  display: grid;
  grid-template-columns:
    12rem 1fr;
  gap: 1rem;
  font-size: 0.8rem;
}

.student-group-form__info span {
  color:
    var(--app-text-muted);
}

.student-group-form__checkbox {
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
  .student-group-form__grid {
    grid-template-columns: 1fr;
  }

  .student-group-form__info > div {
    grid-template-columns: 1fr;
    gap: 0.15rem;
  }
}
</style>
