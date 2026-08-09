<script setup lang="ts">
import Checkbox from 'primevue/checkbox'
import InputNumber from 'primevue/inputnumber'
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

import {
  useLocaleStore,
} from '@/stores/locale'

import type {
  EducationDuration,
  EducationDurationPayload,
  EducationLevel,
  StudyForm,
} from '@/modules/academic-settings/types'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props = withDefaults(
  defineProps<{
    record?: EducationDuration | null

    educationLevels: EducationLevel[]
    studyForms: StudyForm[]

    loading?: boolean
  }>(),
  {
    record: null,
    loading: false,
  },
)

const emit = defineEmits<{
  submit: [
    payload: EducationDurationPayload,
  ]
}>()

const { t } = useI18n()

const localeStore =
  useLocaleStore()

const form = reactive({
  education_level:
    null as number | null,

  study_form:
    null as number | null,

  semesters_count:
    2 as number | null,

  duration_months:
    12 as number | null,

  is_active: true,
})

const error =
  reactive<Record<string, string>>({})

function localizedName(
  item:
    | EducationLevel
    | StudyForm,
): string {
  if (
    localeStore.locale === 'uz'
  ) {
    return (
      item.name_uz ||
      item.name_ru
    )
  }

  return (
    item.name_ru ||
    item.name_uz
  )
}

const levelOptions =
  computed(() =>
    props.educationLevels
      .filter(
        (item) =>
          item.is_active &&
          !item.is_archived,
      )
      .map((item) => ({
        value: item.id,
        label:
          localizedName(item),
      })),
  )

const formOptions =
  computed(() =>
    props.studyForms
      .filter(
        (item) =>
          item.is_active &&
          !item.is_archived,
      )
      .map((item) => ({
        value: item.id,
        label:
          localizedName(item),
      })),
  )

function fill(): void {
  if (!props.record) {
    form.education_level = null
    form.study_form = null

    form.semesters_count = 2
    form.duration_months = 12

    form.is_active = true
    return
  }

  form.education_level =
    props.record.education_level

  form.study_form =
    props.record.study_form

  form.semesters_count =
    props.record.semesters_count

  form.duration_months =
    props.record.duration_months

  form.is_active =
    props.record.is_active
}

function submit(): void {
  Object.keys(error).forEach(
    (key) => {
      delete error[key]
    },
  )

  if (!form.education_level) {
    error.education_level =
      t('common.required')
  }

  if (!form.study_form) {
    error.study_form =
      t('common.required')
  }

  if (
    !form.semesters_count ||
    form.semesters_count < 1 ||
    form.semesters_count > 20
  ) {
    error.semesters_count =
      t(
        'academicSettings.educationDurations.validation.semesters',
      )
  }

  if (
    form.duration_months !==
    (form.semesters_count ?? 0) *
      6
  ) {
    error.duration_months =
      t(
        'academicSettings.educationDurations.validation.months',
      )
  }

  if (
    Object.keys(error).length
  ) {
    return
  }

  emit('submit', {
    education_level:
      form.education_level!,

    study_form:
      form.study_form!,

    semesters_count:
      form.semesters_count!,

    duration_months:
      form.duration_months!,

    is_active:
      form.is_active,
  })
}

watch(
  () => form.semesters_count,
  (value) => {
    if (value) {
      form.duration_months =
        value * 6
    }
  },
)

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
    :title="
      record
        ? t(
            'academicSettings.educationDurations.editTitle',
          )
        : t(
            'academicSettings.educationDurations.createTitle',
          )
    "
    width="44rem"
    :loading="loading"
  >
    <div
      class="duration-form"
    >
      <BaseFormField
        :label="
          t(
            'academicSettings.educationDurations.fields.level',
          )
        "
        name="education_level"
        required
        :error="
          error.education_level
        "
      >
        <Select
          v-model="
            form.education_level
          "
          :options="
            levelOptions
          "
          option-label="label"
          option-value="value"
          class="w-full"
        />
      </BaseFormField>

      <BaseFormField
        :label="
          t(
            'academicSettings.educationDurations.fields.studyForm',
          )
        "
        name="study_form"
        required
        :error="
          error.study_form
        "
      >
        <Select
          v-model="
            form.study_form
          "
          :options="
            formOptions
          "
          option-label="label"
          option-value="value"
          class="w-full"
        />
      </BaseFormField>

      <BaseFormField
        :label="
          t(
            'academicSettings.educationDurations.fields.semesters',
          )
        "
        name="semesters_count"
        required
        :error="
          error.semesters_count
        "
      >
        <InputNumber
          v-model="
            form.semesters_count
          "
          :min="1"
          :max="20"
          :use-grouping="false"
          class="w-full"
          input-class="w-full"
        />
      </BaseFormField>

      <BaseFormField
        :label="
          t(
            'academicSettings.educationDurations.fields.months',
          )
        "
        name="duration_months"
        required
        :error="
          error.duration_months
        "
      >
        <InputNumber
          v-model="
            form.duration_months
          "
          :min="1"
          :max="120"
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

        {{
          t(
            'academicSettings.common.active',
          )
        }}
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
.duration-form {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.duration-form label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  font-weight: 600;
}

@media (max-width: 575px) {
  .duration-form {
    grid-template-columns: 1fr;
  }
}
</style>
