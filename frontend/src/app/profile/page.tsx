'use client'

import { AuthGuard } from '@/components/auth/AuthGuard'
import { AppLayout } from '@/components/layout/AppLayout'
import { useState } from 'react'
import {
  User,
  Briefcase,
  GraduationCap,
  Award,
  Target,
  Plus,
  Edit2,
  Trash2,
  MapPin,
  Mail,
  Phone,
  Linkedin,
  Github,
  Globe,
  Calendar,
  DollarSign,
  TrendingUp,
  Check,
  X,
} from 'lucide-react'

interface Education {
  id: string
  institution: string
  degree: string
  field: string
  startDate: string
  endDate: string
  gpa?: string
  achievements?: string[]
}

interface Experience {
  id: string
  company: string
  position: string
  location: string
  startDate: string
  endDate: string
  current: boolean
  description: string
  achievements: string[]
}

interface Skill {
  id: string
  name: string
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  category: string
}

interface Certification {
  id: string
  name: string
  issuer: string
  date: string
  expiryDate?: string
  credentialId?: string
}

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState<'overview' | 'experience' | 'education' | 'skills' | 'certifications'>('overview')
  const [isEditing, setIsEditing] = useState(false)

  // Sample profile data
  const [profile, setProfile] = useState({
    firstName: 'Alex',
    lastName: 'Johnson',
    headline: 'Full Stack Developer | AI Enthusiast',
    location: 'San Francisco, CA',
    email: 'alex.johnson@email.com',
    phone: '+1 (555) 123-4567',
    linkedin: 'linkedin.com/in/alexjohnson',
    github: 'github.com/alexjohnson',
    website: 'alexjohnson.dev',
    bio: 'Passionate software engineer with 5+ years of experience building scalable web applications. Specialized in React, Node.js, and cloud technologies.',
    careerGoals: 'Transition into AI/ML engineering role within the next 12 months',
    targetSalary: '$120,000 - $150,000',
  })

  const [education, setEducation] = useState<Education[]>([
    {
      id: '1',
      institution: 'Stanford University',
      degree: 'Bachelor of Science',
      field: 'Computer Science',
      startDate: '2015-09',
      endDate: '2019-06',
      gpa: '3.8',
      achievements: ['Dean\'s List', 'President of CS Club'],
    },
  ])

  const [experience, setExperience] = useState<Experience[]>([
    {
      id: '1',
      company: 'Tech Innovations Inc.',
      position: 'Senior Full Stack Developer',
      location: 'San Francisco, CA',
      startDate: '2021-03',
      endDate: '',
      current: true,
      description: 'Leading development of enterprise SaaS platform',
      achievements: [
        'Reduced API response time by 60% through optimization',
        'Mentored 5 junior developers',
        'Led migration to microservices architecture',
      ],
    },
    {
      id: '2',
      company: 'StartupXYZ',
      position: 'Full Stack Developer',
      location: 'San Francisco, CA',
      startDate: '2019-07',
      endDate: '2021-02',
      current: false,
      description: 'Built customer-facing web applications',
      achievements: [
        'Developed 10+ React components used across platform',
        'Implemented real-time chat feature with WebSocket',
      ],
    },
  ])

  const [skills, setSkills] = useState<Skill[]>([
    { id: '1', name: 'JavaScript', level: 'expert', category: 'Programming' },
    { id: '2', name: 'React', level: 'expert', category: 'Frontend' },
    { id: '3', name: 'Node.js', level: 'advanced', category: 'Backend' },
    { id: '4', name: 'Python', level: 'intermediate', category: 'Programming' },
    { id: '5', name: 'AWS', level: 'advanced', category: 'Cloud' },
    { id: '6', name: 'Docker', level: 'advanced', category: 'DevOps' },
  ])

  const [certifications, setCertifications] = useState<Certification[]>([
    {
      id: '1',
      name: 'AWS Certified Solutions Architect',
      issuer: 'Amazon Web Services',
      date: '2022-08',
      expiryDate: '2025-08',
      credentialId: 'AWS-SA-12345',
    },
  ])

  const tabs = [
    { id: 'overview', label: 'Overview', icon: User },
    { id: 'experience', label: 'Experience', icon: Briefcase },
    { id: 'education', label: 'Education', icon: GraduationCap },
    { id: 'skills', label: 'Skills', icon: TrendingUp },
    { id: 'certifications', label: 'Certifications', icon: Award },
  ]

  const skillLevelColors = {
    beginner: 'bg-gray-200',
    intermediate: 'bg-blue-200',
    advanced: 'bg-purple-200',
    expert: 'bg-green-200',
  }

  const skillLevelText = {
    beginner: 'text-gray-700',
    intermediate: 'text-blue-700',
    advanced: 'text-purple-700',
    expert: 'text-green-700',
  }

  return (
    <AuthGuard>
      <AppLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Professional Profile</h1>
              <p className="text-gray-600 mt-1">
                Build and showcase your professional journey
              </p>
            </div>
            <button
              onClick={() => setIsEditing(!isEditing)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                isEditing
                  ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {isEditing ? (
                <>
                  <X className="inline-block w-4 h-4 mr-2" />
                  Cancel
                </>
              ) : (
                <>
                  <Edit2 className="inline-block w-4 h-4 mr-2" />
                  Edit Profile
                </>
              )}
            </button>
          </div>

          {/* Profile Header Card */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="h-32 bg-gradient-to-r from-blue-500 to-purple-600"></div>
            <div className="px-6 pb-6">
              <div className="flex items-start gap-6 -mt-16">
                <div className="w-32 h-32 rounded-full bg-white border-4 border-white shadow-lg flex items-center justify-center text-4xl font-bold text-blue-600">
                  {profile.firstName[0]}{profile.lastName[0]}
                </div>
                <div className="mt-16 flex-1">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {profile.firstName} {profile.lastName}
                  </h2>
                  <p className="text-lg text-gray-600 mt-1">{profile.headline}</p>
                  
                  <div className="flex flex-wrap gap-4 mt-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <MapPin className="w-4 h-4" />
                      {profile.location}
                    </div>
                    <div className="flex items-center gap-1">
                      <Mail className="w-4 h-4" />
                      {profile.email}
                    </div>
                    <div className="flex items-center gap-1">
                      <Phone className="w-4 h-4" />
                      {profile.phone}
                    </div>
                  </div>

                  <div className="flex gap-3 mt-4">
                    {profile.linkedin && (
                      <a href={`https://${profile.linkedin}`} target="_blank" rel="noopener noreferrer" 
                         className="text-blue-600 hover:text-blue-700">
                        <Linkedin className="w-5 h-5" />
                      </a>
                    )}
                    {profile.github && (
                      <a href={`https://${profile.github}`} target="_blank" rel="noopener noreferrer"
                         className="text-gray-700 hover:text-gray-900">
                        <Github className="w-5 h-5" />
                      </a>
                    )}
                    {profile.website && (
                      <a href={`https://${profile.website}`} target="_blank" rel="noopener noreferrer"
                         className="text-blue-600 hover:text-blue-700">
                        <Globe className="w-5 h-5" />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="inline-block w-4 h-4 mr-2" />
                    {tab.label}
                  </button>
                )
              })}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="space-y-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="grid gap-6 md:grid-cols-2">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <User className="w-5 h-5 text-blue-600" />
                    About Me
                  </h3>
                  <p className="text-gray-700 leading-relaxed">{profile.bio}</p>
                </div>

                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <Target className="w-5 h-5 text-purple-600" />
                    Career Goals
                  </h3>
                  <p className="text-gray-700 leading-relaxed mb-4">{profile.careerGoals}</p>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <DollarSign className="w-4 h-4" />
                    <span className="font-medium">Target Salary:</span>
                    <span>{profile.targetSalary}</span>
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="md:col-span-2 grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
                    <div className="text-2xl font-bold text-blue-600">{experience.length}</div>
                    <div className="text-sm text-gray-600 mt-1">Years Experience</div>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-4 border border-purple-100">
                    <div className="text-2xl font-bold text-purple-600">{education.length}</div>
                    <div className="text-sm text-gray-600 mt-1">Degrees</div>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4 border border-green-100">
                    <div className="text-2xl font-bold text-green-600">{skills.length}</div>
                    <div className="text-sm text-gray-600 mt-1">Skills</div>
                  </div>
                  <div className="bg-orange-50 rounded-lg p-4 border border-orange-100">
                    <div className="text-2xl font-bold text-orange-600">{certifications.length}</div>
                    <div className="text-sm text-gray-600 mt-1">Certifications</div>
                  </div>
                </div>
              </div>
            )}

            {/* Experience Tab */}
            {activeTab === 'experience' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-semibold text-gray-900">Work Experience</h3>
                  {isEditing && (
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      <Plus className="inline-block w-4 h-4 mr-2" />
                      Add Experience
                    </button>
                  )}
                </div>

                {experience.map((exp, index) => (
                  <div key={exp.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
                            <Briefcase className="w-6 h-6 text-blue-600" />
                          </div>
                          <div>
                            <h4 className="text-lg font-semibold text-gray-900">{exp.position}</h4>
                            <p className="text-blue-600 font-medium">{exp.company}</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-4 mt-3 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <MapPin className="w-4 h-4" />
                            {exp.location}
                          </div>
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {exp.startDate} - {exp.current ? 'Present' : exp.endDate}
                          </div>
                          {exp.current && (
                            <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                              Current
                            </span>
                          )}
                        </div>

                        <p className="text-gray-700 mt-4">{exp.description}</p>

                        {exp.achievements.length > 0 && (
                          <div className="mt-4">
                            <h5 className="text-sm font-semibold text-gray-900 mb-2">Key Achievements:</h5>
                            <ul className="space-y-2">
                              {exp.achievements.map((achievement, i) => (
                                <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                                  <Check className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                                  {achievement}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>

                      {isEditing && (
                        <div className="flex gap-2 ml-4">
                          <button className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Education Tab */}
            {activeTab === 'education' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-semibold text-gray-900">Education</h3>
                  {isEditing && (
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      <Plus className="inline-block w-4 h-4 mr-2" />
                      Add Education
                    </button>
                  )}
                </div>

                {education.map((edu) => (
                  <div key={edu.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 rounded-lg bg-purple-100 flex items-center justify-center">
                            <GraduationCap className="w-6 h-6 text-purple-600" />
                          </div>
                          <div>
                            <h4 className="text-lg font-semibold text-gray-900">{edu.degree} in {edu.field}</h4>
                            <p className="text-purple-600 font-medium">{edu.institution}</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-4 mt-3 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {edu.startDate} - {edu.endDate}
                          </div>
                          {edu.gpa && (
                            <div>
                              <span className="font-medium">GPA:</span> {edu.gpa}
                            </div>
                          )}
                        </div>

                        {edu.achievements && edu.achievements.length > 0 && (
                          <div className="mt-4">
                            <h5 className="text-sm font-semibold text-gray-900 mb-2">Achievements:</h5>
                            <div className="flex flex-wrap gap-2">
                              {edu.achievements.map((achievement, i) => (
                                <span key={i} className="px-3 py-1 bg-purple-50 text-purple-700 rounded-full text-sm">
                                  {achievement}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {isEditing && (
                        <div className="flex gap-2 ml-4">
                          <button className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Skills Tab */}
            {activeTab === 'skills' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-semibold text-gray-900">Skills & Expertise</h3>
                  {isEditing && (
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      <Plus className="inline-block w-4 h-4 mr-2" />
                      Add Skill
                    </button>
                  )}
                </div>

                {/* Skills by Category */}
                {['Programming', 'Frontend', 'Backend', 'Cloud', 'DevOps'].map((category) => {
                  const categorySkills = skills.filter((s) => s.category === category)
                  if (categorySkills.length === 0) return null

                  return (
                    <div key={category} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4">{category}</h4>
                      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                        {categorySkills.map((skill) => (
                          <div key={skill.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex-1">
                              <div className="font-medium text-gray-900">{skill.name}</div>
                              <div className={`text-xs font-medium mt-1 capitalize ${skillLevelText[skill.level]}`}>
                                {skill.level}
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <div className="flex gap-1">
                                {[1, 2, 3, 4].map((level) => (
                                  <div
                                    key={level}
                                    className={`w-2 h-6 rounded-full ${
                                      level <= ['beginner', 'intermediate', 'advanced', 'expert'].indexOf(skill.level) + 1
                                        ? skillLevelColors[skill.level]
                                        : 'bg-gray-200'
                                    }`}
                                  />
                                ))}
                              </div>
                              {isEditing && (
                                <button className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors">
                                  <Trash2 className="w-3 h-3" />
                                </button>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}

            {/* Certifications Tab */}
            {activeTab === 'certifications' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-semibold text-gray-900">Certifications & Credentials</h3>
                  {isEditing && (
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      <Plus className="inline-block w-4 h-4 mr-2" />
                      Add Certification
                    </button>
                  )}
                </div>

                {certifications.map((cert) => (
                  <div key={cert.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 rounded-lg bg-orange-100 flex items-center justify-center">
                            <Award className="w-6 h-6 text-orange-600" />
                          </div>
                          <div>
                            <h4 className="text-lg font-semibold text-gray-900">{cert.name}</h4>
                            <p className="text-orange-600 font-medium">{cert.issuer}</p>
                          </div>
                        </div>

                        <div className="flex flex-wrap items-center gap-4 mt-3 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            <span>Issued: {cert.date}</span>
                          </div>
                          {cert.expiryDate && (
                            <div className="flex items-center gap-1">
                              <span>Expires: {cert.expiryDate}</span>
                            </div>
                          )}
                          {cert.credentialId && (
                            <div>
                              <span className="font-medium">ID:</span> {cert.credentialId}
                            </div>
                          )}
                        </div>
                      </div>

                      {isEditing && (
                        <div className="flex gap-2 ml-4">
                          <button className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </AppLayout>
    </AuthGuard>
  )
}
