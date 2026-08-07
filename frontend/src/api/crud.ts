import type {
  AxiosInstance,
} from 'axios'

import http from '@/api/http'

import type {
  ApiDeleteResponse,
  ApiListParams,
  PaginatedResponse,
} from '@/types/api'

import type {
  CrudId,
} from '@/types/crud'

import {
  cleanQueryParams,
} from '@/utils/query'

export interface CrudApi<
  TRead,
  TCreate,
  TUpdate,
> {
  list(
    params?: ApiListParams,
  ): Promise<PaginatedResponse<TRead>>

  retrieve(
    id: CrudId,
  ): Promise<TRead>

  create(
    payload: TCreate,
  ): Promise<TRead>

  update(
    id: CrudId,
    payload: TUpdate,
  ): Promise<TRead>

  partialUpdate(
    id: CrudId,
    payload: Partial<TUpdate>,
  ): Promise<TRead>

  remove(
    id: CrudId,
  ): Promise<ApiDeleteResponse | void>
}

export function createCrudApi<
  TRead,
  TCreate,
  TUpdate = TCreate,
>(
  endpoint: string,
  client: AxiosInstance = http,
): CrudApi<
  TRead,
  TCreate,
  TUpdate
> {
  const normalizedEndpoint =
    endpoint.endsWith('/')
      ? endpoint
      : `${endpoint}/`

  function detailUrl(
    id: CrudId,
  ): string {
    return `${normalizedEndpoint}${id}/`
  }

  return {
    async list(
      params: ApiListParams = {},
    ): Promise<
      PaginatedResponse<TRead>
    > {
      const response =
        await client.get<
          PaginatedResponse<TRead>
        >(
          normalizedEndpoint,
          {
            params:
              cleanQueryParams(params),
          },
        )

      return response.data
    },

    async retrieve(
      id: CrudId,
    ): Promise<TRead> {
      const response =
        await client.get<TRead>(
          detailUrl(id),
        )

      return response.data
    },

    async create(
      payload: TCreate,
    ): Promise<TRead> {
      const response =
        await client.post<TRead>(
          normalizedEndpoint,
          payload,
        )

      return response.data
    },

    async update(
      id: CrudId,
      payload: TUpdate,
    ): Promise<TRead> {
      const response =
        await client.put<TRead>(
          detailUrl(id),
          payload,
        )

      return response.data
    },

    async partialUpdate(
      id: CrudId,
      payload: Partial<TUpdate>,
    ): Promise<TRead> {
      const response =
        await client.patch<TRead>(
          detailUrl(id),
          payload,
        )

      return response.data
    },

    async remove(
      id: CrudId,
    ): Promise<
      ApiDeleteResponse | void
    > {
      const response =
        await client.delete<
          ApiDeleteResponse
        >(detailUrl(id))

      return response.data
    },
  }
}
