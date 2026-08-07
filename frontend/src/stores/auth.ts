import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { getApiErrorMessage } from '@/api/http'
import { authService } from '@/services/auth.service'
import { tokenStorageService } from '@/services/token-storage.service'
import { useLocaleStore } from '@/stores/locale'
import type {
  AuthUser,
  ChangePasswordPayload,
  LoginCredentials,
  UpdateProfilePayload,
} from '@/types/auth'

export const useAuthStore = defineStore(
  'auth',
  () => {
    const user = ref<AuthUser | null>(null)
    const initialized = ref(false)
    const loading = ref(false)
    const loginError = ref<string | null>(null)

    const isAuthenticated = computed(
      () =>
        Boolean(user.value) &&
        tokenStorageService.hasTokens(),
    )

    const displayName = computed(() => {
      if (!user.value) {
        return ''
      }

      return (
        user.value.full_name ||
        user.value.username
      )
    })

    const initials = computed(() => {
      if (!user.value) {
        return 'US'
      }

      const source =
        user.value.full_name ||
        user.value.username

      const parts = source
        .trim()
        .split(/\s+/)
        .filter(Boolean)

      if (parts.length >= 2) {
        return `${parts[0]?.[0] ?? ''}${
          parts[1]?.[0] ?? ''
        }`.toUpperCase()
      }

      return source.slice(0, 2).toUpperCase()
    })

    const primaryGroup = computed(() => {
      if (!user.value) {
        return ''
      }

      if (user.value.is_staff) {
        return 'Administrator'
      }

      return user.value.groups[0] || ''
    })

    function setUser(nextUser: AuthUser): void {
      user.value = nextUser

      const localeStore = useLocaleStore()

      if (
        nextUser.interface_language === 'ru' ||
        nextUser.interface_language === 'uz'
      ) {
        localeStore.setLocale(
          nextUser.interface_language,
        )
      }
    }

    async function login(
      credentials: LoginCredentials,
    ): Promise<AuthUser> {
      loading.value = true
      loginError.value = null

      try {
        const response =
          await authService.login(credentials)

        tokenStorageService.saveTokens(
          response.access,
          response.refresh,
        )

        setUser(response.user)

        return response.user
      } catch (error) {
        tokenStorageService.clearTokens()
        user.value = null

        loginError.value = getApiErrorMessage(
          error,
          'Неверное имя пользователя или пароль',
        )

        throw error
      } finally {
        loading.value = false
      }
    }

    async function loadCurrentUser(): Promise<AuthUser> {
      const currentUser =
        await authService.getCurrentUser()

      setUser(currentUser)

      return currentUser
    }

    async function initialize(): Promise<void> {
      if (initialized.value) {
        return
      }

      try {
        if (!tokenStorageService.hasTokens()) {
          user.value = null
          return
        }

        await loadCurrentUser()
      } catch {
        tokenStorageService.clearTokens()
        user.value = null
      } finally {
        initialized.value = true
      }
    }

    async function logout(): Promise<void> {
      const refreshToken =
        tokenStorageService.getRefreshToken()

      try {
        if (refreshToken && user.value) {
          await authService.logout(refreshToken)
        }
      } catch {
        // Локальная сессия должна быть очищена,
        // даже если backend недоступен.
      } finally {
        tokenStorageService.clearTokens()
        user.value = null
      }
    }

    async function updateProfile(
      payload: UpdateProfilePayload,
    ): Promise<AuthUser> {
      const updatedUser =
        await authService.updateProfile(payload)

      setUser(updatedUser)

      return updatedUser
    }

    async function changePassword(
      payload: ChangePasswordPayload,
    ): Promise<void> {
      await authService.changePassword(payload)

      if (user.value) {
        user.value = {
          ...user.value,
          must_change_password: false,
        }
      }
    }

    function hasPermission(
      permission: string,
    ): boolean {
      if (!user.value) {
        return false
      }

      if (user.value.is_staff) {
        return true
      }

      return user.value.permissions.includes(
        permission,
      )
    }

    function hasAnyPermission(
      permissions: string[],
    ): boolean {
      return permissions.some((permission) =>
        hasPermission(permission),
      )
    }

    function hasGroup(group: string): boolean {
      return (
        user.value?.groups.includes(group) ?? false
      )
    }

    function clearLoginError(): void {
      loginError.value = null
    }

    return {
      user,
      initialized,
      loading,
      loginError,
      isAuthenticated,
      displayName,
      initials,
      primaryGroup,
      login,
      logout,
      initialize,
      loadCurrentUser,
      updateProfile,
      changePassword,
      hasPermission,
      hasAnyPermission,
      hasGroup,
      clearLoginError,
    }
  },
)
