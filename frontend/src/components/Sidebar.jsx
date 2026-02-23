import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Upload, 
  Box, 
  FileText, 
  Settings, 
  LogOut,
  Menu,
  X,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { useAuthStore, useUIStore } from '../stores'

const menuItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/upload', icon: Upload, label: 'Upload Video' },
  { path: '/viewer', icon: Box, label: '3D Viewer' },
  { path: '/reports', icon: FileText, label: 'Reports' },
  { path: '/settings', icon: Settings, label: 'Settings' },
]

export const Sidebar = () => {
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const logout = useAuthStore((state) => state.logout)
  const user = useAuthStore((state) => state.user)
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()

  const handleLogout = async () => {
    await logout()
    window.location.href = '/login'
  }

  const NavContent = () => (
    <>
      <div className="p-4">
        <div className={`flex items-center ${sidebarOpen ? 'justify-between' : 'justify-center'}`}>
          {sidebarOpen && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">DS</span>
              </div>
              <span className="font-bold text-gray-900">DepoSafety</span>
            </div>
          )}
          <button
            onClick={toggleSidebar}
            className="p-1.5 hover:bg-gray-100 rounded-lg hidden lg:block"
          >
            {sidebarOpen ? (
              <ChevronLeft className="w-5 h-5 text-gray-500" />
            ) : (
              <ChevronRight className="w-5 h-5 text-gray-500" />
            )}
          </button>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4">
        <ul className="space-y-1">
          {menuItems.map((item) => (
            <li key={item.path}>
              <a
                href={item.path}
                className={`
                  flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                  transition-colors duration-200
                  ${location.pathname === item.path
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                  }
                  ${!sidebarOpen && 'justify-center'}
                `}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {sidebarOpen && <span>{item.label}</span>}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      <div className="p-4 border-t">
        {sidebarOpen && user && (
          <div className="mb-4 px-3">
            <p className="text-sm font-medium text-gray-900 truncate">{user.email}</p>
            <p className="text-xs text-gray-500">{user.user_metadata?.role || 'User'}</p>
          </div>
        )}
        
        <button
          onClick={handleLogout}
          className={`
            flex items-center gap-3 px-3 py-2.5 w-full rounded-lg
            text-sm font-medium text-red-600 hover:bg-red-50
            transition-colors duration-200
            ${!sidebarOpen && 'justify-center'}
          `}
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          {sidebarOpen && <span>Logout</span>}
        </button>
      </div>
    </>
  )

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md"
      >
        {mobileOpen ? (
          <X className="w-6 h-6 text-gray-700" />
        ) : (
          <Menu className="w-6 h-6 text-gray-700" />
        )}
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-40
          bg-white border-r border-gray-200
          flex flex-col
          transition-all duration-300 ease-in-out
          ${sidebarOpen ? 'w-64' : 'w-20'}
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <NavContent />
      </aside>
    </>
  )
}