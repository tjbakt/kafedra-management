const ACCESS_TOKEN_KEY = 'kafedra.access-token'
const REFRESH_TOKEN_KEY = 'kafedra.refresh-token'

export const tokenStorageService = {
  getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY)
  },

  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  },

  saveTokens(access: string, refresh: string): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, access)
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
  },

  saveAccessToken(access: string): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, access)
  },

  saveRefreshToken(refresh: string): void {
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
  },

  clearTokens(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  },

  hasTokens(): boolean {
    return Boolean(
      localStorage.getItem(ACCESS_TOKEN_KEY) &&
        localStorage.getItem(REFRESH_TOKEN_KEY),
    )
  },
}
