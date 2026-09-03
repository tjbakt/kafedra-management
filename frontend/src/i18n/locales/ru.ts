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
    staffEmployments: 'Трудовые назначения',
    staffAcademicYears: 'Кадровые данные по годам',
    workloadNorms: 'Нормы нагрузки',
    academicSettings: 'Академические справочники',
    studyPrograms: 'Направления подготовки',
    curriculumReferences: 'Справочники учебного плана',
    curriculumDisciplines: 'Состав учебного плана',
    teachingSetup: 'Подготовка учебных групп',
    teachingStreams: 'Учебные потоки',
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
      general: 'Основная информация',
      contacts: 'Контактная информация',
      audit: 'История изменений',
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

  staffEmployments: {
    title:
      'Трудовые назначения',

    description:
      'Назначение преподавателей и сотрудников на кафедры и должности, учёт вида занятости, ставки и сроков работы.',

    create:
      'Добавить назначение',

    createTitle:
      'Создание трудового назначения',

    editTitle:
      'Редактирование трудового назначения',

    detailsTitle:
      'Трудовое назначение',

    archive:
      'Архивировать',

    archiveTitle:
      'Архивирование назначения',

    archiveConfirm:
      'Архивировать назначение сотрудника «{name}»? Запись можно будет восстановить из архива.',

    archived:
      'Трудовое назначение перемещено в архив',

    active:
      'Активно',

    inactive:
      'Неактивно',

    allStatuses:
      'Все статусы',

    allDepartments:
      'Все кафедры',

    allPositions:
      'Все должности',

    allTypes:
      'Все виды занятости',

    allAssignments:
      'Все назначения',

    primaryOnly:
      'Только основные',

    additionalOnly:
      'Только дополнительные',

    searchPlaceholder:
      'Поиск по сотруднику, кафедре или должности...',

    types: {
      primary:
        'Основное место работы',

      internalPartTime:
        'Внутреннее совместительство',

      externalPartTime:
        'Внешнее совместительство',

      hourly:
        'Почасовая работа',
    },

    fields: {
      staffMember:
        'Сотрудник',

      faculty:
        'Факультет',

      department:
        'Кафедра',

      position:
        'Должность',

      employmentType:
        'Вид занятости',

      rate:
        'Ставка',

      startDate:
        'Дата начала работы',

      endDate:
        'Дата окончания работы',

      primary:
        'Основное назначение',

      active:
        'Назначение активно',

      status:
        'Статус',

      documentNumber:
        'Номер приказа',

      documentDate:
        'Дата приказа',

      notes:
        'Примечание',

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
      assignment:
        'Назначение',

      period:
        'Период работы',

      document:
        'Приказ',

      audit:
        'История изменений',
    },

    validation: {
      staffRequired:
        'Выберите сотрудника',

      departmentRequired:
        'Выберите кафедру',

      positionRequired:
        'Выберите должность',

      startDateRequired:
        'Укажите дату начала работы',

      rateRange:
        'Ставка должна быть от 0,01 до 3,00',

      endBeforeStart:
        'Дата окончания не может быть раньше даты начала',
    },
  },

  staffAcademicYears: {
    title:
      'Кадровые данные по учебным годам',

    description:
      'Фиксация ставки, учёной степени и учёного звания преподавателя для каждого учебного года.',

    create:
      'Добавить запись',

    createTitle:
      'Кадровые данные на учебный год',

    editTitle:
      'Редактирование кадровых данных',

    archive:
      'Архивировать',

    archiveTitle:
      'Архивирование кадровых данных',

    archiveConfirm:
      'Архивировать данные «{name}» за {year}?',

    archived:
      'Кадровые данные перемещены в архив',

    active:
      'Активно',

    inactive:
      'Неактивно',

    current:
      'Текущий',

    closed:
      'Закрыт',

    allYears:
      'Все учебные годы',

    allDepartments:
      'Все кафедры',

    allStatuses:
      'Все статусы',

    searchPlaceholder:
      'Поиск по сотруднику, кафедре, должности, степени или званию...',

    bulkCreate:
      'Заполнить отсутствующие',

    bulkTitle:
      'Массовое заполнение кадровых данных',

    bulkDescription:
      'Система создаст отсутствующие записи по действующим трудовым назначениям, используя текущую ставку, степень и звание.',

    bulkRun:
      'Заполнить',

    bulkCompleted:
      'Массовое заполнение завершено',

    bulkResult:
      'Создано: {created}; восстановлено: {restored}; пропущено: {skipped}; осталось: {missing}.',

    fields: {
      employment:
        'Трудовое назначение',

      staffMember:
        'Сотрудник',

      academicYear:
        'Учебный год',

      department:
        'Кафедра',

      position:
        'Должность',

      rate:
        'Ставка',

      academicDegree:
        'Учёная степень',

      academicTitle:
        'Учёное звание',

      recommendedHours:
        'Норма часов',

      active:
        'Запись активна',

      status:
        'Статус',

      notes:
        'Примечание',
    },

    validation: {
      employmentRequired:
        'Выберите трудовое назначение',

      yearRequired:
        'Выберите учебный год',

      rateRange:
        'Ставка должна быть от 0,01 до 3,00',
    },
  },

  workloadNorms: {
    title:
      'Нормы учебной нагрузки',

    description:
      'Информационные годовые нормы нагрузки по учебному году, размеру ставки, наличию учёной степени и учёного звания.',

    create:
      'Добавить норму',

    createTitle:
      'Создание нормы нагрузки',

    editTitle:
      'Редактирование нормы нагрузки',

    archive:
      'Архивировать',

    archiveTitle:
      'Архивирование нормы',

    archiveConfirm:
      'Архивировать норму за {year}, ставка {rate}?',

    archived:
      'Норма нагрузки перемещена в архив',

    active:
      'Активна',

    inactive:
      'Неактивна',

    allYears:
      'Все учебные годы',

    allStatuses:
      'Все статусы',

    fields: {
      academicYear:
        'Учебный год',

      rate:
        'Ставка',

      hasDegree:
        'Есть учёная степень',

      hasTitle:
        'Есть учёное звание',

      annualHours:
        'Годовая норма часов',

      active:
        'Норма активна',

      status:
        'Статус',

      notes:
        'Примечание',
    },

    validation: {
      yearRequired:
        'Выберите учебный год',

      rateRange:
        'Ставка должна быть от 0,01 до 3,00',

      hoursRange:
        'Годовая норма должна быть от 0 до 10000 часов',
    },
  },

  academicSettings: {
    title: 'Академические справочники',
    description: 'Учебные годы, уровни образования, формы и продолжительность обучения, академические семестры.',
    archiveConfirm: 'Переместить запись в архив?',

    tabs: {
      years: 'Учебные годы',
      levels: 'Уровни образования',
      forms: 'Формы обучения',
      durations: 'Продолжительность',
      semesters: 'Семестры',
      workloadNorms: 'Нормы учебной нагрузки',
    },

    common: {
      code:
        'Код',

      name:
        'Название',

      nameRu:
        'Название на русском',

      nameUz:
        'Название на узбекском',

      sortOrder:
        'Порядок',

      active:
        'Активно',
    },

    academicYears: {
      createTitle:
        'Создание учебного года',

      editTitle:
        'Редактирование учебного года',

      open:
        'Открыт',

      closed:
        'Закрыт',

      close:
        'Закрыть учебный год',

      reopen:
        'Повторно открыть',

      closeTitle:
        'Закрытие учебного года',

      reopenTitle:
        'Повторное открытие учебного года',

      closeDescription:
        'Закрыть учебный год {year}? После закрытия данные этого года нельзя будет изменять до повторного открытия.',

      reopenDescription:
        'Повторно открыть учебный год {year}? Необходимо указать причину.',

      operationSuccess:
        'Статус учебного года успешно изменён',

      fields: {
        name:
          'Учебный год',

        startYear:
          'Год начала',

        endYear:
          'Год окончания',

        current:
          'Текущий',

        active:
          'Активный',

        status:
          'Статус',

        closingComment:
          'Комментарий к закрытию',

        reopeningReason:
          'Причина повторного открытия',
      },

      validation: {
        startYear:
          'Год начала должен быть от 2000 до 2200',

        endYear:
          'Год окончания должен следовать за годом начала',

        reopenReason:
          'Укажите причину повторного открытия',
      },
    },

    educationLevels: {
      createTitle:
        'Добавление уровня образования',

      editTitle:
        'Редактирование уровня образования',

      codes: {
        bachelor:
          'Бакалавриат',

        master:
          'Магистратура',
      },
    },

    studyForms: {
      createTitle:
        'Добавление формы обучения',

      editTitle:
        'Редактирование формы обучения',

      codes: {
        fullTime:
          'Дневная',

        partTime:
          'Заочная',

        evening:
          'Вечерняя',

        distance:
          'Дистанционная',
      },
    },

    educationDurations: {
      createTitle:
        'Добавление продолжительности обучения',

      editTitle:
        'Редактирование продолжительности обучения',

      fields: {
        level:
          'Уровень образования',

        studyForm:
          'Форма обучения',

        semesters:
          'Количество семестров',

        months:
          'Продолжительность, месяцев',
      },

      validation: {
        semesters:
          'Количество семестров должно быть от 1 до 20',

        months:
          'Продолжительность должна соответствовать количеству семестров: 1 семестр = 6 месяцев',
      },
    },

    semesters: {
      createTitle:
        'Создание семестра',

      editTitle:
        'Редактирование семестра',

      seasons: {
        autumn:
          'Осенний',

        spring:
          'Весенний',
      },

      fields: {
        academicYear:
          'Учебный год',

        season:
          'Семестр',

        startDate:
          'Дата начала',

        endDate:
          'Дата окончания',

        current:
          'Текущий семестр',
      },

      validation: {
        endDate:
          'Дата окончания должна быть позже даты начала',

        autumnYear:
          'Осенний семестр должен начинаться в году начала учебного года',

        springYear:
          'Весенний семестр должен начинаться в году окончания учебного года',
      },
    },
    workloadNorms: {
      generalTitle:
        'Общие нормы учебного года',

      generalDescription:
        'Базовые нормы утверждаются для выбранного учебного года и используются во всех учебных планах и дисциплинах.',

      normsTitle:
        'Коэффициенты неаудиторной учебной работы',

      normsDescription:
        'Коэффициенты используются при автоматическом расчёте нагрузки преподавателей.',

      currentYear:
        'текущий',

      closedYear:
        'Учебный год закрыт. Изменение норм для закрытого учебного года запрещено.',

      empty:
        'Нет видов учебной работы, для которых используются годовые нормы.',

      saveSuccess:
        'Нормы учебной нагрузки успешно сохранены.',

      fields: {
        academicYear:
          'Учебный год',

        hoursPerCredit:
          'Количество часов в 1 кредите',
      },

      columns: {
        enabled:
          'Учитывать',

        workloadType:
          'Вид учебной работы',

        calculationMode:
          'Способ расчёта',

        coefficient:
          'Коэффициент / часы',
      },

      validation: {
        creditPositive:
          'Количество часов в одном кредите должно быть больше нуля.',

        coefficientRequired:
          'Укажите коэффициент для вида работы «{name}».',
      },

      hints: {
        credit:
          'Например: 1 кредит = 30 академических часов.',

        rating:
          'Количество студентов × коэффициент. Например: 0,25 часа на одного студента.',

        courseWorkSupervision:
          'Количество студентов × коэффициент. Обычно около 2 часов на одного студента.',

        courseWorkDefense:
          'Количество студентов × коэффициент. Например: 0,2 часа на одного студента.',

        courseProjectSupervision:
          'Количество студентов × коэффициент. Обычно около 3 часов на одного студента.',

        courseProjectDefense:
          'Количество студентов × коэффициент. Например: 0,3 часа на одного студента.',

        graduationSupervision:
          'Количество студентов × коэффициент руководства выпускной квалификационной работой.',

        masterSupervision:
          'Количество магистрантов × коэффициент руководства магистерской диссертацией.',

        scientificPractice:
          'Количество часов руководства на одну неделю научной практики одной учебной группы.',

        qualificationPractice:
          'Количество часов руководства на одну неделю квалификационной практики одной учебной группы.',

        default:
          'Коэффициент применяется согласно способу расчёта выбранного вида учебной работы.',
      },
    },
  },

  studyPrograms: {
    title:
      'Направления подготовки',

    description:
      'Управление образовательными направлениями, уровнями образования и профилирующими кафедрами.',

    create:
      'Добавить направление',

    createTitle:
      'Создание направления подготовки',

    editTitle:
      'Редактирование направления подготовки',

    detailsTitle:
      'Направление подготовки',

    archive:
      'Архивировать',

    archiveTitle:
      'Архивирование направления',

    archiveConfirm:
      'Архивировать направление «{name}»? Запись можно будет восстановить из архива.',

    archived:
      'Направление подготовки перемещено в архив',

    active:
      'Активно',

    inactive:
      'Неактивно',

    allStatuses:
      'Все статусы',

    allUniversities:
      'Все университеты',

    allEducationLevels:
      'Все уровни образования',

    allDepartments:
      'Все профилирующие кафедры',

    searchPlaceholder:
      'Поиск по коду или названию направления...',

    fields: {
      code:
        'Код направления',

      name:
        'Название',

      nameRu:
        'Название на русском',

      nameUz:
        'Название на узбекском',

      university:
        'Университет',

      educationLevel:
        'Уровень образования',

      profilingFaculty:
        'Профилирующий факультет',

      profilingDepartment:
        'Профилирующая кафедра',

      sortOrder:
        'Порядок сортировки',

      active:
        'Направление активно',

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

    sections: {
      general:
        'Основная информация',

      structure:
        'Академическая структура',

      audit:
        'История изменений',
    },

    validation: {
      universityRequired:
        'Выберите университет',

      educationLevelRequired:
        'Выберите уровень образования',

      codeRequired:
        'Введите код направления',

      nameRuRequired:
        'Введите название на русском языке',

      nameUzRequired:
        'Введите название на узбекском языке',

      departmentRequired:
        'Выберите профилирующую кафедру',

      departmentUniversityMismatch:
        'Профилирующая кафедра должна относиться к выбранному университету',
    },
  },

  studentGroups: {
    title: 'Учебные группы',

    description:
      'Управление учебными группами, направлениями подготовки, формами обучения и контингентом студентов.',

    create:
      'Добавить группу',

    createTitle:
      'Создание учебной группы',

    editTitle:
      'Редактирование учебной группы',

    detailsTitle:
      'Учебная группа',

    archive:
      'Архивировать',

    archiveTitle:
      'Архивирование группы',

    archiveConfirm:
      'Архивировать учебную группу «{code}»? Запись можно будет восстановить из архива.',

    archived:
      'Учебная группа перемещена в архив',

    active:
      'Активна',

    inactive:
      'Неактивна',

    currentYear:
      'Текущий учебный год',

    closedYear:
      'Закрытый учебный год',

    allAdmissionYears:
      'Все годы поступления',

    allFaculties:
      'Все факультеты',

    allPrograms:
      'Все направления',

    allStudyForms:
      'Все формы обучения',

    allStatuses:
      'Все статусы',

    searchPlaceholder:
      'Поиск по коду группы или направлению подготовки...',

    noAvailableStudyForms:
      'Нет доступных форм обучения. Проверьте справочник продолжительности обучения.',

    durationValue:
      '{months} мес. / {semesters} сем.',

    fields: {
      code:
        'Код группы',

      admissionYear:
        'Учебный год поступления',

      graduationYear:
        'Плановый год выпуска',

      faculty:
        'Факультет / отделение',

      studyProgram:
        'Направление подготовки',

      educationLevel:
        'Уровень образования',

      studyForm:
        'Форма обучения',

      profilingFaculty:
        'Профилирующий факультет',

      profilingDepartment:
        'Профилирующая кафедра',

      duration:
        'Нормативная продолжительность',

      studentCount:
        'Количество студентов',

      subgroupCount:
        'Количество подгрупп',

      active:
        'Группа активна',

      status:
        'Статус',

      notes:
        'Примечание',

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
      general:
        'Основные данные',

      education:
        'Параметры обучения',

      programInfo:
        'Параметры выбранного направления',

      profiling:
        'Профилирующее подразделение',

      audit:
        'История изменений',
    },

    validation: {
      codeRequired:
        'Введите код группы',

      admissionYearRequired:
        'Выберите учебный год поступления',

      facultyRequired:
        'Выберите факультет или отделение',

      programRequired:
        'Выберите направление подготовки',

      studyFormRequired:
        'Выберите форму обучения',

      studentCountRange:
        'Количество студентов должно быть от 0 до 1000',

      subgroupCountRange:
        'Количество подгрупп должно быть от 1 до 20',

      universityMismatch:
        'Факультет группы и направление подготовки должны относиться к одному университету',

      durationMissing:
        'Для уровня выбранного направления и формы обучения не задана нормативная продолжительность',

      graduationYear:
        'Учебный год выпуска должен быть позже учебного года поступления',
    },
  },

  curriculumReferences: {
    title:
      'Справочники учебного плана',

    description:
      'Дисциплины и виды учебной работы, используемые при формировании учебных планов и расчёте нагрузки.',

    tabs: {
      disciplines:
        'Дисциплины',

      workloadTypes:
        'Виды учебной работы',
    },

    common: {
      active:
        'Активно',

      inactive:
        'Неактивно',

      status:
        'Статус',

      sortOrder:
        'Порядок',

      archive:
        'Архивировать',
    },

    filters: {
      all:
        'Все',

      allStatuses:
        'Все статусы',

      allDepartments:
        'Все кафедры',

      allCalculationModes:
        'Все способы расчёта',

      classroom:
        'Аудиторная работа',

      teachingLoad:
        'В нагрузке преподавателя',
    },

    disciplines: {
      create:
        'Добавить дисциплину',

      createTitle:
        'Создание дисциплины',

      editTitle:
        'Редактирование дисциплины',

      archiveTitle:
        'Архивирование дисциплины',

      archiveConfirm:
        'Архивировать дисциплину «{name}»?',

      archived:
        'Дисциплина перемещена в архив',

      searchPlaceholder:
        'Поиск по коду или названию дисциплины...',

      fields: {
        code:
          'Код дисциплины',

        name:
          'Название',

        nameRu:
          'Название на русском',

        nameUz:
          'Название на узбекском',

        department: 'Кафедра по умолчанию',
        workloadTypes: 'Вид учебной работы'
      },

      validation: {
        codeRequired:
          'Введите код дисциплины',

        nameRuRequired:
          'Введите название на русском языке',

        nameUzRequired:
          'Введите название на узбекском языке',
      },
    },

    workloadTypes: {
      create: 'Добавить вид работы',
      createTitle: 'Создание вида учебной работы',
      editTitle: 'Редактирование вида учебной работы',
      archiveTitle: 'Архивирование вида работы',
      archiveConfirm: 'Архивировать вид работы «{name}»?',
      archived: 'Вид учебной работы перемещён в архив',
      searchPlaceholder: 'Поиск по коду или названию вида работы...',
      fields: {
        code: 'Вид работы',
        name: 'Название',
        nameRu: 'Название на русском',
        nameUz: 'Название на узбекском',
        calculationMode: 'Способ расчёта',
        reportCategory: 'Категория для отчётов',
        classroom: 'Аудиторная работа',
        teachingLoad: 'Включать в нагрузку преподавателя',
      },

      codes: {
        lecture: 'Лекции',
        practice: 'Практические занятия',
        laboratory: 'Лабораторные занятия',
        seminar: 'Семинарские занятия',
        independentWork: 'Самостоятельная работа',
        courseWork: 'Курсовая работа',
        courseProject: 'Курсовой проект',
        courseWorkProjectDefense: "Защита курсовой работы/проекта",
        scientificPractice: "Научная практика",
        qualificationPractice: "Квалификационная практика",
        masterDissertationSupervision: "Руководство магистерской диссертацией",
        masterDissertationDefense: "Защита магистерской диссертации",
        graduationWorkSupervision: "Руководство выпускной квалификационной работой",
        graduationWorkDefense: "Защита выпускной квалификационной работы",
        courseWorkSupervision: 'Руководство курсовой работой',
        courseWorkDefense: 'Защита курсовой работы',
        courseProjectSupervision: 'Руководство курсовым проектом',
        courseProjectDefense: 'Защита курсового проекта',
        scientificPracticeSupervision: 'Руководство научной практикой',
        qualificationPracticeSupervision: 'Руководство квалификационной практикой',
        rating: 'Рейтинг',
        consultation: 'Консультации',
        exam: 'Экзамен',
        credit: 'Зачёт',
        other: 'Другой вид работы',
      },

      calculationModes: {
        fixed:
          'Фиксированные часы',

        perGroup:
          'На учебную группу',

        perSubgroup:
          'На подгруппу',

        perStudent:
          'На одного студента',
      },

      reportCategories: {
        lecture:
          'Лекции',

        practice:
          'Практические занятия',

        laboratory:
          'Лабораторные занятия',

        courseWorkSupervision:
          'Руководство курсовой работой',

        courseProjectSupervision:
          'Руководство курсовым проектом',

        courseDefense: 'Защита курсовой работы/проекта',
        courseWorkDefense: 'Защита курсовой работы',
        courseProjectDefense: 'Защита курсового проекта',
        scientificPractice: 'Научная практика',

        qualificationPractice:
          'Квалификационная практика',

        masterSupervision:
          'Руководство магистерской диссертацией',
        masterDefense: 'Защита магистерской диссертации',
        graduationSupervision: 'Руководство выпускной квалификационной работой',
        graduationDefense: 'Защита выпускной квалификационной работы',
        rating: 'Рейтинг',
        other: 'Другое',
      },
    },
  },
  curricula: {
    title: 'Учебные планы',
    description: 'Управление версиями учебных планов направлений подготовки и форм обучения.',
    create: 'Добавить учебный план',
    createTitle: 'Создание учебного плана',
    editTitle: 'Редактирование учебного плана',
    detailsTitle: 'Учебный план',
    archive: 'Архивировать',
    archiveTitle: 'Архивирование учебного плана',
    archiveConfirm: 'Архивировать учебный план «{code}»?',
    archived: 'Учебный план перемещён в архив',
    searchPlaceholder: 'Поиск по коду плана или направлению подготовки...',
    currentAcademicYear: 'Текущий учебный год',
    closedAcademicYear: 'Закрытый учебный год',
    noStudyForms: 'Для уровня выбранного направления нет настроенных форм обучения.',
    durationInfo: 'Уровень: {level}. Нормативная продолжительность: {months} мес., {semesters} семестров.',
    openMatrix: 'Состав учебного плана',
    statuses: {
      draft: 'Черновик',
      approved: 'Утверждён',
      archived: 'Устаревшая версия',
    },
    filters: {
      allUniversities: 'Все университеты',
      allPrograms: 'Все направления',
      allStudyForms: 'Все формы обучения',
      allAcademicYears: 'Все учебные годы',
      allStatuses: 'Все статусы',
      allActivity: 'Все по активности',
    },
    sections: {
      general: 'Основные данные',
      approval: 'Утверждение',
      audit: 'История изменений',
    },
    fields: {
      code: 'Код учебного плана',
      version: 'Версия',
      studyProgram: 'Направление подготовки',
      educationLevel: 'Уровень образования',
      studyForm: 'Форма обучения',
      effectiveAcademicYear: 'Учебный год начала действия',
      semestersCount: 'Количество семестров',
      semestersCountShort: 'Сем.',
      disciplinesCount: 'Количество дисциплин',
      disciplinesCountShort: 'Дисциплины',
      status: 'Статус',
      approvedAt: 'Дата утверждения',
      approvalDocument: 'Документ утверждения',
      active: 'Активен',
      notes: 'Примечание',
      createdAt: 'Создано',
      createdBy: 'Создал',
      updatedAt: 'Изменено',
      updatedBy: 'Изменил',
    },
    validation: {
      codeRequired: 'Введите код учебного плана',
      version: 'Номер версии должен быть не меньше 1',
      programRequired: 'Выберите направление подготовки',
      studyFormRequired: 'Выберите форму обучения',
      academicYearRequired: 'Выберите учебный год начала действия',
      approvalDateRequired: 'Для утверждённого учебного плана необходимо указать дату утверждения',
      durationMissing: 'Для выбранного уровня образования и формы обучения не настроена нормативная продолжительность',
    },
  },

  curriculumDisciplines: {
    title:
      'Состав учебного плана',

    description:
      'Матрица дисциплин учебного плана по семестрам.',

    create:
      'Добавить дисциплину',

    createTitle:
      'Добавление дисциплины в учебный план',

    editTitle:
      'Редактирование дисциплины учебного плана',

    archive:
      'Архивировать',

    archiveTitle:
      'Архивирование дисциплины',

    archiveConfirm:
      'Архивировать дисциплину «{discipline}» из {semester} семестра?',

    archived:
      'Дисциплина учебного плана перемещена в архив',

    active:
      'Активна',

    inactive:
      'Неактивна',

    backToCurricula:
      'К учебным планам',

    invalidCurriculum:
      'Некорректный идентификатор учебного плана.',

    searchPlaceholder:
      'Поиск по коду, названию дисциплины или кафедре...',

    semesterOption:
      '{semester} семестр — {season}',

    semesterNumber: '{semester} сем.',
    contactHoursHint: 'Расчётный объём без самостоятельной работы: {hours} ч. Плановые контактные часы будут сформированы из видов нагрузки.',
    departmentFromDiscipline:
      'Обеспечивающая кафедра определяется дисциплиной: {department}',

    auditoriumTotal:
      'Итого аудиторных часов',

    totalAcademic:
      'Всего часов',

    grandTotal:
      'Итого по выбранным семестрам',

    curriculumRuleApplied:
      'Используется единая норма учебного плана',

    curriculumRuleMissing:
      'Сначала задайте единую норму учебного плана',

    weeklyNorm: 'Норма часов × учебные недели × группы',
    creditNormMissing: 'Для учебного года не задано количество часов в одном кредите. Перейдите в «Академические справочники → Нормы учебной нагрузки».',
    semestersCount: '{count} сем.',

    units: {
      hoursPerWeek: 'ч./нед.',
    },

    seasons: {
      autumn:
        'Осенний',

      spring:
        'Весенний',
    },

    componentTypes: {
      required:
        'Обязательная',

      elective:
        'По выбору',

      optional:
        'Факультатив',
    },

    controlForms: {
      none:
        'Без итогового контроля',

      exam:
        'Экзамен',

      credit:
        'Зачёт',

      gradedCredit:
        'Дифференцированный зачёт',

      courseWork:
        'Курсовая работа',

      courseProject:
        'Курсовой проект',
    },

    sections: {
      main: 'Основные данные',
      discipline: 'Дисциплина и семестр',
      hours: 'Кредиты и академический объём',
    },

    summary: {
      plan:
        'Учебный план',

      version:
        'Версия',

      semesters:
        'Семестров',

      disciplines:
        'Записей',
    },

    filters: {
      allSemesters:
        'Все семестры',

      allComponentTypes:
        'Все компоненты',

      allControlForms:
        'Все формы контроля',

      allStatuses:
        'Все статусы',
    },

    fields: {
      discipline:
        'Дисциплина',

      semester:
        'Семестр',

      department:
        'Обеспечивающая кафедра',

      componentType:
        'Компонент',

      controlForm:
        'Форма контроля',

      credits:
        'Кредиты',

      totalHours:
        'Общий академический объём',

      totalHoursShort:
        'Всего ч.',

      independentHours:
        'Самостоятельная работа',

      independentHoursShort:
        'Самост. ч.',

      plannedContactHours:
        'Плановые контактные часы',

      plannedContactHoursShort:
        'Контакт ч.',

      weeks:
        'Учебных недель',

      active:
        'Запись активна',

      status: 'Статус',
      notes: 'Примечание',
      semesters: 'Семестры',
    },

    validation: {
      disciplineRequired:
        'Выберите дисциплину',

      semesterRequired:
        'Выберите семестр',

      semesterRange:
        'Номер семестра превышает нормативную продолжительность учебного плана',

      departmentRequired:
        'Выберите обеспечивающую кафедру',

      nonNegative:
        'Значение не может быть отрицательным',

      independentExceedsTotal: 'Самостоятельные часы не могут превышать общий академический объём',
      weeks: 'Количество учебных недель должно быть не меньше 1',
      semestersRequired: 'Выберите хотя бы один семестр.',
      disciplineDepartmentRequired: 'Для выбранной дисциплины не задана кафедра.',
    },
    workloads: 'Виды нагрузки',
  },

  curriculumWorkloads: {
    title:
      'Виды нагрузки',

    create:
      'Добавить вид нагрузки',

    createTitle:
      'Добавление вида нагрузки',

    editTitle:
      'Редактирование вида нагрузки',

    archive:
      'Архивировать',

    disciplineInfo:
      '{semester} семестр · {department}',

    empty:
      'Для дисциплины виды нагрузки ещё не заданы.',

    loadError:
      'Не удалось загрузить виды нагрузки.',

    active:
      'Активна',

    inactive:
      'Неактивна',

    total:
      'Всего базовых часов:',

    archiveTitle:
      'Архивирование вида нагрузки',

    archiveConfirm:
      'Архивировать вид нагрузки «{workload}»?',

    archived:
      'Вид нагрузки архивирован.',

    fields: {
      workloadType:
        'Вид учебной работы',

      calculationMode:
        'Способ расчёта',

      baseHours:
        'Базовые часы',

      studentsPerUnit:
        'Студентов на расчётную единицу',

      studentsPerUnitShort:
        'Студентов',

      notes:
        'Примечание',
    },

    calculationModes: {
      fixed:
        'Фиксированные часы',

      perGroup:
        'На учебную группу',

      perSubgroup:
        'На подгруппу',

      perStudent:
        'На одного студента',
    },

    validation: {
      workloadTypeRequired: 'Выберите вид учебной работы.',
      baseHoursNonNegative: 'Количество часов не может быть отрицательным.',
      studentsPerUnitRequired: 'Укажите количество студентов на расчётную единицу.',
    },
    activeField: 'Вид нагрузки активен',
  },

  teachingSetup: {
    title:
      'Подготовка учебных групп',

    description:
      'Назначение учебных планов группам и ведение состояния групп по учебным семестрам.',

    currentYear:
      'Текущий учебный год',

    closedYear:
      'Закрытый учебный год',

    tabs: {
      groupCurricula:
        'Учебные планы групп',

      groupSemesters:
        'Семестры групп',
    },

    seasons: {
      autumn:
        'Осенний',

      spring:
        'Весенний',
    },

    common: {
      active:
        'Активно',

      inactive:
        'Неактивно',

      status:
        'Статус',

      notes:
        'Примечание',
    },

    filters: {
      all:
        'Все',

      allYears:
        'Все учебные годы',

      allStatuses:
        'Все статусы',

      primary:
        'Основной план',
    },

    groupCurricula: {
      create:
        'Назначить учебный план',

      createTitle:
        'Назначение учебного плана группе',

      editTitle:
        'Редактирование назначения учебного плана',

      searchPlaceholder:
        'Поиск по группе, учебному плану или направлению...',

      archiveTitle:
        'Архивирование назначения',

      archiveConfirm:
        'Архивировать назначение плана «{curriculum}» группе «{group}»?',

      archived:
        'Назначение учебного плана перемещено в архив',

      fields: {
        group:
          'Учебная группа',

        curriculum:
          'Учебный план',

        studyProgram:
          'Направление подготовки',

        studyForm:
          'Форма обучения',

        startYear:
          'Начало применения',

        endYear:
          'Окончание применения',

        primary:
          'Основной учебный план',
      },

      validation: {
        groupRequired: 'Выберите учебную группу',
        curriculumRequired: 'Выберите учебный план',
        startYearRequired: 'Выберите учебный год начала применения',
        endYear: 'Учебный год окончания не может быть раньше года начала',
      },
    },

    groupSemesters: {
      create:
        'Добавить семестр группы',

      createTitle:
        'Создание семестра учебной группы',

      editTitle:
        'Редактирование семестра учебной группы',

      searchPlaceholder:
        'Поиск по группе или коду учебного плана...',

      semesterOption:
        '{semester} семестр — {season}',

      archiveTitle:
        'Архивирование семестра группы',

      archiveConfirm:
        'Архивировать {semester} семестр группы «{group}»?',

      archived:
        'Семестр учебной группы перемещён в архив',

      statuses: {
        planned:
          'Запланирован',

        active:
          'Обучение идёт',

        completed:
          'Завершён',

        cancelled:
          'Отменён',
      },

      fields: {
        assignment:
          'Учебный план группы',

        group:
          'Группа',

        curriculum:
          'Учебный план',

        academicYear:
          'Учебный год',

        semesterNumber:
          'Номер семестра',

        academicSemester:
          'Календарный семестр',

        weeksCount: 'Учебные недели',

        studentsCount:
          'Количество студентов',

        studentsCountShort:
          'Студенты',

        subgroupCount:
          'Количество подгрупп',

        subgroupCountShort:
          'Подгруппы',

        status:
          'Статус',
      },

      validation: {
        assignmentRequired:
          'Выберите назначение учебного плана',

        yearRequired:
          'Выберите учебный год',

        semesterNumberRequired:
          'Выберите номер семестра',

        academicSemesterRequired:
          'Выберите календарный академический семестр',

        students:
          'Количество студентов должно быть от 0 до 1000',

        subgroups:
          'Количество подгрупп должно быть от 1 до 100',
      },
    },
  },

  workload: {
  tabs: {
    planned: 'Плановая нагрузка',
    distribution: 'Распределение нагрузки',
  },
},

  teachingWorkload: {
    title:
      'Учебные потоки и нагрузка',

    description:
      'Формирование учебных потоков, объединение групп и расчёт плановой учебной нагрузки.',

    calculate:
      'Рассчитать нагрузку',

    calculateAll:
      'Рассчитать все',

    calculateError:
      'Не удалось рассчитать плановую нагрузку.',

    calculateAllSuccess:
      'Успешно рассчитано потоков: {count}.',

    calculatePartialTitle:
      'Расчёт завершён с ошибками',

    calculatePartial:
      'Рассчитано: {calculated}. Ошибок: {errors}.',

    tabs: {
      streams: 'Учебные потоки',
    },

    common: {
      active:
        'Активен',

      inactive:
        'Неактивен',

      archive:
        'Архивировать',

      notes:
        'Примечание',
    },

    calculationModes: {
      fixed:
        'Фиксированные часы',

      perGroup:
        'На группу',

      perSubgroup:
        'На подгруппу',

      perStudent:
        'На студента',
    },

    filters: {
      allYears:
        'Все учебные годы',

      allSemesters:
        'Все семестры',

      allStatuses:
        'Все статусы',

      allActivity:
        'Все по активности',

      allDistribution:
        'Любое распределение',

      fullyDistributed:
        'Полностью распределена',

      notFullyDistributed:
        'Есть остаток',
    },

    streams: {
      create:
        'Добавить поток',

      createTitle:
        'Создание учебного потока',

      editTitle:
        'Редактирование учебного потока',

      searchPlaceholder:
        'Поиск по коду, названию, дисциплине или кафедре...',

      disciplineDescription:
        '{semester} семестр · {department}',

      archiveTitle:
        'Архивирование учебного потока',

      archiveConfirm:
        'Архивировать учебный поток «{code}»?',

      archived:
        'Учебный поток перемещён в архив.',

      statuses: {
        draft:
          'Черновик',

        calculated:
          'Нагрузка рассчитана',

        approved:
          'Утверждён',

        cancelled:
          'Отменён',
      },

      fields: {
        academicYear:
          'Учебный год',

        academicSemester:
          'Академический семестр',

        discipline:
          'Дисциплина учебного плана',

        workloadType:
          'Вид нагрузки',

        department:
          'Обеспечивающая кафедра',

        code:
          'Код потока',

        name:
          'Название потока',

        groups:
          'Группы',

        students:
          'Студенты',

        subgroups:
          'Подгруппы',

        status: 'Статус',
        curriculum: 'Учебный план',

        studyProgram:
          'Направление подготовки',

        semesterNumber:
          'Семестр по учебному плану',

        positions:
          'Позиций',
        totalHours: 'Часов',
      },

      validation: {
        yearRequired:
          'Выберите учебный год.',

        semesterRequired:
          'Выберите академический семестр.',

        disciplineRequired:
          'Выберите дисциплину учебного плана.',

        workloadRequired:
          'Выберите вид нагрузки.',

        departmentRequired:
          'Не определена обеспечивающая кафедра.',

        codeRequired:
          'Введите код учебного потока.',

        nameRequired: 'Введите название учебного потока.',
        curriculumRequired: 'Выберите учебный план.',
        semesterNumberRequired: 'Выберите номер семестра учебного плана.',
      },
    },

    seasons: {
      autumn: 'Осенний',
      spring: 'Весенний',
    },

    streamGroups: {
      title:
        'Группы учебного потока',

      selectGroup:
        'Выберите учебную группу',

      add:
        'Добавить',

      added:
        'Учебная группа добавлена в поток.',

      archive:
        'Исключить из потока',

      archiveTitle:
        'Исключение группы',

      archiveConfirm:
        'Исключить группу «{group}» из учебного потока?',

      archived:
        'Учебная группа исключена из потока.',

      empty:
        'В учебном потоке пока нет групп.',

      groups:
        'Групп',

      students:
        'Студентов',

      subgroups:
        'Подгрупп',

      groupDescription:
        'Студентов: {students} · подгрупп: {subgroups}',
    },

    planned: {
      searchPlaceholder: 'Поиск по потоку, дисциплине или кафедре...',
      description: 'Плановая учебная нагрузка по семестрам, потокам и учебным группам.',
      empty: 'Плановая нагрузка отсутствует.',

      scope: {
        stream: 'Поток',
        group: 'Учебная группа',
      },

      statuses: {
        calculated: 'Рассчитана',
        approved: 'Утверждена',
        partially_distributed: 'Частично распределена',
        distributed: 'Полностью распределена',
        cancelled: 'Отменена',
      },

      fields: {
        stream: 'Поток',
        discipline: 'Дисциплина',
        workloadType: 'Вид нагрузки',
        baseHours: 'Базовые часы',
        quantity: 'Количество',
        totalHours: 'Всего часов',
        remainingHours: 'Остаток',
        distribution: 'Распределение',
        distributedHours: 'Распределено',
        status: 'Статус',
      },

      summary: {
        totalHours: 'Общий объём плановой нагрузки',
        records: 'Позиций нагрузки',
        yearTotal: 'Всего за учебный год',
      },
    },
  },

  workloadDistribution: {
    create: 'Распределить нагрузку',
    title: 'Распределение учебной нагрузки',
    description: 'Распределение рассчитанных часов дисциплин между преподавателями кафедр.',
    createTitle: 'Распределение нагрузки преподавателю',
    editTitle: 'Редактирование распределения',
    searchPlaceholder: 'Поиск по преподавателю, дисциплине или потоку...',
    approve: 'Утвердить',
    cancel: 'Отменить',
    cancelTitle: 'Отмена распределения',
    returnToDraft: 'Вернуть в черновик',
    returnTitle: 'Возврат распределения в черновик',
    archive: 'Архивировать',
    archiveTitle: 'Архивирование распределения',
    archiveConfirm: 'Архивировать распределение нагрузки преподавателя «{teacher}»?',
    archived: 'Распределение перемещено в архив.',
    remainingHint: 'Доступный остаток позиции: {remaining} ч. Общий объём: {total} ч.',
    teacherNormHint: 'Рекомендуемая годовая нагрузка преподавателя: {recommended} ч. Уже распределено: {distributed} ч. Остаток нормы: {remaining} ч.',

    scope: {
      stream: 'Поток',
      group: 'Группа',
    },

    seasons: {
      autumn: 'Осенний',
      spring: 'Весенний',
    },

    shortSemester: 'сем.',
    shortHours: 'ч.',

    statuses: {
      draft: 'Черновик',
      approved: 'Утверждено',
      cancelled: 'Отменено',
    },

    filters: {
      allYears: 'Все учебные годы',
      allDepartments: 'Все кафедры',
      allStatuses: 'Все статусы',
      allSemesters: 'Все семестры',
    },

    fields: {
      plannedWorkload: 'Позиция плановой нагрузки',
      curriculum: 'Учебный план',
      discipline: 'Дисциплина',
      workloadType: 'Вид нагрузки',
      department: 'Кафедра',
      teacher: 'Преподаватель',
      allocatedHours: 'Распределяемые часы',
      semester: 'Семестр',
      scope: 'Поток / группа',
      status: 'Статус',
      notes: 'Примечание',
      reason: 'Причина',
    },

    validation: {
      workloadRequired: 'Выберите позицию плановой нагрузки.',
      teacherRequired: 'Выберите преподавателя.',
      hoursPositive: 'Количество часов должно быть больше нуля.',
      hoursExceeded: 'Количество часов превышает доступный остаток {hours} ч.',
      reasonRequired: 'Укажите причину.',
    },

    planned: {
      title: 'Плановая нагрузка для распределения',
      description: 'Позиции, по которым ещё имеются нераспределённые часы.',
      assign: 'Назначить',
      empty: 'Вся доступная плановая нагрузка распределена.',
      total: 'План, ч.',
      distribution: 'Распределено',
      remaining: 'Остаток, ч.',
      positionsCount: '{count} позиций',
    },

    distributions: {
      title: 'Распределения преподавателям',
      description: 'Созданные распределения учебной нагрузки по преподавателям.',
    },

    teacherLoad: {
      title: 'Контроль нагрузки преподавателей',
      teacher: 'Преподаватель',
      norm: 'Годовая норма',
      approved: 'Утверждено',
      draft: 'Черновик',
      distributed: 'Распределено',
      assigningNow: 'Назначается сейчас',
      afterAssignment: 'После назначения',
      remaining: 'Остаток',
      percent: 'Выполнение',
      empty: 'Нет данных о нагрузке преподавателей.',

      status: {
        title: 'Статус',
        UNDERLOAD: 'Недогруз',
        FULL: 'Норма',
        OVERLOAD: 'Перегруз',
      },
    },

    bulk: {
      selected: 'Выбрано: {count}',
      approve: 'Утвердить ({count})',
      cancel: 'Отменить ({count})',
      restore: 'Восстановить ({count})',
      returnToDraft: 'В черновик ({count})',
      clearSelection: 'Снять выбор',
      cancelTitle: 'Массовая отмена распределений',
      restoreTitle: 'Массовое восстановление распределений',
      returnTitle: 'Массовый возврат в черновик',
      successResult: 'Успешно обработано распределений: {count}.',
      partialTitle: 'Операция выполнена частично',
      partialResult: 'Успешно: {success}. Ошибок: {errors}. Недоступно: {unavailable}.',
    },

    bulkAssign: {
      title: 'Массовое назначение нагрузки',
      selected: 'Выбрано позиций: {count}',
      totalHours: 'Общий остаток: {hours} ч.',
      positions: 'Позиций',
      hours: 'Назначается часов',
      academicYear: 'Учебный год',
      assigningNow: 'Назначается сейчас',
      assign: 'Назначить выбранное',
      submit: 'Назначить ({count})',
      incompatibleTitle: 'Несовместимые позиции',
      incompatible: 'Для массового назначения выберите позиции одного учебного года и одной обеспечивающей кафедры.',
      success: 'Создано распределений: {count}. Назначено часов: {hours}.',
      partialResult: 'Создано: {created}. Ошибок: {errors}. Недоступно: {unavailable}.',
    },
  },

};

export default ru
