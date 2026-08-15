export type GroupSemesterStatus =
  | 'planned'
  | 'active'
  | 'completed'
  | 'cancelled'

export type SemesterSeason =
  | 'autumn'
  | 'spring'

export interface GroupCurriculumAssignment
  extends Record<string, unknown> {
  id: number

  student_group: number
  student_group_code: string

  curriculum: number
  curriculum_code: string

  study_program_name: string
  study_form_name: string

  start_academic_year: number
  start_academic_year_name: string

  end_academic_year: number | null
  end_academic_year_name: string | null

  is_primary: boolean
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

export interface GroupCurriculumPayload {
  student_group: number
  curriculum: number

  start_academic_year: number
  end_academic_year: number | null

  is_primary: boolean
  is_active: boolean

  notes: string
}

export interface GroupSemester
  extends Record<string, unknown> {
  id: number

  group_curriculum: number

  student_group: number
  student_group_code: string

  curriculum: number
  curriculum_code: string

  academic_year: number
  academic_year_name: string

  academic_semester: number
  academic_semester_name: string

  semester_number: number

  season: SemesterSeason

  students_count: number
  subgroup_count: number

  status: GroupSemesterStatus
  status_name: string

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

export interface GroupSemesterPayload {
  group_curriculum: number

  academic_year: number
  academic_semester: number

  semester_number: number

  students_count: number
  subgroup_count: number

  status: GroupSemesterStatus

  is_active: boolean

  notes: string
}

export interface StudentGroupLookup {
  id: number

  code: string

  study_program: number
  study_program_name: string

  education_level: number
  education_level_name: string

  study_form: number
  study_form_name: string

  student_count: number
  subgroup_count: number

  is_active: boolean
  is_archived: boolean
}

export interface CurriculumLookup {
  id: number

  code: string
  version: number

  study_program: number
  study_program_code: string
  study_program_name: string

  study_form: number
  study_form_name: string

  effective_academic_year: number
  effective_academic_year_name: string

  semesters_count: number | null

  status: string

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

  is_closed: boolean
  is_archived: boolean
}

export interface AcademicSemesterLookup {
  id: number

  academic_year: number
  academic_year_name: string

  season: SemesterSeason
  season_name: string

  start_date: string
  end_date: string

  is_current: boolean
  is_active: boolean

  is_archived: boolean
}

export interface SelectOption<T = number> {
  value: T

  label: string

  description?: string
}
