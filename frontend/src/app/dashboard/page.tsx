'use client'

import { AuthGuard } from '@/components/auth/AuthGuard'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Target, FileText, Briefcase, TrendingUp, User, ArrowRight, Sparkles } from 'lucide-react'
import Link from 'next/link'

function DashboardContent() {
  return (
    <AppLayout>
      <div className="container py-8">
        {/* Hero Section */}
        <div className="mb-8">
          <h1 className="font-display text-display-lg text-midnight-950 mb-2">
            Welcome back!
          </h1>
          <p className="text-lg text-midnight-600">
            Continue your career journey with intelligent guidance
          </p>
        </div>

        {/* Quick Actions Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
          {/* Career Discovery Card */}
          <Link href="/career/discovery">
            <Card className="glass-card card-hover h-full border-midnight-200">
              <CardHeader>
                <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-pathfinder-500/10 mb-3 transition-colors">
                  <Target className="h-7 w-7 text-pathfinder-600" strokeWidth={2} />
                </div>
                <CardTitle className="text-lg font-display text-midnight-950">
                  Career Discovery
                </CardTitle>
                <CardDescription className="text-midnight-600">
                  Find your ideal career path with AI guidance
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  className="w-full bg-pathfinder-500 hover:bg-pathfinder-600 text-ivory-50 group/btn"
                  size="sm"
                >
                  Start Discovery
                  <ArrowRight className="w-4 h-4 ml-2 group-hover/btn:translate-x-1 transition-transform" />
                </Button>
              </CardContent>
            </Card>
          </Link>

          {/* Resume Analyzer Card */}
          <Link href="/resume">
            <Card className="glass-card card-hover h-full border-midnight-200">
              <CardHeader>
                <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-pathfinder-500/10 mb-3 transition-colors">
                  <FileText className="h-7 w-7 text-pathfinder-600" strokeWidth={2} />
                </div>
                <CardTitle className="text-lg font-display text-midnight-950">
                  Resume Analyzer
                </CardTitle>
                <CardDescription className="text-midnight-600">
                  Analyze and optimize your resume with AI
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  className="w-full bg-pathfinder-500 hover:bg-pathfinder-600 text-ivory-50 group/btn"
                  size="sm"
                >
                  Analyze Resume
                  <ArrowRight className="w-4 h-4 ml-2 group-hover/btn:translate-x-1 transition-transform" />
                </Button>
              </CardContent>
            </Card>
          </Link>

          {/* Job Recommender Card */}
          <Link href="/jobs">
            <Card className="glass-card card-hover h-full border-midnight-200">
              <CardHeader>
                <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-pathfinder-500/10 mb-3 transition-colors">
                  <Briefcase className="h-7 w-7 text-pathfinder-600" strokeWidth={2} />
                </div>
                <CardTitle className="text-lg font-display text-midnight-950">
                  Job Recommender
                </CardTitle>
                <CardDescription className="text-midnight-600">
                  Get personalized job recommendations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  className="w-full bg-pathfinder-500 hover:bg-pathfinder-600 text-ivory-50 group/btn"
                  size="sm"
                >
                  Find Jobs
                  <ArrowRight className="w-4 h-4 ml-2 group-hover/btn:translate-x-1 transition-transform" />
                </Button>
              </CardContent>
            </Card>
          </Link>
        </div>

        {/* Two-column layout for additional content */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Profile Completion */}
          <Card className="glass-card border-midnight-200 lg:col-span-2">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-pathfinder-600" />
                <CardTitle className="font-display text-midnight-950">
                  Complete Your Profile
                </CardTitle>
              </div>
              <CardDescription className="text-midnight-600">
                Help us provide better recommendations by completing your profile
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Progress bar */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-midnight-700">Profile completion</span>
                    <span className="text-sm font-semibold text-pathfinder-600">40%</span>
                  </div>
                  <div className="w-full h-2 bg-midnight-200 rounded-full overflow-hidden">
                    <div className="h-full bg-pathfinder-500 rounded-full" style={{ width: '40%' }} />
                  </div>
                </div>

                {/* Action items */}
                <div className="space-y-3 pt-2">
                  <div className="flex items-center justify-between p-3 rounded-lg bg-ivory-100 dark:bg-midnight-900">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-pathfinder-500/20 flex items-center justify-center">
                        <User className="w-4 h-4 text-pathfinder-600" />
                      </div>
                      <div>
                        <p className="font-medium text-sm text-midnight-900">Basic Information</p>
                        <p className="text-xs text-midnight-600">
                          Add your education and work experience
                        </p>
                      </div>
                    </div>
                    <Link href="/profile">
                      <Button variant="outline" size="sm" className="border-pathfinder-500 text-pathfinder-600 hover:bg-pathfinder-50">
                        Complete
                      </Button>
                    </Link>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card className="glass-card border-midnight-200">
            <CardHeader>
              <CardTitle className="font-display text-midnight-950">Your Progress</CardTitle>
              <CardDescription className="text-midnight-600">
                Career development overview
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex items-baseline gap-2 mb-1">
                    <span className="text-3xl font-display font-bold text-midnight-950">0</span>
                    <span className="text-sm text-midnight-600">skills assessed</span>
                  </div>
                  <div className="h-1 bg-midnight-200 rounded-full" />
                </div>
                
                <div>
                  <div className="flex items-baseline gap-2 mb-1">
                    <span className="text-3xl font-display font-bold text-midnight-950">0</span>
                    <span className="text-sm text-midnight-600">career paths explored</span>
                  </div>
                  <div className="h-1 bg-midnight-200 rounded-full" />
                </div>

                <div>
                  <div className="flex items-baseline gap-2 mb-1">
                    <span className="text-3xl font-display font-bold text-midnight-950">0</span>
                    <span className="text-sm text-midnight-600">milestones achieved</span>
                  </div>
                  <div className="h-1 bg-midnight-200 rounded-full" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  )
}

export default function DashboardPage() {
  return (
    <AuthGuard>
      <DashboardContent />
    </AuthGuard>
  )
}
