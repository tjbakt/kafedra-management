<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Badge from 'primevue/badge'

import { useLayoutStore } from '@/stores/layout'
import type { SidebarItem } from '@/types/layout'
import { usePermissions } from '@/composables/usePermissions'


interface TranslatedSidebarItem extends SidebarItem {
  labelKey: string
  children?: TranslatedSidebarItem[]
}

const route = useRoute()
const router = useRouter()
const layoutStore = useLayoutStore()
const { t } = useI18n()
const { hasAccess } = usePermissions()

const menuDefinitions: TranslatedSidebarItem[] = [
  {
    label: '',
    labelKey: 'navigation.dashboard',
    icon: 'pi pi-home',
    route: '/',
  },
  {
    label: '',
    labelKey: 'navigation.organizationalStructure',
    icon: 'pi pi-sitemap',
    children: [
      {
        label: '',
        labelKey: 'navigation.departments',
        icon: 'pi pi-building',
        route: '/departments',
        permissions: [
          'organizations.view_department',
        ],
      },
      {
        label: '',
        labelKey: 'navigation.teachers',
        icon: 'pi pi-users',
        route: '/teachers',
        permissions: [
          'staff.view_staffmember',
        ],
      },
      {
        label: '',
        labelKey: 'navigation.staffEmployments',
        icon: 'pi pi-briefcase',
        route: '/staff-employments',
        permissions: [
          'staff.view_staffemployment',
        ],
      },
      {
        label: '',
        labelKey: 'navigation.staffAcademicYears',
        icon: 'pi pi-calendar-clock',
        route: '/staff-academic-years',
        permissions: [
          'staff.view_staffemploymentacademicyear',
        ],
      },
      {
        label: '',
        labelKey: 'navigation.workloadNorms',
        icon: 'pi pi-chart-bar',
        route: '/workload-norms',
        permissions: [
          'staff.view_workloadnorm',
        ],
      },
      {
        label: '',
        labelKey: 'navigation.academicSettings',
        icon: 'pi pi-graduation-cap',
        route: '/academic-settings',
        permissions: [
          'academics.view_academicyear',
        ],
      },
      {
        label: '',
        labelKey: 'navigation.studyPrograms',
        icon: 'pi pi-book',
        route: '/study-programs',
        permissions: [
          'academics.view_studyprogram',
        ],
      },

      {
        label: '',
        labelKey: 'navigation.studentGroups',
        icon: 'pi pi-user',
        route: '/student-groups',
        permissions: [
          'academics.view_studentgroup',
        ],
      },
    ],
  },
  {
    label: '',
    labelKey: 'navigation.educationalProcess',
    icon: 'pi pi-book',
    children: [
      {
        label: '',
        labelKey: 'navigation.disciplines',
        icon: 'pi pi-bookmark',
        route: '/disciplines',
      },
      {
        label: '',
        labelKey: 'navigation.curriculumReferences',
        icon: 'pi pi-book',
        route: '/curriculum-references',
        permissions: [
          'curriculum.view_discipline',
        ],
      },
      {
        label: '',
        labelKey: 'navigation.curricula',
        icon: 'pi pi-list-check',
        route: '/curricula',
        permissions: [
          'curriculum.view_curriculum',
        ],
      },
      {
        label: '',
        labelKey: 'navigation.workload',
        icon: 'pi pi-chart-bar',
        route: '/workload',
        badge: '!',
      },
      {
        label: '',
        labelKey: 'navigation.schedules',
        icon: 'pi pi-calendar',
        route: '/schedules',
      },
    ],
  },
  {
    label: '',
    labelKey: 'navigation.analytics',
    icon: 'pi pi-chart-line',
    children: [
      {
        label: '',
        labelKey: 'navigation.reports',
        icon: 'pi pi-file-export',
        route: '/reports',
      },
    ],
  },
  {
    label: '',
    labelKey: 'navigation.system',
    icon: 'pi pi-cog',
    children: [
      {
        label: '',
        labelKey: 'navigation.settings',
        icon: 'pi pi-sliders-h',
        route: '/settings',
      },
      {
        label: '',
        labelKey:
          'access.debugTitle',

        icon:
          'pi pi-shield',

        route:
          '/access-debug',

        staffOnly: true,
      },
    ],
  },
];

const menuItems =
  computed<TranslatedSidebarItem[]>(
    () => {
      return menuDefinitions
        .map((item) => {
          const children =
            item.children
              ?.map((child) => ({
                ...child,
                label:
                  t(child.labelKey),
              }))
              .filter(canShowItem)

          return {
            ...item,
            label:
              t(item.labelKey),
            children,
          }
        })
        .filter((item) => {
          if (!canShowItem(item)) {
            return false
          }

          if (
            item.children &&
            item.children.length === 0
          ) {
            return false
          }

          return true
        })
    },
  )

const sidebarClass = computed(() => ({
  'app-sidebar--collapsed': layoutStore.sidebarCollapsed,
  'app-sidebar--mobile-visible':
    layoutStore.mobileSidebarVisible,
}))

function isActive(item: SidebarItem): boolean {
  if (!item.route) {
    return (
      item.children?.some((child) =>
        route.path.startsWith(child.route ?? ''),
      ) ?? false
    )
  }

  if (item.route === '/') {
    return route.path === '/'
  }

  return route.path.startsWith(item.route)
}

async function navigate(item: SidebarItem): Promise<void> {
  if (!item.route) {
    return
  }

  await router.push(item.route)
  layoutStore.closeMobileSidebar()
}

function canShowItem(
  item: TranslatedSidebarItem,
): boolean {
  return hasAccess({
    permissions:
      item.permissions,

    permissionMode:
      item.permissionMode,

    groups:
      item.groups,

    groupMode:
      item.groupMode,

    staffOnly:
      item.staffOnly,
  })
}
</script>

<template>
  <aside class="app-sidebar" :class="sidebarClass">
    <div class="app-sidebar__brand">
      <div class="app-sidebar__logo">
        <i class="pi pi-graduation-cap" />
      </div>

      <div class="app-sidebar__brand-text">
        <strong>Kafedra</strong>
        <span>Management</span>
      </div>
    </div>

    <nav class="app-sidebar__navigation" aria-label="Основная навигация">
      <template v-for="item in menuItems" :key="item.label">
        <div v-if="item.children" class="sidebar-group">
          <div
            v-tooltip.right="layoutStore.sidebarCollapsed ? item.label : undefined"
            class="sidebar-group__title"
            :class="{ 'sidebar-group__title--active': isActive(item) }"
          >
            <i :class="item.icon" />
            <span>{{ item.label }}</span>
          </div>

          <button
            v-for="child in item.children"
            :key="child.label"
            v-tooltip.right="layoutStore.sidebarCollapsed ? child.label : undefined"
            type="button"
            class="sidebar-link sidebar-link--child"
            :class="{ 'sidebar-link--active': isActive(child) }"
            @click="navigate(child)"
          >
            <i :class="child.icon" />

            <span class="sidebar-link__label">{{ child.label }}</span>

            <Badge
              v-if="child.badge"
              class="sidebar-link__badge"
              :value="child.badge"
              severity="warn"
              size="small"
            />
          </button>
        </div>

        <button
          v-else
          v-tooltip.right="layoutStore.sidebarCollapsed ? item.label : undefined"
          type="button"
          class="sidebar-link"
          :class="{ 'sidebar-link--active': isActive(item) }"
          @click="navigate(item)"
        >
          <i :class="item.icon" />
          <span class="sidebar-link__label">{{ item.label }}</span>
        </button>
      </template>
    </nav>

    <div class="app-sidebar__footer">
      <div class="sidebar-version">
        <i class="pi pi-code" />

        <span>
          <strong>
            {{ t('app.version', {version: '0.2.0'}) }}
          </strong>
          <small>
            {{ t('app.frontendLayout') }}
          </small>
        </span>
      </div>
    </div>
  </aside>

  <Transition name="fade">
    <button
      v-if="layoutStore.mobileSidebarVisible"
      type="button"
      class="app-sidebar-overlay"
      aria-label="Закрыть боковое меню"
      @click="layoutStore.closeMobileSidebar"
    />
  </Transition>
</template>

<style scoped>
.app-sidebar {
  position: fixed;
  z-index: var(--app-z-sidebar);
  inset: 0 auto 0 0;
  display: flex;
  width: var(--app-sidebar-width);
  flex-direction: column;
  border-right: 1px solid var(--app-border-color);
  background: var(--app-sidebar-bg);
  color: var(--app-sidebar-text);
  transition:
    width var(--app-transition),
    transform var(--app-transition);
}

.app-sidebar__brand {
  display: flex;
  height: var(--app-header-height);
  flex: 0 0 var(--app-header-height);
  align-items: center;
  gap: 0.75rem;
  padding: 0 1.1rem;
  border-bottom: 1px solid var(--app-sidebar-border);
}

.app-sidebar__logo {
  display: grid;
  width: 2.4rem;
  height: 2.4rem;
  flex: 0 0 2.4rem;
  place-items: center;
  border-radius: 0.75rem;
  background: var(--app-primary);
  color: white;
}

.app-sidebar__logo i {
  font-size: 1.25rem;
}

.app-sidebar__brand-text {
  display: grid;
  overflow: hidden;
  line-height: 1;
  white-space: nowrap;
}

.app-sidebar__brand-text strong {
  font-size: 1.1rem;
}

.app-sidebar__brand-text span {
  margin-top: 0.25rem;
  color: var(--app-sidebar-text-muted);
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.app-sidebar__navigation {
  flex: 1;
  padding: 1rem 0.75rem;
  overflow-x: hidden;
  overflow-y: auto;
}

.sidebar-group {
  margin-top: 0.7rem;
}

.sidebar-group:first-child {
  margin-top: 0;
}

.sidebar-group__title,
.sidebar-link {
  display: flex;
  width: 100%;
  min-height: 2.65rem;
  align-items: center;
  gap: 0.8rem;
  border: 0;
  border-radius: 0.65rem;
  background: transparent;
  color: inherit;
  text-align: left;
}

.sidebar-group__title {
  padding: 0 0.75rem;
  color: var(--app-sidebar-text-muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.sidebar-link {
  position: relative;
  margin: 0.15rem 0;
  padding: 0 0.75rem;
  cursor: pointer;
}

.sidebar-link:hover {
  background: var(--app-sidebar-hover);
}

.sidebar-link--active {
  background: var(--app-sidebar-active);
  color: white;
}

.sidebar-link--active:hover {
  background: var(--app-sidebar-active);
}

.sidebar-link--child {
  padding-left: 1.2rem;
}

.sidebar-link > i,
.sidebar-group__title > i {
  width: 1.35rem;
  flex: 0 0 1.35rem;
  text-align: center;
}

.sidebar-link__label {
  flex: 1;
  overflow: hidden;
  font-size: 0.85rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar-link__badge {
  margin-left: auto;
}

.app-sidebar__footer {
  padding: 0.8rem;
  border-top: 1px solid var(--app-sidebar-border);
}

.sidebar-version {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.65rem;
  border-radius: 0.65rem;
  background: var(--app-sidebar-hover);
}

.sidebar-version > i {
  width: 1.35rem;
  text-align: center;
}

.sidebar-version span {
  display: grid;
  gap: 0.1rem;
  overflow: hidden;
  white-space: nowrap;
}

.sidebar-version strong {
  font-size: 0.73rem;
}

.sidebar-version small {
  color: var(--app-sidebar-text-muted);
  font-size: 0.65rem;
}

.app-sidebar--collapsed {
  width: var(--app-sidebar-collapsed-width);
}

.app-sidebar--collapsed .app-sidebar__brand-text,
.app-sidebar--collapsed .sidebar-link__label,
.app-sidebar--collapsed .sidebar-link__badge,
.app-sidebar--collapsed .sidebar-group__title span,
.app-sidebar--collapsed .sidebar-version span {
  display: none;
}

.app-sidebar--collapsed .app-sidebar__brand,
.app-sidebar--collapsed .sidebar-group__title,
.app-sidebar--collapsed .sidebar-link,
.app-sidebar--collapsed .sidebar-version {
  justify-content: center;
}

.app-sidebar--collapsed .sidebar-link,
.app-sidebar--collapsed .sidebar-group__title {
  padding: 0;
}

.app-sidebar-overlay {
  position: fixed;
  z-index: calc(var(--app-z-sidebar) - 1);
  inset: 0;
  border: 0;
  background: rgb(15 23 42 / 55%);
}

@media (max-width: 991px) {
  .app-sidebar {
    width: min(var(--app-sidebar-width), 86vw);
    transform: translateX(-100%);
  }

  .app-sidebar--mobile-visible {
    transform: translateX(0);
  }

  .app-sidebar--collapsed {
    width: min(var(--app-sidebar-width), 86vw);
  }

  .app-sidebar--collapsed .app-sidebar__brand-text,
  .app-sidebar--collapsed .sidebar-link__label,
  .app-sidebar--collapsed .sidebar-link__badge,
  .app-sidebar--collapsed .sidebar-group__title span,
  .app-sidebar--collapsed .sidebar-version span {
    display: grid;
  }

  .app-sidebar--collapsed .app-sidebar__brand,
  .app-sidebar--collapsed .sidebar-group__title,
  .app-sidebar--collapsed .sidebar-link,
  .app-sidebar--collapsed .sidebar-version {
    justify-content: flex-start;
  }

  .app-sidebar--collapsed .sidebar-link,
  .app-sidebar--collapsed .sidebar-group__title {
    padding: 0 0.75rem;
  }

  .app-sidebar--collapsed .sidebar-link--child {
    padding-left: 1.2rem;
  }
}
</style>
