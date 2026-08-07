import type {
  PermissionMode,
} from '@/types/access'

export interface SidebarItem {
  label: string
  labelKey?: string

  icon: string
  route?: string

  badge?: string | number
  badgeSeverity?:
    | 'success'
    | 'info'
    | 'warn'
    | 'danger'
    | 'secondary'
    | 'contrast'

  permissions?: readonly string[]
  permissionMode?: PermissionMode

  groups?: readonly string[]
  groupMode?: PermissionMode

  staffOnly?: boolean

  children?: SidebarItem[]
}

export interface BreadcrumbItem {
  label: string
  route?: string
  icon?: string
}
