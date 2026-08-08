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
    forbiddenTitle: 'Доступ запрещён',
    forbiddenDescription:
      'У вашей учётной записи недостаточно прав для просмотра этого раздела.',
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

  access: {
    debugTitle:
      'Права доступа',

    debugDescription:
      'Диагностическая информация о группах и разрешениях текущего пользователя.',

    userInformation:
      'Пользователь',

    groups:
      'Группы',

    permissions:
      'Разрешения',

    noGroups:
      'Группы отсутствуют',

    noGroupsDescription:
      'Пользователь не включён ни в одну группу.',

    noPermissions:
      'Разрешения отсутствуют',

    noPermissionsDescription:
      'Для пользователя не возвращены отдельные разрешения.',
  },

  crud: {
    emptyTitle:
      'Записи не найдены',

    emptyDescription:
      'По заданным условиям записи отсутствуют.',

    paginationReport:
      'Показано {first}–{last} из {totalRecords}',

    validationFailed:
      'Проверьте введённые данные',

    createTitle:
      'Создание записи',

    editTitle:
      'Редактирование записи',

    viewTitle:
      'Просмотр записи',

    deleteTitle:
      'Удаление записи',

    created:
      'Запись успешно создана',

    updated:
      'Запись успешно обновлена',

    deleted:
      'Запись успешно удалена',

    loadError:
      'Не удалось загрузить данные',

    saveError:
      'Не удалось сохранить данные',

    deleteError:
      'Не удалось удалить запись',

    filters:
      'Фильтры',

    clearFilters:
      'Очистить фильтры',

    rowsPerPage:
      'Записей на странице',

    infrastructureTitle:
      'CRUD-инфраструктура',
  },

  departments: {
    title:
      'Кафедры',

    description:
      'Управление кафедрами, их принадлежностью к факультетам, контактными данными и статусом.',

    create:
      'Создать кафедру',

    createTitle:
      'Создание кафедры',

    editTitle:
      'Редактирование кафедры',

    detailsTitle:
      'Информация о кафедре',

    archive:
      'Архивировать',

    archiveTitle:
      'Архивирование кафедры',

    archiveConfirm:
      'Архивировать кафедру «{name}»? Запись можно будет восстановить из архива.',

    archived:
      'Кафедра перемещена в архив',

    active:
      'Активна',

    inactive:
      'Неактивна',

    allStatuses:
      'Все статусы',

    allUniversities:
      'Все университеты',

    allFaculties:
      'Все факультеты',

    searchPlaceholder:
      'Поиск по коду или названию...',

    fields: {
      code:
        'Код',

      name:
        'Название',

      nameRu:
        'Название на русском',

      nameUz:
        'Название на узбекском',

      shortNameRu:
        'Краткое название на русском',

      shortNameUz:
        'Краткое название на узбекском',

      university:
        'Университет',

      faculty:
        'Факультет',

      head:
        'Заведующий кафедрой',

      phone:
        'Телефон',

      email:
        'Электронная почта',

      room:
        'Аудитория / кабинет',

      sortOrder:
        'Порядок сортировки',

      active:
        'Активная кафедра',

      status:
        'Статус',

      createdAt:
        'Создано',

      createdBy:
        'Создал',

      updatedAt:
        'Изменено',

      updatedBy:
        'Изменил',
    },

    placeholders: {
      faculty:
        'Выберите факультет',
    },

    sections: {
      general:
        'Основная информация',

      contacts:
        'Контактная информация',

      audit:
        'История изменений',
    },

    validation: {
      facultyRequired:
        'Выберите факультет',

      codeRequired:
        'Введите код кафедры',

      nameRuRequired:
        'Введите название на русском языке',

      nameUzRequired:
        'Введите название на узбекском языке',

      invalidEmail:
        'Введите корректный адрес электронной почты',
    },
  },

  staff: {
    title:
      'Преподаватели и сотрудники',

    description:
      'Кадровые карточки преподавателей и сотрудников университета.',

    create:
      'Добавить сотрудника',

    createTitle:
      'Создание карточки сотрудника',

    editTitle:
      'Редактирование карточки сотрудника',

    detailsTitle:
      'Карточка сотрудника',

    archive:
      'Архивировать',

    archiveTitle:
      'Архивирование сотрудника',

    archiveConfirm:
      'Архивировать карточку «{name}»? Запись можно будет восстановить из архива.',

    archived:
      'Карточка сотрудника перемещена в архив',

    working:
      'Работает',

    notWorking:
      'Не работает',

    allStatuses:
      'Все статусы',

    allDegrees:
      'Все учёные степени',

    allTitles:
      'Все учёные звания',

    searchPlaceholder:
      'Поиск по ФИО, табельному номеру, телефону или email...',

    genderMale:
      'Мужской',

    genderFemale:
      'Женский',

    genderNotSpecified:
      'Не указан',

    primaryEmployment:
      'Основное',

    rateShort:
      'ставки',

    noEmployments:
      'Трудовые назначения пока отсутствуют.',

    fields: {
      personnelNumber:
        'Табельный номер',

      fullName:
        'ФИО',

      lastName:
        'Фамилия',

      firstName:
        'Имя',

      middleName:
        'Отчество',

      gender:
        'Пол',

      birthDate:
        'Дата рождения',

      phone:
        'Телефон',

      email:
        'Электронная почта',

      academicDegree:
        'Учёная степень',

      academicTitle:
        'Учёное звание',

      degreeDate:
        'Дата присуждения степени',

      titleDate:
        'Дата присвоения звания',

      active:
        'Сотрудник работает',

      status:
        'Статус',

      notes:
        'Примечание',

      username:
        'Пользователь системы',

      createdAt:
        'Создано',

      createdBy:
        'Создал',

      updatedAt:
        'Изменено',

      updatedBy:
        'Изменил',
    },

    sections: {
      personal:
        'Личные данные',

      contacts:
        'Контактные данные',

      academic:
        'Учёная степень и звание',

      additional:
        'Дополнительная информация',

      employments:
        'Трудовые назначения',

      audit:
        'История изменений',
    },

    validation: {
      personnelNumberRequired:
        'Введите табельный номер',

      lastNameRequired:
        'Введите фамилию',

      firstNameRequired:
        'Введите имя',

      invalidEmail:
        'Введите корректный адрес электронной почты',

      degreeDateWithoutDegree:
        'Нельзя указать дату присуждения без учёной степени',

      titleDateWithoutTitle:
        'Нельзя указать дату присвоения без учёного звания',

      birthDateFuture:
        'Дата рождения не может быть в будущем',
    },
  },
}

export default ru
