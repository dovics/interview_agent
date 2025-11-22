import React, { useState, useEffect, useRef } from 'react';

const PreparePage = ({ mode, config, onBack, onStartInterview }) => {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [draftNotes, setDraftNotes] = useState('');
  const [countdown, setCountdown] = useState(config.thinkingTime);
  const [isWarning, setIsWarning] = useState(false);
  const [isFlashing, setIsFlashing] = useState(false);
  const intervalRef = useRef(null);
  const flashTimeoutRef = useRef(null);

  // Simulate fetching all questions from DeepSeek model at once
  useEffect(() => {
    const generateAllQuestions = async () => {
      setLoading(true);
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Generate all mock questions based on config
      const mockQuestions = [];
      for (let i = 1; i <= config.questionCount; i++) {
        mockQuestions.push({
          id: i,
          text: `请回答结构化面试问题 ${i}：关于公共服务意识和责任担当的问题。请结合实际经历，详细阐述您在面对复杂情况时如何平衡各方利益，确保公众利益最大化。`,
          thinkingTime: config.thinkingTime,
          answeringTime: config.answeringTime
        });
      }

      setQuestions(mockQuestions);
      setLoading(false);
    };

    generateAllQuestions();
  }, [config]);

  // Countdown effect
  useEffect(() => {
    if (loading) return;

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
  }, [loading, isWarning]);

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
    </div>
  );
};

export default PreparePage;