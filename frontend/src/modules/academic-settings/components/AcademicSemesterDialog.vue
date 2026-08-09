<script setup lang="ts">
import Checkbox from 'primevue/checkbox'
import DatePicker from 'primevue/datepicker'
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
  AcademicSemester,
  AcademicSemesterPayload,
  AcademicYear,
  SemesterSeason,
} from '@/modules/academic-settings/types'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props = withDefaults(
  defineProps<{
    record?: AcademicSemester | null

    academicYears: AcademicYear[]

    loading?: boolean
  }>(),
  {
    record: null,
    loading: false,
  },
)

const emit = defineEmits<{
  submit: [
    payload: AcademicSemesterPayload,
  ]
}>()

const { t } = useI18n()

const form = reactive({
  academic_year:
    null as number | null,

  season:
    'autumn' as SemesterSeason,

  start_date:
    null as Date | null,

  end_date:
    null as Date | null,

  is_current: false,
  is_active: true,
})

const errors =
  reactive<Record<string, string>>({})

const yearOptions =
  computed(() =>
    props.academicYears
      .filter(
        (year) =>
          !year.is_archived,
      )
      .map((year) => ({
        value: year.id,
        label: year.name,
      })),
  )

const seasonOptions =
  computed(() => [
    {
      value:
        'autumn' as SemesterSeason,

      label:
        t(
          'academicSettings.semesters.seasons.autumn',
        ),
    },

    {
      value:
        'spring' as SemesterSeason,

      label:
        t(
          'academicSettings.semesters.seasons.spring',
        ),
    },
  ])

function parseDate(
  value: string,
): Date {
  const [year, month, day] =
    value.split('-').map(Number)

  return new Date(
    year!,
    month! - 1,
    day!,
  )
}

function serializeDate(
  value: Date,
): string {
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

function fill(): void {
  if (!props.record) {
    form.academic_year = null
    form.season = 'autumn'

    form.start_date = null
    form.end_date = null

    form.is_current = false
    form.is_active = true

    return
  }

  form.academic_year =
    props.record.academic_year

  form.season =
    props.record.season

  form.start_date =
    parseDate(
      props.record.start_date,
    )

  form.end_date =
    parseDate(
      props.record.end_date,
    )

  form.is_current =
    props.record.is_current

  form.is_active =
    props.record.is_active
}

function submit(): void {
  Object.keys(errors).forEach(
    (key) => {
      delete errors[key]
    },
  )

  if (!form.academic_year) {
    errors.academic_year =
      t('common.required')
  }

  if (!form.start_date) {
    errors.start_date =
      t('common.required')
  }

  if (!form.end_date) {
    errors.end_date =
      t('common.required')
  }

  if (
    form.start_date &&
    form.end_date &&
    form.end_date <=
      form.start_date
  ) {
    errors.end_date =
      t(
        'academicSettings.semesters.validation.endDate',
      )
  }

  const selectedYear =
    props.academicYears.find(
      (year) =>
        year.id ===
        form.academic_year,
    )

  if (
    selectedYear &&
    form.start_date
  ) {
    const expectedYear =
      form.season === 'autumn'
        ? selectedYear.start_year
        : selectedYear.end_year

    if (
      form.start_date.getFullYear() !==
      expectedYear
    ) {
      errors.start_date =
        form.season === 'autumn'
          ? t(
              'academicSettings.semesters.validation.autumnYear',
            )
          : t(
              'academicSettings.semesters.validation.springYear',
            )
    }
  }

  if (
    Object.keys(errors).length
  ) {
    return
  }

  emit('submit', {
    academic_year:
      form.academic_year!,

    season:
      form.season,

    start_date:
      serializeDate(
        form.start_date!,
      ),

    end_date:
      serializeDate(
        form.end_date!,
      ),

    is_current:
      form.is_current,

    is_active:
      form.is_active,
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
    :title="
      record
        ? t(
            'academicSettings.semesters.editTitle',
          )
        : t(
            'academicSettings.semesters.createTitle',
          )
    "
    width="46rem"
    :loading="loading"
  >
    <div class="semester-form">
      <BaseFormField
        :label="
          t(
            'academicSettings.semesters.fields.academicYear',
          )
        "
        name="academic_year"
        required
        :error="
          errors.academic_year
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
            'academicSettings.semesters.fields.season',
          )
        "
        name="season"
        required
      >
        <Select
          v-model="
            form.season
          "
          :options="
            seasonOptions
          "
          option-label="label"
          option-value="value"
          class="w-full"
        />
      </BaseFormField>

      <BaseFormField
        :label="
          t(
            'academicSettings.semesters.fields.startDate',
          )
        "
        name="start_date"
        required
        :error="
          errors.start_date
        "
      >
        <DatePicker
          v-model="
            form.start_date
          "
          date-format="dd.mm.yy"
          show-icon
          class="w-full"
        />
      </BaseFormField>

      <BaseFormField
        :label="
          t(
            'academicSettings.semesters.fields.endDate',
          )
        "
        name="end_date"
        required
        :error="
          errors.end_date
        "
      >
        <DatePicker
          v-model="
            form.end_date
          "
          date-format="dd.mm.yy"
          show-icon
          :min-date="
            form.start_date ||
            undefined
          "
          class="w-full"
        />
      </BaseFormField>

      <label>
        <Checkbox
          v-model="
            form.is_current
          "
          binary
        />

        {{
          t(
            'academicSettings.semesters.fields.current',
          )
        }}
      </label>

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
.semester-form {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.semester-form label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  font-weight: 600;
}

@media (max-width: 575px) {
  .semester-form {
    grid-template-columns: 1fr;
  }
}
</style>
