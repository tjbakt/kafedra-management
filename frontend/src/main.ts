import { createApp } from 'vue'
import { createPinia } from 'pinia'

import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import Tooltip from 'primevue/tooltip'
import Aura from '@primeuix/themes/aura'

import 'primeicons/primeicons.css'
import '@/styles/main.css'

import App from './App.vue'
import router from './router'
import i18n from './i18n'

import { DEFAULT_LOCALE } from '@/i18n'
import { primeVueLocales } from '@/i18n/primevue-locales'
import { useLocaleStore } from '@/stores/locale'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(i18n)
app.use(router)

const localeStore = useLocaleStore(pinia)
localeStore.initialize()

app.use(PrimeVue, {
  ripple: true,

  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.app-dark',
      cssLayer: {
        name: 'primevue',
        order: 'theme, base, primevue, utilities',
      },
    },
  },

  locale: primeVueLocales[
    localeStore.locale ?? DEFAULT_LOCALE
  ],
})

app.use(ToastService)
app.use(ConfirmationService)

app.directive('tooltip', Tooltip)

app.mount('#app')
