<script setup lang="ts">
import Button from 'primevue/button'
import Menu from 'primevue/menu'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { useAppToast } from '@/composables/useAppToast'
import { useLocaleStore } from '@/stores/locale'
import type { AppLocale } from '@/types/locale'

const { t } = useI18n()
const localeStore = useLocaleStore()
const toast = useAppToast()

const menu =
  ref<InstanceType<typeof Menu> | null>(null)

const menuItems = computed(() =>
  localeStore.localeOptions.map((option) => ({
    label: option.label,
    icon:
      option.code === localeStore.locale
        ? 'pi pi-check'
        : 'pi pi-language',
    command: () => changeLocale(option.code),
  })),
)

function toggle(event: Event): void {
  menu.value?.toggle(event)
}

async function changeLocale(
  locale: AppLocale,
): Promise<void> {
  if (locale === localeStore.locale) {
    return
  }

  try {
    await localeStore.changeLocale(locale)

    toast.success(
      t('languages.changed'),
      t('languages.saved'),
    )
  } catch {
    toast.warning(
      t('languages.changed'),
      t('languages.saveError'),
    )
  }
}
</script>

<template>
  <div class="language-switcher">
    <Button
      v-tooltip.bottom="t('languages.select')"
      severity="secondary"
      text
      rounded
      aria-haspopup="true"
      aria-controls="language-menu"
      @click="toggle"
    >
      <span class="language-switcher__button">
        <span>
          {{
            localeStore.currentLocaleOption.flag
          }}
        </span>

        <strong>
          {{
            localeStore.currentLocaleOption
              .shortLabel
          }}
        </strong>
      </span>
    </Button>

    <Menu
      id="language-menu"
      ref="menu"
      :model="menuItems"
      popup
    />
  </div>
</template>

<style scoped>
.language-switcher {
  display: inline-flex;
}

.language-switcher__button {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.language-switcher__button strong {
  font-size: 0.72rem;
  letter-spacing: 0.04em;
}
</style>
