/**
 * MobileDrawer Component
 * Slide-out navigation drawer for mobile devices
 */

'use client'

import React, { useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import {
  Compass,
  LayoutDashboard,
  Target,
  FileText,
  Map,
  TrendingUp,
  Settings,
  HelpCircle,
  X,
} from 'lucide-react'

interface NavItem {
  label: string
  href: string
  icon: React.ElementType
  badge?: string
  disabled?: boolean
}

interface MobileDrawerProps {
  isOpen: boolean
  onClose: () => void
}

const mainNavItems: NavItem[] = [
  {
    label: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    label: 'Career Discovery',
    href: '/career/discovery',
    icon: Target,
  },
  {
    label: 'Resume Studio',
    href: '/resume',
    icon: FileText,
  },
  {
    label: 'Roadmap',
    href: '/roadmap',
    icon: Map,
  },
  {
    label: 'Progress',
    href: '/progress',
    icon: TrendingUp,
  },
]

const secondaryNavItems: NavItem[] = [
  {
    label: 'Settings',
    href: '/settings',
    icon: Settings,
  },
  {
    label: 'Help & Support',
    href: '/help',
    icon: HelpCircle,
  },
]

export const MobileDrawer: React.FC<MobileDrawerProps> = ({ isOpen, onClose }) => {
  const pathname = usePathname()

  // Close drawer on route change
  useEffect(() => {
    onClose()
  }, [pathname, onClose])

  // Lock body scroll when drawer is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [isOpen])

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
    }
    return () => {
      document.removeEventListener('keydown', handleEscape)
    }
  }, [isOpen, onClose])

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard'
    }
    return pathname.startsWith(href)
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className={cn(
          'fixed inset-0 bg-midnight-950/80 backdrop-blur-sm z-50 lg:hidden transition-opacity duration-300',
          isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        )}
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer */}
      <aside
        className={cn(
          'fixed left-0 top-0 z-50 h-screen w-80 bg-midnight-950 text-ivory-50 transition-transform duration-300 lg:hidden',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
        aria-label="Mobile navigation"
      >
        {/* Header */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-midnight-900">
          <Link href="/dashboard" className="flex items-center gap-3" onClick={onClose}>
            <div className="w-10 h-10 rounded-lg bg-pathfinder-500 flex items-center justify-center pathfinder-glow">
              <Compass className="w-6 h-6 text-ivory-50" strokeWidth={2.5} />
            </div>
            <span className="font-display text-xl font-bold">ORVENA</span>
          </Link>
          
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-midnight-900 transition-colors"
            aria-label="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex flex-col h-[calc(100vh-4rem)] overflow-y-auto">
          {/* Main navigation */}
          <div className="flex-1 px-3 py-6">
            <div className="space-y-1">
              {mainNavItems.map((item) => {
                const Icon = item.icon
                const active = isActive(item.href)

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200',
                      active
                        ? 'bg-pathfinder-500 text-ivory-50 shadow-md'
                        : 'text-ivory-200 hover:bg-midnight-900 hover:text-ivory-50',
                      item.disabled && 'opacity-50 cursor-not-allowed'
                    )}
                    onClick={(e) => item.disabled && e.preventDefault()}
                  >
                    <Icon 
                      className={cn(
                        'w-5 h-5 flex-shrink-0',
                        active && 'text-ivory-50'
                      )} 
                      strokeWidth={2}
                    />
                    <span className="flex-1">{item.label}</span>
                    {item.badge && (
                      <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-pathfinder-400 text-midnight-950">
                        {item.badge}
                      </span>
                    )}
                  </Link>
                )
              })}
            </div>
          </div>

          {/* Secondary navigation */}
          <div className="px-3 py-4 border-t border-midnight-900">
            <div className="space-y-1">
              {secondaryNavItems.map((item) => {
                const Icon = item.icon
                const active = isActive(item.href)

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200',
                      active
                        ? 'bg-midnight-900 text-ivory-50'
                        : 'text-ivory-300 hover:bg-midnight-900 hover:text-ivory-50'
                    )}
                  >
                    <Icon className="w-5 h-5 flex-shrink-0" strokeWidth={2} />
                    <span className="flex-1">{item.label}</span>
                  </Link>
                )
              })}
            </div>
          </div>
        </nav>
      </aside>
    </>
  )
}

export default MobileDrawer
