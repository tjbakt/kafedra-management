export type CurriculumStatus =
  | 'draft'
  | 'approved'
  | 'archived'

export interface Curriculum
  extends Record<string, unknown> {
  id: number

  code: string
  version: number

  study_program: number
  study_program_code: string
  study_program_name: string

  education_level: number
  education_level_name: string

  study_form: number
  study_form_name: string

  effective_academic_year: number
  effective_academic_year_name: string

  semesters_count: number | null

  status: CurriculumStatus
  status_name: string

  approved_at: string | null
  approval_document: string

  is_active: boolean

  notes: string

  disciplines_count: number

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

export interface CurriculumPayload {
  code: string

  version: number

  study_program: number
  study_form: number

  effective_academic_year: number

  status: CurriculumStatus

  approved_at: string | null
  approval_document: string

  is_active: boolean

  notes: string
}

export interface StudyProgramLookup {
  id: number

  university: number
  university_name: string

  education_level: number
  education_level_name: string

  code: string

  name_ru: string
  name_uz: string

  display_name: string

  profiling_department: number
  profiling_department_name: string

  profiling_faculty: number
  profiling_faculty_name: string

  is_active: boolean
  is_archived: boolean
}

export interface StudyFormLookup {
  id: number

  code: string

  name_ru: string
  name_uz: string

  display_name: string

  is_active: boolean
  is_archived: boolean
}

export interface AcademicYearLookup {
  id: number

  start_year: number
  end_year: number

  name: string

  is_current: boolean
  is_active: boolean

  status: string
  is_closed: boolean

  is_archived: boolean
}

export interface EducationDurationLookup {
  id: number

  education_level: number
  education_level_name: string

  study_form: number
  study_form_name: string

  duration_months: number
  semesters_count: number

  is_active: boolean
  is_archived: boolean
}

export interface UniversityLookup {
  id: number

  code: string

  name_ru: string
  name_uz: string

  display_name: string

  is_active: boolean
  is_archived: boolean
}

export interface SelectOption<T = number> {
  value: T
  label: string
  description?: string
}
