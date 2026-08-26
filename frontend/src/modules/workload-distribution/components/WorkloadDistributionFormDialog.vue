<script setup lang="ts">
import InputNumber from 'primevue/inputnumber'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'

import {
  computed,
  reactive,
  ref,
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
  StaffEmployment,
} from '@/modules/staff-employments/types'

import type {
  StaffAcademicYearRecord,
} from '@/modules/staff-academic-years/types'

import type {
  PlannedWorkload,
} from '@/modules/teaching-workload/types'

import type {
  FieldErrors,
} from '@/types/validation'

import {
  getFieldError,
} from '@/utils/api-errors'

import {
  getTeacherWorkloadSummary,
} from '@/modules/workload-distribution/api'

import type {
  TeacherWorkloadSummary,
  WorkloadDistribution,
  WorkloadDistributionCreatePayload,
  WorkloadDistributionUpdatePayload,
} from '@/modules/workload-distribution/types'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props = withDefaults(
  defineProps<{
    record?: WorkloadDistribution | null

    plannedWorkloads:
      PlannedWorkload[]

    employments:
      StaffEmployment[]

    annualRecords:
      StaffAcademicYearRecord[]

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
  create: [
    payload:
      WorkloadDistributionCreatePayload,
  ]

  update: [
    payload:
      WorkloadDistributionUpdatePayload,
  ]
}>()

const { t } = useI18n()

const form = reactive({
  planned_workload:
    null as number | null,

  staff_employment:
    null as number | null,

  allocated_hours:
    null as number | null,

  notes: '',
})

const localErrors =
  reactive<Record<string, string>>({})

const teacherSummary =
  ref<TeacherWorkloadSummary | null>(
    null,
  )

const summaryLoading =
  ref(false)

const title = computed(
  () =>
    props.record
      ? t(
          'workloadDistribution.editTitle',
        )
      : t(
          'workloadDistribution.createTitle',
        ),
)

const selectedPlannedWorkload =
  computed(
    () =>
      props.plannedWorkloads.find(
        (item) =>
          item.id ===
          form.planned_workload,
      ) ?? null,
  )

const plannedWorkloadOptions =
  computed(() =>
    props.plannedWorkloads
      .filter(
        (item) =>
          !item.is_archived &&
          Number(
            item.remaining_hours,
          ) > 0,
      )
      .map(
        (item) => {
          const scope =
            item.group_semester ===
            null
              ? t(
                  'workloadDistribution.scope.stream',
                )
              : (
                  item.student_group_code ??
                  t(
                    'workloadDistribution.scope.group',
                  )
                )

          return {
            value:
              item.id,

            label:
              `${item.discipline_code} — ${item.discipline_name}`,

            description:
              [
                `${item.semester_number} ${t(
                  'workloadDistribution.shortSemester',
                )}`,

                scope,

                item.workload_type_name,

                `${item.remaining_hours} ${t(
                  'workloadDistribution.shortHours',
                )}`,
              ].join(' · '),
          }
        },
      ),
  )

const validAnnualEmploymentIds =
  computed(
    () => {
      const workload =
        selectedPlannedWorkload.value

      if (!workload) {
        return new Set<number>()
      }

      return new Set(
        props.annualRecords
          .filter(
            (record) =>
              record.academic_year ===
                workload.academic_year &&
              record.is_active &&
              !record.is_archived,
          )
          .map(
            (record) =>
              record.staff_employment,
          ),
      )
    },
  )

const employmentOptions =
  computed(
    () => {
      const workload =
        selectedPlannedWorkload.value

      if (!workload) {
        return []
      }

      return props.employments
        .filter(
          (employment) =>
            employment.department ===
              workload.teaching_department &&
            employment.is_active &&
            !employment.is_archived &&
            validAnnualEmploymentIds.value
              .has(
                employment.id,
              ),
        )
        .map(
          (employment) => ({
            value:
              employment.id,

            label:
              employment.staff_member_name,

            description:
              `${employment.position_name} · ${employment.rate}`,
          }),
        )
    },
  )

const selectedEmployment =
  computed(
    () =>
      props.employments.find(
        (item) =>
          item.id ===
          form.staff_employment,
      ) ?? null,
  )

const maximumHours =
  computed(
    () => {
      const workload =
        selectedPlannedWorkload.value

      if (!workload) {
        return 0
      }

      if (
        props.record &&
        props.record.planned_workload ===
          workload.id
      ) {
        return (
          Number(
            workload.remaining_hours,
          ) +
          Number(
            props.record.allocated_hours,
          )
        )
      }

      return Number(
        workload.remaining_hours,
      )
    },
  )

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
  form.planned_workload =
    null

  form.staff_employment =
    null

  form.allocated_hours =
    null

  form.notes = ''

  teacherSummary.value =
    null

  clearErrors()
}

function fillForm(
  record:
    WorkloadDistribution,
): void {
  form.planned_workload =
    record.planned_workload

  form.staff_employment =
    record.staff_employment

  form.allocated_hours =
    Number(
      record.allocated_hours,
    )

  form.notes =
    record.notes

  clearErrors()
}

async function loadTeacherSummary(): Promise<void> {
  teacherSummary.value =
    null

  const workload =
    selectedPlannedWorkload.value

  const employment =
    selectedEmployment.value

  if (
    !workload ||
    !employment
  ) {
    return
  }

  summaryLoading.value =
    true

  try {
    const result =
      await getTeacherWorkloadSummary(
        workload.academic_year,
        employment.staff_member,
      )

    teacherSummary.value =
      result.find(
        (item) =>
          item.staff_employment ===
          employment.id,
      ) ?? null
  } finally {
    summaryLoading.value =
      false
  }
}

function validate(): boolean {
  clearErrors()

  if (
    !form.planned_workload
  ) {
    localErrors.planned_workload =
      t(
        'workloadDistribution.validation.workloadRequired',
      )
  }

  if (
    !form.staff_employment
  ) {
    localErrors.staff_employment =
      t(
        'workloadDistribution.validation.teacherRequired',
      )
  }

  if (
    form.allocated_hours ===
      null ||
    form.allocated_hours <= 0
  ) {
    localErrors.allocated_hours =
      t(
        'workloadDistribution.validation.hoursPositive',
      )
  } else if (
    form.allocated_hours >
    maximumHours.value
  ) {
    localErrors.allocated_hours =
      t(
        'workloadDistribution.validation.hoursExceeded',
        {
          hours:
            maximumHours.value.toFixed(
              2,
            ),
        },
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
    !form.staff_employment ||
    form.allocated_hours === null
  ) {
    return
  }

  if (props.record) {
    emit('update', {
      staff_employment:
        form.staff_employment,

      allocated_hours:
        form.allocated_hours,

      notes:
        form.notes.trim(),
    })

    return
  }

  if (!form.planned_workload) {
    return
  }

  emit('create', {
    planned_workload:
      form.planned_workload,

    staff_employment:
      form.staff_employment,

    allocated_hours:
      form.allocated_hours,

    notes:
      form.notes.trim(),
  })
}

watch(
  () => form.planned_workload,
  () => {
    if (
      props.record
    ) {
      return
    }

    form.staff_employment =
      null

    form.allocated_hours =
      null

    teacherSummary.value =
      null
  },
)

watch(
  () =>
    form.staff_employment,
  () => {
    void loadTeacherSummary()
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

      void loadTeacherSummary()
    } else {
      resetForm()
    }
  },
)
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="title"
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
        workload-distribution-form
      "
      novalidate
      @submit.prevent="submit"
    >
      <BaseFormField
        :label="
          t(
            'workloadDistribution.fields.plannedWorkload',
          )
        "
        name="planned_workload"
        required
        :error="fieldError('planned_workload',)"
      >
        <Select
          v-model="form.planned_workload"
          :options="plannedWorkloadOptions"
          option-label="label"
          option-value="value"
          filter
          class="w-full"
          :disabled="loading || Boolean(record)"
        >
          <template #option="{ option }">
            <div class="workload-option">
              <strong>
                {{ option.label }}
              </strong>

              <small>
                {{
                  option.description
                }}
              </small>
            </div>
          </template>
        </Select>
      </BaseFormField>

      <Message
        v-if="selectedPlannedWorkload"
        severity="secondary"
        :closable="false"
      >
        <div class="workload-context">
          <div>
            <span>
              {{ t('workloadDistribution.fields.semester',) }}
            </span>

            <strong>
              {{
                selectedPlannedWorkload.semester_number
              }}
            </strong>
          </div>

          <div>
            <span>
              {{ t('workloadDistribution.fields.scope',) }}
            </span>

            <strong>
              {{
                selectedPlannedWorkload
                  .group_semester === null
                  ? t(
                    'workloadDistribution.scope.stream',
                  )
                  : (
                    selectedPlannedWorkload
                      .student_group_code ??
                    '—'
                  )
              }}
            </strong>
          </div>

          <div>
            <span>
              {{ t('workloadDistribution.fields.workloadType',) }}
            </span>

            <strong>
              {{
                selectedPlannedWorkload.workload_type_name
              }}
            </strong>
          </div>
        </div>
      </Message>

      <BaseFormField
        :label="
          t(
            'workloadDistribution.fields.teacher',
          )
        "
        name="staff_employment"
        required
        :error="fieldError('staff_employment',)"
      >
        <Select
          v-model="form.staff_employment"
          :options="employmentOptions"
          option-label="label"
          option-value="value"
          filter
          class="w-full"
          :disabled="loading || !form.planned_workload"
        >
          <template
            #option="{ option }"
          >
            <div class="workload-option">
              <strong>
                {{ option.label }}
              </strong>

              <small>
                {{
                  option.description
                }}
              </small>
            </div>
          </template>
        </Select>
      </BaseFormField>

      <Message
        v-if="
          selectedPlannedWorkload
        "
        severity="info"
        :closable="false"
      >
        {{
          t(
            'workloadDistribution.remainingHint',
            {
              remaining:
                maximumHours.toFixed(
                  2,
                ),

              total:
                Number(
                  selectedPlannedWorkload
                    .total_hours,
                ).toFixed(
                  2,
                ),
            },
          )
        }}
      </Message>

      <Message
        v-if="
          teacherSummary &&
          !summaryLoading
        "
        severity="secondary"
        :closable="false"
      >
        {{
          t(
            'workloadDistribution.teacherNormHint',
            {
              recommended:
                teacherSummary
                  .recommended_hours ??
                '—',

              distributed:
                teacherSummary
                  .distributed_hours,

              remaining:
                teacherSummary
                  .remaining_hours ??
                '—',
            },
          )
        }}
      </Message>

      <BaseFormField
        :label="
          t(
            'workloadDistribution.fields.allocatedHours',
          )
        "
        name="allocated_hours"
        required
        :error="
          fieldError(
            'allocated_hours',
          )
        "
      >
        <InputNumber
          v-model="
            form.allocated_hours
          "
          :min="0.01"
          :max="
            maximumHours
          "
          :max-fraction-digits="2"
          :min-fraction-digits="2"
          :use-grouping="false"
          class="w-full"
          input-class="w-full"
          :disabled="loading"
        />
      </BaseFormField>

      <BaseFormField
        :label="
          t(
            'workloadDistribution.fields.notes',
          )
        "
        name="notes"
      >
        <Textarea
          v-model="form.notes"
          rows="4"
          auto-resize
          class="w-full"
          :disabled="loading"
        />
      </BaseFormField>
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
.workload-distribution-form {
  display: grid;
  gap: 1rem;
}

.workload-context {
  display: grid;

  grid-template-columns:
    repeat(
      3,
      minmax(0, 1fr)
    );

  gap: 1rem;
}

.workload-context > div {
  display: grid;
  gap: 0.2rem;
}

.workload-context span {
  color:
    var(--app-text-muted);

  font-size: 0.72rem;
}

@media (
  max-width: 700px
) {
  .workload-context {
    grid-template-columns:
      1fr;
  }
}

.workload-option {
  display: grid;
  gap: 0.15rem;
}

.workload-option small {
  color:
    var(--app-text-muted);

  font-size: 0.7rem;
}
</style>
