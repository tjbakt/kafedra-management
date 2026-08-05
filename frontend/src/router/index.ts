import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const moduleRoutes: RouteRecordRaw[] = [
  {
    path: 'departments',
    name: 'departments',
    component: () => import('@/views/ModulePlaceholderView.vue'),
    meta: {
      title: 'Кафедры',
      description: 'Управление кафедрами и организационной структурой.',
      icon: 'pi pi-building',
      breadcrumb: [{ label: 'Кафедры' }],
    },
  },
  {
    path: 'teachers',
    name: 'teachers',
    component: () => import('@/views/ModulePlaceholderView.vue'),
    meta: {
      title: 'Преподаватели',
      description: 'Справочник преподавателей, ставок, степеней и учёных званий.',
      icon: 'pi pi-users',
      breadcrumb: [{ label: 'Преподаватели' }],
    },
  },
  {
    path: 'students',
    name: 'students',
    component: () => import('@/views/ModulePlaceholderView.vue'),
    meta: {
      title: 'Студенческие группы',
      description: 'Управление академическими группами и контингентом.',
      icon: 'pi pi-id-card',
      breadcrumb: [{ label: 'Студенческие группы' }],
    },
  },
  {
    path: 'disciplines',
    name: 'disciplines',
    component: () => import('@/views/ModulePlaceholderView.vue'),
    meta: {
      title: 'Дисциплины',
      description: 'Справочник учебных дисциплин.',
      icon: 'pi pi-bookmark',
      breadcrumb: [{ label: 'Дисциплины' }],
    },
  },
  {
    path: 'curriculum',
    name: 'curriculum',
    component: () => import('@/views/ModulePlaceholderView.vue'),
    meta: {
      title: 'Учебные планы',
      description: 'Формирование и сопровождение учебных планов образовательных программ.',
      icon: 'pi pi-list-check',
      breadcrumb: [{ label: 'Учебные планы' }],
    },
  },
  {
    path: 'workload',
    name: 'workload',
    component: () => import('@/views/ModulePlaceholderView.vue'),
    meta: {
      title: 'Учебная нагрузка',
      description: 'Расчёт и распределение учебной нагрузки между преподавателями.',
      icon: 'pi pi-chart-bar',
      breadcrumb: [{ label: 'Учебная нагрузка' }],
    },
  },
  {
    path: 'schedules',
    name: 'schedules',
    component: () => import('@/views/ModulePlaceholderView.vue'),
    meta: {
      title: 'Расписание',
      description: 'Планирование и просмотр расписания занятий.',
      icon: 'pi pi-calendar',
      breadcrumb: [{ label: 'Расписание' }],
    },
  },
  {
    path: 'reports',
    name: 'reports',
    component: () => import('@/views/ModulePlaceholderView.vue'),
    meta: {
      title: 'Отчёты',
      description: 'Формирование аналитических отчётов, PDF и Excel.',
      icon: 'pi pi-file-export',
      breadcrumb: [{ label: 'Отчёты' }],
    },
  },
  {
    path: 'settings',
    name: 'settings',
    component: () => import('@/views/ModulePlaceholderView.vue'),
    meta: {
      title: 'Настройки',
      description: 'Пользователи, роли, права доступа и параметры системы.',
      icon: 'pi pi-cog',
      breadcrumb: [{ label: 'Настройки' }],
    },
  },
]

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: {
          title: 'Панель управления',
        },
      },
      ...moduleRoutes,
    ],
  },
  {
    path: '/login',
    component: () => import('@/layouts/AuthLayout.vue'),
    children: [
      {
        path: '',
        name: 'login',
        component: () => import('@/views/LoginView.vue'),
        meta: {
          title: 'Вход в систему',
          guestOnly: true,
        },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    component: () => import('@/layouts/EmptyLayout.vue'),
    children: [
      {
        path: '',
        name: 'not-found',
        component: () => import('@/views/NotFoundView.vue'),
        meta: {
          title: 'Страница не найдена',
        },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,

  scrollBehavior() {
    return {
      top: 0,
      behavior: 'smooth',
    }
  },
})

router.beforeEach((to) => {
  const appName = import.meta.env.VITE_APP_NAME || 'Kafedra Management'
  const pageTitle = String(to.meta.title || '')

  document.title = pageTitle ? `${pageTitle} — ${appName}` : appName

  return true
})

export default router
