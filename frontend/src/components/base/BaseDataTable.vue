<script
  setup
  lang="ts"
  generic="T extends Record<string, unknown>"
>
import Button from 'primevue/button'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import Message from 'primevue/message'
import Skeleton from 'primevue/skeleton'

import { useI18n } from 'vue-i18n'

import BaseEmptyState from '@/components/base/BaseEmptyState.vue'

import type {
  CrudColumn,
  CrudPageEvent,
  CrudSortEvent,
} from '@/types/crud'

withDefaults(
  defineProps<{
    value: T[]
    columns: CrudColumn<T>[]

    dataKey?: string

    loading?: boolean
    error?: string

    lazy?: boolean
    paginator?: boolean

    first?: number
    rows?: number
    totalRecords?: number

    rowsPerPageOptions?: number[]

    stripedRows?: boolean
    removableSort?: boolean

    emptyTitle?: string
    emptyDescription?: string

    showRowActions?: boolean
    selectable?: boolean
    selection?: T[]
  }>(),
  {
    dataKey: 'id',

    loading: false,
    error: '',

    lazy: true,
    paginator: true,

    first: 0,
    rows: 20,
    totalRecords: 0,

    rowsPerPageOptions: () => [
      10,
      20,
      50,
      100,
    ],

    stripedRows: true,
    removableSort: true,

    emptyTitle: '',
    emptyDescription: '',

    showRowActions: false,
    selectable: false,
    selection: () => [],
  },
)

const emit = defineEmits<{
  page: [event: CrudPageEvent]
  sort: [event: CrudSortEvent]
  retry: []
  rowClick: [row: T]
  'update:selection': [value: T[],
  ]
}>()

const { t } = useI18n()

function resolveField(
  row: T,
  path: string,
): unknown {
  return path
    .split('.')
    .reduce<unknown>(
      (current, key) => {
        if (
          current &&
          typeof current === 'object' &&
          key in current
        ) {
          return (
            current as Record<
              string,
              unknown
            >
          )[key]
        }

        return undefined
      },
      row,
    )
}

function columnStyle(
  column: CrudColumn<T>,
): Record<string, string> {
  const style:
    Record<string, string> = {}

  if (column.width) {
    style.width = column.width
  }

  if (column.minWidth) {
    style.minWidth =
      column.minWidth
  }

  if (column.align) {
    style.textAlign =
      column.align
  }

  return style
}

function onPage(event: {
  first: number
  rows: number
  page?: number
  pageCount?: number
}): void {
  emit('page', {
    first: event.first,
    rows: event.rows,
    page:
      event.page ??
      Math.floor(
        event.first /
          event.rows,
      ),
    pageCount:
      event.pageCount ?? 0,
  })
}

function onSort(event: {
  sortField?:
    | string
    | ((item: unknown) => string)
  sortOrder?:
    | 1
    | -1
    | 0
    | null
}): void {
  emit('sort', {
    sortField:
      event.sortField,

    sortOrder:
      event.sortOrder,
  })
}
</script>

<template>
  <div class="base-data-table">
    <Message
      v-if="error"
      severity="error"
      :closable="false"
      class="base-data-table__error"
    >
      <div
        class="base-data-table__error-content"
      >
        <span>{{ error }}</span>

        <Button
          :label="
            t('common.refresh')
          "
          icon="pi pi-refresh"
          size="small"
          severity="danger"
          text
          @click="emit('retry')"
        />
      </div>
    </Message>

    <DataTable
      v-if="!error"
      :value="value"
      :data-key="dataKey"
      :lazy="lazy"
      :paginator="paginator"
      :first="first"
      :rows="rows"
      :total-records="totalRecords"
      :rows-per-page-options="rowsPerPageOptions"
      :loading="loading"
      :striped-rows="stripedRows"
      :removable-sort="removableSort"
      :selection="selection"
      paginator-template="
        FirstPageLink
        PrevPageLink
        PageLinks
        NextPageLink
        LastPageLink
        RowsPerPageDropdown
        CurrentPageReport
      "
      :current-page-report-template="t('crud.paginationReport',)"
      responsive-layout="scroll"
      class="base-data-table__table"
      @page="onPage"
      @sort="onSort"
      @row-click="
        emit(
          'rowClick',
          $event.data as T,
        )
      "
      @update:selection="
        emit(
          'update:selection',
          $event as T[],
        )
      "
    >
      <template #loading>
        <div
          class="base-data-table__loading"
        >
          <Skeleton
            v-for="index in 5"
            :key="index"
            height="2.5rem"
          />
        </div>
      </template>

      <template #empty>
        <BaseEmptyState
          :title="
            emptyTitle ||
            t('crud.emptyTitle')
          "
          :description="
            emptyDescription ||
            t(
              'crud.emptyDescription',
            )
          "
        >
          <template
            v-if="$slots.emptyActions"
            #actions
          >
            <slot name="emptyActions" />
          </template>
        </BaseEmptyState>
      </template>

      <Column
        v-if="selectable"
        selection-mode="multiple"
        header-style="width: 3rem"
        body-style="width: 3rem"
      />
      <Column
        v-for="column in columns"
        :key="String(column.field)"
        :field="String(column.field)"
        :header="column.header"
        :sortable="column.sortable"
        :sort-field="column.sortField"
        :header-class="column.headerClass"
        :body-class="column.bodyClass"
        :style="columnStyle(column)"
      >
        <template #body="{ data }">
          <slot
            v-if="column.bodySlot"
            :name="
              column.bodySlot
            "
            :row="data as T"
            :value="
              resolveField(
                data as T,
                String(
                  column.field,
                ),
              )
            "
            :column="column"
          />

          <template v-else>
            {{
              resolveField(
                data as T,
                String(
                  column.field,
                ),
              )
            }}
          </template>
        </template>
      </Column>

      <Column
        v-if="
          showRowActions ||
          $slots.actions
        "
        :header="
          t('common.actions')
        "
        frozen
        align-frozen="right"
        style="
          width: 8rem;
          text-align: center;
        "
      >
        <template #body="{ data }">
          <div
            class="base-data-table__actions"
          >
            <slot
              name="actions"
              :row="data as T"
            />
          </div>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<style scoped>
.base-data-table {
  width: 100%;
}

.base-data-table__error {
  margin: 0;
}

.base-data-table__error-content {
  display: flex;
  align-items: center;
  justify-content:
    space-between;
  gap: 1rem;
}

.base-data-table__loading {
  display: grid;
  gap: 0.65rem;
  padding: 1rem;
}

.base-data-table__actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

:deep(.p-datatable) {
  border:
    1px solid
    var(--app-border-color);
  border-radius:
    var(--app-radius-lg);
  overflow: hidden;
  background:
    var(--app-surface);
}

:deep(.p-datatable-header-cell) {
  white-space: nowrap;
}

:deep(.p-datatable-tbody > tr) {
  cursor: default;
}

:deep(.p-paginator) {
  border-top:
    1px solid
    var(--app-border-color);
  border-radius: 0;
}

@media (max-width: 767px) {
  .base-data-table__error-content {
    align-items:
      flex-start;
    flex-direction: column;
  }
}
</style>
