export type WorkloadTypeCode =
  | 'lecture'
  | 'practice'
  | 'laboratory'
  | 'seminar'
  | 'consultation'
  | 'exam'
  | 'credit'
  | 'course_work'
  | 'course_project'
  | 'course_work_project_defense'
  | 'scientific_practice'
  | 'qualification_practice'
  | 'master_dissertation_supervision'
  | 'master_dissertation_defense'
  | 'graduation_work_supervision'
  | 'graduation_work_defense'
  | 'independent_work'
  | 'other'

export type CalculationMode =
  | 'fixed'
  | 'per_group'
  | 'per_subgroup'
  | 'per_student'

export type ReportCategory =
  | 'lecture'
  | 'practice'
  | 'laboratory'
  | 'course_work_supervision'
  | 'course_project_supervision'
  | 'course_work_project_defense'
  | 'scientific_practice'
  | 'qualification_practice'
  | 'master_dissertation_supervision'
  | 'master_dissertation_defense'
  | 'graduation_work_supervision'
  | 'graduation_work_defense'
  | 'rating'
  | 'other'

export interface Discipline extends Record<string, unknown> {
  id: number

  code: string

  name_ru: string
  name_uz: string

  display_name: string

  default_department: number | null
  default_department_name: string | null

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

export interface DisciplinePayload {
  code: string

  name_ru: string
  name_uz: string

  default_department: number | null

  is_active: boolean
  sort_order: number
}

export interface WorkloadType extends Record<string, unknown> {
  id: number

  code: WorkloadTypeCode

  name_ru: string
  name_uz: string

  display_name: string

  calculation_mode: CalculationMode
  calculation_mode_name: string

  report_category: ReportCategory
  report_category_name: string

  uses_curriculum_rule: boolean

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

export interface WorkloadTypePayload {
  code: WorkloadTypeCode

  name_ru: string
  name_uz: string

  calculation_mode: CalculationMode

  report_category: ReportCategory

  is_classroom: boolean
  is_teaching_load: boolean

  is_active: boolean

  sort_order: number
}

export interface DepartmentLookup {
  id: number

  university: number
  university_name: string

  faculty: number
  faculty_name: string

  code: string

  name_ru: string
  name_uz: string

  display_name: string

  is_active: boolean
  is_archived: boolean
}

export interface SelectOption<T = string> {
  value: T
  label: string

  description?: string
}
