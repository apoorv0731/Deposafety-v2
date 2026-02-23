import { useState } from 'react'
import { Building2, MapPin, Calendar, MoreVertical, Edit, Trash2, Eye } from 'lucide-react'
import { useProperties, useDeleteProperty } from '../hooks/useQueries'
import toast from 'react-hot-toast'

export const PropertyCard = ({ property, onView, onEdit, onDelete }) => {
  const [menuOpen, setMenuOpen] = useState(false)

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
            <Building2 className="w-6 h-6 text-primary-600" />
          </div>
          
          <div>
            <h3 className="font-semibold text-gray-900">{property.name}</h3>
            <div className="flex items-center gap-1 text-sm text-gray-500 mt-1">
              <MapPin className="w-3.5 h-3.5" />
              <span className="truncate max-w-[200px]">{property.address}</span>
            </div>
          </div>
        </div>

        <div className="relative">
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <MoreVertical className="w-4 h-4 text-gray-500" />
          </button>

          {menuOpen && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setMenuOpen(false)}
              />
              <div className="absolute right-0 mt-1 w-40 bg-white rounded-lg shadow-lg border border-gray-200 z-20">
                <button
                  onClick={() => { onView(property); setMenuOpen(false) }}
                  className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full"
                >
                  <Eye className="w-4 h-4" /> View
                </button>
                <button
                  onClick={() => { onEdit(property); setMenuOpen(false) }}
                  className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full"
                >
                  <Edit className="w-4 h-4" /> Edit
                </button>
                <button
                  onClick={() => { onDelete(property.id); setMenuOpen(false) }}
                  className="flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 w-full"
                >
                  <Trash2 className="w-4 h-4" /> Delete
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-4">
            <span className="text-gray-500">
              Type: <span className="text-gray-900">{property.type || 'Residential'}</span>
            </span>
            <span className="text-gray-500">
              Status: 
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                property.status === 'active'
                  ? 'bg-green-100 text-green-700'
                  : 'bg-gray-100 text-gray-700'
              }`}>
                {property.status || 'Active'}
              </span>
            </span>
          </div>
          
          <div className="flex items-center gap-1 text-gray-500">
            <Calendar className="w-3.5 h-3.5" />
            <span>{formatDate(property.created_at)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export const PropertyList = () => {
  const { data: properties, isLoading, error } = useProperties()
  const deleteProperty = useDeleteProperty()

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this property?')) return
    
    try {
      await deleteProperty.mutateAsync(id)
      toast.success('Property deleted successfully')
    } catch (err) {
      toast.error('Failed to delete property')
    }
  }

  const handleView = (property) => {
    window.location.href = `/viewer?property=${property.id}`
  }

  const handleEdit = (property) => {
    // Open edit modal or navigate to edit page
    console.log('Edit property:', property)
  }

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="card animate-pulse">
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load properties</p>
      </div>
    )
  }

  if (!properties?.length) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Building2 className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900">No properties yet</h3>
        <p className="text-gray-500 mt-1">Add your first property to get started</p>
      </div>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {properties.map((property) => (
        <PropertyCard
          key={property.id}
          property={property}
          onView={handleView}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      ))}
    </div>
  )
}