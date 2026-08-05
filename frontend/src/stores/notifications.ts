import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import type { AppNotification } from '@/types/notification'

export const useNotificationsStore = defineStore('notifications', () => {
  const notifications = ref<AppNotification[]>([
    {
      id: 1,
      title: 'Система готова',
      message: 'Frontend-каркас успешно подключён.',
      createdAt: 'Только что',
      severity: 'success',
      read: false,
      route: '/',
    },
    {
      id: 2,
      title: 'Учебная нагрузка',
      message: 'Необходимо проверить распределение часов.',
      createdAt: '15 минут назад',
      severity: 'warn',
      read: false,
      route: '/workload',
    },
    {
      id: 3,
      title: 'Обновление справочника',
      message: 'Данные кафедр были обновлены.',
      createdAt: '1 час назад',
      severity: 'info',
      read: true,
      route: '/departments',
    },
  ])

  const unreadCount = computed(
    () => notifications.value.filter((notification) => !notification.read).length,
  )

  function markAsRead(id: number): void {
    const notification = notifications.value.find((item) => item.id === id)

    if (notification) {
      notification.read = true
    }
  }

  function markAllAsRead(): void {
    notifications.value.forEach((notification) => {
      notification.read = true
    })
  }

  function removeNotification(id: number): void {
    notifications.value = notifications.value.filter((item) => item.id !== id)
  }

  function clearAll(): void {
    notifications.value = []
  }

  return {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAll,
  }
})
