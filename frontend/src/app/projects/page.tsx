'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import {
  Rocket,
  Compass,
  FileCode,
  Award,
  ArrowRight,
  Plus,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  ChevronRight,
  Sparkles,
  ExternalLink,
  Trash2,
  FileText,
} from 'lucide-react'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { api } from '@/lib/api-client'
import { cn } from '@/lib/utils'

interface ProjectItem {
  id: string
  title: string
  description: string
  role?: string
  technologies: string[]
  domain?: string
  difficulty_level?: string
  stage?: string
  status?: string
  blocker_description?: string
  completion_percentage: number
  github_url?: string
  demo_url?: string
  created_at: string
}

function ProjectsHubContent() {
  const router = useRouter()
  const [projects, setProjects] = useState<ProjectItem[]>([])
  const [resumeProjects, setResumeProjects] = useState<any[]>([])
  const [importingTitle, setImportingTitle] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      setLoading(true)
      const data = await api.get<ProjectItem[]>('/api/v1/launchpad/projects')
      setProjects(data || [])
    } catch {
      setProjects([])
    } finally {
      setLoading(false)
    }

    try {
      const rp = await api.get<any[]>('/api/v1/launchpad/resume-projects')
      setResumeProjects(rp || [])
    } catch {
      setResumeProjects([])
    }
  }

  const handleImportResumeProject = async (rp: any) => {
    try {
      setImportingTitle(rp.title)
      const newProject = await api.post<any>('/api/v1/launchpad/projects', {
        title: rp.title,
        description: rp.description || `Engineering project imported from resume: ${rp.title}`,
        technologies: rp.technologies || [],
        domain: 'Software Engineering',
        difficulty_level: 'intermediate',
        primary_goal: 'portfolio',
        problem_statement: rp.description || `Core problem addressed by ${rp.title}`,
        target_users: 'Software Engineers / End Users',
        proposed_solution: `Implemented ${rp.title} with full architecture and validation.`,
        weekly_hours: 8,
        estimated_duration_weeks: 6,
        origin: 'resume',
        initial_milestones: [
          { title: 'System Architecture & Requirements', phase: 'Architecture', sequence_order: 1 },
          { title: 'Core Implementation & Features', phase: 'MVP Core', sequence_order: 2 },
          { title: 'Testing, Validation & Benchmark', phase: 'Testing', sequence_order: 3 },
          { title: 'Outcome Assessment (Startup, Paper, Showcase)', phase: 'Polish & Showcase', sequence_order: 4 },
        ],
      })
      router.push(`/projects/${newProject.id}`)
    } catch (err: any) {
      alert(err.message || 'Failed to import project')
      setImportingTitle(null)
    }
  }

  const handleDelete = async (e: React.MouseEvent, projectId: string) => {
    e.preventDefault()
    e.stopPropagation()
    if (!confirm('Are you sure you want to delete this project?')) return

    try {
      await api.delete(`/api/v1/launchpad/projects/${projectId}`)
      setProjects((prev) => prev.filter((p) => p.id !== projectId))
    } catch (err: any) {
      alert(err.message || 'Failed to delete project')
    }
  }

  return (
    <AppLayout>
      <div className="container py-8 max-w-7xl mx-auto px-4">
        {/* Header Hero */}
        <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-amber-500/20 bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-700 dark:text-amber-400 mb-2">
              <Rocket className="h-3.5 w-3.5" />
              ORVENA Project Launchpad
            </div>
            <h1 className="font-display text-display-md text-midnight-950 dark:text-ivory-50 tracking-tight">
              Project Intelligence & Development Studio
            </h1>
            <p className="text-sm md:text-base text-midnight-600 dark:text-midnight-300 max-w-2xl mt-1">
              Discover career-aligned project ideas, build structured engineering plans, track milestone progress,
              and unlock verified competitions, fellowships, and outcome pathways.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link href="/projects/new">
              <Button className="bg-amber-600 hover:bg-amber-700 text-ivory-50 shadow-sm gap-2">
                <Plus className="h-4 w-4" />
                New Project
              </Button>
            </Link>
          </div>
        </div>

        {/* 3 Primary Student Journeys */}
        <div className="grid gap-6 md:grid-cols-3 mb-12">
          {/* Journey A: Discover Ideas */}
          <Link href="/projects/discover" className="group">
            <Card className="glass-card card-hover h-full border-midnight-200 dark:border-midnight-800 transition-all hover:border-amber-400/50">
              <CardHeader className="pb-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-500/10 text-amber-600 mb-3 group-hover:scale-105 transition-transform">
                  <Compass className="h-6 w-6" />
                </div>
                <div className="text-xs font-semibold tracking-wider uppercase text-amber-600 dark:text-amber-400">
                  Journey A
                </div>
                <CardTitle className="text-lg font-display text-midnight-950 dark:text-ivory-50">
                  Discover Project Ideas
                </CardTitle>
                <CardDescription className="text-xs text-midnight-600 dark:text-midnight-300">
                  Need inspiration? Match against 30+ curated real-world project blueprints ranked deterministically by your skills.
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <span className="inline-flex items-center text-xs font-semibold text-amber-600 dark:text-amber-400 group-hover:translate-x-1 transition-transform">
                  Find tailored ideas <ArrowRight className="h-3.5 w-3.5 ml-1" />
                </span>
              </CardContent>
            </Card>
          </Link>

          {/* Journey B: Plan & Develop */}
          <Link href="/projects/new" className="group">
            <Card className="glass-card card-hover h-full border-midnight-200 dark:border-midnight-800 transition-all hover:border-pathfinder-400/50">
              <CardHeader className="pb-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-pathfinder-500/10 text-pathfinder-600 mb-3 group-hover:scale-105 transition-transform">
                  <FileCode className="h-6 w-6" />
                </div>
                <div className="text-xs font-semibold tracking-wider uppercase text-pathfinder-600 dark:text-pathfinder-400">
                  Journey B
                </div>
                <CardTitle className="text-lg font-display text-midnight-950 dark:text-ivory-50">
                  Plan & Structure My Idea
                </CardTitle>
                <CardDescription className="text-xs text-midnight-600 dark:text-midnight-300">
                  Already have an idea? Generate a structured engineering blueprint: MVP scope, phased milestones, and validation plan.
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <span className="inline-flex items-center text-xs font-semibold text-pathfinder-600 dark:text-pathfinder-400 group-hover:translate-x-1 transition-transform">
                  Generate engineering plan <ArrowRight className="h-3.5 w-3.5 ml-1" />
                </span>
              </CardContent>
            </Card>
          </Link>

          {/* Journey C: Opportunities & Outcomes */}
          <Link href="/projects/opportunities" className="group">
            <Card className="glass-card card-hover h-full border-midnight-200 dark:border-midnight-800 transition-all hover:border-emerald-400/50">
              <CardHeader className="pb-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-600 mb-3 group-hover:scale-105 transition-transform">
                  <Award className="h-6 w-6" />
                </div>
                <div className="text-xs font-semibold tracking-wider uppercase text-emerald-600 dark:text-emerald-400">
                  Journey C
                </div>
                <CardTitle className="text-lg font-display text-midnight-950 dark:text-ivory-50">
                  Opportunities & Outcomes
                </CardTitle>
                <CardDescription className="text-xs text-midnight-600 dark:text-midnight-300">
                  Connect completed work to verified student competitions, fellowships, grants (GSoC, Imagine Cup), and publication pathways.
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <span className="inline-flex items-center text-xs font-semibold text-emerald-600 dark:text-emerald-400 group-hover:translate-x-1 transition-transform">
                  Explore opportunities <ArrowRight className="h-3.5 w-3.5 ml-1" />
                </span>
              </CardContent>
            </Card>
          </Link>
        </div>

        {/* Projects Detected from Resume Banner */}
        {resumeProjects.length > 0 && (
          <Card className="mb-8 border-teal-500/30 bg-teal-500/5 p-6 shadow-sm">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 mb-4">
              <div className="flex items-center gap-2.5">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-500/10 text-teal-600">
                  <FileText className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-display font-semibold text-base text-midnight-950 dark:text-ivory-50">
                    Projects Detected from Your Uploaded Resume ({resumeProjects.length})
                  </h3>
                  <p className="text-xs text-midnight-500">
                    Import to track milestones, perform 5-dimension rubric evaluations, and analyze Outcome Intelligence (Startup, Product, Thesis/Paper)
                  </p>
                </div>
              </div>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              {resumeProjects.map((rp, idx) => (
                <div
                  key={idx}
                  className="flex items-start justify-between gap-3 rounded-xl border border-midnight-200 dark:border-midnight-800 bg-white dark:bg-midnight-900/60 p-4 shadow-sm"
                >
                  <div className="space-y-1">
                    <h4 className="font-semibold text-sm text-midnight-950 dark:text-ivory-50">{rp.title}</h4>
                    {rp.description && (
                      <p className="text-xs text-midnight-500 line-clamp-2">{rp.description}</p>
                    )}
                    {rp.technologies?.length > 0 && (
                      <div className="flex flex-wrap gap-1 pt-1">
                        {rp.technologies.slice(0, 4).map((t: string, i: number) => (
                          <span
                            key={i}
                            className="rounded-md bg-midnight-100 dark:bg-midnight-800 px-1.5 py-0.5 text-[10px] font-medium text-midnight-600 dark:text-midnight-400"
                          >
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <Button
                    size="sm"
                    disabled={importingTitle === rp.title}
                    onClick={() => handleImportResumeProject(rp)}
                    className="shrink-0 bg-teal-600 hover:bg-teal-700 text-ivory-50 text-xs gap-1"
                  >
                    <Plus className="h-3.5 w-3.5" />
                    {importingTitle === rp.title ? 'Importing...' : 'Track & Evaluate'}
                  </Button>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Active Projects Section */}
        <div className="mb-10">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-display font-semibold text-midnight-950 dark:text-ivory-50">
                My Active Projects ({projects.length})
              </h2>
              <p className="text-xs text-midnight-500">
                Persistent project records with milestone completion tracking and evaluation history
              </p>
            </div>
            <Link href="/projects/new">
              <Button size="sm" variant="outline" className="border-midnight-300 dark:border-midnight-700 text-xs gap-1.5">
                <Plus className="h-3.5 w-3.5" />
                Add Project
              </Button>
            </Link>
          </div>

          {loading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-48 rounded-xl border border-midnight-200 dark:border-midnight-800 bg-midnight-900/10 animate-pulse" />
              ))}
            </div>
          ) : projects.length === 0 ? (
            <Card className="border-dashed border-midnight-300 dark:border-midnight-800 p-8 text-center bg-midnight-900/5">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-500/10 text-amber-600 mb-4">
                <Rocket className="h-7 w-7" />
              </div>
              <h3 className="text-base font-semibold text-midnight-950 dark:text-ivory-50">
                No active projects yet
              </h3>
              <p className="text-xs text-midnight-500 max-w-md mx-auto mt-1 mb-6">
                Start by browsing career-aware project ideas or bring your own idea to generate a structured milestone plan.
              </p>
              <div className="flex flex-wrap items-center justify-center gap-3">
                <Link href="/projects/discover">
                  <Button size="sm" className="bg-amber-600 hover:bg-amber-700 text-ivory-50">
                    Discover Ideas
                  </Button>
                </Link>
                <Link href="/projects/new">
                  <Button size="sm" variant="outline">
                    Plan My Own Idea
                  </Button>
                </Link>
              </div>
            </Card>
          ) : (
            <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
              {projects.map((project) => (
                <Link
                  key={project.id}
                  href={`/projects/${project.id}`}
                  className="group relative flex flex-col justify-between rounded-xl border border-midnight-200 dark:border-midnight-800 bg-white dark:bg-midnight-900/70 p-5 shadow-sm hover:border-amber-400/50 hover:shadow-md transition-all"
                >
                  <div>
                    {/* Top Badges */}
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <span className="inline-flex items-center rounded-md bg-midnight-100 dark:bg-midnight-800 px-2 py-0.5 text-[11px] font-medium text-midnight-700 dark:text-midnight-300 capitalize">
                        {project.domain || 'Engineering'}
                      </span>
                      <div className="flex items-center gap-2">
                        <span
                          className={cn(
                            'inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider',
                            project.status === 'completed'
                              ? 'bg-emerald-500/10 text-emerald-600'
                              : project.status === 'blocked'
                              ? 'bg-rose-500/10 text-rose-600'
                              : 'bg-amber-500/10 text-amber-600'
                          )}
                        >
                          {project.stage || project.status || 'in_progress'}
                        </span>
                        <button
                          type="button"
                          onClick={(e) => handleDelete(e, project.id)}
                          title="Delete project"
                          className="text-midnight-400 hover:text-rose-500 p-1 transition-colors"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>

                    <h3 className="font-display font-semibold text-base text-midnight-950 dark:text-ivory-50 group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors line-clamp-1">
                      {project.title}
                    </h3>
                    <p className="text-xs text-midnight-600 dark:text-midnight-300 mt-1 line-clamp-2">
                      {project.description}
                    </p>

                    {/* Blocker alert if present */}
                    {project.blocker_description && (
                      <div className="mt-3 flex items-start gap-1.5 rounded-lg border border-rose-500/20 bg-rose-500/10 p-2 text-[11px] text-rose-700 dark:text-rose-300">
                        <AlertCircle className="h-3.5 w-3.5 mt-0.5 flex-shrink-0" />
                        <span className="line-clamp-1">{project.blocker_description}</span>
                      </div>
                    )}

                    {/* Tech Stack Chips */}
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {(project.technologies || []).slice(0, 3).map((tech) => (
                        <span
                          key={tech}
                          className="rounded-md border border-midnight-200 dark:border-midnight-800 bg-midnight-50 dark:bg-midnight-950 px-2 py-0.5 text-[10px] text-midnight-600 dark:text-midnight-400"
                        >
                          {tech}
                        </span>
                      ))}
                      {(project.technologies || []).length > 3 && (
                        <span className="text-[10px] text-midnight-400 self-center">
                          +{project.technologies.length - 3}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Bottom Progress Bar */}
                  <div className="mt-5 pt-3 border-t border-midnight-100 dark:border-midnight-800/80">
                    <div className="flex items-center justify-between text-[11px] mb-1.5">
                      <span className="text-midnight-500 font-medium">Milestones</span>
                      <span className="font-semibold text-midnight-800 dark:text-midnight-200">
                        {project.completion_percentage}%
                      </span>
                    </div>
                    <div className="h-1.5 w-full rounded-full bg-midnight-100 dark:bg-midnight-800 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-amber-500 transition-all duration-500"
                        style={{ width: `${project.completion_percentage}%` }}
                      />
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  )
}

export default function ProjectsPage() {
  return (
    <AuthGuard>
      <ProjectsHubContent />
    </AuthGuard>
  )
}
