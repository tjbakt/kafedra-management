import http from '@/api/http'
import { createCrudApi } from '@/api/crud'

import type {
  ApiListParams,
  PaginatedResponse,
} from '@/types/api'

import type {
  AcademicDegreeLookup,
  AcademicTitleLookup,
  AcademicYearOption,
  BulkCreatePayload,
  BulkCreateResult,
  DepartmentLookup,
  EmploymentLookup,
  MissingEmployment,
  RecommendedWorkload,
  StaffAcademicYearPayload,
  StaffAcademicYearRecord,
  WorkloadNorm,
  WorkloadNormPayload,
} from '@/modules/staff-academic-years/types'

export const staffAcademicYearsApi =
  createCrudApi<
    StaffAcademicYearRecord,
    StaffAcademicYearPayload,
    StaffAcademicYearPayload
  >(
    '/staff/employment-academic-years/',
  )

export const workloadNormsApi =
  createCrudApi<
    WorkloadNorm,
    WorkloadNormPayload,
    WorkloadNormPayload
  >('/staff/workload-norms/')

export async function getAcademicYears(): Promise<
  PaginatedResponse<AcademicYearOption>
> {
  const response =
    await http.get<
      PaginatedResponse<AcademicYearOption>
    >(
      '/academics/academic-years/',
      {
        params: {
          page_size: 100,
          ordering: '-start_year',
        },
      },
    )

  return response.data
}

export async function getEmployments(): Promise<
  PaginatedResponse<EmploymentLookup>
> {
  const response =
    await http.get<
      PaginatedResponse<EmploymentLookup>
    >(
      '/staff/employments/',
      {
        params: {
          page_size: 500,
          is_active: true,
          ordering:
            'staff_member__last_name',
        },
      },
    )

  return response.data
}

export async function getAcademicDegrees(): Promise<
  PaginatedResponse<AcademicDegreeLookup>
> {
  const response =
    await http.get<
      PaginatedResponse<AcademicDegreeLookup>
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
  PaginatedResponse<AcademicTitleLookup>
> {
  const response =
    await http.get<
      PaginatedResponse<AcademicTitleLookup>
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
          ordering: 'name_ru',
        },
      },
    )

  return response.data
}

export async function getRecommendedWorkload(
  employmentId: number,
  academicYearId: number,
): Promise<RecommendedWorkload> {
  const response =
    await http.get<RecommendedWorkload>(
      `/staff/employments/${employmentId}/recommended-workload/`,
      {
        params: {
          academic_year:
            academicYearId,
        },
      },
    )

  return response.data
}

export async function createMissingStaffRecords(
  payload: BulkCreatePayload,
): Promise<BulkCreateResult> {
  const response =
    await http.post<BulkCreateResult>(
      '/staff/employment-academic-years/create-missing/',
      payload,
    )

  return response.data
}

export async function getMissingStaffRecords(
  params: {
    academic_year: number
    department?: number | null
    page?: number
    page_size?: number
  },
): Promise<
  PaginatedResponse<MissingEmployment>
> {
  const response =
    await http.get<
      PaginatedResponse<MissingEmployment>
    >(
      '/staff/employment-academic-years/missing/',
      {
        params,
      },
    )

  return response.data
}

export async function listStaffAcademicYears(
  params: ApiListParams,
): Promise<
  PaginatedResponse<StaffAcademicYearRecord>
> {
  return staffAcademicYearsApi.list(
    params,
  )
}
