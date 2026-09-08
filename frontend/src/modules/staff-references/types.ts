export type StaffReferenceType =
  | 'position'
  | 'degree'
  | 'title'

export type StaffPositionCategory =
  | 'teaching'
  | 'administrative'
  | 'support'
  | 'other'

export interface StaffPosition extends Record<string, unknown>{
  id: number
  code: string
  name_ru: string
  name_uz: string
  display_name: string
  category: StaffPositionCategory
  category_name: string
  is_teaching_position: boolean
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

export interface StaffPositionPayload {
  code: string
  name_ru: string
  name_uz: string
  category: StaffPositionCategory
  is_teaching_position: boolean
  is_active: boolean
  sort_order: number
}

export interface AcademicDegree extends Record<string, unknown>{
  id: number
  code: string
  name_ru: string
  name_uz: string
  short_name_ru: string
  short_name_uz: string
  display_name: string
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

export interface AcademicDegreePayload {
  code: string
  name_ru: string
  name_uz: string
  short_name_ru: string
  short_name_uz: string
  is_active: boolean
  sort_order: number
}

export interface AcademicTitle extends Record<string, unknown>{
  id: number
  code: string
  name_ru: string
  name_uz: string
  short_name_ru: string
  short_name_uz: string
  display_name: string
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

export interface AcademicTitlePayload {
  code: string
  name_ru: string
  name_uz: string
  short_name_ru: string
  short_name_uz: string
  is_active: boolean
  sort_order: number
}
