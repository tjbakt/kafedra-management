import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import i18n, {
  DEFAULT_LOCALE,
} from '@/i18n'
import { primeVueLocales } from '@/i18n/primevue-locales'
import { refreshDocumentTitle } from '@/router'
import { localeService } from '@/services/locale.service'
import type {
  AppLocale,
  LocaleOption,
} from '@/types/locale'

const DEFAULT_LOCALE_OPTION: LocaleOption = {
  code: 'ru',
  label: 'Русский',
  shortLabel: 'RU',
  flag: ' ',
}

const LOCALE_OPTIONS: readonly LocaleOption[] = [
  DEFAULT_LOCALE_OPTION,
  {
    code: 'uz',
    label: 'O‘zbekcha',
    shortLabel: 'UZ',
    flag: ' ',
  },
]

export const useLocaleStore = defineStore(
  'locale',
  () => {
    const locale = ref<AppLocale>(
      localeService.getLocalLocale() ??
        DEFAULT_LOCALE,
    )

    const initialized = ref(false)
    const synchronizing = ref(false)

    const localeOptions = LOCALE_OPTIONS

    const currentLocaleOption =
      computed<LocaleOption>(() => {
        return (
          localeOptions.find(
            (option) =>
              option.code === locale.value,
          ) ?? DEFAULT_LOCALE_OPTION
        )
      })

    function applyDocumentLocale(
      value: AppLocale,
    ): void {
      document.documentElement.lang = value
    }

    function applyI18nLocale(
      value: AppLocale,
    ): void {
      i18n.global.locale.value = value
    }

    function getPrimeVueLocale(
      value: AppLocale,
    ) {
      return primeVueLocales[value]
    }

    function initialize(): void {
      const savedLocale =
        localeService.getLocalLocale() ??
        DEFAULT_LOCALE

      locale.value = savedLocale

      applyI18nLocale(savedLocale)
      applyDocumentLocale(savedLocale)

      initialized.value = true
    }

    function setLocale(
      value: AppLocale,
    ): void {
      locale.value = value

      localeService.saveLocalLocale(value)

      applyI18nLocale(value)
      applyDocumentLocale(value)
      refreshDocumentTitle()
    }

    async function loadUserLocale(): Promise<void> {
      synchronizing.value = true

      try {
        const userLocale =
          await localeService.getUserLocale()

        if (userLocale) {
          setLocale(userLocale)
        }
      } finally {
        synchronizing.value = false
      }
    }

    async function saveUserLocale(
      value: AppLocale,
    ): Promise<void> {
      setLocale(value)

      synchronizing.value = true

      try {
        await localeService.saveUserLocale(
          value,
        )
      } finally {
        synchronizing.value = false
      }
    }

    return {
      locale,
      initialized,
      synchronizing,
      localeOptions,
      currentLocaleOption,
      initialize,
      setLocale,
      loadUserLocale,
      saveUserLocale,
      getPrimeVueLocale,
    }
  },
)
