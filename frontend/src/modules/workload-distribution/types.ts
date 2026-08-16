export type WorkloadDistributionStatus =
  | 'draft'
  | 'approved'
  | 'cancelled'

export interface WorkloadDistribution
  extends Record<string, unknown> {
  id: number

  planned_workload: number

  planned_total_hours: string
  planned_remaining_hours: string

  curriculum: number
  curriculum_code: string

  stream_code: string

  discipline_code: string
  discipline_name: string

  workload_type_name: string

  department_name: string

  academic_year_name: string
  academic_semester_name: string

  staff_employment: number

  teacher: number
  teacher_name: string
  personnel_number: string

  position_name: string

  employment_rate: string
  employment_type: string

  allocated_hours: string

  status: WorkloadDistributionStatus
  status_name: string

  approved_at: string | null

  approved_by: number | null
  approved_by_name: string | null

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

export interface WorkloadDistributionCreatePayload {
  planned_workload: number

  staff_employment: number

  allocated_hours: number

  notes: string
}

export interface WorkloadDistributionUpdatePayload {
  staff_employment: number

  allocated_hours: number

  notes: string
}

export interface DistributionActionResponse {
  detail: string

  data: WorkloadDistribution
}

export interface TeacherWorkloadSummary {
  staff_employment_academic_year: number

  staff_employment: number

  staff_member: number

  teacher_name: string
  personnel_number: string

  department: number
  department_name: string

  position: number
  position_name: string

  academic_year: number
  academic_year_name: string

  employment_rate: string

  has_academic_degree: boolean
  has_academic_title: boolean

  recommended_hours: string | null

  distributed_hours: string

  remaining_hours: string | null

  difference_hours: string | null

  load_percent: string | null

  load_status:
    | 'underloaded'
    | 'balanced'
    | 'overloaded'
    | 'norm_missing'

  norm_found: boolean
}

export interface SelectOption<T = number> {
  value: T

  label: string

  description?: string
}
