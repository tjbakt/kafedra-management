<script setup lang="ts">
import { watch } from 'vue'
import { usePrimeVue } from 'primevue/config'

import { primeVueLocales } from '@/i18n/primevue-locales'
import { useLocaleStore } from '@/stores/locale'

const primeVue = usePrimeVue()
const localeStore = useLocaleStore()

watch(
  () => localeStore.locale,
  (locale) => {
    const nextLocale = primeVueLocales[locale]

    if (primeVue.config.locale) {
      Object.assign(
        primeVue.config.locale,
        nextLocale,
      )
    } else {
      primeVue.config.locale = {
        ...nextLocale,
      }
    }
  },
  {
    immediate: true,
  },
)
</script>

<template>
  <span
    class="locale-synchronizer"
    aria-hidden="true"
  />
</template>

<style scoped>
.locale-synchronizer {
  display: none;
}
</style>
