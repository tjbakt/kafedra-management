export interface StudentGroup
  extends Record<string, unknown> {
  id: number

  code: string

  academic_year_admission: number
  admission_academic_year_name: string

  graduation_academic_year: number | null
  graduation_academic_year_name: string | null

  faculty: number
  faculty_name: string
  faculty_type: string

  study_program: number
  study_program_name: string

  education_level: number
  education_level_name: string

  study_form: number
  study_form_name: string

  profiling_department: number
  profiling_department_name: string

  profiling_department_faculty: number
  profiling_department_faculty_name: string

  student_count: number
  subgroup_count: number

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

export interface StudentGroupPayload {
  code: string

  academic_year_admission: number
  graduation_academic_year: number | null

  faculty: number
  study_program: number
  study_form: number

  student_count: number
  subgroup_count: number

  is_active: boolean

  notes: string
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

export interface FacultyLookup {
  id: number

  university: number
  university_name: string

  faculty_type: string
  faculty_type_name?: string

  code: string

  name_ru: string
  name_uz: string

  display_name: string

  is_active: boolean
  is_archived: boolean
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

export interface SelectOption<T = number> {
  value: T
  label: string
  description?: string
}
