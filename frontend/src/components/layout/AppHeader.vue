<script setup lang="ts">
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'
import Menu from 'primevue/menu'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import AppLanguageSwitcher from '@/components/layout/AppLanguageSwitcher.vue'
import AppNotifications from '@/components/feedback/AppNotifications.vue'
import { useLayoutStore } from '@/stores/layout'
import { useAppToast } from '@/composables/useAppToast'

const router = useRouter()
const layoutStore = useLayoutStore()
const toast = useAppToast()
const { t } = useI18n()

const profileMenu = ref<InstanceType<typeof Menu> | null>(null)

const profileItems = computed(() => [
  {
    label: t('profile.profile'),
    icon: 'pi pi-user',
    command: () =>
      toast.info(
        t('profile.profile'),
        t('modules.preparedDescription'),
      ),
  },
  {
    label: t('profile.settings'),
    icon: 'pi pi-cog',
    command: () => router.push('/settings'),
  },
  {
    separator: true,
  },
  {
    label: t('profile.logout'),
    icon: 'pi pi-sign-out',
    command: () => router.push('/login'),
  },
])

function toggleProfileMenu(event: Event): void {
  profileMenu.value?.toggle(event)
}
</script>

<template>
  <header class="app-header">
    <div class="app-header__left">
      <Button
        v-tooltip.bottom="t('common.openMenu')"
        icon="pi pi-bars"
        severity="secondary"
        text
        rounded
        :aria-label="t('common.openMenu')"
        @click="layoutStore.toggleSidebar"
      />

      <div class="app-header__title">
        <strong>{{ t('app.title') }}</strong>
        <span>{{ t('app.subtitle') }}</span>
      </div>
    </div>

    <div class="app-header__right">
      <AppLanguageSwitcher />

      <Button
        v-tooltip.bottom="
          layoutStore.darkMode
            ? t('common.lightTheme')
            : t('common.darkTheme')
        "
        :icon="
          layoutStore.darkMode
            ? 'pi pi-sun'
            : 'pi pi-moon'
        "
        severity="secondary"
        text
        rounded
        :aria-label="
          layoutStore.darkMode
            ? t('common.lightTheme')
            : t('common.darkTheme')
        "
        @click="layoutStore.toggleTheme"
      />

      <AppNotifications />

      <button
        type="button"
        class="profile-button"
        :aria-label="t('profile.profile')"
        @click="toggleProfileMenu"
      >
        <Avatar label="АД" shape="circle" />

        <span class="profile-button__info">
          <strong>{{ t('profile.administrator') }}</strong>
          <small>
            {{ t('profile.systemAdministrator') }}
          </small>
        </span>

        <i class="pi pi-chevron-down" />
      </button>

      <Menu
        ref="profileMenu"
        :model="profileItems"
        popup
      />
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: fixed;
  z-index: var(--app-z-header);
  top: 0;
  right: 0;
  left: var(--app-sidebar-width);
  display: flex;
  height: var(--app-header-height);
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0 1.5rem;
  border-bottom: 1px solid var(--app-border-color);
  background: color-mix(
    in srgb,
    var(--app-surface) 92%,
    transparent
  );
  backdrop-filter: blur(16px);
  transition: left var(--app-transition);
}

.app-header__left,
.app-header__right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.app-header__title {
  display: grid;
  gap: 0.15rem;
}

.app-header__title strong {
  font-size: 0.94rem;
}

.app-header__title span {
  color: var(--app-text-muted);
  font-size: 0.73rem;
}

.profile-button {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.3rem 0.5rem;
  border: 0;
  border-radius: var(--app-radius);
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.profile-button:hover {
  background: var(--app-hover-bg);
}

.profile-button__info {
  display: grid;
  min-width: 9rem;
  gap: 0.1rem;
  text-align: left;
}

.profile-button__info strong {
  font-size: 0.82rem;
}

.profile-button__info small {
  color: var(--app-text-muted);
  font-size: 0.7rem;
}

:global(.layout-collapsed) .app-header {
  left: var(--app-sidebar-collapsed-width);
}

@media (max-width: 991px) {
  .app-header {
    left: 0;
    padding: 0 1rem;
  }

  .profile-button__info,
  .profile-button > i {
    display: none;
  }
}

@media (max-width: 575px) {
  .app-header {
    gap: 0.4rem;
  }

  .app-header__title {
    display: none;
  }

  .app-header__right {
    gap: 0.15rem;
  }
}
</style>
