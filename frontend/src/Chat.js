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

  const t = getTranslations(language);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
      const response = await fetch(`http://192.168.1.20:8000/interview/${sessionId}/question`, {
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
    if (!inputValue.trim() || loading) return;

    // 添加用户消息
    const userMessage = {
      text: inputValue,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };
    
    // Deduplicate messages before adding (but user messages won't be checked)
    setMessages(prev => {
      if (isDuplicateMessage(userMessage, prev)) {
        return prev;
      }
      return [...prev, userMessage];
    });
    
    const userText = inputValue;
    setInputValue('');
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`http://192.168.1.20:8000/interview/${sessionId}/question`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ answer: userText }),
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

  return (
    <div className="chat-container">
      <header className="chat-header">
        <div className="language-switch" onClick={onBack}>
          {t.back}
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
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder={t.typeAnswer}
          disabled={loading || showViewResults}
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