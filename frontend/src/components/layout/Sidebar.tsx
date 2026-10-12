/**
 * Sidebar Navigation Component
 * Premium left-side navigation for authenticated ORVENA experience
 */

'use client'

import React from 'react'
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
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'

interface NavItem {
  label: string
  href: string
  icon: React.ElementType
  badge?: string
  disabled?: boolean
}

interface SidebarProps {
  collapsed?: boolean
  onToggleCollapse?: () => void
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
    label: 'Resume Analyzer',
    href: '/resume',
    icon: FileText,
  },
  {
    label: 'Job Recommender',
    href: '/jobs',
    icon: Compass,
  },
  {
    label: 'Career Roadmap',
    href: '/roadmap',
    icon: Map,
  },
  {
    label: 'Progress Tracking',
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

export const Sidebar: React.FC<SidebarProps> = ({ 
  collapsed = false, 
  onToggleCollapse 
}) => {
  const pathname = usePathname()

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard'
    }
    return pathname.startsWith(href)
  }

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-40 h-screen bg-midnight-950 text-ivory-50 transition-all duration-300 border-r border-midnight-900',
        collapsed ? 'w-20' : 'w-64'
      )}
    >
      {/* Logo Section */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-midnight-900">
        <Link 
          href="/dashboard" 
          className={cn(
            'flex items-center gap-3 transition-opacity',
            collapsed && 'opacity-0 pointer-events-none'
          )}
        >
          <div className="w-10 h-10 rounded-lg bg-pathfinder-500 flex items-center justify-center pathfinder-glow flex-shrink-0">
            <Compass className="w-6 h-6 text-ivory-50" strokeWidth={2.5} />
          </div>
          <span className="font-display text-xl font-bold">ORVENA</span>
        </Link>
        
        {/* Collapsed logo */}
        {collapsed && (
          <Link href="/dashboard" className="flex items-center justify-center w-full">
            <div className="w-10 h-10 rounded-lg bg-pathfinder-500 flex items-center justify-center pathfinder-glow">
              <Compass className="w-6 h-6 text-ivory-50" strokeWidth={2.5} />
            </div>
          </Link>
        )}
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
                    'flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium transition-all duration-200 group relative',
                    active
                      ? 'bg-pathfinder-500 text-ivory-50 shadow-md'
                      : 'text-ivory-200 hover:bg-midnight-900 hover:text-ivory-50',
                    collapsed && 'justify-center px-0',
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
                  
                  {!collapsed && (
                    <>
                      <span className="flex-1">{item.label}</span>
                      {item.badge && (
                        <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-pathfinder-400 text-midnight-950">
                          {item.badge}
                        </span>
                      )}
                    </>
                  )}

                  {/* Tooltip for collapsed state */}
                  {collapsed && (
                    <div className="absolute left-full ml-4 px-3 py-2 bg-midnight-800 text-ivory-50 text-sm rounded-md whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 shadow-lg">
                      {item.label}
                      <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-midnight-800" />
                    </div>
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
                    'flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium transition-all duration-200 group relative',
                    active
                      ? 'bg-midnight-900 text-ivory-50'
                      : 'text-ivory-300 hover:bg-midnight-900 hover:text-ivory-50',
                    collapsed && 'justify-center px-0'
                  )}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" strokeWidth={2} />
                  
                  {!collapsed && <span className="flex-1">{item.label}</span>}

                  {/* Tooltip for collapsed state */}
                  {collapsed && (
                    <div className="absolute left-full ml-4 px-3 py-2 bg-midnight-800 text-ivory-50 text-sm rounded-md whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 shadow-lg">
                      {item.label}
                      <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-midnight-800" />
                    </div>
                  )}
                </Link>
              )
            })}
          </div>
        </div>

        {/* Collapse toggle (desktop only) */}
        {onToggleCollapse && (
          <div className="hidden lg:block px-3 py-4 border-t border-midnight-900">
            <button
              onClick={onToggleCollapse}
              className={cn(
                'flex items-center gap-3 px-3 py-2 w-full rounded-lg text-sm font-medium text-ivory-300 hover:bg-midnight-900 hover:text-ivory-50 transition-all duration-200',
                collapsed && 'justify-center px-0'
              )}
            >
              {collapsed ? (
                <ChevronRight className="w-5 h-5" strokeWidth={2} />
              ) : (
                <>
                  <ChevronLeft className="w-5 h-5" strokeWidth={2} />
                  <span>Collapse</span>
                </>
              )}
            </button>
          </div>
        )}
      </nav>
    </aside>
  )
}

export default Sidebar
