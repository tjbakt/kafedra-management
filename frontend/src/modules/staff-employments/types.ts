export type EmploymentType =
  | 'primary'
  | 'internal_part_time'
  | 'external_part_time'
  | 'hourly'

export interface StaffEmployment
  extends Record<string, unknown> {
  id: number

  staff_member: number
  staff_member_name: string

  department: number
  department_name: string

  faculty: number
  faculty_name: string

  position: number
  position_name: string

  employment_type: EmploymentType
  employment_type_name: string

  rate: string

  start_date: string
  end_date: string | null

  is_primary: boolean
  is_active: boolean

  document_number: string
  document_date: string | null

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

export interface StaffEmploymentPayload {
  staff_member: number
  department: number
  position: number

  employment_type: EmploymentType
  rate: number

  start_date: string
  end_date: string | null

  is_primary: boolean
  is_active: boolean

  document_number: string
  document_date: string | null

  notes: string
}

export interface StaffMemberLookup {
  id: number

  personnel_number: string
  full_name: string

  is_active: boolean
  is_archived: boolean
}

export interface DepartmentLookup {
  id: number

  faculty: number
  faculty_name: string

  university: number
  university_name: string

  code: string

  name_ru: string
  name_uz: string

  display_name: string

  is_active: boolean
  is_archived: boolean
}

export interface StaffPositionLookup {
  id: number

  code: string

  name_ru: string
  name_uz: string

  display_name: string

  category: string
  category_name: string

  is_teaching_position: boolean
  is_active: boolean
  is_archived: boolean
}

export interface SelectOption<T = number> {
  value: T
  label: string
  description?: string
}
