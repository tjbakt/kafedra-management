const ru = {
  app: {
    name: 'Kafedra Management',
    title: 'Управление учебным процессом',
    subtitle: 'Информационная система кафедры',
    version: 'Версия {version}',
    frontendLayout: 'Frontend layout',
    allRightsReserved: 'Все права защищены.',
    systemWorking: 'Система работает',
  },

  common: {
    create: 'Создать',
    add: 'Добавить',
    edit: 'Редактировать',
    delete: 'Удалить',
    save: 'Сохранить',
    cancel: 'Отмена',
    close: 'Закрыть',
    confirm: 'Подтвердить',
    back: 'Назад',
    next: 'Далее',
    search: 'Поиск',
    filter: 'Фильтр',
    reset: 'Сбросить',
    clear: 'Очистить',
    refresh: 'Обновить',
    export: 'Экспорт',
    import: 'Импорт',
    print: 'Печать',
    download: 'Скачать',
    upload: 'Загрузить',
    view: 'Просмотр',
    actions: 'Действия',
    yes: 'Да',
    no: 'Нет',
    loading: 'Загрузка...',
    saving: 'Сохранение...',
    noData: 'Нет доступных данных',
    required: 'Обязательное поле',
    success: 'Успешно',
    information: 'Информация',
    warning: 'Предупреждение',
    error: 'Ошибка',
    important: 'Важно',
    status: 'Статус',
    language: 'Язык',
    lightTheme: 'Светлая тема',
    darkTheme: 'Тёмная тема',
    openMenu: 'Открыть или свернуть меню',
    openNotifications: 'Открыть уведомления',
  },

  languages: {
    ru: 'Русский',
    uz: 'O‘zbekcha',
    select: 'Выберите язык',
    changed: 'Язык интерфейса изменён',
    saved: 'Основной язык интерфейса сохранён',
    saveError: 'Не удалось сохранить выбранный язык',
  },

  navigation: {
    dashboard: 'Главная',
    organizationalStructure: 'Организационная структура',
    departments: 'Кафедры',
    teachers: 'Преподаватели',
    studentGroups: 'Студенческие группы',
    educationalProcess: 'Учебный процесс',
    disciplines: 'Дисциплины',
    curricula: 'Учебные планы',
    workload: 'Учебная нагрузка',
    schedules: 'Расписание',
    analytics: 'Аналитика',
    reports: 'Отчёты',
    system: 'Система',
    settings: 'Настройки',
  },

  profile: {
    profile: 'Профиль',
    settings: 'Настройки',
    logout: 'Выйти',
    administrator: 'Администратор',
    systemAdministrator: 'Системный администратор',
  },

  notifications: {
    title: 'Уведомления',
    unread: 'Нет непрочитанных | {count} непрочитанное | {count} непрочитанных',
    markAllAsRead: 'Прочитать все',
    empty: 'Уведомлений пока нет',
    clear: 'Очистить',
    systemReady: 'Система готова',
    frontendConnected: 'Frontend-каркас успешно подключён.',
    workloadTitle: 'Учебная нагрузка',
    workloadCheck: 'Необходимо проверить распределение часов.',
    directoryUpdated: 'Обновление справочника',
    departmentsUpdated: 'Данные кафедр были обновлены.',
    justNow: 'Только что',
    minutesAgo: '{count} минут назад',
    hourAgo: '1 час назад',
  },

  dashboard: {
    title: 'Панель управления',
    description:
      'Общая информация о состоянии учебного процесса и распределении нагрузки.',

    teachers: 'Преподаватели',
    disciplines: 'Дисциплины',
    groups: 'Учебные группы',
    totalWorkload: 'Общая нагрузка',
    hours: 'часов',

    teachersChange: '+3 за месяц',
    activePlans: '12 активных планов',
    studentsCount: '824 студента',
    currentYear: 'На текущий учебный год',

    workloadDistribution: 'Распределение учебной нагрузки',
    workloadDistributionDescription:
      'Состояние подготовки нагрузки на текущий учебный год',
    openModule: 'Открыть модуль',

    distributed: 'Распределено',
    checked: 'Проверено',
    approved: 'Утверждено',
    inProgress: 'Выполняется',
    requiresCheck: 'Требуется проверка',
    processing: 'В процессе',

    quickActions: 'Быстрые действия',
    quickActionsDescription: 'Наиболее часто используемые разделы',
    manageEmployees: 'Управление сотрудниками',
    viewAndEdit: 'Просмотр и редактирование',
    distributeHours: 'Распределение часов',
    pdfAndExcel: 'PDF и Excel',

    showToast: 'Показать Toast',
    checkDialog: 'Проверить Dialog',
    interfaceWorks: 'Интерфейс работает',
    toastConnected: 'Глобальная система Toast успешно подключена.',
    confirmDemoAction: 'Подтвердить выполнение демонстрационного действия?',
    actionConfirmed: 'Действие подтверждено',
  },

  auth: {
    loginTitle: 'Вход в систему',
    loginDescription: 'Введите данные своей учётной записи.',
    username: 'Имя пользователя',
    usernamePlaceholder: 'Введите имя пользователя',
    password: 'Пароль',
    passwordPlaceholder: 'Введите пароль',
    rememberMe: 'Запомнить меня',
    forgotPassword: 'Забыли пароль?',
    login: 'Войти',
    loggingIn: 'Выполняется вход...',
    loginSuccess: 'Вход выполнен',
    welcome: 'Добро пожаловать, {name}!',
    loginFailed: 'Не удалось выполнить вход',
    invalidCredentials:
      'Неверное имя пользователя или пароль.',
    sessionExpired: 'Сессия завершена',
    sessionExpiredDescription:
      'Войдите в систему повторно.',
    logoutSuccess: 'Выход выполнен',
    logoutSuccessDescription:
      'Вы успешно вышли из системы.',
    usernameRequired: 'Введите имя пользователя',
    passwordRequired: 'Введите пароль',
    passwordMinLength:
      'Пароль должен содержать минимум 4 символа',
    passwordRecovery: 'Восстановление пароля',
    passwordRecoveryLater:
      'Функция будет подключена позже.',
    changePassword: 'Смена пароля',
    passwordChangeRequired:
      'Необходимо изменить временный пароль.',
    currentPassword: 'Текущий пароль',
    newPassword: 'Новый пароль',
    confirmPassword: 'Подтверждение пароля',
  },

  modules: {
    prepared: 'Модуль подготовлен',
    preparedDescription:
      'Маршрут, layout и базовые компоненты подключены. CRUD-интерфейс будет реализован на соответствующем этапе.',
    demoMode: 'Демонстрационный режим',
    createLater:
      'Форма создания будет добавлена на этапе реализации CRUD.',
    returnHome: 'Вернуться на главную',

    departmentsDescription:
      'Управление кафедрами и организационной структурой.',
    teachersDescription:
      'Справочник преподавателей, ставок, степеней и учёных званий.',
    studentsDescription:
      'Управление академическими группами и контингентом.',
    disciplinesDescription: 'Справочник учебных дисциплин.',
    curriculaDescription:
      'Формирование и сопровождение учебных планов образовательных программ.',
    workloadDescription:
      'Расчёт и распределение учебной нагрузки между преподавателями.',
    schedulesDescription:
      'Планирование и просмотр расписания занятий.',
    reportsDescription:
      'Формирование аналитических отчётов, PDF и Excel.',
    settingsDescription:
      'Пользователи, роли, права доступа и параметры системы.',
  },

  errors: {
    notFoundTitle: 'Страница не найдена',
    notFoundDescription:
      'Запрошенная страница не существует, была перемещена или удалена.',
    unexpected: 'Произошла непредвиденная ошибка',
    serverUnavailable: 'Не удалось подключиться к серверу',
    timeout: 'Превышено время ожидания ответа сервера',
  },

  confirm: {
    deleteHeader: 'Подтверждение удаления',
    deleteMessage:
      'Вы действительно хотите удалить выбранную запись? Это действие нельзя отменить.',
    deleteAccept: 'Удалить',
    actionHeader: 'Подтверждение действия',
  },

  emptyState: {
    title: 'Данные отсутствуют',
    description: 'Для отображения пока нет доступных данных.',
  },
}

export default ru
