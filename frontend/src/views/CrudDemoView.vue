<script setup lang="ts">
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

import BaseCard from '@/components/base/BaseCard.vue'
import BaseDataTable from '@/components/base/BaseDataTable.vue'
import BasePageHeader from '@/components/base/BasePageHeader.vue'
import BaseToolbar from '@/components/base/BaseToolbar.vue'

import type {
  ApiListParams,
  PaginatedResponse,
} from '@/types/api'

import type {
  CrudColumn,
} from '@/types/crud'

import {
  useCrudList,
} from '@/composables/useCrudList'

interface DemoRecord
  extends Record<
    string,
    unknown
  > {
  id: number
  code: string
  name: string
  active: boolean
}

const { t } = useI18n()

const sourceData: DemoRecord[] =
  Array.from(
    {
      length: 137,
    },
    (_, index) => ({
      id: index + 1,

      code:
        `DEMO-${String(
          index + 1,
        ).padStart(3, '0')}`,

      name:
        `Demo record ${
          index + 1
        }`,

      active:
        index % 4 !== 0,
    }),
  )

async function demoLoader(
  params: ApiListParams,
): Promise<
  PaginatedResponse<DemoRecord>
> {
  await new Promise(
    (resolve) =>
      window.setTimeout(
        resolve,
        250,
      ),
  )

  const search =
    String(
      params.search ?? '',
    )
      .trim()
      .toLowerCase()

  let result = [
    ...sourceData,
  ]

  if (search) {
    result = result.filter(
      (item) =>
        item.name
          .toLowerCase()
          .includes(search) ||
        item.code
          .toLowerCase()
          .includes(search),
    )
  }

  const ordering =
    String(
      params.ordering ?? '',
    )

  if (ordering) {
    const descending =
      ordering.startsWith('-')

    const field =
      descending
        ? ordering.slice(1)
        : ordering

    result.sort((a, b) => {
      const aValue =
        String(
          a[field] ?? '',
        )

      const bValue =
        String(
          b[field] ?? '',
        )

      const compared =
        aValue.localeCompare(
          bValue,
        )

      return descending
        ? -compared
        : compared
    })
  }

  const page =
    Number(params.page ?? 1)

  const pageSize =
    Number(
      params.page_size ?? 20,
    )

  const start =
    (page - 1) *
    pageSize

  return {
    count:
      result.length,

    next:
      start + pageSize <
      result.length
        ? 'next'
        : null,

    previous:
      page > 1
        ? 'previous'
        : null,

    results:
      result.slice(
        start,
        start + pageSize,
      ),
  }
}

const {
  items,
  totalRecords,
  loading,
  error,
  query,
  searchInput,
  first,
  load,
  refresh,
  reset,
  handlePage,
  handleSort,
} = useCrudList<DemoRecord>(
  demoLoader,
  {
    initialPageSize: 20,
    initialOrdering: 'name',
  },
)

const columns = computed<
  CrudColumn<DemoRecord>[]
>(() => [
  {
    field: 'id',
    header: 'ID',
    sortable: true,
    width: '6rem',
  },

  {
    field: 'code',
    header: 'Code',
    sortable: true,
    minWidth: '10rem',
  },

  {
    field: 'name',
    header: 'Name',
    sortable: true,
    minWidth: '16rem',
  },

  {
    field: 'active',
    header: 'Status',
    sortable: true,
    bodySlot: 'active',
    width: '8rem',
    align: 'center',
  },
])

onMounted(() => {
  void load()
})
</script>

<template>
  <div class="crud-demo">
    <BasePageHeader
      title="CRUD Infrastructure"
      description="Проверка server-side pagination, поиска, сортировки и базовых действий."
      icon="pi pi-database"
    />

    <BaseToolbar
      v-model:search="searchInput"
      :show-create="false"
      :loading="loading"
      @refresh="refresh"
      @reset="reset"
    />

    <BaseCard :padding="false">
      <BaseDataTable
        :value="items"
        :columns="columns"
        :loading="loading"
        :error="error"
        :first="first"
        :rows="query.pageSize"
        :total-records="
      totalRecords
    "
        show-row-actions
        @page="handlePage"
        @sort="handleSort"
        @retry="refresh"
      >
        <template
          #active="{ value }"
        >
          <Tag
            :value="
              value
                ? t('common.yes')
                : t('common.no')
            "
            :severity="
              value
                ? 'success'
                : 'secondary'
            "
          />
        </template>

        <template
          #actions="{ row }"
        >
          <Button
            v-tooltip.bottom="
              t('common.view')
            "
            icon="pi pi-eye"
            text
            rounded
            severity="secondary"
            @click="
              console.log(row)
            "
          />

          <Button
            v-tooltip.bottom="
              t('common.edit')
            "
            icon="pi pi-pencil"
            text
            rounded
            @click="
              console.log(row)
            "
          />

          <Button
            v-tooltip.bottom="
              t('common.delete')
            "
            icon="pi pi-trash"
            text
            rounded
            severity="danger"
            @click="
              console.log(row)
            "
          />
        </template>
      </BaseDataTable>
    </BaseCard>
  </div>
</template>

<style scoped>
.crud-demo {
  display: grid;
  gap: 1rem;
}
</style>
