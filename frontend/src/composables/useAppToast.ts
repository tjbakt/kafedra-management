import { useToast } from 'primevue/usetoast'

import {
  API_ERROR_TOAST_EVENT,
  type ApiErrorToastPayload,
} from '@/utils/api-error-toast'

const DEFAULT_LIFE = 4000

export function useAppToast() {
  const toast = useToast()

  function success(summary: string, detail = '', life = DEFAULT_LIFE): void {
    toast.add({
      severity: 'success',
      summary,
      detail,
      life,
    })
  }

  function info(summary: string, detail = '', life = DEFAULT_LIFE): void {
    toast.add({
      severity: 'info',
      summary,
      detail,
      life,
    })
  }

  function warning(summary: string, detail = '', life = DEFAULT_LIFE): void {
    toast.add({
      severity: 'warn',
      summary,
      detail,
      life,
    })
  }

  function error(summary: string, detail = '', life = 6000): void {
    toast.add({
      severity: 'error',
      summary,
      detail,
      life,
    })
  }

  function showApiError(
    payload: ApiErrorToastPayload,
  ): void {
    const apiError = payload.error

    const details: string[] = []

    Object.entries(
      apiError.fieldErrors,
    ).forEach(([field, messages]) => {
      messages.forEach((message) => {
        details.push(
          `${field}: ${message}`,
        )
      })
    })

    details.push(
      ...apiError.nonFieldErrors,
    )

    const detail =
      details.length > 0
        ? [...new Set(details)].join('\n')
        : apiError.message

    const summary =
      apiError.status === 400
        ? 'Ошибка проверки данных'
        : apiError.status === 401
          ? 'Ошибка авторизации'
          : apiError.status === 403
            ? 'Доступ запрещён'
            : apiError.status === 404
              ? 'Данные не найдены'
              : apiError.status === 409
                ? 'Конфликт данных'
                : apiError.status !== null &&
                    apiError.status >= 500
                  ? 'Ошибка сервера'
                  : 'Ошибка'

    error(
      summary,
      detail,
      7000,
    )
  }

  return {
    success,
    info,
    warning,
    error,
    showApiError,
  }
}

export {
  API_ERROR_TOAST_EVENT,
}
