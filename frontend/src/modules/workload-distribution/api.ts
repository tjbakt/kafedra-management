import http from '@/api/http'

import {
  createCrudApi,
} from '@/api/crud'

import {
  staffEmploymentsApi,
} from '@/modules/staff-employments/api'

import {
  staffAcademicYearsApi,
} from '@/modules/staff-academic-years/api'

import {
  plannedWorkloadsApi,
} from '@/modules/teaching-workload/api'

import type {
  StaffEmployment,
} from '@/modules/staff-employments/types'

import type {
  StaffAcademicYearRecord,
} from '@/modules/staff-academic-years/types'

import type {
  PlannedWorkload,
} from '@/modules/teaching-workload/types'

import type {
  PaginatedResponse,
} from '@/types/api'

import type {
  BulkDistributionResult,
  DistributionActionResponse,
  TeacherWorkloadSummary,
  WorkloadDistribution,
  WorkloadDistributionCreatePayload,
  WorkloadDistributionUpdatePayload,
  BulkAssignPlannedWorkloadPayload,
  BulkAssignPlannedWorkloadResult
} from '@/modules/workload-distribution/types'

export const workloadDistributionsApi =
  createCrudApi<
    WorkloadDistribution,
    WorkloadDistributionCreatePayload,
    WorkloadDistributionUpdatePayload
  >(
    '/workload/distributions/',
  )

export async function getPlannedWorkloads(): Promise<
  PaginatedResponse<PlannedWorkload>
> {
  return plannedWorkloadsApi.list({
    page_size: 500,
    ordering:
      '-academic_year__start_year,teaching_department',
  })
}

export async function getStaffEmployments(): Promise<
  PaginatedResponse<StaffEmployment>
> {
  return staffEmploymentsApi.list({
    page_size: 500,
    is_active: true,
    ordering:
      'staff_member__last_name',
  })
}

export async function getStaffAcademicYearRecords(): Promise<
  PaginatedResponse<StaffAcademicYearRecord>
> {
  return staffAcademicYearsApi.list({
    page_size: 500,
    is_active: true,
  })
}

export async function approveDistribution(
  id: number,
): Promise<DistributionActionResponse> {
  const response =
    await http.post<DistributionActionResponse>(
      `/workload/distributions/${id}/approve/`,
    )

  return response.data
}

export async function cancelDistribution(
  id: number,
  reason: string,
): Promise<DistributionActionResponse> {
  const response =
    await http.post<DistributionActionResponse>(
      `/workload/distributions/${id}/cancel/`,
      {
        reason,
      },
    )

  return response.data
}

export async function returnDistributionToDraft(
  id: number,
  reason: string,
): Promise<DistributionActionResponse> {
  const response =
    await http.post<DistributionActionResponse>(
      `/workload/distributions/${id}/return-to-draft/`,
      {
        reason,
      },
    )

  return response.data
}

// export async function getTeacherWorkloadSummary(
//   academicYear: number,
//   staffMember: number,
// ): Promise<TeacherWorkloadSummary[]> {
//   const response =
//     await http.get<
//       TeacherWorkloadSummary[]
//     >(
//       '/workload/distributions/teacher-summary/',
//       {
//         params: {
//           academic_year:
//             academicYear,
//
//           staff_member:
//             staffMember,
//         },
//       },
//     )
//
//   return response.data
// }

export async function approveSelectedDistributions(
  ids: number[],
): Promise<BulkDistributionResult> {
  const response =
    await http.post<
      BulkDistributionResult
    >(
      '/workload/distributions/approve-selected/',
      {
        ids,
      },
    )

  return response.data
}

export async function cancelSelectedDistributions(
  ids: number[],
  reason: string,
): Promise<BulkDistributionResult> {
  const response =
    await http.post<
      BulkDistributionResult
    >(
      '/workload/distributions/cancel-selected/',
      {
        ids,
        reason,
      },
    )

  return response.data
}

export async function restoreSelectedDistributions(
  ids: number[],
  reason: string,
): Promise<BulkDistributionResult> {
  const response =
    await http.post<
      BulkDistributionResult
    >(
      '/workload/distributions/restore-selected/',
      {
        ids,
        reason,
      },
    )

  return response.data
}

export async function returnSelectedDistributionsToDraft(
  ids: number[],
  reason: string,
): Promise<BulkDistributionResult> {
  const response =
    await http.post<
      BulkDistributionResult
    >(
      '/workload/distributions/return-selected-to-draft/',
      {
        ids,
        reason,
      },
    )

  return response.data
}

export async function assignSelectedPlannedWorkloads(
  payload:
    BulkAssignPlannedWorkloadPayload,
): Promise<
  BulkAssignPlannedWorkloadResult
> {
  const response =
    await http.post<
      BulkAssignPlannedWorkloadResult
    >(
      '/workload/distributions/assign-selected/',
      payload,
    )

  return response.data
}

export async function
getTeacherWorkloadSummary(
  academicYearId: number,
  departmentId: number,
): Promise<
  TeacherWorkloadSummary[]
> {
  const response =
    await http.get<
      TeacherWorkloadSummary[]
    >(
      '/workload/distributions/teacher-summary/',
      {
        params: {
          academic_year:
            academicYearId,

          department:
            departmentId,
        },
      },
    )

  return response.data
}
