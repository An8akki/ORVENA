'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  uploadResume,
  getResumes,
  setPrimaryResume,
  deleteResume,
  type Resume,
} from '@/lib/api/resume'
import {
  FileText,
  Upload,
  Trash2,
  Star,
  CheckCircle,
  XCircle,
  Clock,
  Sparkles,
  Plus,
  ArrowRight,
  AlertCircle,
  FileCheck,
  Zap,
} from 'lucide-react'

export default function ResumePage() {
  return (
    <AuthGuard>
      <AppLayout>
        <ResumeContent />
      </AppLayout>
    </AuthGuard>
  )
}

function ResumeContent() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [resumes, setResumes] = useState<Resume[]>([])
  const [error, setError] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [title, setTitle] = useState('')
  const [showUpload, setShowUpload] = useState(false)

  useEffect(() => {
    loadResumes()
  }, [])

  async function loadResumes() {
    try {
      setLoading(true)
      const data = await getResumes()
      setResumes(data)
    } catch (err: any) {
      let errorMessage = 'Failed to load resumes';
      
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
      console.error('Load resumes error:', err);
    } finally {
      setLoading(false)
    }
  }

  async function handleUpload() {
    if (!selectedFile || !title.trim()) return

    try {
      setUploading(true)
      setError(null)
      await uploadResume(selectedFile, title.trim())
      setSelectedFile(null)
      setTitle('')
      setShowUpload(false)
      await loadResumes()
    } catch (err: any) {
      let errorMessage = 'Failed to upload resume';
      
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
      console.error('Upload resume error:', err);
    } finally {
      setUploading(false)
    }
  }

  async function handleSetPrimary(resumeId: string) {
    try {
      await setPrimaryResume(resumeId)
      await loadResumes()
    } catch (err: any) {
      let errorMessage = 'Failed to set primary resume';
      
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
      console.error('Set primary resume error:', err);
    }
  }

  async function handleDelete(resumeId: string) {
    if (!confirm('Are you sure you want to delete this resume?')) return

    try {
      await deleteResume(resumeId)
      await loadResumes()
    } catch (err: any) {
      let errorMessage = 'Failed to delete resume';
      
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
      console.error('Delete resume error:', err);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-pathfinder-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm text-midnight-600">Loading your resumes...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <div className="border-b border-midnight-200 bg-gradient-to-br from-ivory-50 to-pathfinder-50/20">
        <div className="container py-12">
          <div className="max-w-4xl">
            <div className="inline-flex items-center gap-2 bg-pathfinder-500/20 px-4 py-2 rounded-full mb-6">
              <Sparkles className="w-4 h-4 text-pathfinder-600" />
              <span className="text-sm font-semibold text-pathfinder-800">AI-Powered Resume Analysis</span>
            </div>
            
            <h1 className="font-display text-display-lg text-midnight-950 mb-4">
              Resume Analyzer
            </h1>
            <p className="text-lg text-midnight-700 mb-8 max-w-2xl">
              Upload and analyze your resume with AI-powered insights.
              Get scores, recommendations, and ATS optimization tips.
            </p>

            <div className="flex gap-4">
              <Button 
                onClick={() => setShowUpload(!showUpload)}
                className="bg-pathfinder-500 hover:bg-pathfinder-600 text-ivory-50 h-12 px-6 group"
                size="lg"
              >
                <Plus className="w-5 h-5 mr-2" />
                Upload Resume
                <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container py-8 px-4 max-w-5xl">
        {/* Error Message */}
        {error && (
          <Alert variant="destructive" className="mb-6 border-error-500 bg-error-50">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Upload Form */}
        {showUpload && (
          <Card className="glass-card border-midnight-200 mb-8">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-pathfinder-500/10 flex items-center justify-center">
                  <Upload className="h-6 w-6 text-pathfinder-600" strokeWidth={2} />
                </div>
                <div>
                  <CardTitle className="font-display text-midnight-950">Upload New Resume</CardTitle>
                  <CardDescription className="text-midnight-600">
                    Upload a PDF or DOCX file (max 5MB) for AI-powered analysis
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-5">
                <div className="space-y-2">
                  <Label htmlFor="title" className="text-sm font-semibold text-midnight-900">
                    Resume Title
                  </Label>
                  <Input
                    id="title"
                    placeholder="e.g., Software Engineer Resume 2024"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="h-12 bg-white border-midnight-200 focus:border-pathfinder-500 focus:ring-pathfinder-500"
                    disabled={uploading}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="file" className="text-sm font-semibold text-midnight-900">
                    Resume File
                  </Label>
                  <div className="relative">
                    <Input
                      id="file"
                      type="file"
                      accept=".pdf,.docx"
                      onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                      className="h-12 bg-white border-midnight-200 focus:border-pathfinder-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-pathfinder-500 file:text-ivory-50 file:font-medium hover:file:bg-pathfinder-600"
                      disabled={uploading}
                    />
                  </div>
                  {selectedFile && (
                    <div className="flex items-center gap-2 p-3 bg-pathfinder-50 rounded-lg border border-pathfinder-200">
                      <FileCheck className="w-4 h-4 text-pathfinder-600 flex-shrink-0" />
                      <p className="text-sm text-pathfinder-800">
                        <span className="font-medium">{selectedFile.name}</span> 
                        <span className="text-pathfinder-600"> • {(selectedFile.size / 1024).toFixed(1)} KB</span>
                      </p>
                    </div>
                  )}
                </div>

                <div className="flex gap-3 pt-2">
                  <Button
                    onClick={handleUpload}
                    disabled={!selectedFile || !title.trim() || uploading}
                    className="bg-pathfinder-500 hover:bg-pathfinder-600 text-ivory-50 h-11 px-6 group"
                  >
                    {uploading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-ivory-50 border-t-transparent rounded-full animate-spin mr-2" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        Upload & Analyze
                        <Zap className="w-4 h-4 ml-2 group-hover:scale-110 transition-transform" />
                      </>
                    )}
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setShowUpload(false)
                      setSelectedFile(null)
                      setTitle('')
                    }}
                    className="border-midnight-200"
                    disabled={uploading}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Resumes List */}
        {resumes.length === 0 ? (
          <Card className="glass-card border-midnight-200">
            <CardContent className="pt-16 pb-16 text-center">
              <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-pathfinder-500/10 flex items-center justify-center">
                <FileText className="h-12 w-12 text-pathfinder-600" strokeWidth={2} />
              </div>
              <h3 className="font-display text-display-sm text-midnight-950 mb-3">
                No Resumes Yet
              </h3>
              <p className="text-midnight-600 mb-8 max-w-md mx-auto">
                Upload your first resume to get started with AI-powered analysis, 
                skill matching, and personalized improvement suggestions.
              </p>
              <Button 
                onClick={() => setShowUpload(true)}
                className="bg-pathfinder-500 hover:bg-pathfinder-600 text-ivory-50 h-12 px-6 group"
                size="lg"
              >
                <Plus className="w-5 h-5 mr-2" />
                Upload Your First Resume
                <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-6">
              <h2 className="font-display text-xl text-midnight-950">
                Your Resumes ({resumes.length})
              </h2>
            </div>

            {resumes.map((resume) => (
              <Card key={resume.id} className="glass-card border-midnight-200 hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-start gap-6">
                    {/* Icon */}
                    <div className="w-14 h-14 rounded-xl bg-pathfinder-500/10 flex items-center justify-center flex-shrink-0">
                      <FileText className="h-7 w-7 text-pathfinder-600" strokeWidth={2} />
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <div className="flex-1">
                          <h3 className="font-display text-lg text-midnight-950 mb-2">
                            {resume.title}
                          </h3>
                          <div className="flex flex-wrap items-center gap-2 mb-3">
                            {resume.is_primary && (
                              <Badge className="bg-pathfinder-500 hover:bg-pathfinder-600">
                                <Star className="w-3 h-3 mr-1 fill-current" />
                                Primary
                              </Badge>
                            )}
                            {resume.status === 'processing' && (
                              <Badge variant="secondary" className="bg-warning-100 text-warning-700 border-warning-200">
                                <Clock className="w-3 h-3 mr-1" />
                                Processing
                              </Badge>
                            )}
                            {resume.status === 'ready' && (
                              <Badge className="bg-success-100 text-success-700 border-success-200">
                                <CheckCircle className="w-3 h-3 mr-1" />
                                Ready
                              </Badge>
                            )}
                            {resume.status === 'failed' && (
                              <Badge variant="destructive">
                                <XCircle className="w-3 h-3 mr-1" />
                                Failed
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>

                      <p className="text-sm text-midnight-600 mb-4">
                        <span className="font-medium">{resume.original_filename}</span>
                        {' • '}
                        {resume.file_size_bytes ? `${(resume.file_size_bytes / 1024).toFixed(1)} KB` : 'Unknown size'}
                        {' • '}
                        Uploaded {new Date(resume.created_at).toLocaleDateString('en-US', { 
                          month: 'short', 
                          day: 'numeric', 
                          year: 'numeric' 
                        })}
                      </p>

                      <div className="flex flex-wrap gap-2">
                        {!resume.is_primary && resume.status === 'ready' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleSetPrimary(resume.id)}
                            className="border-midnight-200 hover:bg-pathfinder-50 hover:border-pathfinder-500 hover:text-pathfinder-700"
                          >
                            <Star className="w-4 h-4 mr-1" />
                            Set as Primary
                          </Button>
                        )}
                        {resume.status === 'ready' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => router.push(`/resume/${resume.id}`)}
                            className="border-midnight-200 hover:bg-pathfinder-50 hover:border-pathfinder-500 hover:text-pathfinder-700"
                          >
                            <FileText className="w-4 h-4 mr-1" />
                            View Analysis
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDelete(resume.id)}
                          className="border-error-200 text-error-600 hover:bg-error-50 hover:border-error-500"
                        >
                          <Trash2 className="w-4 h-4 mr-1" />
                          Delete
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
