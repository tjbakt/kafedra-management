import type { NormalizedApiError } from '@/types/validation'

export const API_ERROR_TOAST_EVENT =
  'kafedra:api-error'

export interface ApiErrorToastPayload {
  error: NormalizedApiError
}

export function emitApiErrorToast(
  error: NormalizedApiError,
): void {
  window.dispatchEvent(
    new CustomEvent<ApiErrorToastPayload>(
      API_ERROR_TOAST_EVENT,
      {
        detail: {
          error,
        },
      },
    ),
  )
}
