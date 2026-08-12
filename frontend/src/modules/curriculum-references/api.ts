import http from '@/api/http'
import { createCrudApi } from '@/api/crud'

import type {
  PaginatedResponse,
} from '@/types/api'

import type {
  DepartmentLookup,
  Discipline,
  DisciplinePayload,
  WorkloadType,
  WorkloadTypePayload,
} from '@/modules/curriculum-references/types'

export const disciplinesApi =
  createCrudApi<
    Discipline,
    DisciplinePayload,
    DisciplinePayload
  >(
    '/curriculum/disciplines/',
  )

export const workloadTypesApi =
  createCrudApi<
    WorkloadType,
    WorkloadTypePayload,
    WorkloadTypePayload
  >(
    '/curriculum/workload-types/',
  )

export async function getDepartments(): Promise<
  PaginatedResponse<DepartmentLookup>
> {
  const response =
    await http.get<
      PaginatedResponse<DepartmentLookup>
    >(
      '/organizations/departments/',
      {
        params: {
          page_size: 500,
          is_active: true,
          ordering:
            'sort_order,name_ru',
        },
      },
    )

  return response.data
}
