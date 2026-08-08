import http from '@/api/http'
import { createCrudApi } from '@/api/crud'

import type {
  PaginatedResponse,
} from '@/types/api'

import type {
  DepartmentLookup,
  StaffEmployment,
  StaffEmploymentPayload,
  StaffMemberLookup,
  StaffPositionLookup,
} from '@/modules/staff-employments/types'

export const staffEmploymentsApi =
  createCrudApi<
    StaffEmployment,
    StaffEmploymentPayload,
    StaffEmploymentPayload
  >('/staff/employments/')

export async function getStaffMembersLookup(): Promise<
  PaginatedResponse<StaffMemberLookup>
> {
  const response =
    await http.get<
      PaginatedResponse<StaffMemberLookup>
    >(
      '/staff/members/',
      {
        params: {
          page_size: 500,
          is_active: true,
          ordering:
            'last_name,first_name',
        },
      },
    )

  return response.data
}

export async function getDepartmentsLookup(): Promise<
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
          ordering: 'name_ru',
        },
      },
    )

  return response.data
}

export async function getPositionsLookup(): Promise<
  PaginatedResponse<StaffPositionLookup>
> {
  const response =
    await http.get<
      PaginatedResponse<StaffPositionLookup>
    >(
      '/staff/positions/',
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
