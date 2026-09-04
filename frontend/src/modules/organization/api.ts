import {
  createCrudApi,
} from '@/api/crud'

import http from '@/api/http'

import type {
  ApiListParams,
  PaginatedResponse,
} from '@/types/api'

import type {
  Faculty,
  FacultyPayload,
  University,
  UniversityOption,
  UniversityPayload,
} from '@/modules/organization/types'

export const universitiesApi =
  createCrudApi<
    University,
    UniversityPayload,
    UniversityPayload
  >(
    '/organizations/universities/',
  )

export const facultiesApi =
  createCrudApi<
    Faculty,
    FacultyPayload,
    FacultyPayload
  >(
    '/organizations/faculties/',
  )

export async function getUniversityOptions(
  params: ApiListParams = {},
): Promise<
  PaginatedResponse<UniversityOption>
> {
  const response =
    await http.get<
      PaginatedResponse<UniversityOption>
    >(
      '/organizations/universities/',
      {
        params: {
          page_size: 100,

          is_active: true,

          ordering: 'sort_order,name_ru',

          ...params,
        },
      },
    )

  return response.data
}
