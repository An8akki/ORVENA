'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { LoadingSpinner } from '@/components/shared/LoadingSpinner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  getRecommendations,
  generateRecommendations,
  getDiscoverySessions,
  createRoadmap,
  type CareerRecommendation,
} from '@/lib/api/career'
import {
  Target,
  TrendingUp,
  AlertTriangle,
  Sparkles,
  ArrowLeft,
  CheckCircle2,
  XCircle,
  LightbulbIcon,
  MapIcon,
} from 'lucide-react'

export default function CareerRecommendationsPage() {
  return (
    <AuthGuard>
      <RecommendationsContent />
    </AuthGuard>
  )
}

function RecommendationsContent() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [recommendations, setRecommendations] = useState<CareerRecommendation[]>([])
  const [error, setError] = useState<string | null>(null)
  const [creatingRoadmap, setCreatingRoadmap] = useState<string | null>(null)

  useEffect(() => {
    loadRecommendations()
  }, [])

  async function loadRecommendations() {
    try {
      setLoading(true)
      setError(null)
      let data: CareerRecommendation[] = []
      let recommendationsLoadError: unknown = null
      try {
        data = await getRecommendations()
      } catch (loadError) {
        // A failure to list existing records must not prevent generation from
        // the student's saved discovery answers below.
        recommendationsLoadError = loadError
        console.error('Could not load existing career recommendations:', loadError)
      }
      setRecommendations(data)

      // Completed sessions are no longer returned by the active-session
      // endpoint. Find the newest saved session with answers so completing
      // discovery can generate recommendations on the first visit here.
      try {
        const sessions = await getDiscoverySessions()
        const session = sessions
          .filter((item) => (item.responses?.length || 0) > 0)
          .sort((a, b) => Date.parse(b.updated_at) - Date.parse(a.updated_at))[0]
        const newestRecommendation = [...data].sort(
          (a, b) => Date.parse(b.updated_at) - Date.parse(a.updated_at)
        )[0]
        const recommendationsAreStale = session && (
          !newestRecommendation ||
          newestRecommendation.session_id !== session.id ||
          Date.parse(session.updated_at) > Date.parse(newestRecommendation.updated_at)
        )
        if (recommendationsAreStale) {
          setGenerating(true)
          const refreshed = await generateRecommendations(session.id)
          setRecommendations(refreshed)
          if (refreshed.length === 0) {
            setError('We found your saved discovery answers but could not create recommendations. Please try Generate Recommendations again.')
          }
        } else if (recommendationsLoadError && !session) {
          setError(recommendationsLoadError instanceof Error ? recommendationsLoadError.message : 'Could not load recommendations.')
        }
      } catch (refreshError) {
        console.error('Could not refresh recommendations from saved discovery answers:', refreshError)
        // The session-list endpoint can fail independently of generation.
        // The backend generation route selects the latest answered session
        // itself, so try that route without requiring the list response.
        try {
          const generated = await generateRecommendations()
          setRecommendations(generated)
          if (generated.length === 0) {
            setError('Your discovery answers are saved, but no recommendations were produced. Please try again.')
          }
        } catch (generationError) {
          setError(generationError instanceof Error ? generationError.message : 'Could not generate recommendations from your saved answers.')
        }
      } finally {
        setGenerating(false)
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load recommendations')
    } finally {
      setLoading(false)
    }
  }

  async function handleGenerateRecommendations() {
    try {
      setGenerating(true)
      setError(null)
      const data = await generateRecommendations()
      setRecommendations(data)
    } catch (err: any) {
      setError(err.message || 'Failed to generate recommendations')
    } finally {
      setGenerating(false)
    }
  }

  async function handleCreateRoadmap(recommendation: CareerRecommendation) {
    try {
      setCreatingRoadmap(recommendation.id)
      const roadmap = await createRoadmap({
        recommendation_id: recommendation.id,
        career_role_id: recommendation.career_role_id,
        title: `Path to ${recommendation.career_role.name}`,
        target_duration_weeks: 12,
      })
      router.push(`/roadmap?roadmap=${roadmap.id}`)
    } catch (err: any) {
      setError(err.message || 'Failed to create roadmap')
      setCreatingRoadmap(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/dashboard')}
          className="mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </Button>

        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <Target className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">Career Recommendations</h1>
              <p className="text-muted-foreground">
                AI-powered career paths tailored for you
              </p>
            </div>
          </div>
          
          {recommendations.length > 0 && (
            <Button onClick={handleGenerateRecommendations} disabled={generating}>
              {generating ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Regenerating...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Regenerate
                </>
              )}
            </Button>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Empty State */}
      {!loading && recommendations.length === 0 && (
        <Card>
          <CardContent className="pt-12 pb-12 text-center">
            <Target className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Recommendations Yet</h3>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Complete a career discovery session to get personalized AI-powered career
              recommendations based on your profile.
            </p>
            <div className="flex gap-3 justify-center">
              <Button onClick={handleGenerateRecommendations} disabled={generating}>
                {generating ? (
                  <>
                    <LoadingSpinner size="sm" className="mr-2" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Generate Recommendations
                  </>
                )}
              </Button>
              <Button variant="outline" onClick={() => router.push('/career/discovery')}>
                Start Discovery
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recommendations List */}
      {recommendations.length > 0 && (
        <div className="space-y-6">
          {recommendations.map((rec, index) => (
            <Card key={rec.id} className="overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 border-b">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Badge variant="secondary" className="text-lg">
                        #{index + 1}
                      </Badge>
                      <CardTitle className="text-2xl">
                        {rec.career_role.name}
                      </CardTitle>
                      <Badge>{rec.career_role.category}</Badge>
                    </div>
                    <CardDescription className="text-base">
                      {rec.career_role.description}
                    </CardDescription>
                  </div>
                  
                  <div className="text-right">
                    <div className="text-3xl font-bold text-primary">
                      {Math.round(rec.fit_score * 100)}%
                    </div>
                    <div className="text-sm text-muted-foreground">Fit Score</div>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="pt-6">
                {/* Salary Range */}
                {rec.career_role.typical_salary_min && rec.career_role.typical_salary_max && (
                  <div className="mb-6 p-4 bg-green-50 rounded-lg border border-green-200">
                    <div className="text-sm font-medium text-green-900 mb-1">
                      Typical Salary Range
                    </div>
                    <div className="text-2xl font-bold text-green-700">
                      ${rec.career_role.typical_salary_min.toLocaleString()} - $
                      {rec.career_role.typical_salary_max.toLocaleString()}
                    </div>
                  </div>
                )}

                {/* Reasoning */}
                <div className="mb-6">
                  <h4 className="font-semibold mb-2 flex items-center gap-2">
                    <LightbulbIcon className="w-4 h-4 text-yellow-600" />
                    Why This Role Fits You
                  </h4>
                  <p className="text-muted-foreground">{rec.reasoning}</p>
                </div>

                {/* SWOT Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                  {/* Strengths */}
                  <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                    <h4 className="font-semibold text-green-900 mb-3 flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4" />
                      Strengths
                    </h4>
                    <ul className="space-y-1">
                      {rec.strengths.map((strength, idx) => (
                        <li key={idx} className="text-sm text-green-800 flex items-start gap-2">
                          <span className="text-green-600 mt-0.5">•</span>
                          {strength}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Gaps */}
                  <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                    <h4 className="font-semibold text-red-900 mb-3 flex items-center gap-2">
                      <XCircle className="w-4 h-4" />
                      Areas to Develop
                    </h4>
                    <ul className="space-y-1">
                      {rec.gaps.map((gap, idx) => (
                        <li key={idx} className="text-sm text-red-800 flex items-start gap-2">
                          <span className="text-red-600 mt-0.5">•</span>
                          {gap}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Opportunities */}
                  <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
                      <TrendingUp className="w-4 h-4" />
                      Opportunities
                    </h4>
                    <ul className="space-y-1">
                      {rec.opportunities.map((opp, idx) => (
                        <li key={idx} className="text-sm text-blue-800 flex items-start gap-2">
                          <span className="text-blue-600 mt-0.5">•</span>
                          {opp}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Threats */}
                  <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
                    <h4 className="font-semibold text-orange-900 mb-3 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" />
                      Challenges
                    </h4>
                    <ul className="space-y-1">
                      {rec.threats.map((threat, idx) => (
                        <li key={idx} className="text-sm text-orange-800 flex items-start gap-2">
                          <span className="text-orange-600 mt-0.5">•</span>
                          {threat}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                  <Button
                    onClick={() => handleCreateRoadmap(rec)}
                    disabled={creatingRoadmap === rec.id}
                  >
                    {creatingRoadmap === rec.id ? (
                      <>
                        <LoadingSpinner size="sm" className="mr-2" />
                        Creating...
                      </>
                    ) : (
                      <>
                        <MapIcon className="w-4 h-4 mr-2" />
                        Create Development Roadmap
                      </>
                    )}
                  </Button>
                  <Button variant="outline">Learn More</Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
