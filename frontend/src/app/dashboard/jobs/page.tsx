'use client'

import { AuthGuard } from '@/components/auth/AuthGuard'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Briefcase, MapPin, Clock, DollarSign, ExternalLink } from 'lucide-react'

export default function JobsPage() {
  return (
    <AuthGuard>
      <JobsContent />
    </AuthGuard>
  )
}

function JobsContent() {
  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Job Opportunities</h1>
        <p className="text-muted-foreground">
          Find jobs that match your skills and career goals
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Coming Soon</CardTitle>
          <CardDescription>
            Job matching and recommendations feature is currently under development
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <Briefcase className="h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Job Matching Feature</h3>
            <p className="text-muted-foreground mb-6 max-w-md">
              We're working on bringing you personalized job recommendations based on your profile,
              skills, and career goals.
            </p>
            <div className="flex gap-4">
              <Button asChild variant="outline">
                <a href="/profile">Complete Your Profile</a>
              </Button>
              <Button asChild>
                <a href="/career/discovery">Start Career Discovery</a>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
