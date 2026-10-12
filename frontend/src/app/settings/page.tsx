'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import {
  ArrowLeft,
  User,
  Bell,
  Shield,
  Palette,
  Globe,
  Mail,
  Save,
  Trash2
} from 'lucide-react'

export default function SettingsPage() {
  const router = useRouter()
  const [saving, setSaving] = useState(false)
  
  // Settings state
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [pushNotifications, setPushNotifications] = useState(false)
  const [weeklyDigest, setWeeklyDigest] = useState(true)
  const [marketingEmails, setMarketingEmails] = useState(false)

  const handleSave = async () => {
    setSaving(true)
    // Simulate save
    await new Promise(resolve => setTimeout(resolve, 1000))
    setSaving(false)
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <Button
          variant="ghost"
          onClick={() => router.push('/dashboard')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Manage your account preferences and settings</p>
      </div>

      {/* Settings Tabs */}
      <Tabs defaultValue="account" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 lg:w-auto">
          <TabsTrigger value="account">Account</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="privacy">Privacy</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
        </TabsList>

        {/* Account Tab */}
        <TabsContent value="account" className="space-y-4">
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <User className="h-5 w-5 text-pathfinder-teal" />
              <h2 className="text-xl font-semibold">Account Information</h2>
            </div>

            <div className="space-y-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Full Name</Label>
                <Input id="name" defaultValue="John Doe" />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="email">Email Address</Label>
                <Input id="email" type="email" defaultValue="john@example.com" disabled />
                <p className="text-sm text-muted-foreground">
                  Email cannot be changed. Contact support if needed.
                </p>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="phone">Phone Number</Label>
                <Input id="phone" type="tel" placeholder="+1 (555) 000-0000" />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="location">Location</Label>
                <Input id="location" placeholder="City, State" />
              </div>

              <Separator className="my-4" />

              <div className="flex justify-between items-center">
                <Button onClick={handleSave} disabled={saving}>
                  {saving ? (
                    <>
                      <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Save Changes
                    </>
                  )}
                </Button>
              </div>
            </div>
          </Card>

          {/* Password Section */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <Shield className="h-5 w-5 text-pathfinder-teal" />
              <h2 className="text-xl font-semibold">Security</h2>
            </div>

            <div className="space-y-4">
              <div className="grid gap-2">
                <Label htmlFor="current-password">Current Password</Label>
                <Input id="current-password" type="password" />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="new-password">New Password</Label>
                <Input id="new-password" type="password" />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="confirm-password">Confirm New Password</Label>
                <Input id="confirm-password" type="password" />
              </div>

              <Button variant="outline">
                Update Password
              </Button>
            </div>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-4">
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <Bell className="h-5 w-5 text-pathfinder-teal" />
              <h2 className="text-xl font-semibold">Notification Preferences</h2>
            </div>

            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Email Notifications</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive email updates about your career progress
                  </p>
                </div>
                <Switch
                  checked={emailNotifications}
                  onCheckedChange={setEmailNotifications}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Push Notifications</Label>
                  <p className="text-sm text-muted-foreground">
                    Get real-time updates on milestones and recommendations
                  </p>
                </div>
                <Switch
                  checked={pushNotifications}
                  onCheckedChange={setPushNotifications}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Weekly Progress Digest</Label>
                  <p className="text-sm text-muted-foreground">
                    Summary of your weekly achievements and next steps
                  </p>
                </div>
                <Switch
                  checked={weeklyDigest}
                  onCheckedChange={setWeeklyDigest}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Marketing Communications</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive news, tips, and special offers
                  </p>
                </div>
                <Switch
                  checked={marketingEmails}
                  onCheckedChange={setMarketingEmails}
                />
              </div>

              <div className="pt-4">
                <Button onClick={handleSave} disabled={saving}>
                  {saving ? 'Saving...' : 'Save Preferences'}
                </Button>
              </div>
            </div>
          </Card>
        </TabsContent>

        {/* Privacy Tab */}
        <TabsContent value="privacy" className="space-y-4">
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <Shield className="h-5 w-5 text-pathfinder-teal" />
              <h2 className="text-xl font-semibold">Privacy & Data</h2>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="font-medium mb-2">Profile Visibility</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Control who can see your profile and career information
                </p>
                <div className="space-y-3">
                  <label className="flex items-center space-x-2">
                    <input type="radio" name="visibility" defaultChecked />
                    <span>Public - Visible to everyone</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input type="radio" name="visibility" />
                    <span>Private - Only visible to you</span>
                  </label>
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="font-medium mb-2">Data Export</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Download a copy of your data including resumes, goals, and progress
                </p>
                <Button variant="outline">
                  <Mail className="h-4 w-4 mr-2" />
                  Request Data Export
                </Button>
              </div>

              <Separator />

              <div>
                <h3 className="font-medium mb-2 text-red-600">Danger Zone</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Permanently delete your account and all associated data
                </p>
                <Button variant="destructive">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Account
                </Button>
              </div>
            </div>
          </Card>
        </TabsContent>

        {/* Preferences Tab */}
        <TabsContent value="preferences" className="space-y-4">
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <Palette className="h-5 w-5 text-pathfinder-teal" />
              <h2 className="text-xl font-semibold">Appearance & Language</h2>
            </div>

            <div className="space-y-6">
              <div>
                <Label className="mb-3 block">Theme</Label>
                <div className="grid grid-cols-3 gap-3">
                  <button className="p-4 border-2 border-pathfinder-teal rounded-lg">
                    <div className="w-full h-16 bg-white rounded mb-2"></div>
                    <span className="text-sm font-medium">Light</span>
                  </button>
                  <button className="p-4 border rounded-lg hover:border-gray-400">
                    <div className="w-full h-16 bg-gray-900 rounded mb-2"></div>
                    <span className="text-sm">Dark</span>
                  </button>
                  <button className="p-4 border rounded-lg hover:border-gray-400">
                    <div className="w-full h-16 bg-gradient-to-br from-white to-gray-900 rounded mb-2"></div>
                    <span className="text-sm">Auto</span>
                  </button>
                </div>
              </div>

              <Separator />

              <div>
                <Label htmlFor="language" className="mb-3 block">Language</Label>
                <select
                  id="language"
                  className="w-full p-2 border rounded-lg"
                  defaultValue="en"
                >
                  <option value="en">English</option>
                  <option value="es">Español</option>
                  <option value="fr">Français</option>
                  <option value="de">Deutsch</option>
                </select>
              </div>

              <Separator />

              <div>
                <Label htmlFor="timezone" className="mb-3 block">Timezone</Label>
                <select
                  id="timezone"
                  className="w-full p-2 border rounded-lg"
                  defaultValue="utc"
                >
                  <option value="utc-8">Pacific Time (PT)</option>
                  <option value="utc-5">Eastern Time (ET)</option>
                  <option value="utc">UTC</option>
                  <option value="utc+1">Central European Time (CET)</option>
                </select>
              </div>

              <div className="pt-4">
                <Button onClick={handleSave} disabled={saving}>
                  {saving ? 'Saving...' : 'Save Preferences'}
                </Button>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
