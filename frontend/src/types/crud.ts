import type { ApiListParams } from '@/types/api'

export type CrudId = number | string

export type CrudSortOrder = 1 | -1 | 0 | null

export interface CrudColumn<T = Record<string, unknown>> {
  field: keyof T | string
  header: string

  sortable?: boolean
  sortField?: string

  width?: string
  minWidth?: string

  align?: 'left' | 'center' | 'right'

  bodySlot?: string
  headerClass?: string
  bodyClass?: string
}

export interface CrudPageEvent {
  first: number
  rows: number
  page: number
  pageCount: number
}

export interface CrudSortEvent {
  sortField?: string | ((item: unknown) => string)
  sortOrder?: CrudSortOrder
}

export interface CrudQueryState {
  page: number
  pageSize: number
  search: string
  ordering: string
  filters: Record<
    string,
    string | number | boolean | null | undefined
  >
}

export interface CrudListOptions {
  initialPageSize?: number
  initialOrdering?: string
  initialSearch?: string
  initialFilters?: Record<
    string,
    string | number | boolean | null | undefined
  >
  debounceMs?: number
}

export interface CrudListRequestContext {
  params: ApiListParams
}

export interface CrudRowAction<T> {
  key: string
  label: string
  icon?: string

  severity?:
    | 'secondary'
    | 'success'
    | 'info'
    | 'warn'
    | 'danger'
    | 'contrast'

  visible?: (row: T) => boolean
  disabled?: (row: T) => boolean

  command: (row: T) => void | Promise<void>
}
