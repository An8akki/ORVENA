'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import {
  Rocket,
  Compass,
  ExternalLink,
  Github,
  CheckCircle2,
  Lock,
  ArrowLeft,
  Share2,
  Check,
  Eye,
  Calendar,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { api } from '@/lib/api-client'

interface ShowcaseData {
  id: string
  slug: string
  is_public: boolean
  headline?: string
  problem_solution_summary?: string
  key_contributions?: string[]
  outcomes_metrics?: string[]
  skills_highlighted?: string[]
  view_count: number
  project_title: string
  project_description: string
  technologies: string[]
  github_url?: string
  demo_url?: string
  stage?: string
  created_at: string
}

export default function ProjectShowcasePage() {
  const params = useParams()
  const slug = params.slug as string

  const [showcase, setShowcase] = useState<ShowcaseData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    loadShowcase()
  }, [slug])

  const loadShowcase = async () => {
    try {
      setLoading(true)
      const data = await api.get<ShowcaseData>(`/api/v1/launchpad/showcase/${slug}`)
      setShowcase(data)
    } catch (err: any) {
      setError(err.message || 'Showcase not found or private.')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-ivory-50 dark:bg-midnight-950 flex items-center justify-center p-4">
        <div className="text-center space-y-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-amber-600 border-t-transparent mx-auto" />
          <p className="text-xs text-midnight-500">Loading project showcase...</p>
        </div>
      </div>
    )
  }

  if (error || !showcase) {
    return (
      <div className="min-h-screen bg-ivory-50 dark:bg-midnight-950 flex items-center justify-center p-4">
        <Card className="max-w-md w-full p-8 text-center border-midnight-200 dark:border-midnight-800">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-500/10 text-rose-600 mb-4">
            <Lock className="h-6 w-6" />
          </div>
          <h2 className="text-lg font-bold text-midnight-950 dark:text-ivory-50 mb-1">
            Private or Unavailable
          </h2>
          <p className="text-xs text-midnight-500 mb-6">
            {error || 'This project showcase is currently set to private by its author.'}
          </p>
          <Link href="/projects">
            <Button size="sm" variant="outline">
              Return to Launchpad
            </Button>
          </Link>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-ivory-50 dark:bg-midnight-950 text-midnight-950 dark:text-ivory-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Top Navbar */}
        <div className="flex items-center justify-between border-b border-midnight-200 dark:border-midnight-800 pb-4">
          <Link href="/projects" className="inline-flex items-center gap-2 text-xs text-midnight-500 hover:text-midnight-900 dark:hover:text-ivory-50 font-medium">
            <ArrowLeft className="h-4 w-4" />
            Back to Orvena
          </Link>

          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1 text-[11px] text-midnight-400">
              <Eye className="h-3 w-3" />
              {showcase.view_count} views
            </span>
            <Button size="sm" variant="outline" onClick={handleCopy} className="gap-1.5 text-xs">
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Share2 className="h-3.5 w-3.5" />}
              {copied ? 'Link Copied' : 'Share'}
            </Button>
          </div>
        </div>

        {/* Hero Banner */}
        <div className="rounded-3xl border border-midnight-200 dark:border-midnight-800 bg-white dark:bg-midnight-900/80 p-8 shadow-sm space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-amber-500/10 text-amber-700 dark:text-amber-400 px-3 py-1 text-xs font-semibold uppercase tracking-wider">
              {showcase.stage || 'Completed Project'}
            </span>
            <span className="rounded-md border border-midnight-200 dark:border-midnight-700 px-2.5 py-0.5 text-xs text-midnight-600 dark:text-midnight-300">
              Verified Showcase
            </span>
          </div>

          <h1 className="font-display text-3xl sm:text-4xl font-bold tracking-tight text-midnight-950 dark:text-ivory-50">
            {showcase.project_title}
          </h1>

          {showcase.headline && (
            <p className="text-base font-medium text-amber-600 dark:text-amber-400">
              {showcase.headline}
            </p>
          )}

          <p className="text-sm text-midnight-600 dark:text-midnight-300 leading-relaxed max-w-3xl">
            {showcase.project_description}
          </p>

          {/* Links Row */}
          <div className="flex flex-wrap items-center gap-3 pt-2">
            {showcase.demo_url && (
              <a
                href={showcase.demo_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-ivory-50 px-4 py-2 text-xs font-semibold shadow-sm transition-colors"
              >
                <ExternalLink className="h-3.5 w-3.5" />
                Launch Live Demo
              </a>
            )}

            {showcase.github_url && (
              <a
                href={showcase.github_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 rounded-xl border border-midnight-300 dark:border-midnight-700 bg-white dark:bg-midnight-950 hover:bg-midnight-100 dark:hover:bg-midnight-900 px-4 py-2 text-xs font-semibold text-midnight-900 dark:text-ivory-50 transition-colors"
              >
                <Github className="h-3.5 w-3.5" />
                View Source Repository
              </a>
            )}
          </div>
        </div>

        {/* Technical Architecture & Stack */}
        <Card className="border-midnight-200 dark:border-midnight-800 p-6 space-y-4">
          <h2 className="font-display font-semibold text-lg text-midnight-950 dark:text-ivory-50">
            Technical Stack & Toolchain
          </h2>
          <div className="flex flex-wrap gap-2">
            {(showcase.skills_highlighted || showcase.technologies || []).map((tech) => (
              <span
                key={tech}
                className="rounded-lg border border-midnight-200 dark:border-midnight-800 bg-midnight-50 dark:bg-midnight-950 px-3 py-1 text-xs font-medium text-midnight-800 dark:text-midnight-200"
              >
                {tech}
              </span>
            ))}
          </div>
        </Card>

        {/* Problem & Solution Synthesis */}
        {showcase.problem_solution_summary && (
          <Card className="border-midnight-200 dark:border-midnight-800 p-6 space-y-3">
            <h2 className="font-display font-semibold text-lg text-midnight-950 dark:text-ivory-50">
              Problem & Architecture Approach
            </h2>
            <div className="whitespace-pre-line text-xs sm:text-sm text-midnight-600 dark:text-midnight-300 leading-relaxed">
              {showcase.problem_solution_summary}
            </div>
          </Card>
        )}

        {/* Contributions & Demonstrated Outcomes */}
        {showcase.key_contributions && showcase.key_contributions.length > 0 && (
          <Card className="border-midnight-200 dark:border-midnight-800 p-6 space-y-3">
            <h2 className="font-display font-semibold text-lg text-midnight-950 dark:text-ivory-50">
              Key Engineering Contributions
            </h2>
            <ul className="space-y-2 text-xs sm:text-sm text-midnight-600 dark:text-midnight-300">
              {showcase.key_contributions.map((c, i) => (
                <li key={i} className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                  <span>{c}</span>
                </li>
              ))}
            </ul>
          </Card>
        )}

        {/* Footer Attribution */}
        <div className="text-center pt-8 border-t border-midnight-200 dark:border-midnight-800 text-xs text-midnight-400">
          Published with{' '}
          <Link href="/" className="font-semibold text-amber-600 hover:underline">
            ORVENA Career Intelligence Platform
          </Link>
        </div>
      </div>
    </div>
  )
}
