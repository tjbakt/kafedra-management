import http from '@/api/http'
import { createCrudApi } from '@/api/crud'

import type {
  PaginatedResponse,
} from '@/types/api'

import type {
  AcademicDegreeOption,
  AcademicTitleOption,
  StaffMember,
  StaffMemberPayload,
} from '@/modules/staff/types'

export const staffMembersApi =
  createCrudApi<
    StaffMember,
    StaffMemberPayload,
    StaffMemberPayload
  >('/staff/members/')

export async function getAcademicDegrees(): Promise<
  PaginatedResponse<AcademicDegreeOption>
> {
  const response =
    await http.get<
      PaginatedResponse<AcademicDegreeOption>
    >(
      '/staff/academic-degrees/',
      {
        params: {
          page_size: 100,
          is_active: true,
          ordering:
            'sort_order,name_ru',
        },
      },
    )

  return response.data
}

export async function getAcademicTitles(): Promise<
  PaginatedResponse<AcademicTitleOption>
> {
  const response =
    await http.get<
      PaginatedResponse<AcademicTitleOption>
    >(
      '/staff/academic-titles/',
      {
        params: {
          page_size: 100,
          is_active: true,
          ordering:
            'sort_order,name_ru',
        },
      },
    )

  return response.data
}
