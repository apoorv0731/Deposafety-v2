import { useState } from 'react'
import { 
  FileText, 
  Download, 
  Calendar, 
  User, 
  CheckCircle,
  Clock,
  AlertCircle
} from 'lucide-react'
import { useReports } from '../hooks/useQueries'

export const ReportCard = ({ report }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />
      default:
        return <AlertCircle className="w-4 h-4 text-gray-500" />
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const handleDownload = () => {
    // Generate and download PDF
    const element = document.createElement('a')
    const file = new Blob(
      [JSON.stringify(report, null, 2)], 
      { type: 'application/json' }
    )
    element.href = URL.createObjectURL(file)
    element.download = `report-${report.id}.json`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <FileText className="w-5 h-5 text-primary-600" />
          </div>
          
          <div>
            <h3 className="font-medium text-gray-900">{report.title}</h3>
            <p className="text-sm text-gray-500 mt-0.5 line-clamp-2">{report.description}</p>
          </div>
        </div>

        <button
          onClick={handleDownload}
          className="p-2 hover:bg-gray-100 rounded-lg text-gray-500"
          title="Download Report"
        >
          <Download className="w-4 h-4" />
        </button>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5 text-gray-500">
              <User className="w-3.5 h-3.5" />
              <span>{report.created_by || 'System'}</span>
            </div>
            
            <div className="flex items-center gap-1.5 text-gray-500">
              <Calendar className="w-3.5 h-3.5" />
              <span>{formatDate(report.created_at)}</span>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            {getStatusIcon(report.status)}
            <span className={`text-sm capitalize ${
              report.status === 'completed' ? 'text-green-600' : 
              report.status === 'pending' ? 'text-yellow-600' : 'text-gray-600'
            }`}>
              {report.status}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export const ReportList = ({ propertyId }) => {
  const { data: reports, isLoading, error } = useReports(propertyId)

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="card animate-pulse h-32"></div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load reports</p>
      </div>
    )
  }

  if (!reports?.length) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <FileText className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900">No reports yet</h3>
        <p className="text-gray-500 mt-1">Reports will appear here once generated</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {reports.map((report) => (
        <ReportCard key={report.id} report={report} />
      ))}
    </div>
  )
}