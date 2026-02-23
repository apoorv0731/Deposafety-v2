import React from 'react';
import { Shield, Camera, FileCheck } from 'lucide-react';

function App() {
  const [apiStatus, setApiStatus] = React.useState('Checking...');
  
  React.useEffect(() => {
    fetch('https://deposafety-api.onrender.com/health')
      .then(res => res.json())
      .then(data => setApiStatus(data.status))
      .catch(() => setApiStatus('Offline'));
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">DepoSafety</h1>
          <p className="text-xl text-gray-600">Forensic-Grade 3D Evidence for Security Deposits</p>
          <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-green-100 text-green-800 rounded-full">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            API Status: {apiStatus}
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <Camera className="w-12 h-12 text-blue-600 mb-4" />
            <h3 className="text-xl font-bold mb-2">3D Capture</h3>
            <p className="text-gray-600">Millimeter-accurate digital twins</p>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <Shield className="w-12 h-12 text-blue-600 mb-4" />
            <h3 className="text-xl font-bold mb-2">Blockchain Proof</h3>
            <p className="text-gray-600">Immutable evidence anchoring</p>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <FileCheck className="w-12 h-12 text-blue-600 mb-4" />
            <h3 className="text-xl font-bold mb-2">Court-Ready</h3>
            <p className="text-gray-600">Legally admissible reports</p>
          </div>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-lg text-center">
          <h2 className="text-2xl font-bold mb-4">Application Deployed!</h2>
          <p className="text-gray-600 mb-6">
            Backend API is running at:<br />
            <code className="bg-gray-100 px-2 py-1 rounded">https://deposafety-api.onrender.com</code>
          </p>
          <div className="flex justify-center gap-4">
            <a href="https://deposafety-api.onrender.com/docs" target="_blank" rel="noopener noreferrer"
               className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">API Docs</a>
            <a href="https://github.com/apoorv0731/Deposafety-v2" target="_blank" rel="noopener noreferrer"
               className="px-6 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-900">GitHub Repo</a>
          </div>
        </div>

        <div className="mt-12 text-center text-gray-500">
          <p>Built for Pre-Seed Fundraising Round</p>
          <p className="text-sm mt-2">© 2026 DepoSafety</p>
        </div>
      </div>
    </div>
  );
}

export default App;
