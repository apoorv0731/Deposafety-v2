import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      session: null,
      isLoading: true,
      
      setUser: (user) => set({ user, isLoading: false }),
      setSession: (session) => set({ session }),
      setLoading: (isLoading) => set({ isLoading }),
      
      logout: () => set({ user: null, session: null, isLoading: false }),
      
      isAuthenticated: () => !!get().user,
    }),
    {
      name: 'auth-storage',
    }
  )
)

export const useUIStore = create((set) => ({
  sidebarOpen: false,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  
  theme: 'light',
  setTheme: (theme) => set({ theme }),
}))

export const useUploadStore = create((set) => ({
  uploads: [],
  
  addUpload: (upload) => set((state) => ({
    uploads: [...state.uploads, { ...upload, status: 'pending', progress: 0 }],
  })),
  
  updateUpload: (id, updates) => set((state) => ({
    uploads: state.uploads.map((u) =
      u.id === id ? { ...u, ...updates } : u
    ),
  })),
  
  removeUpload: (id) => set((state) => ({
    uploads: state.uploads.filter((u) => u.id !== id),
  })),
  
  clearCompleted: () => set((state) => ({
    uploads: state.uploads.filter((u) => u.status !== 'completed'),
  })),
}))