/**
 * Header Component
 * Top navigation bar with user menu, search, and notifications
 */

'use client'

import React, { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import {
  Menu,
  Search,
  Bell,
  Settings,
  LogOut,
  Moon,
  Sun,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'

interface HeaderProps {
  onMenuClick?: () => void
  sidebarCollapsed?: boolean
}

export const Header: React.FC<HeaderProps> = ({ 
  onMenuClick, 
  sidebarCollapsed = false 
}) => {
  const { user, signOut } = useAuth()
  const router = useRouter()
  const [searchOpen, setSearchOpen] = useState(false)

  const handleSignOut = async () => {
    await signOut()
    router.push('/auth/login')
  }

  const getUserInitials = () => {
    if (!user?.email) return 'U'
    return user.email.charAt(0).toUpperCase()
  }

  return (
    <header
      className={cn(
        'fixed top-0 right-0 z-30 h-16 bg-ivory-50/80 dark:bg-midnight-950/80 backdrop-blur-md border-b border-midnight-200 dark:border-midnight-900 transition-all duration-300',
        sidebarCollapsed ? 'left-20' : 'left-64',
        'lg:left-64' // Desktop always respects sidebar
      )}
    >
      <div className="flex items-center justify-between h-full px-6">
        {/* Left section: Mobile menu + Search */}
        <div className="flex items-center gap-4 flex-1">
          {/* Mobile menu button */}
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg hover:bg-midnight-100 dark:hover:bg-midnight-900 transition-colors"
            aria-label="Open menu"
          >
            <Menu className="w-5 h-5 text-midnight-700 dark:text-ivory-200" />
          </button>

          {/* Search */}
          <div className="hidden md:flex items-center flex-1 max-w-md">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-midnight-500" />
              <Input
                type="search"
                placeholder="Search careers, skills, resources..."
                className="pl-10 h-10 bg-white dark:bg-midnight-900 border-midnight-200 focus:border-pathfinder-500"
              />
            </div>
          </div>

          {/* Mobile search button */}
          <button
            onClick={() => setSearchOpen(!searchOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-midnight-100 dark:hover:bg-midnight-900 transition-colors"
            aria-label="Search"
          >
            <Search className="w-5 h-5 text-midnight-700 dark:text-ivory-200" />
          </button>
        </div>

        {/* Right section: Actions + User menu */}
        <div className="flex items-center gap-3">
          {/* Notifications */}
          <button
            className="relative p-2 rounded-lg hover:bg-midnight-100 dark:hover:bg-midnight-900 transition-colors"
            aria-label="Notifications"
          >
            <Bell className="w-5 h-5 text-midnight-700 dark:text-ivory-200" />
            {/* Notification badge */}
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-pathfinder-500 rounded-full" />
          </button>

          {/* User menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="flex items-center gap-3 p-1.5 pl-3 pr-1.5 rounded-lg hover:bg-midnight-100 dark:hover:bg-midnight-900 transition-colors"
                aria-label="User menu"
              >
                <span className="hidden sm:block text-sm font-medium text-midnight-700 dark:text-ivory-200">
                  {user?.email?.split('@')[0] || 'User'}
                </span>
                <div className="w-8 h-8 rounded-full bg-pathfinder-500 flex items-center justify-center text-ivory-50 font-semibold text-sm">
                  {getUserInitials()}
                </div>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                <div className="flex flex-col">
                  <span className="font-semibold">My Account</span>
                  <span className="text-xs font-normal text-midnight-600 dark:text-midnight-400">
                    {user?.email}
                  </span>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => router.push('/settings')}>
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleSignOut} className="text-error-600">
                <LogOut className="w-4 h-4 mr-2" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Mobile search overlay */}
      {searchOpen && (
        <div className="md:hidden absolute top-full left-0 right-0 p-4 bg-ivory-50 dark:bg-midnight-950 border-b border-midnight-200 dark:border-midnight-900">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-midnight-500" />
            <Input
              type="search"
              placeholder="Search careers, skills, resources..."
              className="pl-10 h-10 bg-white dark:bg-midnight-900 border-midnight-200"
              autoFocus
            />
          </div>
        </div>
      )}
    </header>
  )
}

export default Header
