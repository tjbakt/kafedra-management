<script setup lang="ts">
import Checkbox from 'primevue/checkbox'
import InputText from 'primevue/inputtext'
import MultiSelect from 'primevue/multiselect'
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
  AcademicYearLookup,
  CurriculumLookup,
  GroupSemester,
} from '@/modules/teaching-setup/types'

import type {
  TeachingStream,
  TeachingStreamBulkPayload,
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

    academicYears:
      AcademicYearLookup[]

    curricula:
      CurriculumLookup[]

    groupSemesters:
      GroupSemester[]

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
    payload:
      TeachingStreamBulkPayload,
  ]
}>()

const { t } =
  useI18n()

const form =
  reactive({
    academic_year: null as number | null,

    curriculum: null as number | null,

    semester_numbers: [] as number[],

    code: '',

    name: '',

    status: 'draft' as TeachingStreamStatus,

    is_active: true,

    notes: '',
  })

const localErrors =
  reactive<
    Record<string, string>
  >({})

const yearOptions =
  computed(
    () =>
      props.academicYears
        .filter(
          (year) =>
            !year.is_archived,
        )
        .map(
          (year) => ({
            value:
              year.id,

            label:
              year.name,
          }),
        ),
  )

const curriculumOptions =
  computed(
    () =>
      props.curricula
        .filter(
          (item) =>
            item.is_active &&
            !item.is_archived,
        )
        .map(
          (item) => ({
            value:
              item.id,

            label:
              `${item.code} · v${item.version}`,

            description:
              `${item.study_program_name} · ${item.study_form_name}`,
          }),
        ),
  )

const semesterNumberOptions =
  computed(
    () => {
      if (
        !form.academic_year ||
        !form.curriculum
      ) {
        return []
      }

      const numbers =
        new Set<number>()

      for (
        const item
        of props.groupSemesters
      ) {
        if (
          item.academic_year ===
            form.academic_year &&
          item.curriculum ===
            form.curriculum &&
          item.is_active &&
          !item.is_archived
        ) {
          numbers.add(
            item.semester_number,
          )
        }
      }

      return Array.from(
        numbers,
      )
        .sort(
          (a, b) =>
            a - b,
        )
        .map(
          (value) => ({
            value,

            label:
              `${value} — ${
                value % 2 === 1
                  ? t(
                      'teachingSetup.seasons.autumn',
                    )
                  : t(
                      'teachingSetup.seasons.spring',
                    )
              }`,
          }),
        )
    },
  )

const statusOptions =
  computed(
    () => [
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
    ],
  )

function clearErrors(): void {
  for (
    const key
    of Object.keys(
      localErrors,
    )
  ) {
    delete localErrors[
      key
    ]
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

  form.curriculum =
    null

  form.semester_numbers =
    []

  form.code =
    ''

  form.name =
    ''

  form.status =
    'draft'

  form.is_active =
    true

  form.notes =
    ''

  clearErrors()
}

function fillForm(
  record:
    TeachingStream,
): void {
  form.academic_year =
    record.academic_year

  form.curriculum =
    record.curriculum

  form.semester_numbers =
    [
      record.semester_number,
    ]

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

  if (
    form.semester_numbers.length ===
    0
  ) {
    localErrors.semester_numbers =
      t(
        'teachingWorkload.streams.validation.semesterNumberRequired',
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
    Object.keys(
      localErrors,
    ).length === 0
  )
}

function submit(): void {
  if (!validate()) {
    return
  }

  if (
    !form.academic_year ||
    !form.curriculum ||
    form.semester_numbers.length ===
      0
  ) {
    return
  }

  emit(
    'submit',
    {
      academic_year:
        form.academic_year,

      curriculum:
        form.curriculum,

      semester_numbers:
        [...form.semester_numbers],

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
    },
  )
}

watch(
  [
    () =>
      form.academic_year,

    () =>
      form.curriculum,
  ],
  () => {
    if (props.record) {
      return
    }

    const allowed =
      new Set(
        semesterNumberOptions
          .value
          .map(
            (option) =>
              option.value,
          ),
      )

    form.semester_numbers =
      form.semester_numbers.filter(
        (semesterNumber) =>
          allowed.has(
            semesterNumber,
          ),
      )
  },
)

watch(
  () =>
    visible.value,
  (
    isVisible,
  ) => {
    if (!isVisible) {
      return
    }

    if (props.record) {
      fillForm(
        props.record,
      )

      return
    }

    resetForm()
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
      class="
        teaching-stream-form
      "
      novalidate
      @submit.prevent="
        submit
      "
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
            v-model="
              form.curriculum
            "
            :options="
              curriculumOptions
            "
            option-label="label"
            option-value="value"
            filter
            class="w-full"
          />
        </BaseFormField>

        <BaseFormField
          class="
            teaching-stream-form__wide
          "
          :label="
            t(
              'teachingWorkload.streams.fields.semesterNumber',
            )
          "
          required
          :error="
            fieldError(
              'semester_numbers',
            )
          "
        >
          <MultiSelect
            v-model="
              form.semester_numbers
            "
            :options="
              semesterNumberOptions
            "
            option-label="label"
            option-value="value"
            display="chip"
            class="w-full"
            :disabled="
              !form.academic_year ||
              !form.curriculum
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
            fieldError(
              'code',
            )
          "
        >
          <InputText
            v-model="
              form.code
            "
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
            fieldError(
              'name',
            )
          "
        >
          <InputText
            v-model="
              form.name
            "
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
            v-model="
              form.status
            "
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
          v-model="
            form.notes
          "
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
        :loading="
          loading
        "
        :save-label="
          t(
            'common.save',
          )
        "
        :cancel-label="
          t(
            'common.cancel',
          )
        "
        @submit="
          submit
        "
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

.teaching-stream-form__wide {
  grid-column:
    1 / -1;
}

.teaching-stream-form__active {
  display: flex;

  align-items: center;

  gap: 0.5rem;

  width: fit-content;
}

@media (
  max-width: 767px
) {
  .teaching-stream-form__grid {
    grid-template-columns:
      1fr;
  }

  .teaching-stream-form__wide {
    grid-column: auto;
  }
}
</style>
