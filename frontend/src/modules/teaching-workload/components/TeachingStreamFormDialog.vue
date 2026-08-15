<script setup lang="ts">
import Checkbox from 'primevue/checkbox'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'

import {
  computed,
  reactive,
  watch,
} from 'vue'

import {
  useI18n,
} from 'vue-i18n'

import BaseDialog from '@/components/base/BaseDialog.vue'
import BaseFormActions from '@/components/base/BaseFormActions.vue'
import BaseFormField from '@/components/base/BaseFormField.vue'

import FormValidationSummary from '@/components/forms/FormValidationSummary.vue'

import type {
  CurriculumLookup,
} from '@/modules/teaching-setup/types'

import type {
  AcademicSemesterLookup,
  AcademicYearLookup,
} from '@/modules/teaching-setup/types'

import type {
  TeachingStream,
  TeachingStreamPayload,
  TeachingStreamStatus,
} from '@/modules/teaching-workload/types'

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
    record?: TeachingStream | null

    academicYears: AcademicYearLookup[]
    academicSemesters: AcademicSemesterLookup[]
    curricula: CurriculumLookup[]

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
    payload: TeachingStreamPayload,
  ]
}>()

const { t } = useI18n()

const form = reactive({
  academic_year:
    null as number | null,

  academic_semester:
    null as number | null,

  curriculum:
    null as number | null,

  semester_number:
    null as number | null,

  code: '',
  name: '',

  status:
    'draft' as TeachingStreamStatus,

  is_active: true,

  notes: '',
})

const localErrors =
  reactive<Record<string, string>>({})

const selectedCurriculum =
  computed(
    () =>
      props.curricula.find(
        (item) =>
          item.id ===
          form.curriculum,
      ) ?? null,
  )

const yearOptions =
  computed(() =>
    props.academicYears
      .filter(
        (year) =>
          !year.is_archived,
      )
      .map(
        (year) => ({
          value: year.id,
          label: year.name,
        }),
      ),
  )

const curriculumOptions =
  computed(() =>
    props.curricula
      .filter(
        (item) =>
          item.is_active &&
          !item.is_archived,
      )
      .map(
        (item) => ({
          value: item.id,

          label:
            `${item.code} · v${item.version}`,

          description:
            `${item.study_program_name} · ${item.study_form_name}`,
        }),
      ),
  )

const semesterNumberOptions =
  computed(() => {
    const count =
      selectedCurriculum.value
        ?.semesters_count ?? 0

    return Array.from(
      {
        length: count,
      },

      (_, index) => {
        const semester =
          index + 1

        return {
          value:
            semester,

          label:
            semester % 2 === 1
              ? `${semester} — ${t(
                  'teachingWorkload.seasons.autumn',
                )}`
              : `${semester} — ${t(
                  'teachingWorkload.seasons.spring',
                )}`,
        }
      },
    )
  })

const academicSemesterOptions =
  computed(() => {
    if (
      !form.academic_year ||
      !form.semester_number
    ) {
      return []
    }

    const season =
      form.semester_number % 2 === 1
        ? 'autumn'
        : 'spring'

    return props.academicSemesters
      .filter(
        (item) =>
          item.academic_year ===
            form.academic_year &&
          item.season === season &&
          item.is_active &&
          !item.is_archived,
      )
      .map(
        (item) => ({
          value: item.id,

          label:
            item.season_name,

          description:
            `${item.start_date} — ${item.end_date}`,
        }),
      )
  })

const statusOptions =
  computed(() => [
    {
      value: 'draft',
      label:
        t(
          'teachingWorkload.streams.statuses.draft',
        ),
    },
    {
      value: 'calculated',
      label:
        t(
          'teachingWorkload.streams.statuses.calculated',
        ),
    },
    {
      value: 'approved',
      label:
        t(
          'teachingWorkload.streams.statuses.approved',
        ),
    },
    {
      value: 'cancelled',
      label:
        t(
          'teachingWorkload.streams.statuses.cancelled',
        ),
    },
  ])

function clearErrors(): void {
  for (
    const key of
    Object.keys(localErrors)
  ) {
    delete localErrors[key]
  }
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

function resetForm(): void {
  form.academic_year =
    props.academicYears.find(
      (year) =>
        year.is_current,
    )?.id ?? null

  form.academic_semester =
    null

  form.curriculum =
    null

  form.semester_number =
    null

  form.code = ''
  form.name = ''

  form.status = 'draft'

  form.is_active = true

  form.notes = ''

  clearErrors()
}

function fillForm(
  record: TeachingStream,
): void {
  form.academic_year =
    record.academic_year

  form.academic_semester =
    record.academic_semester

  form.curriculum =
    record.curriculum

  form.semester_number =
    record.semester_number

  form.code =
    record.code

  form.name =
    record.name

  form.status =
    record.status

  form.is_active =
    record.is_active

  form.notes =
    record.notes

  clearErrors()
}

function validate(): boolean {
  clearErrors()

  if (!form.academic_year) {
    localErrors.academic_year =
      t(
        'teachingWorkload.streams.validation.yearRequired',
      )
  }

  if (!form.curriculum) {
    localErrors.curriculum =
      t(
        'teachingWorkload.streams.validation.curriculumRequired',
      )
  }

  if (!form.semester_number) {
    localErrors.semester_number =
      t(
        'teachingWorkload.streams.validation.semesterNumberRequired',
      )
  }

  if (!form.academic_semester) {
    localErrors.academic_semester =
      t(
        'teachingWorkload.streams.validation.semesterRequired',
      )
  }

  if (!form.code.trim()) {
    localErrors.code =
      t(
        'teachingWorkload.streams.validation.codeRequired',
      )
  }

  if (!form.name.trim()) {
    localErrors.name =
      t(
        'teachingWorkload.streams.validation.nameRequired',
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
    !form.academic_year ||
    !form.academic_semester ||
    !form.curriculum ||
    !form.semester_number
  ) {
    return
  }

  emit('submit', {
    academic_year:
      form.academic_year,

    academic_semester:
      form.academic_semester,

    curriculum:
      form.curriculum,

    semester_number:
      form.semester_number,

    code:
      form.code
        .trim()
        .toUpperCase(),

    name:
      form.name.trim(),

    status:
      form.status,

    is_active:
      form.is_active,

    notes:
      form.notes.trim(),
  })
}

watch(
  [
    () => form.academic_year,
    () => form.semester_number,
  ],
  () => {
    if (
      !academicSemesterOptions.value
        .some(
          (option) =>
            option.value ===
            form.academic_semester,
        )
    ) {
      form.academic_semester =
        null
    }
  },
)

watch(
  () => form.curriculum,
  () => {
    if (
      !semesterNumberOptions.value
        .some(
          (option) =>
            option.value ===
            form.semester_number,
        )
    ) {
      form.semester_number =
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

    if (props.record) {
      fillForm(
        props.record,
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
    :title="
      record
        ? t(
            'teachingWorkload.streams.editTitle',
          )
        : t(
            'teachingWorkload.streams.createTitle',
          )
    "
    width="60rem"
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

    <form
      class="
        teaching-stream-form
      "
      novalidate
      @submit.prevent="submit"
    >
      <div
        class="
          teaching-stream-form__grid
        "
      >
        <BaseFormField
          :label="
            t(
              'teachingWorkload.streams.fields.academicYear',
            )
          "
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
              yearOptions
            "
            option-label="label"
            option-value="value"
            class="w-full"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'teachingWorkload.streams.fields.curriculum',
            )
          "
          required
          :error="
            fieldError(
              'curriculum',
            )
          "
        >
          <Select
            v-model="form.curriculum"
            :options="curriculumOptions"
            option-label="label"
            option-value="value"
            filter
            class="w-full"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'teachingWorkload.streams.fields.semesterNumber',
            )
          "
          required
          :error="
            fieldError(
              'semester_number',
            )
          "
        >
          <Select
            v-model="
              form.semester_number
            "
            :options="
              semesterNumberOptions
            "
            option-label="label"
            option-value="value"
            class="w-full"
            :disabled="
              !form.curriculum
            "
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'teachingWorkload.streams.fields.academicSemester',
            )
          "
          required
          :error="
            fieldError(
              'academic_semester',
            )
          "
        >
          <Select
            v-model="
              form.academic_semester
            "
            :options="
              academicSemesterOptions
            "
            option-label="label"
            option-value="value"
            class="w-full"
            :disabled="
              !form.semester_number
            "
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'teachingWorkload.streams.fields.code',
            )
          "
          required
          :error="
            fieldError('code')
          "
        >
          <InputText
            v-model="form.code"
            class="w-full"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'teachingWorkload.streams.fields.name',
            )
          "
          required
          :error="
            fieldError('name')
          "
        >
          <InputText
            v-model="form.name"
            class="w-full"
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'teachingWorkload.streams.fields.status',
            )
          "
        >
          <Select
            v-model="form.status"
            :options="
              statusOptions
            "
            option-label="label"
            option-value="value"
            class="w-full"
          />
        </BaseFormField>
      </div>

      <BaseFormField
        :label="
          t(
            'teachingWorkload.common.notes',
          )
        "
      >
        <Textarea
          v-model="form.notes"
          rows="4"
          class="w-full"
        />
      </BaseFormField>

      <label
        class="
          teaching-stream-form__active
        "
      >
        <Checkbox
          v-model="
            form.is_active
          "
          binary
        />

        <span>
          {{
            t(
              'teachingWorkload.common.active',
            )
          }}
        </span>
      </label>
    </form>

    <template #footer>
      <BaseFormActions
        :loading="loading"
        :save-label="
          t('common.save')
        "
        :cancel-label="
          t('common.cancel')
        "
        @submit="submit"
        @cancel="
          visible = false
        "
      />
    </template>
  </BaseDialog>
</template>

<style scoped>
.teaching-stream-form {
  display: grid;
  gap: 1rem;
}

.teaching-stream-form__grid {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.teaching-stream-form__active {
  display: flex;
  align-items: center;
  gap: 0.5rem;

  width: fit-content;
}

@media (max-width: 767px) {
  .teaching-stream-form__grid {
    grid-template-columns: 1fr;
  }
}
</style>
