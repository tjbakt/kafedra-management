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

import { useI18n } from 'vue-i18n'

import BaseDialog from '@/components/base/BaseDialog.vue'
import BaseFormActions from '@/components/base/BaseFormActions.vue'
import BaseFormField from '@/components/base/BaseFormField.vue'

import FormValidationSummary from '@/components/forms/FormValidationSummary.vue'

import type {
  Department,
  DepartmentPayload,
  FacultyOption,
} from '@/modules/departments/types'

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
    department?: Department | null
    faculties: FacultyOption[]

    loading?: boolean

    fieldErrors?: FieldErrors
    nonFieldErrors?: string[]
    generalError?: string
  }>(),
  {
    department: null,

    loading: false,

    fieldErrors: () => ({}),
    nonFieldErrors: () => [],
    generalError: '',
  },
)

const emit = defineEmits<{
  submit: [payload: DepartmentPayload]
}>()

const { t } = useI18n()

const form = reactive({
  faculty: null as number | null,

  code: '',

  name_ru: '',
  name_uz: '',

  short_name_ru: '',
  short_name_uz: '',

  head_name: '',
  phone: '',
  email: '',
  room: '',

  is_active: true,

  sort_order: 0 as number | null,
})

const localErrors =
  reactive<Record<string, string>>({})

const isEditing = computed(
  () => Boolean(props.department),
)

const title = computed(
  () =>
    isEditing.value
      ? t(
          'departments.editTitle',
        )
      : t(
          'departments.createTitle',
        ),
)

const availableFaculties =
  computed(() =>
    props.faculties.filter(
      (faculty) =>
        faculty.is_active &&
        !faculty.is_archived,
    ),
  )

function resetLocalErrors(): void {
  Object.keys(localErrors).forEach(
    (key) => {
      delete localErrors[key]
    },
  )
}

function resetForm(): void {
  form.faculty = null

  form.code = ''

  form.name_ru = ''
  form.name_uz = ''

  form.short_name_ru = ''
  form.short_name_uz = ''

  form.head_name = ''
  form.phone = ''
  form.email = ''
  form.room = ''

  form.is_active = true
  form.sort_order = 0

  resetLocalErrors()
}

function fillForm(
  department: Department,
): void {
  form.faculty =
    department.faculty

  form.code =
    department.code

  form.name_ru =
    department.name_ru

  form.name_uz =
    department.name_uz

  form.short_name_ru =
    department.short_name_ru

  form.short_name_uz =
    department.short_name_uz

  form.head_name =
    department.head_name

  form.phone =
    department.phone

  form.email =
    department.email

  form.room =
    department.room

  form.is_active =
    department.is_active

  form.sort_order =
    department.sort_order

  resetLocalErrors()
}

function validate(): boolean {
  resetLocalErrors()

  if (!form.faculty) {
    localErrors.faculty =
      t(
        'departments.validation.facultyRequired',
      )
  }

  if (!form.code.trim()) {
    localErrors.code =
      t(
        'departments.validation.codeRequired',
      )
  }

  if (!form.name_ru.trim()) {
    localErrors.name_ru =
      t(
        'departments.validation.nameRuRequired',
      )
  }

  if (!form.name_uz.trim()) {
    localErrors.name_uz =
      t(
        'departments.validation.nameUzRequired',
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
        'departments.validation.invalidEmail',
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

  if (!form.faculty) {
    return
  }

  emit('submit', {
    faculty:
      form.faculty,

    code:
      form.code.trim(),

    name_ru:
      form.name_ru.trim(),

    name_uz:
      form.name_uz.trim(),

    short_name_ru:
      form.short_name_ru.trim(),

    short_name_uz:
      form.short_name_uz.trim(),

    head_name:
      form.head_name.trim(),

    phone:
      form.phone.trim(),

    email:
      form.email.trim(),

    room:
      form.room.trim(),

    is_active:
      form.is_active,

    sort_order:
      form.sort_order ?? 0,
  })
}

watch(
  () => visible.value,
  (isVisible) => {
    if (!isVisible) {
      return
    }

    if (props.department) {
      fillForm(
        props.department,
      )

      return
    }

    resetForm()
  },
)

watch(
  () => props.department,
  (department) => {
    if (
      visible.value &&
      department
    ) {
      fillForm(department)
    }
  },
)
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="title"
    width="52rem"
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
      class="department-form"
      novalidate
      @submit.prevent="submit"
    >
      <div
        class="department-form__grid"
      >
        <BaseFormField
          :label="
            t(
              'departments.fields.faculty',
            )
          "
          name="faculty"
          required
          :error="
            fieldError(
              'faculty',
            )
          "
        >
          <Select
            v-model="
              form.faculty
            "
            input-id="faculty"
            :options="
              availableFaculties
            "
            option-label="
              display_name
            "
            option-value="id"
            :placeholder="
              t(
                'departments.placeholders.faculty',
              )
            "
            :disabled="
              loading
            "
            filter
            class="w-full"
          >
            <template
              #option="{ option }"
            >
              <div
                class="faculty-option"
              >
                <strong>
                  {{
                    option.display_name
                  }}
                </strong>

                <small>
                  {{
                    option.university_name
                  }}
                  ·
                  {{
                    option.code
                  }}
                </small>
              </div>
            </template>
          </Select>
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'departments.fields.code',
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
            class="w-full"
            maxlength="30"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'departments.fields.nameRu',
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
            maxlength="255"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'departments.fields.nameUz',
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
            maxlength="255"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'departments.fields.shortNameRu',
            )
          "
          name="short_name_ru"
          :error="
            fieldError(
              'short_name_ru',
            )
          "
        >
          <InputText
            id="short_name_ru"
            v-model="
              form.short_name_ru
            "
            maxlength="100"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'departments.fields.shortNameUz',
            )
          "
          name="short_name_uz"
          :error="
            fieldError(
              'short_name_uz',
            )
          "
        >
          <InputText
            id="short_name_uz"
            v-model="
              form.short_name_uz
            "
            maxlength="100"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'departments.fields.head',
            )
          "
          name="head_name"
          :error="
            fieldError(
              'head_name',
            )
          "
        >
          <InputText
            id="head_name"
            v-model="
              form.head_name
            "
            maxlength="255"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'departments.fields.room',
            )
          "
          name="room"
          :error="
            fieldError('room')
          "
        >
          <InputText
            id="room"
            v-model="form.room"
            maxlength="100"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'departments.fields.phone',
            )
          "
          name="phone"
          :error="
            fieldError('phone')
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
              'departments.fields.email',
            )
          "
          name="email"
          :error="
            fieldError('email')
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

        <BaseFormField
          :label="
            t(
              'departments.fields.sortOrder',
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

        <div
          class="department-form__checkbox"
        >
          <Checkbox
            v-model="
              form.is_active
            "
            input-id="is_active"
            binary
            :disabled="loading"
          />

          <label
            for="is_active"
          >
            {{
              t(
                'departments.fields.active',
              )
            }}
          </label>
        </div>
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
.department-form {
  display: grid;
}

.department-form__grid {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.department-form__checkbox {
  display: flex;
  align-items: center;
  align-self: end;
  gap: 0.55rem;
  min-height: 2.75rem;
}

.department-form__checkbox label {
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

.faculty-option {
  display: grid;
  gap: 0.1rem;
}

.faculty-option strong {
  font-size: 0.82rem;
}

.faculty-option small {
  color:
    var(--app-text-muted);
  font-size: 0.7rem;
}

@media (max-width: 767px) {
  .department-form__grid {
    grid-template-columns: 1fr;
  }
}
</style>
