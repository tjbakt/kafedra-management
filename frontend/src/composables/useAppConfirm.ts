import { useConfirm } from 'primevue/useconfirm'

interface ConfirmDeleteOptions {
  message?: string
  header?: string
  accept?: () => void | Promise<void>
  reject?: () => void
}

export function useAppConfirm() {
  const confirm = useConfirm()

  function confirmDelete(options: ConfirmDeleteOptions = {}): void {
    confirm.require({
      header: options.header ?? 'Подтверждение удаления',
      message:
        options.message ??
        'Вы действительно хотите удалить выбранную запись? Это действие нельзя отменить.',
      icon: 'pi pi-exclamation-triangle',
      rejectLabel: 'Отмена',
      acceptLabel: 'Удалить',
      rejectProps: {
        severity: 'secondary',
        outlined: true,
      },
      acceptProps: {
        severity: 'danger',
      },
      accept: options.accept,
      reject: options.reject,
    })
  }

  function confirmAction(message: string, accept: () => void | Promise<void>): void {
    confirm.require({
      header: 'Подтверждение действия',
      message,
      icon: 'pi pi-question-circle',
      rejectLabel: 'Отмена',
      acceptLabel: 'Подтвердить',
      rejectProps: {
        severity: 'secondary',
        outlined: true,
      },
      accept,
    })
  }

  return {
    confirmDelete,
    confirmAction,
  }
}
