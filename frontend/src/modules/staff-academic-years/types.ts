export interface AcademicYearOption {
  id: number

  start_year: number
  end_year: number

  name: string

  is_current: boolean
  is_active: boolean

  status: string
  status_label: string

  is_closed: boolean

  is_archived: boolean
}

export interface AcademicDegreeLookup {
  id: number

  code: string

  name_ru: string
  name_uz: string

  short_name_ru: string
  short_name_uz: string

  display_name: string

  is_active: boolean
  is_archived: boolean
}

export interface AcademicTitleLookup {
  id: number

  code: string

  name_ru: string
  name_uz: string

  short_name_ru: string
  short_name_uz: string

  display_name: string

  is_active: boolean
  is_archived: boolean
}

export interface EmploymentLookup {
  id: number

  staff_member: number
  staff_member_name: string

  department: number
  department_name: string

  faculty: number
  faculty_name: string

  position: number
  position_name: string

  rate: string

  is_primary: boolean
  is_active: boolean

  is_archived: boolean
}

export interface DepartmentLookup {
  id: number

  code: string

  name_ru: string
  name_uz: string

  display_name: string

  is_active: boolean
  is_archived: boolean
}

export interface StaffAcademicYearRecord
  extends Record<string, unknown> {
  id: number

  staff_employment: number

  staff_member: number
  staff_member_name: string

  department: number
  department_name: string

  position_name: string

  academic_year: number
  academic_year_name: string

  rate: string

  academic_degree: number | null
  academic_degree_name: string | null

  academic_title: number | null
  academic_title_name: string | null

  has_academic_degree: boolean
  has_academic_title: boolean

  recommended_annual_hours: string | null

  is_active: boolean
  notes: string

  created_at: string
  updated_at: string

  created_by: number | null
  created_by_name: string | null

  updated_by: number | null
  updated_by_name: string | null

  is_archived: boolean
}

export interface StaffAcademicYearPayload {
  staff_employment: number

  academic_year: number

  rate: number

  academic_degree: number | null
  academic_title: number | null

  is_active: boolean

  notes: string
}

export interface WorkloadNorm
  extends Record<string, unknown> {
  id: number

  academic_year: number
  academic_year_name: string

  rate: string

  has_academic_degree: boolean
  has_academic_title: boolean

  annual_hours: string

  is_active: boolean

  notes: string

  created_at: string
  updated_at: string

  created_by: number | null
  created_by_name: string | null

  updated_by: number | null
  updated_by_name: string | null

  is_archived: boolean
}

export interface WorkloadNormPayload {
  academic_year: number

  rate: number

  has_academic_degree: boolean
  has_academic_title: boolean

  annual_hours: number

  is_active: boolean

  notes: string
}

export interface RecommendedWorkload {
  employment: number

  academic_year: number
  academic_year_name: string

  academic_year_record?: number

  academic_year_record_found: boolean

  rate: string | null

  academic_degree: number | null
  academic_degree_name?: string | null

  academic_title: number | null
  academic_title_name?: string | null

  has_academic_degree: boolean | null
  has_academic_title: boolean | null

  annual_hours: string | null

  norm_id?: number

  norm_found: boolean

  message?: string
}

export interface BulkCreatePayload {
  academic_year: number
  department?: number | null
}

export interface BulkCreateResult {
  academic_year: number
  academic_year_name: string

  department: number | null
  department_name: string | null

  total_employments: number

  created: number
  restored: number
  skipped: number
  missing: number
}

export interface MissingEmployment {
  staff_employment: number

  staff_member: number
  staff_member_name: string

  personnel_number: string

  department: number
  department_name: string

  position: number
  position_name: string

  current_rate: string

  current_academic_degree: number | null
  current_academic_degree_name: string | null

  current_academic_title: number | null
  current_academic_title_name: string | null
}

export interface SelectOption<T = number> {
  value: T
  label: string
  description?: string
}
