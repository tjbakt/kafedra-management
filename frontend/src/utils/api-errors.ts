import axios from 'axios'

import type {
  DrfValidationResponse,
  FieldErrors,
  NormalizedApiError,
} from '@/types/validation'

const TECHNICAL_CODES = new Set([
  'required',
  'blank',
  'null',
  'invalid',
  'invalid_choice',
  'does_not_exist',
  'unique',
  'null_value',
])

const FIELD_LABELS: Record<string, string> = {
  id: 'Идентификатор',

  code: 'Код',
  name: 'Наименование',

  academic_year: 'Учебный год',
  academic_year_id: 'Учебный год',

  academic_semester: 'Учебный семестр',
  academic_semester_id: 'Учебный семестр',

  semester: 'Семестр',
  semester_number: 'Номер семестра',

  curriculum: 'Учебный план',
  curriculum_id: 'Учебный план',

  discipline: 'Дисциплина',
  discipline_id: 'Дисциплина',

  workload_type: 'Вид нагрузки',
  workload_type_id: 'Вид нагрузки',

  teaching_stream: 'Код потока',
  teaching_stream_id: 'Учебный поток',

  student_group: 'Учебная группа',
  student_group_id: 'Учебная группа',

  group_semester: 'Семестр группы',
  group_semester_id: 'Семестр группы',

  teaching_department: 'Кафедра',
  teaching_department_id: 'Кафедра',

  department: 'Кафедра',
  department_id: 'Кафедра',

  faculty: 'Факультет',
  faculty_id: 'Факультет',

  organization: 'Организация',
  organization_id: 'Организация',

  teacher: 'Преподаватель',
  teacher_id: 'Преподаватель',

  staff: 'Сотрудник',
  staff_id: 'Сотрудник',

  position: 'Должность',
  position_id: 'Должность',

  academic_degree: 'Учёная степень',
  academic_degree_id: 'Учёная степень',

  academic_title: 'Учёное звание',
  academic_title_id: 'Учёное звание',

  quantity: 'Количество',
  hours: 'Часы',
  base_hours: 'Базовые часы',
  total_hours: 'Всего часов',

  semester_numbers: 'Семестры',

  status: 'Статус',
  is_active: 'Активность',
  is_archived: 'Архивный статус',

  first_name: 'Имя',
  last_name: 'Фамилия',
  middle_name: 'Отчество',

  email: 'Email',
  phone: 'Телефон',

  username: 'Имя пользователя',
  password: 'Пароль',

  start_date: 'Дата начала',
  end_date: 'Дата окончания',

  start_time: 'Время начала',
  end_time: 'Время окончания',

  amount: 'Количество',
  value: 'Значение',

  description: 'Описание',
  comment: 'Комментарий',
}

function normalizeErrorValue(value: unknown): string[] {
  if (typeof value === 'string') {
    return [value]
  }

  if (
    typeof value === 'number' ||
    typeof value === 'boolean'
  ) {
    return [String(value)]
  }

  if (Array.isArray(value)) {
    return value.flatMap(normalizeErrorValue)
  }

  if (value && typeof value === 'object') {
    return Object.values(value).flatMap(normalizeErrorValue)
  }

  return []
}

function unique(values: string[]): string[] {
  return [
    ...new Set(
      values
        .map((value) => value.trim())
        .filter(Boolean),
    ),
  ]
}

function cleanMessages(messages: string[]): string[] {
  const normalized = unique(messages)

  /*
   * Backend иногда возвращает одновременно:
   *
   * [
   *   "Обязательное поле.",
   *   "required"
   * ]
   *
   * Пользователю нужен первый, человекочитаемый вариант.
   */
  const humanMessages = normalized.filter(
    (message) =>
      !TECHNICAL_CODES.has(
        message.toLowerCase(),
      ),
  )

  if (humanMessages.length > 0) {
    return humanMessages
  }

  /*
   * Если backend прислал только технический код,
   * всё равно показываем нормальное сообщение.
   */
  return normalized.map((message) => {
    switch (message.toLowerCase()) {
      case 'required':
        return 'Обязательное поле.'

      case 'blank':
        return 'Поле не может быть пустым.'

      case 'null':
      case 'null_value':
        return 'Поле не может быть пустым.'

      case 'invalid':
        return 'Указано некорректное значение.'

      case 'invalid_choice':
        return 'Выбрано недопустимое значение.'

      case 'does_not_exist':
        return 'Выбранное значение не найдено.'

      case 'unique':
        return 'Такое значение уже существует.'

      default:
        return message
    }
  })
}

function getFieldLabel(field: string): string {
  if (FIELD_LABELS[field]) {
    return FIELD_LABELS[field]
  }

  const lastPart =
    field.split('.').pop() ?? field

  if (FIELD_LABELS[lastPart]) {
    return FIELD_LABELS[lastPart]
  }

  return lastPart
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) =>
      char.toUpperCase(),
    )
}

function isTechnicalResponseKey(
  key: string,
): boolean {
  return new Set([
    'success',
    'status_code',
    'status',
    'error',
    'code',
    'detail',
    'message',
    'non_field_errors',
    'errors',
  ]).has(key)
}

export function normalizeApiError(
  error: unknown,
  fallbackMessage =
    'Произошла непредвиденная ошибка',
): NormalizedApiError {
  if (!axios.isAxiosError<DrfValidationResponse>(error)) {
    return {
      message: fallbackMessage,
      fieldErrors: {},
      nonFieldErrors: [],
      status: null,
    }
  }

  const status =
    error.response?.status ?? null

  const data = error.response?.data

  if (!data) {
    return {
      message: fallbackMessage,
      fieldErrors: {},
      nonFieldErrors: [],
      status,
    }
  }

  const fieldErrors: FieldErrors = {}
  const nonFieldErrors: string[] = []

  /*
   * Обрабатываем обычный DRF:
   *
   * {
   *   "code": ["Обязательное поле."]
   * }
   */
  Object.entries(data).forEach(
    ([field, value]) => {
      if (isTechnicalResponseKey(field)) {
        return
      }

      const messages = cleanMessages(
        normalizeErrorValue(value),
      )

      if (messages.length > 0) {
        fieldErrors[field] = messages
      }
    },
  )

  /*
   * Обрабатываем наш стандартный envelope:
   *
   * {
   *   "success": false,
   *   "status_code": 400,
   *   "error": "validation_error",
   *   "errors": {
   *     "code": [...]
   *   }
   * }
   */
  if (
    data.errors &&
    typeof data.errors === 'object' &&
    !Array.isArray(data.errors)
  ) {
    Object.entries(data.errors).forEach(
      ([field, value]) => {
        const messages = cleanMessages(
          normalizeErrorValue(value),
        )

        if (!messages.length) {
          return
        }

        if (
          field === 'non_field_errors' ||
          field === 'detail'
        ) {
          nonFieldErrors.push(...messages)
          return
        }

        fieldErrors[field] = unique([
          ...(fieldErrors[field] ?? []),
          ...messages,
        ])
      },
    )
  }

  /*
   * Общие ошибки, не относящиеся
   * к конкретному полю.
   */
  if (
    Array.isArray(
      data.non_field_errors,
    )
  ) {
    nonFieldErrors.push(
      ...cleanMessages(
        data.non_field_errors.flatMap(
          normalizeErrorValue,
        ),
      ),
    )
  }

  const normalizedNonFieldErrors =
    unique(nonFieldErrors)

  /*
   * Для 400 с ошибками полей НЕ используем
   * "Request failed with status code 400".
   *
   * Такая строка техническая и не помогает
   * пользователю понять проблему.
   */
  const firstFieldError =
    Object.values(fieldErrors)
      .flatMap(
        (messages) => messages,
      )[0]

  const message =
    normalizedNonFieldErrors[0] ??
    firstFieldError ??
    (
      typeof data.detail === 'string'
        ? data.detail
        : typeof data.message === 'string'
          ? data.message
          : fallbackMessage
    )

  return {
    message,
    fieldErrors,
    nonFieldErrors:
      normalizedNonFieldErrors,
    status,
  }
}

export function getFieldError(
  errors: FieldErrors,
  field: string,
): string {
  return errors[field]?.[0] ?? ''
}

export function hasFieldErrors(
  errors: FieldErrors,
): boolean {
  return Object.keys(errors).length > 0
}

export function getApiErrorDetails(
  error: unknown,
): string[] {
  const normalized =
    normalizeApiError(error)

  const details: string[] = []

  Object.entries(
    normalized.fieldErrors,
  ).forEach(([field, messages]) => {
    const label =
      getFieldLabel(field)

    messages.forEach((message) => {
      details.push(
        `${label}: ${message}`,
      )
    })
  })

  details.push(
    ...normalized.nonFieldErrors,
  )

  return unique(details)
}

export function getFieldErrorLabel(
  field: string,
): string {
  return getFieldLabel(field)
}

export {
  getFieldLabel,
}
