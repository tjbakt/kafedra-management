export interface Department
  extends Record<string, unknown> {
  id: number

  faculty: number
  faculty_name: string

  university: number
  university_name: string

  code: string

  name_ru: string
  name_uz: string

  short_name_ru: string
  short_name_uz: string

  display_name: string
  display_short_name: string

  head_name: string
  phone: string
  email: string
  room: string

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

export interface DepartmentPayload {
  faculty: number

  code: string

  name_ru: string
  name_uz: string

  short_name_ru: string
  short_name_uz: string

  head_name: string
  phone: string
  email: string
  room: string

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

export interface FacultyOption {
  id: number

  university: number
  university_name: string

  faculty_type?: string

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
