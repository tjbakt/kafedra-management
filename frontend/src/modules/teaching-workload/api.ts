import http from '@/api/http'

import {
  createCrudApi,
} from '@/api/crud'

import type {
  PaginatedResponse,
} from '@/types/api'

import type {
  AcademicSemesterLookup,
  AcademicYearLookup,
  CalculateAllResponse,
  CalculateStreamResponse,
  GroupSemester,
  PlannedWorkload,
  PlannedWorkloadSummary,
  TeachingStream,
  TeachingStreamGroup,
  TeachingStreamGroupPayload,
  TeachingStreamPayload,
} from '@/modules/teaching-workload/types'

export const teachingStreamsApi =
  createCrudApi<
    TeachingStream,
    TeachingStreamPayload,
    TeachingStreamPayload
  >(
    '/teaching/streams/',
  )

export const teachingStreamGroupsApi =
  createCrudApi<
    TeachingStreamGroup,
    TeachingStreamGroupPayload,
    TeachingStreamGroupPayload
  >(
    '/teaching/stream-groups/',
  )

export const plannedWorkloadsApi =
  createCrudApi<
    PlannedWorkload,
    never,
    never
  >(
    '/teaching/planned-workloads/',
  )

export async function calculateStream(
  streamId: number,
): Promise<CalculateStreamResponse> {
  const response =
    await http.post<CalculateStreamResponse>(
      `/teaching/streams/${streamId}/calculate/`,
    )

  return response.data
}

export async function calculateAllStreams(
  params?: Record<string, unknown>,
): Promise<CalculateAllResponse> {
  const response =
    await http.post<CalculateAllResponse>(
      '/teaching/streams/calculate-all/',
      undefined,
      {
        params,
      },
    )

  return response.data
}

export async function getPlannedWorkloadSummary(
  params?: Record<string, unknown>,
): Promise<PlannedWorkloadSummary> {
  const response =
    await http.get<PlannedWorkloadSummary>(
      '/teaching/planned-workloads/summary/',
      {
        params,
      },
    )

  return response.data
}

export async function getAcademicYears(): Promise<
  PaginatedResponse<AcademicYearLookup>
> {
  const response =
    await http.get<
      PaginatedResponse<AcademicYearLookup>
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

export async function getAcademicSemesters(): Promise<
  PaginatedResponse<AcademicSemesterLookup>
> {
  const response =
    await http.get<
      PaginatedResponse<AcademicSemesterLookup>
    >(
      '/academics/semesters/',
      {
        params: {
          page_size: 200,
          ordering: '-start_date',
        },
      },
    )

  return response.data
}

export async function getCurricula() {
  const response =
    await http.get(
      '/curriculum/curricula/',
      {
        params: {
          page_size: 500,
          is_active: true,
          ordering:
            '-effective_academic_year__start_year,code,-version',
        },
      },
    )

  return response.data
}

export async function getGroupSemesters(): Promise<
  PaginatedResponse<GroupSemester>
> {
  const response =
    await http.get<
      PaginatedResponse<GroupSemester>
    >(
      '/teaching/group-semesters/',
      {
        params: {
          page_size: 1000,
          is_active: true,
          ordering:
            '-academic_year__start_year,semester_number',
        },
      },
    )

  return response.data
}
