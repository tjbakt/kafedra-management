import http from '@/api/http'
import { createCrudApi } from '@/api/crud'

import type {
  PaginatedResponse,
} from '@/types/api'

import type {
  AcademicDegree,
  AcademicDegreePayload,
  AcademicTitle,
  AcademicTitlePayload,
  StaffPosition,
  StaffPositionPayload,
} from '@/modules/staff-references/types'

export const staffPositionsApi =
  createCrudApi<
    StaffPosition,
    StaffPositionPayload,
    StaffPositionPayload
  >(
    '/staff/positions/',
  )

export const academicDegreesApi =
  createCrudApi<
    AcademicDegree,
    AcademicDegreePayload,
    AcademicDegreePayload
  >(
    '/staff/academic-degrees/',
  )

export const academicTitlesApi =
  createCrudApi<
    AcademicTitle,
    AcademicTitlePayload,
    AcademicTitlePayload
  >(
    '/staff/academic-titles/',
  )

export async function getStaffPositions(): Promise<
  PaginatedResponse<StaffPosition>
> {
  const response =
    await http.get<
      PaginatedResponse<StaffPosition>
    >(
      '/staff/positions/',
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

export async function getAllAcademicDegrees(): Promise<
  PaginatedResponse<AcademicDegree>
> {
  const response =
    await http.get<
      PaginatedResponse<AcademicDegree>
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

export async function getAllAcademicTitles(): Promise<
  PaginatedResponse<AcademicTitle>
> {
  const response =
    await http.get<
      PaginatedResponse<AcademicTitle>
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
