'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { AppLayout } from '@/components/layout/AppLayout'
import { LoadingSpinner } from '@/components/shared/LoadingSpinner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import PathfinderVisual from '@/components/brand/PathfinderVisual'
import {
  createDiscoverySession,
  getActiveDiscoverySession,
  getNextQuestion,
  submitAnswer,
  completeDiscoverySession,
  type CareerDiscoverySession,
  type NextQuestionResponse,
} from '@/lib/api/career'
import { 
  Target, 
  MessageCircle, 
  CheckCircle, 
  Sparkles, 
  Lightbulb,
  TrendingUp,
  ArrowRight,
  Award,
  MapPin,
} from 'lucide-react'

export default function CareerDiscoveryPage() {
  return (
    <AuthGuard>
      <AppLayout>
        <CareerDiscoveryContent />
      </AppLayout>
    </AuthGuard>
  )
}

function CareerDiscoveryContent() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)
  const [session, setSession] = useState<CareerDiscoverySession | null>(null)
  const [currentQuestion, setCurrentQuestion] = useState<NextQuestionResponse | null>(null)
  const [answer, setAnswer] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isComplete, setIsComplete] = useState(false)

  const MAX_QUESTIONS = 10 // Configurable max questions

  useEffect(() => {
    initializeSession()
  }, [])

  async function initializeSession() {
    try {
      setLoading(true)
      setError(null)

      // Try to get active session
      try {
        const activeSession = await getActiveDiscoverySession()
        setSession(activeSession)
        
        // Check how many questions answered (use responses length)
        const questionsAnswered = activeSession.responses?.length || 0
        
        // Load next question if session not complete
        if (questionsAnswered < MAX_QUESTIONS && activeSession.status === 'in_progress') {
          const question = await getNextQuestion(activeSession.id)
          setCurrentQuestion(question)
        } else {
          setIsComplete(true)
        }
      } catch {
        // No active session, create new one
        const newSession = await createDiscoverySession('initial')
        setSession(newSession)
        
        // Get first question
        const question = await getNextQuestion(newSession.id)
        setCurrentQuestion(question)
      }
    } catch (err: any) {
      // Properly extract error message from different error types
      let errorMessage = 'Failed to initialize session';
      
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (err?.error?.message) {
        errorMessage = err.error.message;
      } else if (err?.detail) {
        errorMessage = err.detail;
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else if (err?.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      console.error('Career Discovery initialization error:', err);
    } finally {
      setLoading(false)
    }
  }

  async function handleSubmitAnswer() {
    if (!session || !currentQuestion || !answer.trim()) return

    try {
      setProcessing(true)
      setError(null)

      // Submit answer
      await submitAnswer({
        session_id: session.id,
        question_number: currentQuestion.question_number,
        question_text: currentQuestion.question_text,
        response_text: answer.trim(),
      })

      // Clear answer
      setAnswer('')

      // Update local session with new response count
      const newResponsesCount = (session.responses?.length || 0) + 1
      
      // Check if we've reached max questions
      if (newResponsesCount >= MAX_QUESTIONS) {
        setIsComplete(true)
        await completeDiscoverySession(session.id)
      } else {
        // Get next question
        const nextQ = await getNextQuestion(session.id)
        setCurrentQuestion(nextQ)
        
        // Update session with incremented response count
        setSession({
          ...session,
          responses: [...(session.responses || []), { 
            id: '', 
            session_id: session.id,
            sequence_number: currentQuestion.question_number,
            question_text: currentQuestion.question_text,
            response_text: answer.trim(),
            question_category: null,
            phase: null,
            created_at: new Date().toISOString()
          }]
        })
      }
    } catch (err: any) {
      let errorMessage = 'Failed to submit answer';
      
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (err?.error?.message) {
        errorMessage = err.error.message;
      } else if (err?.detail) {
        errorMessage = err.detail;
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else if (err?.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      console.error('Submit answer error:', err);
    } finally {
      setProcessing(false)
    }
  }

  async function handleComplete() {
    if (!session) return

    try {
      setProcessing(true)
      await completeDiscoverySession(session.id)
      router.push(`/career/results/${session.id}`)
    } catch (err: any) {
      let errorMessage = 'Failed to complete session';
      
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (err?.error?.message) {
        errorMessage = err.error.message;
      } else if (err?.detail) {
        errorMessage = err.detail;
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else if (err?.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      console.error('Complete session error:', err);
      setProcessing(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-pathfinder-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm text-midnight-600">Initializing your career journey...</p>
        </div>
      </div>
    )
  }

  const progress = session
    ? ((session.responses?.length || 0) / MAX_QUESTIONS) * 100
    : 0
  
  const questionsAnswered = session?.responses?.length || 0

  return (
    <div className="min-h-[calc(100vh-4rem)]">
      {/* Hero Section with Pathfinder Visual */}
      {questionsAnswered === 0 && !isComplete && (
        <div className="gradient-midnight border-b border-midnight-900">
          <div className="container py-12 lg:py-16">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              {/* Left: Welcome Content */}
              <div>
                <div className="inline-flex items-center gap-2 bg-pathfinder-500/20 px-4 py-2 rounded-full mb-6">
                  <Sparkles className="w-4 h-4 text-pathfinder-400" />
                  <span className="text-sm font-semibold text-pathfinder-300">AI-Powered Career Discovery</span>
                </div>
                
                <h1 className="font-display text-display-xl text-ivory-50 mb-4">
                  Discover Your Ideal Career Path
                </h1>
                <p className="text-lg text-ivory-200 mb-8 leading-relaxed">
                  Through intelligent questions and analysis, we'll help you uncover career paths 
                  that align with your passions, skills, and goals. Let's chart your course together.
                </p>

                {/* Quick Stats */}
                <div className="grid grid-cols-3 gap-6">
                  <div>
                    <div className="text-3xl font-display font-bold text-pathfinder-400 mb-1">
                      {MAX_QUESTIONS}
                    </div>
                    <div className="text-sm text-ivory-300">Questions</div>
                  </div>
                  <div>
                    <div className="text-3xl font-display font-bold text-pathfinder-400 mb-1">
                      ~15
                    </div>
                    <div className="text-sm text-ivory-300">Minutes</div>
                  </div>
                  <div>
                    <div className="text-3xl font-display font-bold text-pathfinder-400 mb-1">
                      ∞
                    </div>
                    <div className="text-sm text-ivory-300">Possibilities</div>
                  </div>
                </div>
              </div>

              {/* Right: Pathfinder Visual */}
              <div className="hidden lg:block">
                <PathfinderVisual animated className="opacity-90" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="container py-8 px-4 max-w-4xl">
        {/* Progress Bar (when in progress) */}
        {session && !isComplete && questionsAnswered > 0 && (
          <div className="glass-card rounded-xl p-6 mb-6 border-midnight-200">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <MapPin className="w-4 h-4 text-pathfinder-600" />
                  <span className="text-sm font-semibold text-midnight-900">
                    Your Progress
                  </span>
                </div>
                <p className="text-xs text-midnight-600">
                  Question {questionsAnswered + 1} of {MAX_QUESTIONS}
                </p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-display font-bold text-pathfinder-600">
                  {Math.round(progress)}%
                </div>
                <p className="text-xs text-midnight-600">Complete</p>
              </div>
            </div>
            {/* Visual Progress Bar */}
            <div className="relative h-3 bg-midnight-200 rounded-full overflow-hidden">
              <div 
                className="absolute inset-y-0 left-0 bg-pathfinder-500 rounded-full transition-all duration-500 pathfinder-glow"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <Alert variant="destructive" className="mb-6 border-error-500 bg-error-50">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Completion State */}
        {isComplete ? (
          <div className="space-y-6">
            {/* Success Card */}
            <Card className="glass-card border-success-200 bg-success-50/50">
              <CardHeader>
                <div className="flex items-start gap-4">
                  <div className="w-14 h-14 rounded-full bg-success-100 flex items-center justify-center flex-shrink-0 pathfinder-glow">
                    <CheckCircle className="h-8 w-8 text-success-600" />
                  </div>
                  <div className="flex-1">
                    <CardTitle className="font-display text-display-md text-midnight-950 mb-2">
                      Discovery Complete!
                    </CardTitle>
                    <CardDescription className="text-base text-midnight-700">
                      Excellent work! You've completed all {MAX_QUESTIONS} questions. We've gathered 
                      valuable insights about your career interests, skills, and aspirations.
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-4 mb-6">
                  <div className="flex items-center gap-3 p-3 bg-white rounded-lg">
                    <Award className="w-8 h-8 text-pathfinder-600" />
                    <div>
                      <div className="text-lg font-bold text-midnight-950">{questionsAnswered}</div>
                      <div className="text-xs text-midnight-600">Questions Answered</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-white rounded-lg">
                    <TrendingUp className="w-8 h-8 text-pathfinder-600" />
                    <div>
                      <div className="text-lg font-bold text-midnight-950">Ready</div>
                      <div className="text-xs text-midnight-600">Analysis Complete</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-white rounded-lg">
                    <Sparkles className="w-8 h-8 text-pathfinder-600" />
                    <div>
                      <div className="text-lg font-bold text-midnight-950">AI-Powered</div>
                      <div className="text-xs text-midnight-600">Personalized Results</div>
                    </div>
                  </div>
                </div>

                <div className="flex gap-3">
                  <Button 
                    onClick={handleComplete} 
                    disabled={processing}
                    className="bg-pathfinder-500 hover:bg-pathfinder-600 text-ivory-50 h-12 px-6 group"
                    size="lg"
                  >
                    {processing ? (
                      <>
                        <div className="w-4 h-4 border-2 border-ivory-50 border-t-transparent rounded-full animate-spin mr-2" />
                        Processing...
                      </>
                    ) : (
                      <>
                        View My Recommendations
                        <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* What's Next Card */}
            <Card className="glass-card border-midnight-200">
              <CardHeader>
                <CardTitle className="font-display text-midnight-950">What happens next?</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex gap-4">
                    <div className="w-8 h-8 rounded-full bg-pathfinder-500/10 flex items-center justify-center flex-shrink-0">
                      <span className="text-sm font-bold text-pathfinder-600">1</span>
                    </div>
                    <div>
                      <h4 className="font-semibold text-midnight-900 mb-1">AI Analysis</h4>
                      <p className="text-sm text-midnight-600">
                        Our intelligence engine analyzes your responses to identify patterns and insights
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-8 h-8 rounded-full bg-pathfinder-500/10 flex items-center justify-center flex-shrink-0">
                      <span className="text-sm font-bold text-pathfinder-600">2</span>
                    </div>
                    <div>
                      <h4 className="font-semibold text-midnight-900 mb-1">Career Matching</h4>
                      <p className="text-sm text-midnight-600">
                        We match your profile with careers that align with your strengths and interests
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-8 h-8 rounded-full bg-pathfinder-500/10 flex items-center justify-center flex-shrink-0">
                      <span className="text-sm font-bold text-pathfinder-600">3</span>
                    </div>
                    <div>
                      <h4 className="font-semibold text-midnight-900 mb-1">Personalized Roadmap</h4>
                      <p className="text-sm text-midnight-600">
                        Receive actionable steps and development paths tailored to your goals
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          /* Question Card */
          currentQuestion && (
            <div className="space-y-6">
              {/* Question Card */}
              <Card className="glass-card border-midnight-200">
                <CardHeader>
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-pathfinder-500/10 flex items-center justify-center flex-shrink-0">
                      <MessageCircle className="h-6 w-6 text-pathfinder-600" strokeWidth={2} />
                    </div>
                    <div className="flex-1">
                      <CardTitle className="font-display text-xl text-midnight-950 mb-3">
                        {currentQuestion.question_text}
                      </CardTitle>
                      <CardDescription className="text-midnight-600">
                        Take your time and be as detailed as you'd like. Your thoughtful answers help 
                        us understand you better and provide more accurate recommendations.
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <Textarea
                      placeholder="Share your thoughts here... Be specific and authentic."
                      value={answer}
                      onChange={(e) => setAnswer(e.target.value)}
                      rows={8}
                      className="resize-none bg-white border-midnight-200 focus:border-pathfinder-500 focus:ring-pathfinder-500 text-base"
                      disabled={processing}
                    />
                    
                    <div className="flex justify-between items-center pt-2">
                      <p className="text-sm text-midnight-600">
                        {answer.length} {answer.length === 1 ? 'character' : 'characters'}
                      </p>
                      
                      <Button
                        onClick={handleSubmitAnswer}
                        disabled={!answer.trim() || processing}
                        className="bg-pathfinder-500 hover:bg-pathfinder-600 text-ivory-50 h-11 px-6 group"
                      >
                        {processing ? (
                          <>
                            <div className="w-4 h-4 border-2 border-ivory-50 border-t-transparent rounded-full animate-spin mr-2" />
                            Submitting...
                          </>
                        ) : (
                          <>
                            Continue
                            <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Tips Card */}
              <Card className="glass-card border-pathfinder-200 bg-pathfinder-50/30">
                <CardContent className="pt-6">
                  <div className="flex items-start gap-3">
                    <Lightbulb className="w-5 h-5 text-pathfinder-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <h3 className="font-semibold mb-2 text-pathfinder-900">
                        💡 Tips for Better Results
                      </h3>
                      <ul className="text-sm text-pathfinder-800 space-y-1.5">
                        <li className="flex items-start gap-2">
                          <span className="text-pathfinder-600">•</span>
                          <span>Be honest and authentic in your responses</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-pathfinder-600">•</span>
                          <span>Share specific examples when possible</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-pathfinder-600">•</span>
                          <span>Think about both what you enjoy and what you're good at</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-pathfinder-600">•</span>
                          <span>Consider your values and what matters most to you</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )
        )}
      </div>
    </div>
  )
}
