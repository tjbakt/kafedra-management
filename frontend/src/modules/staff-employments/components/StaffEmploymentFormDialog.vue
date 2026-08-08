<script setup lang="ts">
import Checkbox from 'primevue/checkbox'
import DatePicker from 'primevue/datepicker'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
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

import { useLocaleStore } from '@/stores/locale'

import type {
  DepartmentLookup,
  EmploymentType,
  SelectOption,
  StaffEmployment,
  StaffEmploymentPayload,
  StaffMemberLookup,
  StaffPositionLookup,
} from '@/modules/staff-employments/types'

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
    employment?: StaffEmployment | null

    staffMembers: StaffMemberLookup[]
    departments: DepartmentLookup[]
    positions: StaffPositionLookup[]

    loading?: boolean

    fieldErrors?: FieldErrors
    nonFieldErrors?: string[]
    generalError?: string
  }>(),
  {
    employment: null,

    loading: false,

    fieldErrors: () => ({}),
    nonFieldErrors: () => [],
    generalError: '',
  },
)

const emit = defineEmits<{
  submit: [
    payload: StaffEmploymentPayload,
  ]
}>()

const { t } = useI18n()
const localeStore = useLocaleStore()

const form = reactive({
  staff_member:
    null as number | null,

  department:
    null as number | null,

  position:
    null as number | null,

  employment_type:
    'primary' as EmploymentType,

  rate: 1 as number | null,

  start_date:
    null as Date | null,

  end_date:
    null as Date | null,

  is_primary: true,
  is_active: true,

  document_number: '',

  document_date:
    null as Date | null,

  notes: '',
})

const localErrors =
  reactive<Record<string, string>>({})

const isEditing = computed(
  () => Boolean(props.employment),
)

const dialogTitle = computed(
  () =>
    isEditing.value
      ? t(
          'staffEmployments.editTitle',
        )
      : t(
          'staffEmployments.createTitle',
        ),
)

function localizedName(
  ru: string | null | undefined,
  uz: string | null | undefined,
): string {
  if (localeStore.locale === 'uz') {
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

const staffMemberOptions =
  computed<SelectOption<number>[]>(() => {
    const result =
      props.staffMembers
        .filter(
          (item) =>
            item.is_active &&
            !item.is_archived,
        )
        .map((item) => ({
          value: item.id,

          label:
            item.full_name,

          description:
            item.personnel_number,
        }))

    if (
      props.employment &&
      !result.some(
        (item) =>
          item.value ===
          props.employment
            ?.staff_member,
      )
    ) {
      result.unshift({
        value:
          props.employment
            .staff_member,

        label:
          props.employment
            .staff_member_name,

        description: '',
      })
    }

    return result
  })

const departmentOptions =
  computed<SelectOption<number>[]>(() => {
    const result =
      props.departments
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
            item.faculty_name,
        }))

    if (
      props.employment &&
      !result.some(
        (item) =>
          item.value ===
          props.employment
            ?.department,
      )
    ) {
      result.unshift({
        value:
          props.employment
            .department,

        label:
          props.employment
            .department_name,

        description:
          props.employment
            .faculty_name,
      })
    }

    return result
  })

const positionOptions =
  computed<SelectOption<number>[]>(() => {
    const result =
      props.positions
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
            item.category_name,
        }))

    if (
      props.employment &&
      !result.some(
        (item) =>
          item.value ===
          props.employment
            ?.position,
      )
    ) {
      result.unshift({
        value:
          props.employment.position,

        label:
          props.employment
            .position_name,

        description: '',
      })
    }

    return result
  })

const employmentTypeOptions =
  computed<
    SelectOption<EmploymentType>[]
  >(() => [
    {
      value: 'primary',
      label:
        t(
          'staffEmployments.types.primary',
        ),
    },

    {
      value:
        'internal_part_time',

      label:
        t(
          'staffEmployments.types.internalPartTime',
        ),
    },

    {
      value:
        'external_part_time',

      label:
        t(
          'staffEmployments.types.externalPartTime',
        ),
    },

    {
      value: 'hourly',

      label:
        t(
          'staffEmployments.types.hourly',
        ),
    },
  ])

function parseDate(
  value: string | null,
): Date | null {
  if (!value) {
    return null
  }

  const [year, month, day] =
    value.split('-').map(Number)

  if (!year || !month || !day) {
    return null
  }

  return new Date(
    year,
    month - 1,
    day,
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
  Object.keys(
    localErrors,
  ).forEach((key) => {
    delete localErrors[key]
  })
}

function resetForm(): void {
  form.staff_member = null
  form.department = null
  form.position = null

  form.employment_type =
    'primary'

  form.rate = 1

  form.start_date = null
  form.end_date = null

  form.is_primary = true
  form.is_active = true

  form.document_number = ''
  form.document_date = null

  form.notes = ''

  clearLocalErrors()
}

function fillForm(
  employment: StaffEmployment,
): void {
  form.staff_member =
    employment.staff_member

  form.department =
    employment.department

  form.position =
    employment.position

  form.employment_type =
    employment.employment_type

  form.rate =
    Number(employment.rate)

  form.start_date =
    parseDate(
      employment.start_date,
    )

  form.end_date =
    parseDate(
      employment.end_date,
    )

  form.is_primary =
    employment.is_primary

  form.is_active =
    employment.is_active

  form.document_number =
    employment.document_number

  form.document_date =
    parseDate(
      employment.document_date,
    )

  form.notes =
    employment.notes

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

  if (!form.staff_member) {
    localErrors.staff_member =
      t(
        'staffEmployments.validation.staffRequired',
      )
  }

  if (!form.department) {
    localErrors.department =
      t(
        'staffEmployments.validation.departmentRequired',
      )
  }

  if (!form.position) {
    localErrors.position =
      t(
        'staffEmployments.validation.positionRequired',
      )
  }

  if (!form.start_date) {
    localErrors.start_date =
      t(
        'staffEmployments.validation.startDateRequired',
      )
  }

  if (
    form.rate === null ||
    form.rate < 0.01 ||
    form.rate > 3
  ) {
    localErrors.rate =
      t(
        'staffEmployments.validation.rateRange',
      )
  }

  if (
    form.start_date &&
    form.end_date &&
    form.end_date <
      form.start_date
  ) {
    localErrors.end_date =
      t(
        'staffEmployments.validation.endBeforeStart',
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
    !form.staff_member ||
    !form.department ||
    !form.position ||
    !form.start_date ||
    form.rate === null
  ) {
    return
  }

  emit('submit', {
    staff_member:
      form.staff_member,

    department:
      form.department,

    position:
      form.position,

    employment_type:
      form.is_primary
        ? 'primary'
        : form.employment_type,

    rate:
      form.rate,

    start_date:
      serializeDate(
        form.start_date,
      ) as string,

    end_date:
      serializeDate(
        form.end_date,
      ),

    is_primary:
      form.is_primary,

    is_active:
      form.is_active,

    document_number:
      form.document_number.trim(),

    document_date:
      serializeDate(
        form.document_date,
      ),

    notes:
      form.notes.trim(),
  })
}

watch(
  () => form.is_primary,
  (value) => {
    if (value) {
      form.employment_type =
        'primary'
    } else if (
      form.employment_type ===
      'primary'
    ) {
      form.employment_type =
        'internal_part_time'
    }
  },
)

watch(
  () => visible.value,
  (isVisible) => {
    if (!isVisible) {
      return
    }

    if (props.employment) {
      fillForm(
        props.employment,
      )

      return
    }

    resetForm()
  },
)

watch(
  () => props.employment,
  (employment) => {
    if (
      visible.value &&
      employment
    ) {
      fillForm(employment)
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
      class="employment-form"
      novalidate
      @submit.prevent="submit"
    >
      <section>
        <h3>
          {{
            t(
              'staffEmployments.sections.assignment',
            )
          }}
        </h3>

        <div
          class="
            employment-form__grid
          "
        >
          <BaseFormField
            :label="
              t(
                'staffEmployments.fields.staffMember',
              )
            "
            name="staff_member"
            required
            :error="
              fieldError(
                'staff_member',
              )
            "
          >
            <Select
              v-model="
                form.staff_member
              "
              input-id="staff_member"
              :options="
                staffMemberOptions
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
                  class="
                    select-option
                  "
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
                'staffEmployments.fields.department',
              )
            "
            name="department"
            required
            :error="
              fieldError(
                'department',
              )
            "
          >
            <Select
              v-model="
                form.department
              "
              input-id="department"
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
                  class="
                    select-option
                  "
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
                'staffEmployments.fields.position',
              )
            "
            name="position"
            required
            :error="
              fieldError(
                'position',
              )
            "
          >
            <Select
              v-model="
                form.position
              "
              input-id="position"
              :options="
                positionOptions
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
                  class="
                    select-option
                  "
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
                'staffEmployments.fields.employmentType',
              )
            "
            name="employment_type"
            :error="
              fieldError(
                'employment_type',
              )
            "
          >
            <Select
              v-model="
                form.employment_type
              "
              input-id="
                employment_type
              "
              :options="
                employmentTypeOptions
              "
              option-label="label"
              option-value="value"
              class="w-full"
              :disabled="
                loading ||
                form.is_primary
              "
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'staffEmployments.fields.rate',
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
              input-id="rate"
              :min="0.01"
              :max="3"
              :min-fraction-digits="2"
              :max-fraction-digits="2"
              :step="0.25"
              :use-grouping="false"
              class="w-full"
              input-class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <div
            class="
              employment-form__flags
            "
          >
            <label>
              <Checkbox
                v-model="
                  form.is_primary
                "
                binary
                :disabled="loading"
              />

              <span>
                {{
                  t(
                    'staffEmployments.fields.primary',
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
                    'staffEmployments.fields.active',
                  )
                }}
              </span>
            </label>
          </div>
        </div>
      </section>

      <section>
        <h3>
          {{
            t(
              'staffEmployments.sections.period',
            )
          }}
        </h3>

        <div
          class="
            employment-form__grid
          "
        >
          <BaseFormField
            :label="
              t(
                'staffEmployments.fields.startDate',
              )
            "
            name="start_date"
            required
            :error="
              fieldError(
                'start_date',
              )
            "
          >
            <DatePicker
              v-model="
                form.start_date
              "
              input-id="start_date"
              date-format="dd.mm.yy"
              show-icon
              class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'staffEmployments.fields.endDate',
              )
            "
            name="end_date"
            :error="
              fieldError(
                'end_date',
              )
            "
          >
            <DatePicker
              v-model="
                form.end_date
              "
              input-id="end_date"
              date-format="dd.mm.yy"
              show-icon
              class="w-full"
              :min-date="
                form.start_date ||
                undefined
              "
              :disabled="loading"
            />
          </BaseFormField>
        </div>
      </section>

      <section>
        <h3>
          {{
            t(
              'staffEmployments.sections.document',
            )
          }}
        </h3>

        <div
          class="
            employment-form__grid
          "
        >
          <BaseFormField
            :label="
              t(
                'staffEmployments.fields.documentNumber',
              )
            "
            name="document_number"
            :error="
              fieldError(
                'document_number',
              )
            "
          >
            <InputText
              id="document_number"
              v-model="
                form.document_number
              "
              maxlength="100"
              class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'staffEmployments.fields.documentDate',
              )
            "
            name="document_date"
            :error="
              fieldError(
                'document_date',
              )
            "
          >
            <DatePicker
              v-model="
                form.document_date
              "
              input-id="
                document_date
              "
              date-format="dd.mm.yy"
              show-icon
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
              'staffEmployments.fields.notes',
            )
          "
          name="notes"
          :error="
            fieldError('notes')
          "
        >
          <Textarea
            id="notes"
            v-model="form.notes"
            rows="4"
            auto-resize
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>
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
.employment-form {
  display: grid;
  gap: 1.5rem;
}

.employment-form section {
  display: grid;
  gap: 1rem;
}

.employment-form h3 {
  margin: 0;
  padding-bottom: 0.5rem;
  border-bottom:
    1px solid
    var(--app-border-color);
  font-size: 0.9rem;
}

.employment-form__grid {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.employment-form__flags {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  min-height: 2.75rem;
}

.employment-form__flags label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

.select-option {
  display: grid;
  gap: 0.1rem;
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
  .employment-form__grid {
    grid-template-columns: 1fr;
  }

  .employment-form__flags {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
