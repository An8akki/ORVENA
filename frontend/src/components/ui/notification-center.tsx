'use client'

import { useEffect, useState } from 'react'
import { CheckCircle2, X, XCircle, Info } from 'lucide-react'
import type { NotificationVariant } from '@/lib/notifications'

interface Notification {
  id: number
  message: string
  variant: NotificationVariant
}

export function NotificationCenter() {
  const [notifications, setNotifications] = useState<Notification[]>([])

  useEffect(() => {
    const handleNotification = (event: Event) => {
      const detail = (event as CustomEvent<{ message: string; variant: NotificationVariant }>).detail
      const id = Date.now() + Math.random()
      setNotifications((current) => [...current, { id, ...detail }])
      window.setTimeout(() => {
        setNotifications((current) => current.filter((item) => item.id !== id))
      }, 5000)
    }
    window.addEventListener('orvena:notification', handleNotification)
    return () => window.removeEventListener('orvena:notification', handleNotification)
  }, [])

  return (
    <div className="fixed right-4 top-4 z-[100] flex w-[min(28rem,calc(100vw-2rem))] flex-col gap-3">
      {notifications.map(({ id, message, variant }) => {
        const Icon = variant === 'success' ? CheckCircle2 : variant === 'error' ? XCircle : Info
        return (
          <div key={id} role="status" className="flex items-start gap-3 rounded-lg border bg-background p-4 shadow-lg">
            <Icon className={`mt-0.5 h-5 w-5 shrink-0 ${variant === 'error' ? 'text-destructive' : variant === 'success' ? 'text-green-600' : 'text-blue-600'}`} />
            <p className="flex-1 text-sm">{message}</p>
            <button type="button" onClick={() => setNotifications((current) => current.filter((item) => item.id !== id))} aria-label="Dismiss notification">
              <X className="h-4 w-4 text-muted-foreground" />
            </button>
          </div>
        )
      })}
    </div>
  )
}
