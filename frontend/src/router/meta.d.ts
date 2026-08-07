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

    requiredPermissions?: readonly string[]
    permissionMode?: 'all' | 'any'

    requiredGroups?: readonly string[]
    groupMode?: 'all' | 'any'

    staffOnly?: boolean
  }
}
