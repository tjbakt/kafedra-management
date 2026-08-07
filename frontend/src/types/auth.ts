import type { AppLocale } from '@/types/locale'

export interface AuthUser {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  middle_name: string
  full_name: string
  phone: string
  avatar: string | null
  interface_language: AppLocale
  must_change_password: boolean
  is_active: boolean
  is_staff: boolean
  groups: string[]
  permissions: string[]
  last_login: string | null
  created_at: string
  updated_at: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: AuthUser
}

export interface RefreshTokenRequest {
  refresh: string
}

export interface RefreshTokenResponse {
  access: string
  refresh?: string
}

export interface VerifyTokenRequest {
  token: string
}

export interface LogoutRequest {
  refresh: string
}

export interface ChangePasswordPayload {
  current_password: string
  new_password: string
  new_password_confirmation: string
}

export interface UpdateProfilePayload {
  email?: string
  first_name?: string
  last_name?: string
  middle_name?: string
  phone?: string
  interface_language?: AppLocale
}