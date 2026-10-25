'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import {
  Compass,
  ArrowLeft,
  Filter,
  Sparkles,
  CheckCircle2,
  Clock,
  Layers,
  ArrowRight,
  Target,
  BookOpen,
  PlusCircle,
  HelpCircle,
} from 'lucide-react'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { api } from '@/lib/api-client'
import { showNotification } from '@/lib/notifications'
import { cn } from '@/lib/utils'

interface MilestoneTmpl {
  title: string
  phase: string
  description: string
  deliverables?: string[]
}

interface ProjectIdea {
  id: string
  title: string
  problem_statement: string
  intended_users: string
  domain: string
  difficulty: string
  prerequisites: string[]
  recommended_technologies: string[]
  estimated_duration_weeks: number
  weekly_hours: number
  expected_deliverables: string[]
  learning_outcomes: string[]
  suggested_milestones: MilestoneTmpl[]
  validation_strategy: string
  possible_next_stage_pathways: string[]
  relevant_career_skills: string[]
  primary_goals: string[]
  match_score?: number
  match_explanation?: string
}

function ProjectDiscoverContent() {
  const router = useRouter()
  const [ideas, setIdeas] = useState<ProjectIdea[]>([])
  const [loading, setLoading] = useState(true)
  const [creatingId, setCreatingId] = useState<string | null>(null)

  // Filters & Inferred preferences
  const [domainFilter, setDomainFilter] = useState('all')
  const [difficultyFilter, setDifficultyFilter] = useState('any')
  const [weeklyHours, setWeeklyHours] = useState(10)
  const [primaryGoal, setPrimaryGoal] = useState('portfolio')
  const [usedSignals, setUsedSignals] = useState<any>(null)

  useEffect(() => {
    fetchRecommendations()
  }, [domainFilter, difficultyFilter, weeklyHours, primaryGoal])

  const fetchRecommendations = async () => {
    try {
      setLoading(true)
      const res = await api.post<{
        recommendations: ProjectIdea[]
        total_matches: number
        applied_profile_signals: any
      }>('/api/v1/launchpad/ideas/recommend', {
        target_domain: domainFilter === 'all' ? null : domainFilter,
        difficulty_preference: difficultyFilter === 'any' ? null : difficultyFilter,
        weekly_hours_available: Number(weeklyHours),
        primary_objective: primaryGoal,
      })
      setIdeas(res.recommendations || [])
      setUsedSignals(res.applied_profile_signals)
    } catch {
      // Fallback directly to catalog
      try {
        const fallback = await api.get<ProjectIdea[]>('/api/v1/launchpad/ideas')
        setIdeas(fallback || [])
      } catch {
        setIdeas([])
      }
    } finally {
      setLoading(false)
    }
  }

  const handleStartProject = async (idea: ProjectIdea) => {
    try {
      setCreatingId(idea.id)
      const initialMilestones = idea.suggested_milestones.map((m, idx) => ({
        title: m.title,
        description: m.description,
        phase: m.phase,
        sequence_order: idx + 1,
        deliverables: m.deliverables || [],
      }))

      const newProject = await api.post<any>('/api/v1/launchpad/projects', {
        title: idea.title,
        description: idea.problem_statement,
        technologies: idea.recommended_technologies,
        domain: idea.domain,
        difficulty_level: idea.difficulty,
        primary_goal: primaryGoal,
        problem_statement: idea.problem_statement,
        target_users: idea.intended_users,
        proposed_solution: `Building ${idea.title} to address user pain points with validated architecture.`,
        weekly_hours: idea.weekly_hours,
        estimated_duration_weeks: idea.estimated_duration_weeks,
        origin: 'catalogue',
        catalogue_idea_id: idea.id,
        initial_milestones: initialMilestones,
      })

      router.push(`/projects/${newProject.id}`)
    } catch (err: any) {
      showNotification(err.message || 'Failed to start project', 'error')
      setCreatingId(null)
    }
  }

  return (
    <AppLayout>
      <div className="container py-8 max-w-7xl mx-auto px-4">
        {/* Navigation Breadcrumb */}
        <div className="mb-6 flex items-center gap-2 text-xs text-midnight-500">
          <Link href="/projects" className="hover:text-midnight-800 dark:hover:text-midnight-200 flex items-center gap-1">
            <ArrowLeft className="h-3.5 w-3.5" />
            Launchpad Hub
          </Link>
          <span>/</span>
          <span className="text-midnight-900 dark:text-ivory-50 font-medium">Idea Discovery</span>
        </div>

        {/* Title Hero */}
        <div className="mb-8">
          <div className="inline-flex items-center gap-1.5 rounded-full border border-amber-500/20 bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-700 dark:text-amber-400 mb-2">
            <Sparkles className="h-3.5 w-3.5" />
            Career-Aware Idea Matcher
          </div>
          <h1 className="font-display text-display-md text-midnight-950 dark:text-ivory-50 tracking-tight">
            Curated Project Blueprints
          </h1>
          <p className="text-sm text-midnight-600 dark:text-midnight-300 max-w-3xl mt-1">
            Deterministic ranking connecting your verified skills and Career Discovery targets with
            production-grade project specifications.
          </p>

          {/* Applied Profile Signals Banner */}
          {usedSignals?.used_authenticated_profile && (
            <div className="mt-4 flex flex-wrap items-center gap-2 rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3 text-xs text-emerald-800 dark:text-emerald-300">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 flex-shrink-0" />
              <span>
                <strong>Profile Connected:</strong> Recommendations inferred from your{' '}
                {usedSignals.skills_considered?.length > 0 && `${usedSignals.skills_considered.length} verified skills`}
                {usedSignals.career_roles_considered?.length > 0 &&
                  ` and Career Discovery target roles (${usedSignals.career_roles_considered.slice(0, 2).join(', ')})`}
                . You can customize filters below anytime.
              </span>
            </div>
          )}
        </div>

        {/* Interactive Filter Bar */}
        <div className="mb-8 rounded-2xl border border-midnight-200 dark:border-midnight-800 bg-white dark:bg-midnight-900/60 p-4 shadow-sm">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-midnight-500 mb-3">
            <Filter className="h-3.5 w-3.5" />
            Customize Preferences & Constraints
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {/* Domain Filter */}
            <div>
              <label className="block text-[11px] font-medium text-midnight-600 dark:text-midnight-400 mb-1">
                Technical Domain
              </label>
              <select
                value={domainFilter}
                onChange={(e) => setDomainFilter(e.target.value)}
                className="w-full rounded-lg border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3 py-1.5 text-xs text-midnight-950 dark:text-ivory-50 focus:border-amber-500 focus:outline-none"
              >
                <option value="all">All Domains</option>
                <option value="AI / Machine Learning">AI & Machine Learning</option>
                <option value="Full Stack Web">Full Stack Web</option>
                <option value="Cloud & DevOps">Cloud & Distributed Systems</option>
                <option value="HealthTech & BioInformatics">HealthTech & Bio</option>
                <option value="ClimateTech & IoT">ClimateTech & IoT</option>
                <option value="Cybersecurity & Developer Tools">Cybersecurity & DevTools</option>
                <option value="Fintech & Cryptography">Fintech & Cryptography</option>
              </select>
            </div>

            {/* Difficulty Filter */}
            <div>
              <label className="block text-[11px] font-medium text-midnight-600 dark:text-midnight-400 mb-1">
                Difficulty Level
              </label>
              <select
                value={difficultyFilter}
                onChange={(e) => setDifficultyFilter(e.target.value)}
                className="w-full rounded-lg border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3 py-1.5 text-xs text-midnight-950 dark:text-ivory-50 focus:border-amber-500 focus:outline-none"
              >
                <option value="any">Any Difficulty</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            {/* Weekly Hours */}
            <div>
              <label className="block text-[11px] font-medium text-midnight-600 dark:text-midnight-400 mb-1">
                Weekly Time Budget ({weeklyHours} hrs/wk)
              </label>
              <input
                type="range"
                min="4"
                max="30"
                step="2"
                value={weeklyHours}
                onChange={(e) => setWeeklyHours(Number(e.target.value))}
                className="w-full accent-amber-600 cursor-pointer"
              />
            </div>

            {/* Primary Objective */}
            <div>
              <label className="block text-[11px] font-medium text-midnight-600 dark:text-midnight-400 mb-1">
                Primary Goal
              </label>
              <select
                value={primaryGoal}
                onChange={(e) => setPrimaryGoal(e.target.value)}
                className="w-full rounded-lg border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3 py-1.5 text-xs text-midnight-950 dark:text-ivory-50 focus:border-amber-500 focus:outline-none"
              >
                <option value="portfolio">Portfolio Development</option>
                <option value="learning">Foundational Skill Learning</option>
                <option value="research">Research & Publication</option>
                <option value="competition">Competition / Hackathon</option>
                <option value="entrepreneurship">Startup / Commercial</option>
              </select>
            </div>
          </div>
        </div>

        {/* Ideas Grid */}
        {loading ? (
          <div className="grid gap-6 md:grid-cols-2">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-72 rounded-2xl border border-midnight-200 dark:border-midnight-800 bg-midnight-900/10 animate-pulse" />
            ))}
          </div>
        ) : ideas.length === 0 ? (
          <Card className="p-8 text-center border-dashed">
            <h3 className="font-semibold text-midnight-950 dark:text-ivory-50">No matching ideas found</h3>
            <p className="text-xs text-midnight-500 mt-1 mb-4">
              Try adjusting your difficulty or domain filters to view more project blueprints.
            </p>
            <Button size="sm" variant="outline" onClick={() => { setDomainFilter('all'); setDifficultyFilter('any') }}>
              Reset Filters
            </Button>
          </Card>
        ) : (
          <div className="grid gap-6 md:grid-cols-2">
            {ideas.map((idea) => (
              <Card
                key={idea.id}
                className="flex flex-col justify-between border-midnight-200 dark:border-midnight-800 hover:border-amber-400/50 transition-all shadow-sm"
              >
                <CardHeader>
                  {/* Top Badges & Match Score */}
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="rounded-md bg-midnight-100 dark:bg-midnight-800 px-2 py-0.5 text-[11px] font-medium text-midnight-700 dark:text-midnight-300">
                        {idea.domain}
                      </span>
                      <span className="rounded-md border border-midnight-200 dark:border-midnight-700 px-2 py-0.5 text-[11px] font-medium capitalize text-midnight-600 dark:text-midnight-400">
                        {idea.difficulty}
                      </span>
                      <span className="rounded-md bg-amber-500/10 text-amber-700 dark:text-amber-400 px-2 py-0.5 text-[11px] font-medium">
                        {idea.estimated_duration_weeks} wks ({idea.weekly_hours}h/wk)
                      </span>
                    </div>

                    {idea.match_score !== undefined && (
                      <div className="flex flex-col items-end">
                        <span className="text-xs font-bold text-amber-600 dark:text-amber-400">
                          {idea.match_score}% Match
                        </span>
                        <span className="text-[9px] text-midnight-400">rule-based</span>
                      </div>
                    )}
                  </div>

                  <CardTitle className="text-lg font-display text-midnight-950 dark:text-ivory-50 leading-snug">
                    {idea.title}
                  </CardTitle>

                  <CardDescription className="text-xs text-midnight-600 dark:text-midnight-300 mt-1">
                    {idea.problem_statement}
                  </CardDescription>

                  {/* Explicit Explanation Banner */}
                  {idea.match_explanation && (
                    <div className="mt-3 rounded-xl border border-amber-500/20 bg-amber-500/5 p-2.5 text-[11px] text-amber-900 dark:text-amber-200 leading-relaxed">
                      <strong>Why this matches:</strong> {idea.match_explanation}
                    </div>
                  )}
                </CardHeader>

                <CardContent className="space-y-4 pt-0">
                  {/* Recommended Technologies */}
                  <div>
                    <div className="text-[10px] uppercase tracking-wider font-semibold text-midnight-400 mb-1.5">
                      Recommended Toolchain
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {idea.recommended_technologies.map((tech) => (
                        <span
                          key={tech}
                          className="rounded-md border border-midnight-200 dark:border-midnight-800 bg-midnight-50 dark:bg-midnight-950 px-2 py-0.5 text-[10px] text-midnight-700 dark:text-midnight-300"
                        >
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Key Deliverables */}
                  <div>
                    <div className="text-[10px] uppercase tracking-wider font-semibold text-midnight-400 mb-1">
                      Expected Deliverables
                    </div>
                    <ul className="text-xs text-midnight-600 dark:text-midnight-300 space-y-1">
                      {idea.expected_deliverables.slice(0, 2).map((del, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 mt-0.5 flex-shrink-0" />
                          <span className="line-clamp-1">{del}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Action Buttons */}
                  <div className="pt-2 border-t border-midnight-100 dark:border-midnight-800/80 flex items-center justify-between gap-3">
                    <span className="text-[11px] text-midnight-500">
                      {idea.suggested_milestones.length} structured milestones
                    </span>

                    <Button
                      size="sm"
                      disabled={creatingId === idea.id}
                      onClick={() => handleStartProject(idea)}
                      className="bg-amber-600 hover:bg-amber-700 text-ivory-50 gap-1.5 text-xs"
                    >
                      {creatingId === idea.id ? 'Creating Project...' : 'Start this Project'}
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  )
}

export default function ProjectDiscoverPage() {
  return (
    <AuthGuard>
      <ProjectDiscoverContent />
    </AuthGuard>
  )
}
