import {
  computed,
  ref,
  watch,
  type Ref,
} from 'vue'

import {
  normalizeApiError,
} from '@/utils/api-errors'

import {
  buildOrdering,
} from '@/utils/query'

import {
  useDebouncedValue,
} from '@/composables/useDebouncedValue'

import type {
  ApiListParams,
  PaginatedResponse,
} from '@/types/api'

import type {
  CrudListOptions,
  CrudPageEvent,
  CrudQueryState,
  CrudSortEvent,
} from '@/types/crud'

type ListLoader<T> = (
  params: ApiListParams,
) => Promise<PaginatedResponse<T>>

export function useCrudList<T>(
  loader: ListLoader<T>,
  options: CrudListOptions = {},
) {
  const items = ref<T[]>([]) as Ref<T[]>

  const totalRecords = ref(0)
  const loading = ref(false)
  const initialized = ref(false)
  const error = ref('')

  const query = ref<CrudQueryState>({
    page: 1,

    pageSize:
      options.initialPageSize ?? 20,

    search:
      options.initialSearch ?? '',

    ordering:
      options.initialOrdering ?? '',

    filters: {
      ...options.initialFilters,
    },
  })

  const searchInput = ref(
    query.value.search,
  )

  const debouncedSearch =
    useDebouncedValue(
      searchInput,
      options.debounceMs ?? 400,
    )

  const first = computed(
    () =>
      (query.value.page - 1) *
      query.value.pageSize,
  )

  const hasData = computed(
    () => items.value.length > 0,
  )

  const isEmpty = computed(
    () =>
      initialized.value &&
      !loading.value &&
      items.value.length === 0 &&
      !error.value,
  )

  const requestParams = computed<
    ApiListParams
  >(() => ({
    page: query.value.page,
    page_size:
      query.value.pageSize,
    search:
      query.value.search || undefined,
    ordering:
      query.value.ordering || undefined,

    ...query.value.filters,
  }))

  async function load(): Promise<void> {
    loading.value = true
    error.value = ''

    try {
      const response =
        await loader(
          requestParams.value,
        )

      items.value =
        response.results

      totalRecords.value =
        response.count

      const maxPage =
        Math.max(
          1,
          Math.ceil(
            response.count /
              query.value.pageSize,
          ),
        )

      if (
        query.value.page >
        maxPage
      ) {
        query.value.page =
          maxPage

        await load()
        return
      }
    } catch (loadError) {
      const normalized =
        normalizeApiError(loadError)

      error.value =
        normalized.message

      items.value = []
      totalRecords.value = 0
    } finally {
      loading.value = false
      initialized.value = true
    }
  }

  async function refresh(): Promise<void> {
    await load()
  }

  async function reset(): Promise<void> {
    query.value = {
      page: 1,
      pageSize:
        options.initialPageSize ?? 20,
      search:
        options.initialSearch ?? '',
      ordering:
        options.initialOrdering ?? '',
      filters: {
        ...options.initialFilters,
      },
    }

    searchInput.value =
      query.value.search

    await load()
  }

  function handlePage(
    event: CrudPageEvent,
  ): void {
    query.value.page =
      event.page + 1

    query.value.pageSize =
      event.rows

    void load()
  }

  function handleSort(
    event: CrudSortEvent,
  ): void {
    const field =
      typeof event.sortField === 'string'
        ? event.sortField
        : undefined

    query.value.ordering =
      buildOrdering(
        field,
        event.sortOrder,
      )

    query.value.page = 1

    void load()
  }

  function setFilter(
    key: string,
    value:
      | string
      | number
      | boolean
      | null
      | undefined,
  ): void {
    query.value.filters = {
      ...query.value.filters,
      [key]: value,
    }

    query.value.page = 1
  }

  function removeFilter(
    key: string,
  ): void {
    const filters = {
      ...query.value.filters,
    }

    delete filters[key]

    query.value.filters =
      filters

    query.value.page = 1
  }

  function clearFilters(): void {
    query.value.filters = {}
    query.value.page = 1
  }

  watch(
    debouncedSearch,
    (search) => {
      query.value.search =
        search.trim()

      query.value.page = 1

      void load()
    },
  )

  return {
    items,
    totalRecords,
    loading,
    initialized,
    error,

    query,
    searchInput,

    first,
    hasData,
    isEmpty,
    requestParams,

    load,
    refresh,
    reset,

    handlePage,
    handleSort,

    setFilter,
    removeFilter,
    clearFilters,
  }
}
