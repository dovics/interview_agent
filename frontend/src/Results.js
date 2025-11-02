import React, { useState, useEffect } from 'react';
import { getTranslations } from './i18n';

/**
 * @param {{ sessionId: string, language: string, onBack: () => void }} props
 * @returns {JSX.Element}
 */
function Results({ sessionId, language, onBack }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const t = getTranslations(language);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await fetch(`http://192.168.1.20:8000/interview/${sessionId}/result`);
        
        if (response.ok) {
          const data = await response.json();
          setResults(data);
        } else {
          setError(t.fetchQuestionFailed || 'Failed to fetch results');
        }
      } catch (err) {
        setError(t.networkError);
        console.error('Error fetching results:', err);
      } finally {
        setLoading(false);
      }
    };

    if (sessionId) {
      fetchResults();
    }
  }, [sessionId, t]);

  if (loading) {
    return (
      <div className="results-container">
        <header className="results-header">
          <div className="language-switch" onClick={onBack}>
            {t.back}
          </div>
          <h1>{t.interviewAssistant}</h1>
        </header>
        <div className="results-content">
          <p>{t.loading || 'Loading...'}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="results-container">
        <header className="results-header">
          <div className="language-switch" onClick={onBack}>
            {t.back}
          </div>
          <h1>{t.interviewAssistant}</h1>
        </header>
        <div className="results-content">
          <div className="error">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="results-container">
      <header className="results-header">
        <div className="language-switch" onClick={onBack}>
          {t.back}
        </div>
        <h1>{t.interviewAssistant}</h1>
      </header>
      
      <div className="results-content">
        <div className="score-section">
          <h2>{language === 'zh' ? '面试得分' : 'Interview Score'}</h2>
          <div className="score">{results?.final_score || 'N/A'}</div>
        </div>
        
        <div className="feedback-section">
          <h2>{language === 'zh' ? '详细评价' : 'Detailed Feedback'}</h2>
          <div className="feedback">{results?.final_feedback || 'No feedback available'}</div>
        </div>
      </div>
    </div>
  );
}

export default Results;