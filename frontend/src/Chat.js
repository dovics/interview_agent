import React, { useState, useEffect, useRef, useCallback } from 'react';
import { getTranslations } from './i18n';

/**
 * @param {{ sessionId: string, language: string, onBack: () => void, onViewResults: () => void }} props
 * @returns {JSX.Element}
 */
function Chat({ sessionId, language, onBack, onViewResults }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showViewResults, setShowViewResults] = useState(false);
  const [firstQuestionFetched, setFirstQuestionFetched] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const t = getTranslations(language);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const toggleLanguage = () => {
    const newLanguage = language === 'zh' ? 'en' : 'zh';
    // We need to pass this back to the parent component to update the global state
    window.dispatchEvent(new CustomEvent('languageChange', { detail: newLanguage }));
  };

  const toggleTheme = () => {
    const currentTheme = document.querySelector('.App').getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.querySelector('.App').setAttribute('data-theme', newTheme);
    // We need to pass this back to the parent component to update the global state
    window.dispatchEvent(new CustomEvent('themeChange', { detail: newTheme }));
  };

  // 自动调整文本域高度
  const adjustTextareaHeight = useCallback(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    adjustTextareaHeight();
  }, [inputValue, adjustTextareaHeight]);

  // Function to check if a message already exists in the messages array
  // Only check for agent messages
  const isDuplicateMessage = (newMessage, messagesList) => {
    // Only check for duplicates for agent messages
    if (newMessage.sender !== 'agent') {
      return false;
    }
    
    return messagesList.some(message => 
      message.text === newMessage.text && 
      message.sender === 'agent'
    );
  };

  const fetchFirstQuestion = useCallback(async () => {
    // Prevent fetching the first question multiple times
    if (firstQuestionFetched) return;
    
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`/api/v1/interview/${sessionId}/question`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const data = await response.json();
        const newMessage = { 
          text: data.question, 
          sender: 'agent',
          timestamp: new Date().toLocaleTimeString()
        };
        
        // Deduplicate messages before adding
        setMessages(prev => {
          if (isDuplicateMessage(newMessage, prev)) {
            return prev;
          }
          return [...prev, newMessage];
        });
        
        // Check if interview is completed
        if (data.progress && data.progress.stage === 'completed') {
          setShowViewResults(true);
        }
        
        // Mark that we've fetched the first question
        setFirstQuestionFetched(true);
      } else {
        setError(t.fetchQuestionFailed || 'Failed to fetch question');
      }
    } catch (err) {
      setError(t.networkError);
      console.error('Error fetching question:', err);
    } finally {
      setLoading(false);
    }
  }, [sessionId, t, firstQuestionFetched]);

  useEffect(() => {
    // 获取第一个问题
    fetchFirstQuestion();
  }, [fetchFirstQuestion]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim() || loading || showViewResults) return;

    // Add user message to chat
    const userMessage = {
      text: inputValue,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`/api/v1/interview/${sessionId}/answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ answer: inputValue }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Add agent message to chat
        const newMessage = {
          text: data.question || data.final_feedback || '...',
          sender: 'agent',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        
        setMessages(prev => {
          if (isDuplicateMessage(newMessage, prev)) {
            return prev;
          }
          return [...prev, newMessage];
        });
        
        // Check if interview is completed
        if (data.progress && data.progress.stage === 'completed') {
          setShowViewResults(true);
        }
      } else {
        setError(t.fetchQuestionFailed || 'Failed to fetch question');
      }
    } catch (err) {
      setError(t.networkError);
      console.error('Error submitting answer:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <div className="controls">
          <div className="language-switch" onClick={toggleLanguage}>
            {language === 'zh' ? 'EN' : '中文'}
          </div>
          <div className="theme-switch" onClick={toggleTheme}>
            {document.querySelector('.App')?.getAttribute('data-theme') === 'dark' ? '☀️' : '🌙'}
          </div>
          <div className="back-button" onClick={onBack}>
            {t.back}
          </div>
        </div>
        <h1>{t.interviewAssistant}</h1>
      </header>
      
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender}`}>
            <div className="message-content">
              <div className="message-text">{message.text}</div>
              <div className="message-time">{message.timestamp}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="message agent">
            <div className="message-content">
              <div className="message-text">{t.typing}</div>
            </div>
          </div>
        )}
        {showViewResults && (
          <div className="message agent">
            <div className="message-content">
              <div className="message-text">
                <button className="view-results-button" onClick={onViewResults}>
                  {language === 'zh' ? '点击查看面试结果' : 'Click to view interview results'}
                </button>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <form className="chat-input" onSubmit={handleSubmit}>
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t.typeAnswer}
          disabled={loading || showViewResults}
          rows={1}
        />
        <button type="submit" disabled={loading || !inputValue.trim() || showViewResults}>
          {t.send}
        </button>
      </form>
      
      {error && <div className="error">{error}</div>}
    </div>
  );
}

export default Chat;