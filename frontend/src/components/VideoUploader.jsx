import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, X, FileVideo } from 'lucide-react'
import toast from 'react-hot-toast'
import { supabase } from '../lib/supabase'
import { useUploadStore } from '../stores'

export const VideoUploader = ({ propertyId, onUploadComplete }) => {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const addUpload = useUploadStore((state) => state.addUpload)
  const updateUpload = useUploadStore((state) => state.updateUpload)

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return

    if (!file.type.startsWith('video/')) {
      toast.error('Please upload a video file')
      return
    }

    setUploading(true)
    setProgress(0)

    const uploadId = Date.now().toString()
    const filePath = `${propertyId}/${Date.now()}_${file.name}`

    addUpload({
      id: uploadId,
      name: file.name,
      size: file.size,
      propertyId,
    })

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 500)

      const { data, error } = await supabase.storage
        .from('videos')
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: false,
        })

      clearInterval(progressInterval)

      if (error) throw error

      setProgress(100)
      updateUpload(uploadId, { status: 'completed', progress: 100 })
      toast.success('Video uploaded successfully!')
      
      if (onUploadComplete) {
        onUploadComplete(data)
      }
    } catch (error) {
      console.error('Upload error:', error)
      updateUpload(uploadId, { status: 'error', error: error.message })
      toast.error(`Upload failed: ${error.message}`)
    } finally {
      setUploading(false)
    }
  }, [propertyId, addUpload, updateUpload, onUploadComplete])

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.mov', '.avi', '.webm', '.mkv'],
    },
    maxFiles: 1,
    disabled: uploading,
  })

  const clearFile = () => {
    acceptedFiles.length = 0
    setProgress(0)
  }

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
          transition-colors duration-200
          ${isDragActive 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center gap-4">
          <div className="p-4 bg-primary-100 rounded-full">
            <Upload className="w-8 h-8 text-primary-600" />
          </div>
          
          {isDragActive ? (
            <p className="text-primary-600 font-medium">Drop the video here...</p>
          ) : (
            <>
              <p className="text-gray-700 font-medium">
                Drag & drop a video here, or click to select
              </p>
              <p className="text-gray-500 text-sm">
                Supports MP4, MOV, AVI, WebM (max 500MB)
              </p>
            </>
          )}
        </div>
      </div>

      {acceptedFiles.length > 0 && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileVideo className="w-5 h-5 text-gray-500" />
              <div>
                <p className="text-sm font-medium text-gray-900">{acceptedFiles[0].name}</p>
                <p className="text-xs text-gray-500">
                  {(acceptedFiles[0].size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            {!uploading && (
              <button
                onClick={clearFile}
                className="p-1 hover:bg-gray-200 rounded">
                <X className="w-4 h-4 text-gray-500" />
              </button>
            )}
          </div>

          {uploading && (
            <div className="mt-3">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Uploading...{progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}