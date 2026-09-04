<script setup lang="ts">
import {
  computed,
  reactive,
  watch,
} from 'vue'

import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import Message from 'primevue/message'

import type {
  University,
  UniversityPayload,
} from '@/modules/organization/types'

import type {
  FieldErrors,
} from '@/types/validation'

interface Props {
  modelValue: boolean
  university: University | null
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
    payload: UniversityPayload,
  ]
}>()

const form = reactive<
  UniversityPayload
>({
  code: '',
  name_ru: '',
  name_uz: '',
  short_name_ru: '',
  short_name_uz: '',
  address_ru: '',
  address_uz: '',
  phone: '',
  email: '',
  website: '',
  is_active: true,
  sort_order: 0,
})

function resetForm(): void {
  form.code = ''
  form.name_ru = ''
  form.name_uz = ''
  form.short_name_ru = ''
  form.short_name_uz = ''
  form.address_ru = ''
  form.address_uz = ''
  form.phone = ''
  form.email = ''
  form.website = ''
  form.is_active = true
  form.sort_order = 0
}

function fillForm(
  university: University | null,
): void {
  if (!university) {
    resetForm()
    return
  }

  form.code = university.code
  form.name_ru = university.name_ru
  form.name_uz = university.name_uz
  form.short_name_ru =
    university.short_name_ru
  form.short_name_uz =
    university.short_name_uz
  form.address_ru =
    university.address_ru
  form.address_uz =
    university.address_uz
  form.phone = university.phone
  form.email = university.email
  form.website = university.website
  form.is_active =
    university.is_active
  form.sort_order =
    university.sort_order
}

watch(
  () => props.modelValue,
  (visible) => {
    if (visible) {
      fillForm(props.university)
    }
  },
)

watch(
  () => props.university,
  (university) => {
    if (props.modelValue) {
      fillForm(university)
    }
  },
)

const title = computed(
  () =>
    props.university
      ? 'Редактирование ВУЗа'
      : 'Добавление ВУЗа',
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
      code: form.code.trim(),
      name_ru: form.name_ru.trim(),
      name_uz: form.name_uz.trim(),
      short_name_ru:
        form.short_name_ru.trim(),
      short_name_uz:
        form.short_name_uz.trim(),
      address_ru:
        form.address_ru.trim(),
      address_uz:
        form.address_uz.trim(),
      phone: form.phone.trim(),
      email: form.email.trim(),
      website: form.website.trim(),
      is_active: form.is_active,
      sort_order:
        form.sort_order ?? 0,
    },
  )
}
</script>

<template>
  <Dialog
    :visible="modelValue"
    :header="title"
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

      <div class="field">
        <label for="university-code">
          Код
        </label>

        <InputText
          id="university-code"
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
        <label for="university-sort">
          Порядок сортировки
        </label>

        <InputNumber
          id="university-sort"
          v-model="form.sort_order"
          :min="0"
          :use-grouping="false"
        />
      </div>

      <div class="field field--wide">
        <label for="university-name-ru">
          Название на русском
        </label>

        <InputText
          id="university-name-ru"
          v-model="form.name_ru"
          maxlength="255"
          :invalid="
            Boolean(
              errorFor('name_ru'),
            )
          "
        />

        <small
          v-if="errorFor('name_ru')"
          class="error-text"
        >
          {{ errorFor('name_ru') }}
        </small>
      </div>

      <div class="field field--wide">
        <label for="university-name-uz">
          Название на узбекском
        </label>

        <InputText
          id="university-name-uz"
          v-model="form.name_uz"
          maxlength="255"
          :invalid="
            Boolean(
              errorFor('name_uz'),
            )
          "
        />

        <small
          v-if="errorFor('name_uz')"
          class="error-text"
        >
          {{ errorFor('name_uz') }}
        </small>
      </div>

      <div class="field">
        <label for="university-short-ru">
          Краткое название RU
        </label>

        <InputText
          id="university-short-ru"
          v-model="
            form.short_name_ru
          "
          maxlength="100"
        />
      </div>

      <div class="field">
        <label for="university-short-uz">
          Краткое название UZ
        </label>

        <InputText
          id="university-short-uz"
          v-model="
            form.short_name_uz
          "
          maxlength="100"
        />
      </div>

      <div class="field field--wide">
        <label for="university-address-ru">
          Адрес на русском
        </label>

        <InputText
          id="university-address-ru"
          v-model="
            form.address_ru
          "
          maxlength="500"
        />
      </div>

      <div class="field field--wide">
        <label for="university-address-uz">
          Адрес на узбекском
        </label>

        <InputText
          id="university-address-uz"
          v-model="
            form.address_uz
          "
          maxlength="500"
        />
      </div>

      <div class="field">
        <label for="university-phone">
          Телефон
        </label>

        <InputText
          id="university-phone"
          v-model="form.phone"
          maxlength="30"
        />
      </div>

      <div class="field">
        <label for="university-email">
          Электронная почта
        </label>

        <InputText
          id="university-email"
          v-model="form.email"
          maxlength="254"
          :invalid="
            Boolean(
              errorFor('email'),
            )
          "
        />

        <small
          v-if="errorFor('email')"
          class="error-text"
        >
          {{ errorFor('email') }}
        </small>
      </div>

      <div class="field field--wide">
        <label for="university-website">
          Веб-сайт
        </label>

        <InputText
          id="university-website"
          v-model="form.website"
          maxlength="200"
          :invalid="
            Boolean(
              errorFor('website'),
            )
          "
        />

        <small
          v-if="errorFor('website')"
          class="error-text"
        >
          {{ errorFor('website') }}
        </small>
      </div>

      <div class="field field--wide">
        <div class="checkbox-field">
          <Checkbox
            v-model="form.is_active"
            binary
            input-id="university-active"
          />

          <label
            for="university-active"
          >
            ВУЗ активен
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
          university
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
.field :deep(.p-inputnumber),
.field :deep(.p-inputnumber-input) {
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
