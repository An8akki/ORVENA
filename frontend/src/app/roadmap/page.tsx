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
  Circle, 
  Lock, 
  Clock, 
  Target,
  BookOpen,
  ArrowLeft,
  Download,
  Plus,
  TrendingUp
} from 'lucide-react'
import { api } from '@/lib/api-client'

interface Milestone {
  id: string
  title: string
  description: string
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

  useEffect(() => {
    loadRoadmap()
  }, [])

  const loadRoadmap = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // For now, show a message that user needs to complete career discovery first
      // In production, this would call: await apiClient.get('/api/v1/career/roadmaps')
      
      setRoadmap(null)
    } catch (err: any) {
      console.error('Failed to load roadmap:', err)
      setError(null) // Don't show error, just show empty state
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
      description: data.description || '',
      targetRole: data.target_role || data.role_name || 'Software Engineer',
      totalMilestones: data.milestones?.length || 0,
      completedMilestones: data.milestones?.filter((m: any) => m.status === 'completed').length || 0,
      overallProgress: data.overall_progress || 0,
      estimatedCompletion: data.estimated_completion || formatEstimatedCompletion(data),
      milestones: (data.milestones || []).map((m: any, index: number) => ({
        id: m.id || m.milestone_id,
        title: m.title,
        description: m.description,
        status: mapMilestoneStatus(m.status, index),
        estimatedDuration: m.estimated_duration || `${m.estimated_hours || 10} hours`,
        skills: m.skills || m.topics || [],
        resources: m.resources || [],
        order: m.order || m.sequence_number || index + 1,
        progress: m.progress || (m.status === 'completed' ? 100 : m.status === 'current' ? 50 : 0),
        completedDate: m.completed_date
      }))
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
      const goalsResponse = await api.get('/api/v1/career/goals')
      
      if (!goalsResponse.data || goalsResponse.data.length === 0) {
        setError('Please set a career goal first. Complete your career discovery to get started.')
        return
      }

      const primaryGoal = goalsResponse.data[0]

      // Generate roadmap using AI with fallback to template-based
      const response = await api.post('/api/v1/career/roadmaps', {
        career_goal_id: primaryGoal.id,
        title: `Path to ${primaryGoal.target_role}`,
        description: `Personalized roadmap to become a ${primaryGoal.target_role}`,
        target_duration_weeks: 16
      })

      setRoadmap(formatRoadmapData(response.data))
    } catch (err: any) {
      console.error('Failed to generate roadmap:', err)
      
      if (err.response?.status === 404) {
        setError('No career goal found. Please complete your career discovery first.')
      } else if (err.response?.status === 400) {
        setError('Unable to generate roadmap. Please complete your career discovery and set a career goal.')
      } else {
        setError('Failed to generate roadmap. Please try again or contact support.')
      }
    } finally {
      setGeneratingRoadmap(false)
    }
  }

  const updateMilestoneStatus = async (milestoneId: string, newStatus: string) => {
    if (!roadmap) return
    
    try {
      await api.patch(`/api/v1/career/roadmaps/milestones/${milestoneId}`, {
        status: newStatus.toUpperCase()
      })
      
      // Reload roadmap to get updated data
      await loadRoadmap()
    } catch (err) {
      console.error('Failed to update milestone:', err)
      setError('Failed to update milestone status. Please try again.')
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-pathfinder-teal" />
      case 'current':
        return <Circle className="h-5 w-5 text-pathfinder-teal fill-pathfinder-teal" />
      case 'upcoming':
        return <Circle className="h-5 w-5 text-muted-foreground" />
      case 'locked':
        return <Lock className="h-5 w-5 text-muted-foreground" />
      default:
        return <Circle className="h-5 w-5 text-muted-foreground" />
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
            <p className="text-muted-foreground">{roadmap.description}</p>
          </div>
        </div>
        <Button variant="outline" className="gap-2">
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

      {/* Visual Roadmap - Timeline */}
      <div className="space-y-4">
        {roadmap.milestones.map((milestone, index) => (
          <Card
            key={milestone.id}
            className={`p-6 transition-all ${
              milestone.status === 'current'
                ? 'ring-2 ring-pathfinder-teal shadow-lg'
                : ''
            }`}
          >
            <div className="flex gap-6">
              {/* Timeline indicator */}
              <div className="flex flex-col items-center">
                <div className="relative">
                  {getStatusIcon(milestone.status)}
                  {index < roadmap.milestones.length - 1 && (
                    <div
                      className={`absolute top-8 left-1/2 -translate-x-1/2 w-0.5 h-16 ${
                        milestone.status === 'completed'
                          ? 'bg-pathfinder-teal'
                          : 'bg-gray-300'
                      }`}
                    />
                  )}
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 space-y-4">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <h3 className="text-xl font-semibold">{milestone.title}</h3>
                      <Badge className={getStatusColor(milestone.status)}>
                        {milestone.status}
                      </Badge>
                    </div>
                    <p className="text-muted-foreground">{milestone.description}</p>
                  </div>

                  {milestone.status === 'current' && (
                    <Button
                      size="sm"
                      onClick={() => updateMilestoneStatus(milestone.id, 'completed')}
                    >
                      Mark Complete
                    </Button>
                  )}
                </div>

                {/* Progress bar for current milestone */}
                {milestone.status === 'current' && (
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Progress</span>
                      <span className="font-medium">{milestone.progress}%</span>
                    </div>
                    <Progress value={milestone.progress} className="h-2" />
                  </div>
                )}

                {/* Metadata */}
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    {milestone.estimatedDuration}
                  </div>
                  {milestone.completedDate && (
                    <div className="flex items-center gap-1">
                      <CheckCircle2 className="h-4 w-4" />
                      Completed {milestone.completedDate}
                    </div>
                  )}
                </div>

                {/* Skills to learn */}
                {milestone.skills.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Skills to Master:</p>
                    <div className="flex flex-wrap gap-2">
                      {milestone.skills.map((skill, idx) => (
                        <Badge key={idx} variant="outline">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Resources */}
                {milestone.resources.length > 0 && milestone.status !== 'locked' && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Learning Resources:</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {milestone.resources.map((resource, idx) => (
                        <a
                          key={idx}
                          href={resource.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-2 p-3 rounded-lg border hover:border-pathfinder-teal hover:bg-pathfinder-teal/5 transition-colors"
                        >
                          <BookOpen className="h-4 w-4 text-pathfinder-teal flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">
                              {resource.title}
                            </p>
                            <p className="text-xs text-muted-foreground capitalize">
                              {resource.type}
                            </p>
                          </div>
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>

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
