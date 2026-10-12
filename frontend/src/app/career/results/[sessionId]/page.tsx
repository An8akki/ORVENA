'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { LoadingSpinner } from '@/components/shared/LoadingSpinner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  getDiscoverySession,
  analyzeDiscoverySession,
  type CareerDiscoverySession,
  type SessionAnalysis,
} from '@/lib/api/career'
import { Target, Sparkles, ArrowLeft, MessageCircle } from 'lucide-react'

export default function CareerResultsPage() {
  return (
    <AuthGuard>
      <CareerResultsContent />
    </AuthGuard>
  )
}

function CareerResultsContent() {
  const router = useRouter()
  const params = useParams()
  const sessionId = params.sessionId as string

  const [loading, setLoading] = useState(true)
  const [session, setSession] = useState<CareerDiscoverySession | null>(null)
  const [analysis, setAnalysis] = useState<SessionAnalysis | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (sessionId) {
      loadResults()
    }
  }, [sessionId])

  async function loadResults() {
    try {
      setLoading(true)
      setError(null)

      const [sessionData, analysisData] = await Promise.all([
        getDiscoverySession(sessionId),
        analyzeDiscoverySession(sessionId),
      ])

      setSession(sessionData)
      setAnalysis(analysisData)
    } catch (err: any) {
      setError(err.message || 'Failed to load results')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (error || !session || !analysis) {
    return (
      <div className="container mx-auto py-8 px-4 max-w-3xl">
        <Alert variant="destructive">
          <AlertDescription>{error || 'Session not found'}</AlertDescription>
        </Alert>
        <Button onClick={() => router.push('/dashboard')} className="mt-4">
          Back to Dashboard
        </Button>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-4xl">
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

        <div className="flex items-center gap-3 mb-2">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Your Career Discovery Results</h1>
            <p className="text-muted-foreground">
              Based on your responses, here's what we learned about you
            </p>
          </div>
        </div>
      </div>

      {/* Analysis Summary */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Career Profile Summary</CardTitle>
          <CardDescription>
            AI-generated insights from your discovery session
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="prose prose-sm max-w-none">
            <p className="text-muted-foreground whitespace-pre-wrap">
              {analysis.summary}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Conversation History */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Your Responses</CardTitle>
          <CardDescription>
            Review what you shared during the discovery process
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {session.responses.map((response, index) => (
              <div key={response.id} className="border-l-2 border-blue-500 pl-4 py-2">
                <div className="flex items-start gap-2 mb-2">
                  <MessageCircle className="w-4 h-4 text-blue-500 mt-1 flex-shrink-0" />
                  <p className="text-sm font-medium text-muted-foreground">
                    Question {response.question_number}
                  </p>
                </div>
                <p className="text-sm font-semibold mb-2">{response.question_text}</p>
                <p className="text-sm text-muted-foreground">{response.response_text}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Next Steps */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <CardHeader>
          <CardTitle>Next Steps</CardTitle>
          <CardDescription>
            Continue your career journey with ORVENA
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <Button
              onClick={() => router.push('/career/recommendations')}
              className="w-full"
            >
              <Target className="w-4 h-4 mr-2" />
              Get Personalized Career Recommendations
            </Button>
            
            <Button
              variant="outline"
              onClick={() => router.push('/profile')}
              className="w-full"
            >
              Complete Your Profile
            </Button>

            <Button
              variant="ghost"
              onClick={() => router.push('/dashboard')}
              className="w-full"
            >
              Back to Dashboard
            </Button>
          </div>

          <div className="mt-6 p-4 bg-white/50 rounded-lg">
            <p className="text-sm text-muted-foreground">
              💡 <strong>Pro Tip:</strong> The more complete your profile, the better
              career recommendations we can provide. Consider adding your skills,
              projects, and education before viewing recommendations.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
