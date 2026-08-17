<script setup lang="ts">
// import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import InputNumber from 'primevue/inputnumber'
import Message from 'primevue/message'
import MultiSelect from 'primevue/multiselect'
import Select from 'primevue/select'
// import Textarea from 'primevue/textarea'

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
  Curriculum,
} from '@/modules/curricula/types'

import type {
  Discipline,
  WorkloadType,
} from '@/modules/curriculum-references/types'

import type {
  CurriculumDiscipline,
  CurriculumDisciplineBundlePayload,
  CurriculumComponentType,
} from '@/modules/curriculum-disciplines/types'

import type {
  CurriculumWorkloadRule,
  WorkloadCalculationMode,
} from '@/modules/curriculum-disciplines/workload-types'

import type {
  FieldErrors,
} from '@/types/validation'

import {
  getFieldError,
} from '@/utils/api-errors'

interface WorkloadFormRow {
  enabled: boolean
  workload_type: number
  calculation_mode: WorkloadCalculationMode
  base_hours: number
  students_per_unit:
    number | null
  notes: string
}

interface SemesterForm {
  semester_number: number
  credits: number
  weeks_count: number
  is_active: boolean
  notes: string
  workloads:
    Record<
      number,
      WorkloadFormRow
    >
}

const visible =
  defineModel<boolean>({
    default: false,
  })

const props = withDefaults(
  defineProps<{
    curriculum: Curriculum
    record?: CurriculumDiscipline | null
    existingEntries?: CurriculumDiscipline[]
    disciplines: Discipline[]
    workloadTypes: WorkloadType[]
    workloadRules: CurriculumWorkloadRule[]
    creditHoursPerCredit?: number
    loading?: boolean
    fieldErrors?: FieldErrors
    nonFieldErrors?: string[]
    generalError?: string
  }>(),
  {
    record: null,
    existingEntries: () => [],
    creditHoursPerCredit: 0,
    loading: false,
    fieldErrors: () => ({}),
    nonFieldErrors: () => [],
    generalError: '',
  },
)

const emit = defineEmits<{
  submit: [
    payload:
      CurriculumDisciplineBundlePayload,
  ]
}>()

const { t } = useI18n()

const form =
  reactive({
    discipline:
      null as number | null,

    component_type: 'required' as CurriculumComponentType,

    semesters: [] as number[],
  })

const semesterForms = reactive< Record<number, SemesterForm> >({})

const localErrors = reactive< Record<string, string> >({})

const selectedDiscipline =
  computed(
    () =>
      props.disciplines.find(
        (item) =>
          item.id ===
          form.discipline,
      ) ?? null,
  )

const title =
  computed(
    () =>
      props.record
        ? t(
            'curriculumDisciplines.editTitle',
          )
        : t(
            'curriculumDisciplines.createTitle',
          ),
  )

const disciplineOptions =
  computed(
    () =>
      props.disciplines
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
              `${item.code} — ${item.display_name}`,

            description:
              item.default_department_name,
          }),
        ),
  )

const semesterOptions =
  computed(
    () =>
      Array.from(
        {
          length:
            props.curriculum
              .semesters_count ??
            0,
        },

        (_, index) => {
          const value =
            index + 1

          return {
            value,

            label:
              `${value} — ${
                value % 2 === 1
                  ? t(
                      'curriculumDisciplines.seasons.autumn',
                    )
                  : t(
                      'curriculumDisciplines.seasons.spring',
                    )
              }`,
          }
        },
      ),
  )

const componentOptions =
  computed(
    () => [
      {
        value: 'required',

        label:
          t(
            'curriculumDisciplines.componentTypes.required',
          ),
      },
      {
        value: 'elective',

        label:
          t(
            'curriculumDisciplines.componentTypes.elective',
          ),
      },
      {
        value: 'optional',

        label:
          t(
            'curriculumDisciplines.componentTypes.optional',
          ),
      },
    ],
  )

const calculationModeOptions =
  computed(
    () => [
      {
        value: 'fixed',

        label:
          t(
            'curriculumWorkloads.calculationModes.fixed',
          ),
      },
      {
        value: 'per_group',

        label:
          t(
            'curriculumWorkloads.calculationModes.perGroup',
          ),
      },
      {
        value: 'per_subgroup',

        label:
          t(
            'curriculumWorkloads.calculationModes.perSubgroup',
          ),
      },
      {
        value: 'per_student',

        label:
          t(
            'curriculumWorkloads.calculationModes.perStudent',
          ),
      },
    ],
  )

function ruleFor(
  workloadTypeId: number,
): CurriculumWorkloadRule | null {
  return (
    props.workloadRules.find(
      (item) =>
        item.workload_type ===
          workloadTypeId &&
        item.is_active &&
        !item.is_archived,
    ) ?? null
  )
}

function createWorkloadRow(
  workloadType:
    WorkloadType,
): WorkloadFormRow {
  const rule =
    ruleFor(
      workloadType.id,
    )

  return {
    enabled: false,

    workload_type: workloadType.id,

    calculation_mode:
      rule
        ?.calculation_mode ??
      workloadType.calculation_mode,

    base_hours:
      rule
        ? Number(
            rule.base_hours,
          )
        : 0,

    students_per_unit:
      rule
        ?.students_per_unit ??
      null,

    notes: '',
  }
}

function ensureSemester(
  semesterNumber: number,
): void {
  if (
    semesterForms[
      semesterNumber
    ]
  ) {
    return
  }

  const workloads:
    Record<
      number,
      WorkloadFormRow
    > = {}

  for (
    const workloadType
    of props.workloadTypes
  ) {
    if (
      !workloadType.is_active ||
      workloadType.is_archived
    ) {
      continue
    }

    workloads[
      workloadType.id
    ] =
      createWorkloadRow(
        workloadType,
      )
  }

  semesterForms[
    semesterNumber
  ] = {
    semester_number: semesterNumber,
    credits: 0,
    weeks_count: 15,
    is_active: true,
    notes: '',
    workloads,
  }
}

function getSemesterForm(
  semesterNumber: number,
): SemesterForm {
  ensureSemester(
    semesterNumber,
  )

  const semester =
    semesterForms[
      semesterNumber
    ]

  if (!semester) {
    throw new Error(
      `Semester ${semesterNumber} was not initialized.`,
    )
  }

  return semester
}

function getWorkloadRow(
  semesterNumber: number,
  workloadTypeId: number,
): WorkloadFormRow {
  const semester =
    getSemesterForm(
      semesterNumber,
    )

  const existingRow =
    semester.workloads[
      workloadTypeId
    ]

  if (existingRow) {
    return existingRow
  }

  const type =
    props.workloadTypes.find(
      (item) =>
        item.id ===
        workloadTypeId,
    )

  if (!type) {
    throw new Error(
      `Workload type ${workloadTypeId} was not found.`,
    )
  }

  const row =
    createWorkloadRow(
      type,
    )

  semester.workloads[
    workloadTypeId
  ] = row

  return row
}

function workloadType(
  id: number,
): WorkloadType | null {
  return (
    props.workloadTypes.find(
      (item) =>
        item.id === id,
    ) ?? null
  )
}

function classroomHours(
  semester:
    SemesterForm,
): number {
  const classroomCodes =
    new Set([
      'lecture',
      'practice',
      'laboratory',
      'seminar',
    ])

  return Object.values(
    semester.workloads,
  )
    .filter(
      (row) => {
        if (!row.enabled) {
          return false
        }

        const type =
          workloadType(
            row.workload_type,
          )

        return Boolean(
          type &&
          classroomCodes.has(
            type.code,
          ),
        )
      },
    )
    .reduce(
      (
        total,
        row,
      ) =>
        total +
        Number(
          row.base_hours ||
          0,
        ),
      0,
    )
}

function independentHours(
  semester:
    SemesterForm,
): number {
  return Object.values(
    semester.workloads,
  )
    .filter(
      (row) => {
        if (!row.enabled) {
          return false
        }

        return (
          workloadType(
            row.workload_type,
          )?.code ===
          'independent_work'
        )
      },
    )
    .reduce(
      (
        total,
        row,
      ) =>
        total +
        Number(
          row.base_hours ||
          0,
        ),
      0,
    )
}

function totalAcademicHours(
  semester:
    SemesterForm,
): number {
  return (
    classroomHours(
      semester,
    ) +
    independentHours(
      semester,
    )
  )
}

function semesterCredits(
  semester:
    SemesterForm,
): number {
  const value = props.creditHoursPerCredit

  if (
    !value ||
    value <= 0
  ) {
    return 0
  }

  return (
    totalAcademicHours(
      semester,
    ) /
    value
  )
}

const selectedSemesterForms =
  computed(
    () =>
      form.semesters
        .slice()
        .sort(
          (a, b) =>
            a - b,
        )
        .map(
          (
            semesterNumber,
          ) =>
            getSemesterForm(
              semesterNumber,
            ),
        ),
  )

const activeWorkloadTypes =
  computed<WorkloadType[]>(
    () => {
      const discipline =
        selectedDiscipline.value

      if (!discipline) {
        return []
      }

      const allowedIds =
        new Set(
          discipline
            .workload_types,
        )

      return props.workloadTypes
        .filter(
          (item) =>
            allowedIds.has(
              item.id,
            ) &&
            item.is_active &&
            !item.is_archived,
        )
        .sort(
          (a, b) =>
            a.sort_order -
            b.sort_order,
        )
    },
  )

const footerTotals =
  computed(
    () => {
      const totals =
        new Map<
          number,
          number
        >()

      for (
        const semester
        of selectedSemesterForms.value
      ) {
        for (
          const row
          of Object.values(
            semester.workloads,
          )
        ) {
          if (!row.enabled) {
            continue
          }

          totals.set(
            row.workload_type,

            (
              totals.get(
                row.workload_type,
              ) ?? 0
            ) +
              Number(
                row.base_hours ||
                0,
              ),
          )
        }
      }

      return activeWorkloadTypes.value
        .filter(
          (type) =>
            totals.has(
              type.id,
            ),
        )
        .map(
          (type) => ({
            workloadType:
              type,

            hours:
              totals.get(
                type.id,
              ) ?? 0,
          }),
        )
    },
  )

const footerClassroom =
  computed(
    () =>
      selectedSemesterForms.value.reduce(
        (
          total,
          semester,
        ) =>
          total +
          classroomHours(
            semester,
          ),
        0,
      ),
  )

const footerIndependent =
  computed(
    () =>
      selectedSemesterForms.value.reduce(
        (
          total,
          semester,
        ) =>
          total +
          independentHours(
            semester,
          ),
        0,
      ),
  )

const footerTotal =
  computed(
    () =>
      footerClassroom.value +
      footerIndependent.value,
  )

function usesDirectHours(
  type: WorkloadType,
): boolean {
  return (
    type.is_classroom ||
    type.code ===
      'independent_work'
  )
}

function fieldError(
  field: string,
): string {
  return (
    localErrors[
      field
    ] ||
    getFieldError(
      props.fieldErrors,
      field,
    )
  )
}

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

function reset(): void {
  form.discipline =
    null

  form.component_type =
    'required'

  form.semesters = []

  for (
    const key
    of Object.keys(
      semesterForms,
    )
  ) {
    delete semesterForms[
      Number(key)
    ]
  }

  clearErrors()
}

function loadExisting(): void {
  reset()

  const entries =
    props.existingEntries
      .length
      ? props.existingEntries
      : props.record
        ? [props.record]
        : []

  if (!entries.length) {
    return
  }

  const first =
    entries[0]

  if (!first) {
    return
  }

  form.discipline =
    first.discipline

  form.component_type =
    first.component_type

  form.semesters =
    entries
      .map(
        (entry) =>
          entry.semester_number,
      )
      .sort(
        (a, b) =>
          a - b,
      )

  for (
    const entry
    of entries
  ) {
    const semester =
      getSemesterForm(
        entry.semester_number,
      )

    semester.credits =
      Number(
        entry.credits,
      )

    semester.weeks_count =
      entry.weeks_count

    semester.is_active =
      entry.is_active

    semester.notes =
      entry.notes

    for (
      const workload
      of entry.workload_items
    ) {
      const row =
        getWorkloadRow(
          entry.semester_number,
          workload.workload_type,
        )

      row.enabled =
        workload.is_active &&
        !workload.is_archived

      row.calculation_mode =
        workload.calculation_mode as WorkloadCalculationMode

      row.base_hours =
        Number(
          workload.base_hours,
        )

      row.students_per_unit =
        workload.students_per_unit

      row.notes =
        workload.notes
    }
  }
}

function validate(): boolean {
  clearErrors()

  if (!form.discipline) {
    localErrors.discipline =
      t(
        'curriculumDisciplines.validation.disciplineRequired',
      )
  }

  if (
    !selectedDiscipline
      .value
      ?.default_department
  ) {
    localErrors.discipline =
      t(
        'curriculumDisciplines.validation.disciplineDepartmentRequired',
      )
  }

  if (
    form.semesters.length ===
    0
  ) {
    localErrors.semesters =
      t(
        'curriculumDisciplines.validation.semestersRequired',
      )
  }

  for (
    const semesterNumber
    of form.semesters
  ) {
    const semester =
      getSemesterForm(
        semesterNumber,
      )

    if (
      semester.credits < 0
    ) {
      localErrors[
        `semester_${semesterNumber}`
      ] =
        t(
          'curriculumDisciplines.validation.nonNegative',
        )
    }

    for (
      const row
      of Object.values(
        semester.workloads,
      )
    ) {
      if (
        row.enabled &&
        row.base_hours < 0
      ) {
        localErrors[
          `semester_${semesterNumber}`
        ] =
          t(
            'curriculumDisciplines.validation.nonNegative',
          )
      }
    }
  }

  return (
    Object.keys(
      localErrors,
    ).length === 0
  )
}

function handleSemesterWorkloadToggle(
  semesterNumber: number,
  type: WorkloadType,
): void {
  const row =
    getWorkloadRow(
      semesterNumber,
      type.id,
    )

  if (
    !type.paired_code
  ) {
    return
  }

  const pair =
    activeWorkloadTypes.value
      .find(
        (item) =>
          item.code ===
          type.paired_code,
      )

  if (!pair) {
    return
  }

  const pairRow =
    getWorkloadRow(
      semesterNumber,
      pair.id,
    )

  pairRow.enabled =
    row.enabled
}

function submit(): void {
  if (!validate()) {
    return
  }

  if (!form.discipline) {
    return
  }

  const payload:
    CurriculumDisciplineBundlePayload =
    {
      curriculum: props.curriculum.id,
      discipline: form.discipline,
      component_type: form.component_type,
      replace_semesters: true,
      semesters:
        form.semesters
          .slice()
          .sort(
            (a, b) =>
              a - b,
          )
          .map(
            (
              semesterNumber,
            ) => {
              const semester =
                getSemesterForm(
                  semesterNumber,
                )

              return {
                semester_number: semesterNumber,
                credits:semesterCredits(semester,),
                weeks_count: semester.weeks_count,
                is_active:semester.is_active,

                notes:
                  semester.notes
                    .trim(),

                workloads:
                  Object.values(
                    semester.workloads,
                  )
                    .filter(
                      (row) =>
                        row.enabled,
                    )
                    .map(
                      (row) => ({
                        workload_type:
                          row.workload_type,

                        calculation_mode:
                          row.calculation_mode,

                        base_hours:
                          row.base_hours,

                        students_per_unit:
                          row.students_per_unit,

                        is_active:
                          true,

                        notes:
                          row.notes
                            .trim(),
                      }),
                    ),
              }
            },
          ),
    }

  emit(
    'submit',
    payload,
  )
}

watch(
  () =>
    form.semesters.slice(),
  (values) => {
    for (
      const semesterNumber
      of values
    ) {
      ensureSemester(
        semesterNumber,
      )
    }
  },
)

watch(
  () =>
    props.workloadRules,
  () => {
    for (
      const semester
      of Object.values(
        semesterForms,
      )
    ) {
      for (
        const type
        of props.workloadTypes
      ) {
        if (
          !type.uses_curriculum_rule
        ) {
          continue
        }

        const rule =
          ruleFor(
            type.id,
          )

        const row =
          semester.workloads[
            type.id
          ]

        if (
          rule &&
          row
        ) {
          row.calculation_mode =
            rule.calculation_mode

          row.base_hours =
            Number(
              rule.base_hours,
            )

          row.students_per_unit =
            rule.students_per_unit
        }
      }
    }
  },
  {
    deep: true,
  },
)

watch(
  () => visible.value,
  (value) => {
    if (!value) {
      return
    }

    if (
      props.record ||
      props.existingEntries
        .length
    ) {
      loadExisting()

      return
    }

    reset()
  },
)
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="title"
    width="90rem"
    :loading="loading"
  >
    <FormValidationSummary
      :field-errors="fieldErrors"
      :non-field-errors="nonFieldErrors"
      :general-error="generalError"
    />

    <form
      class="curriculum-bundle-form"
      @submit.prevent="submit"
    >
      <section
        class="curriculum-section"
      >
        <h3>
          {{
            t(
              'curriculumDisciplines.sections.main',
            )
          }}
        </h3>

        <div
          class="curriculum-grid"
        >
          <BaseFormField
            :label="
              t(
                'curriculumDisciplines.fields.discipline',
              )
            "
            required
            :error="
              fieldError(
                'discipline',
              )
            "
          >
            <Select
              v-model="
                form.discipline
              "
              :options="
                disciplineOptions
              "
              option-label="label"
              option-value="value"
              filter
              class="w-full"
              :disabled="
                loading ||
                Boolean(record)
              "
            >
              <template
                #option="{ option }"
              >
                <div
                  class="option-item"
                >
                  <strong>
                    {{
                      option.label
                    }}
                  </strong>

                  <small
                    v-if="
                      option.description
                    "
                  >
                    {{
                      option.description
                    }}
                  </small>
                </div>
              </template>
            </Select>
          </BaseFormField>

          <BaseFormField
            :label="
              t(
                'curriculumDisciplines.fields.componentType',
              )
            "
          >
            <Select
              v-model="
                form.component_type
              "
              :options="
                componentOptions
              "
              option-label="label"
              option-value="value"
              class="w-full"
            />
          </BaseFormField>

          <BaseFormField
            class="curriculum-grid__wide"
            :label="
              t(
                'curriculumDisciplines.fields.semesters',
              )
            "
            required
            :error="
              fieldError(
                'semesters',
              )
            "
          >
            <MultiSelect
              v-model="
                form.semesters
              "
              :options="
                semesterOptions
              "
              option-label="label"
              option-value="value"
              display="chip"
              class="w-full"
            />
          </BaseFormField>
        </div>

        <Message
          v-if="
            selectedDiscipline
          "
          severity="secondary"
          :closable="false"
        >
          {{
            t(
              'curriculumDisciplines.departmentFromDiscipline',
              {
                department:
                  selectedDiscipline
                    .default_department_name ??
                  '—',
              },
            )
          }}
        </Message>
      </section>

      <section
        class="curriculum-section"
      >
        <h3>
          {{
            t(
              'curriculumDisciplines.sections.hours',
            )
          }}
        </h3>

        <div
          v-for="
            semesterNumber
            in form.semesters
              .slice()
              .sort(
                (a, b) =>
                  a - b,
              )
          "
          :key="
            semesterNumber
          "
          class="semester-card"
        >
          <header
            class="semester-card__header"
          >
            <strong>
              {{
                t(
                  'curriculumDisciplines.semesterOption',
                  {
                    semester:
                      semesterNumber,

                    season:
                      semesterNumber %
                        2 ===
                      1
                        ? t(
                            'curriculumDisciplines.seasons.autumn',
                          )
                        : t(
                            'curriculumDisciplines.seasons.spring',
                          ),
                  },
                )
              }}
            </strong>
          </header>

          <div
            class="semester-meta"
          >
            <BaseFormField
              :label="
                t(
                  'curriculumDisciplines.fields.credits',
                )
              "
            >
              <InputNumber
                :model-value="semesterCredits(
                  getSemesterForm(
                    semesterNumber,
                    ),
                  )
                "
                :min="0"
                :max-fraction-digits="2"
                :use-grouping="false"
                disabled
                class="w-full"
              />
            </BaseFormField>

            <BaseFormField
              :label="
                t(
                  'curriculumDisciplines.fields.weeks',
                )
              "
            >
              <InputNumber
                :model-value="
                  getSemesterForm(
                    semesterNumber,
                  ).weeks_count
                "
                @update:model-value="
                  (value) =>
                    getSemesterForm(
                      semesterNumber,
                    ).weeks_count =
                      Number(
                        value ?? 0,
                      )
                "
                :min="1"
                :use-grouping="false"
                class="w-full"
              />
            </BaseFormField>
          </div>

          <div
            class="workload-table"
          >
            <div
              class="workload-table__header"
            >
              <span></span>

              <span>
                {{
                  t(
                    'curriculumWorkloads.fields.workloadType',
                  )
                }}
              </span>

              <span>
                {{
                  t(
                    'curriculumWorkloads.fields.calculationMode',
                  )
                }}
              </span>

              <span>
                {{
                  t(
                    'curriculumWorkloads.fields.baseHours',
                  )
                }}
              </span>
            </div>

            <div
              v-for="
                type
                in activeWorkloadTypes
              "
              :key="type.id"
              class="workload-table__row"
            >
              <Checkbox
                :model-value="
                  getWorkloadRow(
                    semesterNumber,
                    type.id,
                  ).enabled
                "
                @update:model-value="
                  (value: boolean | undefined) => {
                    getWorkloadRow(
                      semesterNumber,
                      type.id,
                    ).enabled =
                      Boolean( value, )
                  }
                "
                binary
                :disabled="
                Boolean (
                  type.uses_curriculum_rule &&
                  !ruleFor( type.id,)
                )
                "
              />

              <div
                class="workload-name"
              >
                <strong>
                  {{
                    type.display_name
                  }}
                </strong>

                <small
                  v-if="
                    type.uses_curriculum_rule
                  "
                >
                  {{
                    ruleFor(
                      type.id,
                    )
                      ? t(
                          'curriculumDisciplines.curriculumRuleApplied',
                        )
                      : t(
                          'curriculumDisciplines.curriculumRuleMissing',
                        )
                  }}
                </small>
              </div>

              <Select
                :model-value="
                  getWorkloadRow(
                    semesterNumber,
                    type.id,
                  ).calculation_mode
                "
                @update:model-value="
                  (value: unknown) =>
                    getWorkloadRow(
                      semesterNumber,
                      type.id,
                    ).calculation_mode =
                      value as WorkloadCalculationMode
                "
                :options="
                  calculationModeOptions
                "
                option-label="label"
                option-value="value"
                :disabled="
                  Boolean(
                    type.uses_curriculum_rule ||
                      !getWorkloadRow(
                        semesterNumber,
                        type.id,
                      ).enabled,
                  )
                "
                class="w-full"
              />

              <InputNumber
                v-if="usesDirectHours(type)"
                v-model="getWorkloadRow(semesterNumber, type.id,).base_hours"
                :min="0"
                :max-fraction-digits="2"
                :use-grouping="false"
                :disabled="!getWorkloadRow(semesterNumber, type.id,).enabled"
                class="w-full"
              />

              <Checkbox
                v-else
                v-model="getWorkloadRow(semesterNumber, type.id,).enabled"
                binary @change="handleSemesterWorkloadToggle(semesterNumber, type,)"
              />
            </div>
          </div>

          <footer
            class="semester-totals"
          >
            <div>
              <span>
                {{
                  t(
                    'curriculumDisciplines.auditoriumTotal',
                  )
                }}
              </span>

              <strong>
                {{
                  classroomHours(
                    getSemesterForm(
                      semesterNumber,
                    ),
                  ).toFixed(2)
                }}
              </strong>
            </div>

            <div>
              <span>
                {{
                  t(
                    'curriculumDisciplines.fields.independentHours',
                  )
                }}
              </span>

              <strong>
                {{
                  independentHours(
                    getSemesterForm(
                      semesterNumber,
                    ),
                  ).toFixed(2)
                }}
              </strong>
            </div>

            <div>
              <span>
                {{
                  t(
                    'curriculumDisciplines.totalAcademic',
                  )
                }}
              </span>

              <strong>
                {{
                  totalAcademicHours(
                    getSemesterForm(
                      semesterNumber,
                    ),
                  ).toFixed(2)
                }}
              </strong>
            </div>
            <div>
              <span>
                {{
                  t(
                    'curriculumDisciplines.fields.credits',
                  )
                }}
              </span>

              <strong>
                {{
                  semesterCredits(
                    getSemesterForm(
                      semesterNumber,
                    ),
                  ).toFixed(2)
                }}
              </strong>
            </div>
          </footer>
        </div>

        <div
          v-if="
            form.semesters.length
          "
          class="grand-total"
        >
          <h4>
            {{
              t(
                'curriculumDisciplines.grandTotal',
              )
            }}
          </h4>

          <div
            class="grand-total__types"
          >
            <div
              v-for="
                item
                in footerTotals
              "
              :key="
                item.workloadType.id
              "
            >
              <span>
                {{
                  item.workloadType
                    .display_name
                }}
              </span>

              <strong>
                {{
                  item.hours.toFixed(
                    2,
                  )
                }}
              </strong>
            </div>
          </div>

          <div
            class="grand-total__main"
          >
            <div>
              <span>
                {{
                  t(
                    'curriculumDisciplines.auditoriumTotal',
                  )
                }}
              </span>

              <strong>
                {{
                  footerClassroom
                    .toFixed(2)
                }}
              </strong>
            </div>

            <div>
              <span>
                {{
                  t(
                    'curriculumDisciplines.fields.independentHours',
                  )
                }}
              </span>

              <strong>
                {{
                  footerIndependent
                    .toFixed(2)
                }}
              </strong>
            </div>

            <div>
              <span>
                {{
                  t(
                    'curriculumDisciplines.totalAcademic',
                  )
                }}
              </span>

              <strong>
                {{
                  footerTotal
                    .toFixed(2)
                }}
              </strong>
            </div>
          </div>
        </div>
      </section>
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
.curriculum-bundle-form,
.curriculum-section {
  display: grid;
  gap: 1rem;
}

.curriculum-section h3,
.grand-total h4 {
  margin: 0;
}

.curriculum-grid,
.semester-meta {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.curriculum-grid__wide {
  grid-column: 1 / -1;
}

.option-item,
.workload-name {
  display: grid;
  gap: 0.15rem;
}

.option-item small,
.workload-name small {
  color:
    var(--app-text-muted, #6b7280);

  font-size: 0.7rem;
}

.semester-card {
  display: grid;
  gap: 1rem;

  padding: 1rem;

  border:
    1px solid
    var(--app-border-color, #d1d5db);

  border-radius:
    var(--app-radius-md, 0.5rem);
}

.semester-card__header {
  display: flex;
  align-items: center;
  justify-content:
    space-between;
}

.workload-table {
  display: grid;

  border:
    1px solid
    var(--app-border-color, #d1d5db);

  border-radius:
    var(--app-radius-md, 0.5rem);

  overflow: hidden;
}

.workload-table__header,
.workload-table__row {
  display: grid;

  grid-template-columns:
    3rem
    minmax(
      15rem,
      1fr
    )
    minmax(
      12rem,
      16rem
    )
    10rem;

  align-items: center;

  gap: 0.75rem;

  padding:
    0.65rem
    0.75rem;
}

.workload-table__header {
  font-size: 0.72rem;

  font-weight: 700;

  background:
    var(
      --app-surface-muted,
      #f3f4f6
    );
}

.workload-table__row
  + .workload-table__row {
  border-top:
    1px solid
    var(--app-border-color, #d1d5db);
}

.semester-totals,
.grand-total__main {
  display: grid;

  grid-template-columns:
    repeat(
      3,
      minmax(0, 1fr)
    );

  gap: 0.75rem;
}

.semester-totals > div,
.grand-total__main > div,
.grand-total__types > div {
  display: flex;

  justify-content:
    space-between;

  gap: 1rem;

  padding: 0.75rem;

  border:
    1px solid
    var(--app-border-color, #d1d5db);

  border-radius:
    var(--app-radius-md, 0.5rem);
}

.grand-total {
  display: grid;

  gap: 1rem;

  padding: 1rem;

  border:
    2px solid
    var(--app-border-color, #d1d5db);

  border-radius:
    var(--app-radius-md, 0.5rem);
}

.grand-total__types {
  display: grid;

  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );

  gap: 0.5rem;
}

@media (
  max-width: 850px
) {
  .curriculum-grid,
  .semester-meta,
  .semester-totals,
  .grand-total__main,
  .grand-total__types {
    grid-template-columns:
      1fr;
  }

  .curriculum-grid__wide {
    grid-column: auto;
  }

  .workload-table {
    overflow-x: auto;
  }

  .workload-table__header,
  .workload-table__row {
    min-width: 52rem;
  }
}
</style>
