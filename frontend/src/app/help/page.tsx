'use client'

import { AuthGuard } from '@/components/auth/AuthGuard'
import { AppLayout } from '@/components/layout/AppLayout'
import { useState } from 'react'
import {
  HelpCircle,
  Search,
  BookOpen,
  Video,
  MessageCircle,
  Mail,
  FileText,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Sparkles,
  Target,
  BarChart3,
  FileCheck,
  Zap,
  Shield,
  Settings,
  Users,
} from 'lucide-react'

interface FAQ {
  id: string
  question: string
  answer: string
  category: string
}

interface Guide {
  id: string
  title: string
  description: string
  icon: any
  duration: string
  link: string
}

export default function HelpPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedFAQ, setExpandedFAQ] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  const categories = [
    { id: 'all', label: 'All Topics' },
    { id: 'getting-started', label: 'Getting Started' },
    { id: 'features', label: 'Features' },
    { id: 'ai', label: 'AI Features' },
    { id: 'account', label: 'Account' },
    { id: 'troubleshooting', label: 'Troubleshooting' },
  ]

  const faqs: FAQ[] = [
    {
      id: '1',
      question: 'What is ORVENA?',
      answer: 'ORVENA is an AI-powered career intelligence platform that helps you discover your ideal career path, analyze your resume, get personalized job recommendations, and build a roadmap to achieve your career goals. It combines advanced AI with statistical analysis to provide reliable career guidance.',
      category: 'getting-started',
    },
    {
      id: '2',
      question: 'How does the Career Discovery work?',
      answer: 'Career Discovery uses a comprehensive questionnaire to understand your interests, skills, values, and preferences. Our AI analyzes your responses and matches them against hundreds of career profiles to recommend careers that align with your unique profile. Even if AI is unavailable, our statistical engine ensures you always get meaningful recommendations.',
      category: 'features',
    },
    {
      id: '3',
      question: 'What does the Resume Analyzer check?',
      answer: 'The Resume Analyzer evaluates your resume across multiple dimensions: completeness (20%), experience relevance (25%), education background (15%), skills match (20%), formatting quality (10%), and ATS keyword optimization (10%). You receive a detailed score with specific recommendations for improvement.',
      category: 'features',
    },
    {
      id: '4',
      question: 'How accurate are the job recommendations?',
      answer: 'Our Job Recommender uses a sophisticated matching algorithm that evaluates 5 key factors: skills match (40%), education fit (25%), experience level (20%), market demand (10%), and your preferences (5%). We maintain a curated database of job roles with salary ranges, growth potential, and detailed requirements.',
      category: 'features',
    },
    {
      id: '5',
      question: 'What is the Career Roadmap feature?',
      answer: 'Career Roadmap creates a personalized timeline with milestones to help you reach your career goals. It breaks down your journey into actionable steps, tracks your progress, and adjusts recommendations based on your advancement. You can see both short-term (0-6 months) and long-term (6-24 months) goals.',
      category: 'features',
    },
    {
      id: '6',
      question: 'How does ORVENA ensure AI reliability?',
      answer: 'ORVENA implements a comprehensive fallback system. Every AI-powered feature has a statistical/ML backup that activates automatically if AI fails or times out (within 10 seconds). This ensures you always receive results with 99.9% uptime guarantee. The fallback algorithms are scientifically validated and provide high-quality results.',
      category: 'ai',
    },
    {
      id: '7',
      question: 'What AI models does ORVENA use?',
      answer: 'ORVENA supports multiple AI providers including Gemini, OpenAI, and Anthropic. The system automatically routes requests to available providers and falls back to statistical engines if needed. You don\'t need to worry about AI availability - the system handles it seamlessly.',
      category: 'ai',
    },
    {
      id: '8',
      question: 'Is my data secure?',
      answer: 'Yes, absolutely. ORVENA uses industry-standard encryption for data at rest and in transit. We never share your personal information with third parties. Your resume data, career assessments, and profile information are stored securely in Supabase with role-based access control.',
      category: 'account',
    },
    {
      id: '9',
      question: 'Can I export my data?',
      answer: 'Yes, you can export your profile, resume analysis, career recommendations, and roadmap data at any time. Go to Settings > Privacy & Data > Export Data to download all your information in JSON format.',
      category: 'account',
    },
    {
      id: '11',
      question: 'What if a feature isn\'t working?',
      answer: 'First, try refreshing the page. If the issue persists, check your internet connection. All features have fallback mechanisms, so you should always receive results even if AI is temporarily unavailable. If you continue experiencing issues, contact support using the form below.',
      category: 'troubleshooting',
    },
    {
      id: '12',
      question: 'How often should I update my resume?',
      answer: 'We recommend running the Resume Analyzer after every significant change to your resume or at least once a month. This helps you track improvements and ensure your resume stays optimized for ATS systems and recruiter preferences.',
      category: 'troubleshooting',
    },
  ]

  const guides: Guide[] = [
    {
      id: '1',
      title: 'Getting Started with ORVENA',
      description: 'Learn the basics of navigating ORVENA and using its career tools',
      icon: Sparkles,
      duration: '5 min',
      link: '#getting-started',
    },
    {
      id: '2',
      title: 'Discovering Your Career Path',
      description: 'Complete the career discovery questionnaire for personalized recommendations',
      icon: Target,
      duration: '15 min',
      link: '#career-discovery',
    },
    {
      id: '3',
      title: 'Optimizing Your Resume',
      description: 'Upload and analyze your resume to maximize your job search success',
      icon: FileCheck,
      duration: '10 min',
      link: '#resume-analyzer',
    },
    {
      id: '4',
      title: 'Finding the Right Jobs',
      description: 'Get AI-powered job recommendations tailored to your skills and goals',
      icon: Zap,
      duration: '8 min',
      link: '#job-recommender',
    },
    {
      id: '5',
      title: 'Building Your Career Roadmap',
      description: 'Create a step-by-step plan to achieve your career objectives',
      icon: BarChart3,
      duration: '12 min',
      link: '#roadmap',
    },
    {
      id: '6',
      title: 'Tracking Your Progress',
      description: 'Monitor your career development and celebrate milestones',
      icon: Target,
      duration: '7 min',
      link: '#progress',
    },
  ]

  const filteredFAQs = faqs.filter((faq) => {
    const matchesSearch = faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || faq.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <AuthGuard>
      <AppLayout>
        <div className="space-y-8">
          {/* Header */}
          <div className="text-center max-w-3xl mx-auto">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <HelpCircle className="w-8 h-8 text-blue-600" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">How can we help you?</h1>
            <p className="text-lg text-gray-600">
              Find answers, learn about features, or get in touch with our support team
            </p>
          </div>

          {/* Search Bar */}
          <div className="max-w-2xl mx-auto">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search for help articles, features, or topics..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-4 border border-gray-300 rounded-xl shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg"
              />
            </div>
          </div>

          {/* Quick Access Cards */}
          <div className="grid gap-6 md:grid-cols-3">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Documentation</h3>
              <p className="text-gray-600 mb-4">
                Comprehensive guides and feature documentation
              </p>
              <a href="#guides" className="text-blue-600 font-medium hover:text-blue-700 flex items-center gap-1">
                Browse Guides
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>

            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
              <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center mb-4">
                <Video className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Video Tutorials</h3>
              <p className="text-gray-600 mb-4">
                Step-by-step video guides for all features
              </p>
              <a href="#videos" className="text-purple-600 font-medium hover:text-purple-700 flex items-center gap-1">
                Watch Videos
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
              <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center mb-4">
                <MessageCircle className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Contact Support</h3>
              <p className="text-gray-600 mb-4">
                Get help from our dedicated support team
              </p>
              <a href="#contact" className="text-green-600 font-medium hover:text-green-700 flex items-center gap-1">
                Get in Touch
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          </div>

          {/* Popular Guides */}
          <div id="guides" className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
            <div className="flex items-center gap-3 mb-6">
              <BookOpen className="w-6 h-6 text-blue-600" />
              <h2 className="text-2xl font-bold text-gray-900">Getting Started Guides</h2>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {guides.map((guide) => {
                const Icon = guide.icon
                return (
                  <a
                    key={guide.id}
                    href={guide.link}
                    className="block p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all group"
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center group-hover:bg-blue-600 transition-colors">
                        <Icon className="w-5 h-5 text-blue-600 group-hover:text-white transition-colors" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
                          {guide.title}
                        </h4>
                        <p className="text-sm text-gray-600 mb-2">{guide.description}</p>
                        <span className="text-xs text-gray-500">{guide.duration} read</span>
                      </div>
                    </div>
                  </a>
                )
              })}
            </div>
          </div>

          {/* FAQs */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
            <div className="flex items-center gap-3 mb-6">
              <HelpCircle className="w-6 h-6 text-purple-600" />
              <h2 className="text-2xl font-bold text-gray-900">Frequently Asked Questions</h2>
            </div>

            {/* Category Filter */}
            <div className="flex flex-wrap gap-2 mb-6">
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    selectedCategory === cat.id
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            {/* FAQ List */}
            <div className="space-y-3">
              {filteredFAQs.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-500">No results found. Try a different search or category.</p>
                </div>
              ) : (
                filteredFAQs.map((faq) => (
                  <div
                    key={faq.id}
                    className="border border-gray-200 rounded-lg overflow-hidden"
                  >
                    <button
                      onClick={() => setExpandedFAQ(expandedFAQ === faq.id ? null : faq.id)}
                      className="w-full px-6 py-4 flex items-center justify-between bg-white hover:bg-gray-50 transition-colors text-left"
                    >
                      <span className="font-medium text-gray-900">{faq.question}</span>
                      {expandedFAQ === faq.id ? (
                        <ChevronUp className="w-5 h-5 text-gray-500 flex-shrink-0" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-gray-500 flex-shrink-0" />
                      )}
                    </button>
                    {expandedFAQ === faq.id && (
                      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
                        <p className="text-gray-700 leading-relaxed">{faq.answer}</p>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Contact Support */}
          <div id="contact" className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl border border-gray-200 p-8">
            <div className="max-w-2xl mx-auto text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <Mail className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Still need help?</h2>
              <p className="text-gray-600 mb-6">
                Can't find what you're looking for? Our support team is here to help you succeed.
              </p>
              
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-left space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Your Email
                  </label>
                  <input
                    type="email"
                    placeholder="you@example.com"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Subject
                  </label>
                  <input
                    type="text"
                    placeholder="How can we help?"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Message
                  </label>
                  <textarea
                    rows={5}
                    placeholder="Describe your issue or question..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <button className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium">
                  Send Message
                </button>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200">
                <p className="text-sm text-gray-600 mb-3">Or reach us directly:</p>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4 text-sm">
                  <a href="mailto:support@orvena.com" className="text-blue-600 hover:text-blue-700 flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    support@orvena.com
                  </a>
                  <span className="hidden sm:block text-gray-300">|</span>
                  <span className="text-gray-600">Average response time: 24 hours</span>
                </div>
              </div>
            </div>
          </div>

          {/* Additional Resources */}
          <div className="grid gap-6 md:grid-cols-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-4">
                <FileText className="w-5 h-5 text-gray-600" />
                <h3 className="text-lg font-semibold text-gray-900">Release Notes</h3>
              </div>
              <p className="text-gray-600 mb-4">
                Stay updated with the latest features, improvements, and bug fixes
              </p>
              <a href="#releases" className="text-blue-600 font-medium hover:text-blue-700 flex items-center gap-1">
                View Changelog
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-4">
                <Users className="w-5 h-5 text-gray-600" />
                <h3 className="text-lg font-semibold text-gray-900">Community</h3>
              </div>
              <p className="text-gray-600 mb-4">
                Join discussions, share tips, and connect with other ORVENA users
              </p>
              <a href="#community" className="text-blue-600 font-medium hover:text-blue-700 flex items-center gap-1">
                Join Community
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>
      </AppLayout>
    </AuthGuard>
  )
}
