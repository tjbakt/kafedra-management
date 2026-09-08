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
  FieldErrors,
} from '@/types/validation'

import type {
  StaffPosition,
  StaffPositionCategory,
  StaffPositionPayload,
} from '@/modules/staff-references/types'

import {
  getFieldError,
} from '@/utils/api-errors'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props =
  withDefaults(
    defineProps<{
      record?: StaffPosition | null
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

const emit =
  defineEmits<{
    submit: [
      payload: StaffPositionPayload,
    ]
  }>()

const { t } = useI18n()

const form = reactive({
  code: '',
  name_ru: '',
  name_uz: '',
  category:
    'teaching' as StaffPositionCategory,
  is_teaching_position: true,
  is_active: true,
  sort_order: 0,
})

const localErrors =
  reactive<Record<string, string>>({})

const title =
  computed(() =>
    props.record
      ? t(
          'staffReferences.positions.editTitle',
        )
      : t(
          'staffReferences.positions.createTitle',
        ),
  )

const categoryOptions =
  computed(() => [
    {
      value: 'teaching',
      label: t(
        'staffReferences.positions.categories.teaching',
      ),
    },
    {
      value: 'administrative',
      label: t(
        'staffReferences.positions.categories.administrative',
      ),
    },
    {
      value: 'support',
      label: t(
        'staffReferences.positions.categories.support',
      ),
    },
    {
      value: 'other',
      label: t(
        'staffReferences.positions.categories.other',
      ),
    },
  ])

function clearErrors(): void {
  Object.keys(localErrors)
    .forEach(
      (key) => {
        delete localErrors[key]
      },
    )
}

function resetForm(): void {
  form.code = ''
  form.name_ru = ''
  form.name_uz = ''
  form.category = 'teaching'
  form.is_teaching_position = true
  form.is_active = true
  form.sort_order = 0

  clearErrors()
}

function fillForm(
  record: StaffPosition,
): void {
  form.code = record.code
  form.name_ru = record.name_ru
  form.name_uz = record.name_uz
  form.category = record.category
  form.is_teaching_position =
    record.is_teaching_position
  form.is_active = record.is_active
  form.sort_order = record.sort_order

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

  if (!form.code.trim()) {
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
      form.code.trim().toUpperCase(),
    name_ru:
      form.name_ru.trim(),
    name_uz:
      form.name_uz.trim(),
    category:
      form.category,
    is_teaching_position:
      form.is_teaching_position,
    is_active:
      form.is_active,
    sort_order:
      form.sort_order,
  })
}

watch(
  () => visible.value,
  (value) => {
    if (!value) {
      return
    }

    if (props.record) {
      fillForm(props.record)
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
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="title"
    width="52rem"
    :loading="loading"
  >
    <FormValidationSummary
      :field-errors="fieldErrors"
      :non-field-errors="nonFieldErrors"
      :general-error="generalError"
    />

    <form
      class="reference-form"
      novalidate
      @submit.prevent="submit"
    >
      <div class="reference-form__grid">
        <BaseFormField
          :label="
            t(
              'staffReferences.common.code',
            )
          "
          name="code"
          required
          :error="fieldError('code')"
        >
          <InputText
            v-model="form.code"
            maxlength="50"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'staffReferences.positions.category',
            )
          "
          name="category"
          required
          :error="fieldError('category')"
        >
          <Select
            v-model="form.category"
            :options="categoryOptions"
            option-label="label"
            option-value="value"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'staffReferences.common.nameRu',
            )
          "
          name="name_ru"
          required
          :error="fieldError('name_ru')"
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
              'staffReferences.common.nameUz',
            )
          "
          name="name_uz"
          required
          :error="fieldError('name_uz')"
        >
          <InputText
            v-model="form.name_uz"
            maxlength="255"
            class="w-full"
            :disabled="loading"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'staffReferences.common.sortOrder',
            )
          "
          name="sort_order"
          :error="fieldError('sort_order')"
        >
          <InputNumber
            v-model="form.sort_order"
            :min="0"
            :use-grouping="false"
            class="w-full"
            input-class="w-full"
            :disabled="loading"
          />
        </BaseFormField>
      </div>

      <div class="reference-form__flags">
        <label>
          <Checkbox
            v-model="
              form.is_teaching_position
            "
            binary
            :disabled="loading"
          />
          <span>
            {{
              t(
                'staffReferences.positions.teachingPosition',
              )
            }}
          </span>
        </label>

        <label>
          <Checkbox
            v-model="form.is_active"
            binary
            :disabled="loading"
          />
          <span>
            {{
              t(
                'staffReferences.common.active',
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
.reference-form {
  display: grid;
  gap: 1.25rem;
}

.reference-form__grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.reference-form__flags {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.reference-form__flags label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
}

@media (max-width: 767px) {
  .reference-form__grid {
    grid-template-columns: 1fr;
  }
}
</style>
