import { useState, useEffect } from 'react'
import { 
  User, 
  Mail, 
  Building2, 
  Camera,
  Save,
  Loader2
} from 'lucide-react'
import { Header } from '../components/Header'
import { Sidebar } from '../components/Sidebar'
import { useRequireAuth } from '../hooks/useAuth'
import { useAuthStore } from '../stores'
import { supabase } from '../lib/supabase'
import toast from 'react-hot-toast'

export const SettingsPage = () => {
  useRequireAuth()
  const user = useAuthStore((state) => state.user)
  const setUser = useAuthStore((state) => state.setUser)
  
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    company: '',
  })
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    if (user) {
      setFormData({
        fullName: user.user_metadata?.full_name || '',
        email: user.email || '',
        company: user.user_metadata?.company || '',
      })
    }
  }, [user])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSaving(true)

    try {
      const { data, error } = await supabase.auth.updateUser({
        data: {
          full_name: formData.fullName,
          company: formData.company,
        },
      })

      if (error) throw error

      setUser(data.user)
      toast.success('Profile updated successfully')
    } catch (err) {
      toast.error('Failed to update profile')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      <Sidebar />
      
      <div className="flex-1 flex flex-col lg:ml-0">
        <Header title="Settings" />
        
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <div className="max-w-2xl mx-auto">
            <div className="card">
              <div className="flex items-center gap-4 mb-6">
                <div className="relative">
                  <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center">
                    <User className="w-10 h-10 text-primary-600" />
                  </div>
                  <button className="absolute bottom-0 right-0 p-1.5 bg-white rounded-full shadow-md border border-gray-200 hover:bg-gray-50">
                    <Camera className="w-4 h-4 text-gray-600" />
                  </button>
                </div>
                
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Profile Settings</h2>
                  <p className="text-gray-500">Manage your account information</p>
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      value={formData.fullName}
                      onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                      className="input pl-10"
                      placeholder="Your full name"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="email"
                      value={formData.email}
                      disabled
                      className="input pl-10 bg-gray-50 cursor-not-allowed"
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Company
                  </label>
                  <div className="relative">
                    <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      value={formData.company}
                      onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                      className="input pl-10"
                      placeholder="Your company name"
                    />
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <button
                    type="submit"
                    disabled={isSaving}
                    className="btn-primary flex items-center gap-2 disabled:opacity-50"
                  >
                    {isSaving ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4" />
                        Save Changes
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>

            {/* Security Section */}
            <div className="card mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Security</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b border-gray-100">
                  <div>
                    <p className="font-medium text-gray-900">Change Password</p>
                    <p className="text-sm text-gray-500">Update your account password</p>
                  </div>
                  <button className="btn-secondary">
                    Change
                  </button>
                </div>

                <div className="flex items-center justify-between py-3">
                  <div>
                    <p className="font-medium text-gray-900">Two-Factor Authentication</p>
                    <p className="text-sm text-gray-500">Add an extra layer of security</p>
                  </div>
                  <button className="btn-secondary">
                    Enable
                  </button>
                </div>
              </div>
            </div>

            {/* Danger Zone */}
            <div className="card mt-6 border-red-200">
              <h3 className="text-lg font-semibold text-red-600 mb-4">Danger Zone</h3>
              
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">Delete Account</p>
                  <p className="text-sm text-gray-500">Permanently delete your account and all data</p>
                </div>
                <button className="btn-danger">
                  Delete Account
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}