/**
 * AppLayout Component
 * Main layout wrapper for authenticated pages
 * Combines Sidebar, Header, and MobileDrawer
 */

'use client'

import React, { useState } from 'react'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import { MobileDrawer } from './MobileDrawer'
import { OrvenaGuideWidget } from '@/components/guide/OrvenaGuideWidget'
import { cn } from '@/lib/utils'

interface AppLayoutProps {
  children: React.ReactNode
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false)

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed)
  }

  const toggleMobileDrawer = () => {
    setMobileDrawerOpen(!mobileDrawerOpen)
  }

  return (
    <div className="min-h-screen bg-ivory-50 dark:bg-midnight-950">
      {/* Desktop Sidebar */}
      <div className="hidden lg:block">
        <Sidebar 
          collapsed={sidebarCollapsed} 
          onToggleCollapse={toggleSidebar} 
        />
      </div>

      {/* Mobile Drawer */}
      <MobileDrawer 
        isOpen={mobileDrawerOpen} 
        onClose={() => setMobileDrawerOpen(false)} 
      />

      {/* Header */}
      <Header 
        onMenuClick={toggleMobileDrawer}
        sidebarCollapsed={sidebarCollapsed}
      />

      {/* Main Content */}
      <main
        className={cn(
          'pt-16 transition-all duration-300',
          // Desktop: respect sidebar
          'lg:pl-64',
          // Mobile: full width
          'pl-0'
        )}
      >
        <div className="min-h-[calc(100vh-4rem)]">
          {children}
        </div>
      </main>

      {/* Floating Orvena Guide Platform Assistant */}
      <OrvenaGuideWidget />
    </div>
  )
}

export default AppLayout
