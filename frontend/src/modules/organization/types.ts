export interface University extends Record<string, unknown> {
  id: number
  code: string

  name_ru: string
  name_uz: string

  short_name_ru: string
  short_name_uz: string

  display_name: string
  display_short_name: string

  address_ru: string
  address_uz: string

  phone: string
  email: string
  website: string

  is_active: boolean
  sort_order: number

  faculties_count: number

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

export interface UniversityPayload {
  code: string

  name_ru: string
  name_uz: string

  short_name_ru: string
  short_name_uz: string

  address_ru: string
  address_uz: string

  phone: string
  email: string
  website: string

  is_active: boolean
  sort_order: number
}

export interface UniversityOption {
  id: number
  code: string

  name_ru: string
  name_uz: string

  short_name_ru: string
  short_name_uz: string

  display_name: string
  display_short_name: string

  is_active: boolean
  is_archived: boolean
}

export type FacultyType =
  | 'standard'
  | 'magistracy'

export interface Faculty  extends Record<string, unknown> {
  id: number

  university: number
  university_name: string

  faculty_type: FacultyType

  code: string

  name_ru: string
  name_uz: string

  short_name_ru: string
  short_name_uz: string

  display_name: string
  display_short_name: string

  dean_name: string

  phone: string
  email: string

  is_active: boolean
  sort_order: number

  departments_count: number

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

export interface FacultyPayload {
  university: number

  faculty_type: FacultyType

  code: string

  name_ru: string
  name_uz: string

  short_name_ru: string
  short_name_uz: string

  dean_name: string

  phone: string
  email: string

  is_active: boolean
  sort_order: number
}

export interface SelectOption<T = number | null> {
  value: T
  label: string
}
