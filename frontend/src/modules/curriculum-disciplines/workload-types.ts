export type WorkloadCalculationMode =
  | 'fixed'
  | 'per_group'
  | 'per_subgroup'
  | 'per_student'

export interface WorkloadType {
  id: number

  code: string

  name_ru: string
  name_uz: string
  display_name: string

  calculation_mode:
    WorkloadCalculationMode

  calculation_mode_name: string

  report_category: string
  report_category_name: string

  is_classroom: boolean
  is_teaching_load: boolean
  is_active: boolean

  sort_order: number

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

export interface CurriculumWorkload {
  id: number

  curriculum_discipline: number

  workload_type: number

  workload_type_name: string

  calculation_mode:
    WorkloadCalculationMode

  calculation_mode_name: string

  base_hours: string

  students_per_unit:
    number | null

  is_active: boolean

  notes: string

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

export interface CurriculumWorkloadPayload {
  curriculum_discipline: number

  workload_type: number

  calculation_mode:
    WorkloadCalculationMode

  base_hours: number

  students_per_unit:
    number | null

  is_active: boolean

  notes: string
}

export interface WorkloadTypeOption {
  value: number
  label: string
  description?: string
  defaultCalculationMode:
    WorkloadCalculationMode
}
