export type NotificationVariant = 'success' | 'error' | 'info'

export function showNotification(message: string, variant: NotificationVariant = 'info') {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new CustomEvent('orvena:notification', {
    detail: { message, variant },
  }))
}
