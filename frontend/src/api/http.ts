import axios, {
  AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'

import { tokenStorageService } from '@/services/token-storage.service'
import type { RefreshTokenResponse } from '@/types/auth'

interface ApiErrorResponse {
  detail?: string
  message?: string
  code?: string
  errors?: Record<string, string[]>
  [key: string]: unknown
}

interface RetriableRequestConfig
  extends InternalAxiosRequestConfig {
  _retry?: boolean
}

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL || '/api/v1'

const apiTimeout = Number(
  import.meta.env.VITE_API_TIMEOUT || 15000,
)

const http: AxiosInstance = axios.create({
  baseURL: apiBaseUrl,
  timeout: apiTimeout,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

const refreshClient: AxiosInstance = axios.create({
  baseURL: apiBaseUrl,
  timeout: apiTimeout,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

let refreshPromise: Promise<string> | null = null

function getInterfaceLanguage(): string {
  return (
    localStorage.getItem(
      'kafedra.interface-language',
    ) || 'ru'
  )
}

async function requestNewAccessToken(): Promise<string> {
  const refreshToken =
    tokenStorageService.getRefreshToken()

  if (!refreshToken) {
    throw new Error('Refresh token is missing')
  }

  const response =
    await refreshClient.post<RefreshTokenResponse>(
      '/auth/refresh/',
      {
        refresh: refreshToken,
      },
    )

  const { access, refresh } = response.data

  tokenStorageService.saveAccessToken(access)

  if (refresh) {
    tokenStorageService.saveRefreshToken(refresh)
  }

  return access
}

function redirectToLogin(): void {
  if (window.location.pathname !== '/login') {
    const redirect = encodeURIComponent(
      `${window.location.pathname}${window.location.search}`,
    )

    window.location.assign(
      `/login?redirect=${redirect}`,
    )
  }
}

http.interceptors.request.use(
  (
    config: InternalAxiosRequestConfig,
  ): InternalAxiosRequestConfig => {
    const accessToken =
      tokenStorageService.getAccessToken()

    if (accessToken) {
      config.headers.Authorization =
        `Bearer ${accessToken}`
    }

    config.headers['Accept-Language'] =
      getInterfaceLanguage()

    return config
  },
  (error: AxiosError) => Promise.reject(error),
)

http.interceptors.response.use(
  (response: AxiosResponse) => response,

  async (
    error: AxiosError<ApiErrorResponse>,
  ): Promise<AxiosResponse> => {
    const originalRequest =
      error.config as RetriableRequestConfig | undefined

    if (
      error.response?.status !== 401 ||
      !originalRequest
    ) {
      return Promise.reject(error)
    }

    const isAuthRequest =
      originalRequest.url?.includes('/auth/login/') ||
      originalRequest.url?.includes('/auth/refresh/') ||
      originalRequest.url?.includes('/auth/verify/')

    if (isAuthRequest || originalRequest._retry) {
      tokenStorageService.clearTokens()
      return Promise.reject(error)
    }

    const refreshToken =
      tokenStorageService.getRefreshToken()

    if (!refreshToken) {
      tokenStorageService.clearTokens()
      redirectToLogin()

      return Promise.reject(error)
    }

    originalRequest._retry = true

    try {
      if (!refreshPromise) {
        refreshPromise = requestNewAccessToken().finally(
          () => {
            refreshPromise = null
          },
        )
      }

      const accessToken = await refreshPromise

      originalRequest.headers.Authorization =
        `Bearer ${accessToken}`

      return http(originalRequest)
    } catch (refreshError) {
      tokenStorageService.clearTokens()
      redirectToLogin()

      return Promise.reject(refreshError)
    }
  },
)

export function getApiErrorMessage(
  error: unknown,
  fallback = 'Произошла непредвиденная ошибка',
): string {
  if (!axios.isAxiosError<ApiErrorResponse>(error)) {
    return fallback
  }

  if (error.code === 'ECONNABORTED') {
    return 'Превышено время ожидания ответа сервера'
  }

  if (!error.response) {
    return 'Не удалось подключиться к серверу'
  }

  const data = error.response.data

  if (typeof data?.detail === 'string') {
    return data.detail
  }

  if (typeof data?.message === 'string') {
    return data.message
  }

  const firstFieldError = Object.values(data ?? {}).find(
    (value) =>
      Array.isArray(value) &&
      typeof value[0] === 'string',
  )

  if (Array.isArray(firstFieldError)) {
    return String(firstFieldError[0])
  }

  return error.message || fallback
}

export function isRequestCancelled(
  error: unknown,
): boolean {
  return axios.isCancel(error)
}

export type {
  ApiErrorResponse,
  AxiosRequestConfig,
}
export default http
