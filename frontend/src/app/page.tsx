import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { ArrowRight, Briefcase, FileText, Target, TrendingUp } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">ORVENA</span>
          </div>
          <nav className="hidden md:flex items-center gap-6">
            <Link href="#features" className="text-sm font-medium hover:text-primary transition-colors">
              Features
            </Link>
            <Link href="#how-it-works" className="text-sm font-medium hover:text-primary transition-colors">
              How It Works
            </Link>
            <Link href="#about" className="text-sm font-medium hover:text-primary transition-colors">
              About
            </Link>
          </nav>
          <div className="flex items-center gap-4">
            <Link href="/auth/login">
              <Button variant="ghost" size="sm">
                Log In
              </Button>
            </Link>
            <Link href="/auth/register">
              <Button size="sm">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container flex flex-col items-center justify-center gap-8 py-24 text-center md:py-32">
        <div className="flex flex-col gap-4 max-w-3xl">
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl">
            Your AI-Powered Career Success Platform
          </h1>
          <p className="text-lg text-muted-foreground sm:text-xl md:text-2xl max-w-2xl mx-auto">
            Discover your ideal career path, optimize your resume, find matching opportunities, and ace your interviews—all powered by AI.
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-4">
          <Link href="/auth/register">
            <Button size="lg" className="gap-2">
              Start Your Journey
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="#how-it-works">
            <Button size="lg" variant="outline">
              Learn More
            </Button>
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="container py-24 md:py-32 bg-muted/30">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl mb-4">
            Everything You Need to Succeed
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Comprehensive tools powered by AI to guide you from career discovery to landing your dream job
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {/* Career Intelligence */}
          <div className="flex flex-col gap-4 rounded-lg border bg-card p-6 hover:shadow-lg transition-shadow">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <Target className="h-6 w-6 text-primary" />
            </div>
            <h3 className="text-xl font-semibold">Career Intelligence</h3>
            <p className="text-muted-foreground">
              Discover your ideal career path through AI-powered assessments and personalized recommendations
            </p>
          </div>

          {/* Resume Intelligence */}
          <div className="flex flex-col gap-4 rounded-lg border bg-card p-6 hover:shadow-lg transition-shadow">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <FileText className="h-6 w-6 text-primary" />
            </div>
            <h3 className="text-xl font-semibold">Resume Optimization</h3>
            <p className="text-muted-foreground">
              Build, analyze, and tailor your resume with AI-driven feedback and job-specific customization
            </p>
          </div>

          {/* Job Matching */}
          <div className="flex flex-col gap-4 rounded-lg border bg-card p-6 hover:shadow-lg transition-shadow">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <Briefcase className="h-6 w-6 text-primary" />
            </div>
            <h3 className="text-xl font-semibold">Job Matching</h3>
            <p className="text-muted-foreground">
              Find opportunities that match your skills, preferences, and career goals with intelligent matching
            </p>
          </div>

          {/* Interview Prep */}
          <div className="flex flex-col gap-4 rounded-lg border bg-card p-6 hover:shadow-lg transition-shadow">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <TrendingUp className="h-6 w-6 text-primary" />
            </div>
            <h3 className="text-xl font-semibold">Interview Preparation</h3>
            <p className="text-muted-foreground">
              Practice with AI-generated questions and receive detailed feedback to ace your interviews
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="container py-24 md:py-32">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl mb-4">
            How ORVENA Works
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            A simple, guided process to help you achieve your career goals
          </p>
        </div>

        <div className="grid gap-12 md:grid-cols-3">
          <div className="flex flex-col items-center text-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-2xl font-bold text-primary-foreground">
              1
            </div>
            <h3 className="text-xl font-semibold">Discover Your Path</h3>
            <p className="text-muted-foreground">
              Answer guided questions to understand your strengths, interests, and ideal career direction
            </p>
          </div>

          <div className="flex flex-col items-center text-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-2xl font-bold text-primary-foreground">
              2
            </div>
            <h3 className="text-xl font-semibold">Strengthen Your Resume</h3>
            <p className="text-muted-foreground">
              Create an optimized resume that highlights your unique qualifications
            </p>
          </div>

          <div className="flex flex-col items-center text-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-2xl font-bold text-primary-foreground">
              3
            </div>
            <h3 className="text-xl font-semibold">Land Your Dream Job</h3>
            <p className="text-muted-foreground">
              Find matching opportunities, prepare for interviews, and track your applications
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container py-24 md:py-32 bg-primary/5">
        <div className="flex flex-col items-center text-center gap-8 max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
            Ready to Start Your Career Journey?
          </h2>
          <p className="text-lg text-muted-foreground">
            Join students and professionals who are achieving their career goals with ORVENA
          </p>
          <Link href="/auth/register">
            <Button size="lg" className="gap-2">
              Get Started Free
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t">
        <div className="container py-12 md:py-16">
          <div className="grid gap-8 md:grid-cols-4">
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-2">
                <Target className="h-5 w-5 text-primary" />
                <span className="font-bold">ORVENA</span>
              </div>
              <p className="text-sm text-muted-foreground">
                AI-powered career platform for students and professionals
              </p>
            </div>

            <div className="flex flex-col gap-4">
              <h3 className="font-semibold">Product</h3>
              <ul className="flex flex-col gap-2 text-sm text-muted-foreground">
                <li><Link href="#features" className="hover:text-foreground transition-colors">Features</Link></li>
                <li><Link href="#how-it-works" className="hover:text-foreground transition-colors">How It Works</Link></li>
              </ul>
            </div>

            <div className="flex flex-col gap-4">
              <h3 className="font-semibold">Company</h3>
              <ul className="flex flex-col gap-2 text-sm text-muted-foreground">
                <li><Link href="#about" className="hover:text-foreground transition-colors">About</Link></li>
                <li><Link href="#contact" className="hover:text-foreground transition-colors">Contact</Link></li>
              </ul>
            </div>

            <div className="flex flex-col gap-4">
              <h3 className="font-semibold">Legal</h3>
              <ul className="flex flex-col gap-2 text-sm text-muted-foreground">
                <li><Link href="/privacy" className="hover:text-foreground transition-colors">Privacy Policy</Link></li>
                <li><Link href="/terms" className="hover:text-foreground transition-colors">Terms of Service</Link></li>
              </ul>
            </div>
          </div>

          <div className="mt-12 border-t pt-8">
            <p className="text-center text-sm text-muted-foreground">
              © {new Date().getFullYear()} ORVENA. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
