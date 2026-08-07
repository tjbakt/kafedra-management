import type { AxiosInstance } from 'axios'

import http from '@/api/http'
import type {
  AuthUser,
  ChangePasswordPayload,
  LoginCredentials,
  LoginResponse,
  LogoutRequest,
  RefreshTokenRequest,
  RefreshTokenResponse,
  UpdateProfilePayload,
  VerifyTokenRequest,
} from '@/types/auth'

const AUTH_BASE_URL = '/auth'

export const authService = {
  async login(
    credentials: LoginCredentials,
  ): Promise<LoginResponse> {
    const response = await http.post<LoginResponse>(
      `${AUTH_BASE_URL}/login/`,
      credentials,
    )

    return response.data
  },

  async refresh(
    refreshToken: string,
    client: AxiosInstance = http,
  ): Promise<RefreshTokenResponse> {
    const payload: RefreshTokenRequest = {
      refresh: refreshToken,
    }

    const response = await client.post<RefreshTokenResponse>(
      `${AUTH_BASE_URL}/refresh/`,
      payload,
    )

    return response.data
  },

  async verify(token: string): Promise<void> {
    const payload: VerifyTokenRequest = {
      token,
    }

    await http.post(`${AUTH_BASE_URL}/verify/`, payload)
  },

  async logout(refreshToken: string): Promise<void> {
    const payload: LogoutRequest = {
      refresh: refreshToken,
    }

    await http.post(`${AUTH_BASE_URL}/logout/`, payload)
  },

  async getCurrentUser(): Promise<AuthUser> {
    const response = await http.get<AuthUser>(
      `${AUTH_BASE_URL}/me/`,
    )

    return response.data
  },

  async updateProfile(
    payload: UpdateProfilePayload,
  ): Promise<AuthUser> {
    const response = await http.patch<AuthUser>(
      `${AUTH_BASE_URL}/me/`,
      payload,
    )

    return response.data
  },

  async changePassword(
    payload: ChangePasswordPayload,
  ): Promise<void> {
    await http.post(
      `${AUTH_BASE_URL}/change-password/`,
      payload,
    )
  },
}
