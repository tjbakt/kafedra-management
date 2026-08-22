<script setup lang="ts">
import Button from 'primevue/button'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import Select from 'primevue/select'
import Tag from 'primevue/tag'

import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  useI18n,
} from 'vue-i18n'

import BaseCard from '@/components/base/BaseCard.vue'
import BasePageHeader from '@/components/base/BasePageHeader.vue'
import BaseToolbar from '@/components/base/BaseToolbar.vue'

import {
  getAcademicYears,
  plannedWorkloadsApi,
} from '@/modules/teaching-workload/api'

import type {
  AcademicYearLookup,
  PlannedWorkload,
  SelectOption,
} from '@/modules/teaching-workload/types'

import {
  useAppToast,
} from '@/composables/useAppToast'

import {
  normalizeApiError,
} from '@/utils/api-errors'

const { t } =
  useI18n()

const toast =
  useAppToast()

const academicYears =
  ref<AcademicYearLookup[]>([])

const items =
  ref<PlannedWorkload[]>([])

const loading =
  ref(false)

const lookupLoading =
  ref(false)

const selectedYear =
  ref<number | null>(null)

const selectedStatus =
  ref<string | null>(null)

const search =
  ref('')

const yearOptions =
  computed<
    SelectOption<number | null>[]
  >(() => [
    {
      value: null,

      label:
        t(
          'teachingWorkload.filters.allYears',
        ),
    },

    ...academicYears.value.map(
      (year) => ({
        value:
          year.id,

        label:
          year.name,
      }),
    ),
  ])

const statusOptions =
  computed(() => [
    {
      value: null,

      label:
        t(
          'teachingWorkload.filters.allStatuses',
        ),
    },

    {
      value: 'calculated',

      label:
        t(
          'teachingWorkload.planned.statuses.calculated',
        ),
    },

    {
      value: 'approved',

      label:
        t(
          'teachingWorkload.planned.statuses.approved',
        ),
    },

    {
      value:
        'partially_distributed',

      label:
        t(
          'teachingWorkload.planned.statuses.partially_distributed',
        ),
    },

    {
      value: 'distributed',

      label:
        t(
          'teachingWorkload.planned.statuses.distributed',
        ),
    },

    {
      value: 'cancelled',

      label:
        t(
          'teachingWorkload.planned.statuses.cancelled',
        ),
    },
  ])

function asNumber(
  value:
    string |
    number |
    null |
    undefined,
): number {
  const result =
    Number(
      value ?? 0,
    )

  return Number.isFinite(
    result,
  )
    ? result
    : 0
}

function normalizeSearchValue(
  value:
    string |
    null |
    undefined,
): string {
  return (
    value ?? ''
  )
    .toLocaleLowerCase()
    .trim()
}

const filteredItems =
  computed(
    () => {
      const query =
        normalizeSearchValue(
          search.value,
        )

      if (!query) {
        return items.value
      }

      return items.value.filter(
        (item) => {
          const values = [
            item.teaching_stream_code,
            item.teaching_stream_name,
            item.curriculum_code,
            item.discipline_code,
            item.discipline_name,
            item.workload_type_name,
            item.department_name,
            item.student_group_code,
          ]

          return values.some(
            (value) =>
              normalizeSearchValue(
                value,
              ).includes(
                query,
              ),
          )
        },
      )
    },
  )

const autumnItems =
  computed(
    () =>
      filteredItems.value.filter(
        (item) =>
          item.semester_number %
            2 ===
          1,
      ),
  )

const springItems =
  computed(
    () =>
      filteredItems.value.filter(
        (item) =>
          item.semester_number %
            2 ===
          0,
      ),
  )

function sumField(
  rows: PlannedWorkload[],
  field:
    | 'base_hours'
    | 'total_hours'
    | 'distributed_hours'
    | 'remaining_hours',
): number {
  return rows.reduce(
    (
      total,
      item,
    ) =>
      total +
      asNumber(
        item[field],
      ),
    0,
  )
}

function totalHours(
  rows:
    PlannedWorkload[],
): number {
  return sumField(
    rows,
    'total_hours',
  )
}

function distributedHours(
  rows:
    PlannedWorkload[],
): number {
  return sumField(
    rows,
    'distributed_hours',
  )
}

function remainingHours(
  rows:
    PlannedWorkload[],
): number {
  return sumField(
    rows,
    'remaining_hours',
  )
}

const autumnTotal =
  computed(
    () =>
      totalHours(
        autumnItems.value,
      ),
  )

const springTotal =
  computed(
    () =>
      totalHours(
        springItems.value,
      ),
  )

const autumnDistributed =
  computed(
    () =>
      distributedHours(
        autumnItems.value,
      ),
  )

const springDistributed =
  computed(
    () =>
      distributedHours(
        springItems.value,
      ),
  )

const autumnRemaining =
  computed(
    () =>
      remainingHours(
        autumnItems.value,
      ),
  )

const springRemaining =
  computed(
    () =>
      remainingHours(
        springItems.value,
      ),
  )

const grandTotal =
  computed(
    () =>
      autumnTotal.value +
      springTotal.value,
  )

const grandDistributed =
  computed(
    () =>
      autumnDistributed.value +
      springDistributed.value,
  )

const grandRemaining =
  computed(
    () =>
      autumnRemaining.value +
      springRemaining.value,
  )

function workloadScope(
  item:
    PlannedWorkload,
): string {
  /*
   * group_semester === null:
   * позиция рассчитана на весь поток.
   *
   * group_semester !== null:
   * позиция относится к конкретной группе.
   */
  if (
    item.group_semester ===
      null ||
    item.group_semester ===
      undefined
  ) {
    return (
      item.teaching_stream_code ||
      '—'
    )
  }

  return (
    item.student_group_code ||
    '—'
  )
}

function workloadScopeType(
  item:
    PlannedWorkload,
): 'stream' | 'group' {
  return (
    item.group_semester ===
      null ||
    item.group_semester ===
      undefined
  )
    ? 'stream'
    : 'group'
}

function statusSeverity(
  status: string,
):
  | 'success'
  | 'info'
  | 'warn'
  | 'secondary'
  | 'danger' {
  if (
    status ===
    'distributed'
  ) {
    return 'success'
  }

  if (
    status ===
    'partially_distributed'
  ) {
    return 'warn'
  }

  if (
    status ===
    'approved'
  ) {
    return 'info'
  }

  if (
    status ===
    'cancelled'
  ) {
    return 'danger'
  }

  return 'secondary'
}

async function loadYears(): Promise<void> {
  lookupLoading.value =
    true

  try {
    const response =
      await getAcademicYears()

    academicYears.value =
      response.results

    if (
      selectedYear.value ===
      null
    ) {
      selectedYear.value =
        response.results.find(
          (year) =>
            year.is_current,
        )?.id ?? null
    }
  } catch (error) {
    toast.error(
      t('common.error'),

      normalizeApiError(
        error,
        t('crud.loadError'),
      ).message,
    )
  } finally {
    lookupLoading.value =
      false
  }
}

async function load(): Promise<void> {
  loading.value =
    true

  try {
    const response =
      await plannedWorkloadsApi.list({
        page: 1,

        page_size: 1000,

        academic_year:
          selectedYear.value ??
          undefined,

        status:
          selectedStatus.value ??
          undefined,

        ordering:
          'teaching_stream__semester_number,teaching_stream__code,curriculum_workload__curriculum_discipline__discipline__name_ru',
      })

    items.value =
      response.results
  } catch (error) {
    items.value = []

    toast.error(
      t('common.error'),

      normalizeApiError(
        error,
        t('crud.loadError'),
      ).message,
    )
  } finally {
    loading.value =
      false
  }
}

async function applyFilters(): Promise<void> {
  await load()
}

async function resetFilters(): Promise<void> {
  selectedYear.value =
    academicYears.value.find(
      (year) =>
        year.is_current,
    )?.id ?? null

  selectedStatus.value =
    null

  search.value =
    ''

  await load()
}

onMounted(
  async () => {
    await loadYears()

    await load()
  },
)
</script>

<template>
  <div
    class="
      planned-workload-view
    "
  >
    <BasePageHeader
      :title="
        t(
          'workload.tabs.planned',
        )
      "
      :description="
        t(
          'teachingWorkload.planned.description',
        )
      "
      icon="
        pi pi-calculator
      "
    />

    <BaseToolbar
      v-model:search="
        search
      "
      :show-create="
        false
      "
      :show-reset="
        true
      "
      :loading="
        loading ||
        lookupLoading
      "
      :search-placeholder="
        t(
          'teachingWorkload.planned.searchPlaceholder',
        )
      "
      @refresh="
        load
      "
      @reset="
        resetFilters
      "
    >
      <template #center>
        <Select
          v-model="selectedYear"
          :options="yearOptions"
          option-label="label"
          option-value="value"
          class="workload-filter"
          @change="applyFilters"
        />

        <Select
          v-model="selectedStatus"
          :options="statusOptions"
          option-label="label"
          option-value="value"
          class="workload-filter"
          @change="applyFilters"
        />
      </template>

      <template #end>
        <Button
          icon="
            pi pi-refresh
          "
          severity="
            secondary
          "
          text
          rounded
          :loading="
            loading
          "
          @click="
            load
          "
        />
      </template>
    </BaseToolbar>

    <!-- ОСЕННИЙ СЕМЕСТР -->
    <section
      class="
        semester-section
      "
    >
      <div
        class="
          semester-section__header
        "
      >
        <div>
          <h2>
            {{
              t(
                'teachingSetup.seasons.autumn',
              )
            }}
          </h2>

          <small>
            {{
              autumnItems.length
            }}
            {{
              t(
                'teachingWorkload.planned.summary.records',
              )
            }}
          </small>
        </div>

        <div
          class="
            semester-section__total
          "
        >
          <span>
            {{
              t(
                'teachingWorkload.planned.summary.totalHours',
              )
            }}
          </span>

          <strong>
            {{
              autumnTotal.toFixed(
                2,
              )
            }}
          </strong>
        </div>
      </div>

      <BaseCard
        :padding="
          false
        "
      >
        <DataTable
          :value="
            autumnItems
          "
          :loading="
            loading
          "
          data-key="
            id
          "
          striped-rows
          scrollable
          scroll-height="
            flex
          "
          class="
            planned-table
          "
        >
          <template #empty>
            <div
              class="
                planned-table__empty
              "
            >
              {{
                t(
                  'teachingWorkload.planned.empty',
                )
              }}
            </div>
          </template>

          <Column
            field="
              semester_number
            "
            :header="
              t(
                'teachingWorkload.streams.fields.semesterNumber',
              )
            "
          >
            <template
              #body="
                { data }
              "
            >
              <strong>
                {{
                  data
                    .semester_number
                }}
              </strong>
            </template>
          </Column>

          <Column
            :header="
              t(
                'teachingWorkload.planned.fields.stream',
              )
            "
            frozen
          >
            <template
              #body="
                { data }
              "
            >
              <div
                class="
                  workload-scope
                "
              >
                <strong>
                  {{
                    workloadScope(
                      data,
                    )
                  }}
                </strong>

                <small>
                  {{
                    workloadScopeType(
                      data,
                    ) ===
                    'stream'
                      ? t(
                          'teachingWorkload.planned.scope.stream',
                        )
                      : t(
                          'teachingWorkload.planned.scope.group',
                        )
                  }}
                </small>
              </div>
            </template>
          </Column>

          <Column
            field="
              discipline_name
            "
            :header="
              t(
                'teachingWorkload.planned.fields.discipline',
              )
            "
          />

          <Column
            field="
              workload_type_name
            "
            :header="
              t(
                'teachingWorkload.planned.fields.workloadType',
              )
            "
          />

          <Column
            field="
              base_hours
            "
            :header="
              t(
                'teachingWorkload.planned.fields.baseHours',
              )
            "
          >
            <template
              #body="
                { data }
              "
            >
              {{
                asNumber(
                  data
                    .base_hours,
                ).toFixed(2)
              }}
            </template>
          </Column>

          <Column
            field="
              calculation_quantity
            "
            :header="
              t(
                'teachingWorkload.planned.fields.quantity',
              )
            "
          >
            <template
              #body="
                { data }
              "
            >
              {{
                asNumber(
                  data
                    .calculation_quantity,
                ).toFixed(2)
              }}
            </template>
          </Column>

          <Column
            field="
              total_hours
            "
            :header="
              t(
                'teachingWorkload.planned.fields.totalHours',
              )
            "
          >
            <template
              #body="
                { data }
              "
            >
              <strong>
                {{
                  asNumber(
                    data
                      .total_hours,
                  ).toFixed(2)
                }}
              </strong>
            </template>
          </Column>

          <Column
            field="
              status
            "
            :header="
              t(
                'teachingWorkload.planned.fields.status',
              )
            "
          >
            <template
              #body="
                { data }
              "
            >
              <Tag
                :value="
                  t(
                    `teachingWorkload.planned.statuses.${data.status}`,
                  )
                "
                :severity="
                  statusSeverity(
                    data.status,
                  )
                "
              />
            </template>
          </Column>
        </DataTable>

        <div
          class="
            semester-footer
          "
        >
          <div>
            <span>
              {{
                t(
                  'teachingWorkload.planned.summary.totalHours',
                )
              }}
            </span>

            <strong>
              {{
                autumnTotal
                  .toFixed(2)
              }}
            </strong>
          </div>

          <div>
            <span>
              {{
                t(
                  'teachingWorkload.planned.fields.distributedHours',
                )
              }}
            </span>

            <strong>
              {{
                autumnDistributed
                  .toFixed(2)
              }}
            </strong>
          </div>

          <div>
            <span>
              {{
                t(
                  'teachingWorkload.planned.fields.remainingHours',
                )
              }}
            </span>

            <strong>
              {{
                autumnRemaining
                  .toFixed(2)
              }}
            </strong>
          </div>
        </div>
      </BaseCard>
    </section>

    <!-- ВЕСЕННИЙ СЕМЕСТР -->
    <section
      class="
        semester-section
      "
    >
      <div
        class="
          semester-section__header
        "
      >
        <div>
          <h2>
            {{
              t(
                'teachingSetup.seasons.spring',
              )
            }}
          </h2>

          <small>
            {{
              springItems.length
            }}
            {{
              t(
                'teachingWorkload.planned.summary.records',
              )
            }}
          </small>
        </div>

        <div
          class="
            semester-section__total
          "
        >
          <span>
            {{
              t(
                'teachingWorkload.planned.summary.totalHours',
              )
            }}
          </span>

          <strong>
            {{
              springTotal.toFixed(
                2,
              )
            }}
          </strong>
        </div>
      </div>

      <BaseCard
        :padding="
          false
        "
      >
        <DataTable
          :value="
            springItems
          "
          :loading="
            loading
          "
          data-key="
            id
          "
          striped-rows
          scrollable
          scroll-height="
            flex
          "
          class="
            planned-table
          "
        >
          <template #empty>
            <div
              class="
                planned-table__empty
              "
            >
              {{
                t(
                  'teachingWorkload.planned.empty',
                )
              }}
            </div>
          </template>

          <Column
            field="
              semester_number
            "
            :header="
              t(
                'teachingWorkload.streams.fields.semesterNumber',
              )
            "
          >
            <template
              #body="
                { data }
              "
            >
              <strong>
                {{
                  data
                    .semester_number
                }}
              </strong>
            </template>
          </Column>

          <Column
            :header="
              t(
                'teachingWorkload.planned.fields.stream',
              )
            "
            frozen
          >
            <template
              #body="
                { data }
              "
            >
              <div
                class="
                  workload-scope
                "
              >
                <strong>
                  {{
                    workloadScope(
                      data,
                    )
                  }}
                </strong>

                <small>
                  {{
                    workloadScopeType(
                      data,
                    ) ===
                    'stream'
                      ? t(
                          'teachingWorkload.planned.scope.stream',
                        )
                      : t(
                          'teachingWorkload.planned.scope.group',
                        )
                  }}
                </small>
              </div>
            </template>
          </Column>

          <Column
            field="
              discipline_name
            "
            :header="
              t(
                'teachingWorkload.planned.fields.discipline',
              )
            "
          />

          <Column
            field="
              workload_type_name
            "
            :header="
              t(
                'teachingWorkload.planned.fields.workloadType',
              )
            "
          />

          <Column
            field="
              base_hours
            "
            :header="
              t(
                'teachingWorkload.planned.fields.baseHours',
              )
            "
          >
            <template
              #body="
                { data }
              "
            >
              {{
                asNumber(
                  data
                    .base_hours,
                ).toFixed(2)
              }}
            </template>
          </Column>

          <Column
            field="
              calculation_quantity
            "
            :header="
              t(
                'teachingWorkload.planned.fields.quantity',
              )
            "
          >
            <template
              #body="
                { data }
              "
            >
              {{
                asNumber(
                  data
                    .calculation_quantity,
                ).toFixed(2)
              }}
            </template>
          </Column>

          <Column
            field="
              total_hours
            "
            :header="
              t(
                'teachingWorkload.planned.fields.totalHours',
              )
            "
          >
            <template
              #body="
                { data }
              "
            >
              <strong>
                {{
                  asNumber(
                    data
                      .total_hours,
                  ).toFixed(2)
                }}
              </strong>
            </template>
          </Column>

          <Column
            field="
              status
            "
            :header="
              t(
                'teachingWorkload.planned.fields.status',
              )
            "
          >
            <template
              #body="
                { data }
              "
            >
              <Tag
                :value="
                  t(
                    `teachingWorkload.planned.statuses.${data.status}`,
                  )
                "
                :severity="
                  statusSeverity(
                    data.status,
                  )
                "
              />
            </template>
          </Column>
        </DataTable>

        <div
          class="
            semester-footer
          "
        >
          <div>
            <span>
              {{
                t(
                  'teachingWorkload.planned.summary.totalHours',
                )
              }}
            </span>

            <strong>
              {{
                springTotal
                  .toFixed(2)
              }}
            </strong>
          </div>

          <div>
            <span>
              {{
                t(
                  'teachingWorkload.planned.fields.distributedHours',
                )
              }}
            </span>

            <strong>
              {{
                springDistributed
                  .toFixed(2)
              }}
            </strong>
          </div>

          <div>
            <span>
              {{
                t(
                  'teachingWorkload.planned.fields.remainingHours',
                )
              }}
            </span>

            <strong>
              {{
                springRemaining
                  .toFixed(2)
              }}
            </strong>
          </div>
        </div>
      </BaseCard>
    </section>

    <!-- ОБЩИЙ ИТОГ -->
    <BaseCard>
      <div
        class="
          annual-total
        "
      >
        <div
          class="
            annual-total__title
          "
        >
          <span>
            {{
              t(
                'teachingWorkload.planned.summary.yearTotal',
              )
            }}
          </span>

          <strong>
            {{
              grandTotal
                .toFixed(2)
            }}
          </strong>
        </div>

        <div
          class="
            annual-total__details
          "
        >
          <div>
            <span>
              {{
                t(
                  'teachingSetup.seasons.autumn',
                )
              }}
            </span>

            <strong>
              {{
                autumnTotal
                  .toFixed(2)
              }}
            </strong>
          </div>

          <div>
            <span>
              {{
                t(
                  'teachingSetup.seasons.spring',
                )
              }}
            </span>

            <strong>
              {{
                springTotal
                  .toFixed(2)
              }}
            </strong>
          </div>

          <div>
            <span>
              {{
                t(
                  'teachingWorkload.planned.fields.distributedHours',
                )
              }}
            </span>

            <strong>
              {{
                grandDistributed
                  .toFixed(2)
              }}
            </strong>
          </div>

          <div>
            <span>
              {{
                t(
                  'teachingWorkload.planned.fields.remainingHours',
                )
              }}
            </span>

            <strong>
              {{
                grandRemaining
                  .toFixed(2)
              }}
            </strong>
          </div>
        </div>
      </div>
    </BaseCard>
  </div>
</template>

<style scoped>
.planned-workload-view {
  display: grid;
  gap: 1.5rem;
}

.workload-filter {
  width: 14rem;
}

.semester-section {
  display: grid;
  gap: 0.75rem;
}

.semester-section__header {
  display: flex;

  align-items: flex-end;
  justify-content:
    space-between;

  gap: 1rem;
}

.semester-section__header h2 {
  margin: 0;

  font-size: 1.1rem;
}

.semester-section__header small {
  color:
    var(
      --app-text-muted,
      #6b7280
    );
}

.semester-section__total {
  display: grid;

  justify-items: end;

  gap: 0.15rem;
}

.semester-section__total span {
  color:
    var(
      --app-text-muted,
      #6b7280
    );

  font-size: 0.72rem;
}

.semester-section__total strong {
  font-size: 1.25rem;
}

.planned-table {
  width: 100%;
}

.planned-table__empty {
  padding: 2rem;

  color:
    var(
      --app-text-muted,
      #6b7280
    );

  text-align: center;
}

.workload-scope {
  display: grid;
  gap: 0.15rem;
}

.workload-scope small {
  color:
    var(
      --app-text-muted,
      #6b7280
    );

  font-size: 0.65rem;
}

.semester-footer {
  display: grid;

  grid-template-columns:
    repeat(
      3,
      minmax(0, 1fr)
    );

  gap: 1rem;

  padding: 1rem;

  border-top:
    1px solid
    var(
      --app-border-color,
      #d1d5db
    );
}

.semester-footer > div {
  display: flex;

  align-items: center;
  justify-content:
    space-between;

  gap: 1rem;
}

.semester-footer span {
  color:
    var(
      --app-text-muted,
      #6b7280
    );

  font-size: 0.75rem;
}

.annual-total {
  display: grid;
  gap: 1rem;
}

.annual-total__title {
  display: flex;

  align-items: center;
  justify-content:
    space-between;

  gap: 1rem;

  font-size: 1rem;
}

.annual-total__title strong {
  font-size: 1.5rem;
}

.annual-total__details {
  display: grid;

  grid-template-columns:
    repeat(
      4,
      minmax(0, 1fr)
    );

  gap: 1rem;
}

.annual-total__details > div {
  display: flex;

  justify-content:
    space-between;

  gap: 0.75rem;

  padding: 0.75rem;

  border:
    1px solid
    var(
      --app-border-color,
      #d1d5db
    );

  border-radius: 0.5rem;
}

.annual-total__details span {
  color:
    var(
      --app-text-muted,
      #6b7280
    );

  font-size: 0.72rem;
}

@media (
  max-width: 900px
) {
  .workload-filter {
    width: 100%;
  }

  .semester-section__header {
    align-items:
      flex-start;

    flex-direction:
      column;
  }

  .semester-section__total {
    justify-items:
      start;
  }

  .semester-footer,
  .annual-total__details {
    grid-template-columns:
      1fr;
  }
}
</style>
