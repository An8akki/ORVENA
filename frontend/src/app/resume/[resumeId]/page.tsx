'use client'

import { useEffect, useState, type ReactNode } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { AppLayout } from '@/components/layout/AppLayout'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { LoadingSpinner } from '@/components/shared/LoadingSpinner'
import { getResume, getResumeAnalysis, getResumeExtraction, type Resume, type ResumeAnalysis, type ResumeExtraction } from '@/lib/api/resume'
import { ArrowLeft, Award, Briefcase, CheckCircle2, FileText, GraduationCap, Lightbulb, Target, TrendingUp } from 'lucide-react'

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

function labelize(value: string) {
  return value.replace(/_/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function scoreColor(score: number) {
  if (score < 40) return 'bg-rose-500'
  if (score < 70) return 'bg-amber-500'
  return 'bg-teal-600'
}

function TextValue({ value }: { value: unknown }): ReactNode {
  if (value == null || value === '') return null
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
    return <span>{String(value)}</span>
  }
  if (Array.isArray(value)) {
    if (value.every((item) => typeof item === 'string' || typeof item === 'number')) {
      return <div className="flex flex-wrap gap-2">{value.map((item, index) => <span key={`${item}-${index}`} className="rounded-full bg-teal-50 px-3 py-1 text-xs font-medium text-teal-800">{String(item)}</span>)}</div>
    }
    return <div className="space-y-3">{value.map((item, index) => <RecordValue key={index} value={item} />)}</div>
  }
  if (typeof value === 'object') return <RecordValue value={value} />
  return null
}

function RecordValue({ value }: { value: unknown }) {
  if (value == null) return null
  if (typeof value !== 'object' || Array.isArray(value)) {
    return <div className="text-sm leading-6 text-slate-700"><TextValue value={value} /></div>
  }
  const entries = Object.entries(value as Record<string, unknown>).filter(([, item]) => item != null && item !== '')
  if (!entries.length) return null
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="grid gap-x-6 gap-y-3 sm:grid-cols-2">
        {entries.map(([key, item]) => (
          <div key={key} className="min-w-0">
            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">{labelize(key)}</p>
            <div className="text-sm leading-6 text-slate-800"><TextValue value={item} /></div>
          </div>
        ))}
      </div>
    </div>
  )
}

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

  const score = Math.max(0, Math.min(100, analysis?.overall_score ?? 0))
  const roleFits = [...(analysis?.role_fit ?? [])].sort((a, b) => b.score - a.score)

  return (
    <div className="container mx-auto max-w-5xl px-4 py-8">
      <Button variant="ghost" onClick={() => router.push('/resume')} className="mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Resumes
      </Button>
      {error ? (
        <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>
      ) : (
        <>
          <div className="mb-7 flex items-center gap-4">
            <div className="rounded-2xl bg-teal-50 p-3 text-teal-700"><FileText className="h-7 w-7" /></div>
            <div className="min-w-0">
              <h1 className="truncate text-2xl font-bold text-slate-900 sm:text-3xl">{resume?.title || 'Resume Analysis'}</h1>
              <p className="mt-1 truncate text-sm text-slate-500">{resume?.original_filename} <span aria-hidden="true">·</span> {extraction?.extraction_method || 'Resume'} extraction</p>
            </div>
          </div>
          {resume?.status === 'failed' && (
            <Alert className="mb-6"><AlertDescription>The file uploaded, but text extraction did not complete. You can still view the uploaded resume from your resumes list.</AlertDescription></Alert>
          )}
          {analysis && (
            <div className="space-y-6">
              <Card className="overflow-hidden border-0 bg-gradient-to-br from-teal-950 via-teal-900 to-slate-900 text-white shadow-lg">
                <CardContent className="grid gap-7 p-6 sm:grid-cols-[auto_1fr] sm:items-center sm:p-8">
                  <div className="mx-auto flex h-40 w-40 items-center justify-center rounded-full p-2" style={{ background: `conic-gradient(#5eead4 ${score}%, rgba(255,255,255,.16) ${score}% 100%)` }} aria-label={`Resume score ${score} out of 100`}>
                    <div className="flex h-full w-full flex-col items-center justify-center rounded-full bg-teal-950 ring-4 ring-teal-900">
                      <span className="text-4xl font-bold tabular-nums">{analysis.overall_score}</span>
                      <span className="text-xs text-teal-100">out of 100</span>
                    </div>
                  </div>
                  <div>
                    <div className="mb-3 flex flex-wrap items-center gap-2">
                      <span className="rounded-full bg-white/15 px-3 py-1 text-sm font-semibold">Grade {analysis.score_grade}</span>
                      <span className="rounded-full bg-teal-300/15 px-3 py-1 text-sm text-teal-100">{analysis.extraction_method || 'Statistical'} analysis</span>
                    </div>
                    <h2 className="text-2xl font-bold sm:text-3xl">Your resume snapshot</h2>
                    <p className="mt-2 max-w-2xl leading-7 text-teal-50/90">A quick view of what is already strong, what needs attention, and which roles your current experience supports.</p>
                    <div className="mt-5 flex flex-wrap gap-3">
                      <div className="rounded-xl bg-white/10 px-4 py-3"><p className="text-xs text-teal-100">ATS estimate</p><p className="mt-1 font-semibold">{analysis.estimated_pass_rate}</p></div>
                      <div className="rounded-xl bg-white/10 px-4 py-3"><p className="text-xs text-teal-100">ATS structure</p><p className="mt-1 font-semibold">{analysis.ats_friendly ? 'Readable' : 'Needs polish'}</p></div>
                      <div className="rounded-xl bg-white/10 px-4 py-3"><p className="text-xs text-teal-100">Role matches</p><p className="mt-1 font-semibold">{roleFits.length} evaluated</p></div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-slate-200 shadow-sm">
                <CardHeader className="pb-3"><CardTitle className="flex items-center gap-2 text-xl"><TrendingUp className="h-5 w-5 text-teal-700" />Score breakdown</CardTitle><p className="text-sm text-slate-500">See which parts of the resume contribute most to the overall score.</p></CardHeader>
                <CardContent className="grid gap-x-8 gap-y-5 sm:grid-cols-2">
                  {Object.entries(analysis.category_scores).map(([category, value]) => {
                    const categoryScore = Math.max(0, Math.min(100, value))
                    return <div key={category}>
                      <div className="mb-2 flex items-center justify-between gap-3"><span className="font-medium text-slate-700">{labelize(category)}</span><span className="text-sm font-bold tabular-nums text-slate-900">{value}/100</span></div>
                      <div className="h-2.5 overflow-hidden rounded-full bg-slate-100"><div className={`h-full rounded-full transition-all ${scoreColor(categoryScore)}`} style={{ width: `${categoryScore}%` }} /></div>
                    </div>
                  })}
                </CardContent>
              </Card>

              <div className="grid gap-5 lg:grid-cols-2">
                <Card className="border-emerald-100 bg-emerald-50/50 shadow-sm">
                  <CardHeader><CardTitle className="flex items-center gap-2 text-lg"><CheckCircle2 className="h-5 w-5 text-emerald-700" />What is working</CardTitle></CardHeader>
                  <CardContent>{analysis.strengths.length ? <ul className="space-y-3">{analysis.strengths.map((item) => <li key={item} className="flex gap-3 text-sm leading-6 text-slate-700"><span className="mt-2 h-2 w-2 shrink-0 rounded-full bg-emerald-600" />{item}</li>)}</ul> : <p className="text-sm text-slate-500">No strengths were returned for this analysis.</p>}</CardContent>
                </Card>
                <Card className="border-amber-100 bg-amber-50/50 shadow-sm">
                  <CardHeader><CardTitle className="flex items-center gap-2 text-lg"><Lightbulb className="h-5 w-5 text-amber-700" />Recommended improvements</CardTitle></CardHeader>
                  <CardContent>{analysis.suggestions.length ? <ol className="space-y-3">{analysis.suggestions.map((item, index) => <li key={item} className="flex gap-3 text-sm leading-6 text-slate-700"><span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-amber-100 text-xs font-bold text-amber-800">{index + 1}</span>{item}</li>)}</ol> : <p className="text-sm text-slate-500">No improvement suggestions were returned.</p>}</CardContent>
                </Card>
              </div>

              {roleFits.length > 0 && <Card className="border-slate-200 shadow-sm">
                <CardHeader><CardTitle className="flex items-center gap-2 text-xl"><Target className="h-5 w-5 text-teal-700" />Role fit</CardTitle><p className="text-sm text-slate-500">Match scores use skills and experience detected in this resume.</p></CardHeader>
                <CardContent className="grid gap-4 md:grid-cols-2">
                  {roleFits.map((fit, index) => <div key={fit.role} className="rounded-xl border border-slate-200 bg-white p-4">
                    <div className="mb-3 flex items-start justify-between gap-3"><div className="flex items-center gap-2"><Briefcase className="h-4 w-4 text-teal-700" /><h3 className="font-semibold text-slate-900">{fit.role}</h3></div><span className={`rounded-full px-2.5 py-1 text-sm font-bold tabular-nums ${index === 0 ? 'bg-teal-100 text-teal-800' : 'bg-slate-100 text-slate-700'}`}>{fit.score}%</span></div>
                    <div className="mb-3 h-2 overflow-hidden rounded-full bg-slate-100"><div className={`h-full rounded-full ${index === 0 ? 'bg-teal-600' : 'bg-sky-500'}`} style={{ width: `${Math.max(0, Math.min(100, fit.score))}%` }} /></div>
                    <p className="text-sm leading-6 text-slate-600">{fit.assessment}</p>
                    {!!fit.matched_skills.length && <div className="mt-3"><p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Evidence found</p><div className="flex flex-wrap gap-1.5">{fit.matched_skills.map((skill) => <span key={skill} className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs text-emerald-800">{skill}</span>)}</div></div>}
                    {!!fit.priority_gaps.length && <div className="mt-3"><p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Skills to build</p><div className="flex flex-wrap gap-1.5">{fit.priority_gaps.map((skill) => <span key={skill} className="rounded-full bg-amber-50 px-2.5 py-1 text-xs text-amber-800">{skill}</span>)}</div></div>}
                  </div>)}
                </CardContent>
              </Card>}

              {!!analysis.missing_elements.length && <Card className="border-rose-100 bg-rose-50/50 shadow-sm"><CardHeader><CardTitle className="flex items-center gap-2 text-lg"><Award className="h-5 w-5 text-rose-700" />Sections to strengthen</CardTitle></CardHeader><CardContent><div className="flex flex-wrap gap-2">{analysis.missing_elements.map((item) => <span key={item} className="rounded-full border border-rose-200 bg-white px-3 py-1.5 text-sm text-rose-800">{item}</span>)}</div></CardContent></Card>}
            </div>
          )}

          {extraction && <section className="mt-8 space-y-4">
            <div><h2 className="text-2xl font-bold text-slate-900">Resume evidence</h2><p className="mt-1 text-sm text-slate-500">Structured details extracted from your file and used to assess your profile.</p></div>
            <div className="grid gap-4 md:grid-cols-2">
              {sections.map(([key, label]) => {
                const value = extraction[key]
                if (value == null || value === '' || (Array.isArray(value) && value.length === 0)) return null
                const Icon = key === 'education' ? GraduationCap : key === 'experience' || key === 'projects' ? Briefcase : key === 'achievements' || key === 'certifications' ? Award : FileText
                return <Card key={key} className="border-slate-200 shadow-sm"><CardHeader className="pb-3"><CardTitle className="flex items-center gap-2 text-base"><Icon className="h-4 w-4 text-teal-700" />{label}</CardTitle></CardHeader><CardContent className="space-y-3">{typeof value === 'string' ? <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">{value}</p> : <TextValue value={value} />}</CardContent></Card>
              })}
            </div>
            {extraction.raw_text && <details className="group rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><summary className="cursor-pointer list-none font-medium text-slate-700 marker:hidden"><span className="inline-flex items-center gap-2"><FileText className="h-4 w-4 text-teal-700" />View full extracted text<span className="text-xs text-slate-400 group-open:hidden">(expand)</span></span></summary><pre className="mt-4 max-h-[32rem] overflow-auto whitespace-pre-wrap break-words rounded-lg bg-slate-50 p-4 text-sm leading-6 text-slate-700">{extraction.raw_text}</pre></details>}
          </section>}
          {!extraction && <Alert><AlertDescription>No analysis data is available for this resume yet.</AlertDescription></Alert>}
        </>
      )}
    </div>
  )
}

export default function ResumeAnalysisPage() {
  return <AuthGuard><AppLayout><ResumeAnalysisContent /></AppLayout></AuthGuard>
}
