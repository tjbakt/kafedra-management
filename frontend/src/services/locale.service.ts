import http from '@/api/http'

import {
  LOCALE_STORAGE_KEY,
} from '@/i18n'
import type {
  AppLocale,
  UserLocalePreference,
} from '@/types/locale'

const USER_PREFERENCE_ENDPOINT = '/users/me/preferences/'

export const localeService = {
  getLocalLocale(): AppLocale | null {
    const locale = localStorage.getItem(LOCALE_STORAGE_KEY)

    if (locale === 'ru' || locale === 'uz') {
      return locale
    }

    return null
  },

  saveLocalLocale(locale: AppLocale): void {
    localStorage.setItem(LOCALE_STORAGE_KEY, locale)
  },

  removeLocalLocale(): void {
    localStorage.removeItem(LOCALE_STORAGE_KEY)
  },

  async getUserLocale(): Promise<AppLocale | null> {
    const response = await http.get<UserLocalePreference>(
      USER_PREFERENCE_ENDPOINT,
    )

    const language = response.data.language

    return language === 'ru' || language === 'uz'
      ? language
      : null
  },

  async saveUserLocale(locale: AppLocale): Promise<void> {
    await http.patch<UserLocalePreference>(
      USER_PREFERENCE_ENDPOINT,
      {
        language: locale,
      },
    )
  },
}
