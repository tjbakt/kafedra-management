<script setup lang="ts">
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

import BaseDialog
  from '@/components/base/BaseDialog.vue'

import BaseFormActions
  from '@/components/base/BaseFormActions.vue'

import BaseFormField
  from '@/components/base/BaseFormField.vue'

import type {
  PlannedWorkload,
} from '@/modules/teaching-workload/types'

import type {
  StaffEmployment,
} from '@/modules/staff-employments/types'

import type {
  StaffAcademicYearRecord,
} from '@/modules/staff-academic-years/types'

import type {
  BulkAssignPlannedWorkloadPayload,
  TeacherWorkloadSummary,
} from '@/modules/workload-distribution/types'

import {
  getTeacherWorkloadSummary,
} from '@/modules/workload-distribution/api'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props =
  withDefaults(
    defineProps<{
      workloads:
        PlannedWorkload[]

      employments:
        StaffEmployment[]

      annualRecords:
        StaffAcademicYearRecord[]

      loading?: boolean
    }>(),
    {
      loading: false,
    },
  )

const emit =
  defineEmits<{
    submit: [
      payload:
        BulkAssignPlannedWorkloadPayload,
    ]
  }>()

const { t } =
  useI18n()

const form =
  reactive({
    staff_employment:
      null as number | null,

    notes: '',
  })

const localError =
  ref('')

const teacherSummary =
  ref<
    TeacherWorkloadSummary | null
  >(null)

const summaryLoading =
  ref(false)

const academicYearIds =
  computed(
    () =>
      new Set(
        props.workloads.map(
          (item) =>
            item.academic_year,
        ),
      ),
  )

const departmentIds =
  computed(
    () =>
      new Set(
        props.workloads.map(
          (item) =>
            item.teaching_department,
        ),
      ),
  )

const compatible =
  computed(
    () =>
      props.workloads.length >
        0 &&
      academicYearIds.value.size ===
        1 &&
      departmentIds.value.size ===
        1,
  )

const academicYear =
  computed(
    () =>
      compatible.value
        ? props.workloads[0]
            ?.academic_year ??
          null
        : null,
  )

const department =
  computed(
    () =>
      compatible.value
        ? props.workloads[0]
            ?.teaching_department ??
          null
        : null,
  )

const totalRemainingHours =
  computed(
    () =>
      props.workloads.reduce(
        (
          total,
          workload,
        ) =>
          total +
          Number(
            workload
              .remaining_hours,
          ),
        0,
      ),
  )

const validAnnualEmploymentIds =
  computed(
    () => {
      if (
        academicYear.value ===
        null
      ) {
        return new Set<number>()
      }

      return new Set(
        props.annualRecords
          .filter(
            (record) =>
              record.academic_year ===
                academicYear.value &&
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
      if (
        department.value ===
        null
      ) {
        return []
      }

      return props.employments
        .filter(
          (employment) =>
            employment.department ===
              department.value &&
            employment.is_active &&
            !employment.is_archived &&
            validAnnualEmploymentIds
              .value
              .has(
                employment.id,
              ),
        )
        .map(
          (employment) => ({
            value:
              employment.id,

            label:
              employment
                .staff_member_name,

            description:
              [
                employment
                  .position_name,

                employment.rate,
              ].join(' · '),
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

const projectedHours =
  computed(
    () => {
      if (
        !teacherSummary.value
      ) {
        return null
      }

      return (
        Number(
          teacherSummary
            .value
            .distributed_hours,
        ) +
        totalRemainingHours.value
      )
    },
  )

const projectedPercent =
  computed(
    () => {
      const recommended =
        Number(
          teacherSummary.value
            ?.recommended_hours ??
          0,
        )

      if (
        recommended <= 0 ||
        projectedHours.value ===
          null
      ) {
        return null
      }

      return (
        projectedHours.value /
        recommended *
        100
      )
    },
  )

async function loadSummary():
  Promise<void> {
  teacherSummary.value =
    null

  if (
    academicYear.value ===
      null ||
    !selectedEmployment.value
  ) {
    return
  }

  summaryLoading.value =
    true

  try {
    const summaries =
      await getTeacherWorkloadSummary(
        academicYear.value,

        selectedEmployment
          .value
          .staff_member,
      )

    teacherSummary.value =
      summaries.find(
        (item) =>
          item.staff_employment ===
          selectedEmployment
            .value
            ?.id,
      ) ?? null
  } finally {
    summaryLoading.value =
      false
  }
}

function reset(): void {
  form.staff_employment =
    null

  form.notes = ''

  teacherSummary.value =
    null

  localError.value = ''
}

function submit(): void {
  localError.value = ''

  if (
    !compatible.value
  ) {
    localError.value =
      t(
        'workloadDistribution.bulkAssign.incompatible',
      )

    return
  }

  if (
    !form.staff_employment
  ) {
    localError.value =
      t(
        'workloadDistribution.validation.teacherRequired',
      )

    return
  }

  emit(
    'submit',
    {
      planned_workloads:
        props.workloads.map(
          (item) =>
            item.id,
        ),

      staff_employment:
        form.staff_employment,

      notes:
        form.notes.trim(),
    },
  )
}

watch(
  () =>
    form.staff_employment,

  () => {
    void loadSummary()
  },
)

watch(
  () =>
    visible.value,

  (isVisible) => {
    if (isVisible) {
      reset()
    }
  },
)
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="
      t(
        'workloadDistribution.bulkAssign.title',
      )
    "
    width="58rem"
    :loading="loading"
  >
    <div
      class="
        bulk-assign
      "
    >
      <Message
        v-if="
          !compatible
        "
        severity="error"
        :closable="false"
      >
        {{
          t(
            'workloadDistribution.bulkAssign.incompatible',
          )
        }}
      </Message>

      <Message
        v-if="
          localError
        "
        severity="error"
        :closable="false"
      >
        {{
          localError
        }}
      </Message>

      <div
        class="
          bulk-assign__summary
        "
      >
        <div>
          <span>
            {{
              t(
                'workloadDistribution.bulkAssign.positions',
              )
            }}
          </span>

          <strong>
            {{
              workloads.length
            }}
          </strong>
        </div>

        <div>
          <span>
            {{
              t(
                'workloadDistribution.bulkAssign.hours',
              )
            }}
          </span>

          <strong>
            {{
              totalRemainingHours
                .toFixed(2)
            }}
          </strong>
        </div>

        <div>
          <span>
            {{
              t(
                'workloadDistribution.fields.department',
              )
            }}
          </span>

          <strong>
            {{
              compatible &&
              workloads.length
                ? workloads[0]
                    ?.department_name
                : '—'
            }}
          </strong>
        </div>

        <div>
          <span>
            {{
              t(
                'workloadDistribution.bulkAssign.academicYear',
              )
            }}
          </span>

          <strong>
            {{
              compatible &&
              workloads.length
                ? workloads[0]
                    ?.academic_year_name
                : '—'
            }}
          </strong>
        </div>
      </div>

      <BaseFormField
        :label="
          t(
            'workloadDistribution.fields.teacher',
          )
        "
        name="
          staff_employment
        "
        required
      >
        <Select
          v-model="
            form.staff_employment
          "
          :options="
            employmentOptions
          "
          option-label="label"
          option-value="value"
          filter
          class="w-full"
          :disabled="
            loading ||
            !compatible
          "
        >
          <template
            #option="
              { option }
            "
          >
            <div
              class="
                teacher-option
              "
            >
              <strong>
                {{
                  option.label
                }}
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
          teacherSummary &&
          !summaryLoading
        "
        severity="info"
        :closable="false"
      >
        <div
          class="
            teacher-summary
          "
        >
          <div>
            <span>
              {{
                t(
                  'workloadDistribution.teacherLoad.norm',
                )
              }}
            </span>

            <strong>
              {{
                teacherSummary
                  .recommended_hours ??
                '—'
              }}
            </strong>
          </div>

          <div>
            <span>
              {{
                t(
                  'workloadDistribution.teacherLoad.distributed',
                )
              }}
            </span>

            <strong>
              {{
                teacherSummary
                  .distributed_hours
              }}
            </strong>
          </div>

          <div>
            <span>
              {{
                t(
                  'workloadDistribution.bulkAssign.assigningNow',
                )
              }}
            </span>

            <strong>
              {{
                totalRemainingHours
                  .toFixed(2)
              }}
            </strong>
          </div>

          <div>
            <span>
              {{
                t(
                  'workloadDistribution.teacherLoad.afterAssignment',
                )
              }}
            </span>

            <strong>
              {{
                projectedHours !==
                null
                  ? projectedHours
                      .toFixed(2)
                  : '—'
              }}
            </strong>
          </div>

          <div>
            <span>
              {{
                t(
                  'workloadDistribution.teacherLoad.percent',
                )
              }}
            </span>

            <strong>
              {{
                projectedPercent !==
                null
                  ? `${projectedPercent.toFixed(1)}%`
                  : '—'
              }}
            </strong>
          </div>
        </div>
      </Message>

      <BaseFormField
        :label="
          t(
            'workloadDistribution.fields.notes',
          )
        "
        name="notes"
      >
        <Textarea
          v-model="
            form.notes
          "
          rows="3"
          auto-resize
          class="w-full"
          :disabled="
            loading
          "
        />
      </BaseFormField>
    </div>

    <template #footer>
      <BaseFormActions
        :loading="loading"
        :save-label="
          t(
            'workloadDistribution.bulkAssign.submit',
            {
              count:
                workloads.length,
            },
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
.bulk-assign {
  display: grid;
  gap: 1rem;
}

.bulk-assign__summary,
.teacher-summary {
  display: grid;

  grid-template-columns:
    repeat(
      4,
      minmax(0, 1fr)
    );

  gap: 1rem;
}

.bulk-assign__summary {
  padding: 1rem;

  border:
    1px solid
    var(--app-border-color);

  border-radius:
    var(--app-radius-md);
}

.bulk-assign__summary > div,
.teacher-summary > div {
  display: grid;
  gap: 0.2rem;
}

.bulk-assign__summary span,
.teacher-summary span {
  color:
    var(--app-text-muted);

  font-size: 0.7rem;
}

.teacher-option {
  display: grid;
  gap: 0.15rem;
}

.teacher-option small {
  color:
    var(--app-text-muted);

  font-size: 0.7rem;
}

@media (
  max-width: 800px
) {
  .bulk-assign__summary,
  .teacher-summary {
    grid-template-columns:
      repeat(
        2,
        minmax(0, 1fr)
      );
  }
}
</style>
