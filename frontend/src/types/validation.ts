export type FieldErrors = Record<string, string[]>

export interface NormalizedApiError {
  message: string
  fieldErrors: FieldErrors
  nonFieldErrors: string[]
  status: number | null
}

export interface DrfValidationResponse {
  detail?: string
  message?: string

  non_field_errors?: string[]
  errors?: Record<string, unknown>

  [key: string]: unknown
}
