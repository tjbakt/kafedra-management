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

import {
  useLocaleStore,
} from '@/stores/locale'

import type {
  AcademicDegreeLookup,
  AcademicTitleLookup,
  AcademicYearOption,
  EmploymentLookup,
  SelectOption,
  StaffAcademicYearPayload,
  StaffAcademicYearRecord,
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
    record?: StaffAcademicYearRecord | null

    academicYears: AcademicYearOption[]
    employments: EmploymentLookup[]

    academicDegrees: AcademicDegreeLookup[]
    academicTitles: AcademicTitleLookup[]

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
    payload: StaffAcademicYearPayload,
  ]
}>()

const { t } = useI18n()

const localeStore =
  useLocaleStore()

const form = reactive({
  staff_employment:
    null as number | null,

  academic_year:
    null as number | null,

  rate:
    1 as number | null,

  academic_degree:
    null as number | null,

  academic_title:
    null as number | null,

  is_active: true,

  notes: '',
})

const localErrors =
  reactive<Record<string, string>>({})

const isEditing = computed(
  () => Boolean(props.record),
)

const dialogTitle = computed(
  () =>
    isEditing.value
      ? t(
          'staffAcademicYears.editTitle',
        )
      : t(
          'staffAcademicYears.createTitle',
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

const academicYearOptions =
  computed<
    SelectOption<number>[]
  >(() =>
    props.academicYears
      .filter(
        (year) =>
          year.is_active &&
          !year.is_archived,
      )
      .map((year) => ({
        value: year.id,
        label: year.name,

        description:
          year.is_closed
            ? t(
                'staffAcademicYears.closed',
              )
            : year.is_current
              ? t(
                  'staffAcademicYears.current',
                )
              : '',
      })),
  )

const employmentOptions =
  computed<
    SelectOption<number>[]
  >(() => {
    const result =
      props.employments
        .filter(
          (item) =>
            item.is_active &&
            !item.is_archived,
        )
        .map((item) => ({
          value: item.id,

          label:
            item.staff_member_name,

          description:
            `${item.department_name} · ${item.position_name}`,
        }))

    if (
      props.record &&
      !result.some(
        (item) =>
          item.value ===
          props.record
            ?.staff_employment,
      )
    ) {
      result.unshift({
        value:
          props.record
            .staff_employment,

        label:
          props.record
            .staff_member_name,

        description:
          `${props.record.department_name} · ${props.record.position_name}`,
      })
    }

    return result
  })

const degreeOptions =
  computed<
    SelectOption<number>[]
  >(() =>
    props.academicDegrees
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
      })),
  )

const titleOptions =
  computed<
    SelectOption<number>[]
  >(() =>
    props.academicTitles
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
      })),
  )

function clearLocalErrors(): void {
  Object.keys(localErrors).forEach(
    (key) => {
      delete localErrors[key]
    },
  )
}

function resetForm(): void {
  form.staff_employment = null
  form.academic_year = null

  form.rate = 1

  form.academic_degree = null
  form.academic_title = null

  form.is_active = true

  form.notes = ''

  clearLocalErrors()
}

function fillForm(
  record: StaffAcademicYearRecord,
): void {
  form.staff_employment =
    record.staff_employment

  form.academic_year =
    record.academic_year

  form.rate =
    Number(record.rate)

  form.academic_degree =
    record.academic_degree

  form.academic_title =
    record.academic_title

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

  if (
    !form.staff_employment
  ) {
    localErrors.staff_employment =
      t(
        'staffAcademicYears.validation.employmentRequired',
      )
  }

  if (!form.academic_year) {
    localErrors.academic_year =
      t(
        'staffAcademicYears.validation.yearRequired',
      )
  }

  if (
    form.rate === null ||
    form.rate < 0.01 ||
    form.rate > 3
  ) {
    localErrors.rate =
      t(
        'staffAcademicYears.validation.rateRange',
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
    !form.staff_employment ||
    !form.academic_year ||
    form.rate === null
  ) {
    return
  }

  emit('submit', {
    staff_employment:
      form.staff_employment,

    academic_year:
      form.academic_year,

    rate:
      form.rate,

    academic_degree:
      form.academic_degree,

    academic_title:
      form.academic_title,

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

    if (props.record) {
      fillForm(props.record)
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
    :title="dialogTitle"
    width="54rem"
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
      class="academic-year-form"
      novalidate
      @submit.prevent="submit"
    >
      <div
        class="
          academic-year-form__grid
        "
      >
        <BaseFormField
          :label="
            t(
              'staffAcademicYears.fields.employment',
            )
          "
          name="staff_employment"
          required
          :error="
            fieldError(
              'staff_employment',
            )
          "
        >
          <Select
            v-model="
              form.staff_employment
            "
            :options="
              employmentOptions
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
              'staffAcademicYears.fields.academicYear',
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
              'staffAcademicYears.fields.rate',
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

        <div />

        <BaseFormField
          :label="
            t(
              'staffAcademicYears.fields.academicDegree',
            )
          "
          name="academic_degree"
          :error="
            fieldError(
              'academic_degree',
            )
          "
        >
          <Select
            v-model="
              form.academic_degree
            "
            :options="
              degreeOptions
            "
            option-label="label"
            option-value="value"
            show-clear
            filter
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'staffAcademicYears.fields.academicTitle',
            )
          "
          name="academic_title"
          :error="
            fieldError(
              'academic_title',
            )
          "
        >
          <Select
            v-model="
              form.academic_title
            "
            :options="
              titleOptions
            "
            option-label="label"
            option-value="value"
            show-clear
            filter
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>
      </div>

      <BaseFormField
        :label="
          t(
            'staffAcademicYears.fields.notes',
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
          academic-year-form__checkbox
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
              'staffAcademicYears.fields.active',
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
.academic-year-form {
  display: grid;
  gap: 1rem;
}

.academic-year-form__grid {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.academic-year-form__checkbox {
  display: flex;
  width: fit-content;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
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
  .academic-year-form__grid {
    grid-template-columns: 1fr;
  }
}
</style>
