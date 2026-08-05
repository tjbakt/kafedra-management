import { useToast } from 'primevue/usetoast'

const DEFAULT_LIFE = 4000

export function useAppToast() {
  const toast = useToast()

  function success(summary: string, detail = '', life = DEFAULT_LIFE): void {
    toast.add({
      severity: 'success',
      summary,
      detail,
      life,
    })
  }

  function info(summary: string, detail = '', life = DEFAULT_LIFE): void {
    toast.add({
      severity: 'info',
      summary,
      detail,
      life,
    })
  }

  function warning(summary: string, detail = '', life = DEFAULT_LIFE): void {
    toast.add({
      severity: 'warn',
      summary,
      detail,
      life,
    })
  }

  function error(summary: string, detail = '', life = 6000): void {
    toast.add({
      severity: 'error',
      summary,
      detail,
      life,
    })
  }

  return {
    success,
    info,
    warning,
    error,
  }
}
