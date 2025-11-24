import React, { useState, useEffect, useRef } from 'react';
import { generateInterviewQuestions } from '../services/openaiService';

const PreparePage = ({ mode, config, onBack, onStartInterview }) => {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [draftNotes, setDraftNotes] = useState('');
  const [countdown, setCountdown] = useState(config.thinkingTime);
  const [isWarning, setIsWarning] = useState(false);
  const [isFlashing, setIsFlashing] = useState(false);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState({ show: false, message: '', type: 'error' }); // 添加 toast 状态
  const intervalRef = useRef(null);
  const flashTimeoutRef = useRef(null);

  // 显示 toast 通知的函数
  const showToast = (message, type = 'error') => {
    setToast({ show: true, message, type });
    // 3秒后自动隐藏 toast
    setTimeout(() => {
      setToast({ show: false, message: '', type });
    }, 3000);
  };

  const generateAllQuestions = async () => {
    setLoading(true);
    setError(null);

    try {
      // Generate questions using DeepSeek model
      // Pass difficulty and questionLength options to the service
      const questions = await generateInterviewQuestions(config.questionCount, {
        difficulty: config.difficulty,
        questionLength: config.questionLength
      });
      setQuestions(questions);
    } catch (error) {
      console.error('Error generating questions with DeepSeek:', error);
      setError('生成面试题目失败，请稍后重试');
      showToast('Error generating questions with DeepSeek:' + error, 'error');
    }

    setLoading(false);
  };

  // Generate questions using DeepSeek model via LangChain
  useEffect(() => {
    generateAllQuestions();
  }, [config]);

  // Countdown effect
  useEffect(() => {
    if (loading || error) return;

    intervalRef.current = setInterval(() => {
      setCountdown(prev => {
        // Check if we're entering the last minute
        if (prev === 60 && !isWarning) {
          setIsWarning(true);
          startFlashing();
        }

        // If countdown finishes, automatically start the interview
        if (prev <= 1) {
          clearInterval(intervalRef.current);
          if (flashTimeoutRef.current) {
            clearTimeout(flashTimeoutRef.current);
          }
          handleStartInterview();
          return 0;
        }

        return prev - 1;
      });
    }, 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (flashTimeoutRef.current) {
        clearTimeout(flashTimeoutRef.current);
      }
    };
  }, [loading, isWarning, error]);

  const startFlashing = () => {
    // Flash 3 times (6 transitions: on/off/on/off/on/off)
    let count = 0;
    const flash = () => {
      if (count < 6) {
        setIsFlashing(count % 2 === 0); // Alternate between true and false
        count++;
        flashTimeoutRef.current = setTimeout(flash, 500);
      } else {
        setIsFlashing(false); // Ensure it ends with flashing off
      }
    };

    flash();
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStartInterview = () => {
    if (onStartInterview) {
      onStartInterview(draftNotes, questions);
    }
  };

  const handleRetry = () => {
    generateAllQuestions();
  };

  if (loading) {
    return (
      <div className="max-w-4xl w-full bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 py-6 px-6">
          <h1 className="text-2xl font-bold text-white">题目生成中...</h1>
        </div>
        <div className="p-8 flex flex-col items-center justify-center h-96">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-600">正在从 DeepSeek 大模型获取面试题目，请稍候...</p>
        </div>
        
        {/* Toast notification container */}
        {toast.show && (
          <div className="fixed top-4 right-4 z-50">
            <div className={`px-4 py-2 rounded-lg shadow-lg text-white ${
              toast.type === 'error' ? 'bg-red-500' : 'bg-green-500'
            }`}>
              {toast.message}
            </div>
          </div>
        )}
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl w-full bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 py-6 px-6">
          <h1 className="text-2xl font-bold text-white">结构化面试准备</h1>
        </div>
        <div className="p-8 flex flex-col items-center justify-center h-96">
          <div className="text-red-500 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <p className="text-gray-600 mb-6 text-center">{error}</p>
          <button
            onClick={handleRetry}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            重试
          </button>
          <button
            onClick={onBack}
            className="mt-4 text-blue-600 hover:text-blue-800 transition-colors"
          >
            返回主页
          </button>
        </div>
        
        {/* Toast notification container */}
        {toast.show && (
          <div className="fixed top-4 right-4 z-50">
            <div className={`px-4 py-2 rounded-lg shadow-lg text-white ${
              toast.type === 'error' ? 'bg-red-500' : 'bg-green-500'
            }`}>
              {toast.message}
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`max-w-4xl w-full bg-white rounded-2xl shadow-xl overflow-hidden ${isFlashing ? 'bg-red-500 bg-opacity-30' : ''}`}>
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 py-6 px-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white">结构化面试准备</h1>
          <button
            onClick={onBack}
            className="text-white hover:text-blue-200 transition-colors"
          >
            返回主页
          </button>
        </div>
        <div className="flex items-center mt-4 text-blue-100">
          <span className="mr-4">模式: {mode === 'real' ? '全真模拟' : '练习模式'}</span>
          <span>题目总数: {questions.length}</span>
        </div>
      </div>
      <div className="p-6">
        {/* Countdown Timer */}
        {mode !== 'real' && (<div className={`mb-6 p-4 rounded-lg text-center ${isWarning ? 'bg-yellow-100 border border-yellow-300' : 'bg-blue-50'}`}>
          <p className="text-gray-600 mb-2">准备时间倒计时</p>
          <p className={`text-3xl font-bold ${isWarning ? 'text-yellow-600 font-extrabold' : 'text-blue-700'}`}>
            {formatTime(countdown)}
          </p>
        </div>
        )}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">所有面试题目</h2>
          <div className="space-y-6">
            {questions.map((question, index) => (
              <div key={question.id} className="bg-gray-50 p-6 rounded-lg border border-gray-200">
                <div className="flex items-start mb-3">
                  <span className="flex-shrink-0 flex items-center justify-center h-8 w-8 rounded-full bg-blue-500 text-white font-medium mr-3">
                    {index + 1}
                  </span>
                  <p className="text-gray-700">{question.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Draft Notes Section */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">草稿区</h2>
          <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
            <textarea
              className="w-full h-40 p-3 border border-yellow-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500 resize-none"
              placeholder="在此记录您的答题思路和大纲..."
              value={draftNotes}
              onChange={(e) => setDraftNotes(e.target.value)}
            ></textarea>
            <p className="text-sm text-yellow-700 mt-2">
              您的草稿内容仅在此会话中保存，建议在准备阶段记录答题思路和要点。
            </p>
          </div>
        </div>

        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200 mb-6">
          <p className="text-yellow-700">
            请仔细阅读所有题目，做好答题准备。点击下方按钮开始正式答题。
          </p>
        </div>

        <div className="flex justify-center">
          <button
            onClick={handleStartInterview}
            className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
          >
            开始答题
          </button>
        </div>
      </div>
      
      {/* Toast notification container */}
      {toast.show && (
        <div className="fixed top-4 right-4 z-50">
          <div className={`px-4 py-2 rounded-lg shadow-lg text-white ${
            toast.type === 'error' ? 'bg-red-500' : 'bg-green-500'
          }`}>
            {toast.message}
          </div>
        </div>
      )}
    </div>
  );
};

export default PreparePage;