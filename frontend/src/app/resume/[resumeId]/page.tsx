'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { AppLayout } from '@/components/layout/AppLayout'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { LoadingSpinner } from '@/components/shared/LoadingSpinner'
import { getResume, getResumeAnalysis, getResumeExtraction, type Resume, type ResumeAnalysis, type ResumeExtraction } from '@/lib/api/resume'
import { ArrowLeft, FileText, Target } from 'lucide-react'

const sections: Array<[keyof ResumeExtraction, string]> = [
  ['contact_info', 'Contact Information'],
  ['summary', 'Professional Summary'],
  ['education', 'Education'],
  ['experience', 'Experience'],
  ['projects', 'Projects'],
  ['skills', 'Skills'],
  ['certifications', 'Certifications'],
  ['achievements', 'Achievements'],
]

function ResumeAnalysisContent() {
  const router = useRouter()
  const params = useParams()
  const resumeId = params.resumeId as string
  const [resume, setResume] = useState<Resume | null>(null)
  const [extraction, setExtraction] = useState<ResumeExtraction | null>(null)
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const [resumeData, extractionData, analysisData] = await Promise.all([
          getResume(resumeId),
          getResumeExtraction(resumeId),
          getResumeAnalysis(resumeId),
        ])
        setResume(resumeData)
        setExtraction({ ...extractionData, ...analysisData.normalized_extraction })
        setAnalysis(analysisData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Could not load resume analysis')
      } finally {
        setLoading(false)
      }
    }
    if (resumeId) void load()
  }, [resumeId])

  if (loading) return <div className="flex min-h-[60vh] items-center justify-center"><LoadingSpinner size="lg" /></div>

  return (
    <div className="container mx-auto max-w-4xl px-4 py-8">
      <Button variant="ghost" onClick={() => router.push('/resume')} className="mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Resumes
      </Button>
      {error ? (
        <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>
      ) : (
        <>
          <div className="mb-6 flex items-center gap-3">
            <FileText className="h-8 w-8 text-pathfinder-teal" />
            <div>
              <h1 className="text-3xl font-bold">{resume?.title || 'Resume Analysis'}</h1>
              <p className="text-muted-foreground">{resume?.original_filename} · {extraction?.extraction_method || 'Resume'} extraction</p>
            </div>
          </div>
          {resume?.status === 'failed' && (
            <Alert className="mb-6"><AlertDescription>
              The file uploaded, but text extraction did not complete. You can still view the uploaded resume from your resumes list.
            </AlertDescription></Alert>
          )}
          {analysis && (
            <>
              <Card className="mb-6">
                <CardHeader>
                  <CardTitle>Resume Score: {analysis.overall_score}/100 · Grade {analysis.score_grade}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-5">
                  <p className="text-sm text-muted-foreground">
                    Statistical ATS estimate: {analysis.estimated_pass_rate}. {analysis.ats_friendly ? 'The document has standard ATS-readable sections.' : 'Improve section structure and parsing consistency for applicant tracking systems.'}
                  </p>
                  <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {Object.entries(analysis.category_scores).map(([category, score]) => (
                      <div key={category} className="rounded-lg border p-3">
                        <p className="text-sm capitalize text-muted-foreground">{category}</p>
                        <p className="text-xl font-semibold">{score}/100</p>
                      </div>
                    ))}
                  </div>
                  {analysis.strengths.length > 0 && (
                    <div><h2 className="mb-2 font-semibold">What is working</h2><ul className="list-disc space-y-1 pl-5 text-sm">{analysis.strengths.map((item) => <li key={item}>{item}</li>)}</ul></div>
                  )}
                  {analysis.suggestions.length > 0 && (
                    <div><h2 className="mb-2 font-semibold">Improvements to make</h2><ul className="list-disc space-y-1 pl-5 text-sm">{analysis.suggestions.map((item) => <li key={item}>{item}</li>)}</ul></div>
                  )}
                  <div>
                    <h2 className="mb-3 flex items-center gap-2 font-semibold"><Target className="h-4 w-4" />Role fit and priority gaps</h2>
                    <div className="grid gap-3 md:grid-cols-2">
                      {analysis.role_fit.map((fit) => (
                        <div key={fit.role} className="rounded-lg border p-4">
                          <div className="mb-2 flex items-center justify-between"><h3 className="font-medium">{fit.role}</h3><span className="font-semibold">{fit.score}%</span></div>
                          <p className="mb-2 text-sm text-muted-foreground">{fit.assessment}</p>
                          {fit.matched_skills.length > 0 && <p className="text-sm"><strong>Evidence:</strong> {fit.matched_skills.join(', ')}</p>}
                          {fit.priority_gaps.length > 0 && <p className="mt-1 text-sm"><strong>Build:</strong> {fit.priority_gaps.join(', ')}</p>}
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
              {analysis.missing_elements.length > 0 && (
                <Alert className="mb-6"><AlertDescription>Sections to strengthen: {analysis.missing_elements.join(', ')}.</AlertDescription></Alert>
              )}
            </>
          )}
          {extraction && sections.map(([key, label]) => {
            const value = extraction[key]
            if (value == null || value === '' || (Array.isArray(value) && value.length === 0)) return null
            return (
              <Card key={key} className="mb-4">
                <CardHeader><CardTitle>{label}</CardTitle></CardHeader>
                <CardContent>
                  <pre className="whitespace-pre-wrap break-words font-sans text-sm">
                    {typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
                  </pre>
                </CardContent>
              </Card>
            )
          })}
          {extraction?.raw_text && (
            <Card>
              <CardHeader><CardTitle>Extracted Resume Text</CardTitle></CardHeader>
              <CardContent><pre className="whitespace-pre-wrap break-words font-sans text-sm">{extraction.raw_text}</pre></CardContent>
            </Card>
          )}
          {!extraction && <Alert><AlertDescription>No analysis data is available for this resume yet.</AlertDescription></Alert>}
        </>
      )}
    </div>
  )
}

export default function ResumeAnalysisPage() {
  return <AuthGuard><AppLayout><ResumeAnalysisContent /></AppLayout></AuthGuard>
}
