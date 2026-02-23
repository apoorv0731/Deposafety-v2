import { useState } from 'react'
import { ChevronDown, ChevronUp, FileText, Plus } from 'lucide-react'
import { ReportList } from '../components/ReportList'
import { Header } from '../components/Header'
import { Sidebar } from '../components/Sidebar'
import { useRequireAuth } from '../hooks/useAuth'
import { useProperties, useCreateReport } from '../hooks/useQueries'
import toast from 'react-hot-toast'

export const ReportsPage = () => {
  const [selectedProperty, setSelectedProperty] = useState('')
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newReport, setNewReport] = useState({ title: '', description: '' })
  
  useRequireAuth()
  const { data: properties } = useProperties()
  const createReport = useCreateReport()

  const selectedPropertyData = properties?.find(p => p.id === selectedProperty)

  const handleCreateReport = async (e) => {
    e.preventDefault()
    
    if (!selectedProperty) {
      toast.error('Please select a property first')
      return
    }

    try {
      await createReport.mutateAsync({
        ...newReport,
        property_id: selectedProperty,
        status: 'pending',
      })
      toast.success('Report created successfully')
      setShowCreateForm(false)
      setNewReport({ title: '', description: '' })
    } catch (err) {
      toast.error('Failed to create report')
    }
  }

  return (
    <div className="min-h-screen flex">
      <Sidebar />
      
      <div className="flex-1 flex flex-col lg:ml-0">
        <Header title="Evidence Reports" />
        
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <div className="max-w-4xl mx-auto">
            <div className="card mb-6">
              <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Property
                  </label>
                  
                  <div className="relative">
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

                <button
                  onClick={() => setShowCreateForm(!showCreateForm)}
                  disabled={!selectedProperty}
                  className="btn-primary flex items-center gap-2 disabled:opacity-50"
                >
                  <Plus className="w-4 h-4" />
                  New Report
                </button>
              </div>

              {showCreateForm && selectedProperty && (
                <form onSubmit={handleCreateReport} className="mt-6 pt-6 border-t border-gray-200">
                  <h3 className="font-medium text-gray-900 mb-4">Create New Report</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Report Title
                      </label>
                      <input
                        type="text"
                        required
                        value={newReport.title}
                        onChange={(e) => setNewReport({ ...newReport, title: e.target.value })}
                        className="input"
                        placeholder="e.g., Property Inspection - Jan 2024"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Description
                      </label>
                      <textarea
                        value={newReport.description}
                        onChange={(e) => setNewReport({ ...newReport, description: e.target.value })}
                        className="input h-24 resize-none"
                        placeholder="Enter report details..."
                      />
                    </div>

                    <div className="flex gap-3">
                      <button
                        type="button"
                        onClick={() => setShowCreateForm(false)}
                        className="btn-secondary"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={createReport.isPending}
                        className="btn-primary disabled:opacity-50"
                      >
                        {createReport.isPending ? 'Creating...' : 'Create Report'}
                      </button>
                    </div>
                  </div>
                </form>
              )}
            </div>

            {selectedProperty ? (
              <ReportList propertyId={selectedProperty} />
            ) : (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <FileText className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900">Select a Property</h3>
                <p className="text-gray-500 mt-1">Choose a property to view its reports</p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}