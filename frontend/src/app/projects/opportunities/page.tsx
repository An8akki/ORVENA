'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import {
  Award,
  ArrowLeft,
  Filter,
  ExternalLink,
  Calendar,
  Globe,
  DollarSign,
  Bookmark,
  BookmarkCheck,
  CheckCircle2,
  Clock,
  Search,
  Sparkles,
} from 'lucide-react'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { api } from '@/lib/api-client'
import { cn } from '@/lib/utils'

interface Opportunity {
  id: string
  title: string
  provider: string
  opportunity_type: string
  description: string
  official_url: string
  eligibility_requirements?: string[]
  beneficiary_type: string
  geographic_scope: string
  domains?: string[]
  required_project_stage: string
  funding_amount_or_benefits?: string
  is_monetary: boolean
  application_deadline?: string
  is_rolling: boolean
  application_instructions?: string
  date_last_verified: string
  status: string
  is_verified: boolean
  source_notes?: string
}

interface SavedApp {
  id: string
  opportunity_id: string
  status: string
  notes?: string
  opportunity: Opportunity
}

function OpportunitiesContent() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [savedApps, setSavedApps] = useState<SavedApp[]>([])
  const [loading, setLoading] = useState(true)
  const [activeView, setActiveView] = useState<'directory' | 'saved'>('directory')

  // Filters
  const [typeFilter, setTypeFilter] = useState('all')
  const [domainFilter, setDomainFilter] = useState('all')
  const [stageFilter, setStageFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadData()
  }, [typeFilter, domainFilter, stageFilter])

  const loadData = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (typeFilter !== 'all') params.append('type', typeFilter)
      if (domainFilter !== 'all') params.append('domain', domainFilter)
      if (stageFilter !== 'all') params.append('stage', stageFilter)

      const [opps, saved] = await Promise.all([
        api.get<Opportunity[]>(`/api/v1/launchpad/opportunities?${params.toString()}`),
        api.get<SavedApp[]>('/api/v1/launchpad/opportunities/saved').catch(() => []),
      ])

      setOpportunities(opps || [])
      setSavedApps(saved || [])
    } catch {
      setOpportunities([])
    } finally {
      setLoading(false)
    }
  }

  const isSaved = (oppId: string) => savedApps.some((s) => s.opportunity_id === oppId)

  const handleToggleBookmark = async (oppId: string) => {
    const existing = savedApps.find((s) => s.opportunity_id === oppId)
    if (existing) {
      try {
        await api.delete(`/api/v1/launchpad/opportunities/${oppId}/bookmark`)
        setSavedApps((prev) => prev.filter((s) => s.opportunity_id !== oppId))
      } catch (err: any) {
        alert(err.message || 'Failed to remove bookmark')
      }
    } else {
      try {
        const created = await api.post<SavedApp>(
          `/api/v1/launchpad/opportunities/${oppId}/bookmark`,
          { status: 'saved' }
        )
        setSavedApps((prev) => [...prev, created])
      } catch (err: any) {
        alert(err.message || 'Failed to save opportunity')
      }
    }
  }

  const handleUpdateAppStatus = async (oppId: string, nextStatus: string) => {
    try {
      await api.post(`/api/v1/launchpad/opportunities/${oppId}/bookmark`, {
        status: nextStatus,
      })
      setSavedApps((prev) =>
        prev.map((s) => (s.opportunity_id === oppId ? { ...s, status: nextStatus } : s))
      )
    } catch (err: any) {
      alert(err.message || 'Failed to update status')
    }
  }

  const filteredOpportunities = opportunities.filter((o) => {
    if (!searchQuery.trim()) return true
    const q = searchQuery.toLowerCase()
    return (
      o.title.toLowerCase().includes(q) ||
      o.provider.toLowerCase().includes(q) ||
      o.description.toLowerCase().includes(q)
    )
  })

  return (
    <AppLayout>
      <div className="container py-8 max-w-7xl mx-auto px-4">
        {/* Navigation Breadcrumb */}
        <div className="mb-4 flex items-center gap-2 text-xs text-midnight-500">
          <Link href="/projects" className="hover:text-midnight-800 dark:hover:text-midnight-200 flex items-center gap-1">
            <ArrowLeft className="h-3.5 w-3.5" />
            Launchpad Hub
          </Link>
          <span>/</span>
          <span className="text-midnight-900 dark:text-ivory-50 font-medium">Opportunities Directory</span>
        </div>

        {/* Title Hero */}
        <div className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-700 dark:text-emerald-400 mb-2">
              <Award className="h-3.5 w-3.5" />
              Verified External Programs
            </div>
            <h1 className="font-display text-display-md text-midnight-950 dark:text-ivory-50 tracking-tight">
              Opportunities & Funding Directory
            </h1>
            <p className="text-sm text-midnight-600 dark:text-midnight-300 max-w-2xl mt-1">
              Source-backed student competitions, hackathons, open source fellowships (GSoC), and innovation grants.
              Zero fabricated deadlines or mock awards.
            </p>
          </div>

          <div className="flex items-center rounded-xl border border-midnight-200 dark:border-midnight-800 bg-midnight-50 dark:bg-midnight-950 p-1">
            <button
              type="button"
              onClick={() => setActiveView('directory')}
              className={cn(
                'rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors',
                activeView === 'directory'
                  ? 'bg-white dark:bg-midnight-900 text-midnight-950 dark:text-ivory-50 shadow-sm'
                  : 'text-midnight-500 hover:text-midnight-900 dark:hover:text-ivory-50'
              )}
            >
              All Opportunities ({opportunities.length})
            </button>
            <button
              type="button"
              onClick={() => setActiveView('saved')}
              className={cn(
                'rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors',
                activeView === 'saved'
                  ? 'bg-white dark:bg-midnight-900 text-midnight-950 dark:text-ivory-50 shadow-sm'
                  : 'text-midnight-500 hover:text-midnight-900 dark:hover:text-ivory-50'
              )}
            >
              Tracked Applications ({savedApps.length})
            </button>
          </div>
        </div>

        {/* Filter & Search Bar */}
        <div className="mb-8 rounded-2xl border border-midnight-200 dark:border-midnight-800 bg-white dark:bg-midnight-900/60 p-4 shadow-sm">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-midnight-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by title or provider..."
                className="w-full rounded-lg border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 pl-8 pr-3 py-1.5 text-xs text-midnight-950 dark:text-ivory-50 focus:outline-none"
              />
            </div>

            {/* Type */}
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="rounded-lg border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3 py-1.5 text-xs text-midnight-950 dark:text-ivory-50 focus:outline-none"
            >
              <option value="all">All Categories</option>
              <option value="competition">Competitions</option>
              <option value="hackathon">Hackathons</option>
              <option value="research_fellowship">Research Fellowships</option>
              <option value="grant">Maker & Student Grants</option>
              <option value="incubator">Incubators & Accelerators</option>
            </select>

            {/* Domain */}
            <select
              value={domainFilter}
              onChange={(e) => setDomainFilter(e.target.value)}
              className="rounded-lg border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3 py-1.5 text-xs text-midnight-950 dark:text-ivory-50 focus:outline-none"
            >
              <option value="all">All Domains</option>
              <option value="AI / Machine Learning">AI & Machine Learning</option>
              <option value="Full Stack Web">Full Stack Web</option>
              <option value="Cloud & DevOps">Cloud & Systems</option>
              <option value="ClimateTech & IoT">ClimateTech & IoT</option>
              <option value="DeepTech">DeepTech</option>
            </select>

            {/* Required Stage */}
            <select
              value={stageFilter}
              onChange={(e) => setStageFilter(e.target.value)}
              className="rounded-lg border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3 py-1.5 text-xs text-midnight-950 dark:text-ivory-50 focus:outline-none"
            >
              <option value="all">Any Stage Accepted</option>
              <option value="idea">Idea Stage</option>
              <option value="prototype">Working Prototype</option>
            </select>
          </div>
        </div>

        {/* Directory View */}
        {activeView === 'directory' ? (
          loading ? (
            <div className="grid gap-5 md:grid-cols-2">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-64 rounded-2xl border border-midnight-200 dark:border-midnight-800 bg-midnight-900/10 animate-pulse" />
              ))}
            </div>
          ) : filteredOpportunities.length === 0 ? (
            <Card className="p-8 text-center border-dashed">
              <p className="text-xs text-midnight-500">No opportunities match the selected criteria.</p>
            </Card>
          ) : (
            <div className="grid gap-5 md:grid-cols-2">
              {filteredOpportunities.map((opp) => (
                <Card
                  key={opp.id}
                  className="flex flex-col justify-between border-midnight-200 dark:border-midnight-800 hover:border-emerald-500/50 transition-all shadow-sm"
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="flex flex-wrap items-center gap-1.5 mb-1.5">
                          <span className="rounded-md bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider">
                            {opp.opportunity_type.replace('_', ' ')}
                          </span>
                          <span className="rounded-md border border-midnight-200 dark:border-midnight-700 px-2 py-0.5 text-[10px] text-midnight-600 dark:text-midnight-400 capitalize">
                            {opp.beneficiary_type.replace('_', ' ')}
                          </span>
                          <span className="rounded-md bg-midnight-100 dark:bg-midnight-800 px-2 py-0.5 text-[10px] text-midnight-600 dark:text-midnight-300">
                            {opp.geographic_scope}
                          </span>
                        </div>
                        <CardTitle className="text-base font-display text-midnight-950 dark:text-ivory-50 leading-snug">
                          {opp.title}
                        </CardTitle>
                        <div className="text-xs text-midnight-500 font-medium">{opp.provider}</div>
                      </div>

                      <button
                        type="button"
                        onClick={() => handleToggleBookmark(opp.id)}
                        title={isSaved(opp.id) ? 'Remove bookmark' : 'Bookmark opportunity'}
                        className={cn(
                          'p-1.5 rounded-lg border transition-colors',
                          isSaved(opp.id)
                            ? 'border-emerald-500 bg-emerald-500/10 text-emerald-600'
                            : 'border-midnight-200 dark:border-midnight-800 text-midnight-400 hover:text-midnight-900 dark:hover:text-ivory-50'
                        )}
                      >
                        {isSaved(opp.id) ? (
                          <BookmarkCheck className="h-4 w-4" />
                        ) : (
                          <Bookmark className="h-4 w-4" />
                        )}
                      </button>
                    </div>

                    <CardDescription className="text-xs text-midnight-600 dark:text-midnight-300 mt-2">
                      {opp.description}
                    </CardDescription>

                    {/* Funding / Benefits */}
                    {opp.funding_amount_or_benefits && (
                      <div className="mt-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20 p-2 text-[11px] text-emerald-900 dark:text-emerald-300 flex items-start gap-1.5">
                        <DollarSign className="h-3.5 w-3.5 mt-0.5 flex-shrink-0 text-emerald-600" />
                        <span><strong>Award / Benefit:</strong> {opp.funding_amount_or_benefits}</span>
                      </div>
                    )}
                  </CardHeader>

                  <CardContent className="space-y-3 pt-0">
                    <div className="flex flex-wrap items-center justify-between text-[11px] text-midnight-500 border-t border-midnight-100 dark:border-midnight-800/80 pt-2.5">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        <span>
                          {opp.is_rolling
                            ? 'Rolling Applications'
                            : opp.application_deadline
                            ? `Deadline: ${new Date(opp.application_deadline).toLocaleDateString()}`
                            : 'Open'}
                        </span>
                      </div>

                      <span className="text-[10px] text-midnight-400">
                        Verified {new Date(opp.date_last_verified).toLocaleDateString()}
                      </span>
                    </div>

                    <div className="flex items-center justify-between gap-2 pt-1">
                      <a
                        href={opp.official_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-xs text-amber-600 hover:underline font-medium"
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                        Official Provider Portal
                      </a>

                      <Button
                        size="sm"
                        variant={isSaved(opp.id) ? 'outline' : 'default'}
                        onClick={() => handleToggleBookmark(opp.id)}
                        className={cn(
                          'text-xs',
                          !isSaved(opp.id) && 'bg-emerald-600 hover:bg-emerald-700 text-ivory-50'
                        )}
                      >
                        {isSaved(opp.id) ? 'Saved' : 'Track Application'}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )
        ) : (
          /* Tracked Applications View */
          <div className="space-y-4">
            {savedApps.length === 0 ? (
              <Card className="p-8 text-center border-dashed">
                <p className="text-xs text-midnight-500 mb-3">No opportunities saved for tracking yet.</p>
                <Button size="sm" onClick={() => setActiveView('directory')} variant="outline">
                  Browse All Opportunities
                </Button>
              </Card>
            ) : (
              <div className="space-y-3">
                {savedApps.map((app) => (
                  <Card key={app.id} className="p-4 border-midnight-200 dark:border-midnight-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-semibold text-midnight-950 dark:text-ivory-50">
                          {app.opportunity?.title}
                        </h4>
                        <span className="text-xs text-midnight-500">({app.opportunity?.provider})</span>
                      </div>
                      <div className="text-xs text-midnight-500 mt-0.5">
                        {app.opportunity?.funding_amount_or_benefits || 'Non-monetary opportunity'}
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <select
                        value={app.status}
                        onChange={(e) => handleUpdateAppStatus(app.opportunity_id, e.target.value)}
                        className="rounded-lg border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-2.5 py-1 text-xs text-midnight-900 dark:text-ivory-50 focus:outline-none"
                      >
                        <option value="saved">Saved</option>
                        <option value="researching">Researching</option>
                        <option value="preparing">Preparing Application</option>
                        <option value="submitted">Submitted</option>
                        <option value="accepted">Accepted 🎉</option>
                        <option value="rejected">Rejected</option>
                        <option value="closed">Closed</option>
                      </select>

                      <a
                        href={app.opportunity?.official_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-midnight-400 hover:text-midnight-900 dark:hover:text-ivory-50 p-1"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  )
}

export default function OpportunitiesPage() {
  return (
    <AuthGuard>
      <OpportunitiesContent />
    </AuthGuard>
  )
}
