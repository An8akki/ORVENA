import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ORVENA - AI-Powered Career Platform',
  description: 'Career intelligence, resume optimization, job matching, and interview preparation platform for students and early-career professionals',
  keywords: ['career', 'resume', 'jobs', 'interview preparation', 'AI', 'career guidance'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>{children}</body>
    </html>
  )
}
