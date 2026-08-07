import http from '@/api/http'
import { createCrudApi } from '@/api/crud'

import type {
  ApiListParams,
  PaginatedResponse,
} from '@/types/api'

import type {
  Department,
  DepartmentPayload,
  FacultyOption,
  UniversityOption,
} from '@/modules/departments/types'

export const departmentsApi =
  createCrudApi<
    Department,
    DepartmentPayload,
    DepartmentPayload
  >(
    '/organizations/departments/',
  )

export async function getFacultyOptions(
  params: ApiListParams = {},
): Promise<PaginatedResponse<FacultyOption>> {
  const response =
    await http.get<
      PaginatedResponse<FacultyOption>
    >(
      '/organizations/faculties/',
      {
        params: {
          page_size: 100,
          is_active: true,
          ...params,
        },
      },
    )

  return response.data
}

export async function getUniversityOptions(): Promise<
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
          ordering: 'name_ru',
        },
      },
    )

  return response.data
}
