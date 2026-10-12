'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { signUp } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { AlertCircle, CheckCircle, ArrowRight, Compass, Sparkles } from 'lucide-react'
import PathfinderVisual from '@/components/brand/PathfinderVisual'

const registerSchema = z.object({
  fullName: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
})

type RegisterFormData = z.infer<typeof registerSchema>

export default function RegisterPage() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  })

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setError(null)
      setLoading(true)

      await signUp({
        email: data.email,
        password: data.password,
        fullName: data.fullName,
      })

      setSuccess(true)
      
      // Redirect after successful registration
      setTimeout(() => {
        router.push('/dashboard')
      }, 2000)
    } catch (err: any) {
      setError(err.message || 'Failed to create account')
    } finally {
      setLoading(false)
    }
  }

  // Success state
  if (success) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-ivory-50 dark:bg-midnight-950 px-4">
        <div className="glass-card rounded-xl p-10 max-w-md w-full text-center">
          <div className="flex items-center justify-center mb-6">
            <div className="rounded-full bg-success-100 p-4 pathfinder-glow">
              <CheckCircle className="h-12 w-12 text-success-600" />
            </div>
          </div>
          <h2 className="font-display text-display-md text-midnight-950 mb-3">
            Welcome to ORVENA!
          </h2>
          <p className="text-base text-midnight-600 mb-6">
            Your account has been created successfully. Redirecting you to your dashboard...
          </p>
          <div className="flex justify-center">
            <div className="w-8 h-8 border-3 border-pathfinder-500 border-t-transparent rounded-full animate-spin" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-ivory-50 dark:bg-midnight-950">
      {/* Left side: Branded section with pathfinder visual */}
      <div className="hidden lg:flex lg:w-1/2 gradient-midnight relative overflow-hidden">
        {/* Background pattern overlay */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(247, 245, 239, 0.15) 1px, transparent 0)',
            backgroundSize: '40px 40px'
          }} />
        </div>

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-between p-12 w-full">
          {/* Logo and tagline */}
          <div>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-xl bg-pathfinder-500 flex items-center justify-center pathfinder-glow">
                <Compass className="w-7 h-7 text-ivory-50" strokeWidth={2.5} />
              </div>
              <h1 className="font-display text-3xl font-bold text-ivory-50">
                ORVENA
              </h1>
            </div>
            <p className="text-ivory-100 text-lg leading-relaxed max-w-md">
              Start your journey with intelligent career guidance. 
              Map your path, develop your skills, reach your potential.
            </p>
          </div>

          {/* Pathfinder visualization */}
          <div className="flex-1 flex items-center justify-center py-12">
            <div className="w-full max-w-lg">
              <PathfinderVisual animated className="opacity-90" />
            </div>
          </div>

          {/* Stats/Social proof */}
          <div className="grid grid-cols-3 gap-6">
            <div>
              <div className="font-display text-3xl font-bold text-pathfinder-400 mb-1">
                100%
              </div>
              <div className="text-sm text-ivory-200">
                Offline capable
              </div>
            </div>
            <div>
              <div className="font-display text-3xl font-bold text-pathfinder-400 mb-1">
                <Sparkles className="w-8 h-8" />
              </div>
              <div className="text-sm text-ivory-200">
                AI-powered insights
              </div>
            </div>
            <div>
              <div className="font-display text-3xl font-bold text-pathfinder-400 mb-1">
                ∞
              </div>
              <div className="text-sm text-ivory-200">
                Career paths
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right side: Register form */}
      <div className="flex-1 flex items-center justify-center p-8 lg:p-12">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden mb-8 text-center">
            <div className="inline-flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-lg bg-pathfinder-500 flex items-center justify-center">
                <Compass className="w-6 h-6 text-ivory-50" strokeWidth={2.5} />
              </div>
              <h1 className="font-display text-2xl font-bold text-midnight-950">
                ORVENA
              </h1>
            </div>
          </div>

          {/* Form container */}
          <div className="glass-card rounded-xl p-8 lg:p-10">
            {/* Header */}
            <div className="mb-8">
              <h2 className="font-display text-display-md text-midnight-950 mb-2">
                Start your journey
              </h2>
              <p className="text-base text-midnight-600">
                Create your ORVENA account
              </p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
              {/* Error alert */}
              {error && (
                <Alert variant="destructive" className="border-error-500 bg-error-50">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Full name field */}
              <div className="space-y-2">
                <Label 
                  htmlFor="fullName" 
                  className="text-sm font-semibold text-midnight-900"
                >
                  Full name
                </Label>
                <Input
                  id="fullName"
                  type="text"
                  placeholder="John Doe"
                  className="h-12 bg-white border-midnight-200 focus:border-pathfinder-500 focus:ring-pathfinder-500"
                  {...register('fullName')}
                  disabled={loading}
                />
                {errors.fullName && (
                  <p className="text-sm text-error-600 flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" />
                    {errors.fullName.message}
                  </p>
                )}
              </div>

              {/* Email field */}
              <div className="space-y-2">
                <Label 
                  htmlFor="email" 
                  className="text-sm font-semibold text-midnight-900"
                >
                  Email address
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  className="h-12 bg-white border-midnight-200 focus:border-pathfinder-500 focus:ring-pathfinder-500"
                  {...register('email')}
                  disabled={loading}
                />
                {errors.email && (
                  <p className="text-sm text-error-600 flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" />
                    {errors.email.message}
                  </p>
                )}
              </div>

              {/* Password field */}
              <div className="space-y-2">
                <Label 
                  htmlFor="password" 
                  className="text-sm font-semibold text-midnight-900"
                >
                  Password
                </Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Minimum 8 characters"
                  className="h-12 bg-white border-midnight-200 focus:border-pathfinder-500 focus:ring-pathfinder-500"
                  {...register('password')}
                  disabled={loading}
                />
                {errors.password && (
                  <p className="text-sm text-error-600 flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" />
                    {errors.password.message}
                  </p>
                )}
              </div>

              {/* Confirm password field */}
              <div className="space-y-2">
                <Label 
                  htmlFor="confirmPassword" 
                  className="text-sm font-semibold text-midnight-900"
                >
                  Confirm password
                </Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="Re-enter your password"
                  className="h-12 bg-white border-midnight-200 focus:border-pathfinder-500 focus:ring-pathfinder-500"
                  {...register('confirmPassword')}
                  disabled={loading}
                />
                {errors.confirmPassword && (
                  <p className="text-sm text-error-600 flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" />
                    {errors.confirmPassword.message}
                  </p>
                )}
              </div>

              {/* Terms acceptance */}
              <p className="text-xs text-midnight-600 leading-relaxed">
                By creating an account, you agree to our{' '}
                <Link href="/terms" className="text-pathfinder-600 hover:text-pathfinder-700 font-medium">
                  Terms of Service
                </Link>
                {' '}and{' '}
                <Link href="/privacy" className="text-pathfinder-600 hover:text-pathfinder-700 font-medium">
                  Privacy Policy
                </Link>
              </p>

              {/* Submit button */}
              <Button 
                type="submit" 
                className="w-full h-12 bg-pathfinder-500 hover:bg-pathfinder-600 text-ivory-50 font-semibold text-base group transition-all duration-200 shadow-md hover:shadow-lg"
                disabled={loading}
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-ivory-50 border-t-transparent rounded-full animate-spin" />
                    Creating account...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    Create account
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </span>
                )}
              </Button>

              {/* Divider */}
              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-midnight-200" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-ivory-50 dark:bg-midnight-950 px-2 text-midnight-500">
                    Already have an account?
                  </span>
                </div>
              </div>

              {/* Sign in link */}
              <div className="text-center">
                <Link
                  href="/auth/login"
                  className="inline-flex items-center gap-2 text-sm font-medium text-midnight-700 hover:text-pathfinder-600 transition-colors"
                >
                  Sign in instead
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
