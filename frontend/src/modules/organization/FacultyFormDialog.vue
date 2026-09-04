<script setup lang="ts">
import {
  reactive,
  watch,
} from 'vue'

import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import Message from 'primevue/message'

import type {
  Faculty,
  FacultyPayload,
  FacultyType,
  UniversityOption,
} from '@/modules/organization/types'

import type {
  FieldErrors,
} from '@/types/validation'

interface Props {
  modelValue: boolean
  faculty: Faculty | null
  universities: UniversityOption[]
  loading?: boolean
  fieldErrors?: FieldErrors
  nonFieldErrors?: string[]
  generalError?: string
}

const props = withDefaults(
  defineProps<Props>(),
  {
    loading: false,
    fieldErrors: () => ({}),
    nonFieldErrors: () => [],
    generalError: '',
  },
)

const emit = defineEmits<{
  'update:modelValue': [
    value: boolean,
  ]

  submit: [
    payload: FacultyPayload,
  ]
}>()

const form =
  reactive<FacultyPayload>({
    university: 0,
    faculty_type: 'standard',
    code: '',
    name_ru: '',
    name_uz: '',
    short_name_ru: '',
    short_name_uz: '',
    dean_name: '',
    phone: '',
    email: '',
    is_active: true,
    sort_order: 0,
  })

const facultyTypeOptions = [
  {
    value: 'standard' as FacultyType,
    label: 'Обычный факультет',
  },
  {
    value: 'magistracy' as FacultyType,
    label: 'Отделение магистратуры',
  },
]

function resetForm(): void {
  form.university = 0
  form.faculty_type = 'standard'
  form.code = ''
  form.name_ru = ''
  form.name_uz = ''
  form.short_name_ru = ''
  form.short_name_uz = ''
  form.dean_name = ''
  form.phone = ''
  form.email = ''
  form.is_active = true
  form.sort_order = 0
}

function fillForm(
  faculty: Faculty | null,
): void {
  if (!faculty) {
    resetForm()
    return
  }

  form.university =
    faculty.university

  form.faculty_type =
    faculty.faculty_type

  form.code =
    faculty.code

  form.name_ru =
    faculty.name_ru

  form.name_uz =
    faculty.name_uz

  form.short_name_ru =
    faculty.short_name_ru

  form.short_name_uz =
    faculty.short_name_uz

  form.dean_name =
    faculty.dean_name

  form.phone =
    faculty.phone

  form.email =
    faculty.email

  form.is_active =
    faculty.is_active

  form.sort_order =
    faculty.sort_order
}

watch(
  () => props.modelValue,
  (visible) => {
    if (visible) {
      fillForm(props.faculty)
    }
  },
)

watch(
  () => props.faculty,
  (faculty) => {
    if (props.modelValue) {
      fillForm(faculty)
    }
  },
)

function errorFor(
  field: string,
): string {
  const value =
    props.fieldErrors?.[field]

  if (!value) {
    return ''
  }

  if (Array.isArray(value)) {
    return value.join(', ')
  }

  return String(value)
}

function close(): void {
  emit(
    'update:modelValue',
    false,
  )
}

function submit(): void {
  emit(
    'submit',
    {
      university:
        form.university,

      faculty_type:
        form.faculty_type,

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

      dean_name:
        form.dean_name.trim(),

      phone:
        form.phone.trim(),

      email:
        form.email.trim(),

      is_active:
        form.is_active,

      sort_order:
        form.sort_order ?? 0,
    },
  )
}
</script>

<template>
  <Dialog
    :visible="modelValue"
    :header="
      faculty
        ? 'Редактирование факультета'
        : 'Добавление факультета'
    "
    modal
    :style="{ width: '52rem' }"
    :breakpoints="{
      '960px': '80vw',
      '640px': '95vw',
    }"
    @update:visible="
      emit(
        'update:modelValue',
        $event,
      )
    "
  >
    <div class="form-grid">
      <Message
        v-if="generalError"
        severity="error"
        :closable="false"
        class="form-error"
      >
        {{ generalError }}
      </Message>

      <Message
        v-for="error in nonFieldErrors"
        :key="error"
        severity="error"
        :closable="false"
        class="form-error"
      >
        {{ error }}
      </Message>

      <div class="field field--wide">
        <label for="faculty-university">
          ВУЗ
        </label>

        <Select
          id="faculty-university"
          v-model="form.university"
          :options="universities"
          option-label="display_name"
          option-value="id"
          placeholder="Выберите ВУЗ"
          filter
          :invalid="
            Boolean(
              errorFor(
                'university',
              ),
            )
          "
        />

        <small
          v-if="
            errorFor('university')
          "
          class="error-text"
        >
          {{
            errorFor('university')
          }}
        </small>
      </div>

      <div class="field">
        <label for="faculty-type">
          Тип
        </label>

        <Select
          id="faculty-type"
          v-model="form.faculty_type"
          :options="
            facultyTypeOptions
          "
          option-label="label"
          option-value="value"
        />
      </div>

      <div class="field">
        <label for="faculty-code">
          Код
        </label>

        <InputText
          id="faculty-code"
          v-model="form.code"
          maxlength="30"
          :invalid="
            Boolean(
              errorFor('code'),
            )
          "
        />

        <small
          v-if="errorFor('code')"
          class="error-text"
        >
          {{ errorFor('code') }}
        </small>
      </div>

      <div class="field">
        <label for="faculty-sort">
          Порядок сортировки
        </label>

        <InputNumber
          id="faculty-sort"
          v-model="form.sort_order"
          :min="0"
          :use-grouping="false"
        />
      </div>

      <div class="field field--wide">
        <label for="faculty-name-ru">
          Название на русском
        </label>

        <InputText
          id="faculty-name-ru"
          v-model="form.name_ru"
          maxlength="255"
          :invalid="
            Boolean(
              errorFor('name_ru'),
            )
          "
        />
      </div>

      <div class="field field--wide">
        <label for="faculty-name-uz">
          Название на узбекском
        </label>

        <InputText
          id="faculty-name-uz"
          v-model="form.name_uz"
          maxlength="255"
          :invalid="
            Boolean(
              errorFor('name_uz'),
            )
          "
        />
      </div>

      <div class="field">
        <label for="faculty-short-ru">
          Краткое название RU
        </label>

        <InputText
          id="faculty-short-ru"
          v-model="
            form.short_name_ru
          "
          maxlength="100"
        />
      </div>

      <div class="field">
        <label for="faculty-short-uz">
          Краткое название UZ
        </label>

        <InputText
          id="faculty-short-uz"
          v-model="
            form.short_name_uz
          "
          maxlength="100"
        />
      </div>

      <div class="field field--wide">
        <label for="faculty-dean">
          Декан / руководитель
        </label>

        <InputText
          id="faculty-dean"
          v-model="form.dean_name"
          maxlength="255"
        />
      </div>

      <div class="field">
        <label for="faculty-phone">
          Телефон
        </label>

        <InputText
          id="faculty-phone"
          v-model="form.phone"
          maxlength="30"
        />
      </div>

      <div class="field">
        <label for="faculty-email">
          Электронная почта
        </label>

        <InputText
          id="faculty-email"
          v-model="form.email"
          maxlength="254"
          :invalid="
            Boolean(
              errorFor('email'),
            )
          "
        />
      </div>

      <div class="field field--wide">
        <div class="checkbox-field">
          <Checkbox
            v-model="form.is_active"
            binary
            input-id="faculty-active"
          />

          <label
            for="faculty-active"
          >
            Факультет активен
          </label>
        </div>
      </div>
    </div>

    <template #footer>
      <Button
        label="Отмена"
        severity="secondary"
        text
        :disabled="loading"
        @click="close"
      />

      <Button
        :label="
          faculty
            ? 'Сохранить'
            : 'Создать'
        "
        icon="pi pi-check"
        :loading="loading"
        @click="submit"
      />
    </template>
  </Dialog>
</template>

<style scoped>
.form-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.field {
  display: grid;
  gap: 0.4rem;
}

.field--wide {
  grid-column: 1 / -1;
}

.field label {
  font-weight: 600;
}

.field :deep(.p-inputtext),
.field :deep(.p-select),
.field :deep(.p-inputnumber) {
  width: 100%;
}

.checkbox-field {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.error-text {
  color: var(--p-red-500);
}

.form-error {
  grid-column: 1 / -1;
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .field--wide {
    grid-column: auto;
  }
}
</style>
