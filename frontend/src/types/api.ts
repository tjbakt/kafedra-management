export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiListParams {
  page?: number
  page_size?: number
  search?: string
  ordering?: string

  [key: string]:
    | string
    | number
    | boolean
    | null
    | undefined
}

export interface ApiSuccessResponse<T = unknown> {
  data: T
  message?: string
}

export interface ApiDeleteResponse {
  detail?: string
}
