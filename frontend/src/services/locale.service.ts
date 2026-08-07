import http from '@/api/http'
import { LOCALE_STORAGE_KEY } from '@/i18n'
import type { AppLocale } from '@/types/locale'

interface UserLocaleResponse {
  interface_language: AppLocale
}

export const localeService = {
  getLocalLocale(): AppLocale | null {
    const locale = localStorage.getItem(
      LOCALE_STORAGE_KEY,
    )

    if (locale === 'ru' || locale === 'uz') {
      return locale
    }

    return null
  },

  saveLocalLocale(locale: AppLocale): void {
    localStorage.setItem(
      LOCALE_STORAGE_KEY,
      locale,
    )
  },

  removeLocalLocale(): void {
    localStorage.removeItem(
      LOCALE_STORAGE_KEY,
    )
  },

  async getUserLocale(): Promise<AppLocale | null> {
    const response =
      await http.get<UserLocaleResponse>(
        '/auth/me/',
      )

    const language =
      response.data.interface_language

    return language === 'ru' ||
      language === 'uz'
      ? language
      : null
  },

  async saveUserLocale(
    locale: AppLocale,
  ): Promise<void> {
    await http.patch('/auth/me/', {
      interface_language: locale,
    })
  },
}
