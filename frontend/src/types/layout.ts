export interface SidebarItem {
  label: string
  icon: string
  route?: string
  badge?: string | number
  children?: SidebarItem[]
}

export interface BreadcrumbItem {
  label: string
  route?: string
  icon?: string
}
