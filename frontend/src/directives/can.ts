import type {
  Directive,
  DirectiveBinding,
} from 'vue'

import type { Pinia } from 'pinia'

import { useAuthStore } from '@/stores/auth'
import type {
  AccessRequirement,
} from '@/types/access'

export type CanDirectiveValue =
  | string
  | readonly string[]
  | AccessRequirement

function normalizeRequirement(
  value: CanDirectiveValue,
): AccessRequirement {
  if (typeof value === 'string') {
    return {
      permissions: [value],
    }
  }

  if (Array.isArray(value)) {
    return {
      permissions: value,
      permissionMode: 'all',
    }
  }

  return value as AccessRequirement
}

function isAllowed(
  pinia: Pinia,
  binding: DirectiveBinding<
    CanDirectiveValue
  >,
): boolean {
  const authStore = useAuthStore(pinia)

  if (!authStore.isAuthenticated) {
    return false
  }

  if (authStore.user?.is_staff) {
    return true
  }

  const requirement =
    normalizeRequirement(binding.value)

  if (requirement.staffOnly) {
    return false
  }

  if (
    requirement.permissions?.length
  ) {
    const hasPermission =
      requirement.permissionMode === 'any'
        ? authStore.hasAnyPermission(
            [...requirement.permissions],
          )
        : authStore.hasAllPermissions(
            requirement.permissions,
          )

    if (!hasPermission) {
      return false
    }
  }

  if (requirement.groups?.length) {
    const hasGroup =
      requirement.groupMode === 'all'
        ? authStore.hasAllGroups(
            requirement.groups,
          )
        : authStore.hasAnyGroup(
            requirement.groups,
          )

    if (!hasGroup) {
      return false
    }
  }

  return true
}

function applyVisibility(
  element: HTMLElement,
  allowed: boolean,
): void {
  element.style.display = allowed
    ? ''
    : 'none'
}

export function createCanDirective(
  pinia: Pinia,
): Directive<
  HTMLElement,
  CanDirectiveValue
> {
  return {
    mounted(element, binding) {
      applyVisibility(
        element,
        isAllowed(pinia, binding),
      )
    },

    updated(element, binding) {
      applyVisibility(
        element,
        isAllowed(pinia, binding),
      )
    },
  }
}
