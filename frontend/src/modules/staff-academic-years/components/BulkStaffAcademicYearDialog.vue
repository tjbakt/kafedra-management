<script setup lang="ts">
import Select from 'primevue/select'

import {
  computed,
  ref,
} from 'vue'

import { useI18n } from 'vue-i18n'

import BaseDialog from '@/components/base/BaseDialog.vue'
import BaseFormActions from '@/components/base/BaseFormActions.vue'
import BaseFormField from '@/components/base/BaseFormField.vue'

import {
  useLocaleStore,
} from '@/stores/locale'

import type {
  AcademicYearOption,
  BulkCreatePayload,
  DepartmentLookup,
} from '@/modules/staff-academic-years/types'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props = withDefaults(
  defineProps<{
    academicYears: AcademicYearOption[]
    departments: DepartmentLookup[]

    loading?: boolean
  }>(),
  {
    loading: false,
  },
)

const emit = defineEmits<{
  submit: [
    payload: BulkCreatePayload,
  ]
}>()

const { t } = useI18n()

const localeStore =
  useLocaleStore()

const academicYear =
  ref<number | null>(null)

const department =
  ref<number | null>(null)

function localizedName(
  ru: string,
  uz: string,
): string {
  if (
    localeStore.locale === 'uz'
  ) {
    return uz || ru
  }

  return ru || uz
}

const yearOptions =
  computed(() =>
    props.academicYears
      .filter(
        (year) =>
          year.is_active &&
          !year.is_archived &&
          !year.is_closed,
      )
      .map((year) => ({
        value: year.id,
        label: year.name,
      })),
  )

const departmentOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'staffAcademicYears.allDepartments',
        ),
    },

    ...props.departments.map(
      (item) => ({
        value: item.id,

        label:
          localizedName(
            item.name_ru,
            item.name_uz,
          ),
      }),
    ),
  ])

function submit(): void {
  if (!academicYear.value) {
    return
  }

  emit('submit', {
    academic_year:
      academicYear.value,

    department:
      department.value,
  })
}
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="
      t(
        'staffAcademicYears.bulkTitle',
      )
    "
    width="34rem"
    :loading="loading"
  >
    <div class="bulk-form">
      <p>
        {{
          t(
            'staffAcademicYears.bulkDescription',
          )
        }}
      </p>

      <BaseFormField
        :label="
          t(
            'staffAcademicYears.fields.academicYear',
          )
        "
        name="academic_year"
        required
      >
        <Select
          v-model="academicYear"
          :options="yearOptions"
          option-label="label"
          option-value="value"
          class="w-full"
        />
      </BaseFormField>

      <BaseFormField
        :label="
          t(
            'staffAcademicYears.fields.department',
          )
        "
        name="department"
      >
        <Select
          v-model="department"
          :options="
            departmentOptions
          "
          option-label="label"
          option-value="value"
          show-clear
          filter
          class="w-full"
        />
      </BaseFormField>
    </div>

    <template #footer>
      <BaseFormActions
        :loading="loading"
        :disabled="
          !academicYear
        "
        :save-label="
          t(
            'staffAcademicYears.bulkRun',
          )
        "
        submit-icon="pi pi-bolt"
        @cancel="
          visible = false
        "
        @submit="submit"
      />
    </template>
  </BaseDialog>
</template>

<style scoped>
.bulk-form {
  display: grid;
  gap: 1rem;
}

.bulk-form p {
  margin: 0;
  color:
    var(--app-text-muted);
  font-size: 0.82rem;
  line-height: 1.6;
}
</style>
