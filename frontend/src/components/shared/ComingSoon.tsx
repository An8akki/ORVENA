/**
 * ComingSoon Component
 * Placeholder for pages under development
 */

'use client'

import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'
import { LucideIcon, Sparkles, ArrowLeft } from 'lucide-react'

interface ComingSoonProps {
  icon: LucideIcon
  title: string
  description: string
  features?: string[]
}

export const ComingSoon: React.FC<ComingSoonProps> = ({
  icon: Icon,
  title,
  description,
  features = [],
}) => {
  const router = useRouter()

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-8">
      <Card className="glass-card border-midnight-200 max-w-2xl w-full">
        <CardContent className="pt-16 pb-16 text-center">
          <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-pathfinder-500/10 flex items-center justify-center">
            <Icon className="h-12 w-12 text-pathfinder-600" strokeWidth={2} />
          </div>
          
          <div className="inline-flex items-center gap-2 bg-pathfinder-500/20 px-4 py-2 rounded-full mb-6">
            <Sparkles className="w-4 h-4 text-pathfinder-600" />
            <span className="text-sm font-semibold text-pathfinder-800">Coming Soon</span>
          </div>

          <h1 className="font-display text-display-md text-midnight-950 mb-4">
            {title}
          </h1>
          <p className="text-lg text-midnight-600 mb-8 max-w-lg mx-auto">
            {description}
          </p>

          {features.length > 0 && (
            <div className="mb-8">
              <h3 className="font-semibold text-midnight-900 mb-4">What to expect:</h3>
              <ul className="text-left max-w-md mx-auto space-y-2">
                {features.map((feature, index) => (
                  <li key={index} className="flex items-start gap-2 text-midnight-700">
                    <span className="text-pathfinder-600 mt-1">•</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex gap-3 justify-center">
            <Button
              onClick={() => router.push('/dashboard')}
              className="bg-pathfinder-500 hover:bg-pathfinder-600 text-ivory-50"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default ComingSoon
