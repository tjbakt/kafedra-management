import type {
  AcademicSemesterLookup,
  AcademicYearLookup,
  CurriculumLookup,
  GroupSemester,
} from '@/modules/teaching-setup/types'

import type {
  CurriculumDiscipline,
} from '@/modules/curriculum-disciplines/types'

import type {
  CurriculumWorkload,
} from '@/modules/curriculum-disciplines/workload-types'

export type TeachingStreamStatus =
  | 'draft'
  | 'calculated'
  | 'approved'
  | 'cancelled'

export type PlannedWorkloadStatus =
  | 'calculated'
  | 'approved'
  | 'partially_distributed'
  | 'distributed'
  | 'cancelled'

export interface TeachingStreamGroup
  extends Record<string, unknown> {
  id: number

  teaching_stream: number

  group_semester: number

  student_group: number
  student_group_code: string

  students_count: number
  subgroup_count: number

  is_active: boolean

  notes: string

  is_archived: boolean
}

export interface TeachingStream
  extends Record<string, unknown> {
  id: number

  academic_year: number
  academic_year_name: string

  academic_semester: number
  academic_semester_name: string

  curriculum: number
  curriculum_code: string

  study_program_name: string
  study_form_name: string

  semester_number: number

  code: string
  name: string

  groups_count: number
  students_count: number
  subgroups_count: number

  planned_workloads_count: number
  total_planned_hours: string

  status: TeachingStreamStatus
  status_name: string

  is_active: boolean
  notes: string

  stream_groups: TeachingStreamGroup[]

  created_at: string
  updated_at: string

  is_archived: boolean
}

export interface TeachingStreamPayload {
  academic_year: number
  // academic_semester: number

  curriculum: number
  semester_number: number

  code: string
  name: string

  status: TeachingStreamStatus

  is_active: boolean

  notes: string
}

export interface TeachingStreamBulkPayload {
  academic_year: number

  curriculum: number

  semester_numbers: number[]

  code: string

  name: string

  status: TeachingStreamStatus

  is_active: boolean

  notes: string
}

export interface TeachingStreamGroupPayload {
  teaching_stream: number
  group_semester: number

  is_active: boolean

  notes: string
}

export interface PlannedWorkload
  extends Record<string, unknown> {
  id: number

  teaching_stream: number

  teaching_stream_code: string
  teaching_stream_name: string

  curriculum: number
  curriculum_code: string

  curriculum_discipline: number

  discipline_code: string
  discipline_name: string

  academic_year: number
  academic_year_name: string

  academic_semester: number
  academic_semester_name: string

  teaching_department: number
  department_name: string

  curriculum_workload: number
  workload_type_name: string

  calculation_mode: string

  base_hours: string
  calculation_quantity: string

  total_hours: string

  distributed_hours: string
  remaining_hours: string

  distribution_percent: string

  is_fully_distributed: boolean

  groups_count: number
  subgroups_count: number
  students_count: number

  group_semester: number | null

  student_group: number | null

  student_group_code: string | null

  semester_number: number

  season: 'autumn' | 'spring'

  status: string
  status_name: string

  calculated_at: string

  notes: string

  is_archived: boolean
}

export interface CalculateStreamResponse {
  detail: string
  calculated_count: number
  data: PlannedWorkload[]
}

export interface CalculateAllError {
  stream: number
  code: string
  error: unknown
}

export interface CalculateAllResponse {
  calculated_count: number
  calculated_ids: number[]

  errors_count: number

  errors: CalculateAllError[]
}

export interface PlannedWorkloadSummaryDepartment {
  teaching_department_id: number
  teaching_department__name_ru: string
  total_hours: string
}

export interface PlannedWorkloadSummary {
  total_hours: string | number

  by_department:
    PlannedWorkloadSummaryDepartment[]
}

export interface SelectOption<T = number> {
  value: T
  label: string
  description?: string
}

export type {
  AcademicSemesterLookup,
  AcademicYearLookup,
  CurriculumDiscipline,
  CurriculumWorkload,
  CurriculumLookup,
  GroupSemester,
}
