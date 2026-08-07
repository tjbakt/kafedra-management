import { computed } from 'vue'

import { useAuthStore } from '@/stores/auth'
import type {
  AccessRequirement,
  PermissionRequirement,
} from '@/types/access'

export function usePermissions() {
  const authStore = useAuthStore()

  const permissions = computed(
    () => authStore.user?.permissions ?? [],
  )

  const groups = computed(
    () => authStore.user?.groups ?? [],
  )

  const isStaff = computed(
    () => authStore.user?.is_staff ?? false,
  )

  function can(
    permission: string,
  ): boolean {
    return authStore.hasPermission(permission)
  }

  function canAny(
    requirement: PermissionRequirement,
  ): boolean {
    if (typeof requirement === 'string') {
      return can(requirement)
    }

    if (requirement.length === 0) {
      return true
    }

    return requirement.some(
      (permission) =>
        authStore.hasPermission(permission),
    )
  }

  function canAll(
    requirement: PermissionRequirement,
  ): boolean {
    if (typeof requirement === 'string') {
      return can(requirement)
    }

    if (requirement.length === 0) {
      return true
    }

    return requirement.every(
      (permission) =>
        authStore.hasPermission(permission),
    )
  }

  function inGroup(
    group: string,
  ): boolean {
    return authStore.hasGroup(group)
  }

  function inAnyGroup(
    requiredGroups: readonly string[],
  ): boolean {
    if (requiredGroups.length === 0) {
      return true
    }

    return requiredGroups.some(
      (group) => authStore.hasGroup(group),
    )
  }

  function inAllGroups(
    requiredGroups: readonly string[],
  ): boolean {
    if (requiredGroups.length === 0) {
      return true
    }

    return requiredGroups.every(
      (group) => authStore.hasGroup(group),
    )
  }

  function hasAccess(
    requirement: AccessRequirement = {},
  ): boolean {
    if (!authStore.isAuthenticated) {
      return false
    }

    if (authStore.user?.is_staff) {
      return true
    }

    if (
      requirement.staffOnly &&
      !authStore.user?.is_staff
    ) {
      return false
    }

    if (
      requirement.permissions &&
      requirement.permissions.length
    ) {
      const allowed =
        requirement.permissionMode === 'any'
          ? canAny(requirement.permissions)
          : canAll(requirement.permissions)

      if (!allowed) {
        return false
      }
    }

    if (
      requirement.groups &&
      requirement.groups.length
    ) {
      const allowed =
        requirement.groupMode === 'all'
          ? inAllGroups(requirement.groups)
          : inAnyGroup(requirement.groups)

      if (!allowed) {
        return false
      }
    }

    return true
  }

  return {
    permissions,
    groups,
    isStaff,

    can,
    canAny,
    canAll,

    inGroup,
    inAnyGroup,
    inAllGroups,

    hasAccess,
  }
}
