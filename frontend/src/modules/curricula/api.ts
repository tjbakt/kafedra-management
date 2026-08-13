import http from '@/api/http'
import {
  createCrudApi,
} from '@/api/crud'

import type {
  PaginatedResponse,
} from '@/types/api'

import type {
  AcademicYearLookup,
  Curriculum,
  CurriculumPayload,
  EducationDurationLookup,
  StudyFormLookup,
  StudyProgramLookup,
  UniversityLookup,
} from '@/modules/curricula/types'

export const curriculaApi =
  createCrudApi<
    Curriculum,
    CurriculumPayload,
    CurriculumPayload
  >(
    '/curriculum/curricula/',
  )

export async function getStudyPrograms(): Promise<
  PaginatedResponse<StudyProgramLookup>
> {
  const response =
    await http.get<
      PaginatedResponse<StudyProgramLookup>
    >(
      '/academics/study-programs/',
      {
        params: {
          page_size: 500,
          is_active: true,
          ordering:
            'sort_order,code',
        },
      },
    )

  return response.data
}

export async function getStudyForms(): Promise<
  PaginatedResponse<StudyFormLookup>
> {
  const response =
    await http.get<
      PaginatedResponse<StudyFormLookup>
    >(
      '/academics/study-forms/',
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
          ordering:
            '-start_year',
        },
      },
    )

  return response.data
}

export async function getEducationDurations(): Promise<
  PaginatedResponse<EducationDurationLookup>
> {
  const response =
    await http.get<
      PaginatedResponse<EducationDurationLookup>
    >(
      '/academics/education-durations/',
      {
        params: {
          page_size: 200,
          is_active: true,
        },
      },
    )

  return response.data
}

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
