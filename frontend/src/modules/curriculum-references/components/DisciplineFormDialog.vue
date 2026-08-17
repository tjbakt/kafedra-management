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

import MultiSelect from 'primevue/multiselect'

import { useI18n } from 'vue-i18n'

import BaseDialog from '@/components/base/BaseDialog.vue'
import BaseFormActions from '@/components/base/BaseFormActions.vue'
import BaseFormField from '@/components/base/BaseFormField.vue'

import FormValidationSummary from '@/components/forms/FormValidationSummary.vue'

import { useLocaleStore } from '@/stores/locale'

import type {
  DepartmentLookup,
  Discipline,
  DisciplinePayload,
  SelectOption,
  WorkloadType,
  WorkloadTypeCode,
} from '@/modules/curriculum-references/types'

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
    discipline?: Discipline | null

    departments: DepartmentLookup[]
    workloadTypes: WorkloadType[]

    loading?: boolean

    fieldErrors?: FieldErrors
    nonFieldErrors?: string[]
    generalError?: string
  }>(),
  {
    discipline: null,

    loading: false,

    fieldErrors: () => ({}),
    nonFieldErrors: () => [],
    generalError: '',
  },
)

const emit = defineEmits<{
  submit: [
    payload: DisciplinePayload,
  ]
}>()

const { t } = useI18n()

const localeStore =
  useLocaleStore()

const form = reactive({
  code: '',

  name_ru: '',
  name_uz: '',

  default_department: null as number | null,
  workload_types: [] as number[],

  is_active: true,

  sort_order: 0,
})

const localErrors =
  reactive<Record<string, string>>({})

const dialogTitle = computed(
  () =>
    props.discipline
      ? t(
          'curriculumReferences.disciplines.editTitle',
        )
      : t(
          'curriculumReferences.disciplines.createTitle',
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

const departmentOptions =
  computed<
    SelectOption<number>[]
  >(() => {
    const options =
      props.departments
        .filter(
          (department) =>
            department.is_active &&
            !department.is_archived,
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
      props.discipline?.default_department &&
      !options.some(
        (option) =>
          option.value ===
          props.discipline
            ?.default_department,
      )
    ) {
      options.unshift({
        value: props.discipline.default_department,
        label: props.discipline.default_department_name ?? '—',
        description: '',
      })
    }

    return options
  })

const workloadTypeOptions =
  computed(() =>
    props.workloadTypes
      .filter(
        (item) =>
          item.is_active &&
          !item.is_archived &&
          item.code !==
          'course_work_project_defense',
      )
      .map(
        (item) => ({
          value: item.id,

          code: item.code,

          label:
          item.display_name,

          pairedCode:
          item.paired_code,
        }),
      ),
  )

function workloadByCode(
  code:
  WorkloadTypeCode,
): WorkloadType | null {
  return (
    props.workloadTypes.find(
      (item) =>
        item.code === code,
    ) ?? null
  )
}

function idsByCodes(
  codes:
  WorkloadTypeCode[],
): number[] {
  return props.workloadTypes
    .filter(
      (item) =>
        codes.includes(
          item.code,
        ),
    )
    .map(
      (item) =>
        item.id,
    )
}

function handleWorkloadTypesChange(): void {
  const selected =
    new Set(
      form.workload_types,
    )
  for (
    const id
    of selected
    ) {
    const type =
      props.workloadTypes.find(
        (item) =>
          item.id === id,
      )

    if (
      !type?.paired_code
    ) {
      continue
    }

    const pair =
      workloadByCode(
        type.paired_code,
      )

    if (pair) {
      selected.add(
        pair.id,
      )
    }
  }

  const courseWorkIds =
    idsByCodes([
      'course_work_supervision',
      'course_work_defense',
    ])

  const courseProjectIds =
    idsByCodes([
      'course_project_supervision',
      'course_project_defense',
    ])

  const hasCourseWork =
    courseWorkIds.some(
      (id) =>
        selected.has(id),
    )

  const hasCourseProject =
    courseProjectIds.some(
      (id) =>
        selected.has(id),
    )

  if (
    hasCourseWork &&
    hasCourseProject
  ) {
    localErrors.workload_types =
      t(
        'curriculumReferences.disciplines.validation.courseWorkOrProject',
      )

    return
  }

  const graduationIds =
    idsByCodes([
      'graduation_work_supervision',
      'graduation_work_defense',
    ])

  const masterIds =
    idsByCodes([
      'master_dissertation_supervision',
      'master_dissertation_defense',
    ])

  if (
    graduationIds.some(
      (id) =>
        selected.has(id),
    ) &&
    masterIds.some(
      (id) =>
        selected.has(id),
    )
  ) {
    localErrors.workload_types =
      t(
        'curriculumReferences.disciplines.validation.graduationOrMaster',
      )

    return
  }

  delete localErrors
    .workload_types

  form.workload_types =
    [...selected]
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

  form.name_ru = ''
  form.name_uz = ''

  form.workload_types = []
  form.default_department = null

  form.is_active = true

  form.sort_order = 0

  clearLocalErrors()
}

function fillForm(
  discipline: Discipline,
): void {
  form.code = discipline.code

  form.name_ru = discipline.name_ru

  form.name_uz = discipline.name_uz

  form.workload_types = [...discipline.workload_types]
  form.default_department = discipline.default_department

  form.is_active = discipline.is_active
  form.sort_order = discipline.sort_order

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
        'curriculumReferences.disciplines.validation.codeRequired',
      )
  }

  if (!form.name_ru.trim()) {
    localErrors.name_ru =
      t(
        'curriculumReferences.disciplines.validation.nameRuRequired',
      )
  }

  if (!form.name_uz.trim()) {
    localErrors.name_uz =
      t(
        'curriculumReferences.disciplines.validation.nameUzRequired',
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

  emit('submit', {
    code: form.code.trim().toUpperCase(),
    name_ru: form.name_ru.trim(),
    name_uz: form.name_uz.trim(),
    default_department: form.default_department,
    workload_types: [...form.workload_types],
    is_active: form.is_active,
    sort_order: form.sort_order,
  })
}

watch(
  () => visible.value,
  (isVisible) => {
    if (!isVisible) {
      return
    }

    if (props.discipline) {
      fillForm(
        props.discipline,
      )

      return
    }

    resetForm()
  },
)

watch(
  () => props.discipline,
  (discipline) => {
    if (
      visible.value &&
      discipline
    ) {
      fillForm(discipline)
    }
  },
)
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="dialogTitle"
    width="54rem"
    :loading="loading"
  >
    <FormValidationSummary
      :field-errors="fieldErrors"
      :non-field-errors="
        nonFieldErrors
      "
      :general-error="
        generalError
      "
    />

    <form
      class="discipline-form"
      novalidate
      @submit.prevent="submit"
    >
      <div
        class="discipline-form__grid"
      >
        <BaseFormField
          :label="
            t(
              'curriculumReferences.disciplines.fields.code',
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
              'curriculumReferences.disciplines.fields.department',
            )
          "
          name="default_department"
          :error="
            fieldError(
              'default_department',
            )
          "
        >
          <Select
            v-model="
              form.default_department
            "
            :options="
              departmentOptions
            "
            option-label="label"
            option-value="value"
            filter
            show-clear
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
          :label=" t( 'curriculumReferences.disciplines.fields.workloadTypes', ) "
          name="workload_types"
          :error=" fieldError( 'workload_types', ) "
        >
          <MultiSelect
            v-model=" form.workload_types "
            :options=" workloadTypeOptions "
            option-label="label"
            option-value="value"
            display="chip"
            filter
            class="w-full"
            :disabled="loading"
            @change="handleWorkloadTypesChange"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'curriculumReferences.disciplines.fields.nameRu',
            )
          "
          name="name_ru"
          required
          :error="
            fieldError('name_ru')
          "
        >
          <InputText
            v-model="form.name_ru"
            maxlength="500"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'curriculumReferences.disciplines.fields.nameUz',
            )
          "
          name="name_uz"
          required
          :error="
            fieldError('name_uz')
          "
        >
          <InputText
            v-model="form.name_uz"
            maxlength="500"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'curriculumReferences.common.sortOrder',
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
            :min="0"
            :use-grouping="false"
            class="w-full"
            input-class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <label
          class="
            discipline-form__checkbox
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
                'curriculumReferences.common.active',
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
.discipline-form__grid {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.discipline-form__checkbox {
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

.select-option small {
  color:
    var(--app-text-muted);
  font-size: 0.7rem;
}

@media (max-width: 767px) {
  .discipline-form__grid {
    grid-template-columns:
      1fr;
  }
}
</style>
