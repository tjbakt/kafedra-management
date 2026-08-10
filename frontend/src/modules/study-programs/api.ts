import http from '@/api/http'
import {
  createCrudApi,
} from '@/api/crud'

import type {
  PaginatedResponse,
} from '@/types/api'

import type {
  DepartmentLookup,
  EducationLevelLookup,
  StudyProgram,
  StudyProgramPayload,
  UniversityLookup,
} from '@/modules/study-programs/types'

export const studyProgramsApi =
  createCrudApi<
    StudyProgram,
    StudyProgramPayload,
    StudyProgramPayload
  >(
    '/academics/study-programs/',
  )

export async function getUniversities(): Promise<
  PaginatedResponse<UniversityLookup>
> {
  const response =
    await http.get<
      PaginatedResponse<UniversityLookup>
    >(
      '/organizations/universities/',
      {
        params: {
          page_size: 200,
          is_active: true,
          ordering: 'name_ru',
        },
      },
    )

  return response.data
}

export async function getEducationLevels(): Promise<
  PaginatedResponse<EducationLevelLookup>
> {
  const response =
    await http.get<
      PaginatedResponse<EducationLevelLookup>
    >(
      '/academics/education-levels/',
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
          ordering:
            'sort_order,name_ru',
        },
      },
    )

  return response.data
}
