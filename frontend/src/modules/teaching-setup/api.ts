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
  CurriculumLookup,
  GroupCurriculumAssignment,
  GroupCurriculumPayload,
  GroupSemester,
  GroupSemesterPayload,
  StudentGroupLookup,
} from '@/modules/teaching-setup/types'

export const groupCurriculaApi =
  createCrudApi<
    GroupCurriculumAssignment,
    GroupCurriculumPayload,
    GroupCurriculumPayload
  >(
    '/teaching/group-curricula/',
  )

export const groupSemestersApi =
  createCrudApi<
    GroupSemester,
    GroupSemesterPayload,
    GroupSemesterPayload
  >(
    '/teaching/group-semesters/',
  )

export async function getStudentGroups(): Promise<
  PaginatedResponse<StudentGroupLookup>
> {
  const response =
    await http.get<
      PaginatedResponse<StudentGroupLookup>
    >(
      '/academics/student-groups/',
      {
        params: {
          page_size: 500,
          is_active: true,
          ordering: 'code',
        },
      },
    )

  return response.data
}

export async function getCurricula(): Promise<
  PaginatedResponse<CurriculumLookup>
> {
  const response =
    await http.get<
      PaginatedResponse<CurriculumLookup>
    >(
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
