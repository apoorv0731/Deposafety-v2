import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Auth helpers
export const signUp = async (email, password, metadata = {}) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: metadata,
    },
  })
  return { data, error }
}

export const signIn = async (email, password) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })
  return { data, error }
}

export const signOut = async () => {
  const { error } = await supabase.auth.signOut()
  return { error }
}

export const getCurrentUser = async () => {
  const { data: { user }, error } = await supabase.auth.getUser()
  return { user, error }
}

export const getSession = async () => {
  const { data: { session }, error } = await supabase.auth.getSession()
  return { session, error }
}

// Database helpers
export const getProperties = async () => {
  const { data, error } = await supabase
    .from('properties')
    .select('*')
    .order('created_at', { ascending: false })
  return { data, error }
}

export const getProperty = async (id) => {
  const { data, error } = await supabase
    .from('properties')
    .select('*')
    .eq('id', id)
    .single()
  return { data, error }
}

export const createProperty = async (property) => {
  const { data, error } = await supabase
    .from('properties')
    .insert(property)
    .select()
    .single()
  return { data, error }
}

export const updateProperty = async (id, updates) => {
  const { data, error } = await supabase
    .from('properties')
    .update(updates)
    .eq('id', id)
    .select()
    .single()
  return { data, error }
}

export const deleteProperty = async (id) => {
  const { error } = await supabase
    .from('properties')
    .delete()
    .eq('id', id)
  return { error }
}

// Storage helpers
export const uploadVideo = async (file, path, onProgress) => {
  const { data, error } = await supabase.storage
    .from('videos')
    .upload(path, file, {
      cacheControl: '3600',
      upsert: false,
      onUploadProgress: onProgress,
    })
  return { data, error }
}

export const getVideoUrl = (path) => {
  const { data } = supabase.storage.from('videos').getPublicUrl(path)
  return data.publicUrl
}

export const uploadModel = async (file, path) => {
  const { data, error } = await supabase.storage
    .from('models')
    .upload(path, file, {
      cacheControl: '3600',
      upsert: false,
    })
  return { data, error }
}

export const getModelUrl = (path) => {
  const { data } = supabase.storage.from('models').getPublicUrl(path)
  return data.publicUrl
}

// Reports
export const getReports = async (propertyId) => {
  const { data, error } = await supabase
    .from('reports')
    .select('*')
    .eq('property_id', propertyId)
    .order('created_at', { ascending: false })
  return { data, error }
}

export const createReport = async (report) => {
  const { data, error } = await supabase
    .from('reports')
    .insert(report)
    .select()
    .single()
  return { data, error }
}