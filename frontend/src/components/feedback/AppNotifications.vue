<script setup lang="ts">
import Popover from 'primevue/popover'
import Button from 'primevue/button'
import Badge from 'primevue/badge'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useNotificationsStore } from '@/stores/notifications'
import type { AppNotification } from '@/types/notification'

const router = useRouter()
const notificationsStore = useNotificationsStore()
const popover = ref<InstanceType<typeof Popover> | null>(null)

function toggle(event: Event): void {
  popover.value?.toggle(event)
}

async function openNotification(notification: AppNotification): Promise<void> {
  notificationsStore.markAsRead(notification.id)
  popover.value?.hide()

  if (notification.route) {
    await router.push(notification.route)
  }
}

function getSeverityIcon(severity: AppNotification['severity']): string {
  const icons = {
    success: 'pi pi-check-circle',
    info: 'pi pi-info-circle',
    warn: 'pi pi-exclamation-triangle',
    error: 'pi pi-times-circle',
  }

  return icons[severity]
}
</script>

<template>
  <div class="notifications">
    <Button
      v-tooltip.bottom="'Уведомления'"
      aria-label="Открыть уведомления"
      icon="pi pi-bell"
      severity="secondary"
      text
      rounded
      @click="toggle"
    />

    <Badge
      v-if="notificationsStore.unreadCount > 0"
      class="notifications__badge"
      :value="notificationsStore.unreadCount > 99 ? '99+' : notificationsStore.unreadCount"
      severity="danger"
    />

    <Popover ref="popover" class="notifications-popover">
      <div class="notifications-panel">
        <div class="notifications-panel__header">
          <div>
            <h3>Уведомления</h3>
            <span>{{ notificationsStore.unreadCount }} непрочитанных</span>
          </div>

          <Button
            v-if="notificationsStore.unreadCount"
            label="Прочитать все"
            severity="secondary"
            size="small"
            text
            @click="notificationsStore.markAllAsRead"
          />
        </div>

        <div v-if="notificationsStore.notifications.length" class="notifications-panel__list">
          <button
            v-for="notification in notificationsStore.notifications"
            :key="notification.id"
            type="button"
            class="notification-item"
            :class="{ 'notification-item--unread': !notification.read }"
            @click="openNotification(notification)"
          >
            <span
              class="notification-item__icon"
              :class="`notification-item__icon--${notification.severity}`"
            >
              <i :class="getSeverityIcon(notification.severity)" />
            </span>

            <span class="notification-item__body">
              <strong>{{ notification.title }}</strong>
              <span>{{ notification.message }}</span>
              <small>{{ notification.createdAt }}</small>
            </span>

            <span
              v-if="!notification.read"
              class="notification-item__indicator"
              aria-label="Непрочитанное уведомление"
            />
          </button>
        </div>

        <div v-else class="notifications-panel__empty">
          <i class="pi pi-bell-slash" />
          <p>Уведомлений пока нет</p>
        </div>

        <div v-if="notificationsStore.notifications.length" class="notifications-panel__footer">
          <Button
            label="Очистить"
            icon="pi pi-trash"
            severity="secondary"
            size="small"
            text
            @click="notificationsStore.clearAll"
          />
        </div>
      </div>
    </Popover>
  </div>
</template>

<style scoped>
.notifications {
  position: relative;
  display: inline-flex;
}

.notifications__badge {
  position: absolute;
  top: -0.15rem;
  right: -0.2rem;
  pointer-events: none;
}

.notifications-panel {
  width: min(24rem, calc(100vw - 2rem));
}

.notifications-panel__header,
.notifications-panel__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.notifications-panel__header {
  padding: 0.25rem 0.25rem 0.75rem;
  border-bottom: 1px solid var(--app-border-color);
}

.notifications-panel__header h3 {
  margin: 0;
  font-size: 1rem;
}

.notifications-panel__header span {
  color: var(--app-text-muted);
  font-size: 0.78rem;
}

.notifications-panel__list {
  max-height: 24rem;
  overflow-y: auto;
}

.notification-item {
  position: relative;
  display: flex;
  width: 100%;
  gap: 0.75rem;
  padding: 0.9rem 0.5rem;
  border: 0;
  border-bottom: 1px solid var(--app-border-color);
  background: transparent;
  color: inherit;
  text-align: left;
  cursor: pointer;
}

.notification-item:hover {
  background: var(--app-hover-bg);
}

.notification-item--unread {
  background: color-mix(in srgb, var(--app-primary) 7%, transparent);
}

.notification-item__icon {
  display: grid;
  flex: 0 0 2.25rem;
  width: 2.25rem;
  height: 2.25rem;
  place-items: center;
  border-radius: 50%;
}

.notification-item__icon--success {
  color: var(--app-success);
  background: color-mix(in srgb, var(--app-success) 12%, transparent);
}

.notification-item__icon--info {
  color: var(--app-info);
  background: color-mix(in srgb, var(--app-info) 12%, transparent);
}

.notification-item__icon--warn {
  color: var(--app-warning);
  background: color-mix(in srgb, var(--app-warning) 12%, transparent);
}

.notification-item__icon--error {
  color: var(--app-danger);
  background: color-mix(in srgb, var(--app-danger) 12%, transparent);
}

.notification-item__body {
  display: grid;
  min-width: 0;
  gap: 0.2rem;
}

.notification-item__body strong {
  font-size: 0.88rem;
}

.notification-item__body span {
  color: var(--app-text-muted);
  font-size: 0.8rem;
  line-height: 1.4;
}

.notification-item__body small {
  color: var(--app-text-soft);
  font-size: 0.72rem;
}

.notification-item__indicator {
  position: absolute;
  top: 1rem;
  right: 0.4rem;
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 50%;
  background: var(--app-primary);
}

.notifications-panel__footer {
  justify-content: flex-end;
  padding-top: 0.5rem;
}

.notifications-panel__empty {
  display: grid;
  min-height: 11rem;
  place-content: center;
  justify-items: center;
  color: var(--app-text-muted);
}

.notifications-panel__empty i {
  font-size: 2rem;
}

.notifications-panel__empty p {
  margin-bottom: 0;
}
</style>
