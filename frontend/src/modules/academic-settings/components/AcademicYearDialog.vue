<script setup lang="ts">
import Checkbox from 'primevue/checkbox'
import InputNumber from 'primevue/inputnumber'

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
  AcademicYear,
  AcademicYearPayload,
} from '@/modules/academic-settings/types'

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
    academicYear?: AcademicYear | null

    loading?: boolean

    fieldErrors?: FieldErrors
    nonFieldErrors?: string[]
    generalError?: string
  }>(),
  {
    academicYear: null,
    loading: false,

    fieldErrors: () => ({}),
    nonFieldErrors: () => [],
    generalError: '',
  },
)

const emit = defineEmits<{
  submit: [
    payload: AcademicYearPayload,
  ]
}>()

const { t } = useI18n()

const form = reactive({
  start_year:
    new Date().getFullYear(),

  end_year:
    new Date().getFullYear() + 1,

  is_current: false,
  is_active: true,
})

const localErrors =
  reactive<Record<string, string>>({})

const title = computed(
  () =>
    props.academicYear
      ? t(
          'academicSettings.academicYears.editTitle',
        )
      : t(
          'academicSettings.academicYears.createTitle',
        ),
)

function clearErrors(): void {
  Object.keys(localErrors).forEach(
    (key) => {
      delete localErrors[key]
    },
  )
}

function resetForm(): void {
  const year =
    new Date().getFullYear()

  form.start_year = year
  form.end_year = year + 1

  form.is_current = false
  form.is_active = true

  clearErrors()
}

function fillForm(
  year: AcademicYear,
): void {
  form.start_year =
    year.start_year

  form.end_year =
    year.end_year

  form.is_current =
    year.is_current

  form.is_active =
    year.is_active

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
    form.start_year < 2000 ||
    form.start_year > 2200
  ) {
    localErrors.start_year =
      t(
        'academicSettings.academicYears.validation.startYear',
      )
  }

  if (
    form.end_year !==
    form.start_year + 1
  ) {
    localErrors.end_year =
      t(
        'academicSettings.academicYears.validation.endYear',
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
    start_year:
      form.start_year,

    end_year:
      form.end_year,

    is_current:
      form.is_current,

    is_active:
      form.is_active,
  })
}

watch(
  () => form.start_year,
  (value) => {
    if (!props.academicYear) {
      form.end_year =
        value + 1
    }
  },
)

watch(
  () => visible.value,
  (value) => {
    if (!value) {
      return
    }

    if (props.academicYear) {
      fillForm(
        props.academicYear,
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
    width="38rem"
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

    <div
      class="academic-year-form"
    >
      <BaseFormField
        :label="
          t(
            'academicSettings.academicYears.fields.startYear',
          )
        "
        name="start_year"
        required
        :error="
          fieldError('start_year')
        "
      >
        <InputNumber
          v-model="
            form.start_year
          "
          :min="2000"
          :max="2200"
          :use-grouping="false"
          class="w-full"
          input-class="w-full"
        />
      </BaseFormField>

      <BaseFormField
        :label="
          t(
            'academicSettings.academicYears.fields.endYear',
          )
        "
        name="end_year"
        required
        :error="
          fieldError('end_year')
        "
      >
        <InputNumber
          v-model="
            form.end_year
          "
          :min="2001"
          :max="2201"
          :use-grouping="false"
          class="w-full"
          input-class="w-full"
        />
      </BaseFormField>

      <label>
        <Checkbox
          v-model="
            form.is_current
          "
          binary
        />

        <span>
          {{
            t(
              'academicSettings.academicYears.fields.current',
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
        />

        <span>
          {{
            t(
              'academicSettings.academicYears.fields.active',
            )
          }}
        </span>
      </label>
    </div>

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
.academic-year-form {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.academic-year-form label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  font-weight: 600;
}

@media (max-width: 575px) {
  .academic-year-form {
    grid-template-columns: 1fr;
  }
}
</style>
