'use client'

import { useEffect, useState } from 'react'
import { redirect, useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { LoadingSpinner } from '@/components/shared/LoadingSpinner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { getProfile, updateProfile } from '@/lib/api/student'
import type { StudentProfile } from '@/types'
import { ArrowLeft, Save } from 'lucide-react'

const profileSchema = z.object({
  full_name: z.string().min(1, 'Name is required').max(200),
  phone: z.string().max(20).optional().nullable(),
  location: z.string().max(200).optional().nullable(),
  linkedin_url: z.string().url('Invalid URL').max(500).optional().nullable().or(z.literal('')),
  github_url: z.string().url('Invalid URL').max(500).optional().nullable().or(z.literal('')),
  portfolio_url: z.string().url('Invalid URL').max(500).optional().nullable().or(z.literal('')),
  bio: z.string().optional().nullable(),
  graduation_year: z.number().int().min(1950).max(2050).optional().nullable(),
  expected_salary_min: z.number().int().min(0).optional().nullable(),
  expected_salary_max: z.number().int().min(0).optional().nullable(),
})

type ProfileFormData = z.infer<typeof profileSchema>

export default function ProfileEditPage() {
  redirect('/dashboard')
  return (
    <AuthGuard>
      <ProfileEditContent />
    </AuthGuard>
  )
}

function ProfileEditContent() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
  })

  useEffect(() => {
    loadProfile()
  }, [])

  async function loadProfile() {
    try {
      setLoading(true)
      const profile = await getProfile()
      reset({
        full_name: profile.full_name,
        phone: profile.phone || '',
        location: profile.location || '',
        linkedin_url: profile.linkedin_url || '',
        github_url: profile.github_url || '',
        portfolio_url: profile.portfolio_url || '',
        bio: profile.bio || '',
        graduation_year: profile.graduation_year || undefined,
        expected_salary_min: profile.expected_salary_min || undefined,
        expected_salary_max: profile.expected_salary_max || undefined,
      })
    } catch (err: any) {
      setError(err.message || 'Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  async function onSubmit(data: ProfileFormData) {
    try {
      setSaving(true)
      setError(null)
      setSuccess(false)

      // Convert empty strings to null
      const cleanData = {
        ...data,
        phone: data.phone || null,
        location: data.location || null,
        linkedin_url: data.linkedin_url || null,
        github_url: data.github_url || null,
        portfolio_url: data.portfolio_url || null,
        bio: data.bio || null,
      }

      await updateProfile(cleanData)
      setSuccess(true)
      setTimeout(() => router.push('/profile'), 1500)
    } catch (err: any) {
      setError(err.message || 'Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-3xl">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/profile')}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Edit Profile</h1>
          <p className="text-muted-foreground">Update your personal information</p>
        </div>
      </div>

      {/* Success Message */}
      {success && (
        <Alert className="mb-6 bg-green-50 border-green-200">
          <AlertDescription className="text-green-800">
            Profile updated successfully! Redirecting...
          </AlertDescription>
        </Alert>
      )}

      {/* Error Message */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)}>
        <Card>
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
            <CardDescription>Basic details about you</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Full Name */}
            <div>
              <Label htmlFor="full_name">Full Name *</Label>
              <Input
                id="full_name"
                {...register('full_name')}
                className={errors.full_name ? 'border-red-500' : ''}
              />
              {errors.full_name && (
                <p className="text-sm text-red-500 mt-1">{errors.full_name.message}</p>
              )}
            </div>

            {/* Phone */}
            <div>
              <Label htmlFor="phone">Phone Number</Label>
              <Input
                id="phone"
                type="tel"
                {...register('phone')}
                className={errors.phone ? 'border-red-500' : ''}
              />
              {errors.phone && (
                <p className="text-sm text-red-500 mt-1">{errors.phone.message}</p>
              )}
            </div>

            {/* Location */}
            <div>
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                placeholder="e.g., San Francisco, CA"
                {...register('location')}
                className={errors.location ? 'border-red-500' : ''}
              />
              {errors.location && (
                <p className="text-sm text-red-500 mt-1">{errors.location.message}</p>
              )}
            </div>

            {/* Bio */}
            <div>
              <Label htmlFor="bio">Bio</Label>
              <Textarea
                id="bio"
                placeholder="Tell us about yourself..."
                rows={4}
                {...register('bio')}
                className={errors.bio ? 'border-red-500' : ''}
              />
              {errors.bio && (
                <p className="text-sm text-red-500 mt-1">{errors.bio.message}</p>
              )}
            </div>

            {/* Graduation Year */}
            <div>
              <Label htmlFor="graduation_year">Graduation Year</Label>
              <Input
                id="graduation_year"
                type="number"
                placeholder="e.g., 2024"
                {...register('graduation_year', { valueAsNumber: true })}
                className={errors.graduation_year ? 'border-red-500' : ''}
              />
              {errors.graduation_year && (
                <p className="text-sm text-red-500 mt-1">{errors.graduation_year.message}</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Online Presence</CardTitle>
            <CardDescription>Your social and professional profiles</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* LinkedIn */}
            <div>
              <Label htmlFor="linkedin_url">LinkedIn URL</Label>
              <Input
                id="linkedin_url"
                type="url"
                placeholder="https://linkedin.com/in/yourname"
                {...register('linkedin_url')}
                className={errors.linkedin_url ? 'border-red-500' : ''}
              />
              {errors.linkedin_url && (
                <p className="text-sm text-red-500 mt-1">{errors.linkedin_url.message}</p>
              )}
            </div>

            {/* GitHub */}
            <div>
              <Label htmlFor="github_url">GitHub URL</Label>
              <Input
                id="github_url"
                type="url"
                placeholder="https://github.com/yourname"
                {...register('github_url')}
                className={errors.github_url ? 'border-red-500' : ''}
              />
              {errors.github_url && (
                <p className="text-sm text-red-500 mt-1">{errors.github_url.message}</p>
              )}
            </div>

            {/* Portfolio */}
            <div>
              <Label htmlFor="portfolio_url">Portfolio URL</Label>
              <Input
                id="portfolio_url"
                type="url"
                placeholder="https://yourportfolio.com"
                {...register('portfolio_url')}
                className={errors.portfolio_url ? 'border-red-500' : ''}
              />
              {errors.portfolio_url && (
                <p className="text-sm text-red-500 mt-1">{errors.portfolio_url.message}</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Salary Expectations</CardTitle>
            <CardDescription>Optional salary range (annual, USD)</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              {/* Min Salary */}
              <div>
                <Label htmlFor="expected_salary_min">Minimum</Label>
                <Input
                  id="expected_salary_min"
                  type="number"
                  placeholder="50000"
                  {...register('expected_salary_min', { valueAsNumber: true })}
                  className={errors.expected_salary_min ? 'border-red-500' : ''}
                />
                {errors.expected_salary_min && (
                  <p className="text-sm text-red-500 mt-1">
                    {errors.expected_salary_min.message}
                  </p>
                )}
              </div>

              {/* Max Salary */}
              <div>
                <Label htmlFor="expected_salary_max">Maximum</Label>
                <Input
                  id="expected_salary_max"
                  type="number"
                  placeholder="80000"
                  {...register('expected_salary_max', { valueAsNumber: true })}
                  className={errors.expected_salary_max ? 'border-red-500' : ''}
                />
                {errors.expected_salary_max && (
                  <p className="text-sm text-red-500 mt-1">
                    {errors.expected_salary_max.message}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex gap-4 mt-8">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.push('/profile')}
            disabled={saving}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={saving}>
            {saving ? (
              <>
                <LoadingSpinner size="sm" className="mr-2" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  )
}
