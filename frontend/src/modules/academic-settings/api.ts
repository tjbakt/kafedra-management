import http from '@/api/http'
import {
  createCrudApi,
} from '@/api/crud'

import type {
  PaginatedResponse,
} from '@/types/api'

import type {
  AcademicYearCreditNorm,
  AcademicYearCreditNormPayload,
  AcademicYearWorkloadNorm,
  AcademicYearWorkloadNormPayload,
} from './types'

export const academicYearWorkloadNormsApi =
  createCrudApi<
    AcademicYearWorkloadNorm,
    AcademicYearWorkloadNormPayload,
    AcademicYearWorkloadNormPayload
  >(
    '/curriculum/academic-year-workload-norms/',
  )

export const academicYearCreditNormsApi =
  createCrudApi<
    AcademicYearCreditNorm,
    AcademicYearCreditNormPayload,
    AcademicYearCreditNormPayload
  >(
    '/curriculum/academic-year-credit-norms/',
  )

import type {
  AcademicSemester,
  AcademicSemesterPayload,
  AcademicYear,
  AcademicYearOperationResult,
  AcademicYearPayload,
  EducationDuration,
  EducationDurationPayload,
  EducationLevel,
  EducationLevelPayload,
  StudyForm,
  StudyFormPayload,
} from '@/modules/academic-settings/types'

export const academicYearsApi =
  createCrudApi<
    AcademicYear,
    AcademicYearPayload,
    AcademicYearPayload
  >(
    '/academics/academic-years/',
  )

export const educationLevelsApi =
  createCrudApi<
    EducationLevel,
    EducationLevelPayload,
    EducationLevelPayload
  >(
    '/academics/education-levels/',
  )

export const studyFormsApi =
  createCrudApi<
    StudyForm,
    StudyFormPayload,
    StudyFormPayload
  >(
    '/academics/study-forms/',
  )

export const educationDurationsApi =
  createCrudApi<
    EducationDuration,
    EducationDurationPayload,
    EducationDurationPayload
  >(
    '/academics/education-durations/',
  )

export const academicSemestersApi =
  createCrudApi<
    AcademicSemester,
    AcademicSemesterPayload,
    AcademicSemesterPayload
  >(
    '/academics/semesters/',
  )

export async function getAllAcademicYears(): Promise<
  PaginatedResponse<AcademicYear>
> {
  return academicYearsApi.list({
    page_size: 100,
    ordering: '-start_year',
  })
}

export async function getAllEducationLevels(): Promise<
  PaginatedResponse<EducationLevel>
> {
  return educationLevelsApi.list({
    page_size: 100,
    ordering: 'sort_order,name_ru',
  })
}

export async function getAllStudyForms(): Promise<
  PaginatedResponse<StudyForm>
> {
  return studyFormsApi.list({
    page_size: 100,
    ordering: 'sort_order,name_ru',
  })
}

export async function closeAcademicYear(
  id: number,
  comment: string,
): Promise<AcademicYearOperationResult> {
  const response =
    await http.post<
      AcademicYearOperationResult
    >(
      `/academics/academic-years/${id}/close/`,
      {
        comment:
          comment.trim(),
      },
    )

  return response.data
}

export async function reopenAcademicYear(
  id: number,
  reason: string,
): Promise<AcademicYearOperationResult> {
  const response =
    await http.post<
      AcademicYearOperationResult
    >(
      `/academics/academic-years/${id}/reopen/`,
      {
        reason:
          reason.trim(),
      },
    )

  return response.data
}
