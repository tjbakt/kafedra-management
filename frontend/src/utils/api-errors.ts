import axios from 'axios'

import type {
  DrfValidationResponse,
  FieldErrors,
  NormalizedApiError,
} from '@/types/validation'

function normalizeErrorValue(
  value: unknown,
): string[] {
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
    return value
      .flatMap((item) =>
        normalizeErrorValue(item),
      )
      .filter(Boolean)
  }

  if (
    value &&
    typeof value === 'object'
  ) {
    return Object.values(value)
      .flatMap((item) =>
        normalizeErrorValue(item),
      )
      .filter(Boolean)
  }

  return []
}

function normalizeFieldName(
  field: string,
): string {
  const labels: Record<string, string> = {
    id: 'Идентификатор',
    code: 'Код',
    name: 'Наименование',

    academic_year: 'Учебный год',
    academic_semester: 'Учебный семестр',

    semester: 'Семестр',
    semester_number: 'Номер семестра',

    curriculum: 'Учебный план',
    curriculum_id: 'Учебный план',

    discipline: 'Дисциплина',
    discipline_id: 'Дисциплина',

    workload_type: 'Вид нагрузки',
    workload_type_id: 'Вид нагрузки',

    teaching_stream: 'Учебный поток',
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

  if (labels[field]) {
    return labels[field]
  }

  const lastPart = field
    .split('.')
    .pop() ?? field

  if (labels[lastPart]) {
    return labels[lastPart]
  }

  return lastPart
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) =>
      char.toUpperCase(),
    )
}

function getFieldLabel(
  field: string,
): string {
  const labels: Record<string, string> = {
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

    teaching_stream: 'Учебный поток',
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

  const lastPart =
    field.split('.').pop() ?? field

  if (labels[lastPart]) {
    return labels[lastPart]
  }

  return lastPart
    .replace(/_/g, ' ')
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase(),
    )
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
      message:
        error.message || fallbackMessage,
      fieldErrors: {},
      nonFieldErrors: [],
      status,
    }
  }

  const fieldErrors: FieldErrors = {}
  const nonFieldErrors: string[] = []

  if (
    Array.isArray(
      data.non_field_errors,
    )
  ) {
    nonFieldErrors.push(
      ...data.non_field_errors.map(String),
    )
  }

  const ignoredKeys = new Set([
    'detail',
    'message',
    'code',
    'status',
    'non_field_errors',
    'errors',
  ])

  Object.entries(data).forEach(
    ([field, value]) => {
      if (ignoredKeys.has(field)) {
        return
      }

      const messages =
        normalizeErrorValue(value)

      if (messages.length) {
        fieldErrors[field] = messages
      }
    },
  )

  if (
    data.errors &&
    typeof data.errors === 'object' &&
    !Array.isArray(data.errors)
  ) {
    Object.entries(
      data.errors,
    ).forEach(([field, value]) => {
      const messages =
        normalizeErrorValue(value)

      if (!messages.length) {
        return
      }

      if (
        field === 'non_field_errors' ||
        field === 'detail'
      ) {
        nonFieldErrors.push(
          ...messages,
        )
        return
      }

      fieldErrors[field] = [
        ...(fieldErrors[field] ?? []),
        ...messages,
      ]
    })
  }

  const message =
    nonFieldErrors[0] ||
    Object.values(fieldErrors)[0]?.[0] ||
    (typeof data.detail === 'string'
      ? data.detail
      : typeof data.message === 'string'
        ? data.message
        : error.message ||
        fallbackMessage)

  return {
    message,
    fieldErrors,
    nonFieldErrors,
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

  return [
    ...new Set(
      details.filter(Boolean),
    ),
  ]
}

export {
  normalizeFieldName,
}
