import axios from 'axios'

import type {
  DrfValidationResponse,
  FieldErrors,
  NormalizedApiError,
} from '@/types/validation'

function normalizeErrorValue(
  value: unknown,
): string[] {
  if (typeof value === 'string') {
    return [value]
  }

  if (typeof value === 'number') {
    return [String(value)]
  }

  if (Array.isArray(value)) {
    return value
      .flatMap((item) =>
        normalizeErrorValue(item),
      )
      .filter(Boolean)
  }

  if (
    value &&
    typeof value === 'object'
  ) {
    return Object.values(value)
      .flatMap((item) =>
        normalizeErrorValue(item),
      )
      .filter(Boolean)
  }

  return []
}

export function normalizeApiError(
  error: unknown,
  fallbackMessage =
    'Произошла непредвиденная ошибка',
): NormalizedApiError {
  if (!axios.isAxiosError<DrfValidationResponse>(error)) {
    return {
      message: fallbackMessage,
      fieldErrors: {},
      nonFieldErrors: [],
      status: null,
    }
  }

  const status =
    error.response?.status ?? null

  const data = error.response?.data

  if (!data) {
    return {
      message:
        error.message || fallbackMessage,
      fieldErrors: {},
      nonFieldErrors: [],
      status,
    }
  }

  const fieldErrors: FieldErrors = {}
  const nonFieldErrors: string[] = []

  if (
    Array.isArray(
      data.non_field_errors,
    )
  ) {
    nonFieldErrors.push(
      ...data.non_field_errors.map(String),
    )
  }

  const ignoredKeys = new Set([
    'detail',
    'message',
    'non_field_errors',
    'errors',
  ])

  Object.entries(data).forEach(
    ([field, value]) => {
      if (ignoredKeys.has(field)) {
        return
      }

      const messages =
        normalizeErrorValue(value)

      if (messages.length) {
        fieldErrors[field] = messages
      }
    },
  )

  if (
    data.errors &&
    typeof data.errors === 'object' &&
    !Array.isArray(data.errors)
  ) {
    Object.entries(
      data.errors,
    ).forEach(([field, value]) => {
      const messages =
        normalizeErrorValue(value)

      if (!messages.length) {
        return
      }

      if (
        field === 'non_field_errors' ||
        field === 'detail'
      ) {
        nonFieldErrors.push(
          ...messages,
        )
        return
      }

      fieldErrors[field] = [
        ...(fieldErrors[field] ?? []),
        ...messages,
      ]
    })
  }

  const message =
    typeof data.detail === 'string'
      ? data.detail
      : typeof data.message === 'string'
        ? data.message
        : nonFieldErrors[0] ||
          Object.values(fieldErrors)[0]?.[0] ||
          error.message ||
          fallbackMessage

  return {
    message,
    fieldErrors,
    nonFieldErrors,
    status,
  }
}

export function getFieldError(
  errors: FieldErrors,
  field: string,
): string {
  return errors[field]?.[0] ?? ''
}

export function hasFieldErrors(
  errors: FieldErrors,
): boolean {
  return Object.keys(errors).length > 0
}
