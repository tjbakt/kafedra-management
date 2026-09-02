<script setup lang="ts">
import Button from 'primevue/button'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import ProgressBar from 'primevue/progressbar'
import Tag from 'primevue/tag'

import {
  computed,
} from 'vue'

import {
  useI18n,
} from 'vue-i18n'

import type {
  PlannedWorkload,
} from '@/modules/teaching-workload/types'

const props =
  withDefaults(
    defineProps<{
      items: PlannedWorkload[]
      loading?: boolean
      canAssign?: boolean
      selection?: PlannedWorkload[]
    }>(),
    {
      loading: false,
      canAssign: false,
      selection: () => [],
    },
  )

const emit =
  defineEmits<{
    assign: [
      workload:
        PlannedWorkload,
    ]
    'update:selection': [
      value:
        PlannedWorkload[],
    ]
  }>()

const { t } =
  useI18n()

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

const rows =
  computed(
    () =>
      props.items
        .filter(
          (item) =>
            !item.is_archived &&
            item.status !==
              'cancelled' &&
            asNumber(
              item.remaining_hours,
            ) > 0,
        )
        .sort(
          (
            left,
            right,
          ) => {
            if (
              left.semester_number !==
              right.semester_number
            ) {
              return (
                left.semester_number -
                right.semester_number
              )
            }

            const discipline =
              left.discipline_name
                .localeCompare(
                  right.discipline_name,
                )

            if (discipline) {
              return discipline
            }

            return (
              left.workload_type_name
                .localeCompare(
                  right.workload_type_name,
                )
            )
          },
        ),
  )

function distributionPercent(
  item:
    PlannedWorkload,
): number {
  const total =
    asNumber(
      item.total_hours,
    )

  if (total <= 0) {
    return 0
  }

  const distributed =
    asNumber(
      item.distributed_hours,
    )

  return Math.min(
    100,
    Math.max(
      0,
      (
        distributed /
        total
      ) * 100,
    ),
  )
}

function scopeLabel(
  item:
    PlannedWorkload,
): string {
  if (
    item.group_semester ===
    null
  ) {
    return t(
      'workloadDistribution.scope.stream',
    )
  }

  return (
    item.student_group_code ??
    t(
      'workloadDistribution.scope.group',
    )
  )
}

function scopeSeverity(
  item:
    PlannedWorkload,
):
  | 'info'
  | 'secondary' {
  return (
    item.group_semester ===
    null
  )
    ? 'info'
    : 'secondary'
}

function statusSeverity(
  item:
    PlannedWorkload,
):
  | 'success'
  | 'warn'
  | 'secondary' {
  if (
    item.is_fully_distributed
  ) {
    return 'success'
  }

  if (
    asNumber(
      item.distributed_hours,
    ) > 0
  ) {
    return 'warn'
  }

  return 'secondary'
}
</script>

<template>
  <div
    class="
      planned-distribution
    "
  >
    <div
      class="
        planned-distribution__header
      "
    >
      <div>
        <h3>
          {{
            t(
              'workloadDistribution.planned.title',
            )
          }}
        </h3>

        <p>
          {{
            t(
              'workloadDistribution.planned.description',
            )
          }}
        </p>
      </div>

      <Tag
        :value="
          t(
            'workloadDistribution.planned.positionsCount',
            {
              count:
                rows.length,
            },
          )
        "
        severity="secondary"
      />
    </div>

    <DataTable
      :value="rows"
      :selection="selection"
      :loading="loading"
      data-key="id"
      striped-rows
      scrollable
      class="planned-distribution__table"
      @update:selection="
        emit(
          'update:selection',
          $event as PlannedWorkload[],
        )
      "
    >
      <template #empty>
        <Column
          v-if="canAssign"
          selection-mode="multiple"
          header-style="width: 3rem"
          body-style="width: 3rem"
        />
        <div class="planned-distribution__empty">
          {{
            t(
              'workloadDistribution.planned.empty',
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
            'workloadDistribution.fields.semester',
          )
        "
        style="
          min-width: 7rem
        "
      >
        <template
          #body="
            { data }
          "
        >
          <div
            class="
              semester-cell
            "
          >
            <strong>
              {{
                data.semester_number
              }}
            </strong>

            <small>
              {{
                data.season ===
                'autumn'
                  ? t(
                      'workloadDistribution.seasons.autumn',
                    )
                  : t(
                      'workloadDistribution.seasons.spring',
                    )
              }}
            </small>
          </div>
        </template>
      </Column>

      <Column
        field="
          curriculum_code
        "
        :header="
          t(
            'workloadDistribution.fields.curriculum',
          )
        "
        style="
          min-width: 9rem
        "
      />

      <Column
        field="
          discipline_name
        "
        :header="
          t(
            'workloadDistribution.fields.discipline',
          )
        "
        style="
          min-width: 16rem
        "
      >
        <template
          #body="
            { data }
          "
        >
          <div
            class="
              discipline-cell
            "
          >
            <strong>
              {{
                data.discipline_name
              }}
            </strong>

            <small>
              {{
                data.discipline_code
              }}
            </small>
          </div>
        </template>
      </Column>

      <Column
        field="
          workload_type_name
        "
        :header="
          t(
            'workloadDistribution.fields.workloadType',
          )
        "
        style="
          min-width: 13rem
        "
      />

      <Column
        :header="
          t(
            'workloadDistribution.fields.scope',
          )
        "
        style="
          min-width: 9rem
        "
      >
        <template
          #body="
            { data }
          "
        >
          <Tag
            :value="
              scopeLabel(
                data,
              )
            "
            :severity="
              scopeSeverity(
                data,
              )
            "
          />
        </template>
      </Column>

      <Column
        field="
          total_hours
        "
        :header="
          t(
            'workloadDistribution.planned.total',
          )
        "
        style="
          min-width: 8rem
        "
      >
        <template
          #body="
            { data }
          "
        >
          {{
            asNumber(
              data.total_hours,
            ).toFixed(2)
          }}
        </template>
      </Column>

      <Column
        :header="
          t(
            'workloadDistribution.planned.distribution',
          )
        "
        style="
          min-width: 14rem
        "
      >
        <template
          #body="
            { data }
          "
        >
          <div
            class="
              distribution-progress
            "
          >
            <div
              class="
                distribution-progress__values
              "
            >
              <span>
                {{
                  asNumber(
                    data.distributed_hours,
                  ).toFixed(2)
                }}
              </span>

              <span>
                /
              </span>

              <span>
                {{
                  asNumber(
                    data.total_hours,
                  ).toFixed(2)
                }}
              </span>
            </div>

            <ProgressBar
              :value="
                distributionPercent(
                  data,
                )
              "
              :show-value="
                false
              "
              class="
                distribution-progress__bar
              "
            />
          </div>
        </template>
      </Column>

      <Column
        field="
          remaining_hours
        "
        :header="
          t(
            'workloadDistribution.planned.remaining',
          )
        "
        style="
          min-width: 8rem
        "
      >
        <template
          #body="
            { data }
          "
        >
          <Tag
            :value="
              asNumber(
                data.remaining_hours,
              ).toFixed(2)
            "
            :severity="
              statusSeverity(
                data,
              )
            "
          />
        </template>
      </Column>

      <Column
        v-if="
          canAssign
        "
        :header="
          t(
            'common.actions',
          )
        "
        frozen
        align-frozen="right"
        style="
          min-width: 8rem
        "
      >
        <template
          #body="
            { data }
          "
        >
          <Button
            :label="
              t(
                'workloadDistribution.planned.assign',
              )
            "
            icon="
              pi pi-user-plus
            "
            size="small"
            severity="success"
            outlined
            @click="
              emit(
                'assign',
                data,
              )
            "
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<style scoped>
.planned-distribution {
  display: grid;
  gap: 1rem;
}

.planned-distribution__header {
  display: flex;
  align-items: flex-start;
  justify-content:
    space-between;
  gap: 1rem;

  padding:
    1rem
    1rem
    0;
}

.planned-distribution__header h3 {
  margin: 0;

  font-size: 1rem;
}

.planned-distribution__header p {
  margin:
    0.25rem
    0
    0;

  color:
    var(--app-text-muted);

  font-size: 0.78rem;
}

.planned-distribution__empty {
  padding: 2rem;

  color:
    var(--app-text-muted);

  text-align: center;
}

.semester-cell,
.discipline-cell {
  display: grid;
  gap: 0.1rem;
}

.semester-cell small,
.discipline-cell small {
  color:
    var(--app-text-muted);

  font-size: 0.68rem;
}

.distribution-progress {
  display: grid;
  gap: 0.35rem;
}

.distribution-progress__values {
  display: flex;
  gap: 0.25rem;

  font-size: 0.72rem;
}

.distribution-progress__bar {
  height: 0.4rem;
}

:deep(
  .distribution-progress__bar
  .p-progressbar-value
) {
  transition:
    width
    0.2s
    ease;
}

@media (
  max-width: 900px
) {
  .planned-distribution__header {
    flex-direction:
      column;
  }
}
</style>
