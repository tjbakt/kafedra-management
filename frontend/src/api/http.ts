import axios, {
  AxiosError,
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'

interface ApiErrorResponse {
  detail?: string
  message?: string
  errors?: Record<string, string[]>
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api'
const apiTimeout = Number(import.meta.env.VITE_API_TIMEOUT || 15000)

const http: AxiosInstance = axios.create({
  baseURL: apiBaseUrl,
  timeout: apiTimeout,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

http.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const accessToken = localStorage.getItem('access_token')

    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }

    return config
  },
  (error: AxiosError) => Promise.reject(error),
)

http.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError<ApiErrorResponse>) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }

    return Promise.reject(error)
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

  return error.response.data?.detail || error.response.data?.message || error.message || fallback
}

export default http
