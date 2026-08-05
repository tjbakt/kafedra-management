export type NotificationSeverity = 'info' | 'success' | 'warn' | 'error'

export interface AppNotification {
  id: number
  title: string
  message: string
  createdAt: string
  severity: NotificationSeverity
  read: boolean
  route?: string
}
