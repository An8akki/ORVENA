'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'
import {
  Rocket,
  ArrowLeft,
  CheckCircle2,
  Circle,
  Clock,
  AlertCircle,
  Plus,
  Trash2,
  Award,
  Layers,
  Sparkles,
  Share2,
  ExternalLink,
  ChevronRight,
  ShieldCheck,
  TrendingUp,
  FileText,
  Copy,
  Check,
} from 'lucide-react'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { api } from '@/lib/api-client'
import { showNotification } from '@/lib/notifications'
import { cn } from '@/lib/utils'

interface Milestone {
  id: string
  title: string
  description?: string
  phase: string
  sequence_order: number
  status: 'not_started' | 'in_progress' | 'blocked' | 'completed'
  target_date?: string
  deliverables?: string[]
  completed_at?: string
  blocker_notes?: string
}

interface DimensionScore {
  dimension_name: string
  score: number
  max_score: number
  status_label: string
  level: number
  feedback: string
  evidence_provided: boolean
}

interface EvaluationResult {
  overall_score: number
  overall_rating: string
  dimension_scores: Record<string, DimensionScore>
  strengths: string[]
  missing_evidence: string[]
  improvement_priorities: string[]
  recommended_milestone: string
  reassessment_conditions: string
  summary: string
}

interface Pathway {
  pathway_key: string
  title: string
  score: number
  tier: string
  summary_rationale: string
  readiness_factors: string[]
  missing_evidence: string[]
  action_checklist: string[]
  suggested_milestones: { title: string; phase: string; description: string; deliverables: string[] }[]
}

interface ProjectDetail {
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
  weekly_hours?: number
  estimated_duration_weeks?: number
  completion_percentage: number
  github_url?: string
  demo_url?: string
  milestones: Milestone[]
  latest_assessment?: any
  latest_outcome?: any
  showcase_slug?: string
  showcase_public: boolean
}

const EVALUATION_QUESTIONS = [
  {
    key: 'problem_clarity',
    title: '1. Problem Clarity & Relevance',
    options: [
      { level: 0, text: 'Vague / Undefined (Generic idea without identified users)' },
      { level: 1, text: 'Basic Identification (Broad topic identified, but lacks specific user pain points)' },
      { level: 2, text: 'Defined & Relevant (Clear pain point and specific user demographic defined)' },
      { level: 3, text: 'Well-Researched (Backed by user interviews or domain literature)' },
      { level: 4, text: 'Exemplary (Quantified friction metrics and explicit success criteria)' },
    ],
  },
  {
    key: 'implementation_maturity',
    title: '2. Implementation Maturity',
    options: [
      { level: 0, text: 'Concept Only (Wireframes or non-functional mocks)' },
      { level: 1, text: 'Early Prototype (Minimal skeleton codebase with placeholder responses)' },
      { level: 2, text: 'Working MVP (Core user workflows execute end-to-end with persistent storage)' },
      { level: 3, text: 'Hardened System (Modular architecture with error boundaries and async tasks)' },
      { level: 4, text: 'Production-Grade (Fully containerized, optimized queries, security controls)' },
    ],
  },
  {
    key: 'testing_validation',
    title: '3. Testing & Evidence of Validation',
    options: [
      { level: 0, text: 'No Formal Verification (Untested or purely ad-hoc manual clicks)' },
      { level: 1, text: 'Manual Sanity Checks (Basic happy paths verified manually)' },
      { level: 2, text: 'Basic Unit Testing (Automated unit tests for core calculation functions)' },
      { level: 3, text: 'Integration & Edge Coverage (Automated suite testing boundary cases and transactions)' },
      { level: 4, text: 'Comprehensive Verification (Rigorous test coverage, load benchmarks, user trial data)' },
    ],
  },
  {
    key: 'differentiation',
    title: '4. Differentiation & Technical Substance',
    options: [
      { level: 0, text: 'Generic Clone (Direct tutorial replication with minimal changes)' },
      { level: 1, text: 'Minor Customization (Standard CRUD boilerplate with custom styling)' },
      { level: 2, text: 'Distinct Adaptation (Established tools applied to a tailored domain challenge)' },
      { level: 3, text: 'Substantial Innovation (Novel tool combinations, unique algorithms, or superior UX)' },
      { level: 4, text: 'High Novelty (Exemplary technical innovation or potential publication candidate)' },
    ],
  },
  {
    key: 'documentation_readiness',
    title: '5. Documentation, Usability & Readiness',
    options: [
      { level: 0, text: 'Minimal Documentation (No setup steps, comments, or demo)' },
      { level: 1, text: 'Basic README (Simple setup steps without architecture overview)' },
      { level: 2, text: 'Good Technical Overview (Clear installation, architecture spec, schema docs)' },
      { level: 3, text: 'Showcase-Ready (Live demo link, clean docker config, contribution guide)' },
      { level: 4, text: 'Exemplary Portfolio Standard (Interactive Swagger docs, live demo, video walkthrough)' },
    ],
  },
]

function ProjectWorkspaceContent() {
  const params = useParams()
  const router = useRouter()
  const projectId = params.projectId as string

  const [project, setProject] = useState<ProjectDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'milestones' | 'evaluate' | 'outcomes' | 'showcase'>('milestones')

  // Milestone Form Modal
  const [newMilestoneTitle, setNewMilestoneTitle] = useState('')
  const [newMilestonePhase, setNewMilestonePhase] = useState('Implementation')
  const [showAddMilestone, setShowAddMilestone] = useState(false)

  // Evaluation Form State
  const [evalAnswers, setEvalAnswers] = useState<Record<string, number>>({
    problem_clarity: 2,
    implementation_maturity: 2,
    testing_validation: 1,
    differentiation: 2,
    documentation_readiness: 2,
  })
  const [evaluating, setEvaluating] = useState(false)
  const [evalResult, setEvalResult] = useState<EvaluationResult | null>(null)

  // Outcome Intelligence State
  const [analyzingOutcomes, setAnalyzingOutcomes] = useState(false)
  const [pathways, setPathways] = useState<Pathway[]>([])
  const [outcomeSummary, setOutcomeSummary] = useState('')
  const [applyingPathway, setApplyingPathway] = useState<string | null>(null)

  // Showcase State
  const [showcasePublic, setShowcasePublic] = useState(false)
  const [showcaseHeadline, setShowcaseHeadline] = useState('')
  const [showcaseSlug, setShowcaseSlug] = useState('')
  const [copiedLink, setCopiedLink] = useState(false)

  useEffect(() => {
    loadProject()
  }, [projectId])

  const loadProject = async () => {
    try {
      setLoading(true)
      const data = await api.get<ProjectDetail>(`/api/v1/launchpad/projects/${projectId}`)
      setProject(data)
      setShowcasePublic(data.showcase_public || false)
      setShowcaseSlug(data.showcase_slug || '')
    } catch (err: any) {
      showNotification(err.message || 'Failed to load project', 'error')
      router.push('/projects')
    } finally {
      setLoading(false)
    }
  }

  // Milestone Operations
  const handleToggleMilestone = async (m: Milestone) => {
    const nextStatus = m.status === 'completed' ? 'in_progress' : 'completed'
    try {
      await api.patch(`/api/v1/launchpad/projects/${projectId}/milestones/${m.id}`, {
        status: nextStatus,
      })
      await loadProject()
    } catch (err: any) {
      showNotification(err.message || 'Failed to update milestone', 'error')
    }
  }

  const handleAddMilestone = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMilestoneTitle.trim()) return

    try {
      await api.post(`/api/v1/launchpad/projects/${projectId}/milestones`, {
        title: newMilestoneTitle,
        phase: newMilestonePhase,
        sequence_order: (project?.milestones.length || 0) + 1,
      })
      setNewMilestoneTitle('')
      setShowAddMilestone(false)
      await loadProject()
    } catch (err: any) {
      showNotification(err.message || 'Failed to add milestone', 'error')
    }
  }

  const handleDeleteMilestone = async (mId: string) => {
    if (!confirm('Delete this milestone?')) return
    try {
      await api.delete(`/api/v1/launchpad/projects/${projectId}/milestones/${mId}`)
      await loadProject()
    } catch (err: any) {
      showNotification(err.message || 'Failed to delete milestone', 'error')
    }
  }

  // Evaluation Operations
  const handleRunEvaluation = async () => {
    try {
      setEvaluating(true)
      const answersList = Object.entries(evalAnswers).map(([k, v]) => ({
        dimension_key: k,
        selected_option_level: v,
      }))

      const res = await api.post<EvaluationResult>(
        `/api/v1/launchpad/projects/${projectId}/evaluate`,
        {
          answers: answersList,
          repository_url: project?.github_url,
          demo_url: project?.demo_url,
        }
      )
      setEvalResult(res)
    } catch (err: any) {
      showNotification(err.message || 'Evaluation failed', 'error')
    } finally {
      setEvaluating(false)
    }
  }

  // Outcome Intelligence Operations
  const handleRunOutcomes = async () => {
    try {
      setAnalyzingOutcomes(true)
      const res = await api.post<any>(
        `/api/v1/launchpad/projects/${projectId}/outcome-intelligence`,
        {}
      )
      setPathways(res.pathways || [])
      setOutcomeSummary(res.readiness_summary || '')
    } catch (err: any) {
      showNotification(err.message || 'Outcome intelligence analysis failed', 'error')
    } finally {
      setAnalyzingOutcomes(false)
    }
  }

  const handleApplyPathway = async (pathwayKey: string) => {
    if (!confirm('Convert this pathway into active project milestone tasks?')) return
    try {
      setApplyingPathway(pathwayKey)
      await api.post(`/api/v1/launchpad/projects/${projectId}/apply-pathway-milestones`, {
        pathway_key: pathwayKey,
        replace_existing_milestones: false,
      })
      await loadProject()
      setActiveTab('milestones')
      showNotification('Pathway milestones successfully added to your project!', 'success')
    } catch (err: any) {
      showNotification(err.message || 'Failed to apply pathway milestones', 'error')
    } finally {
      setApplyingPathway(null)
    }
  }

  // Showcase Operations
  const handleSaveShowcase = async () => {
    try {
      await api.put(`/api/v1/launchpad/projects/${projectId}/showcase`, {
        is_public: showcasePublic,
        headline: showcaseHeadline || project?.title,
      })
      await loadProject()
      showNotification('Showcase settings saved!', 'success')
    } catch (err: any) {
      showNotification(err.message || 'Failed to save showcase', 'error')
    }
  }

  const handleCopyShowcaseUrl = () => {
    const url = `${window.location.origin}/projects/showcase/${showcaseSlug}`
    navigator.clipboard.writeText(url)
    setCopiedLink(true)
    setTimeout(() => setCopiedLink(false), 2000)
  }

  if (loading || !project) {
    return (
      <AppLayout>
        <div className="container py-12 max-w-6xl mx-auto px-4 text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-amber-600 border-t-transparent mx-auto mb-3" />
          <p className="text-xs text-midnight-500">Loading project workspace...</p>
        </div>
      </AppLayout>
    )
  }

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
          <span className="text-midnight-900 dark:text-ivory-50 font-medium truncate max-w-xs">{project.title}</span>
        </div>

        {/* Project Header Banner */}
        <div className="mb-6 rounded-2xl border border-midnight-200 dark:border-midnight-800 bg-white dark:bg-midnight-900/60 p-6 shadow-sm">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div className="space-y-2 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded-md bg-midnight-100 dark:bg-midnight-800 px-2 py-0.5 text-xs font-medium text-midnight-700 dark:text-midnight-300 capitalize">
                  {project.domain || 'Engineering'}
                </span>
                <span className="rounded-full bg-amber-500/10 text-amber-700 dark:text-amber-400 px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider">
                  {project.stage || 'In Progress'}
                </span>
                {project.github_url && (
                  <a
                    href={project.github_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-midnight-500 hover:text-midnight-900 dark:hover:text-ivory-50"
                  >
                    <ExternalLink className="h-3 w-3" />
                    Repository
                  </a>
                )}
                {project.demo_url && (
                  <a
                    href={project.demo_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-amber-600 hover:underline"
                  >
                    <ExternalLink className="h-3 w-3" />
                    Live Demo
                  </a>
                )}
              </div>

              <h1 className="font-display text-2xl font-bold text-midnight-950 dark:text-ivory-50">
                {project.title}
              </h1>

              <p className="text-xs text-midnight-600 dark:text-midnight-300 max-w-3xl leading-relaxed">
                {project.description}
              </p>

              <div className="flex flex-wrap gap-1.5 pt-1">
                {project.technologies.map((t) => (
                  <span
                    key={t}
                    className="rounded-md border border-midnight-200 dark:border-midnight-800 bg-midnight-50 dark:bg-midnight-950 px-2 py-0.5 text-[10px] text-midnight-700 dark:text-midnight-300"
                  >
                    {t}
                  </span>
                ))}
              </div>
            </div>

            {/* Progress Badge */}
            <div className="flex flex-col items-end min-w-[140px] pt-1">
              <div className="text-xs text-midnight-500 font-medium mb-1">Completion</div>
              <div className="text-2xl font-bold text-amber-600 dark:text-amber-400">
                {project.completion_percentage}%
              </div>
              <div className="h-2 w-32 rounded-full bg-midnight-100 dark:bg-midnight-800 overflow-hidden mt-1">
                <div
                  className="h-full rounded-full bg-amber-500 transition-all duration-500"
                  style={{ width: `${project.completion_percentage}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Workspace Navigation Tabs */}
        <div className="mb-6 flex border-b border-midnight-200 dark:border-midnight-800 overflow-x-auto gap-1">
          <button
            type="button"
            onClick={() => setActiveTab('milestones')}
            className={cn(
              'flex items-center gap-2 border-b-2 px-4 py-2.5 text-xs font-semibold whitespace-nowrap transition-colors',
              activeTab === 'milestones'
                ? 'border-amber-600 text-amber-600 dark:border-amber-400 dark:text-amber-400'
                : 'border-transparent text-midnight-500 hover:text-midnight-900 dark:hover:text-ivory-50'
            )}
          >
            <Clock className="h-4 w-4" />
            Milestones & Tasks ({project.milestones.length})
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('evaluate')}
            className={cn(
              'flex items-center gap-2 border-b-2 px-4 py-2.5 text-xs font-semibold whitespace-nowrap transition-colors',
              activeTab === 'evaluate'
                ? 'border-amber-600 text-amber-600 dark:border-amber-400 dark:text-amber-400'
                : 'border-transparent text-midnight-500 hover:text-midnight-900 dark:hover:text-ivory-50'
            )}
          >
            <ShieldCheck className="h-4 w-4" />
            5-Dimension Evaluation
          </button>

          <button
            type="button"
            onClick={() => {
              setActiveTab('outcomes')
              if (pathways.length === 0) handleRunOutcomes()
            }}
            className={cn(
              'flex items-center gap-2 border-b-2 px-4 py-2.5 text-xs font-semibold whitespace-nowrap transition-colors',
              activeTab === 'outcomes'
                ? 'border-amber-600 text-amber-600 dark:border-amber-400 dark:text-amber-400'
                : 'border-transparent text-midnight-500 hover:text-midnight-900 dark:hover:text-ivory-50'
            )}
          >
            <TrendingUp className="h-4 w-4" />
            Outcome Intelligence (6 Pathways)
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('showcase')}
            className={cn(
              'flex items-center gap-2 border-b-2 px-4 py-2.5 text-xs font-semibold whitespace-nowrap transition-colors',
              activeTab === 'showcase'
                ? 'border-amber-600 text-amber-600 dark:border-amber-400 dark:text-amber-400'
                : 'border-transparent text-midnight-500 hover:text-midnight-900 dark:hover:text-ivory-50'
            )}
          >
            <Share2 className="h-4 w-4" />
            Project Showcase
          </button>
        </div>

        {/* TAB 1: MILESTONES & TASKS */}
        {activeTab === 'milestones' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-display font-semibold text-base text-midnight-950 dark:text-ivory-50">
                  Execution Milestones
                </h3>
                <p className="text-xs text-midnight-500">
                  Click the checkmark to mark milestone completed and update project readiness
                </p>
              </div>

              <Button
                size="sm"
                onClick={() => setShowAddMilestone(!showAddMilestone)}
                className="bg-amber-600 hover:bg-amber-700 text-ivory-50 gap-1.5 text-xs"
              >
                <Plus className="h-3.5 w-3.5" />
                Add Milestone
              </Button>
            </div>

            {/* Add Milestone Form */}
            {showAddMilestone && (
              <Card className="border-amber-500/30 bg-amber-500/5 p-4 animate-in fade-in duration-150">
                <form onSubmit={handleAddMilestone} className="space-y-3">
                  <div className="grid gap-3 sm:grid-cols-3">
                    <div className="sm:col-span-2">
                      <label className="block text-[11px] font-semibold text-midnight-700 dark:text-midnight-300 mb-1">
                        Milestone Title
                      </label>
                      <input
                        type="text"
                        required
                        value={newMilestoneTitle}
                        onChange={(e) => setNewMilestoneTitle(e.target.value)}
                        placeholder="e.g. Implement JWT authentication & role-based middleware"
                        className="w-full rounded-lg border border-midnight-200 dark:border-midnight-700 bg-white dark:bg-midnight-950 px-3 py-1.5 text-xs text-midnight-950 dark:text-ivory-50 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-midnight-700 dark:text-midnight-300 mb-1">
                        Phase
                      </label>
                      <select
                        value={newMilestonePhase}
                        onChange={(e) => setNewMilestonePhase(e.target.value)}
                        className="w-full rounded-lg border border-midnight-200 dark:border-midnight-700 bg-white dark:bg-midnight-950 px-3 py-1.5 text-xs text-midnight-950 dark:text-ivory-50 focus:outline-none"
                      >
                        <option value="Architecture & Design">Architecture & Design</option>
                        <option value="Core Implementation">Core Implementation</option>
                        <option value="Testing & Verification">Testing & Verification</option>
                        <option value="Documentation & Deployment">Documentation & Deployment</option>
                        <option value="Outcome Next Steps">Outcome Next Steps</option>
                      </select>
                    </div>
                  </div>
                  <div className="flex justify-end gap-2 pt-1">
                    <Button size="sm" variant="ghost" onClick={() => setShowAddMilestone(false)}>
                      Cancel
                    </Button>
                    <Button size="sm" type="submit" className="bg-amber-600 hover:bg-amber-700 text-ivory-50">
                      Save Milestone
                    </Button>
                  </div>
                </form>
              </Card>
            )}

            {/* Milestones List */}
            {project.milestones.length === 0 ? (
              <Card className="p-8 text-center border-dashed">
                <p className="text-xs text-midnight-500 mb-3">No milestones created yet.</p>
                <Button size="sm" onClick={() => setShowAddMilestone(true)} variant="outline">
                  Create First Milestone
                </Button>
              </Card>
            ) : (
              <div className="space-y-3">
                {project.milestones.map((m) => (
                  <div
                    key={m.id}
                    className={cn(
                      'flex items-start justify-between rounded-xl border p-4 transition-all shadow-sm',
                      m.status === 'completed'
                        ? 'border-emerald-500/30 bg-emerald-500/5'
                        : 'border-midnight-200 dark:border-midnight-800 bg-white dark:bg-midnight-900/60'
                    )}
                  >
                    <div className="flex items-start gap-3">
                      <button
                        type="button"
                        onClick={() => handleToggleMilestone(m)}
                        className="mt-0.5 text-midnight-400 hover:text-emerald-500 transition-colors"
                      >
                        {m.status === 'completed' ? (
                          <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                        ) : (
                          <Circle className="h-5 w-5 text-midnight-400" />
                        )}
                      </button>

                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold text-midnight-950 dark:text-ivory-50">
                            {m.title}
                          </span>
                          <span className="rounded-md bg-midnight-100 dark:bg-midnight-800 px-1.5 py-0.5 text-[9px] font-medium text-midnight-600 dark:text-midnight-400">
                            {m.phase}
                          </span>
                        </div>
                        {m.description && (
                          <p className="text-xs text-midnight-500 mt-1">{m.description}</p>
                        )}
                        {m.deliverables && m.deliverables.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2 text-[10px] text-midnight-400">
                            <strong>Deliverables:</strong> {m.deliverables.join(', ')}
                          </div>
                        )}
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => handleDeleteMilestone(m.id)}
                      className="text-midnight-400 hover:text-rose-500 p-1 transition-colors"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 2: 5-DIMENSION EVALUATION */}
        {activeTab === 'evaluate' && (
          <div className="space-y-8">
            <div className="rounded-xl border border-midnight-200 dark:border-midnight-800 bg-midnight-50 dark:bg-midnight-900/40 p-4 text-xs text-midnight-600 dark:text-midnight-300">
              <strong>About this evaluation:</strong> Preliminary, rubric-based evaluation scoring across 5 software engineering dimensions.
              Operates deterministically without an LLM. Handles unanswered questions as neutral unknown states.
            </div>

            {/* Rubric Questionnaire */}
            <div className="space-y-6">
              {EVALUATION_QUESTIONS.map((q) => (
                <Card key={q.key} className="border-midnight-200 dark:border-midnight-800 p-5">
                  <h4 className="font-display font-semibold text-sm text-midnight-950 dark:text-ivory-50 mb-3">
                    {q.title}
                  </h4>
                  <div className="space-y-2">
                    {q.options.map((opt) => (
                      <label
                        key={opt.level}
                        className={cn(
                          'flex items-center gap-3 rounded-lg border p-3 text-xs cursor-pointer transition-all',
                          evalAnswers[q.key] === opt.level
                            ? 'border-amber-500 bg-amber-500/10 text-amber-950 dark:text-amber-100 font-medium'
                            : 'border-midnight-200 dark:border-midnight-800 hover:bg-midnight-100 dark:hover:bg-midnight-800/50'
                        )}
                      >
                        <input
                          type="radio"
                          name={q.key}
                          value={opt.level}
                          checked={evalAnswers[q.key] === opt.level}
                          onChange={() => setEvalAnswers((prev) => ({ ...prev, [q.key]: opt.level }))}
                          className="accent-amber-600"
                        />
                        <span>{opt.text}</span>
                      </label>
                    ))}
                  </div>
                </Card>
              ))}

              <div className="flex justify-end">
                <Button
                  disabled={evaluating}
                  onClick={handleRunEvaluation}
                  className="bg-amber-600 hover:bg-amber-700 text-ivory-50 gap-2"
                >
                  <Sparkles className="h-4 w-4" />
                  {evaluating ? 'Evaluating Project...' : 'Run 5-Dimension Assessment'}
                </Button>
              </div>
            </div>

            {/* Evaluation Results Card */}
            {evalResult && (
              <Card className="border-amber-500/40 bg-amber-500/5 p-6 animate-in fade-in duration-200 space-y-6">
                <div className="flex items-center justify-between border-b border-amber-500/20 pb-4">
                  <div>
                    <span className="text-xs uppercase tracking-wider font-semibold text-amber-700 dark:text-amber-400">
                      Assessment Results
                    </span>
                    <h3 className="text-xl font-display font-bold text-midnight-950 dark:text-ivory-50">
                      {evalResult.overall_rating}
                    </h3>
                  </div>
                  <div className="text-right">
                    <span className="text-3xl font-bold text-amber-600 dark:text-amber-400">
                      {evalResult.overall_score}
                    </span>
                    <span className="text-xs text-midnight-500"> / 100</span>
                  </div>
                </div>

                {/* Dimension Breakdown */}
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
                  {Object.entries(evalResult.dimension_scores).map(([k, ds]) => (
                    <div key={k} className="rounded-xl border border-midnight-200 dark:border-midnight-800 bg-white dark:bg-midnight-900 p-3">
                      <div className="text-[10px] text-midnight-400 font-semibold uppercase">{ds.dimension_name}</div>
                      <div className="text-base font-bold text-midnight-900 dark:text-ivory-50 mt-1">
                        {ds.score} <span className="text-[10px] font-normal text-midnight-400">/ 20</span>
                      </div>
                      <div className="text-[10px] text-amber-600 dark:text-amber-400 mt-0.5">{ds.status_label}</div>
                    </div>
                  ))}
                </div>

                {/* Strengths & Priorities */}
                <div className="grid gap-5 md:grid-cols-2 text-xs">
                  <div>
                    <h4 className="font-semibold text-emerald-600 mb-2 flex items-center gap-1.5">
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      Identified Strengths
                    </h4>
                    <ul className="space-y-1 text-midnight-600 dark:text-midnight-300">
                      {evalResult.strengths.map((s, i) => (
                        <li key={i}>• {s}</li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-semibold text-amber-700 dark:text-amber-400 mb-2 flex items-center gap-1.5">
                      <AlertCircle className="h-3.5 w-3.5" />
                      Improvement Priorities
                    </h4>
                    <ul className="space-y-1 text-midnight-600 dark:text-midnight-300">
                      {evalResult.improvement_priorities.map((p, i) => (
                        <li key={i}>• {p}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="rounded-xl bg-midnight-900/60 border border-midnight-800 p-3 text-xs text-midnight-300">
                  <strong>Recommended Next Milestone:</strong> {evalResult.recommended_milestone}
                </div>
              </Card>
            )}
          </div>
        )}

        {/* TAB 3: OUTCOME INTELLIGENCE */}
        {activeTab === 'outcomes' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-display font-semibold text-base text-midnight-950 dark:text-ivory-50">
                  Strategic Outcome Intelligence
                </h3>
                <p className="text-xs text-midnight-500">
                  Evaluates readiness for Product Development, Research Papers, Startups, Competitions & Portfolio
                </p>
              </div>

              <Button
                size="sm"
                disabled={analyzingOutcomes}
                onClick={handleRunOutcomes}
                className="bg-amber-600 hover:bg-amber-700 text-ivory-50 gap-1.5 text-xs"
              >
                <Sparkles className="h-3.5 w-3.5" />
                {analyzingOutcomes ? 'Analyzing...' : 'Re-evaluate Pathways'}
              </Button>
            </div>

            {outcomeSummary && (
              <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-xs text-amber-900 dark:text-amber-200">
                {outcomeSummary}
              </div>
            )}

            {pathways.length === 0 ? (
              <div className="h-48 rounded-xl border border-midnight-200 dark:border-midnight-800 bg-midnight-900/10 animate-pulse" />
            ) : (
              <div className="grid gap-5 md:grid-cols-2">
                {pathways.map((p) => (
                  <Card key={p.pathway_key} className="flex flex-col justify-between border-midnight-200 dark:border-midnight-800 p-5">
                    <div className="space-y-3">
                      <div className="flex items-start justify-between">
                        <div>
                          <span
                            className={cn(
                              'inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider',
                              p.tier === 'Ready'
                                ? 'bg-emerald-500/10 text-emerald-600'
                                : p.tier === 'Near-Ready'
                                ? 'bg-amber-500/10 text-amber-600'
                                : 'bg-midnight-100 dark:bg-midnight-800 text-midnight-500'
                            )}
                          >
                            {p.tier}
                          </span>
                          <h4 className="font-display font-semibold text-base text-midnight-950 dark:text-ivory-50 mt-1">
                            {p.title}
                          </h4>
                        </div>
                        <span className="text-lg font-bold text-amber-600 dark:text-amber-400">
                          {p.score}%
                        </span>
                      </div>

                      <p className="text-xs text-midnight-600 dark:text-midnight-300 leading-relaxed">
                        {p.summary_rationale}
                      </p>

                      <div>
                        <div className="text-[10px] uppercase font-semibold text-midnight-400 mb-1">
                          Action Checklist
                        </div>
                        <ul className="text-xs text-midnight-600 dark:text-midnight-300 space-y-1">
                          {p.action_checklist.slice(0, 3).map((act, i) => (
                            <li key={i} className="flex items-start gap-1.5">
                              <span className="text-amber-500 font-bold">•</span>
                              <span className="line-clamp-1">{act}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    <div className="pt-4 mt-4 border-t border-midnight-100 dark:border-midnight-800 flex justify-end">
                      <Button
                        size="sm"
                        disabled={applyingPathway === p.pathway_key}
                        onClick={() => handleApplyPathway(p.pathway_key)}
                        className="bg-amber-600 hover:bg-amber-700 text-ivory-50 text-xs gap-1.5"
                      >
                        <Plus className="h-3.5 w-3.5" />
                        {applyingPathway === p.pathway_key ? 'Applying...' : 'Apply Pathway Milestones'}
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 4: SHOWCASE */}
        {activeTab === 'showcase' && (
          <div className="max-w-2xl mx-auto space-y-6">
            <Card className="border-midnight-200 dark:border-midnight-800 p-6 space-y-5">
              <div>
                <h3 className="font-display font-semibold text-lg text-midnight-950 dark:text-ivory-50">
                  Project Portfolio Showcase
                </h3>
                <p className="text-xs text-midnight-500 mt-0.5">
                  Generate a shareable public portfolio page to showcase your project to recruiters and judges.
                </p>
              </div>

              {/* Visibility Switch */}
              <div className="flex items-center justify-between rounded-xl border border-midnight-200 dark:border-midnight-800 bg-midnight-50 dark:bg-midnight-950 p-4">
                <div>
                  <div className="text-xs font-semibold text-midnight-900 dark:text-ivory-50">Public Visibility</div>
                  <div className="text-[11px] text-midnight-500">
                    {showcasePublic ? 'Anyone with the link can view your showcase' : 'Private (Only you can view)'}
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={showcasePublic}
                  onChange={(e) => setShowcasePublic(e.target.checked)}
                  className="h-5 w-5 accent-amber-600 rounded cursor-pointer"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-midnight-700 dark:text-midnight-300 mb-1">
                  Showcase Headline
                </label>
                <input
                  type="text"
                  value={showcaseHeadline}
                  onChange={(e) => setShowcaseHeadline(e.target.value)}
                  placeholder={`e.g. ${project.title} - High Performance System`}
                  className="w-full rounded-xl border border-midnight-200 dark:border-midnight-700 bg-midnight-50 dark:bg-midnight-950 px-3.5 py-2 text-xs text-midnight-950 dark:text-ivory-50 focus:outline-none"
                />
              </div>

              {/* Shareable Link Box */}
              {showcaseSlug && (
                <div className="rounded-xl border border-midnight-200 dark:border-midnight-800 bg-midnight-900/40 p-3.5 space-y-2">
                  <span className="text-[11px] font-semibold text-midnight-400">Shareable URL</span>
                  <div className="flex items-center gap-2">
                    <input
                      readOnly
                      value={`${typeof window !== 'undefined' ? window.location.origin : ''}/projects/showcase/${showcaseSlug}`}
                      className="flex-1 rounded-lg border border-midnight-800 bg-midnight-950 px-3 py-1.5 text-xs text-midnight-300"
                    />
                    <Button size="sm" variant="outline" onClick={handleCopyShowcaseUrl} className="gap-1.5 text-xs">
                      {copiedLink ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
                      {copiedLink ? 'Copied' : 'Copy'}
                    </Button>
                  </div>
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-2">
                {showcaseSlug && (
                  <Link href={`/projects/showcase/${showcaseSlug}`} target="_blank">
                    <Button size="sm" variant="outline" className="gap-1.5 text-xs">
                      <ExternalLink className="h-3.5 w-3.5" />
                      Preview Showcase
                    </Button>
                  </Link>
                )}
                <Button size="sm" onClick={handleSaveShowcase} className="bg-amber-600 hover:bg-amber-700 text-ivory-50 text-xs">
                  Save Settings
                </Button>
              </div>
            </Card>
          </div>
        )}
      </div>
    </AppLayout>
  )
}

export default function ProjectWorkspacePage() {
  return (
    <AuthGuard>
      <ProjectWorkspaceContent />
    </AuthGuard>
  )
}
