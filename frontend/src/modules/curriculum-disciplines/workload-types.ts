import type {
  WorkloadType,
} from '@/modules/curriculum-references/types'

export type {
  WorkloadType,
}

export type WorkloadCalculationMode =
  | 'fixed'
  | 'per_group'
  | 'per_subgroup'
  | 'per_student'

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

export interface CurriculumWorkloadRule
  extends Record<string, unknown> {
  id: number

  curriculum: number

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

  is_archived: boolean
}

export interface CurriculumWorkloadRulePayload {
  curriculum: number

  workload_type: number

  calculation_mode:
    WorkloadCalculationMode

  base_hours: number

  students_per_unit:
    number | null

  is_active: boolean

  notes: string
}
