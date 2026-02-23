import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { LoginPage, RegisterPage } from './pages/Auth'
import { DashboardPage } from './pages/Dashboard'
import { UploadPage } from './pages/Upload'
import { ViewerPage } from './pages/Viewer'
import { ReportsPage } from './pages/Reports'
import { SettingsPage } from './pages/Settings'
import { useAuthStore } from './stores'
import { supabase } from './lib/supabase'

function App() {
  const setUser = useAuthStore((state) => state.setUser)
  const setLoading = useAuthStore((state) => state.setLoading)

  useEffect(() => {
    // Check for existing session on mount
    const checkSession = async () => {
      setLoading(true)
      const { data: { session } } = await supabase.auth.getSession()
      if (session?.user) {
        setUser(session.user)
      }
      setLoading(false)
    }

    checkSession()

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session?.user || null)
      }
    )

    return () => subscription.unsubscribe()
  }, [setUser, setLoading])

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/" element={<DashboardPage />} />
      <Route path="/upload" element={<UploadPage />} />
      <Route path="/viewer" element={<ViewerPage />} />
      <Route path="/reports" element={<ReportsPage />} />
      <Route path="/settings" element={<SettingsPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App