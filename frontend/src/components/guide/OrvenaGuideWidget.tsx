'use client'

import React, { useState, useEffect, useRef } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { MessageSquare, X, Send, Sparkles, Compass, ChevronRight, HelpCircle, RotateCcw, ArrowRight } from 'lucide-react'
import { api } from '@/lib/api-client'
import { getUser } from '@/lib/auth'
import { cn } from '@/lib/utils'

interface Action {
  label: string
  href: string
  description?: string
}

interface Message {
  id: string
  sender: 'user' | 'guide'
  text: string
  actions?: Action[]
  suggestedPrompts?: string[]
  timestamp: string
}

const DEFAULT_PROMPTS = [
  'How do I choose the right project idea?',
  'What is Project Launchpad?',
  'Where can I find student hackathons and grants?',
  'How is my resume ATS score calculated?',
]

export function OrvenaGuideWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [userName, setUserName] = useState<string>('')
  const pathname = usePathname()
  const router = useRouter()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'guide',
      text: "👋 Hi there! I'm **Orvena Guide**, your project & career navigator. How can I help you today? You can ask me any doubts about your projects, choosing ideas, milestones, evaluations, or student competitions!",
      actions: [
        { label: 'Explore Launchpad', href: '/projects', description: 'Ideas, milestones & evaluation' },
        { label: 'Start Career Discovery', href: '/career/discovery', description: '5-phase career assessment' },
        { label: 'Analyze Resume', href: '/resume', description: '6-factor ATS analysis' },
      ],
      suggestedPrompts: DEFAULT_PROMPTS,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ])

  useEffect(() => {
    getUser()
      .then((user) => {
        const name = (user as any)?.user_metadata?.full_name || (user as any)?.email?.split('@')[0] || ''
        if (name) {
          setUserName(name)
          setMessages([
            {
              id: 'welcome',
              sender: 'guide',
              text: `👋 Hi ${name}! I'm **Orvena Guide**, your project & career navigator. How can I help you today? You can ask me any doubts about your projects, choosing ideas, milestones, evaluations, or student competitions!`,
              actions: [
                { label: 'Explore Launchpad', href: '/projects', description: 'Ideas, milestones & evaluation' },
                { label: 'Start Career Discovery', href: '/career/discovery', description: '5-phase career assessment' },
                { label: 'Analyze Resume', href: '/resume', description: '6-factor ATS analysis' },
              ],
              suggestedPrompts: DEFAULT_PROMPTS,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            },
          ])
        }
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isOpen])

  const handleSend = async (textToSend?: string) => {
    const text = (textToSend || inputText).trim()
    if (!text || isLoading) return

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }

    setMessages((prev) => [...prev, userMsg])
    setInputText('')
    setIsLoading(true)

    try {
      const response = await api.post<{
        reply: string
        matched_intent: string
        confidence: number
        suggested_actions: Action[]
        suggested_prompts: string[]
      }>('/api/v1/guide/chat', {
        message: text,
        current_path: pathname,
        user_name: userName,
      })

      const guideMsg: Message = {
        id: `guide-${Date.now()}`,
        sender: 'guide',
        text: response.reply,
        actions: response.suggested_actions || [],
        suggestedPrompts: response.suggested_prompts || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages((prev) => [...prev, guideMsg])
    } catch {
      // Local deterministic fallback
      const guideMsg: Message = {
        id: `guide-${Date.now()}`,
        sender: 'guide',
        text: "I couldn't reach the Guide service right now. You can still navigate directly to a core section below, or try your question again in a moment:",
        actions: [
          { label: 'Project Launchpad', href: '/projects', description: 'Ideas, milestones & outcomes' },
          { label: 'Career Discovery', href: '/career/discovery', description: 'Guided questionnaire' },
          { label: 'Resume Analyzer', href: '/resume', description: 'ATS score & feedback' },
          { label: 'Opportunities', href: '/projects/opportunities', description: 'Competitions & grants' },
        ],
        suggestedPrompts: DEFAULT_PROMPTS,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages((prev) => [...prev, guideMsg])
    } finally {
      setIsLoading(false)
    }
  }

  const handleActionClick = (href: string) => {
    router.push(href)
    setIsOpen(false)
  }

  return (
    <>
      {/* Floating Toggle Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Open Orvena Guide"
        className={cn(
          'fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-full px-4 py-3 shadow-lg transition-all duration-300',
          'bg-midnight-950 text-ivory-50 border border-midnight-800 hover:border-pathfinder-400 hover:shadow-pathfinder-500/20',
          isOpen && 'scale-95 border-pathfinder-500 ring-2 ring-pathfinder-500/30'
        )}
      >
        <div className="relative flex items-center justify-center">
          <Compass className="h-5 w-5 text-pathfinder-400 animate-spin-slow" />
          <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-emerald-400" />
        </div>
        <span className="text-sm font-medium tracking-wide">Orvena Guide</span>
      </button>

      {/* Slide-Up Assistant Panel */}
      {isOpen && (
        <div
          role="dialog"
          aria-label="Orvena Guide Assistant"
          className="fixed bottom-20 right-6 z-50 flex h-[580px] w-[380px] sm:w-[420px] flex-col rounded-2xl border border-midnight-800 bg-midnight-950 text-ivory-50 shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-200"
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-midnight-800 bg-midnight-900/80 px-4 py-3 backdrop-blur-md">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-pathfinder-500/20 text-pathfinder-400">
                <Compass className="h-4 w-4" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-ivory-50">ORVENA Guide</h3>
                <p className="text-[11px] text-midnight-300">Rule-based platform navigator</p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={() =>
                  setMessages([
                    {
                      id: 'welcome-reset',
                      sender: 'guide',
                      text: "Conversation reset. How can I help you navigate Orvena today?",
                      actions: [
                        { label: 'Project Launchpad', href: '/projects' },
                        { label: 'Career Discovery', href: '/career/discovery' },
                        { label: 'Resume Analyzer', href: '/resume' },
                      ],
                      suggestedPrompts: DEFAULT_PROMPTS,
                      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    },
                  ])
                }
                title="Reset conversation"
                className="rounded-lg p-1.5 text-midnight-400 hover:bg-midnight-800 hover:text-ivory-50 transition-colors"
              >
                <RotateCcw className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                title="Close Guide"
                className="rounded-lg p-1.5 text-midnight-400 hover:bg-midnight-800 hover:text-ivory-50 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Messages Body */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs scrollbar-thin">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={cn('flex flex-col', msg.sender === 'user' ? 'items-end' : 'items-start')}
              >
                <div
                  className={cn(
                    'max-w-[85%] rounded-2xl px-3.5 py-2.5 leading-relaxed shadow-sm',
                    msg.sender === 'user'
                      ? 'bg-pathfinder-600 text-ivory-50 rounded-br-sm'
                      : 'bg-midnight-900 border border-midnight-800 text-midnight-100 rounded-bl-sm'
                  )}
                >
                  <div className="whitespace-pre-wrap font-sans">{msg.text}</div>
                </div>

                {/* Navigation Actions */}
                {msg.actions && msg.actions.length > 0 && (
                  <div className="mt-2.5 flex flex-col gap-1.5 w-full max-w-[90%]">
                    {msg.actions.map((act) => (
                      <button
                        key={act.href + act.label}
                        type="button"
                        onClick={() => handleActionClick(act.href)}
                        className="group flex items-center justify-between rounded-xl border border-midnight-800 bg-midnight-900/60 p-2.5 text-left hover:border-pathfinder-500/50 hover:bg-midnight-900 transition-all"
                      >
                        <div>
                          <div className="font-semibold text-pathfinder-300 text-[11px] group-hover:text-pathfinder-200 flex items-center gap-1">
                            {act.label}
                            <ArrowRight className="h-3 w-3 transition-transform group-hover:translate-x-1" />
                          </div>
                          {act.description && (
                            <div className="text-[10px] text-midnight-400 mt-0.5">{act.description}</div>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                {/* Suggested Prompt Chips */}
                {msg.suggestedPrompts && msg.suggestedPrompts.length > 0 && (
                  <div className="mt-2.5 flex flex-wrap gap-1.5">
                    {msg.suggestedPrompts.map((p) => (
                      <button
                        key={p}
                        type="button"
                        onClick={() => handleSend(p)}
                        className="rounded-full border border-midnight-800 bg-midnight-900 px-2.5 py-1 text-[10px] text-midnight-300 hover:border-pathfinder-400 hover:text-ivory-50 transition-colors"
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                )}

                <span className="text-[9px] text-midnight-500 mt-1 px-1">{msg.timestamp}</span>
              </div>
            ))}

            {isLoading && (
              <div className="flex items-center gap-1.5 text-midnight-400 text-xs pl-2">
                <span className="h-2 w-2 rounded-full bg-pathfinder-400 animate-ping" />
                <span>Orvena Guide is searching rules...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Footer */}
          <div className="border-t border-midnight-800 bg-midnight-900/90 p-3">
            <form
              onSubmit={(e) => {
                e.preventDefault()
                handleSend()
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Ask about careers, projects, resume, or jobs..."
                className="flex-1 rounded-xl border border-midnight-800 bg-midnight-950 px-3 py-2 text-xs text-ivory-50 placeholder:text-midnight-500 focus:border-pathfinder-400 focus:outline-none focus:ring-1 focus:ring-pathfinder-400"
              />
              <button
                type="submit"
                disabled={!inputText.trim() || isLoading}
                className="flex h-8 w-8 items-center justify-center rounded-xl bg-pathfinder-500 text-ivory-50 hover:bg-pathfinder-600 disabled:opacity-50 transition-colors flex-shrink-0"
              >
                <Send className="h-3.5 w-3.5" />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  )
}
