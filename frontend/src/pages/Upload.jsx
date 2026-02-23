import { useState } from 'react'
import { Upload, ChevronDown, ChevronUp } from 'lucide-react'
import { VideoUploader } from '../components/VideoUploader'
import { Header } from '../components/Header'
import { Sidebar } from '../components/Sidebar'
import { useRequireAuth } from '../hooks/useAuth'
import { useProperties } from '../hooks/useQueries'
import { useUploadStore } from '../stores'

export const UploadPage = () => {
  const [selectedProperty, setSelectedProperty] = useState('')
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const uploads = useUploadStore((state) => state.uploads)
  const clearCompleted = useUploadStore((state) => state.clearCompleted)
  
  useRequireAuth()
  const { data: properties } = useProperties()

  const selectedPropertyName = properties?.find(p => p.id === selectedProperty)?.name || 'Select Property'

  return (
    <div className="min-h-screen flex">
      <Sidebar />
      
      <div className="flex-1 flex flex-col lg:ml-0">
        <Header title="Upload Video" />
        
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <div className="max-w-3xl mx-auto">
            <div className="card">
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Property
                </label>
                
                <div className="relative">
                  <button
                    onClick={() => setDropdownOpen(!dropdownOpen)}
                    className="w-full flex items-center justify-between px-4 py-2.5 border border-gray-300 rounded-lg bg-white hover:bg-gray-50"
                  >
                    <span className={selectedProperty ? 'text-gray-900' : 'text-gray-500'}>
                      {selectedPropertyName}
                    </span>
                    {dropdownOpen ? (
                      <ChevronUp className="w-5 h-5 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-400" />
                    )}
                  </button>

                  {dropdownOpen && (
                    <>
                      <div
                        className="fixed inset-0 z-10"
                        onClick={() => setDropdownOpen(false)}
                      />
                      <div className="absolute z-20 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
                        {properties?.map((property) => (
                          <button
                            key={property.id}
                            onClick={() => {
                              setSelectedProperty(property.id)
                              setDropdownOpen(false)
                            }}
                            className={`w-full px-4 py-2.5 text-left hover:bg-gray-50 ${
                              selectedProperty === property.id ? 'bg-primary-50 text-primary-700' : ''
                            }`}
                          >
                            {property.name}
                          </button>
                        ))}
                        {!properties?.length && (
                          <div className="px-4 py-3 text-gray-500 text-sm">
                            No properties available
                          </div>
                        )}
                      </div>
                    </>
                  )}
                </div>
              </div>

              {selectedProperty ? (
                <VideoUploader propertyId={selectedProperty} />
              ) : (
                <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-xl">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Please select a property first</p>
                </div>
              )}
            </div>

            {/* Upload History */}
            {uploads.length > 0 && (
              <div className="card mt-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-gray-900">Recent Uploads</h3>
                  <button
                    onClick={clearCompleted}
                    className="text-sm text-primary-600 hover:text-primary-500"
                  >
                    Clear Completed
                  </button>
                </div>

                <div className="space-y-3">
                  {uploads.map((upload) => (
                    <div key={upload.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${
                          upload.status === 'completed' ? 'bg-green-500' :
                          upload.status === 'error' ? 'bg-red-500' :
                          upload.status === 'uploading' ? 'bg-yellow-500' :
                          'bg-gray-400'
                        }`} />
                        <div>
                          <p className="text-sm font-medium text-gray-900">{upload.name}</p>
                          <p className="text-xs text-gray-500">
                            {(upload.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                      </div>

                      <span className={`text-xs px-2 py-1 rounded-full ${
                        upload.status === 'completed' ? 'bg-green-100 text-green-700' :
                        upload.status === 'error' ? 'bg-red-100 text-red-700' :
                        upload.status === 'uploading' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {upload.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}