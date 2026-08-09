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

import type {
  EducationLevel,
  EducationLevelCode,
  StudyForm,
  StudyFormCode,
} from '@/modules/academic-settings/types'

type Kind =
  | 'education-level'
  | 'study-form'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props = withDefaults(
  defineProps<{
    kind: Kind

    record?:
      | EducationLevel
      | StudyForm
      | null

    loading?: boolean
  }>(),
  {
    record: null,
    loading: false,
  },
)

const emit = defineEmits<{
  submit: [
    payload: {
      code: string

      name_ru: string
      name_uz: string

      is_active: boolean
      sort_order: number
    },
  ]
}>()

const { t } = useI18n()

const form = reactive({
  code: '',

  name_ru: '',
  name_uz: '',

  is_active: true,
  sort_order: 0,
})

const errors =
  reactive<Record<string, string>>({})

const title = computed(
  () => {
    if (
      props.kind ===
      'education-level'
    ) {
      return props.record
        ? t(
            'academicSettings.educationLevels.editTitle',
          )
        : t(
            'academicSettings.educationLevels.createTitle',
          )
    }

    return props.record
      ? t(
          'academicSettings.studyForms.editTitle',
        )
      : t(
          'academicSettings.studyForms.createTitle',
        )
  },
)

const codeOptions = computed(
  () => {
    if (
      props.kind ===
      'education-level'
    ) {
      return [
        {
          value:
            'bachelor' satisfies EducationLevelCode,

          label:
            t(
              'academicSettings.educationLevels.codes.bachelor',
            ),
        },

        {
          value:
            'master' satisfies EducationLevelCode,

          label:
            t(
              'academicSettings.educationLevels.codes.master',
            ),
        },
      ]
    }

    return [
      {
        value:
          'full_time' satisfies StudyFormCode,

        label:
          t(
            'academicSettings.studyForms.codes.fullTime',
          ),
      },

      {
        value:
          'part_time' satisfies StudyFormCode,

        label:
          t(
            'academicSettings.studyForms.codes.partTime',
          ),
      },

      {
        value:
          'evening' satisfies StudyFormCode,

        label:
          t(
            'academicSettings.studyForms.codes.evening',
          ),
      },

      {
        value:
          'distance' satisfies StudyFormCode,

        label:
          t(
            'academicSettings.studyForms.codes.distance',
          ),
      },
    ]
  },
)

function reset(): void {
  form.code = ''
  form.name_ru = ''
  form.name_uz = ''

  form.is_active = true
  form.sort_order = 0

  Object.keys(errors).forEach(
    (key) => {
      delete errors[key]
    },
  )
}

function fill(): void {
  if (!props.record) {
    reset()
    return
  }

  form.code =
    props.record.code

  form.name_ru =
    props.record.name_ru

  form.name_uz =
    props.record.name_uz

  form.is_active =
    props.record.is_active

  form.sort_order =
    props.record.sort_order
}

function submit(): void {
  Object.keys(errors).forEach(
    (key) => {
      delete errors[key]
    },
  )

  if (!form.code) {
    errors.code =
      t('common.required')
  }

  if (!form.name_ru.trim()) {
    errors.name_ru =
      t('common.required')
  }

  if (!form.name_uz.trim()) {
    errors.name_uz =
      t('common.required')
  }

  if (
    Object.keys(errors).length
  ) {
    return
  }

  emit('submit', {
    code:
      form.code,

    name_ru:
      form.name_ru.trim(),

    name_uz:
      form.name_uz.trim(),

    is_active:
      form.is_active,

    sort_order:
      form.sort_order,
  })
}

watch(
  visible,
  (value) => {
    if (value) {
      fill()
    }
  },
)
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="title"
    width="44rem"
    :loading="loading"
  >
    <div class="reference-form">
      <BaseFormField
        :label="
          t(
            'academicSettings.common.code',
          )
        "
        name="code"
        required
        :error="errors.code"
      >
        <Select
          v-model="form.code"
          :options="codeOptions"
          option-label="label"
          option-value="value"
          class="w-full"
          :disabled="
            Boolean(record)
          "
        />
      </BaseFormField>

      <BaseFormField
        :label="
          t(
            'academicSettings.common.nameRu',
          )
        "
        name="name_ru"
        required
        :error="
          errors.name_ru
        "
      >
        <InputText
          v-model="
            form.name_ru
          "
          class="w-full"
        />
      </BaseFormField>

      <BaseFormField
        :label="
          t(
            'academicSettings.common.nameUz',
          )
        "
        name="name_uz"
        required
        :error="
          errors.name_uz
        "
      >
        <InputText
          v-model="
            form.name_uz
          "
          class="w-full"
        />
      </BaseFormField>

      <BaseFormField
        :label="
          t(
            'academicSettings.common.sortOrder',
          )
        "
        name="sort_order"
      >
        <InputNumber
          v-model="
            form.sort_order
          "
          :min="0"
          :use-grouping="false"
          class="w-full"
          input-class="w-full"
        />
      </BaseFormField>

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
              'academicSettings.common.active',
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
.reference-form {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.reference-form label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  font-weight: 600;
}

@media (max-width: 575px) {
  .reference-form {
    grid-template-columns: 1fr;
  }
}
</style>
