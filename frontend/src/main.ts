import { createPinia } from 'pinia'
import { createApp } from 'vue'

import Aura from '@primeuix/themes/aura'
import ConfirmationService from 'primevue/confirmationservice'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import Tooltip from 'primevue/tooltip'

import 'primeicons/primeicons.css'
import '@/styles/main.css'

import App from './App.vue'
import i18n, {
  DEFAULT_LOCALE,
} from './i18n'
import router from './router'

import { primeVueLocales } from '@/i18n/primevue-locales'
import { useLocaleStore } from '@/stores/locale'
import { createCanDirective } from '@/directives/can'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(i18n)

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
        order:
          'theme, base, primevue, utilities',
      },
    },
  },

  locale:
    primeVueLocales[
      localeStore.locale ?? DEFAULT_LOCALE
    ],
})

app.use(ToastService)
app.use(ConfirmationService)

app.directive('tooltip', Tooltip)
app.directive('can',
  createCanDirective(pinia),
)

app.use(router)

router.isReady().then(() => {
  app.mount('#app')
})
