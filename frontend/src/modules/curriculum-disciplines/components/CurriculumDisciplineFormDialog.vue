<script setup lang="ts">
import Checkbox from 'primevue/checkbox'
import InputNumber from 'primevue/inputnumber'
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
  SemesterOption,
} from '@/modules/curriculum-disciplines/types'

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
    curriculum: Curriculum

    studyProgram:
      StudyProgram | null

    record?:
      CurriculumDiscipline | null

    disciplines: Discipline[]

    departments:
      DepartmentLookup[]

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
      CurriculumDisciplinePayload,
  ]
}>()

const { t } = useI18n()

const localeStore =
  useLocaleStore()

const form = reactive({
  discipline:
    null as number | null,

  semester_number:
    null as number | null,

  teaching_department:
    null as number | null,

  component_type:
    'required' as CurriculumComponentType,

  control_form:
    'none' as CurriculumControlForm,

  credits:
    0 as number | null,

  total_academic_hours:
    0 as number | null,

  independent_hours:
    0 as number | null,

  weeks_count:
    15 as number | null,

  is_active: true,

  notes: '',
})

const localErrors =
  reactive<
    Record<string, string>
  >({})

const title = computed(
  () =>
    props.record
      ? t(
          'curriculumDisciplines.editTitle',
        )
      : t(
          'curriculumDisciplines.createTitle',
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

const semesterOptions =
  computed<
    SemesterOption[]
  >(() => {
    const count =
      props.curriculum
        .semesters_count ?? 0

    return Array.from(
      {
        length: count,
      },

      (_, index) => {
        const semester =
          index + 1

        const season =
          semester % 2 === 1
            ? 'autumn'
            : 'spring'

        return {
          value:
            semester,

          season,

          seasonLabel:
            season ===
            'autumn'
              ? t(
                  'curriculumDisciplines.seasons.autumn',
                )
              : t(
                  'curriculumDisciplines.seasons.spring',
                ),

          label:
            t(
              'curriculumDisciplines.semesterOption',
              {
                semester,

                season:
                  season ===
                  'autumn'
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
    )
  })

const disciplineOptions =
  computed<
    SelectOption<number>[]
  >(() => {
    const result =
      props.disciplines
        .filter(
          (discipline) =>
            discipline.is_active &&
            !discipline.is_archived,
        )
        .map(
          (discipline) => ({
            value:
              discipline.id,

            label:
              `${discipline.code} — ${
                localizedName(
                  discipline.name_ru,
                  discipline.name_uz,
                )
              }`,

            description:
              discipline
                .default_department_name ??
              undefined,
          }),
        )

    if (
      props.record &&
      !result.some(
        (option) =>
          option.value ===
          props.record
            ?.discipline,
      )
    ) {
      result.unshift({
        value: props.record.discipline,
        label: `${props.record.discipline_code} — ${props.record.discipline_name}`,
        description: '',
      })
    }

    return result
  })

const departmentOptions =
  computed<
    SelectOption<number>[]
  >(() => {
    const universityId =
      props.studyProgram
        ?.university

    const result =
      props.departments
        .filter(
          (department) =>
            department.is_active &&
            !department.is_archived &&
            (
              !universityId ||
              department.university ===
                universityId
            ),
        )
        .map(
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
        )

    if (
      props.record &&
      !result.some(
        (option) =>
          option.value ===
          props.record
            ?.teaching_department,
      )
    ) {
      result.unshift({
        value: props.record.teaching_department,
        label: props.record.teaching_department_name,
        description: '',
      })
    }

    return result
  })

const componentTypeOptions =
  computed<
    SelectOption<
      CurriculumComponentType
    >[]
  >(() => [
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
      CurriculumControlForm
    >[]
  >(() => [
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

// const selectedDiscipline =
//   computed(
//     () =>
//       props.disciplines.find(
//         (discipline) =>
//           discipline.id ===
//           form.discipline,
//       ) ?? null,
//   )

const contactHours =
  computed(() => {
    const total =
      Number(
        form.total_academic_hours ??
        0,
      )

    const independent =
      Number(
        form.independent_hours ??
        0,
      )

    return Math.max(
      0,
      total - independent,
    )
  })

function clearLocalErrors(): void {
  Object.keys(localErrors)
    .forEach(
      (key) => {
        delete localErrors[key]
      },
    )
}

function resetForm(): void {
  form.discipline = null

  form.semester_number =
    null

  form.teaching_department =
    null

  form.component_type =
    'required'

  form.control_form =
    'none'

  form.credits = 0

  form.total_academic_hours =
    0

  form.independent_hours =
    0

  form.weeks_count =
    15

  form.is_active =
    true

  form.notes = ''

  clearLocalErrors()
}

function fillForm(
  record:
    CurriculumDiscipline,
): void {
  form.discipline =
    record.discipline

  form.semester_number =
    record.semester_number

  form.teaching_department =
    record.teaching_department

  form.component_type =
    record.component_type

  form.control_form =
    record.control_form

  form.credits =
    Number(record.credits)

  form.total_academic_hours =
    Number(
      record.total_academic_hours,
    )

  form.independent_hours =
    Number(
      record.independent_hours,
    )

  form.weeks_count =
    record.weeks_count

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

  if (!form.discipline) {
    localErrors.discipline =
      t(
        'curriculumDisciplines.validation.disciplineRequired',
      )
  }

  if (
    !form.semester_number
  ) {
    localErrors.semester_number =
      t(
        'curriculumDisciplines.validation.semesterRequired',
      )
  }

  if (
    form.semester_number &&
    props.curriculum
      .semesters_count &&
    form.semester_number >
      props.curriculum
        .semesters_count
  ) {
    localErrors.semester_number =
      t(
        'curriculumDisciplines.validation.semesterRange',
      )
  }

  if (
    !form.teaching_department
  ) {
    localErrors.teaching_department =
      t(
        'curriculumDisciplines.validation.departmentRequired',
      )
  }

  if (
    form.credits === null ||
    form.credits < 0
  ) {
    localErrors.credits =
      t(
        'curriculumDisciplines.validation.nonNegative',
      )
  }

  if (
    form.total_academic_hours ===
      null ||
    form.total_academic_hours <
      0
  ) {
    localErrors.total_academic_hours =
      t(
        'curriculumDisciplines.validation.nonNegative',
      )
  }

  if (
    form.independent_hours ===
      null ||
    form.independent_hours <
      0
  ) {
    localErrors.independent_hours =
      t(
        'curriculumDisciplines.validation.nonNegative',
      )
  }

  if (
    form.total_academic_hours !==
      null &&
    form.independent_hours !==
      null &&
    form.independent_hours >
      form.total_academic_hours
  ) {
    localErrors.independent_hours =
      t(
        'curriculumDisciplines.validation.independentExceedsTotal',
      )
  }

  if (
    form.weeks_count === null ||
    form.weeks_count < 1
  ) {
    localErrors.weeks_count =
      t(
        'curriculumDisciplines.validation.weeks',
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
    !form.discipline ||
    !form.semester_number ||
    !form.teaching_department ||
    form.credits === null ||
    form.total_academic_hours ===
      null ||
    form.independent_hours ===
      null ||
    form.weeks_count === null
  ) {
    return
  }

  emit('submit', {
    curriculum:
      props.curriculum.id,

    discipline:
      form.discipline,

    semester_number:
      form.semester_number,

    teaching_department:
      form.teaching_department,

    component_type:
      form.component_type,

    control_form:
      form.control_form,

    credits:
      form.credits,

    total_academic_hours:
      form.total_academic_hours,

    independent_hours:
      form.independent_hours,

    weeks_count:
      form.weeks_count,

    is_active:
      form.is_active,

    notes:
      form.notes.trim(),
  })
}

watch(
  () => form.discipline,
  (disciplineId) => {
    if (!disciplineId) {
      return
    }

    /*
     * При редактировании уже
     * сохранённую кафедру не
     * перезаписываем автоматически.
     */
    if (
      props.record &&
      disciplineId ===
        props.record.discipline
    ) {
      return
    }

    const discipline =
      props.disciplines.find(
        (item) =>
          item.id ===
          disciplineId,
      )

    if (
      discipline
        ?.default_department
    ) {
      const departmentAllowed =
        departmentOptions.value
          .some(
            (option) =>
              option.value ===
              discipline
                .default_department,
          )

      if (departmentAllowed) {
        form.teaching_department =
          discipline
            .default_department
      }
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
      fillForm(
        props.record,
      )

      return
    }

    resetForm()
  },
)

watch(
  () => props.record,
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
    :title="title"
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
      class="
        curriculum-discipline-form
      "
      novalidate
      @submit.prevent="submit"
    >
      <section>
        <h3>
          {{
            t(
              'curriculumDisciplines.sections.discipline',
            )
          }}
        </h3>

        <div
          class="
            curriculum-discipline-form__grid
          "
        >
          <BaseFormField
            class="
              curriculum-discipline-form__wide
            "
            :label="
              t(
                'curriculumDisciplines.fields.discipline',
              )
            "
            name="discipline"
            required
            :error="
              fieldError(
                'discipline',
              )
            "
          >
            <Select
              v-model="
                form.discipline
              "
              :options="
                disciplineOptions
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
                'curriculumDisciplines.fields.semester',
              )
            "
            name="semester_number"
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
                semesterOptions
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
                'curriculumDisciplines.fields.department',
              )
            "
            name="
              teaching_department
            "
            required
            :error="
              fieldError(
                'teaching_department',
              )
            "
          >
            <Select
              v-model="
                form.teaching_department
              "
              :options="
                departmentOptions
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
                'curriculumDisciplines.fields.componentType',
              )
            "
            name="component_type"
            required
            :error="
              fieldError(
                'component_type',
              )
            "
          >
            <Select
              v-model="
                form.component_type
              "
              :options="
                componentTypeOptions
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
                'curriculumDisciplines.fields.controlForm',
              )
            "
            name="control_form"
            required
            :error="
              fieldError(
                'control_form',
              )
            "
          >
            <Select
              v-model="
                form.control_form
              "
              :options="
                controlFormOptions
              "
              option-label="label"
              option-value="value"
              class="w-full"
              :disabled="loading"
            />
          </BaseFormField>
        </div>
      </section>

      <section>
        <h3>
          {{
            t(
              'curriculumDisciplines.sections.hours',
            )
          }}
        </h3>

        <div
          class="
            curriculum-discipline-form__grid
          "
        >
          <BaseFormField
            :label="
              t(
                'curriculumDisciplines.fields.credits',
              )
            "
            name="credits"
            :error="
              fieldError(
                'credits',
              )
            "
          >
            <InputNumber
              v-model="
                form.credits
              "
              :min="0"
              :max-fraction-digits="2"
              :min-fraction-digits="2"
              :use-grouping="false"
              class="w-full"
              input-class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'curriculumDisciplines.fields.weeks',
              )
            "
            name="weeks_count"
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
              :max="52"
              :use-grouping="false"
              class="w-full"
              input-class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'curriculumDisciplines.fields.totalHours',
              )
            "
            name="
              total_academic_hours
            "
            :error="
              fieldError(
                'total_academic_hours',
              )
            "
          >
            <InputNumber
              v-model="
                form.total_academic_hours
              "
              :min="0"
              :max-fraction-digits="2"
              :min-fraction-digits="2"
              :use-grouping="false"
              class="w-full"
              input-class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'curriculumDisciplines.fields.independentHours',
              )
            "
            name="
              independent_hours
            "
            :error="
              fieldError(
                'independent_hours',
              )
            "
          >
            <InputNumber
              v-model="
                form.independent_hours
              "
              :min="0"
              :max-fraction-digits="2"
              :min-fraction-digits="2"
              :use-grouping="false"
              class="w-full"
              input-class="w-full"
              :disabled="loading"
            />
          </BaseFormField>
        </div>

        <Message
          severity="info"
          :closable="false"
        >
          {{
            t(
              'curriculumDisciplines.contactHoursHint',
              {
                hours:
                  contactHours.toFixed(
                    2,
                  ),
              },
            )
          }}
        </Message>
      </section>

      <section>
        <BaseFormField
          :label="
            t(
              'curriculumDisciplines.fields.notes',
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
            :disabled="loading"
          />
        </BaseFormField>

        <label
          class="
            curriculum-discipline-form__checkbox
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
                'curriculumDisciplines.fields.active',
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
.curriculum-discipline-form {
  display: grid;
  gap: 1.5rem;
}

.curriculum-discipline-form section {
  display: grid;
  gap: 1rem;
}

.curriculum-discipline-form h3 {
  margin: 0;
  padding-bottom: 0.5rem;
  border-bottom:
    1px solid
    var(--app-border-color);
  font-size: 0.9rem;
}

.curriculum-discipline-form__grid {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.curriculum-discipline-form__wide {
  grid-column: 1 / -1;
}

.curriculum-discipline-form__checkbox {
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
  .curriculum-discipline-form__grid {
    grid-template-columns:
      1fr;
  }

  .curriculum-discipline-form__wide {
    grid-column: auto;
  }
}
</style>
