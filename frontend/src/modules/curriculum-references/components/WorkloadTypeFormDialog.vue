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

import type {
  CalculationMode,
  ReportCategory,
  SelectOption,
  WorkloadType,
  WorkloadTypeCode,
  WorkloadTypePayload,
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
    workloadType?: WorkloadType | null

    loading?: boolean

    fieldErrors?: FieldErrors
    nonFieldErrors?: string[]
    generalError?: string
  }>(),
  {
    workloadType: null,

    loading: false,

    fieldErrors: () => ({}),
    nonFieldErrors: () => [],
    generalError: '',
  },
)

const emit = defineEmits<{
  submit: [
    payload: WorkloadTypePayload,
  ]
}>()

const { t } = useI18n()

const form = reactive({
  code:
    'lecture' as WorkloadTypeCode,

  name_ru: '',
  name_uz: '',

  calculation_mode:
    'per_group' as CalculationMode,

  report_category:
    'other' as ReportCategory,

  is_classroom: true,

  is_teaching_load: true,

  is_active: true,

  sort_order: 0,
})

const localErrors =
  reactive<Record<string, string>>({})

const dialogTitle = computed(
  () =>
    props.workloadType
      ? t(
          'curriculumReferences.workloadTypes.editTitle',
        )
      : t(
          'curriculumReferences.workloadTypes.createTitle',
        ),
)

const codeOptions =
  computed<
    SelectOption<WorkloadTypeCode>[]
  >(() => [
    {
      value: 'lecture',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.lecture',
        ),
    },
    {
      value: 'practice',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.practice',
        ),
    },
    {
      value: 'laboratory',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.laboratory',
        ),
    },
    {
      value: 'seminar',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.seminar',
        ),
    },
    {
      value: 'consultation',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.consultation',
        ),
    },
    {
      value: 'exam',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.exam',
        ),
    },
    {
      value: 'credit',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.credit',
        ),
    },
    {
      value: 'course_work',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.courseWork',
        ),
    },
    {
      value: 'course_project',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.courseProject',
        ),
    },
    {
      value:
        'course_work_project_defense',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.courseWorkProjectDefense',
        ),
    },
    {
      value:
        'scientific_practice',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.scientificPractice',
        ),
    },
    {
      value:
        'qualification_practice',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.qualificationPractice',
        ),
    },
    {
      value:
        'master_dissertation_supervision',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.masterDissertationSupervision',
        ),
    },
    {
      value:
        'master_dissertation_defense',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.masterDissertationDefense',
        ),
    },
    {
      value:
        'graduation_work_supervision',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.graduationWorkSupervision',
        ),
    },
    {
      value:
        'graduation_work_defense',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.graduationWorkDefense',
        ),
    },
    {
      value: 'independent_work',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.independentWork',
        ),
    },
    {
      value: 'other',
      label:
        t(
          'curriculumReferences.workloadTypes.codes.other',
        ),
    },
  ])

const calculationModeOptions =
  computed<
    SelectOption<CalculationMode>[]
  >(() => [
    {
      value: 'fixed',
      label:
        t(
          'curriculumReferences.workloadTypes.calculationModes.fixed',
        ),
    },
    {
      value: 'per_group',
      label:
        t(
          'curriculumReferences.workloadTypes.calculationModes.perGroup',
        ),
    },
    {
      value: 'per_subgroup',
      label:
        t(
          'curriculumReferences.workloadTypes.calculationModes.perSubgroup',
        ),
    },
    {
      value: 'per_student',
      label:
        t(
          'curriculumReferences.workloadTypes.calculationModes.perStudent',
        ),
    },
  ])

const reportCategoryOptions =
  computed<
    SelectOption<ReportCategory>[]
  >(() => [
    {
      value: 'lecture',
      label:
        t(
          'curriculumReferences.workloadTypes.reportCategories.lecture',
        ),
    },
    {
      value: 'practice',
      label:
        t(
          'curriculumReferences.workloadTypes.reportCategories.practice',
        ),
    },
    {
      value: 'laboratory',
      label:
        t(
          'curriculumReferences.workloadTypes.reportCategories.laboratory',
        ),
    },
    {
      value:
        'course_work_supervision',
      label:
        t(
          'curriculumReferences.workloadTypes.reportCategories.courseWorkSupervision',
        ),
    },
    {
      value:
        'course_project_supervision',
      label:
        t(
          'curriculumReferences.workloadTypes.reportCategories.courseProjectSupervision',
        ),
    },
    {
      value:
        'course_work_project_defense',
      label:
        t(
          'curriculumReferences.workloadTypes.reportCategories.courseDefense',
        ),
    },
    {
      value:
        'scientific_practice',
      label:
        t(
          'curriculumReferences.workloadTypes.reportCategories.scientificPractice',
        ),
    },
    {
      value:
        'qualification_practice',
      label:
        t(
          'curriculumReferences.workloadTypes.reportCategories.qualificationPractice',
        ),
    },
    {
      value:
        'master_dissertation_supervision',
      label:
        t(
          'curriculumReferences.workloadTypes.reportCategories.masterSupervision',
        ),
    },
    {
      value:
        'master_dissertation_defense',
      label:
        t(
          'curriculumReferences.workloadTypes.reportCategories.masterDefense',
        ),
    },
    {
      value:
        'graduation_work_supervision',
      label:
        t(
          'curriculumReferences.workloadTypes.reportCategories.graduationSupervision',
        ),
    },
    {
      value:
        'graduation_work_defense',
      label:
        t(
          'curriculumReferences.workloadTypes.reportCategories.graduationDefense',
        ),
    },
    {
      value: 'rating',
      label:
        t(
          'curriculumReferences.workloadTypes.reportCategories.rating',
        ),
    },
    {
      value: 'other',
      label:
        t(
          'curriculumReferences.workloadTypes.reportCategories.other',
        ),
    },
  ])

function clearLocalErrors(): void {
  for (
    const key of
    Object.keys(localErrors)
  ) {
    delete localErrors[key]
  }
}

function resetForm(): void {
  form.code = 'lecture'

  form.name_ru = ''
  form.name_uz = ''

  form.calculation_mode =
    'per_group'

  form.report_category =
    'other'

  form.is_classroom = true

  form.is_teaching_load =
    true

  form.is_active = true

  form.sort_order = 0

  clearLocalErrors()
}

function fillForm(
  workloadType: WorkloadType,
): void {
  form.code =
    workloadType.code

  form.name_ru =
    workloadType.name_ru

  form.name_uz =
    workloadType.name_uz

  form.calculation_mode =
    workloadType.calculation_mode

  form.report_category =
    workloadType.report_category

  form.is_classroom =
    workloadType.is_classroom

  form.is_teaching_load =
    workloadType.is_teaching_load

  form.is_active =
    workloadType.is_active

  form.sort_order =
    workloadType.sort_order

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

  if (!form.code) {
    localErrors.code =
      t('common.required')
  }

  if (!form.name_ru.trim()) {
    localErrors.name_ru =
      t('common.required')
  }

  if (!form.name_uz.trim()) {
    localErrors.name_uz =
      t('common.required')
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
    code:
      form.code,

    name_ru:
      form.name_ru.trim(),

    name_uz:
      form.name_uz.trim(),

    calculation_mode:
      form.calculation_mode,

    report_category:
      form.report_category,

    is_classroom:
      form.is_classroom,

    is_teaching_load:
      form.is_teaching_load,

    is_active:
      form.is_active,

    sort_order:
      form.sort_order,
  })
}

watch(
  () => visible.value,
  (isVisible) => {
    if (!isVisible) {
      return
    }

    if (props.workloadType) {
      fillForm(
        props.workloadType,
      )

      return
    }

    resetForm()
  },
)

watch(
  () => props.workloadType,
  (workloadType) => {
    if (
      visible.value &&
      workloadType
    ) {
      fillForm(workloadType)
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
      class="workload-type-form"
      novalidate
      @submit.prevent="submit"
    >
      <div
        class="
          workload-type-form__grid
        "
      >
        <BaseFormField
          :label="
            t(
              'curriculumReferences.workloadTypes.fields.code',
            )
          "
          name="code"
          required
          :error="
            fieldError('code')
          "
        >
          <Select
            v-model="form.code"
            :options="
              codeOptions
            "
            option-label="label"
            option-value="value"
            class="w-full"
            :disabled="
              loading ||
              Boolean(workloadType)
            "
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'curriculumReferences.workloadTypes.fields.calculationMode',
            )
          "
          name="calculation_mode"
          required
          :error="
            fieldError(
              'calculation_mode',
            )
          "
        >
          <Select
            v-model="
              form.calculation_mode
            "
            :options="
              calculationModeOptions
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
              'curriculumReferences.workloadTypes.fields.nameRu',
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
            maxlength="255"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'curriculumReferences.workloadTypes.fields.nameUz',
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
            maxlength="255"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          class="
            workload-type-form__wide
          "
          :label="
            t(
              'curriculumReferences.workloadTypes.fields.reportCategory',
            )
          "
          name="report_category"
          required
          :error="
            fieldError(
              'report_category',
            )
          "
        >
          <Select
            v-model="
              form.report_category
            "
            :options="
              reportCategoryOptions
            "
            option-label="label"
            option-value="value"
            filter
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
      </div>

      <div
        class="
          workload-type-form__flags
        "
      >
        <label>
          <Checkbox
            v-model="
              form.is_classroom
            "
            binary
            :disabled="loading"
          />

          <span>
            {{
              t(
                'curriculumReferences.workloadTypes.fields.classroom',
              )
            }}
          </span>
        </label>

        <label>
          <Checkbox
            v-model="
              form.is_teaching_load
            "
            binary
            :disabled="loading"
          />

          <span>
            {{
              t(
                'curriculumReferences.workloadTypes.fields.teachingLoad',
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
.workload-type-form {
  display: grid;
  gap: 1.25rem;
}

.workload-type-form__grid {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.workload-type-form__wide {
  grid-column: 1 / -1;
}

.workload-type-form__flags {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  padding-top: 0.5rem;
}

.workload-type-form__flags label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  font-weight: 600;
}

@media (max-width: 767px) {
  .workload-type-form__grid {
    grid-template-columns:
      1fr;
  }

  .workload-type-form__wide {
    grid-column: auto;
  }

  .workload-type-form__flags {
    display: grid;
  }
}
</style>
