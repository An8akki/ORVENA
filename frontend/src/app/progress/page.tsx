'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  ArrowLeft,
  TrendingUp,
  Target,
  Calendar,
  Award,
  BookOpen,
  CheckCircle2,
  Clock,
  Zap,
  Download
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface SkillProgress {
  skill: string
  currentLevel: number
  targetLevel: number
  progress: number
  lastUpdated: string
  trend: 'improving' | 'stable' | 'declining'
}

interface MilestoneStats {
  id: string
  title: string
  status: 'completed' | 'in-progress' | 'upcoming'
  completedDate?: string
  daysToComplete?: number
  phase: string
}

interface Activity {
  id: string
  date: string
  type: 'course' | 'project' | 'assessment' | 'milestone' | 'job_application'
  title: string
  outcome?: string
  duration?: number
}

interface GoalProgress {
  id: string
  title: string
  targetDate: string
  completionRate: number
  onTrack: boolean
  daysRemaining: number
}

interface ProgressMetrics {
  skillsDevelopment: SkillProgress[]
  milestones: MilestoneStats[]
  recentActivities: Activity[]
  goals: GoalProgress[]
  overallStats: {
    totalActivities: number
    completedMilestones: number
    totalMilestones: number
    learningStreak: number
    hoursLearned: number
    skillsImproved: number
  }
}

export default function ProgressPage() {
  const router = useRouter()
  const [metrics, setMetrics] = useState<ProgressMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'quarter' | 'year'>('month')

  useEffect(() => {
    loadProgressMetrics()
  }, [selectedPeriod])

  const loadProgressMetrics = async () => {
    try {
      setLoading(true)
      setError(null)

      // For now, show empty state since user hasn't started their journey yet
      // In production, this would fetch real data from the backend
      
      setMetrics(null)
    } catch (err: any) {
      console.error('Failed to load progress data:', err)
      setError(null) // Don't show error, just show empty state
      setMetrics(null)
    } finally {
      setLoading(false)
    }
  }

  const calculateMetrics = (roadmaps: any[], goals: any[]): ProgressMetrics => {
    // Extract data from roadmaps and goals
    const allMilestones: MilestoneStats[] = []
    const skillsMap: Map<string, SkillProgress> = new Map()
    const activities: Activity[] = []

    // Process roadmaps
    roadmaps.forEach((roadmap) => {
      if (roadmap.milestones) {
        roadmap.milestones.forEach((m: any) => {
          allMilestones.push({
            id: m.id || m.milestone_id,
            title: m.title,
            status: mapStatus(m.status),
            completedDate: m.completed_date,
            daysToComplete: m.days_to_complete,
            phase: m.phase_id || 'General'
          })

          // Extract skills
          const skills = m.skills || m.topics || []
          skills.forEach((skill: string) => {
            if (!skillsMap.has(skill)) {
              skillsMap.set(skill, {
                skill,
                currentLevel: m.status === 'completed' ? 4 : m.status === 'in_progress' ? 2 : 1,
                targetLevel: 5,
                progress: m.status === 'completed' ? 100 : m.status === 'in_progress' ? 50 : 20,
                lastUpdated: m.updated_at || new Date().toISOString(),
                trend: 'improving'
              })
            }
          })

          // Add to activities
          if (m.completed_date) {
            activities.push({
              id: m.id,
              date: m.completed_date,
              type: 'milestone',
              title: `Completed: ${m.title}`,
              outcome: 'success',
              duration: m.estimated_hours
            })
          }
        })
      }
    })

    const completedMilestones = allMilestones.filter(m => m.status === 'completed').length
    const totalHours = activities.reduce((sum, a) => sum + (a.duration || 0), 0)

    return {
      skillsDevelopment: Array.from(skillsMap.values()),
      milestones: allMilestones,
      recentActivities: activities.sort((a, b) => 
        new Date(b.date).getTime() - new Date(a.date).getTime()
      ).slice(0, 10),
      goals: goals.map((g: any) => ({
        id: g.id,
        title: g.title || g.target_role,
        targetDate: g.target_date || g.deadline,
        completionRate: calculateGoalCompletion(g, allMilestones),
        onTrack: true,
        daysRemaining: calculateDaysRemaining(g.target_date)
      })),
      overallStats: {
        totalActivities: activities.length,
        completedMilestones,
        totalMilestones: allMilestones.length,
        learningStreak: calculateStreak(activities),
        hoursLearned: totalHours,
        skillsImproved: skillsMap.size
      }
    }
  }

  const mapStatus = (status: string): 'completed' | 'in-progress' | 'upcoming' => {
    if (status === 'completed' || status === 'COMPLETED') return 'completed'
    if (status === 'in_progress' || status === 'IN_PROGRESS' || status === 'current') return 'in-progress'
    return 'upcoming'
  }

  const calculateGoalCompletion = (goal: any, milestones: MilestoneStats[]): number => {
    if (milestones.length === 0) return 0
    const completed = milestones.filter(m => m.status === 'completed').length
    return Math.round((completed / milestones.length) * 100)
  }

  const calculateDaysRemaining = (targetDate?: string): number => {
    if (!targetDate) return 90 // Default 90 days
    const target = new Date(targetDate)
    const now = new Date()
    const diff = target.getTime() - now.getTime()
    return Math.ceil(diff / (1000 * 60 * 60 * 24))
  }

  const calculateStreak = (activities: Activity[]): number => {
    // Simple calculation - can be enhanced
    return activities.length > 0 ? Math.min(activities.length, 7) : 0
  }

  const getSkillLevelLabel = (level: number): string => {
    if (level >= 5) return 'Expert'
    if (level >= 4) return 'Advanced'
    if (level >= 3) return 'Intermediate'
    if (level >= 2) return 'Beginner'
    return 'Novice'
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'course':
        return <BookOpen className="h-4 w-4" />
      case 'milestone':
        return <CheckCircle2 className="h-4 w-4" />
      case 'assessment':
        return <Award className="h-4 w-4" />
      default:
        return <Zap className="h-4 w-4" />
    }
  }

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    const now = new Date()
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays} days ago`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
    return date.toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-4">
          <div className="animate-spin h-8 w-8 border-4 border-pathfinder-teal border-t-transparent rounded-full mx-auto" />
          <p className="text-muted-foreground">Loading your progress...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Button variant="ghost" onClick={() => router.push('/dashboard')} className="mb-6">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>
        <Card className="p-8 text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={loadProgressMetrics}>Try Again</Button>
        </Card>
      </div>
    )
  }

  if (!metrics || metrics.overallStats.totalActivities === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Button variant="ghost" onClick={() => router.push('/dashboard')} className="mb-6">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>
        <Card className="p-12 text-center space-y-6">
          <div className="w-16 h-16 bg-pathfinder-teal/10 rounded-full flex items-center justify-center mx-auto">
            <TrendingUp className="h-8 w-8 text-pathfinder-teal" />
          </div>
          <div className="space-y-2">
            <h1 className="text-3xl font-bold">Start Tracking Your Progress</h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Complete your career discovery and start working on your roadmap to see your progress here.
            </p>
          </div>
          <div className="flex gap-4 justify-center">
            <Button onClick={() => router.push('/career/discovery')}>
              Start Career Discovery
            </Button>
            <Button variant="outline" onClick={() => router.push('/roadmap')}>
              View Roadmap
            </Button>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => router.push('/dashboard')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Progress Tracking</h1>
            <p className="text-muted-foreground">Monitor your career development journey</p>
          </div>
        </div>
        <Button variant="outline" className="gap-2">
          <Download className="h-4 w-4" />
          Export Report
        </Button>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Card className="p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-pathfinder-teal/10 rounded-lg flex items-center justify-center">
              <CheckCircle2 className="h-6 w-6 text-pathfinder-teal" />
            </div>
            <div>
              <p className="text-2xl font-bold">{metrics.overallStats.completedMilestones}</p>
              <p className="text-sm text-muted-foreground">Milestones Completed</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center">
              <Clock className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{metrics.overallStats.hoursLearned}</p>
              <p className="text-sm text-muted-foreground">Hours Learned</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-orange-500/10 rounded-lg flex items-center justify-center">
              <Zap className="h-6 w-6 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{metrics.overallStats.learningStreak}</p>
              <p className="text-sm text-muted-foreground">Day Streak</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{metrics.overallStats.skillsImproved}</p>
              <p className="text-sm text-muted-foreground">Skills Developing</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Tabs for different views */}
      <Tabs defaultValue="skills" className="space-y-6">
        <TabsList>
          <TabsTrigger value="skills">Skills Development</TabsTrigger>
          <TabsTrigger value="milestones">Milestones</TabsTrigger>
          <TabsTrigger value="goals">Goals</TabsTrigger>
          <TabsTrigger value="activity">Recent Activity</TabsTrigger>
        </TabsList>

        {/* Skills Development Tab */}
        <TabsContent value="skills" className="space-y-4">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-6">Skills Progress</h2>
            <div className="space-y-6">
              {metrics.skillsDevelopment.slice(0, 8).map((skill) => (
                <div key={skill.skill} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="font-medium">{skill.skill}</span>
                      <Badge variant="outline" className="text-xs">
                        {getSkillLevelLabel(skill.currentLevel)}
                      </Badge>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {skill.progress}%
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Progress value={skill.progress} className="flex-1 h-2" />
                    <span className="text-xs text-muted-foreground whitespace-nowrap">
                      Target: {getSkillLevelLabel(skill.targetLevel)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>

        {/* Milestones Tab */}
        <TabsContent value="milestones" className="space-y-4">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-6">Milestone Timeline</h2>
            <div className="space-y-4">
              {metrics.milestones.map((milestone) => (
                <div
                  key={milestone.id}
                  className="flex items-start gap-4 p-4 rounded-lg border"
                >
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    milestone.status === 'completed'
                      ? 'bg-pathfinder-teal/20'
                      : milestone.status === 'in-progress'
                      ? 'bg-blue-500/20'
                      : 'bg-gray-300/20'
                  }`}>
                    {milestone.status === 'completed' ? (
                      <CheckCircle2 className="h-5 w-5 text-pathfinder-teal" />
                    ) : (
                      <Clock className="h-5 w-5 text-gray-500" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-1">
                      <h3 className="font-medium">{milestone.title}</h3>
                      <Badge
                        variant="outline"
                        className={
                          milestone.status === 'completed'
                            ? 'bg-pathfinder-teal/20 text-pathfinder-teal'
                            : milestone.status === 'in-progress'
                            ? 'bg-blue-500/20 text-blue-600'
                            : 'bg-gray-300/20 text-gray-600'
                        }
                      >
                        {milestone.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {milestone.completedDate
                        ? `Completed ${formatDate(milestone.completedDate)}`
                        : 'In progress'}
                      {milestone.daysToComplete && ` • ${milestone.daysToComplete} days`}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>

        {/* Goals Tab */}
        <TabsContent value="goals" className="space-y-4">
          <div className="grid gap-4">
            {metrics.goals.map((goal) => (
              <Card key={goal.id} className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-pathfinder-teal/10 rounded-lg flex items-center justify-center">
                      <Target className="h-5 w-5 text-pathfinder-teal" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{goal.title}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">
                          {goal.daysRemaining} days remaining
                        </span>
                      </div>
                    </div>
                  </div>
                  <Badge variant={goal.onTrack ? 'default' : 'destructive'}>
                    {goal.onTrack ? 'On Track' : 'Behind'}
                  </Badge>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Progress</span>
                    <span className="font-medium">{goal.completionRate}%</span>
                  </div>
                  <Progress value={goal.completionRate} className="h-3" />
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Recent Activity Tab */}
        <TabsContent value="activity" className="space-y-4">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-6">Recent Activities</h2>
            <div className="space-y-3">
              {metrics.recentActivities.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-start gap-3 p-3 rounded-lg border"
                >
                  <div className="w-8 h-8 bg-pathfinder-teal/10 rounded-lg flex items-center justify-center text-pathfinder-teal">
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{activity.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatDate(activity.date)}
                      {activity.duration && ` • ${activity.duration} hours`}
                    </p>
                  </div>
                  {activity.outcome && (
                    <Badge variant="outline" className="text-xs">
                      {activity.outcome}
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
