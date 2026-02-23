import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores'
import { getCurrentUser } from '../lib/supabase'

export const useAuth = () => {
  const { user, setUser, setLoading, logout } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    setLoading(true)
    const { user, error } = await getCurrentUser()
    if (user && !error) {
      setUser(user)
    } else {
      setUser(null)
    }
    setLoading(false)
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return {
    user,
    isAuthenticated: !!user,
    isLoading: useAuthStore((state) => state.isLoading),
    checkAuth,
    handleLogout,
  }
}

export const useRequireAuth = () => {
  const { user, isLoading } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoading && !user) {
      navigate('/login')
    }
  }, [user, isLoading, navigate])

  return { user, isLoading }
}