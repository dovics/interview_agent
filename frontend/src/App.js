import React, { useState } from 'react';
import './App.css';
import { getTranslations } from './i18n';
import Chat from './Chat';
import Results from './Results';

/**
 * @returns {JSX.Element}
 */
function App() {
  const [currentPage, setCurrentPage] = useState('upload'); // 'upload', 'chat', or 'results'
  const [sessionId, setSessionId] = useState('');
  const [resume, setResume] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [language, setLanguage] = useState('zh');
  const [adaptiveQuestioning, setAdaptiveQuestioning] = useState(true);

  const t = getTranslations(language);

  /** 
   * @param {React.ChangeEvent<HTMLInputElement>} event 
   */
  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (file) {
      setResume(file);
      setError('');
    }
  };

  const handleAdaptiveQuestioningChange = (event) => {
    setAdaptiveQuestioning(event.target.checked);
  };

  const handleUpload = async () => {
    if (!resume) {
      setError(t.chooseFile);
      return;
    }

    const formData = new FormData();
    formData.append('file', resume);

    setUploading(true);
    setError('');

    try {
      const url = 'http://192.168.1.20:8000/interview/start?adaptive_questioning=' + (adaptiveQuestioning ? 'True' : 'False')
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        localStorage.setItem('session_id', data.session_id);
        console.log('Session ID stored:', data.session_id);
        // 跳转到聊天页面
        setCurrentPage('chat');
      } else {
        setError(t.uploadFailed);
      }
    } catch (err) {
      setError(t.networkError);
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const toggleLanguage = () => {
    setLanguage(prevLang => prevLang === 'zh' ? 'en' : 'zh');
  };

  const handleBackToUpload = () => {
    setCurrentPage('upload');
    setSessionId('');
  };

  const handleViewResults = () => {
    setCurrentPage('results');
  };

  const handleBackToChat = () => {
    setCurrentPage('chat');
  };

  return (
    <div className="App">
      {currentPage === 'upload' ? (
        <header className="App-header">
          <div className="language-switch" onClick={toggleLanguage}>
            {language === 'zh' ? 'EN' : '中文'}
          </div>
          <h1>{t.interviewAssistant}</h1>
          <div className="upload-container">
            <input
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileChange}
              disabled={uploading}
            />
            <div className="adaptive-questioning">
              <label>
                <input
                  type="checkbox"
                  checked={adaptiveQuestioning}
                  onChange={handleAdaptiveQuestioningChange}
                  disabled={uploading}
                />
                {language === 'zh' ? '开启自适应问题' : 'Enable Adaptive Questioning'}
              </label>
            </div>
            <button onClick={handleUpload} disabled={uploading || !resume}>
              {uploading ? t.uploading : t.uploadResume}
            </button>
            {error && <p className="error">{error}</p>}
            {resume && <p>{t.selectedFile} {resume.name}</p>}
          </div>
        </header>
      ) : currentPage === 'chat' ? (
        <Chat
          sessionId={sessionId}
          language={language}
          onBack={handleBackToUpload}
          onViewResults={handleViewResults}
        />
      ) : (
        <Results
          sessionId={sessionId}
          language={language}
          onBack={handleBackToChat}
        />
      )}
    </div>
  );
}

export default App;