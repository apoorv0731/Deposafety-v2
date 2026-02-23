import { useRef, useState, Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Grid, Box, Sphere, Cylinder } from '@react-three/drei'
import * as THREE from 'three'

// Sample 3D building component
const Building = ({ color = '#3b82f6' }) => {
  const meshRef = useRef()
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.1
    }
  })

  return (
    <group ref={meshRef}>
      {/* Main building */}
      <Box args={[2, 3, 2]} position={[0, 1.5, 0]}>
        <meshStandardMaterial color={color} />
      </Box>
      
      {/* Roof */}
      <Cylinder args={[1.5, 1.5, 0.5, 4]} position={[0, 3.25, 0]} rotation={[0, Math.PI / 4, 0]}>
        <meshStandardMaterial color="#1e40af" />
      </Cylinder>
      
      {/* Windows */}
      {[-0.5, 0.5].map((x, i) => (
        <group key={i}>
          {[1, 2].map((y, j) => (
            <Box key={j} args={[0.4, 0.5, 0.1]} position={[x, y, 1.05]}>
              <meshStandardMaterial color="#93c5fd" emissive="#1e3a8a" emissiveIntensity={0.2} />
            </Box>
          ))}
        </group>
      ))}
      
      {/* Door */}
      <Box args={[0.6, 1.2, 0.1]} position={[0, 0.6, 1.05]}>
        <meshStandardMaterial color="#78350f" />
      </Box>
      
      {/* Ground marker */}
      <Box args={[3, 0.1, 3]} position={[0, 0.05, 0]}>
        <meshStandardMaterial color="#e5e7eb" />
      </Box>
    </group>
  )
}

// Sample terrain
const Terrain = () => {
  return (
    <Grid
      position={[0, 0, 0]}
      args={[20, 20]}
      cellSize={1}
      cellThickness={0.5}
      cellColor="#6b7280"
      sectionSize={5}
      sectionThickness={1}
      sectionColor="#374151"
      fadeDistance={25}
      fadeStrength={1}
      infiniteGrid
    />
  )
}

// Loading fallback
const Loader = () => (
  <div className="flex items-center justify-center h-full">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
  </div>
)

export const ModelViewer = ({ modelUrl, propertyName = 'Property' }) => {
  const [autoRotate, setAutoRotate] = useState(true)
  const [wireframe, setWireframe] = useState(false)

  return (
    <div className="w-full h-full flex flex-col">
      {/* Controls */}
      <div className="flex items-center justify-between p-4 bg-gray-100 border-b">
        <div>
          <h3 className="font-semibold text-gray-900">{propertyName}</h3>
          <p className="text-sm text-gray-500">3D Model Viewer</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setAutoRotate(!autoRotate)}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
              autoRotate 
                ? 'bg-primary-600 text-white' 
                : 'bg-white text-gray-700 border hover:bg-gray-50'
            }`}
          >
            Auto Rotate
          </button>
          <button
            onClick={() => setWireframe(!wireframe)}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
              wireframe 
                ? 'bg-primary-600 text-white' 
                : 'bg-white text-gray-700 border hover:bg-gray-50'
            }`}
          >
            Wireframe
          </button>
        </div>
      </div>

      {/* 3D Canvas */}
      <div className="flex-1 min-h-[400px]">
        <Canvas
          camera={{ position: [5, 5, 5], fov: 50 }}
          style={{ background: '#f9fafb' }}
        >
          <Suspense fallback={null}>
            <ambientLight intensity={0.5} />
            <directionalLight position={[10, 10, 5]} intensity={1} />
            <pointLight position={[-10, -10, -10]} intensity={0.5} />
            
            <Building />
            <Terrain />
            
            <OrbitControls
              autoRotate={autoRotate}
              autoRotateSpeed={2}
              enablePan={true}
              enableZoom={true}
              minDistance={3}
              maxDistance={15}
            />
          </Suspense>
        </Canvas>
      </div>

      {/* Instructions */}
      <div className="p-4 bg-gray-50 border-t text-sm text-gray-600">
        <div className="flex items-center gap-6">
          <span>🖱️ Left click + drag to rotate</span>
          <span>🖱️ Right click + drag to pan</span>
          <span>🖱️ Scroll to zoom</span>
        </div>
      </div>
    </div>
  )
}

export default ModelViewer