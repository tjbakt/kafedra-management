import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from 'vue-router'

import i18n from '@/i18n'
import { useAuthStore } from '@/stores/auth'

const moduleRoutes: RouteRecordRaw[] = [
  {
    path: 'departments',
    name: 'departments',
    component: () =>
      import(
        '@/modules/departments/DepartmentView.vue'
        ),

    meta: {
      requiresAuth: true,

      requiredPermissions: [
        'organizations.view_department',
      ],

      titleKey:
        'navigation.departments',

      descriptionKey:
        'modules.departmentsDescription',

      icon:
        'pi pi-building',

      breadcrumbKeys: [
        'navigation.departments',
      ],
    },
  },
  {
    path: 'teachers',

    name: 'teachers',

    component: () =>
      import(
        '@/modules/staff/StaffMembersView.vue'
        ),

    meta: {
      requiresAuth: true,

      requiredPermissions: [
        'staff.view_staffmember',
      ],

      titleKey:
        'navigation.teachers',

      descriptionKey:
        'modules.teachersDescription',

      icon:
        'pi pi-users',

      breadcrumbKeys: [
        'navigation.teachers',
      ],
    },
  },
  {
    path: 'student-groups',
    name: 'student-groups',
    component: () =>
      import(
        '@/modules/student-groups/StudentGroupsView.vue'
        ),
    meta: {
      requiresAuth: true,
      requiredPermissions: [
        'academics.view_studentgroup',
      ],
      titleKey: 'navigation.studentGroups',
      icon: 'pi pi-users',
      breadcrumbKeys: [
        'navigation.academicSettings',
        'navigation.studentGroups',
      ],
    },
  },
  {
    path: 'disciplines',
    name: 'disciplines',
    component: () =>
      import('@/views/ModulePlaceholderView.vue'),
    meta: {
      requiresAuth: true,
      titleKey: 'navigation.disciplines',
      descriptionKey:
        'modules.disciplinesDescription',
      icon: 'pi pi-bookmark',
      breadcrumbKeys: [
        'navigation.disciplines',
      ],
    },
  },
  {
    path: 'curriculum-references',
    name: 'curriculum-references',
    component: () =>
      import(
        '@/modules/curriculum-references/CurriculumReferencesView.vue'
        ),
    meta: {
      requiresAuth: true,
      requiredPermissions: [
        'curriculum.view_discipline',
      ],
      titleKey: 'navigation.curriculumReferences',
      icon: 'pi pi-book',
      breadcrumbKeys: [
        'navigation.curriculumReferences',
      ],
    },
  },
  {
    path: 'curricula',
    name: 'curricula',
    component: () =>
      import(
        '@/modules/curricula/CurriculaView.vue'
        ),
    meta: {
      requiresAuth: true,
      requiredPermissions: [
        'curriculum.view_curriculum',
      ],
      titleKey: 'navigation.curricula',
      icon: 'pi pi-list-check',
      breadcrumbKeys: [
        'navigation.curriculumReferences',
        'navigation.curricula',
      ],
    },
  },
  {
    path: 'curricula/:curriculumId/disciplines',
    name: 'curriculum-disciplines',
    component: () =>
      import(
        '@/modules/curriculum-disciplines/CurriculumDisciplinesView.vue'
        ),
    meta: {
      requiresAuth: true,
      requiredPermissions: [
        'curriculum.view_curriculumdiscipline',
      ],
      titleKey: 'navigation.curriculumDisciplines',
      icon: 'pi pi-table',

      breadcrumbKeys: [
        'navigation.curricula',
        'navigation.curriculumDisciplines',
      ],
    },
  },

  {
    path: 'workload',
    name: 'workload',
    component: () =>
      import('@/views/ModulePlaceholderView.vue'),
    meta: {
      requiresAuth: true,
      titleKey: 'navigation.workload',
      descriptionKey:
        'modules.workloadDescription',
      icon: 'pi pi-chart-bar',
      breadcrumbKeys: [
        'navigation.workload',
      ],
    },
  },
  {
    path: 'schedules',
    name: 'schedules',
    component: () =>
      import('@/views/ModulePlaceholderView.vue'),
    meta: {
      requiresAuth: true,
      titleKey: 'navigation.schedules',
      descriptionKey:
        'modules.schedulesDescription',
      icon: 'pi pi-calendar',
      breadcrumbKeys: [
        'navigation.schedules',
      ],
    },
  },
  {
    path: 'reports',
    name: 'reports',
    component: () =>
      import('@/views/ModulePlaceholderView.vue'),
    meta: {
      requiresAuth: true,
      titleKey: 'navigation.reports',
      descriptionKey:
        'modules.reportsDescription',
      icon: 'pi pi-file-export',
      breadcrumbKeys: ['navigation.reports'],
    },
  },
  {
    path: 'settings',
    name: 'settings',
    component: () =>
      import('@/views/ModulePlaceholderView.vue'),
    meta: {
      requiresAuth: true,
      titleKey: 'navigation.settings',
      descriptionKey:
        'modules.settingsDescription',
      icon: 'pi pi-cog',
      breadcrumbKeys: [
        'navigation.settings',
      ],
    },
  },
]

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () =>
      import('@/layouts/DefaultLayout.vue'),
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () =>
          import('@/views/DashboardView.vue'),
        meta: {
          requiresAuth: true,
          titleKey: 'dashboard.title',
        },
      },
      {
        path: 'staff-employments',

        name: 'staff-employments',

        component: () =>
          import(
            '@/modules/staff-employments/StaffEmploymentsView.vue'
            ),

        meta: {
          requiresAuth: true,

          requiredPermissions: [
            'staff.view_staffemployment',
          ],

          titleKey:
            'navigation.staffEmployments',

          icon:
            'pi pi-briefcase',

          breadcrumbKeys: [
            'navigation.teachers',
            'navigation.staffEmployments',
          ],
        },
      },
      {
        path: 'staff-academic-years',
        name: 'staff-academic-years',
        component: () =>
          import(
            '@/modules/staff-academic-years/StaffAcademicYearsView.vue'
            ),
        meta: {
          requiresAuth: true,
          requiredPermissions: [
            'staff.view_staffemploymentacademicyear',
          ],
          titleKey: 'navigation.staffAcademicYears',
          icon:'pi pi-calendar-clock',
          breadcrumbKeys: [
            'navigation.teachers',
            'navigation.staffAcademicYears',
          ],
        },
      },

      {
        path: 'workload-norms',
        name: 'workload-norms',
        component: () =>
          import(
            '@/modules/staff-academic-years/WorkloadNormsView.vue'
            ),
        meta: {
          requiresAuth: true,
          requiredPermissions: [
            'staff.view_workloadnorm',
          ],
          titleKey: 'navigation.workloadNorms',
          icon: 'pi pi-chart-bar',
          breadcrumbKeys: [
            'navigation.workload',
            'navigation.workloadNorms',
          ],
        },
      },

      {
        path: 'academic-settings',
        name: 'academic-settings',
        component: () =>
          import(
            '@/modules/academic-settings/AcademicSettingsView.vue'
            ),
        meta: {
          requiresAuth: true,
          requiredPermissions: [
            'academics.view_academicyear',
          ],
          titleKey: 'navigation.academicSettings',
          icon: 'pi pi-graduation-cap',
          breadcrumbKeys: [
            'navigation.academicSettings',
          ],
        },
      },

      {
        path: 'study-programs',
        name: 'study-programs',
        component: () =>
          import(
            '@/modules/study-programs/StudyProgramsView.vue'
            ),
        meta: {
          requiresAuth: true,
          requiredPermissions: [
            'academics.view_studyprogram',
          ],
          titleKey: 'navigation.studyPrograms',
          icon: 'pi pi-book',
          breadcrumbKeys: [
            'navigation.academicSettings',
            'navigation.studyPrograms',
          ],
        },
      },

      {
        path: 'access-debug',
        name: 'access-debug',

        component: () =>
          import(
            '@/views/AccessDebugView.vue'
            ),

        meta: {
          requiresAuth: true,
          staffOnly: true,

          titleKey:
            'access.debugTitle',

          breadcrumbKeys: [
            'access.debugTitle',
          ],
        },
      },
      ...moduleRoutes,
    ],
  },
  {
    path: '/login',
    component: () =>
      import('@/layouts/AuthLayout.vue'),
    children: [
      {
        path: '',
        name: 'login',
        component: () =>
          import('@/views/LoginView.vue'),
        meta: {
          titleKey: 'auth.loginTitle',
          guestOnly: true,
        },
      },
      {
        path: 'change-password',
        name: 'change-password',
        component: () =>
          import(
            '@/views/ChangePasswordView.vue'
          ),
        meta: {
          titleKey: 'auth.changePassword',
          requiresAuth: true,
        },
      },
    ],
  },
  {
    path: '/403',
    component: () =>
      import('@/layouts/EmptyLayout.vue'),

    children: [
      {
        path: '',
        name: 'forbidden',
        component: () =>
          import(
            '@/views/ForbiddenView.vue'
            ),

        meta: {
          titleKey:
            'errors.forbiddenTitle',
          requiresAuth: true,
        },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    component: () =>
      import('@/layouts/EmptyLayout.vue'),
    children: [
      {
        path: '',
        name: 'not-found',
        component: () =>
          import('@/views/NotFoundView.vue'),
        meta: {
          titleKey: 'errors.notFoundTitle',
        },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(
    import.meta.env.BASE_URL,
  ),
  routes,

  scrollBehavior() {
    return {
      top: 0,
      behavior: 'smooth',
    }
  },
})

function updateDocumentTitle(
  titleKey?: unknown,
): void {
  const appName =
    import.meta.env.VITE_APP_NAME ||
    'Kafedra Management'

  const pageTitle =
    typeof titleKey === 'string'
      ? i18n.global.t(titleKey)
      : ''

  document.title = pageTitle
    ? `${pageTitle} — ${appName}`
    : appName
}

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (!authStore.initialized) {
    await authStore.initialize()
  }

  updateDocumentTitle(to.meta.titleKey)

  if (
    to.meta.requiresAuth &&
    !authStore.isAuthenticated
  ) {
    return {
      name: 'login',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  if (
    to.meta.guestOnly &&
    authStore.isAuthenticated
  ) {
    if (authStore.user?.must_change_password) {
      return {
        name: 'change-password',
      }
    }

    return {
      name: 'dashboard',
    }
  }

  if (
    authStore.isAuthenticated &&
    authStore.user?.must_change_password &&
    to.name !== 'change-password'
  ) {
    return {
      name: 'change-password',
    }
  }

  if (
    to.name === 'change-password' &&
    authStore.isAuthenticated &&
    !authStore.user?.must_change_password
  ) {
    return {
      name: 'dashboard',
    }
  }
  if (
    authStore.isAuthenticated &&
    to.name !== 'forbidden'
  ) {
    if (
      to.meta.staffOnly &&
      !authStore.user?.is_staff
    ) {
      return {
        name: 'forbidden',
      }
    }

    const requiredPermissions =
      to.meta.requiredPermissions ?? []

    if (requiredPermissions.length) {
      const hasPermissions =
        to.meta.permissionMode === 'any'
          ? authStore.hasAnyPermission(
            [...requiredPermissions],
          )
          : authStore.hasAllPermissions(
            requiredPermissions,
          )

      if (!hasPermissions) {
        return {
          name: 'forbidden',
        }
      }
    }

    const requiredGroups =
      to.meta.requiredGroups ?? []

    if (requiredGroups.length) {
      const hasGroups =
        to.meta.groupMode === 'all'
          ? authStore.hasAllGroups(
            requiredGroups,
          )
          : authStore.hasAnyGroup(
            requiredGroups,
          )

      if (!hasGroups) {
        return {
          name: 'forbidden',
        }
      }
    }
  }

  return true
})

export function refreshDocumentTitle(): void {
  updateDocumentTitle(
    router.currentRoute.value.meta.titleKey,
  )
}

export default router
