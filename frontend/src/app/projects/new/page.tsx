'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import {
  FileCode,
  ArrowLeft,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Layers,
  AlertTriangle,
  Clock,
  Plus,
  Trash2,
} from 'lucide-react'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { api } from '@/lib/api-client'

interface PlannedPhase {
  phase_name: string
  target_week_start: number
  target_week_end: number
  objective: string
  tasks: string[]
  deliverables: string[]
  validation_criteria: string
}

interface MilestoneTmpl {
  title: string
  phase: string
  description: string
  deliverables: string[]
}

interface GeneratedPlan {
  title: string
  problem_definition: string
  minimum_viable_scope: string[]
  future_scope: string[]
  required_prerequisites: string[]
  phases: PlannedPhase[]
  testing_and_validation_plan: string[]
  risks_and_dependencies: { risk: string; impact: string; mitigation: string }[]
  suggested_milestones: MilestoneTmpl[]
  suggested_timeline_weeks: number
}

function NewProjectContent() {
  const router = useRouter()
  const [step, setStep] = useState<1 | 2>(1)
  const [generating, setGenerating] = useState(false)
  const [committing, setCommitting] = useState(false)

  // Form State
  const [title, setTitle] = useState('')
  const [problemStatement, setProblemStatement] = useState('')
  const [intendedUsers, setIntendedUsers] = useState('')
  const [proposedSolution, setProposedSolution] = useState('')
  const [domain, setDomain] = useState('Full Stack Web')
  const [technologiesText, setTechnologiesText] = useState('React, TypeScript, FastAPI, PostgreSQL')
  const [currentStage, setCurrentStage] = useState('idea')
  const [weeklyHours, setWeeklyHours] = useState(10)
  const [targetDurationWeeks, setTargetDurationWeeks] = useState(8)
  const [primaryGoal, setPrimaryGoal] = useState('portfolio')
  const [repoUrl, setRepoUrl] = useState('')
  const [demoUrl, setDemoUrl] = useState('')

  // Plan State
  const [generatedPlan, setGeneratedPlan] = useState<GeneratedPlan | null>(null)

  const handleGeneratePlan = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim() || !problemStatement.trim() || !proposedSolution.trim()) {
      alert('Please fill out the project title, problem statement, and proposed solution.')
      return
    }

    const techArray = technologiesText
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean)

    if (techArray.length === 0) {
      alert('Please specify at least one core technology.')
      return
    }

    try {
      setGenerating(true)
      const plan = await api.post<GeneratedPlan>('/api/v1/launchpad/plan', {
        title,
        problem_statement: problemStatement,
        intended_users: intendedUsers || 'Software engineering users',
        proposed_solution: proposedSolution,
        domain,
        technologies: techArray,
        current_stage: currentStage,
        weekly_hours: Number(weeklyHours),
        target_duration_weeks: Number(targetDurationWeeks),
        primary_goal: primaryGoal,
        repository_url: repoUrl || null,
        demo_url: demoUrl || null,
      })

      setGeneratedPlan(plan)
      setStep(2)
    } catch (err: any) {
      alert(err.message || 'Failed to generate project plan')
    } finally {
      setGenerating(false)
    }
  }

  const handleCommitProject = async () => {
    if (!generatedPlan) return

    const techArray = technologiesText
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean)

    try {
      setCommitting(true)
      const initialMilestones = generatedPlan.suggested_milestones.map((m, idx) => ({
        title: m.title,
        description: m.description,
        phase: m.phase,
        sequence_order: idx + 1,
        deliverables: m.deliverables || [],
      }))

      const created = await api.post<any>('/api/v1/launchpad/projects', {
        title,
        description: problemStatement,
        technologies: techArray,
        domain,
        difficulty_level: 'intermediate',
        primary_goal: primaryGoal,
        stage: currentStage,
        problem_statement: problemStatement,
        target_users: intendedUsers,
        proposed_solution: proposedSolution,
        weekly_hours: Number(weeklyHours),
        estimated_duration_weeks: Number(targetDurationWeeks),
        github_url: repoUrl || null,
        demo_url: demoUrl || null,
        origin: 'scratch',
        initial_milestones: initialMilestones,
        plan_data: generatedPlan,
      })

      router.push(`/projects/${created.id}`)
    } catch (err: any) {
      alert(err.message || 'Failed to create project')
      setCommitting(false)
    }
  }

  return (
    <AppLayout>
      <div className="container py-8 max-w-4xl mx-auto px-4">
        {/* Navigation Breadcrumb */}
        <div className="mb-6 flex items-center gap-2 text-xs text-midnight-500">
          <Link href="/projects" className="hover:text-midnight-800 dark:hover:text-midnight-200 flex items-center gap-1">
            <ArrowLeft className="h-3.5 w-3.5" />
            Launchpad Hub
          </Link>
          <span>/</span>
          <span className="text-midnight-900 dark:text-ivory-50 font-medium">New Project</span>
        </div>

        {/* Header */}
        <div className="mb-8">
          <h1 className="font-display text-display-md text-midnight-950 dark:text-ivory-50 tracking-tight">
            {step === 1 ? 'Structure Your Project Idea' : 'Review & Commit Engineering Plan'}
          </h1>
          <p className="text-sm text-midnight-600 dark:text-midnight-300 mt-1">
            {step === 1
              ? 'Provide your idea parameters to generate a phased roadmap, MVP scope boundary, and risk mitigation plan.'
              : 'Review your deterministic project blueprint. You can edit any milestone in your workspace after committing.'}
          </p>
        </div>

        {step === 1 ? (
          /* Step 1: Input Form */
          <form onSubmit={handleGeneratePlan} className="space-y-6">
            <Card className="border-midnight-200 dark:border-midnight-800 p-6 space-y-5">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-midnight-700 dark:text-midnight-300 mb-1.5">
                  Project Title *
                </label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Distributed Task Orchestrator & Worker Pool"
                  className="w-full rounded-xl border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3.5 py-2.5 text-sm text-midnight-950 dark:text-ivory-50 focus:border-amber-500 focus:outline-none"
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-midnight-700 dark:text-midnight-300 mb-1.5">
                    Domain Category
                  </label>
                  <select
                    value={domain}
                    onChange={(e) => setDomain(e.target.value)}
                    className="w-full rounded-xl border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3.5 py-2.5 text-sm text-midnight-950 dark:text-ivory-50 focus:border-amber-500 focus:outline-none"
                  >
                    <option value="Full Stack Web">Full Stack Web</option>
                    <option value="AI / Machine Learning">AI / Machine Learning</option>
                    <option value="Cloud & DevOps">Cloud & DevOps / Distributed Systems</option>
                    <option value="HealthTech & BioInformatics">HealthTech & BioInformatics</option>
                    <option value="ClimateTech & IoT">ClimateTech & IoT</option>
                    <option value="Cybersecurity & Developer Tools">Cybersecurity & Developer Tools</option>
                    <option value="Fintech & Cryptography">Fintech & Cryptography</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-midnight-700 dark:text-midnight-300 mb-1.5">
                    Current Stage
                  </label>
                  <select
                    value={currentStage}
                    onChange={(e) => setCurrentStage(e.target.value)}
                    className="w-full rounded-xl border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3.5 py-2.5 text-sm text-midnight-950 dark:text-ivory-50 focus:border-amber-500 focus:outline-none"
                  >
                    <option value="idea">Idea / Concept Stage</option>
                    <option value="planning">Architecture & Planning</option>
                    <option value="in_progress">Active Implementation</option>
                    <option value="validation">Testing & Validation</option>
                    <option value="completed">Completed Prototype</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-midnight-700 dark:text-midnight-300 mb-1.5">
                  Problem Statement *
                </label>
                <textarea
                  required
                  rows={3}
                  value={problemStatement}
                  onChange={(e) => setProblemStatement(e.target.value)}
                  placeholder="What friction or problem does this project solve? Who experiences this challenge?"
                  className="w-full rounded-xl border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3.5 py-2.5 text-sm text-midnight-950 dark:text-ivory-50 focus:border-amber-500 focus:outline-none"
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-midnight-700 dark:text-midnight-300 mb-1.5">
                    Intended Users or Beneficiaries
                  </label>
                  <input
                    type="text"
                    value={intendedUsers}
                    onChange={(e) => setIntendedUsers(e.target.value)}
                    placeholder="e.g. University researchers, DevOps engineers"
                    className="w-full rounded-xl border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3.5 py-2.5 text-sm text-midnight-950 dark:text-ivory-50 focus:border-amber-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-midnight-700 dark:text-midnight-300 mb-1.5">
                    Proposed Solution *
                  </label>
                  <input
                    type="text"
                    required
                    value={proposedSolution}
                    onChange={(e) => setProposedSolution(e.target.value)}
                    placeholder="e.g. Master-worker queue with heartbeat health checks"
                    className="w-full rounded-xl border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3.5 py-2.5 text-sm text-midnight-950 dark:text-ivory-50 focus:border-amber-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-midnight-700 dark:text-midnight-300 mb-1.5">
                  Core Technologies (Comma Separated) *
                </label>
                <input
                  type="text"
                  required
                  value={technologiesText}
                  onChange={(e) => setTechnologiesText(e.target.value)}
                  placeholder="e.g. Python, FastAPI, Docker, Redis"
                  className="w-full rounded-xl border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3.5 py-2.5 text-sm text-midnight-950 dark:text-ivory-50 focus:border-amber-500 focus:outline-none"
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-midnight-700 dark:text-midnight-300 mb-1.5">
                    Weekly Hours ({weeklyHours} h/wk)
                  </label>
                  <input
                    type="number"
                    min="2"
                    max="40"
                    value={weeklyHours}
                    onChange={(e) => setWeeklyHours(Number(e.target.value))}
                    className="w-full rounded-xl border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3.5 py-2 text-sm text-midnight-950 dark:text-ivory-50 focus:border-amber-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-midnight-700 dark:text-midnight-300 mb-1.5">
                    Target Weeks ({targetDurationWeeks} wks)
                  </label>
                  <input
                    type="number"
                    min="3"
                    max="24"
                    value={targetDurationWeeks}
                    onChange={(e) => setTargetDurationWeeks(Number(e.target.value))}
                    className="w-full rounded-xl border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3.5 py-2 text-sm text-midnight-950 dark:text-ivory-50 focus:border-amber-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-midnight-700 dark:text-midnight-300 mb-1.5">
                    Primary Goal
                  </label>
                  <select
                    value={primaryGoal}
                    onChange={(e) => setPrimaryGoal(e.target.value)}
                    className="w-full rounded-xl border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3.5 py-2 text-sm text-midnight-950 dark:text-ivory-50 focus:border-amber-500 focus:outline-none"
                  >
                    <option value="portfolio">Portfolio Asset</option>
                    <option value="learning">Technical Learning</option>
                    <option value="research">Research / Paper</option>
                    <option value="competition">Competition / Hackathon</option>
                    <option value="entrepreneurship">Startup / MVP</option>
                  </select>
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-midnight-700 dark:text-midnight-300 mb-1.5">
                    Repository URL (Optional)
                  </label>
                  <input
                    type="url"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    placeholder="https://github.com/username/project"
                    className="w-full rounded-xl border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3.5 py-2 text-sm text-midnight-950 dark:text-ivory-50 focus:border-amber-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-midnight-700 dark:text-midnight-300 mb-1.5">
                    Demo URL (Optional)
                  </label>
                  <input
                    type="url"
                    value={demoUrl}
                    onChange={(e) => setDemoUrl(e.target.value)}
                    placeholder="https://my-demo-app.vercel.app"
                    className="w-full rounded-xl border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3.5 py-2 text-sm text-midnight-950 dark:text-ivory-50 focus:border-amber-500 focus:outline-none"
                  />
                </div>
              </div>
            </Card>

            <div className="flex items-center justify-end gap-3">
              <Link href="/projects">
                <Button variant="outline">Cancel</Button>
              </Link>
              <Button
                type="submit"
                disabled={generating}
                className="bg-amber-600 hover:bg-amber-700 text-ivory-50 gap-2"
              >
                {generating ? 'Generating Engineering Plan...' : 'Generate Structured Plan'}
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </form>
        ) : (
          /* Step 2: Plan Preview & Commit */
          <div className="space-y-6">
            <div className="flex items-center justify-between bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 text-xs text-amber-900 dark:text-amber-200">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-amber-600 flex-shrink-0" />
                <span>
                  <strong>Deterministic Plan Generated:</strong> 4 phases, {generatedPlan?.suggested_milestones.length} milestones, and MVP bounds calculated based on your inputs.
                </span>
              </div>
              <Button size="sm" variant="ghost" onClick={() => setStep(1)} className="text-amber-800 dark:text-amber-300 hover:bg-amber-500/20">
                Edit Parameters
              </Button>
            </div>

            {/* Scope Boundaries */}
            <div className="grid gap-5 md:grid-cols-2">
              <Card className="border-midnight-200 dark:border-midnight-800 p-5">
                <div className="text-xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 mb-2 flex items-center gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  Minimum Viable Scope (MVP)
                </div>
                <ul className="text-xs text-midnight-600 dark:text-midnight-300 space-y-1.5">
                  {generatedPlan?.minimum_viable_scope.map((item, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-emerald-500 font-bold">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </Card>

              <Card className="border-midnight-200 dark:border-midnight-800 p-5">
                <div className="text-xs font-semibold uppercase tracking-wider text-midnight-500 mb-2 flex items-center gap-1.5">
                  <Layers className="h-3.5 w-3.5" />
                  Future Phase Extensions
                </div>
                <ul className="text-xs text-midnight-600 dark:text-midnight-300 space-y-1.5">
                  {generatedPlan?.future_scope.map((item, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-midnight-400">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </Card>
            </div>

            {/* Phased Roadmap */}
            <Card className="border-midnight-200 dark:border-midnight-800 p-5">
              <h3 className="font-display font-semibold text-base text-midnight-950 dark:text-ivory-50 mb-4">
                4-Phase Engineering Schedule ({generatedPlan?.suggested_timeline_weeks} Weeks)
              </h3>
              <div className="space-y-4">
                {generatedPlan?.phases.map((phase, idx) => (
                  <div key={idx} className="rounded-xl border border-midnight-200 dark:border-midnight-800 bg-midnight-50 dark:bg-midnight-950/60 p-4">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="font-semibold text-midnight-900 dark:text-ivory-50">{phase.phase_name}</span>
                      <span className="text-[11px] text-amber-600 dark:text-amber-400 font-medium">
                        Weeks {phase.target_week_start}–{phase.target_week_end}
                      </span>
                    </div>
                    <p className="text-xs text-midnight-500 mb-2">{phase.objective}</p>
                    <div className="flex flex-wrap gap-2 text-[11px] text-midnight-700 dark:text-midnight-300">
                      <strong>Deliverables:</strong> {phase.deliverables.join(' • ')}
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Commit Actions */}
            <div className="flex items-center justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setStep(1)}>
                Back to Edit
              </Button>
              <Button
                disabled={committing}
                onClick={handleCommitProject}
                className="bg-amber-600 hover:bg-amber-700 text-ivory-50 gap-2"
              >
                {committing ? 'Creating Project...' : 'Commit & Create Project'}
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  )
}

export default function NewProjectPage() {
  return (
    <AuthGuard>
      <NewProjectContent />
    </AuthGuard>
  )
}
