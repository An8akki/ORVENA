'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  Map, 
  CheckCircle2, 
  Clock, 
  Target,
  BookOpen,
  ArrowLeft,
  Download,
  Plus,
  TrendingUp,
  Sparkles,
  Check,
  ChevronRight
} from 'lucide-react'
import { api } from '@/lib/api-client'

interface Milestone {
  id: string
  title: string
  description: string
  focusTopics: string
  weekLabel: string
  work: string
  practice: string
  deliverable: string
  projectDepth: string[]
  projectTheme: string
  personalization: string
  status: 'completed' | 'current' | 'upcoming' | 'locked'
  estimatedDuration: string
  skills: string[]
  resources: Array<{
    title: string
    type: 'course' | 'article' | 'video' | 'project'
    url: string
  }>
  order: number
  progress: number
  completedDate?: string
}

interface Roadmap {
  id: string
  title: string
  description: string
  targetRole: string
  totalMilestones: number
  completedMilestones: number
  overallProgress: number
  estimatedCompletion: string
  milestones: Milestone[]
}

export default function RoadmapPage() {
  const router = useRouter()
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [generatingRoadmap, setGeneratingRoadmap] = useState(false)
  const [updatingMilestoneId, setUpdatingMilestoneId] = useState<string | null>(null)
  const [activeMilestoneId, setActiveMilestoneId] = useState<string | null>(null)
  const activeMilestone = roadmap?.milestones.find((milestone) => milestone.id === activeMilestoneId)
    || roadmap?.milestones.find((milestone) => milestone.status === 'current')
    || roadmap?.milestones[0]

  useEffect(() => {
    loadRoadmap()
    // The page loads the signed-in user's roadmap once when this route mounts.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const loadRoadmap = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const roadmaps = await api.get<any[]>('/api/v1/career/roadmaps')
      const requestedId = new URLSearchParams(window.location.search).get('roadmap')
      const selected = (requestedId && roadmaps.find((item) => item.id === requestedId)) || roadmaps[0]
      if (selected && ((selected.milestones?.length || 0) < 6 || !selected.description?.includes('[plan-v2]'))) {
        // Upgrade older text-heavy plans to the current visual phase plan.
        // Carry completed phases forward so users keep their progress.
        const upgraded = await api.post<any>('/api/v1/career/roadmaps', {
          career_goal_id: selected.career_goal_id,
          recommendation_id: selected.recommendation_id,
          title: selected.title,
          target_duration_weeks: Math.max(12, selected.target_duration_weeks || 12),
        })
        const completedOrders = (selected.milestones || [])
          .filter((milestone: any) => milestone.status === 'completed')
          .map((milestone: any) => milestone.sequence_number || Number(milestone.title?.match(/Phase\s+(\d+)/i)?.[1]))
          .filter((order: number) => Number.isFinite(order))
          .sort((a: number, b: number) => a - b)
        const upgradedMilestones = [...(upgraded.milestones || [])].sort(
          (a: any, b: any) => (a.sequence_number || 0) - (b.sequence_number || 0)
        )
        for (const order of completedOrders) {
          const milestone = upgradedMilestones.find((item: any) => item.sequence_number === order)
          if (milestone) {
            await api.patch(`/api/v1/career/roadmaps/milestones/${milestone.id}`, { status: 'completed' })
          }
        }
        const refreshedRoadmaps = await api.get<any[]>('/api/v1/career/roadmaps')
        const refreshed = refreshedRoadmaps.find((item) => item.id === upgraded.id) || upgraded
        const formatted = formatRoadmapData(refreshed)
        setRoadmap(formatted)
        setActiveMilestoneId(formatted.milestones.find((item) => item.status === 'current')?.id || formatted.milestones[0]?.id || null)
        router.replace(`/roadmap?roadmap=${upgraded.id}`)
      } else {
        const formatted = selected ? formatRoadmapData(selected) : null
        setRoadmap(formatted)
        setActiveMilestoneId(formatted?.milestones.find((item) => item.status === 'current')?.id || formatted?.milestones[0]?.id || null)
      }
    } catch (err: any) {
      console.error('Failed to load roadmap:', err)
      setError(err.message || 'Failed to load your roadmap')
      setRoadmap(null)
    } finally {
      setLoading(false)
    }
  }

  const formatRoadmapData = (data: any): Roadmap => {
    // Format backend data to match frontend interface
    return {
      id: data.id || data.roadmap_id,
      title: data.title || 'Your Career Roadmap',
      description: (data.description || '').replace('[plan-v2]', '').trim(),
      targetRole: data.target_role?.name || data.role_name || data.title?.replace(/^(Path to|Roadmap to)\s*/, '') || 'Software Engineer',
      totalMilestones: data.milestones?.length || 0,
      completedMilestones: data.milestones?.filter((m: any) => m.status === 'completed').length || 0,
      overallProgress: data.progress_percentage ?? data.overall_progress ?? 0,
      estimatedCompletion: data.estimated_completion || formatEstimatedCompletion(data),
      milestones: [...(data.milestones || [])]
        .sort((a: any, b: any) => (a.sequence_number || a.order || 0) - (b.sequence_number || b.order || 0))
        .map((m: any, index: number) => {
        const description = m.description || ''
        const readSection = (label: string, endings: string[]) => {
          const start = description.indexOf(`${label}:`)
          if (start < 0) return ''
          const contentStart = start + label.length + 1
          const end = endings.map((ending) => description.indexOf(`\n${ending}:`, contentStart))
            .filter((position) => position >= 0)
            .reduce((nearest, position) => Math.min(nearest, position), description.length)
          return description.slice(contentStart, end).trim()
        }
        const weekRange = description.match(/Weeks\s+(\d+)\s*[\u2013\u2014-]\s*(\d+)/i)
        const projectDepth = readSection('Project depth checklist', ['Project theme'])
        return {
        id: m.id || m.milestone_id,
        title: m.title,
        description,
        focusTopics: readSection('Focus topics', ['Work', 'Practice', 'Personalization', 'Deliverable', 'Project depth checklist', 'Project theme']),
        weekLabel: weekRange ? `Weeks ${weekRange[1]}-${weekRange[2]}` : `Phase ${index + 1}`,
        work: readSection('Work', ['Practice', 'Personalization', 'Deliverable', 'Project depth checklist', 'Project theme']),
        practice: readSection('Practice', ['Personalization', 'Deliverable', 'Project depth checklist', 'Project theme']),
        deliverable: readSection('Deliverable', ['Project depth checklist', 'Project theme']),
        projectDepth: projectDepth ? projectDepth.split(';').map((item: string) => item.trim()).filter(Boolean) : [],
        projectTheme: readSection('Project theme', []),
        personalization: readSection('Personalization', ['Deliverable', 'Project depth checklist', 'Project theme']),
        status: mapMilestoneStatus(m.status, index),
        estimatedDuration: m.estimated_duration || `${m.estimated_hours || 10} hours`,
        skills: m.skills || m.topics || [],
        resources: (m.resources || []).map((resource: any) => typeof resource === 'string'
          ? { title: resource, type: 'article', url: /^https?:\/\//.test(resource) ? resource : '#' }
          : resource),
        order: m.order || m.sequence_number || index + 1,
        progress: m.progress || (m.status === 'completed' ? 100 : m.status === 'current' ? 50 : 0),
        completedDate: m.completed_date
      }}
      )
    }
  }

  const mapMilestoneStatus = (status: string, index: number): 'completed' | 'current' | 'upcoming' | 'locked' => {
    if (status === 'completed' || status === 'COMPLETED') return 'completed'
    if (status === 'in_progress' || status === 'IN_PROGRESS' || status === 'CURRENT') return 'current'
    if (index === 0) return 'current' // First milestone is always current if not completed
    return 'upcoming'
  }

  const formatEstimatedCompletion = (data: any): string => {
    if (data.target_duration_weeks) {
      const weeks = data.target_duration_weeks
      if (weeks < 4) return `${weeks} weeks`
      const months = Math.round(weeks / 4)
      return `${months} month${months > 1 ? 's' : ''}`
    }
    return '3 months'
  }

  const generateRoadmap = async () => {
    try {
      setGeneratingRoadmap(true)
      setError(null)

      // Get user's career goal first
      const goals = await api.get<any[]>('/api/v1/career/goals')
      let body: any
      if (goals.length > 0) {
        const primaryGoal = goals[0]
        body = {
          career_goal_id: primaryGoal.id,
          career_role_id: primaryGoal.career_role_id,
          title: `Path to ${primaryGoal.title}`,
          target_duration_weeks: 12,
        }
      } else {
        const recommendations = await api.get<any[]>('/api/v1/career/recommendations')
        if (recommendations.length === 0) {
          setError('Complete career discovery and generate recommendations first.')
          return
        }
        const recommendation = recommendations[0]
        body = {
          recommendation_id: recommendation.id,
          career_role_id: recommendation.career_role_id,
          title: `Path to ${recommendation.career_role.name}`,
          target_duration_weeks: 12,
        }
      }
      const created = await api.post<any>('/api/v1/career/roadmaps', body)
      const formatted = formatRoadmapData(created)
      setRoadmap(formatted)
      setActiveMilestoneId(formatted.milestones.find((item) => item.status === 'current')?.id || formatted.milestones[0]?.id || null)
      router.replace(`/roadmap?roadmap=${created.id}`)
    } catch (err: any) {
      console.error('Failed to generate roadmap:', err)
      
      setError(err.message || 'Failed to generate roadmap. Please try again.')
    } finally {
      setGeneratingRoadmap(false)
    }
  }

  const updateMilestoneStatus = async (milestoneId: string, newStatus: string) => {
    if (!roadmap) return
    
    try {
      setUpdatingMilestoneId(milestoneId)
      setError(null)
      await api.patch(`/api/v1/career/roadmaps/milestones/${milestoneId}`, {
        status: newStatus === 'current' ? 'in_progress' : newStatus
      })
      
      // Reload roadmap to get updated data
      await loadRoadmap()
    } catch (err: any) {
      console.error('Failed to update milestone:', err)
      setError(err?.message || 'Failed to update milestone status. Please try again.')
    } finally {
      setUpdatingMilestoneId(null)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-pathfinder-teal/20 text-pathfinder-teal'
      case 'current':
        return 'bg-blue-500/20 text-blue-600'
      case 'upcoming':
        return 'bg-gray-500/20 text-gray-600'
      case 'locked':
        return 'bg-gray-300/20 text-gray-500'
      default:
        return 'bg-gray-500/20 text-gray-600'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-4">
          <div className="animate-spin h-8 w-8 border-4 border-pathfinder-teal border-t-transparent rounded-full mx-auto" />
          <p className="text-muted-foreground">Loading your roadmap...</p>
        </div>
      </div>
    )
  }

  // No roadmap exists - show generation UI
  if (!roadmap) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Button
          variant="ghost"
          onClick={() => router.push('/dashboard')}
          className="mb-6"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>

        <Card className="p-12 text-center space-y-6">
          <div className="w-16 h-16 bg-pathfinder-teal/10 rounded-full flex items-center justify-center mx-auto">
            <Map className="h-8 w-8 text-pathfinder-teal" />
          </div>

          <div className="space-y-2">
            <h1 className="text-3xl font-bold">Create Your Career Roadmap</h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Generate a personalized learning path with milestones, skills to master, and resources to help you reach your career goals.
            </p>
          </div>

          {error && (
            <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg max-w-md mx-auto">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <Button
              size="lg"
              onClick={generateRoadmap}
              disabled={generatingRoadmap}
              className="gap-2"
            >
              {generatingRoadmap ? (
                <>
                  <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                  Generating Roadmap...
                </>
              ) : (
                <>
                  <Plus className="h-4 w-4" />
                  Generate My Roadmap
                </>
              )}
            </Button>

            <p className="text-sm text-muted-foreground">
              Make sure you've completed your{' '}
              <button
                onClick={() => router.push('/career/discovery')}
                className="text-pathfinder-teal hover:underline"
              >
                career discovery
              </button>{' '}
              first for personalized results.
            </p>
          </div>
        </Card>
      </div>
    )
  }

  // Roadmap exists - show visual roadmap
  const exportRoadmap = () => {
    if (!roadmap) return
    const content = [
      roadmap.title,
      `Target role: ${roadmap.targetRole}`,
      roadmap.description,
      '',
      ...roadmap.milestones.map((milestone, index) =>
        `${index + 1}. ${milestone.title} (${milestone.weekLabel})\n` +
        `${milestone.description}\n` +
        `Work: ${milestone.work}\n` +
        `Deliverable: ${milestone.deliverable}`
      ),
    ].join('\n')
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `${roadmap.title.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.txt`
    anchor.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => router.push('/dashboard')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{roadmap.title}</h1>
          <p className="max-w-2xl text-muted-foreground">A focused path from your saved interests and resume evidence. Open a phase to see its topics, weekly work, and completion target.</p>
          </div>
        </div>
        <Button variant="outline" className="gap-2" onClick={exportRoadmap}>
          <Download className="h-4 w-4" />
          Export
        </Button>
      </div>

      {/* Progress Overview */}
      <Card className="p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Target className="h-4 w-4" />
              <span className="text-sm">Target Role</span>
            </div>
            <p className="text-xl font-semibold">{roadmap.targetRole}</p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2 text-muted-foreground">
              <TrendingUp className="h-4 w-4" />
              <span className="text-sm">Overall Progress</span>
            </div>
            <div className="space-y-1">
              <p className="text-xl font-semibold">{roadmap.overallProgress}%</p>
              <Progress value={roadmap.overallProgress} className="h-2" />
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2 text-muted-foreground">
              <CheckCircle2 className="h-4 w-4" />
              <span className="text-sm">Milestones</span>
            </div>
            <p className="text-xl font-semibold">
              {roadmap.completedMilestones} / {roadmap.totalMilestones}
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Clock className="h-4 w-4" />
              <span className="text-sm">Est. Completion</span>
            </div>
            <p className="text-xl font-semibold">{roadmap.estimatedCompletion}</p>
          </div>
        </div>
      </Card>

      {error && <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <section className="mb-7" aria-label="Roadmap phases">
        <div className="mb-4 flex items-end justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.16em] text-pathfinder-teal">Your learning journey</p>
            <h2 className="mt-1 text-xl font-semibold">Six clear phases</h2>
          </div>
          <span className="text-sm text-muted-foreground">Select a phase to explore</span>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {roadmap.milestones.map((milestone, index) => {
            const selected = activeMilestone?.id === milestone.id
            return (
              <button
                type="button"
                key={milestone.id}
                onClick={() => setActiveMilestoneId(milestone.id)}
                aria-pressed={selected}
                className={`group rounded-xl border p-4 text-left transition-all hover:-translate-y-0.5 hover:shadow-md ${selected ? 'border-pathfinder-teal bg-pathfinder-teal/5 ring-2 ring-pathfinder-teal/20' : 'bg-white hover:border-pathfinder-teal/50'}`}
              >
                <div className="mb-3 flex items-center justify-between">
                  <span className={`flex h-9 w-9 items-center justify-center rounded-full text-sm font-bold ${milestone.status === 'completed' ? 'bg-pathfinder-teal text-white' : selected ? 'bg-pathfinder-teal text-white' : 'bg-slate-100 text-slate-600'}`}>
                    {milestone.status === 'completed' ? <Check className="h-4 w-4" /> : String(index + 1).padStart(2, '0')}
                  </span>
                  <Badge className={getStatusColor(milestone.status)}>{milestone.status}</Badge>
                </div>
                <p className="font-semibold leading-snug">{milestone.title.replace(/^Phase\s+\d+:\s*/i, '')}</p>
                <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                  <span>{milestone.weekLabel}</span>
                  <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" />{milestone.estimatedDuration}</span>
                </div>
                <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-100">
                  <div className={`h-full rounded-full ${milestone.status === 'completed' ? 'bg-pathfinder-teal' : milestone.status === 'current' ? 'bg-blue-500' : 'bg-transparent'}`} style={{ width: `${milestone.status === 'completed' ? 100 : milestone.status === 'current' ? Math.max(8, milestone.progress) : 0}%` }} />
                </div>
                <span className="mt-3 inline-flex items-center gap-1 text-sm font-medium text-pathfinder-teal">Explore phase <ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" /></span>
              </button>
            )
          })}
        </div>
      </section>

      {activeMilestone && (
        <Card className="overflow-hidden border-0 shadow-lg ring-1 ring-slate-200">
          <div className="bg-gradient-to-r from-pathfinder-teal/10 via-cyan-50 to-white p-6 md:p-8">
            <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-start">
              <div>
                <div className="mb-3 flex flex-wrap items-center gap-2">
                  <Badge variant="outline" className="border-pathfinder-teal/30 bg-white">{activeMilestone.weekLabel}</Badge>
                  <Badge className={getStatusColor(activeMilestone.status)}>{activeMilestone.status}</Badge>
                  <span className="inline-flex items-center gap-1 text-sm text-muted-foreground"><Clock className="h-4 w-4" />{activeMilestone.estimatedDuration}</span>
                </div>
                <h2 className="text-2xl font-bold">{activeMilestone.title.replace(/^Phase\s+\d+:\s*/i, '')}</h2>
                {activeMilestone.personalization && (
                  <p className="mt-2 flex max-w-3xl items-start gap-2 text-sm text-slate-600"><Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-pathfinder-teal" />{activeMilestone.personalization}</p>
                )}
              </div>
              {activeMilestone.status === 'current' && (
                <Button size="sm" disabled={updatingMilestoneId === activeMilestone.id} onClick={() => updateMilestoneStatus(activeMilestone.id, 'completed')}>
                  {updatingMilestoneId === activeMilestone.id ? 'Saving…' : 'Mark phase complete'}
                </Button>
              )}
            </div>
          </div>
          <div className="grid gap-6 p-6 md:grid-cols-[1fr_280px] md:p-8">
            <div className="space-y-6">
              {activeMilestone.focusTopics && (
                <div>
                  <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-500">Topics to cover</h3>
                  <div className="flex flex-wrap gap-2">
                    {activeMilestone.focusTopics.split(';').map((topic, index) => <Badge key={index} variant="outline" className="rounded-full bg-slate-50 px-3 py-1.5 text-sm font-medium">{topic.trim().replace(/[.]$/, '')}</Badge>)}
                  </div>
                </div>
              )}
              <div className="rounded-xl border bg-slate-50/70 p-4 md:p-5">
                <h3 className="mb-2 font-semibold">What to work on</h3>
                <p className="text-sm leading-6 text-slate-600">{activeMilestone.work || activeMilestone.description}</p>
                {activeMilestone.practice && <p className="mt-3 border-t pt-3 text-sm leading-6 text-slate-600">{activeMilestone.practice}</p>}
              </div>
              {activeMilestone.projectTheme && <div className="rounded-xl border border-violet-200 bg-violet-50/70 p-4"><p className="text-sm font-semibold text-violet-900">Personal project direction</p><p className="mt-1 text-sm leading-6 text-violet-800">{activeMilestone.projectTheme}</p></div>}
              {activeMilestone.projectDepth.length > 0 && (
                <div>
                  <h3 className="mb-3 font-semibold">Project depth checklist</h3>
                  <div className="grid gap-2 sm:grid-cols-2">
                    {activeMilestone.projectDepth.map((item, index) => <div key={index} className="flex gap-2 rounded-lg border p-3 text-sm text-slate-600"><CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-pathfinder-teal" />{item}</div>)}
                  </div>
                </div>
              )}
              {activeMilestone.deliverable && <div className="flex gap-3 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-900"><Target className="h-5 w-5 shrink-0 text-emerald-700" /><div><p className="font-semibold">How you’ll know you’re done</p><p className="mt-1 leading-6">{activeMilestone.deliverable}</p></div></div>}
            </div>
            <aside className="space-y-4">
              <div className="rounded-xl border p-4">
                <h3 className="font-semibold">Phase progress</h3>
                <div className="mt-3 flex items-center justify-between text-sm text-muted-foreground"><span>{activeMilestone.status === 'completed' ? 'Complete' : activeMilestone.status === 'current' ? 'In progress' : 'Not started'}</span><span>{activeMilestone.status === 'completed' ? '100%' : `${activeMilestone.progress}%`}</span></div>
                <Progress value={activeMilestone.status === 'completed' ? 100 : activeMilestone.progress} className="mt-2 h-2" />
              </div>
              {activeMilestone.resources.length > 0 && (
                <div className="rounded-xl border p-4">
                  <h3 className="mb-3 font-semibold">Useful references</h3>
                  <div className="space-y-2">
                    {activeMilestone.resources.map((resource, index) => <a key={index} href={resource.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 rounded-lg bg-slate-50 p-3 text-sm transition-colors hover:bg-pathfinder-teal/10"><BookOpen className="h-4 w-4 shrink-0 text-pathfinder-teal" /><span className="min-w-0 flex-1 truncate">{resource.title}</span><ChevronRight className="h-4 w-4 shrink-0 text-slate-400" /></a>)}
                  </div>
                </div>
              )}
            </aside>
          </div>
        </Card>
      )}

      {/* Actions */}
      <div className="mt-8 flex justify-center gap-4">
        <Button
          variant="outline"
          onClick={generateRoadmap}
          disabled={generatingRoadmap}
        >
          Regenerate Roadmap
        </Button>
      </div>
    </div>
  )
}
