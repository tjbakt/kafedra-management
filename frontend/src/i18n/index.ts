import { createI18n } from 'vue-i18n'

import ru from '@/i18n/locales/ru'
import uz from '@/i18n/locales/uz'
import type { AppLocale } from '@/types/locale'

export const DEFAULT_LOCALE: AppLocale = 'ru'
export const LOCALE_STORAGE_KEY = 'kafedra.interface-language'

function getSavedLocale(): AppLocale {
  const savedLocale = localStorage.getItem(LOCALE_STORAGE_KEY)

  return savedLocale === 'uz' || savedLocale === 'ru'
    ? savedLocale
    : DEFAULT_LOCALE
}

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: getSavedLocale(),
  fallbackLocale: DEFAULT_LOCALE,
  messages: {
    ru,
    uz,
  },
  missingWarn: import.meta.env.DEV,
  fallbackWarn: import.meta.env.DEV,
})

export default i18n
