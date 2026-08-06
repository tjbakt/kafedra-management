import { useConfirm } from 'primevue/useconfirm'
import { useI18n } from 'vue-i18n'

interface ConfirmDeleteOptions {
  message?: string
  header?: string
  accept?: () => void | Promise<void>
  reject?: () => void
}

export function useAppConfirm() {
  const confirm = useConfirm()
  const { t } = useI18n()

  function confirmDelete(
    options: ConfirmDeleteOptions = {},
  ): void {
    confirm.require({
      header:
        options.header ??
        t('confirm.deleteHeader'),

      message:
        options.message ??
        t('confirm.deleteMessage'),

      icon: 'pi pi-exclamation-triangle',

      rejectLabel: t('common.cancel'),
      acceptLabel: t('confirm.deleteAccept'),

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

  function confirmAction(
    message: string,
    accept: () => void | Promise<void>,
  ): void {
    confirm.require({
      header: t('confirm.actionHeader'),
      message,
      icon: 'pi pi-question-circle',
      rejectLabel: t('common.cancel'),
      acceptLabel: t('common.confirm'),

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
