import http from '@/api/http'

import {
  createCrudApi,
} from '@/api/crud'

import type {
  PaginatedResponse,
} from '@/types/api'

import type {
  CurriculumWorkload,
  CurriculumWorkloadPayload,
  WorkloadType,
} from './workload-types'

import type {
  CurriculumWorkloadRule,
  CurriculumWorkloadRulePayload,
} from './workload-types'

export const workloadTypesApi =
  createCrudApi<
    WorkloadType,
    Partial<WorkloadType>,
    Partial<WorkloadType>
  >(
    '/curriculum/workload-types/',
  )

export const curriculumWorkloadsApi =
  createCrudApi<
    CurriculumWorkload,
    CurriculumWorkloadPayload,
    CurriculumWorkloadPayload
  >(
    '/curriculum/curriculum-workloads/',
  )

export async function getWorkloadTypes(): Promise<
  PaginatedResponse<WorkloadType>
> {
  const response =
    await workloadTypesApi.list({
      page_size: 500,

      is_active: true,

      ordering:
        'sort_order,name_ru',
    })

  return response
}

export async function getCurriculumWorkloads(
  curriculumDisciplineId: number,
): Promise<
  PaginatedResponse<CurriculumWorkload>
> {
  const response =
    await http.get<
      PaginatedResponse<CurriculumWorkload>
    >(
      '/curriculum/curriculum-workloads/',
      {
        params: {
          curriculum_discipline:
            curriculumDisciplineId,

          page_size: 500,

          ordering:
            'workload_type__sort_order',
        },
      },
    )

  return response.data
}

export const curriculumWorkloadRulesApi =
  createCrudApi<
    CurriculumWorkloadRule,
    CurriculumWorkloadRulePayload,
    CurriculumWorkloadRulePayload
  >(
    '/curriculum/curriculum-workload-rules/',
  )


export async function getCurriculumWorkloadRules(
  curriculumId: number,
): Promise<
  PaginatedResponse<CurriculumWorkloadRule>
> {
  return curriculumWorkloadRulesApi.list({
    curriculum:
      curriculumId,

    page_size: 500,

    is_active: true,

    ordering:
      'workload_type__sort_order',
  })
}
