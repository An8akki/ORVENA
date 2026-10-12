'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { signIn } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { AlertCircle, ArrowRight, Compass } from 'lucide-react'
import PathfinderVisual from '@/components/brand/PathfinderVisual'

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

type LoginFormData = z.infer<typeof loginSchema>

export default function LoginPage() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginFormData) => {
    try {
      setError(null)
      setLoading(true)

      await signIn({
        email: data.email,
        password: data.password,
      })

      router.push('/dashboard')
    } catch (err: any) {
      setError(err.message || 'Failed to sign in')
    } finally {
      setLoading(false)
    }
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
              Navigate your career journey with AI-powered intelligence. 
              Discover your path, build your skills, achieve your goals.
            </p>
          </div>

          {/* Pathfinder visualization */}
          <div className="flex-1 flex items-center justify-center py-12">
            <div className="w-full max-w-lg">
              <PathfinderVisual animated className="opacity-90" />
            </div>
          </div>

          {/* Features list */}
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-pathfinder-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <div className="w-2 h-2 rounded-full bg-pathfinder-400" />
              </div>
              <div>
                <h3 className="font-semibold text-ivory-50 mb-1">Intelligent Career Mapping</h3>
                <p className="text-sm text-ivory-200">Personalized roadmaps based on your skills and goals</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-pathfinder-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <div className="w-2 h-2 rounded-full bg-pathfinder-400" />
              </div>
              <div>
                <h3 className="font-semibold text-ivory-50 mb-1">Skills Analysis</h3>
                <p className="text-sm text-ivory-200">Evidence-based assessment of your capabilities</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-pathfinder-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <div className="w-2 h-2 rounded-full bg-pathfinder-400" />
              </div>
              <div>
                <h3 className="font-semibold text-ivory-50 mb-1">Works Offline</h3>
                <p className="text-sm text-ivory-200">Complete intelligence engine with no dependencies</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right side: Login form */}
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
                Welcome back
              </h2>
              <p className="text-base text-midnight-600">
                Continue your career journey
              </p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Error alert */}
              {error && (
                <Alert variant="destructive" className="border-error-500 bg-error-50">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

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
                <div className="flex items-center justify-between">
                  <Label 
                    htmlFor="password" 
                    className="text-sm font-semibold text-midnight-900"
                  >
                    Password
                  </Label>
                  <Link
                    href="/auth/forgot-password"
                    className="text-sm font-medium text-pathfinder-600 hover:text-pathfinder-700 transition-colors"
                  >
                    Forgot password?
                  </Link>
                </div>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
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

              {/* Submit button */}
              <Button 
                type="submit" 
                className="w-full h-12 bg-pathfinder-500 hover:bg-pathfinder-600 text-ivory-50 font-semibold text-base group transition-all duration-200 shadow-md hover:shadow-lg"
                disabled={loading}
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-ivory-50 border-t-transparent rounded-full animate-spin" />
                    Signing in...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    Sign in
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
                    New to ORVENA?
                  </span>
                </div>
              </div>

              {/* Sign up link */}
              <div className="text-center">
                <Link
                  href="/auth/register"
                  className="inline-flex items-center gap-2 text-sm font-medium text-midnight-700 hover:text-pathfinder-600 transition-colors"
                >
                  Create your account
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </form>
          </div>

          {/* Footer */}
          <p className="text-center text-sm text-midnight-500 mt-8">
            By signing in, you agree to our{' '}
            <Link href="/terms" className="text-pathfinder-600 hover:text-pathfinder-700">
              Terms
            </Link>{' '}
            and{' '}
            <Link href="/privacy" className="text-pathfinder-600 hover:text-pathfinder-700">
              Privacy Policy
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
