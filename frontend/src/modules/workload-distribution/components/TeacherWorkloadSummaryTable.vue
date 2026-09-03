<script setup lang="ts">
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import Tag from 'primevue/tag'

import {
  computed,
} from 'vue'

import {
  useI18n,
} from 'vue-i18n'

import type {
  TeacherWorkloadSummary,
} from '../types'

const props =
  defineProps<{
    items:
      TeacherWorkloadSummary[]

    loading?: boolean
  }>()

const { t } =
  useI18n()

const rows =
  computed(
    () =>
      props.items,
  )

function statusLabel(
  status:
    TeacherWorkloadSummary[
      'status'
    ],
): string {
  return t(
    `workloadDistribution.teacherLoad.status.${status}`,
  )
}

function statusSeverity(
  status:
    TeacherWorkloadSummary[
      'status'
    ],
): 'success' | 'warn' | 'danger' {
  if (
    status === 'FULL'
  ) {
    return 'success'
  }

  if (
    status === 'OVERLOAD'
  ) {
    return 'danger'
  }

  return 'warn'
}
</script>

<template>
  <DataTable
    :value="rows"
    :loading="loading"
    data-key="
      staff_employment
    "
    striped-rows
    scrollable
    responsive-layout="scroll"
  >
    <template #empty>
      <div
        class="
          p-4
          text-center
        "
      >
        {{
          t(
            'workloadDistribution.teacherLoad.empty',
          )
        }}
      </div>
    </template>

    <Column
      field="
        staff_member_name
      "
      :header="
        t(
          'workloadDistribution.teacherLoad.teacher',
        )
      "
      frozen
    />

    <Column
      field="
        annual_norm_hours
      "
      :header="
        t(
          'workloadDistribution.teacherLoad.norm',
        )
      "
    />

    <Column
      field="
        approved_hours
      "
      :header="
        t(
          'workloadDistribution.teacherLoad.approved',
        )
      "
    />

    <Column
      field="
        draft_hours
      "
      :header="
        t(
          'workloadDistribution.teacherLoad.draft',
        )
      "
    />

    <Column
      field="
        remaining_hours
      "
      :header="
        t(
          'workloadDistribution.teacherLoad.remaining',
        )
      "
    />

    <Column
      field="
        completion_percent
      "
      :header="
        t(
          'workloadDistribution.teacherLoad.percent',
        )
      "
    >
      <template
        #body="
          { data }
        "
      >
        {{
          Number(
            data.completion_percent,
          ).toFixed(1)
        }}%
      </template>
    </Column>

    <Column
      :header="
        t(
          'workloadDistribution.teacherLoad.status.title',
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
            statusLabel(
              data.status,
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
</template>
