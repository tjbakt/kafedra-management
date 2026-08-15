<script setup lang="ts">
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'

import Checkbox from 'primevue/checkbox'

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
  FieldErrors,
} from '@/types/validation'

import {
  getFieldError,
} from '@/utils/api-errors'

import type {
  CurriculumWorkload,
  CurriculumWorkloadPayload,
  WorkloadCalculationMode,
  WorkloadType,
} from '@/modules/curriculum-disciplines/workload-types'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props =
  withDefaults(
    defineProps<{
      curriculumDisciplineId:
        number

      record?:
        CurriculumWorkload | null

      workloadTypes:
        WorkloadType[]

      loading?: boolean

      fieldErrors?:
        FieldErrors

      nonFieldErrors?:
        string[]

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

const emit =
  defineEmits<{
    submit: [
      payload:
        CurriculumWorkloadPayload,
    ]
  }>()

const { t } = useI18n()

const form = reactive({
  workload_type:
    null as number | null,

  calculation_mode:
    'fixed' as WorkloadCalculationMode,

  base_hours:
    0 as number | null,

  students_per_unit:
    null as number | null,

  is_active:
    true,

  notes:
    '',
})

const localErrors =
  reactive<Record<string, string>>({})

const title =
  computed(() =>
    props.record
      ? t(
          'curriculumWorkloads.editTitle',
        )
      : t(
          'curriculumWorkloads.createTitle',
        ),
  )

const workloadTypeOptions =
  computed(() =>
    props.workloadTypes
      .filter(
        (item) =>
          item.is_active &&
          !item.is_archived,
      )
      .map(
        (item) => ({
          value: item.id,

          label:
            item.display_name ||
            item.name_ru,

          description:
            item.code,

          defaultCalculationMode:
            item.calculation_mode,
        }),
      ),
  )

const calculationModeOptions =
  computed(() => [
    {
      value: 'fixed',
      label: t(
        'curriculumWorkloads.calculationModes.fixed',
      ),
    },

    {
      value: 'per_group',
      label: t(
        'curriculumWorkloads.calculationModes.perGroup',
      ),
    },

    {
      value: 'per_subgroup',
      label: t(
        'curriculumWorkloads.calculationModes.perSubgroup',
      ),
    },

    {
      value: 'per_student',
      label: t(
        'curriculumWorkloads.calculationModes.perStudent',
      ),
    },
  ])

const requiresStudentsPerUnit =
  computed(
    () =>
      form.calculation_mode ===
        'per_student' ||
      form.calculation_mode ===
        'per_subgroup',
  )

function clearErrors(): void {
  Object.keys(localErrors)
    .forEach(
      (key) => {
        delete localErrors[key]
      },
    )
}

function resetForm(): void {
  form.workload_type =
    null

  form.calculation_mode =
    'fixed'

  form.base_hours =
    0

  form.students_per_unit =
    null

  form.is_active =
    true

  form.notes =
    ''

  clearErrors()
}

function fillForm(
  record: CurriculumWorkload,
): void {
  form.workload_type =
    record.workload_type

  form.calculation_mode =
    record.calculation_mode

  form.base_hours =
    Number(
      record.base_hours,
    )

  form.students_per_unit =
    record.students_per_unit

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

  if (
    !form.workload_type
  ) {
    localErrors.workload_type =
      t(
        'curriculumWorkloads.validation.workloadTypeRequired',
      )
  }

  if (
    form.base_hours === null ||
    form.base_hours < 0
  ) {
    localErrors.base_hours =
      t(
        'curriculumWorkloads.validation.baseHoursNonNegative',
      )
  }

  if (
    requiresStudentsPerUnit.value &&
    (
      form.students_per_unit ===
        null ||
      form.students_per_unit < 1
    )
  ) {
    localErrors.students_per_unit =
      t(
        'curriculumWorkloads.validation.studentsPerUnitRequired',
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
    !form.workload_type ||
    form.base_hours === null
  ) {
    return
  }

  emit(
    'submit',
    {
      curriculum_discipline:
        props.curriculumDisciplineId,

      workload_type:
        form.workload_type,

      calculation_mode:
        form.calculation_mode,

      base_hours:
        form.base_hours,

      students_per_unit:
        form.students_per_unit,

      is_active:
        form.is_active,

      notes:
        form.notes.trim(),
    },
  )
}

watch(
  () => visible.value,
  (value) => {
    if (!value) {
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

watch(
  () => form.workload_type,
  (workloadTypeId) => {
    if (
      !workloadTypeId ||
      props.record
    ) {
      return
    }

    const workloadType =
      props.workloadTypes.find(
        (item) =>
          item.id ===
          workloadTypeId,
      )

    if (
      workloadType
    ) {
      form.calculation_mode =
        workloadType.calculation_mode
    }
  },
)
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="title"
    width="48rem"
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
      class="curriculum-workload-form"
      novalidate
      @submit.prevent="submit"
    >
      <BaseFormField
        :label="
          t(
            'curriculumWorkloads.fields.workloadType',
          )
        "
        name="workload_type"
        required
        :error="
          fieldError(
            'workload_type',
          )
        "
      >
        <Select
          v-model="
            form.workload_type
          "
          :options="
            workloadTypeOptions
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
            'curriculumWorkloads.fields.calculationMode',
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
            'curriculumWorkloads.fields.baseHours',
          )
        "
        name="base_hours"
        required
        :error="
          fieldError(
            'base_hours',
          )
        "
      >
        <InputNumber
          v-model="
            form.base_hours
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
            'curriculumWorkloads.fields.studentsPerUnit',
          )
        "
        name="students_per_unit"
        :error="
          fieldError(
            'students_per_unit',
          )
        "
      >
        <InputNumber
          v-model="
            form.students_per_unit
          "
          :min="1"
          :use-grouping="false"
          class="w-full"
          input-class="w-full"
          :disabled="
            loading ||
            !requiresStudentsPerUnit
          "
        />
      </BaseFormField>

      <label class="curriculum-workload-form__active">
        <Checkbox v-model="form.is_active" binary :disabled="loading" />
        <span>
          {{ t( 'curriculumWorkloads.activeField',) }}
        </span>
      </label>

      <BaseFormField
        :label="
          t(
            'curriculumWorkloads.fields.notes',
          )
        "
        name="notes"
      >
        <Textarea
          v-model="
            form.notes
          "
          rows="4"
          class="w-full"
          :disabled="loading"
        />
      </BaseFormField>

      <BaseFormActions
        :loading="loading"
        :save-label="t('common.save')"
        :cancel-label="t('common.cancel')"
        @submit="submit"
        @cancel="visible = false"
      />
    </form>
  </BaseDialog>
</template>

<style scoped>
.curriculum-workload-form__active {
  display: flex;
  align-items: center;
  gap: 0.5rem;

  width: fit-content;

  font-size: 0.82rem;
  font-weight: 600;
}

.curriculum-workload-form {
  display: grid;
  gap: 1rem;
}

.select-option {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.select-option small {
  opacity: 0.7;
}
</style>
