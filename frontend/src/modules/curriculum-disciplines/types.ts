import type { CurriculumWorkload, } from './workload-types'
import type { WorkloadCalculationMode, } from './workload-types'

export type CurriculumComponentType =
  | 'required'
  | 'elective'
  | 'optional'

export type CurriculumControlForm =
  | 'none'
  | 'exam'
  | 'credit'
  | 'graded_credit'
  | 'course_work'
  | 'course_project'

export type SemesterSeason =
  | 'autumn'
  | 'spring'

export type NestedCurriculumWorkload = CurriculumWorkload

// export interface NestedCurriculumWorkload
//   extends Record<string, unknown> {
//   id: number
//
//   curriculum_discipline: number
//
//   workload_type: number
//   workload_type_name: string
//
//   calculation_mode: string
//   calculation_mode_name: string
//
//   base_hours: string
//
//   students_per_unit:
//     number | null
//
//   is_active: boolean
//
//   notes: string
//
//   is_archived: boolean
// }

export interface CurriculumBundleWorkloadPayload {
  workload_type: number

  calculation_mode?:
    WorkloadCalculationMode

  base_hours?: number

  students_per_unit?:
    number | null

  is_active: boolean

  notes: string
}

export interface CurriculumBundleSemesterPayload {
  semester_number: number

  credits: number

  weeks_count: number

  is_active: boolean

  notes: string

  workloads:
    CurriculumBundleWorkloadPayload[]
}

export interface CurriculumDisciplineBundlePayload {
  curriculum: number

  discipline: number

  component_type:
    CurriculumComponentType

  semesters:
    CurriculumBundleSemesterPayload[]

  replace_semesters: boolean
}

export interface CurriculumDisciplineBundleResponse {
  detail: string

  data:
    CurriculumDiscipline[]
}

export interface CurriculumDiscipline
  extends Record<string, unknown> {
  id: number

  curriculum: number

  discipline: number

  discipline_code: string
  discipline_name: string

  semester_number: number

  season: SemesterSeason
  season_name: string

  teaching_department: number
  teaching_department_name: string

  component_type:
    CurriculumComponentType

  component_type_name: string

  control_form:
    CurriculumControlForm

  control_form_name: string

  credits: string

  total_academic_hours: string

  independent_hours: string

  planned_contact_hours: string

  weeks_count: number

  is_active: boolean

  notes: string

  workload_items: NestedCurriculumWorkload[]

  created_at: string
  updated_at: string

  created_by: number | null
  created_by_name: string | null

  updated_by: number | null
  updated_by_name: string | null

  is_archived: boolean

  archived_at: string | null

  archived_by: number | null
  archived_by_name: string | null
}

export interface CurriculumDisciplinePayload {
  curriculum: number

  discipline: number

  semester_number: number

  teaching_department: number

  component_type:
    CurriculumComponentType

  control_form:
    CurriculumControlForm

  credits: number

  total_academic_hours: number

  independent_hours: number

  weeks_count: number

  is_active: boolean

  notes: string
}

export interface SemesterOption {
  value: number

  label: string

  season: SemesterSeason

  seasonLabel: string
}

export interface SelectOption<
  T = number,
> {
  value: T

  label: string

  description?: string
}
