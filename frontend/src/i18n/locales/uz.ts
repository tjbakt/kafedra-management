const uz = {
  app: {
    name: 'Kafedra Management',
    title: 'O‘quv jarayonini boshqarish',
    subtitle: 'Kafedra axborot tizimi',
    version: 'Versiya {version}',
    frontendLayout: 'Frontend layout',
    allRightsReserved: 'Barcha huquqlar himoyalangan.',
    systemWorking: 'Tizim ishlamoqda',
  },

  common: {
    create: 'Yaratish',
    add: 'Qo‘shish',
    edit: 'Tahrirlash',
    delete: 'O‘chirish',
    save: 'Saqlash',
    cancel: 'Bekor qilish',
    close: 'Yopish',
    confirm: 'Tasdiqlash',
    back: 'Orqaga',
    next: 'Keyingi',
    search: 'Qidirish',
    filter: 'Filtr',
    reset: 'Tiklash',
    clear: 'Tozalash',
    refresh: 'Yangilash',
    export: 'Eksport',
    import: 'Import',
    print: 'Chop etish',
    download: 'Yuklab olish',
    upload: 'Yuklash',
    view: 'Ko‘rish',
    actions: 'Amallar',
    yes: 'Ha',
    no: 'Yo‘q',
    loading: 'Yuklanmoqda...',
    saving: 'Saqlanmoqda...',
    noData: 'Ma’lumotlar mavjud emas',
    required: 'Majburiy maydon',
    success: 'Muvaffaqiyatli',
    information: 'Ma’lumot',
    warning: 'Ogohlantirish',
    error: 'Xato',
    important: 'Muhim',
    status: 'Holat',
    language: 'Til',
    lightTheme: 'Yorug‘ mavzu',
    darkTheme: 'Qorong‘i mavzu',
    openMenu: 'Menyuni ochish yoki yig‘ish',
    openNotifications: 'Bildirishnomalarni ochish',
  },

  languages: {
    ru: 'Русский',
    uz: 'O‘zbekcha',
    select: 'Tilni tanlang',
    changed: 'Interfeys tili o‘zgartirildi',
    saved: 'Asosiy interfeys tili saqlandi',
    saveError: 'Tanlangan tilni saqlab bo‘lmadi',
  },

  navigation: {
    dashboard: 'Bosh sahifa',
    organizationalStructure: 'Tashkiliy tuzilma',
    departments: 'Kafedralar',
    teachers: 'O‘qituvchilar',
    studentGroups: 'Talabalar guruhlari',
    educationalProcess: 'O‘quv jarayoni',
    disciplines: 'Fanlar',
    curricula: 'O‘quv rejalari',
    workload: 'O‘quv yuklamasi',
    schedules: 'Dars jadvali',
    analytics: 'Tahlil',
    reports: 'Hisobotlar',
    system: 'Tizim',
    settings: 'Sozlamalar',
    staffEmployments: 'Mehnat tayinlovlari',
    staffAcademicYears: 'Yillar bo‘yicha kadrlar',
    workloadNorms: 'Yuklama me’yorlari',
    academicSettings: 'Akademik ma’lumotnomalar',
    studyPrograms: 'Ta’lim yo‘nalishlari',
  },

  profile: {
    profile: 'Profil',
    settings: 'Sozlamalar',
    logout: 'Chiqish',
    administrator: 'Administrator',
    systemAdministrator: 'Tizim administratori',
  },

  notifications: {
    title: 'Bildirishnomalar',
    unread:
      'O‘qilmagan bildirishnoma yo‘q | {count} ta o‘qilmagan bildirishnoma',
    markAllAsRead: 'Barchasini o‘qilgan deb belgilash',
    empty: 'Bildirishnomalar mavjud emas',
    clear: 'Tozalash',
    systemReady: 'Tizim tayyor',
    frontendConnected: 'Frontend karkasi muvaffaqiyatli ulandi.',
    workloadTitle: 'O‘quv yuklamasi',
    workloadCheck: 'Soatlar taqsimotini tekshirish kerak.',
    directoryUpdated: 'Ma’lumotnoma yangilandi',
    departmentsUpdated: 'Kafedralar ma’lumotlari yangilandi.',
    justNow: 'Hozirgina',
    minutesAgo: '{count} daqiqa oldin',
    hourAgo: '1 soat oldin',
  },

  dashboard: {
    title: 'Boshqaruv paneli',
    description:
      'O‘quv jarayoni va yuklama taqsimoti holati haqida umumiy ma’lumot.',

    teachers: 'O‘qituvchilar',
    disciplines: 'Fanlar',
    groups: 'O‘quv guruhlari',
    totalWorkload: 'Umumiy yuklama',
    hours: 'soat',

    teachersChange: 'Oy davomida +3',
    activePlans: '12 ta faol reja',
    studentsCount: '824 talaba',
    currentYear: 'Joriy o‘quv yili uchun',

    workloadDistribution: 'O‘quv yuklamasini taqsimlash',
    workloadDistributionDescription:
      'Joriy o‘quv yili yuklamasini tayyorlash holati',
    openModule: 'Modulni ochish',

    distributed: 'Taqsimlangan',
    checked: 'Tekshirilgan',
    approved: 'Tasdiqlangan',
    inProgress: 'Bajarilmoqda',
    requiresCheck: 'Tekshirish kerak',
    processing: 'Jarayonda',

    quickActions: 'Tezkor amallar',
    quickActionsDescription: 'Eng ko‘p foydalaniladigan bo‘limlar',
    manageEmployees: 'Xodimlarni boshqarish',
    viewAndEdit: 'Ko‘rish va tahrirlash',
    distributeHours: 'Soatlarni taqsimlash',
    pdfAndExcel: 'PDF va Excel',

    showToast: 'Toast ko‘rsatish',
    checkDialog: 'Dialogni tekshirish',
    interfaceWorks: 'Interfeys ishlamoqda',
    toastConnected: 'Global Toast tizimi muvaffaqiyatli ulandi.',
    confirmDemoAction: 'Namoyish amalini bajarishni tasdiqlaysizmi?',
    actionConfirmed: 'Amal tasdiqlandi',
  },

  auth: {
    loginTitle: 'Tizimga kirish',
    loginDescription:
      'Hisob ma’lumotlaringizni kiriting.',
    username: 'Foydalanuvchi nomi',
    usernamePlaceholder:
      'Foydalanuvchi nomini kiriting',
    password: 'Parol',
    passwordPlaceholder: 'Parolni kiriting',
    rememberMe: 'Meni eslab qolish',
    forgotPassword: 'Parolni unutdingizmi?',
    login: 'Kirish',
    loggingIn: 'Kirilmoqda...',
    loginSuccess: 'Kirish bajarildi',
    welcome: 'Xush kelibsiz, {name}!',
    loginFailed: 'Tizimga kirib bo‘lmadi',
    invalidCredentials:
      'Foydalanuvchi nomi yoki parol noto‘g‘ri.',
    sessionExpired: 'Sessiya yakunlandi',
    sessionExpiredDescription:
      'Tizimga qayta kiring.',
    logoutSuccess: 'Chiqish bajarildi',
    logoutSuccessDescription:
      'Siz tizimdan muvaffaqiyatli chiqdingiz.',
    usernameRequired:
      'Foydalanuvchi nomini kiriting',
    passwordRequired: 'Parolni kiriting',
    passwordMinLength:
      'Parol kamida 4 ta belgidan iborat bo‘lishi kerak',
    passwordRecovery: 'Parolni tiklash',
    passwordRecoveryLater:
      'Funksiya keyinroq ulanadi.',
    changePassword: 'Parolni o‘zgartirish',
    passwordChangeRequired:
      'Vaqtinchalik parolni o‘zgartirish kerak.',
    currentPassword: 'Joriy parol',
    newPassword: 'Yangi parol',
    confirmPassword: 'Parolni tasdiqlash',
  },

  modules: {
    prepared: 'Modul tayyorlandi',
    preparedDescription:
      'Marshrut, layout va asosiy komponentlar ulandi. CRUD interfeysi tegishli bosqichda amalga oshiriladi.',
    demoMode: 'Namoyish rejimi',
    createLater:
      'Yaratish formasi CRUD bosqichida qo‘shiladi.',
    returnHome: 'Bosh sahifaga qaytish',

    departmentsDescription:
      'Kafedralar va tashkiliy tuzilmani boshqarish.',
    teachersDescription:
      'O‘qituvchilar, stavkalar, ilmiy darajalar va unvonlar ma’lumotnomasi.',
    studentsDescription:
      'Akademik guruhlar va talabalar kontingentini boshqarish.',
    disciplinesDescription: 'O‘quv fanlari ma’lumotnomasi.',
    curriculaDescription:
      'Ta’lim dasturlari o‘quv rejalarini shakllantirish va yuritish.',
    workloadDescription:
      'O‘quv yuklamasini hisoblash va o‘qituvchilar o‘rtasida taqsimlash.',
    schedulesDescription:
      'Dars jadvalini rejalashtirish va ko‘rish.',
    reportsDescription:
      'Tahliliy hisobotlar, PDF va Excel hujjatlarini shakllantirish.',
    settingsDescription:
      'Foydalanuvchilar, rollar, huquqlar va tizim parametrlarini boshqarish.',
  },

  errors: {
    notFoundTitle: 'Sahifa topilmadi',
    notFoundDescription:
      'So‘ralgan sahifa mavjud emas, ko‘chirilgan yoki o‘chirilgan.',
    unexpected: 'Kutilmagan xatolik yuz berdi',
    serverUnavailable: 'Serverga ulanib bo‘lmadi',
    timeout: 'Server javobini kutish vaqti tugadi',
    forbiddenTitle: 'Kirish taqiqlangan',

    forbiddenDescription:
      'Sizning hisobingiz ushbu bo‘limni ko‘rish uchun yetarli huquqlarga ega emas.',
  },

  confirm: {
    deleteHeader: 'O‘chirishni tasdiqlash',
    deleteMessage:
      'Tanlangan yozuvni o‘chirishni xohlaysizmi? Bu amalni bekor qilib bo‘lmaydi.',
    deleteAccept: 'O‘chirish',
    actionHeader: 'Amalni tasdiqlash',
  },

  emptyState: {
    title: 'Ma’lumotlar mavjud emas',
    description: 'Ko‘rsatish uchun ma’lumotlar mavjud emas.',
  },

  access: {
    debugTitle:
      'Kirish huquqlari',

    debugDescription:
      'Joriy foydalanuvchining guruhlari va ruxsatlari haqidagi diagnostika ma’lumotlari.',

    userInformation:
      'Foydalanuvchi',

    groups:
      'Guruhlar',

    permissions:
      'Ruxsatlar',

    noGroups:
      'Guruhlar mavjud emas',

    noGroupsDescription:
      'Foydalanuvchi hech qanday guruhga kiritilmagan.',

    noPermissions:
      'Ruxsatlar mavjud emas',

    noPermissionsDescription:
      'Foydalanuvchi uchun alohida ruxsatlar qaytarilmadi.',
  },

  crud: {
    emptyTitle:
      'Yozuvlar topilmadi',

    emptyDescription:
      'Berilgan shartlar bo‘yicha yozuvlar mavjud emas.',

    paginationReport:
      '{first}–{last} / {totalRecords} ta ko‘rsatildi',

    validationFailed:
      'Kiritilgan ma’lumotlarni tekshiring',

    createTitle:
      'Yozuv yaratish',

    editTitle:
      'Yozuvni tahrirlash',

    viewTitle:
      'Yozuvni ko‘rish',

    deleteTitle:
      'Yozuvni o‘chirish',

    created:
      'Yozuv muvaffaqiyatli yaratildi',

    updated:
      'Yozuv muvaffaqiyatli yangilandi',

    deleted:
      'Yozuv muvaffaqiyatli o‘chirildi',

    loadError:
      'Ma’lumotlarni yuklab bo‘lmadi',

    saveError:
      'Ma’lumotlarni saqlab bo‘lmadi',

    deleteError:
      'Yozuvni o‘chirib bo‘lmadi',

    filters:
      'Filtrlar',

    clearFilters:
      'Filtrlarni tozalash',

    rowsPerPage:
      'Sahifadagi yozuvlar',

    infrastructureTitle:
      'CRUD infratuzilmasi',
  },

  departments: {
    title:
      'Kafedralar',

    description:
      'Kafedralar, ularning fakultetlarga tegishliligi, aloqa ma’lumotlari va holatini boshqarish.',

    create:
      'Kafedra yaratish',

    createTitle:
      'Kafedra yaratish',

    editTitle:
      'Kafedrani tahrirlash',

    detailsTitle:
      'Kafedra haqida ma’lumot',

    archive:
      'Arxivlash',

    archiveTitle:
      'Kafedrani arxivlash',

    archiveConfirm:
      '«{name}» kafedrasini arxivlaysizmi? Yozuvni keyinchalik arxivdan tiklash mumkin.',

    archived:
      'Kafedra arxivga ko‘chirildi',

    active:
      'Faol',

    inactive:
      'Faol emas',

    allStatuses:
      'Barcha holatlar',

    allUniversities:
      'Barcha universitetlar',

    allFaculties:
      'Barcha fakultetlar',

    searchPlaceholder:
      'Kod yoki nom bo‘yicha qidirish...',

    fields: {
      code:
        'Kod',

      name:
        'Nomi',

      nameRu:
        'Rus tilidagi nomi',

      nameUz:
        'O‘zbek tilidagi nomi',

      shortNameRu:
        'Rus tilidagi qisqa nomi',

      shortNameUz:
        'O‘zbek tilidagi qisqa nomi',

      university:
        'Universitet',

      faculty:
        'Fakultet',

      head:
        'Kafedra mudiri',

      phone:
        'Telefon',

      email:
        'Elektron pochta',

      room:
        'Auditoriya / xona',

      sortOrder:
        'Saralash tartibi',

      active:
        'Faol kafedra',

      status:
        'Holat',

      createdAt:
        'Yaratilgan',

      createdBy:
        'Yaratgan',

      updatedAt:
        'O‘zgartirilgan',

      updatedBy:
        'O‘zgartirgan',
    },

    placeholders: {
      faculty:
        'Fakultetni tanlang',
    },

    sections: {
      general:
        'Asosiy ma’lumot',

      contacts:
        'Aloqa ma’lumotlari',

      audit:
        'O‘zgarishlar tarixi',
    },

    validation: {
      facultyRequired:
        'Fakultetni tanlang',

      codeRequired:
        'Kafedra kodini kiriting',

      nameRuRequired:
        'Rus tilidagi nomni kiriting',

      nameUzRequired:
        'O‘zbek tilidagi nomni kiriting',

      invalidEmail:
        'To‘g‘ri elektron pochta manzilini kiriting',
    },
  },

  staff: {
    title:
      'O‘qituvchilar va xodimlar',

    description:
      'Universitet o‘qituvchilari va xodimlarining kadrlar kartochkalari.',

    create:
      'Xodim qo‘shish',

    createTitle:
      'Xodim kartochkasini yaratish',

    editTitle:
      'Xodim kartochkasini tahrirlash',

    detailsTitle:
      'Xodim kartochkasi',

    archive:
      'Arxivlash',

    archiveTitle:
      'Xodimni arxivlash',

    archiveConfirm:
      '«{name}» kartochkasini arxivlaysizmi? Yozuvni keyinchalik tiklash mumkin.',

    archived:
      'Xodim kartochkasi arxivga ko‘chirildi',

    working:
      'Ishlamoqda',

    notWorking:
      'Ishlamaydi',

    allStatuses:
      'Barcha holatlar',

    allDegrees:
      'Barcha ilmiy darajalar',

    allTitles:
      'Barcha ilmiy unvonlar',

    searchPlaceholder:
      'F.I.Sh., tabel raqami, telefon yoki email bo‘yicha qidirish...',

    genderMale:
      'Erkak',

    genderFemale:
      'Ayol',

    genderNotSpecified:
      'Ko‘rsatilmagan',

    primaryEmployment:
      'Asosiy',

    rateShort:
      'stavka',

    noEmployments:
      'Mehnat tayinlovlari hali mavjud emas.',

    fields: {
      personnelNumber:
        'Tabel raqami',

      fullName:
        'F.I.Sh.',

      lastName:
        'Familiya',

      firstName:
        'Ism',

      middleName:
        'Otasining ismi',

      gender:
        'Jinsi',

      birthDate:
        'Tug‘ilgan sana',

      phone:
        'Telefon',

      email:
        'Elektron pochta',

      academicDegree:
        'Ilmiy daraja',

      academicTitle:
        'Ilmiy unvon',

      degreeDate:
        'Ilmiy daraja berilgan sana',

      titleDate:
        'Ilmiy unvon berilgan sana',

      active:
        'Xodim ishlamoqda',

      status:
        'Holat',

      notes:
        'Izoh',

      username:
        'Tizim foydalanuvchisi',

      createdAt:
        'Yaratilgan',

      createdBy:
        'Yaratgan',

      updatedAt:
        'O‘zgartirilgan',

      updatedBy:
        'O‘zgartirgan',
    },

    sections: {
      personal:
        'Shaxsiy ma’lumotlar',

      contacts:
        'Aloqa ma’lumotlari',

      academic:
        'Ilmiy daraja va unvon',

      additional:
        'Qo‘shimcha ma’lumot',

      employments:
        'Mehnat tayinlovlari',

      audit:
        'O‘zgarishlar tarixi',
    },

    validation: {
      personnelNumberRequired:
        'Tabel raqamini kiriting',

      lastNameRequired:
        'Familiyani kiriting',

      firstNameRequired:
        'Ismni kiriting',

      invalidEmail:
        'To‘g‘ri elektron pochta manzilini kiriting',

      degreeDateWithoutDegree:
        'Ilmiy darajasiz uning berilgan sanasini ko‘rsatib bo‘lmaydi',

      titleDateWithoutTitle:
        'Ilmiy unvonsiz uning berilgan sanasini ko‘rsatib bo‘lmaydi',

      birthDateFuture:
        'Tug‘ilgan sana kelajakda bo‘lishi mumkin emas',
    },
  },

  staffEmployments: {
    title:
      'Mehnat tayinlovlari',

    description:
      'O‘qituvchilar va xodimlarni kafedra hamda lavozimlarga tayinlash, bandlik turi, stavka va ish muddatlarini yuritish.',

    create:
      'Tayinlov qo‘shish',

    createTitle:
      'Mehnat tayinlovini yaratish',

    editTitle:
      'Mehnat tayinlovini tahrirlash',

    detailsTitle:
      'Mehnat tayinlovi',

    archive:
      'Arxivlash',

    archiveTitle:
      'Tayinlovni arxivlash',

    archiveConfirm:
      '«{name}» xodimining tayinlovini arxivlaysizmi? Yozuvni keyinchalik tiklash mumkin.',

    archived:
      'Mehnat tayinlovi arxivga ko‘chirildi',

    active:
      'Faol',

    inactive:
      'Faol emas',

    allStatuses:
      'Barcha holatlar',

    allDepartments:
      'Barcha kafedralar',

    allPositions:
      'Barcha lavozimlar',

    allTypes:
      'Barcha bandlik turlari',

    allAssignments:
      'Barcha tayinlovlar',

    primaryOnly:
      'Faqat asosiy',

    additionalOnly:
      'Faqat qo‘shimcha',

    searchPlaceholder:
      'Xodim, kafedra yoki lavozim bo‘yicha qidirish...',

    types: {
      primary:
        'Asosiy ish joyi',

      internalPartTime:
        'Ichki o‘rindoshlik',

      externalPartTime:
        'Tashqi o‘rindoshlik',

      hourly:
        'Soatbay ish',
    },

    fields: {
      staffMember:
        'Xodim',

      faculty:
        'Fakultet',

      department:
        'Kafedra',

      position:
        'Lavozim',

      employmentType:
        'Bandlik turi',

      rate:
        'Stavka',

      startDate:
        'Ish boshlanish sanasi',

      endDate:
        'Ish tugash sanasi',

      primary:
        'Asosiy tayinlov',

      active:
        'Tayinlov faol',

      status:
        'Holat',

      documentNumber:
        'Buyruq raqami',

      documentDate:
        'Buyruq sanasi',

      notes:
        'Izoh',

      createdAt:
        'Yaratilgan',

      createdBy:
        'Yaratgan',

      updatedAt:
        'O‘zgartirilgan',

      updatedBy:
        'O‘zgartirgan',
    },

    sections: {
      assignment:
        'Tayinlov',

      period:
        'Ish davri',

      document:
        'Buyruq',

      audit:
        'O‘zgarishlar tarixi',
    },

    validation: {
      staffRequired:
        'Xodimni tanlang',

      departmentRequired:
        'Kafedrani tanlang',

      positionRequired:
        'Lavozimni tanlang',

      startDateRequired:
        'Ish boshlanish sanasini kiriting',

      rateRange:
        'Stavka 0,01 dan 3,00 gacha bo‘lishi kerak',

      endBeforeStart:
        'Tugash sanasi boshlanish sanasidan oldin bo‘lishi mumkin emas',
    },
  },

  staffAcademicYears: {
    title:
      'O‘quv yillari bo‘yicha kadr ma’lumotlari',

    description:
      'Har bir o‘quv yili uchun o‘qituvchining stavkasi, ilmiy darajasi va ilmiy unvonini qayd etish.',

    create:
      'Yozuv qo‘shish',

    createTitle:
      'O‘quv yili uchun kadr ma’lumotlari',

    editTitle:
      'Kadr ma’lumotlarini tahrirlash',

    archive:
      'Arxivlash',

    archiveTitle:
      'Kadr ma’lumotlarini arxivlash',

    archiveConfirm:
      '«{name}»ning {year} yil uchun ma’lumotlarini arxivlaysizmi?',

    archived:
      'Kadr ma’lumotlari arxivga ko‘chirildi',

    active:
      'Faol',

    inactive:
      'Faol emas',

    current:
      'Joriy',

    closed:
      'Yopilgan',

    allYears:
      'Barcha o‘quv yillari',

    allDepartments:
      'Barcha kafedralar',

    allStatuses:
      'Barcha holatlar',

    searchPlaceholder:
      'Xodim, kafedra, lavozim, daraja yoki unvon bo‘yicha qidirish...',

    bulkCreate:
      'Yetishmayotganlarni to‘ldirish',

    bulkTitle:
      'Kadr ma’lumotlarini ommaviy to‘ldirish',

    bulkDescription:
      'Tizim amaldagi mehnat tayinlovlari uchun yetishmayotgan yozuvlarni joriy stavka, daraja va unvon asosida yaratadi.',

    bulkRun:
      'To‘ldirish',

    bulkCompleted:
      'Ommaviy to‘ldirish yakunlandi',

    bulkResult:
      'Yaratildi: {created}; tiklandi: {restored}; o‘tkazib yuborildi: {skipped}; qoldi: {missing}.',

    fields: {
      employment:
        'Mehnat tayinlovi',

      staffMember:
        'Xodim',

      academicYear:
        'O‘quv yili',

      department:
        'Kafedra',

      position:
        'Lavozim',

      rate:
        'Stavka',

      academicDegree:
        'Ilmiy daraja',

      academicTitle:
        'Ilmiy unvon',

      recommendedHours:
        'Soat me’yori',

      active:
        'Yozuv faol',

      status:
        'Holat',

      notes:
        'Izoh',
    },

    validation: {
      employmentRequired:
        'Mehnat tayinlovini tanlang',

      yearRequired:
        'O‘quv yilini tanlang',

      rateRange:
        'Stavka 0,01 dan 3,00 gacha bo‘lishi kerak',
    },
  },

  workloadNorms: {
    title:
      'O‘quv yuklamasi me’yorlari',

    description:
      'O‘quv yili, stavka, ilmiy daraja va ilmiy unvon mavjudligiga qarab axborot xarakteridagi yillik yuklama me’yorlari.',

    create:
      'Me’yor qo‘shish',

    createTitle:
      'Yuklama me’yorini yaratish',

    editTitle:
      'Yuklama me’yorini tahrirlash',

    archive:
      'Arxivlash',

    archiveTitle:
      'Me’yorni arxivlash',

    archiveConfirm:
      '{year} yil, {rate} stavka uchun me’yorni arxivlaysizmi?',

    archived:
      'Yuklama me’yori arxivga ko‘chirildi',

    active:
      'Faol',

    inactive:
      'Faol emas',

    allYears:
      'Barcha o‘quv yillari',

    allStatuses:
      'Barcha holatlar',

    fields: {
      academicYear:
        'O‘quv yili',

      rate:
        'Stavka',

      hasDegree:
        'Ilmiy daraja mavjud',

      hasTitle:
        'Ilmiy unvon mavjud',

      annualHours:
        'Yillik soat me’yori',

      active:
        'Me’yor faol',

      status:
        'Holat',

      notes:
        'Izoh',
    },

    validation: {
      yearRequired:
        'O‘quv yilini tanlang',

      rateRange:
        'Stavka 0,01 dan 3,00 gacha bo‘lishi kerak',

      hoursRange:
        'Yillik me’yor 0 dan 10000 soatgacha bo‘lishi kerak',
    },
  },

  academicSettings: {
    title:
      'Akademik ma’lumotnomalar',

    description:
      'O‘quv yillari, ta’lim darajalari, ta’lim shakllari, davomiyligi va akademik semestrlar.',

    archiveConfirm:
      'Yozuvni arxivga ko‘chirasizmi?',

    tabs: {
      years:
        'O‘quv yillari',

      levels:
        'Ta’lim darajalari',

      forms:
        'Ta’lim shakllari',

      durations:
        'Davomiylik',

      semesters:
        'Semestrlar',
    },

    common: {
      code:
        'Kod',

      name:
        'Nomi',

      nameRu:
        'Rus tilidagi nomi',

      nameUz:
        'O‘zbek tilidagi nomi',

      sortOrder:
        'Tartib',

      active:
        'Faol',
    },

    academicYears: {
      createTitle:
        'O‘quv yilini yaratish',

      editTitle:
        'O‘quv yilini tahrirlash',

      open:
        'Ochiq',

      closed:
        'Yopilgan',

      close:
        'O‘quv yilini yopish',

      reopen:
        'Qayta ochish',

      closeTitle:
        'O‘quv yilini yopish',

      reopenTitle:
        'O‘quv yilini qayta ochish',

      closeDescription:
        '{year} o‘quv yilini yopasizmi? Yopilgandan so‘ng qayta ochilmaguncha ma’lumotlarni o‘zgartirib bo‘lmaydi.',

      reopenDescription:
        '{year} o‘quv yilini qayta ochasizmi? Sabab ko‘rsatilishi shart.',

      operationSuccess:
        'O‘quv yili holati muvaffaqiyatli o‘zgartirildi',

      fields: {
        name:
          'O‘quv yili',

        startYear:
          'Boshlanish yili',

        endYear:
          'Tugash yili',

        current:
          'Joriy',

        active:
          'Faol',

        status:
          'Holat',

        closingComment:
          'Yopish izohi',

        reopeningReason:
          'Qayta ochish sababi',
      },

      validation: {
        startYear:
          'Boshlanish yili 2000 dan 2200 gacha bo‘lishi kerak',

        endYear:
          'Tugash yili boshlanish yilidan keyingi yil bo‘lishi kerak',

        reopenReason:
          'Qayta ochish sababini kiriting',
      },
    },

    educationLevels: {
      createTitle:
        'Ta’lim darajasini qo‘shish',

      editTitle:
        'Ta’lim darajasini tahrirlash',

      codes: {
        bachelor:
          'Bakalavriat',

        master:
          'Magistratura',
      },
    },

    studyForms: {
      createTitle:
        'Ta’lim shaklini qo‘shish',

      editTitle:
        'Ta’lim shaklini tahrirlash',

      codes: {
        fullTime:
          'Kunduzgi',

        partTime:
          'Sirtqi',

        evening:
          'Kechki',

        distance:
          'Masofaviy',
      },
    },

    educationDurations: {
      createTitle:
        'Ta’lim davomiyligini qo‘shish',

      editTitle:
        'Ta’lim davomiyligini tahrirlash',

      fields: {
        level:
          'Ta’lim darajasi',

        studyForm:
          'Ta’lim shakli',

        semesters:
          'Semestrlar soni',

        months:
          'Davomiyligi, oy',
      },

      validation: {
        semesters:
          'Semestrlar soni 1 dan 20 gacha bo‘lishi kerak',

        months:
          'Davomiylik semestrlar soniga mos bo‘lishi kerak: 1 semestr = 6 oy',
      },
    },

    semesters: {
      createTitle:
        'Semestr yaratish',

      editTitle:
        'Semestrni tahrirlash',

      seasons: {
        autumn:
          'Kuzgi',

        spring:
          'Bahorgi',
      },

      fields: {
        academicYear:
          'O‘quv yili',

        season:
          'Semestr',

        startDate:
          'Boshlanish sanasi',

        endDate:
          'Tugash sanasi',

        current:
          'Joriy semestr',
      },

      validation: {
        endDate:
          'Tugash sanasi boshlanish sanasidan keyin bo‘lishi kerak',

        autumnYear:
          'Kuzgi semestr o‘quv yilining boshlanish yilida boshlanishi kerak',

        springYear:
          'Bahorgi semestr o‘quv yilining tugash yilida boshlanishi kerak',
      },
    },
  },

  studyPrograms: {
    title:
      'Ta’lim yo‘nalishlari',

    description:
      'Ta’lim yo‘nalishlari, ta’lim darajalari va profil kafedralarini boshqarish.',

    create:
      'Yo‘nalish qo‘shish',

    createTitle:
      'Ta’lim yo‘nalishini yaratish',

    editTitle:
      'Ta’lim yo‘nalishini tahrirlash',

    detailsTitle:
      'Ta’lim yo‘nalishi',

    archive:
      'Arxivlash',

    archiveTitle:
      'Yo‘nalishni arxivlash',

    archiveConfirm:
      '«{name}» yo‘nalishini arxivlaysizmi? Yozuvni keyinchalik tiklash mumkin.',

    archived:
      'Ta’lim yo‘nalishi arxivga ko‘chirildi',

    active:
      'Faol',

    inactive:
      'Faol emas',

    allStatuses:
      'Barcha holatlar',

    allUniversities:
      'Barcha universitetlar',

    allEducationLevels:
      'Barcha ta’lim darajalari',

    allDepartments:
      'Barcha profil kafedralar',

    searchPlaceholder:
      'Yo‘nalish kodi yoki nomi bo‘yicha qidirish...',

    fields: {
      code:
        'Yo‘nalish kodi',

      name:
        'Nomi',

      nameRu:
        'Rus tilidagi nomi',

      nameUz:
        'O‘zbek tilidagi nomi',

      university:
        'Universitet',

      educationLevel:
        'Ta’lim darajasi',

      profilingFaculty:
        'Profil fakultet',

      profilingDepartment:
        'Profil kafedra',

      sortOrder:
        'Saralash tartibi',

      active:
        'Yo‘nalish faol',

      status:
        'Holat',

      createdAt:
        'Yaratilgan',

      createdBy:
        'Yaratgan',

      updatedAt:
        'O‘zgartirilgan',

      updatedBy:
        'O‘zgartirgan',
    },

    sections: {
      general:
        'Asosiy ma’lumot',

      structure:
        'Akademik tuzilma',

      audit:
        'O‘zgarishlar tarixi',
    },

    validation: {
      universityRequired:
        'Universitetni tanlang',

      educationLevelRequired:
        'Ta’lim darajasini tanlang',

      codeRequired:
        'Yo‘nalish kodini kiriting',

      nameRuRequired:
        'Rus tilidagi nomni kiriting',

      nameUzRequired:
        'O‘zbek tilidagi nomni kiriting',

      departmentRequired:
        'Profil kafedrani tanlang',

      departmentUniversityMismatch:
        'Profil kafedra tanlangan universitetga tegishli bo‘lishi kerak',
    },
  },

  studentGroups: {
    title:
      'O‘quv guruhlari',

    description:
      'O‘quv guruhlari, ta’lim yo‘nalishlari, ta’lim shakllari va talabalar kontingentini boshqarish.',

    create:
      'Guruh qo‘shish',

    createTitle:
      'O‘quv guruhini yaratish',

    editTitle:
      'O‘quv guruhini tahrirlash',

    detailsTitle:
      'O‘quv guruhi',

    archive:
      'Arxivlash',

    archiveTitle:
      'Guruhni arxivlash',

    archiveConfirm:
      '«{code}» o‘quv guruhini arxivlaysizmi? Yozuvni keyinchalik tiklash mumkin.',

    archived:
      'O‘quv guruhi arxivga ko‘chirildi',

    active:
      'Faol',

    inactive:
      'Faol emas',

    currentYear:
      'Joriy o‘quv yili',

    closedYear:
      'Yopilgan o‘quv yili',

    allAdmissionYears:
      'Barcha qabul yillari',

    allFaculties:
      'Barcha fakultetlar',

    allPrograms:
      'Barcha yo‘nalishlar',

    allStudyForms:
      'Barcha ta’lim shakllari',

    allStatuses:
      'Barcha holatlar',

    searchPlaceholder:
      'Guruh kodi yoki ta’lim yo‘nalishi bo‘yicha qidirish...',

    noAvailableStudyForms:
      'Mavjud ta’lim shakllari yo‘q. Ta’lim davomiyligi ma’lumotnomasini tekshiring.',

    durationValue:
      '{months} oy / {semesters} sem.',

    fields: {
      code:
        'Guruh kodi',

      admissionYear:
        'Qabul qilingan o‘quv yili',

      graduationYear:
        'Rejalashtirilgan bitiruv yili',

      faculty:
        'Fakultet / bo‘lim',

      studyProgram:
        'Ta’lim yo‘nalishi',

      educationLevel:
        'Ta’lim darajasi',

      studyForm:
        'Ta’lim shakli',

      profilingFaculty:
        'Profil fakultet',

      profilingDepartment:
        'Profil kafedra',

      duration:
        'Me’yoriy ta’lim davomiyligi',

      studentCount:
        'Talabalar soni',

      subgroupCount:
        'Kichik guruhlar soni',

      active:
        'Guruh faol',

      status:
        'Holat',

      notes:
        'Izoh',

      createdAt:
        'Yaratilgan',

      createdBy:
        'Yaratgan',

      updatedAt:
        'O‘zgartirilgan',

      updatedBy:
        'O‘zgartirgan',
    },

    sections: {
      general:
        'Asosiy ma’lumotlar',

      education:
        'Ta’lim parametrlari',

      programInfo:
        'Tanlangan yo‘nalish parametrlari',

      profiling:
        'Profil bo‘linma',

      audit:
        'O‘zgarishlar tarixi',
    },

    validation: {
      codeRequired:
        'Guruh kodini kiriting',

      admissionYearRequired:
        'Qabul o‘quv yilini tanlang',

      facultyRequired:
        'Fakultet yoki bo‘limni tanlang',

      programRequired:
        'Ta’lim yo‘nalishini tanlang',

      studyFormRequired:
        'Ta’lim shaklini tanlang',

      studentCountRange:
        'Talabalar soni 0 dan 1000 gacha bo‘lishi kerak',

      subgroupCountRange:
        'Kichik guruhlar soni 1 dan 20 gacha bo‘lishi kerak',

      universityMismatch:
        'Guruh fakulteti va ta’lim yo‘nalishi bir universitetga tegishli bo‘lishi kerak',

      durationMissing:
        'Tanlangan yo‘nalish darajasi va ta’lim shakli uchun me’yoriy davomiylik belgilanmagan',

      graduationYear:
        'Bitiruv o‘quv yili qabul o‘quv yilidan keyin bo‘lishi kerak',
    },
  },

}

export default uz
