import { useState } from 'react'
import { ChevronDown, ChevronUp, Box } from 'lucide-react'
import { ModelViewer } from '../components/ModelViewer'
import { Header } from '../components/Header'
import { Sidebar } from '../components/Sidebar'
import { useRequireAuth } from '../hooks/useAuth'
import { useProperties } from '../hooks/useQueries'

export const ViewerPage = () => {
  const [selectedProperty, setSelectedProperty] = useState('')
  const [dropdownOpen, setDropdownOpen] = useState(false)
  
  useRequireAuth()
  const { data: properties } = useProperties()

  const selectedPropertyData = properties?.find(p => p.id === selectedProperty)

  return (
    <div className="min-h-screen flex">
      <Sidebar />
      
      <div className="flex-1 flex flex-col lg:ml-0">
        <Header title="3D Model Viewer" />
        
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <div className="max-w-6xl mx-auto h-[calc(100vh-200px)]">
            <div className="card h-full flex flex-col">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Property
                </label>
                
                <div className="relative max-w-md">
                  <button
                    onClick={() => setDropdownOpen(!dropdownOpen)}
                    className="w-full flex items-center justify-between px-4 py-2.5 border border-gray-300 rounded-lg bg-white hover:bg-gray-50"
                  >
                    <span className={selectedProperty ? 'text-gray-900' : 'text-gray-500'}>
                      {selectedPropertyData?.name || 'Select Property'}
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

              <div className="flex-1 border border-gray-200 rounded-xl overflow-hidden">
                {selectedProperty ? (
                  <ModelViewer 
                    propertyName={selectedPropertyData?.name}
                  />
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-gray-400">
                    <Box className="w-16 h-16 mb-4" />
                    <p className="text-lg">Select a property to view 3D model</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}