export type AcademicYearStatus =
  | 'open'
  | 'closed'

export type EducationLevelCode =
  | 'bachelor'
  | 'master'

export type StudyFormCode =
  | 'full_time'
  | 'part_time'
  | 'evening'
  | 'distance'

export type SemesterSeason =
  | 'autumn'
  | 'spring'

export interface AcademicYear
  extends Record<string, unknown> {
  id: number

  start_year: number
  end_year: number
  name: string

  is_current: boolean
  is_active: boolean

  status: AcademicYearStatus
  status_label: string
  is_closed: boolean

  closed_at: string | null
  closed_by: number | null
  closed_by_name: string | null
  closing_comment: string

  reopened_at: string | null
  reopened_by: number | null
  reopened_by_name: string | null
  reopening_reason: string

  created_at: string
  updated_at: string

  is_archived: boolean
}

export interface AcademicYearPayload {
  start_year: number
  end_year: number

  is_current: boolean
  is_active: boolean
}

export interface LocalizedReference
  extends Record<string, unknown> {
  id: number

  code: string

  name_ru: string
  name_uz: string

  display_name: string

  is_active: boolean
  sort_order: number

  is_archived: boolean
}

export interface EducationLevel
  extends LocalizedReference {
  code: EducationLevelCode
}

export interface StudyForm
  extends LocalizedReference {
  code: StudyFormCode
}

export interface LocalizedReferencePayload<
  TCode extends string,
> {
  code: TCode

  name_ru: string
  name_uz: string

  is_active: boolean
  sort_order: number
}

export type EducationLevelPayload =
  LocalizedReferencePayload<EducationLevelCode>

export type StudyFormPayload =
  LocalizedReferencePayload<StudyFormCode>

export interface EducationDuration
  extends Record<string, unknown> {
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

export interface EducationDurationPayload {
  education_level: number
  study_form: number

  duration_months: number
  semesters_count: number

  is_active: boolean
}

export interface AcademicSemester
  extends Record<string, unknown> {
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

export interface AcademicSemesterPayload {
  academic_year: number

  season: SemesterSeason

  start_date: string
  end_date: string

  is_current: boolean
  is_active: boolean
}

export interface AcademicYearOperationResult {
  id: number
  name: string

  status: AcademicYearStatus
  status_label: string

  is_current: boolean
  is_active: boolean

  closed_at: string | null
  closed_by: number | null
  closed_by_name: string | null
  closing_comment: string

  reopened_at: string | null
  reopened_by: number | null
  reopened_by_name: string | null
  reopening_reason: string
}
