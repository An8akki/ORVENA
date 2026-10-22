'use client'

import { AuthGuard } from '@/components/auth/AuthGuard'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Target, FileText, Briefcase, ArrowRight, Rocket } from 'lucide-react'
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
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
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

          {/* Project Launchpad Card */}
          <Link href="/projects">
            <Card className="glass-card card-hover h-full border-midnight-200">
              <CardHeader>
                <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-amber-500/10 mb-3 transition-colors">
                  <Rocket className="h-7 w-7 text-amber-600" strokeWidth={2} />
                </div>
                <CardTitle className="text-lg font-display text-midnight-950">
                  Project Launchpad
                </CardTitle>
                <CardDescription className="text-midnight-600">
                  Discover ideas, track milestones & evaluate projects
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  className="w-full bg-amber-600 hover:bg-amber-700 text-ivory-50 group/btn"
                  size="sm"
                >
                  Explore Launchpad
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
