import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getProperties,
  getProperty,
  createProperty,
  updateProperty,
  deleteProperty,
  getReports,
  createReport,
} from '../lib/supabase'

// Properties
export const useProperties = () => {
  return useQuery({
    queryKey: ['properties'],
    queryFn: async () => {
      const { data, error } = await getProperties()
      if (error) throw error
      return data
    },
  })
}

export const useProperty = (id) => {
  return useQuery({
    queryKey: ['property', id],
    queryFn: async () => {
      const { data, error } = await getProperty(id)
      if (error) throw error
      return data
    },
    enabled: !!id,
  })
}

export const useCreateProperty = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: createProperty,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['properties'] })
    },
  })
}

export const useUpdateProperty = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, updates }) => updateProperty(id, updates),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['properties'] })
      queryClient.invalidateQueries({ queryKey: ['property', variables.id] })
    },
  })
}

export const useDeleteProperty = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: deleteProperty,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['properties'] })
    },
  })
}

// Reports
export const useReports = (propertyId) => {
  return useQuery({
    queryKey: ['reports', propertyId],
    queryFn: async () => {
      const { data, error } = await getReports(propertyId)
      if (error) throw error
      return data
    },
    enabled: !!propertyId,
  })
}

export const useCreateReport = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: createReport,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['reports', variables.property_id] })
    },
  })
}