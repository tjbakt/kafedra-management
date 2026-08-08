<script setup lang="ts">
import Checkbox from 'primevue/checkbox'
import DatePicker from 'primevue/datepicker'
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

import type {
  AcademicDegreeOption,
  AcademicTitleOption,
  Gender,
  StaffMember,
  StaffMemberPayload,
} from '@/modules/staff/types'

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
    staffMember?: StaffMember | null

    academicDegrees: AcademicDegreeOption[]
    academicTitles: AcademicTitleOption[]

    loading?: boolean

    fieldErrors?: FieldErrors
    nonFieldErrors?: string[]
    generalError?: string
  }>(),
  {
    staffMember: null,

    loading: false,

    fieldErrors: () => ({}),
    nonFieldErrors: () => [],
    generalError: '',
  },
)

const emit = defineEmits<{
  submit: [payload: StaffMemberPayload]
}>()

const { t } = useI18n()

const form = reactive({
  personnel_number: '',

  last_name: '',
  first_name: '',
  middle_name: '',

  gender: '' as Gender,

  birth_date: null as Date | null,

  phone: '',
  email: '',

  academic_degree: null as number | null,
  academic_title: null as number | null,

  degree_awarded_date: null as Date | null,
  title_awarded_date: null as Date | null,

  is_active: true,

  notes: '',
})

const localErrors =
  reactive<Record<string, string>>({})

const isEditing = computed(
  () => Boolean(props.staffMember),
)

const title = computed(
  () =>
    isEditing.value
      ? t('staff.editTitle')
      : t('staff.createTitle'),
)

const genderOptions = computed(() => [
  {
    label: t('staff.genderNotSpecified'),
    value: '',
  },
  {
    label: t('staff.genderMale'),
    value: 'male',
  },
  {
    label: t('staff.genderFemale'),
    value: 'female',
  },
])

function clearLocalErrors(): void {
  Object.keys(localErrors).forEach(
    (key) => {
      delete localErrors[key]
    },
  )
}

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

function formatDate(
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

function resetForm(): void {
  form.personnel_number = ''

  form.last_name = ''
  form.first_name = ''
  form.middle_name = ''

  form.gender = ''

  form.birth_date = null

  form.phone = ''
  form.email = ''

  form.academic_degree = null
  form.academic_title = null

  form.degree_awarded_date = null
  form.title_awarded_date = null

  form.is_active = true

  form.notes = ''

  clearLocalErrors()
}

function fillForm(
  staffMember: StaffMember,
): void {
  form.personnel_number =
    staffMember.personnel_number

  form.last_name =
    staffMember.last_name

  form.first_name =
    staffMember.first_name

  form.middle_name =
    staffMember.middle_name

  form.gender =
    staffMember.gender

  form.birth_date =
    parseDate(
      staffMember.birth_date,
    )

  form.phone =
    staffMember.phone

  form.email =
    staffMember.email

  form.academic_degree =
    staffMember.academic_degree

  form.academic_title =
    staffMember.academic_title

  form.degree_awarded_date =
    parseDate(
      staffMember.degree_awarded_date,
    )

  form.title_awarded_date =
    parseDate(
      staffMember.title_awarded_date,
    )

  form.is_active =
    staffMember.is_active

  form.notes =
    staffMember.notes

  clearLocalErrors()
}

function validate(): boolean {
  clearLocalErrors()

  if (
    !form.personnel_number.trim()
  ) {
    localErrors.personnel_number =
      t(
        'staff.validation.personnelNumberRequired',
      )
  }

  if (!form.last_name.trim()) {
    localErrors.last_name =
      t(
        'staff.validation.lastNameRequired',
      )
  }

  if (!form.first_name.trim()) {
    localErrors.first_name =
      t(
        'staff.validation.firstNameRequired',
      )
  }

  if (
    form.email.trim() &&
    !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
      form.email.trim(),
    )
  ) {
    localErrors.email =
      t(
        'staff.validation.invalidEmail',
      )
  }

  if (
    form.degree_awarded_date &&
    !form.academic_degree
  ) {
    localErrors.degree_awarded_date =
      t(
        'staff.validation.degreeDateWithoutDegree',
      )
  }

  if (
    form.title_awarded_date &&
    !form.academic_title
  ) {
    localErrors.title_awarded_date =
      t(
        'staff.validation.titleDateWithoutTitle',
      )
  }

  const today = new Date()

  today.setHours(
    0,
    0,
    0,
    0,
  )

  if (
    form.birth_date &&
    form.birth_date > today
  ) {
    localErrors.birth_date =
      t(
        'staff.validation.birthDateFuture',
      )
  }

  return (
    Object.keys(localErrors)
      .length === 0
  )
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

function submit(): void {
  if (!validate()) {
    return
  }

  emit('submit', {
    personnel_number:
      form.personnel_number
        .trim()
        .toUpperCase(),

    last_name:
      form.last_name.trim(),

    first_name:
      form.first_name.trim(),

    middle_name:
      form.middle_name.trim(),

    gender:
      form.gender,

    birth_date:
      formatDate(
        form.birth_date,
      ),

    phone:
      form.phone.trim(),

    email:
      form.email.trim(),

    academic_degree:
      form.academic_degree,

    academic_title:
      form.academic_title,

    degree_awarded_date:
      formatDate(
        form.degree_awarded_date,
      ),

    title_awarded_date:
      formatDate(
        form.title_awarded_date,
      ),

    is_active:
      form.is_active,

    notes:
      form.notes.trim(),
  })
}

watch(
  () => form.academic_degree,
  (value) => {
    if (!value) {
      form.degree_awarded_date =
        null
    }
  },
)

watch(
  () => form.academic_title,
  (value) => {
    if (!value) {
      form.title_awarded_date =
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

    if (props.staffMember) {
      fillForm(
        props.staffMember,
      )

      return
    }

    resetForm()
  },
)

watch(
  () => props.staffMember,
  (staffMember) => {
    if (
      visible.value &&
      staffMember
    ) {
      fillForm(staffMember)
    }
  },
)
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="title"
    width="58rem"
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
      class="staff-form"
      novalidate
      @submit.prevent="submit"
    >
      <section>
        <h3>
          {{
            t(
              'staff.sections.personal',
            )
          }}
        </h3>

        <div
          class="staff-form__grid"
        >
          <BaseFormField
            :label="
              t(
                'staff.fields.personnelNumber',
              )
            "
            name="personnel_number"
            required
            :error="
              fieldError(
                'personnel_number',
              )
            "
          >
            <InputText
              id="personnel_number"
              v-model="
                form.personnel_number
              "
              maxlength="50"
              class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'staff.fields.gender',
              )
            "
            name="gender"
            :error="
              fieldError(
                'gender',
              )
            "
          >
            <Select
              v-model="
                form.gender
              "
              input-id="gender"
              :options="
                genderOptions
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
                'staff.fields.lastName',
              )
            "
            name="last_name"
            required
            :error="
              fieldError(
                'last_name',
              )
            "
          >
            <InputText
              id="last_name"
              v-model="
                form.last_name
              "
              maxlength="150"
              class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'staff.fields.firstName',
              )
            "
            name="first_name"
            required
            :error="
              fieldError(
                'first_name',
              )
            "
          >
            <InputText
              id="first_name"
              v-model="
                form.first_name
              "
              maxlength="150"
              class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'staff.fields.middleName',
              )
            "
            name="middle_name"
            :error="
              fieldError(
                'middle_name',
              )
            "
          >
            <InputText
              id="middle_name"
              v-model="
                form.middle_name
              "
              maxlength="150"
              class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'staff.fields.birthDate',
              )
            "
            name="birth_date"
            :error="
              fieldError(
                'birth_date',
              )
            "
          >
            <DatePicker
              v-model="
                form.birth_date
              "
              input-id="birth_date"
              date-format="dd.mm.yy"
              show-icon
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
              'staff.sections.contacts',
            )
          }}
        </h3>

        <div
          class="staff-form__grid"
        >
          <BaseFormField
            :label="
              t(
                'staff.fields.phone',
              )
            "
            name="phone"
            :error="
              fieldError(
                'phone',
              )
            "
          >
            <InputText
              id="phone"
              v-model="form.phone"
              maxlength="30"
              class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'staff.fields.email',
              )
            "
            name="email"
            :error="
              fieldError(
                'email',
              )
            "
          >
            <InputText
              id="email"
              v-model="form.email"
              type="email"
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
              'staff.sections.academic',
            )
          }}
        </h3>

        <div
          class="staff-form__grid"
        >
          <BaseFormField
            :label="
              t(
                'staff.fields.academicDegree',
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
              input-id="academic_degree"
              :options="
                academicDegrees
              "
              option-label="name_ru"
              option-value="id"
              show-clear
              filter
              class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'staff.fields.degreeDate',
              )
            "
            name="degree_awarded_date"
            :error="
              fieldError(
                'degree_awarded_date',
              )
            "
          >
            <DatePicker
              v-model="
                form.degree_awarded_date
              "
              input-id="degree_awarded_date"
              date-format="dd.mm.yy"
              show-icon
              class="w-full"
              :disabled="
                loading ||
                !form.academic_degree
              "
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'staff.fields.academicTitle',
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
              input-id="academic_title"
              :options="
                academicTitles
              "
              option-label="name_ru"
              option-value="id"
              show-clear
              filter
              class="w-full"
              :disabled="loading"
            />
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'staff.fields.titleDate',
              )
            "
            name="title_awarded_date"
            :error="
              fieldError(
                'title_awarded_date',
              )
            "
          >
            <DatePicker
              v-model="
                form.title_awarded_date
              "
              input-id="title_awarded_date"
              date-format="dd.mm.yy"
              show-icon
              class="w-full"
              :disabled="
                loading ||
                !form.academic_title
              "
            />
          </BaseFormField>
        </div>
      </section>

      <section>
        <h3>
          {{
            t(
              'staff.sections.additional',
            )
          }}
        </h3>

        <BaseFormField
          :label="
            t(
              'staff.fields.notes',
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
            id="notes"
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
          class="staff-form__checkbox"
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
                'staff.fields.active',
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
.staff-form {
  display: grid;
  gap: 1.5rem;
}

.staff-form section {
  display: grid;
  gap: 1rem;
}

.staff-form h3 {
  margin: 0;
  padding-bottom: 0.5rem;
  border-bottom:
    1px solid
    var(--app-border-color);
  font-size: 0.9rem;
}

.staff-form__grid {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.staff-form__checkbox {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  width: fit-content;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 767px) {
  .staff-form__grid {
    grid-template-columns: 1fr;
  }
}
</style>
