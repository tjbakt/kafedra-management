import type { AppLocale } from '@/types/locale'

export interface PrimeVueLocaleMessages {
  startsWith: string
  contains: string
  notContains: string
  endsWith: string
  equals: string
  notEquals: string
  noFilter: string
  lt: string
  lte: string
  gt: string
  gte: string
  dateIs: string
  dateIsNot: string
  dateBefore: string
  dateAfter: string
  clear: string
  apply: string
  matchAll: string
  matchAny: string
  addRule: string
  removeRule: string
  accept: string
  reject: string
  choose: string
  upload: string
  cancel: string
  completed: string
  pending: string
  fileSizeTypes: string[]
  dayNames: string[]
  dayNamesShort: string[]
  dayNamesMin: string[]
  monthNames: string[]
  monthNamesShort: string[]
  today: string
  weekHeader: string
  firstDayOfWeek: number
  dateFormat: string
  weak: string
  medium: string
  strong: string
  passwordPrompt: string
  emptyFilterMessage: string
  searchMessage: string
  selectionMessage: string
  emptySelectionMessage: string
  emptySearchMessage: string
  emptyMessage: string
}

const ru: PrimeVueLocaleMessages = {
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
  dayNames: [
    'Воскресенье',
    'Понедельник',
    'Вторник',
    'Среда',
    'Четверг',
    'Пятница',
    'Суббота',
  ],
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
  searchMessage: 'Доступно результатов: {0}',
  selectionMessage: 'Выбрано элементов: {0}',
  emptySelectionMessage: 'Нет выбранных элементов',
  emptySearchMessage: 'Результаты не найдены',
  emptyMessage: 'Нет доступных данных',
}

const uz: PrimeVueLocaleMessages = {
  startsWith: 'Boshlanadi',
  contains: 'O‘z ichiga oladi',
  notContains: 'O‘z ichiga olmaydi',
  endsWith: 'Tugaydi',
  equals: 'Teng',
  notEquals: 'Teng emas',
  noFilter: 'Filtrsiz',
  lt: 'Kichik',
  lte: 'Kichik yoki teng',
  gt: 'Katta',
  gte: 'Katta yoki teng',
  dateIs: 'Sana teng',
  dateIsNot: 'Sana teng emas',
  dateBefore: 'Sanadan oldin',
  dateAfter: 'Sanadan keyin',
  clear: 'Tozalash',
  apply: 'Qo‘llash',
  matchAll: 'Barcha shartlar',
  matchAny: 'Istalgan shart',
  addRule: 'Qoida qo‘shish',
  removeRule: 'Qoidani o‘chirish',
  accept: 'Ha',
  reject: 'Yo‘q',
  choose: 'Tanlash',
  upload: 'Yuklash',
  cancel: 'Bekor qilish',
  completed: 'Bajarildi',
  pending: 'Kutilmoqda',
  fileSizeTypes: ['B', 'KB', 'MB', 'GB', 'TB'],
  dayNames: [
    'Yakshanba',
    'Dushanba',
    'Seshanba',
    'Chorshanba',
    'Payshanba',
    'Juma',
    'Shanba',
  ],
  dayNamesShort: ['Yak', 'Dush', 'Sesh', 'Chor', 'Pay', 'Jum', 'Shan'],
  dayNamesMin: ['Ya', 'Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh'],
  monthNames: [
    'Yanvar',
    'Fevral',
    'Mart',
    'Aprel',
    'May',
    'Iyun',
    'Iyul',
    'Avgust',
    'Sentabr',
    'Oktabr',
    'Noyabr',
    'Dekabr',
  ],
  monthNamesShort: [
    'Yan',
    'Fev',
    'Mar',
    'Apr',
    'May',
    'Iyn',
    'Iyl',
    'Avg',
    'Sen',
    'Okt',
    'Noy',
    'Dek',
  ],
  today: 'Bugun',
  weekHeader: 'Hafta',
  firstDayOfWeek: 1,
  dateFormat: 'dd.mm.yy',
  weak: 'Zaif',
  medium: 'O‘rtacha',
  strong: 'Ishonchli',
  passwordPrompt: 'Parolni kiriting',
  emptyFilterMessage: 'Natijalar topilmadi',
  searchMessage: '{0} ta natija mavjud',
  selectionMessage: '{0} ta element tanlandi',
  emptySelectionMessage: 'Element tanlanmagan',
  emptySearchMessage: 'Natijalar topilmadi',
  emptyMessage: 'Ma’lumotlar mavjud emas',
}

export const primeVueLocales: Record<AppLocale, PrimeVueLocaleMessages> = {
  ru,
  uz,
}
