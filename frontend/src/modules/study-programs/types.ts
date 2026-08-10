export interface StudyProgram
  extends Record<string, unknown> {
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

export interface StudyProgramPayload {
  university: number

  education_level: number

  code: string

  name_ru: string
  name_uz: string

  profiling_department: number

  is_active: boolean
  sort_order: number
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

export interface EducationLevelLookup {
  id: number

  code: string

  name_ru: string
  name_uz: string

  display_name: string

  is_active: boolean
  is_archived: boolean
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

export interface SelectOption<T = number> {
  value: T
  label: string
  description?: string
}
