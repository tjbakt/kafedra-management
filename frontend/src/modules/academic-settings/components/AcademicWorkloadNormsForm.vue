<script setup lang="ts">
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import InputNumber from 'primevue/inputnumber'
import Message from 'primevue/message'
import Select from 'primevue/select'

import {
  computed,
  onMounted,
  ref,
  watch,
} from 'vue'

import {
  useI18n,
} from 'vue-i18n'

import BaseCard from '@/components/base/BaseCard.vue'
import BaseFormField from '@/components/base/BaseFormField.vue'

import {
  academicYearCreditNormsApi,
  academicYearWorkloadNormsApi,
  getAllAcademicYears,
} from '@/modules/academic-settings/api'

import type {
  AcademicYear,
  AcademicYearCreditNorm,
  AcademicYearCreditNormPayload,
  AcademicYearWorkloadNorm,
  AcademicYearWorkloadNormPayload,
} from '@/modules/academic-settings/types'

import {
  getAllWorkloadTypes,
} from '@/modules/curriculum-references/api'

import type {
  WorkloadType,
} from '@/modules/curriculum-references/types'

import {
  useAppToast,
} from '@/composables/useAppToast'

import {
  normalizeApiError,
} from '@/utils/api-errors'

interface NormFormRow {
  workloadType: WorkloadType

  existingId: number | null

  enabled: boolean

  coefficient:
    number | null
}

const { t } =
  useI18n()

const toast =
  useAppToast()

const years =
  ref<AcademicYear[]>([])

const workloadTypes =
  ref<WorkloadType[]>([])

const rows =
  ref<NormFormRow[]>([])

const selectedYearId =
  ref<number | null>(null)

const creditNorm =
  ref<AcademicYearCreditNorm | null>(
    null,
  )

const hoursPerCredit =
  ref<number | null>(30)

const loading =
  ref(false)

const saving =
  ref(false)

const loadError =
  ref('')

const creditError =
  ref('')

const annualNormCodes =
  new Set<string>([
    'rating',

    'course_work_supervision',
    'course_work_defense',

    'course_project_supervision',
    'course_project_defense',

    'scientific_practice_supervision',
    'qualification_practice_supervision',

    'graduation_work_supervision',
    'graduation_work_defense',

    'master_dissertation_supervision',
    'master_dissertation_defense',
  ])

const selectedYear =
  computed<AcademicYear | null>(
    () =>
      years.value.find(
        (item) =>
          item.id ===
          selectedYearId.value,
      ) ?? null,
  )

const isYearClosed =
  computed(
    () =>
      Boolean(
        selectedYear.value
          ?.is_closed,
      ),
  )

const yearOptions =
  computed(
    () =>
      years.value.map(
        (year) => ({
          value: year.id,

          label:
            year.is_current
              ? `${year.name} — ${t(
                  'academicSettings.workloadNorms.currentYear',
                )}`
              : year.name,
        }),
      ),
  )

const availableWorkloadTypes =
  computed(
    () =>
      workloadTypes.value
        .filter(
          (type) =>
            type.is_active &&
            !type.is_archived &&
            annualNormCodes.has(
              type.code,
            ),
        )
        .sort(
          (a, b) =>
            a.sort_order -
            b.sort_order,
        ),
  )

function clearErrors(): void {
  loadError.value = ''

  creditError.value = ''
}

function createEmptyRows(): void {
  rows.value =
    availableWorkloadTypes.value.map(
      (workloadType) => ({
        workloadType,

        existingId: null,

        enabled: false,

        coefficient: null,
      }),
    )
}

async function loadLookups(): Promise<void> {
  loading.value = true

  clearErrors()

  try {
    const [
      yearsResponse,
      workloadTypesResponse,
    ] = await Promise.all([
      getAllAcademicYears(),

      getAllWorkloadTypes(),
    ])

    years.value =
      yearsResponse.results

    workloadTypes.value =
      workloadTypesResponse.results

    const currentYear =
      years.value.find(
        (year) =>
          year.is_current,
      )

    selectedYearId.value =
      currentYear?.id ??
      years.value[0]?.id ??
      null

    createEmptyRows()
  } catch (error) {
    const normalized =
      normalizeApiError(
        error,
        t('crud.loadError'),
      )

    loadError.value =
      normalized.message

    toast.error(
      t('common.error'),
      normalized.message,
    )
  } finally {
    loading.value = false
  }
}

async function loadNorms(): Promise<void> {
  if (!selectedYearId.value) {
    creditNorm.value = null

    hoursPerCredit.value =
      30

    createEmptyRows()

    return
  }

  loading.value = true

  clearErrors()

  try {
    const [
      creditResponse,
      normsResponse,
    ] = await Promise.all([
      academicYearCreditNormsApi.list({
        academic_year:
          selectedYearId.value,

        page_size: 100,
      }),

      academicYearWorkloadNormsApi.list({
        academic_year:
          selectedYearId.value,

        page_size: 500,

        ordering:
          'workload_type__sort_order',
      }),
    ])

    creditNorm.value =
      creditResponse.results[0] ??
      null

    hoursPerCredit.value =
      creditNorm.value
        ? Number(
            creditNorm.value
              .hours_per_credit,
          )
        : 30

    const existingNorms =
      new Map<
        number,
        AcademicYearWorkloadNorm
      >(
        normsResponse.results.map(
          (norm) => [
            norm.workload_type,
            norm,
          ],
        ),
      )

    rows.value =
      availableWorkloadTypes.value.map(
        (workloadType) => {
          const existing =
            existingNorms.get(
              workloadType.id,
            )

          return {
            workloadType,

            existingId:
              existing?.id ??
              null,

            enabled:
              existing
                ? existing.is_active
                : false,

            coefficient:
              existing
                ? Number(
                    existing.coefficient,
                  )
                : null,
          }
        },
      )
  } catch (error) {
    const normalized =
      normalizeApiError(
        error,
        t('crud.loadError'),
      )

    loadError.value =
      normalized.message

    toast.error(
      t('common.error'),
      normalized.message,
    )
  } finally {
    loading.value = false
  }
}

function isWeeklyNorm(
  row: NormFormRow,
): boolean {
  return (
    row.workloadType
      .uses_weekly_norm
  )
}

function validate(): boolean {
  clearErrors()

  if (
    !hoursPerCredit.value ||
    hoursPerCredit.value <= 0
  ) {
    creditError.value =
      t(
        'academicSettings.workloadNorms.validation.creditPositive',
      )

    return false
  }

  for (
    const row
    of rows.value
  ) {
    if (
      row.enabled &&
      (
        row.coefficient ===
          null ||
        row.coefficient < 0
      )
    ) {
      toast.error(
        t('common.error'),

        t(
          'academicSettings.workloadNorms.validation.coefficientRequired',
          {
            name:
              row.workloadType
                .display_name,
          },
        ),
      )

      return false
    }
  }

  return true
}

async function saveCreditNorm(
  academicYearId: number,
): Promise<void> {
  if (
    hoursPerCredit.value ===
    null
  ) {
    return
  }

  const payload:
    AcademicYearCreditNormPayload =
    {
      academic_year:
        academicYearId,

      hours_per_credit:
        hoursPerCredit.value,

      notes: '',
    }

  if (creditNorm.value) {
    await academicYearCreditNormsApi
      .update(
        creditNorm.value.id,
        payload,
      )

    return
  }

  await academicYearCreditNormsApi
    .create(payload)
}

async function saveWorkloadRow(
  academicYearId: number,
  row: NormFormRow,
): Promise<void> {
  /*
   * Не создаём новую строку,
   * если она вообще не включена.
   */
  if (
    !row.enabled &&
    row.existingId === null
  ) {
    return
  }

  const payload:
    AcademicYearWorkloadNormPayload =
    {
      academic_year:
        academicYearId,

      workload_type:
        row.workloadType.id,

      coefficient:
        row.coefficient ?? 0,

      is_active:
        row.enabled,

      notes: '',
    }

  if (row.existingId !== null) {
    await academicYearWorkloadNormsApi
      .update(
        row.existingId,
        payload,
      )

    return
  }

  await academicYearWorkloadNormsApi
    .create(payload)
}

async function save(): Promise<void> {
  if (
    !selectedYearId.value ||
    isYearClosed.value ||
    !validate()
  ) {
    return
  }

  saving.value = true

  clearErrors()

  try {
    const academicYearId =
      selectedYearId.value

    await saveCreditNorm(
      academicYearId,
    )

    await Promise.all(
      rows.value.map(
        (row) =>
          saveWorkloadRow(
            academicYearId,
            row,
          ),
      ),
    )

    toast.success(
      t('common.success'),

      t(
        'academicSettings.workloadNorms.saveSuccess',
      ),
    )

    await loadNorms()
  } catch (error) {
    const normalized =
      normalizeApiError(
        error,
        t('crud.saveError'),
      )

    toast.error(
      t('common.error'),
      normalized.message,
    )
  } finally {
    saving.value = false
  }
}

function coefficientHint(
  code: string,
): string {
  switch (code) {
    case 'rating':
      return t(
        'academicSettings.workloadNorms.hints.rating',
      )

    case 'course_work_supervision':
      return t(
        'academicSettings.workloadNorms.hints.courseWorkSupervision',
      )

    case 'course_work_defense':
      return t(
        'academicSettings.workloadNorms.hints.courseWorkDefense',
      )

    case 'course_project_supervision':
      return t(
        'academicSettings.workloadNorms.hints.courseProjectSupervision',
      )

    case 'course_project_defense':
      return t(
        'academicSettings.workloadNorms.hints.courseProjectDefense',
      )

    case 'graduation_work_supervision':
      return t(
        'academicSettings.workloadNorms.hints.graduationSupervision',
      )

    case 'master_dissertation_supervision':
      return t(
        'academicSettings.workloadNorms.hints.masterSupervision',
      )

    case 'scientific_practice_supervision':
      return t(
        'academicSettings.workloadNorms.hints.scientificPractice',
      )

    case 'qualification_practice_supervision':
      return t(
        'academicSettings.workloadNorms.hints.qualificationPractice',
      )

    default:
      return t(
        'academicSettings.workloadNorms.hints.default',
      )
  }
}

watch(
  selectedYearId,
  async (
    value,
    oldValue,
  ) => {
    if (
      value === oldValue ||
      value === null
    ) {
      return
    }

    await loadNorms()
  },
)

onMounted(
  async () => {
    await loadLookups()

    if (selectedYearId.value) {
      await loadNorms()
    }
  },
)
</script>

<template>
  <div
    class="
      workload-norms
    "
  >
    <Message
      v-if="loadError"
      severity="error"
      :closable="false"
    >
      {{ loadError }}
    </Message>

    <BaseCard
      :title="
        t(
          'academicSettings.workloadNorms.generalTitle',
        )
      "
      :subtitle="
        t(
          'academicSettings.workloadNorms.generalDescription',
        )
      "
    >
      <div
        class="
          workload-norms__general
        "
      >
        <BaseFormField
          :label="
            t(
              'academicSettings.workloadNorms.fields.academicYear',
            )
          "
          required
        >
          <Select
            v-model="
              selectedYearId
            "
            :options="
              yearOptions
            "
            option-label="label"
            option-value="value"
            class="w-full"
            :disabled="
              loading ||
              saving
            "
          />
        </BaseFormField>

        <BaseFormField
          :label="
            t(
              'academicSettings.workloadNorms.fields.hoursPerCredit',
            )
          "
          required
          :error="
            creditError
          "
          :hint="
            t(
              'academicSettings.workloadNorms.hints.credit',
            )
          "
        >
          <InputNumber
            v-model="
              hoursPerCredit
            "
            :min="0.01"
            :min-fraction-digits="2"
            :max-fraction-digits="2"
            :use-grouping="false"
            suffix=" ч."
            class="w-full"
            input-class="w-full"
            :disabled="
              loading ||
              saving ||
              isYearClosed
            "
          />
        </BaseFormField>
      </div>

      <Message
        v-if="isYearClosed"
        severity="warn"
        :closable="false"
        class="
          workload-norms__message
        "
      >
        {{
          t(
            'academicSettings.workloadNorms.closedYear',
          )
        }}
      </Message>
    </BaseCard>

    <BaseCard
      :title="
        t(
          'academicSettings.workloadNorms.normsTitle',
        )
      "
      :subtitle="
        t(
          'academicSettings.workloadNorms.normsDescription',
        )
      "
    >
      <div
        v-if="
          rows.length === 0 &&
          !loading
        "
        class="
          workload-norms__empty
        "
      >
        {{
          t(
            'academicSettings.workloadNorms.empty',
          )
        }}
      </div>

      <div
        v-else
        class="
          workload-norms-table
        "
      >
        <div
          class="
            workload-norms-table__header
          "
        >
          <span>
            {{
              t(
                'academicSettings.workloadNorms.columns.enabled',
              )
            }}
          </span>

          <span>
            {{
              t(
                'academicSettings.workloadNorms.columns.workloadType',
              )
            }}
          </span>

          <span>
            {{
              t(
                'academicSettings.workloadNorms.columns.calculationMode',
              )
            }}
          </span>

          <span>
            {{
              t(
                'academicSettings.workloadNorms.columns.coefficient',
              )
            }}
          </span>
        </div>

        <div
          v-for="
            row in rows
          "
          :key="
            row.workloadType.id
          "
          class="
            workload-norms-table__row
          "
        >
          <div
            class="
              workload-norms-table__check
            "
          >
            <Checkbox
              v-model="
                row.enabled
              "
              binary
              :disabled="
                loading ||
                saving ||
                isYearClosed
              "
            />
          </div>

          <div
            class="
              workload-norms-table__name
            "
          >
            <strong>
              {{
                row.workloadType
                  .display_name
              }}
            </strong>

            <small>
              {{
                coefficientHint(
                  row.workloadType
                    .code,
                )
              }}
            </small>
          </div>

          <div>
            {{
              row.workloadType
                .calculation_mode_name
            }}
          </div>

          <InputNumber
            v-model="row.coefficient"
            :min="0"
            :min-fraction-digits="2"
            :max-fraction-digits="4"
            :use-grouping="false"
            :suffix=" isWeeklyNorm(row) ? ' ч./нед.' : '' "
            class="w-full"
            input-class="w-full"
            :disabled="
              !row.enabled ||
              loading ||
              saving ||
              isYearClosed
            "
          />
        </div>
      </div>

      <template #footer>
        <div
          class="
            workload-norms__actions
          "
        >
          <Button
            :label="
              t('common.save')
            "
            icon="pi pi-save"
            :loading="
              saving
            "
            :disabled="
              loading ||
              !selectedYearId ||
              isYearClosed
            "
            @click="save"
          />
        </div>
      </template>
    </BaseCard>
  </div>
</template>

<style scoped>
.workload-norms {
  display: grid;
  gap: 1rem;
}

.workload-norms__general {
  display: grid;

  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );

  gap: 1rem;
}

.workload-norms__message {
  margin-top: 1rem;
}

.workload-norms__empty {
  padding: 2rem;

  color:
    var(
      --app-text-muted,
      #6b7280
    );

  text-align: center;
}

.workload-norms-table {
  display: grid;

  overflow: hidden;

  border:
    1px solid
    var(
      --app-border-color,
      #d1d5db
    );

  border-radius:
    var(
      --app-radius-md,
      0.5rem
    );
}

.workload-norms-table__header,
.workload-norms-table__row {
  display: grid;

  grid-template-columns:
    5rem
    minmax(
      18rem,
      1fr
    )
    minmax(
      10rem,
      14rem
    )
    12rem;

  align-items: center;

  gap: 1rem;

  padding:
    0.75rem
    1rem;
}

.workload-norms-table__header {
  font-size: 0.75rem;

  font-weight: 700;

  background:
    var(
      --app-surface-muted,
      #f3f4f6
    );
}

.workload-norms-table__row
  + .workload-norms-table__row {
  border-top:
    1px solid
    var(
      --app-border-color,
      #d1d5db
    );
}

.workload-norms-table__check {
  display: flex;
  justify-content: center;
}

.workload-norms-table__name {
  display: grid;
  gap: 0.15rem;
}

.workload-norms-table__name strong {
  font-size: 0.82rem;
}

.workload-norms-table__name small {
  color:
    var(
      --app-text-muted,
      #6b7280
    );

  font-size: 0.7rem;
}

.workload-norms__actions {
  display: flex;
  justify-content: flex-end;
}

@media (
  max-width: 850px
) {
  .workload-norms__general {
    grid-template-columns:
      1fr;
  }

  .workload-norms-table {
    overflow-x: auto;
  }

  .workload-norms-table__header,
  .workload-norms-table__row {
    min-width: 55rem;
  }
}
</style>
