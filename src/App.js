import React, { useState } from 'react';
import StartPage from './pages/StartPage';
import ConfigPage from './pages/ConfigPage';
import PreparePage from './pages/PreparePage';
import './App.css';

function App() {
  const [showConfig, setShowConfig] = useState(false);
  const [currentPage, setCurrentPage] = useState('start'); // 'start', 'prepare'
  const [interviewMode, setInterviewMode] = useState(''); // 'real' or 'practice'
  const [config, setConfig] = useState({
    questionCount: 3,
    thinkingTime: 300, // 5 minutes in seconds
    answeringTime: 600 // 10 minutes in seconds
  });

  const toggleConfig = () => {
    setShowConfig(!showConfig);
  };

  const saveConfig = (newConfig) => {
    // Save the interview configuration
    setConfig({
      ...config,
      ...newConfig.interviewConfig
    });
    console.log('Interview Config:', newConfig.interviewConfig);
    console.log('Model Config:', newConfig.modelConfig);
  };

  const startInterview = (mode) => {
    setInterviewMode(mode);
    setCurrentPage('prepare');
  };

  const handleBackToStart = () => {
    setCurrentPage('start');
  };

  const handleStartInterview = () => {
    // TODO: 实现开始答题的功能
    alert('开始答题功能待实现');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col items-center justify-center p-4">
      {/* Configuration Button */}
      <div className="absolute top-4 right-4">
        <button 
          onClick={toggleConfig}
          className="bg-white rounded-full p-2 shadow-md hover:bg-gray-100 transition-all duration-300"
          aria-label="Configuration"
        >
          <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
          </svg>
        </button>
      </div>

      {/* Configuration Modal */}
      {showConfig && (
        <ConfigPage 
          onClose={toggleConfig}
          onSave={saveConfig}
        />
      )}

      {/* Main Content */}
      {currentPage === 'start' && (
        <StartPage onStartInterview={startInterview} />
      )}
      
      {currentPage === 'prepare' && (
        <PreparePage 
          mode={interviewMode} 
          config={config} 
          onBack={handleBackToStart} 
          onStartInterview={handleStartInterview}
        />
      )}
    </div>
  );
}

export default App;