export type PermissionRequirement =
  | string
  | readonly string[]

export type PermissionMode = 'all' | 'any'

export interface AccessRequirement {
  permissions?: readonly string[]
  permissionMode?: PermissionMode
  groups?: readonly string[]
  groupMode?: PermissionMode
  staffOnly?: boolean
}

export interface AccessCheckOptions
  extends AccessRequirement {
  authenticated?: boolean
}
