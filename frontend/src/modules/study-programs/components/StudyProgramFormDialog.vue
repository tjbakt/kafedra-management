<script setup lang="ts">
import Checkbox from 'primevue/checkbox'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'

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
  DepartmentLookup,
  EducationLevelLookup,
  SelectOption,
  StudyProgram,
  StudyProgramPayload,
  UniversityLookup,
} from '@/modules/study-programs/types'

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
    studyProgram?: StudyProgram | null

    universities: UniversityLookup[]
    educationLevels: EducationLevelLookup[]
    departments: DepartmentLookup[]

    loading?: boolean

    fieldErrors?: FieldErrors
    nonFieldErrors?: string[]
    generalError?: string
  }>(),
  {
    studyProgram: null,

    loading: false,

    fieldErrors: () => ({}),
    nonFieldErrors: () => [],
    generalError: '',
  },
)

const emit = defineEmits<{
  submit: [
    payload: StudyProgramPayload,
  ]
}>()

const { t } = useI18n()

const localeStore =
  useLocaleStore()

const form = reactive({
  university:
    null as number | null,

  education_level:
    null as number | null,

  code: '',

  name_ru: '',
  name_uz: '',

  profiling_department:
    null as number | null,

  is_active: true,

  sort_order: 0,
})

const localErrors =
  reactive<Record<string, string>>({})

const dialogTitle = computed(
  () =>
    props.studyProgram
      ? t(
          'studyPrograms.editTitle',
        )
      : t(
          'studyPrograms.createTitle',
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

const universityOptions =
  computed<
    SelectOption<number>[]
  >(() =>
    props.universities
      .filter(
        (item) =>
          item.is_active &&
          !item.is_archived,
      )
      .map((item) => ({
        value: item.id,

        label:
          localizedName(
            item.name_ru,
            item.name_uz,
          ),

        description:
          item.code,
      })),
  )

const educationLevelOptions =
  computed<
    SelectOption<number>[]
  >(() =>
    props.educationLevels
      .filter(
        (item) =>
          item.is_active &&
          !item.is_archived,
      )
      .map((item) => ({
        value: item.id,

        label:
          localizedName(
            item.name_ru,
            item.name_uz,
          ),

        description:
          item.code,
      })),
  )

const departmentOptions =
  computed<
    SelectOption<number>[]
  >(() => {
    const selectedUniversity =
      form.university

    const result =
      props.departments
        .filter(
          (item) =>
            item.is_active &&
            !item.is_archived &&
            (
              !selectedUniversity ||
              item.university ===
                selectedUniversity
            ),
        )
        .map((item) => ({
          value: item.id,

          label:
            localizedName(
              item.name_ru,
              item.name_uz,
            ),

          description:
            `${item.faculty_name} · ${item.code}`,
        }))

    /*
     * Fallback для редактирования:
     * текущая кафедра должна существовать
     * в options даже если впоследствии
     * была деактивирована.
     */
    if (
      props.studyProgram &&
      !result.some(
        (item) =>
          item.value ===
          props.studyProgram
            ?.profiling_department,
      )
    ) {
      result.unshift({
        value:
          props.studyProgram
            .profiling_department,

        label:
          props.studyProgram
            .profiling_department_name,

        description:
          props.studyProgram
            .profiling_faculty_name,
      })
    }

    return result
  })

function clearLocalErrors(): void {
  Object.keys(localErrors).forEach(
    (key) => {
      delete localErrors[key]
    },
  )
}

function resetForm(): void {
  form.university = null

  form.education_level = null

  form.code = ''

  form.name_ru = ''
  form.name_uz = ''

  form.profiling_department =
    null

  form.is_active = true

  form.sort_order = 0

  clearLocalErrors()
}

function fillForm(
  record: StudyProgram,
): void {
  form.university =
    record.university

  form.education_level =
    record.education_level

  form.code =
    record.code

  form.name_ru =
    record.name_ru

  form.name_uz =
    record.name_uz

  form.profiling_department =
    record.profiling_department

  form.is_active =
    record.is_active

  form.sort_order =
    record.sort_order

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

  if (!form.university) {
    localErrors.university =
      t(
        'studyPrograms.validation.universityRequired',
      )
  }

  if (!form.education_level) {
    localErrors.education_level =
      t(
        'studyPrograms.validation.educationLevelRequired',
      )
  }

  if (!form.code.trim()) {
    localErrors.code =
      t(
        'studyPrograms.validation.codeRequired',
      )
  }

  if (!form.name_ru.trim()) {
    localErrors.name_ru =
      t(
        'studyPrograms.validation.nameRuRequired',
      )
  }

  if (!form.name_uz.trim()) {
    localErrors.name_uz =
      t(
        'studyPrograms.validation.nameUzRequired',
      )
  }

  if (!form.profiling_department) {
    localErrors.profiling_department =
      t(
        'studyPrograms.validation.departmentRequired',
      )
  }

  if (
    form.university &&
    form.profiling_department
  ) {
    const department =
      props.departments.find(
        (item) =>
          item.id ===
          form.profiling_department,
      )

    if (
      department &&
      department.university !==
        form.university
    ) {
      localErrors.profiling_department =
        t(
          'studyPrograms.validation.departmentUniversityMismatch',
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
    !form.university ||
    !form.education_level ||
    !form.profiling_department
  ) {
    return
  }

  emit('submit', {
    university:
      form.university,

    education_level:
      form.education_level,

    code:
      form.code
        .trim()
        .toUpperCase(),

    name_ru:
      form.name_ru.trim(),

    name_uz:
      form.name_uz.trim(),

    profiling_department:
      form.profiling_department,

    is_active:
      form.is_active,

    sort_order:
      form.sort_order,
  })
}

/*
 * Если пользователь изменил университет,
 * а выбранная кафедра относится к другому,
 * очищаем выбор.
 */
watch(
  () => form.university,
  (university) => {
    if (
      !university ||
      !form.profiling_department
    ) {
      return
    }

    const department =
      props.departments.find(
        (item) =>
          item.id ===
          form.profiling_department,
      )

    if (
      department &&
      department.university !==
        university
    ) {
      form.profiling_department =
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

    if (props.studyProgram) {
      fillForm(
        props.studyProgram,
      )

      return
    }

    resetForm()
  },
)

watch(
  () => props.studyProgram,
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
    width="56rem"
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
      class="study-program-form"
      novalidate
      @submit.prevent="submit"
    >
      <div
        class="
          study-program-form__grid
        "
      >
        <BaseFormField
          :label="
            t(
              'studyPrograms.fields.university',
            )
          "
          name="university"
          required
          :error="
            fieldError(
              'university',
            )
          "
        >
          <Select
            v-model="
              form.university
            "
            input-id="university"
            :options="
              universityOptions
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
              'studyPrograms.fields.educationLevel',
            )
          "
          name="education_level"
          required
          :error="
            fieldError(
              'education_level',
            )
          "
        >
          <Select
            v-model="
              form.education_level
            "
            input-id="
              education_level
            "
            :options="
              educationLevelOptions
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
              'studyPrograms.fields.code',
            )
          "
          name="code"
          required
          :error="
            fieldError('code')
          "
        >
          <InputText
            id="code"
            v-model="form.code"
            maxlength="50"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'studyPrograms.fields.profilingDepartment',
            )
          "
          name="
            profiling_department
          "
          required
          :error="
            fieldError(
              'profiling_department',
            )
          "
        >
          <Select
            v-model="
              form.profiling_department
            "
            input-id="
              profiling_department
            "
            :options="
              departmentOptions
            "
            option-label="label"
            option-value="value"
            filter
            class="w-full"
            :disabled="
              loading ||
              !form.university
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
              'studyPrograms.fields.nameRu',
            )
          "
          name="name_ru"
          required
          :error="
            fieldError(
              'name_ru',
            )
          "
        >
          <InputText
            id="name_ru"
            v-model="
              form.name_ru
            "
            maxlength="500"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'studyPrograms.fields.nameUz',
            )
          "
          name="name_uz"
          required
          :error="
            fieldError(
              'name_uz',
            )
          "
        >
          <InputText
            id="name_uz"
            v-model="
              form.name_uz
            "
            maxlength="500"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'studyPrograms.fields.sortOrder',
            )
          "
          name="sort_order"
          :error="
            fieldError(
              'sort_order',
            )
          "
        >
          <InputNumber
            v-model="
              form.sort_order
            "
            input-id="sort_order"
            :min="0"
            :use-grouping="false"
            class="w-full"
            input-class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <label
          class="
            study-program-form__checkbox
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
                'studyPrograms.fields.active',
              )
            }}
          </span>
        </label>
      </div>
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
.study-program-form {
  display: grid;
}

.study-program-form__grid {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.study-program-form__checkbox {
  display: flex;
  align-items: center;
  align-self: end;
  gap: 0.5rem;
  min-height: 2.75rem;
  font-size: 0.82rem;
  font-weight: 600;
}

.select-option {
  display: grid;
  gap: 0.15rem;
}

.select-option strong {
  font-size: 0.82rem;
}

.select-option small {
  color:
    var(--app-text-muted);
  font-size: 0.7rem;
}

@media (max-width: 767px) {
  .study-program-form__grid {
    grid-template-columns: 1fr;
  }
}
</style>
