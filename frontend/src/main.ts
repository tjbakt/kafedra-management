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

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

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
  locale: {
    startsWith: 'Начинается с',
    contains: 'Содержит',
    notContains: 'Не содержит',
    endsWith: 'Заканчивается на',
    equals: 'Равно',
    notEquals: 'Не равно',
    noFilter: 'Без фильтра',
    lt: 'Меньше',
    lte: 'Меньше или равно',
    gt: 'Больше',
    gte: 'Больше или равно',
    dateIs: 'Дата равна',
    dateIsNot: 'Дата не равна',
    dateBefore: 'Дата до',
    dateAfter: 'Дата после',
    clear: 'Очистить',
    apply: 'Применить',
    matchAll: 'Все условия',
    matchAny: 'Любое условие',
    addRule: 'Добавить правило',
    removeRule: 'Удалить правило',
    accept: 'Да',
    reject: 'Нет',
    choose: 'Выбрать',
    upload: 'Загрузить',
    cancel: 'Отмена',
    completed: 'Завершено',
    pending: 'Ожидание',
    fileSizeTypes: ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ'],
    dayNames: ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'],
    dayNamesShort: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
    dayNamesMin: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
    monthNames: [
      'Январь',
      'Февраль',
      'Март',
      'Апрель',
      'Май',
      'Июнь',
      'Июль',
      'Август',
      'Сентябрь',
      'Октябрь',
      'Ноябрь',
      'Декабрь',
    ],
    monthNamesShort: [
      'Янв',
      'Фев',
      'Мар',
      'Апр',
      'Май',
      'Июн',
      'Июл',
      'Авг',
      'Сен',
      'Окт',
      'Ноя',
      'Дек',
    ],
    today: 'Сегодня',
    weekHeader: 'Нед',
    firstDayOfWeek: 1,
    dateFormat: 'dd.mm.yy',
    weak: 'Слабый',
    medium: 'Средний',
    strong: 'Надёжный',
    passwordPrompt: 'Введите пароль',
    emptyFilterMessage: 'Результаты не найдены',
    emptyMessage: 'Нет доступных данных',
  },
})

app.use(ToastService)
app.use(ConfirmationService)

app.directive('tooltip', Tooltip)

app.mount('#app')
