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

import { useI18n } from 'vue-i18n'

import BaseDialog from '@/components/base/BaseDialog.vue'
import BaseFormActions from '@/components/base/BaseFormActions.vue'
import BaseFormField from '@/components/base/BaseFormField.vue'

import FormValidationSummary from '@/components/forms/FormValidationSummary.vue'

import type {
  AcademicYearOption,
  WorkloadNorm,
  WorkloadNormPayload,
} from '@/modules/staff-academic-years/types'

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
    norm?: WorkloadNorm | null

    academicYears: AcademicYearOption[]

    loading?: boolean

    fieldErrors?: FieldErrors
    nonFieldErrors?: string[]
    generalError?: string
  }>(),
  {
    norm: null,

    loading: false,

    fieldErrors: () => ({}),
    nonFieldErrors: () => [],
    generalError: '',
  },
)

const emit = defineEmits<{
  submit: [
    payload: WorkloadNormPayload,
  ]
}>()

const { t } = useI18n()

const form = reactive({
  academic_year:
    null as number | null,

  rate:
    1 as number | null,

  has_academic_degree:
    false,

  has_academic_title:
    false,

  annual_hours:
    0 as number | null,

  is_active:
    true,

  notes:
    '',
})

const localErrors =
  reactive<Record<string, string>>({})

const dialogTitle = computed(
  () =>
    props.norm
      ? t(
          'workloadNorms.editTitle',
        )
      : t(
          'workloadNorms.createTitle',
        ),
)

const academicYearOptions =
  computed(() =>
    props.academicYears.map(
      (year) => ({
        value: year.id,
        label: year.name,
      }),
    ),
  )

function clearLocalErrors(): void {
  Object.keys(localErrors).forEach(
    (key) => {
      delete localErrors[key]
    },
  )
}

function resetForm(): void {
  form.academic_year = null

  form.rate = 1

  form.has_academic_degree =
    false

  form.has_academic_title =
    false

  form.annual_hours = 0

  form.is_active = true

  form.notes = ''

  clearLocalErrors()
}

function fillForm(
  norm: WorkloadNorm,
): void {
  form.academic_year =
    norm.academic_year

  form.rate =
    Number(norm.rate)

  form.has_academic_degree =
    norm.has_academic_degree

  form.has_academic_title =
    norm.has_academic_title

  form.annual_hours =
    Number(norm.annual_hours)

  form.is_active =
    norm.is_active

  form.notes =
    norm.notes

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

  if (!form.academic_year) {
    localErrors.academic_year =
      t(
        'workloadNorms.validation.yearRequired',
      )
  }

  if (
    form.rate === null ||
    form.rate < 0.01 ||
    form.rate > 3
  ) {
    localErrors.rate =
      t(
        'workloadNorms.validation.rateRange',
      )
  }

  if (
    form.annual_hours === null ||
    form.annual_hours < 0 ||
    form.annual_hours > 10000
  ) {
    localErrors.annual_hours =
      t(
        'workloadNorms.validation.hoursRange',
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
    !form.academic_year ||
    form.rate === null ||
    form.annual_hours === null
  ) {
    return
  }

  emit('submit', {
    academic_year:
      form.academic_year,

    rate:
      form.rate,

    has_academic_degree:
      form.has_academic_degree,

    has_academic_title:
      form.has_academic_title,

    annual_hours:
      form.annual_hours,

    is_active:
      form.is_active,

    notes:
      form.notes.trim(),
  })
}

watch(
  () => visible.value,
  (isVisible) => {
    if (!isVisible) {
      return
    }

    if (props.norm) {
      fillForm(props.norm)
      return
    }

    resetForm()
  },
)

watch(
  () => props.norm,
  (norm) => {
    if (
      visible.value &&
      norm
    ) {
      fillForm(norm)
    }
  },
)
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="dialogTitle"
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
      class="norm-form"
      novalidate
      @submit.prevent="submit"
    >
      <div
        class="norm-form__grid"
      >
        <BaseFormField
          :label="
            t(
              'workloadNorms.fields.academicYear',
            )
          "
          name="academic_year"
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
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'workloadNorms.fields.rate',
            )
          "
          name="rate"
          required
          :error="
            fieldError('rate')
          "
        >
          <InputNumber
            v-model="form.rate"
            :min="0.01"
            :max="3"
            :step="0.25"
            :min-fraction-digits="2"
            :max-fraction-digits="2"
            :use-grouping="false"
            class="w-full"
            input-class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'workloadNorms.fields.annualHours',
            )
          "
          name="annual_hours"
          required
          :error="
            fieldError(
              'annual_hours',
            )
          "
        >
          <InputNumber
            v-model="
              form.annual_hours
            "
            :min="0"
            :max="10000"
            :min-fraction-digits="2"
            :max-fraction-digits="2"
            :use-grouping="false"
            class="w-full"
            input-class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <div
          class="
            norm-form__flags
          "
        >
          <label>
            <Checkbox
              v-model="
                form.has_academic_degree
              "
              binary
              :disabled="loading"
            />

            <span>
              {{
                t(
                  'workloadNorms.fields.hasDegree',
                )
              }}
            </span>
          </label>

          <label>
            <Checkbox
              v-model="
                form.has_academic_title
              "
              binary
              :disabled="loading"
            />

            <span>
              {{
                t(
                  'workloadNorms.fields.hasTitle',
                )
              }}
            </span>
          </label>
        </div>
      </div>

      <BaseFormField
        :label="
          t(
            'workloadNorms.fields.notes',
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
          norm-form__active
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
              'workloadNorms.fields.active',
            )
          }}
        </span>
      </label>
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
.norm-form {
  display: grid;
  gap: 1rem;
}

.norm-form__grid {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.norm-form__flags {
  display: grid;
  align-content: center;
  gap: 0.65rem;
}

.norm-form__flags label,
.norm-form__active {
  display: flex;
  width: fit-content;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 767px) {
  .norm-form__grid {
    grid-template-columns: 1fr;
  }
}
</style>
