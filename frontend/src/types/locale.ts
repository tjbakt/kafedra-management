export const SUPPORTED_LOCALES = ['ru', 'uz'] as const

export type AppLocale = (typeof SUPPORTED_LOCALES)[number]

export interface LocaleOption {
  code: AppLocale
  label: string
  shortLabel: string
  flag: string
}

export interface UserLocalePreference {
  language: AppLocale
}
