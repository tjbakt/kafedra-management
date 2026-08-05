import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

const MOBILE_BREAKPOINT = 992

export const useLayoutStore = defineStore('layout', () => {
  const sidebarCollapsed = ref(false)
  const mobileSidebarVisible = ref(false)
  const darkMode = ref(localStorage.getItem('theme') === 'dark')

  const isDesktop = computed(() => window.innerWidth >= MOBILE_BREAKPOINT)

  function applyTheme(): void {
    document.documentElement.classList.toggle('app-dark', darkMode.value)
    document.documentElement.style.colorScheme = darkMode.value ? 'dark' : 'light'
  }

  function initializeTheme(): void {
    const savedTheme = localStorage.getItem('theme')

    if (savedTheme === 'dark' || savedTheme === 'light') {
      darkMode.value = savedTheme === 'dark'
    } else {
      darkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }

    applyTheme()
  }

  function toggleTheme(): void {
    darkMode.value = !darkMode.value
    localStorage.setItem('theme', darkMode.value ? 'dark' : 'light')
    applyTheme()
  }

  function toggleSidebar(): void {
    if (window.innerWidth < MOBILE_BREAKPOINT) {
      mobileSidebarVisible.value = !mobileSidebarVisible.value
      return
    }

    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function closeMobileSidebar(): void {
    mobileSidebarVisible.value = false
  }

  function handleResize(): void {
    if (window.innerWidth >= MOBILE_BREAKPOINT) {
      mobileSidebarVisible.value = false
    }
  }

  return {
    sidebarCollapsed,
    mobileSidebarVisible,
    darkMode,
    isDesktop,
    initializeTheme,
    toggleTheme,
    toggleSidebar,
    closeMobileSidebar,
    handleResize,
  }
})
