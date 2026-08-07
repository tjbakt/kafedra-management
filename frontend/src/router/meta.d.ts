import 'vue-router'

export {}

declare module 'vue-router' {
  interface RouteMeta {
    titleKey?: string
    descriptionKey?: string
    icon?: string
    breadcrumbKeys?: string[]
    guestOnly?: boolean
    requiresAuth?: boolean
    requiredPermissions?: string[]
    requiredGroups?: string[]
  }
}
