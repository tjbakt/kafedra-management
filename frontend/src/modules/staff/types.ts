export type Gender = '' | 'male' | 'female'

export interface StaffEmploymentShort
  extends Record<string, unknown> {
  id: number

  department: number
  department_name: string

  position: number
  position_name: string

  employment_type: string
  employment_type_name: string

  rate: string

  start_date: string
  end_date: string | null

  is_primary: boolean
  is_active: boolean
}

export interface StaffMember
  extends Record<string, unknown> {
  id: number

  user: number | null
  username: string | null

  personnel_number: string

  last_name: string
  first_name: string
  middle_name: string

  full_name: string

  gender: Gender
  birth_date: string | null

  phone: string
  email: string

  academic_degree: number | null
  academic_degree_name: string | null

  academic_title: number | null
  academic_title_name: string | null

  has_academic_degree: boolean
  has_academic_title: boolean

  degree_awarded_date: string | null
  title_awarded_date: string | null

  is_active: boolean

  notes: string

  employments: StaffEmploymentShort[]

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

export interface StaffMemberPayload {
  user?: number | null

  personnel_number: string

  last_name: string
  first_name: string
  middle_name: string

  gender: Gender
  birth_date: string | null

  phone: string
  email: string

  academic_degree: number | null
  academic_title: number | null

  degree_awarded_date: string | null
  title_awarded_date: string | null

  is_active: boolean

  notes: string
}

export interface AcademicDegreeOption {
  id: number

  code: string

  name_ru: string
  name_uz: string

  short_name_ru: string
  short_name_uz: string

  is_active: boolean
}

export interface AcademicTitleOption {
  id: number

  code: string

  name_ru: string
  name_uz: string

  short_name_ru: string
  short_name_uz: string

  is_active: boolean
}

export type StaffGender =
  | ''
  | 'male'
  | 'female'

export interface StaffEmploymentShort
  extends Record<string, unknown> {
  id: number

  department: number
  department_name: string

  position: number
  position_name: string

  employment_type: string
  employment_type_name: string

  rate: string

  start_date: string
  end_date: string | null

  is_primary: boolean
  is_active: boolean
}

export interface StaffMember
  extends Record<string, unknown> {
  id: number

  user: number | null
  username: string | null

  personnel_number: string

  last_name: string
  first_name: string
  middle_name: string

  full_name: string

  gender: StaffGender
  birth_date: string | null

  phone: string
  email: string

  academic_degree: number | null
  academic_degree_name: string | null

  academic_title: number | null
  academic_title_name: string | null

  has_academic_degree: boolean
  has_academic_title: boolean

  degree_awarded_date: string | null
  title_awarded_date: string | null

  is_active: boolean

  notes: string

  employments: StaffEmploymentShort[]

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

export interface StaffMemberPayload {
  personnel_number: string

  last_name: string
  first_name: string
  middle_name: string

  gender: StaffGender
  birth_date: string | null

  phone: string
  email: string

  academic_degree: number | null
  academic_title: number | null

  degree_awarded_date: string | null
  title_awarded_date: string | null

  is_active: boolean

  notes: string
}

export interface AcademicDegreeOption {
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

export interface AcademicTitleOption {
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

export interface SelectOption {
  id: number | null
  label: string
}
