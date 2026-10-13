'use client'

import { AuthGuard } from '@/components/auth/AuthGuard'
import { AppLayout } from '@/components/layout/AppLayout'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api-client'
import {
  Briefcase,
  MapPin,
  DollarSign,
  TrendingUp,
  Clock,
  Star,
  CheckCircle,
  AlertCircle,
  Sparkles,
  Target,
  Award,
  BarChart3,
} from 'lucide-react'

interface Job {
  id: string
  title: string
  company: string
  location: string
  salaryMin: number
  salaryMax: number
  matchScore: number
  growthRate: number
  demandLevel: 'High' | 'Medium' | 'Low'
  matchedSkills: string[]
  missingSkills: string[]
  description: string
  requirements: string[]
  jobUrl?: string  // External job posting URL
  companyWebsite?: string
}

export default function JobsPage() {
  return (
    <AuthGuard>
      <AppLayout>
        <JobsContent />
      </AppLayout>
    </AuthGuard>
  )
}

function JobsContent() {
  const [loading, setLoading] = useState(true)
  const [jobs, setJobs] = useState<Job[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.get<Job[]>('/api/v1/jobs/recommendations')
      .then(setJobs)
      .catch((err) => setError(err instanceof Error ? err.message : 'Could not load career matches'))
      .finally(() => setLoading(false))
  }, [])

  const averageMatch = jobs.length
    ? Math.round(jobs.reduce((sum, job) => sum + job.matchScore, 0) / jobs.length)
    : 0
  const averageGrowth = jobs.length
    ? Math.round(jobs.reduce((sum, job) => sum + job.growthRate, 0) / jobs.length)
    : 0
  const demandLevel = jobs.some((job) => job.demandLevel === 'High') ? 'High' : jobs.length ? 'Medium' : '—'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Job Recommender</h1>
          <p className="text-gray-600 mt-1">
            Personalized job matches based on your profile and skills
          </p>
        </div>
        <div className="flex items-center gap-2 bg-blue-50 px-4 py-2 rounded-lg border border-blue-200">
          <Sparkles className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-medium text-blue-700">Profile + Answer Matching</span>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Briefcase className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{loading ? '…' : jobs.length}</div>
              <div className="text-sm text-gray-600">Matched Jobs</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{loading ? '…' : `${averageMatch}%`}</div>
              <div className="text-sm text-gray-600">Avg Match Score</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{loading ? '…' : `${averageGrowth}%`}</div>
              <div className="text-sm text-gray-600">Avg Growth Rate</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <Target className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{loading ? '…' : demandLevel}</div>
              <div className="text-sm text-gray-600">Market Demand</div>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works Banner */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200 p-6">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center flex-shrink-0">
            <BarChart3 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Smart Job Matching Algorithm
            </h3>
            <p className="text-gray-700 mb-3">
              Your profile, resume skills, education, and saved career discovery answers are scored locally.
              Each role match includes evidence, skill gaps, market context, and a search link for current openings.
            </p>
            <div className="flex flex-wrap gap-3 text-sm">
              <div className="flex items-center gap-1 text-blue-700">
                <CheckCircle className="w-4 h-4" />
                <span className="font-medium">Skills Match: 40%</span>
              </div>
              <div className="flex items-center gap-1 text-purple-700">
                <CheckCircle className="w-4 h-4" />
                <span className="font-medium">Education: 25%</span>
              </div>
              <div className="flex items-center gap-1 text-green-700">
                <CheckCircle className="w-4 h-4" />
                <span className="font-medium">Experience: 20%</span>
              </div>
              <div className="flex items-center gap-1 text-orange-700">
                <CheckCircle className="w-4 h-4" />
                <span className="font-medium">Market Demand: 10%</span>
              </div>
              <div className="flex items-center gap-1 text-teal-700">
                <CheckCircle className="w-4 h-4" />
                <span className="font-medium">Career Interests: 5%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Job Listings */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">
            Top Recommendations for You
          </h2>
        </div>

        {error && <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>}
        {loading && <div className="rounded-lg border bg-white p-8 text-center text-gray-600">Matching your profile, resume and saved answers…</div>}
        {!loading && !error && jobs.length === 0 && <div className="rounded-lg border bg-white p-8 text-center text-gray-600">Add skills or complete career discovery to get profile-specific role matches.</div>}
        {jobs.map((job, index) => (
          <div
            key={job.id}
            className="bg-white rounded-lg shadow-sm border border-gray-200 card-hover cursor-pointer"
            onClick={() => job.jobUrl && window.open(job.jobUrl, '_blank', 'noopener,noreferrer')}
          >
            <div className="p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    {index === 0 && (
                      <div className="flex items-center gap-1 bg-yellow-100 px-2 py-1 rounded-full">
                        <Star className="w-3 h-3 text-yellow-600 fill-yellow-600" />
                        <span className="text-xs font-semibold text-yellow-700">Best Match</span>
                      </div>
                    )}
                    <div className="flex items-center gap-1 bg-green-100 px-2 py-1 rounded-full">
                      <TrendingUp className="w-3 h-3 text-green-600" />
                      <span className="text-xs font-semibold text-green-700">
                        {job.growthRate}% Growth
                      </span>
                    </div>
                    <div className={`flex items-center gap-1 px-2 py-1 rounded-full ${
                      job.demandLevel === 'High' 
                        ? 'bg-blue-100 text-blue-700'
                        : job.demandLevel === 'Medium'
                        ? 'bg-orange-100 text-orange-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      <span className="text-xs font-semibold">
                        {job.demandLevel} Demand
                      </span>
                    </div>
                  </div>
                  
                  <h3 className="text-xl font-semibold text-gray-900 mb-1">
                    {job.title}
                  </h3>
                  <p className="text-lg text-blue-600 font-medium mb-3">{job.company}</p>
                  
                  <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <MapPin className="w-4 h-4" />
                      {job.location}
                    </div>
                    <div className="flex items-center gap-1">
                      <DollarSign className="w-4 h-4" />
                      ${job.salaryMin.toLocaleString()} - ${job.salaryMax.toLocaleString()}
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      Career fit profile
                    </div>
                  </div>
                </div>

                {/* Match Score */}
                <div className="flex flex-col items-center ml-6">
                  <div className="relative w-20 h-20">
                    <svg className="w-20 h-20 transform -rotate-90">
                      <circle
                        cx="40"
                        cy="40"
                        r="36"
                        stroke="#e5e7eb"
                        strokeWidth="8"
                        fill="none"
                      />
                      <circle
                        cx="40"
                        cy="40"
                        r="36"
                        stroke="#3b82f6"
                        strokeWidth="8"
                        fill="none"
                        strokeDasharray={`${2 * Math.PI * 36}`}
                        strokeDashoffset={`${2 * Math.PI * 36 * (1 - job.matchScore / 100)}`}
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <div className="text-2xl font-bold text-gray-900">{job.matchScore}%</div>
                      <div className="text-xs text-gray-600">Match</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Description */}
              <p className="text-gray-700 mb-4">{job.description}</p>

              {/* Requirements */}
              <div className="mb-4">
                  <h4 className="text-sm font-semibold text-gray-900 mb-2">Skills to build next:</h4>
                <ul className="space-y-1">
                  {job.requirements.map((req, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                      <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                      {req}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Skills Analysis */}
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    Matched Skills ({job.matchedSkills.length})
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {job.matchedSkills.map((skill, i) => (
                      <span
                        key={i}
                        className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm border border-green-200"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-orange-600" />
                    Skills to Learn ({job.missingSkills.length})
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {job.missingSkills.map((skill, i) => (
                      <span
                        key={i}
                        className="px-3 py-1 bg-orange-50 text-orange-700 rounded-full text-sm border border-orange-200"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    job.jobUrl && window.open(job.jobUrl, '_blank');
                  }}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={!job.jobUrl}
                >
                  Search Current Openings
                </button>
                <button 
                  onClick={(e) => e.stopPropagation()}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                >
                  Save for Later
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State Prompt */}
      <div className="bg-blue-50 rounded-xl border border-blue-200 p-6 text-center">
        <Award className="w-12 h-12 text-blue-600 mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Want a Stronger Match?
        </h3>
        <p className="text-gray-600 mb-4">
          Add skills and project evidence to your profile. These local matches update from your saved answers and resume.
        </p>
        <div className="flex gap-3 justify-center">
          <button onClick={() => { window.location.href = '/profile' }} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium">
            Complete Profile
          </button>
          <button onClick={() => { window.location.href = '/resume' }} className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium">
            Upload Resume
          </button>
        </div>
      </div>
    </div>
  )
}
