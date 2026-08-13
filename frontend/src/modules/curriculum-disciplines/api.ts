import http from '@/api/http'

import {
  createCrudApi,
} from '@/api/crud'

import {
  curriculaApi,
} from '@/modules/curricula/api'

import {
  disciplinesApi,
} from '@/modules/curriculum-references/api'

import {
  studyProgramsApi,
} from '@/modules/study-programs/api'

import type {
  Curriculum,
} from '@/modules/curricula/types'

import type {
  DepartmentLookup,
  Discipline,
} from '@/modules/curriculum-references/types'

import type {
  StudyProgram,
} from '@/modules/study-programs/types'

import type {
  CurriculumDiscipline,
  CurriculumDisciplinePayload,
} from '@/modules/curriculum-disciplines/types'

import type {
  PaginatedResponse,
} from '@/types/api'

export const curriculumDisciplinesApi =
  createCrudApi<
    CurriculumDiscipline,
    CurriculumDisciplinePayload,
    CurriculumDisciplinePayload
  >(
    '/curriculum/curriculum-disciplines/',
  )

export async function getCurriculum(
  id: number,
): Promise<Curriculum> {
  return curriculaApi.retrieve(id)
}

export async function getStudyProgram(
  id: number,
): Promise<StudyProgram> {
  return studyProgramsApi.retrieve(id)
}

export async function getDisciplines(): Promise<
  PaginatedResponse<Discipline>
> {
  return disciplinesApi.list({
    page_size: 500,

    is_active: true,

    ordering:
      'sort_order,name_ru',
  })
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
