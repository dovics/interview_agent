import React, { useState, useEffect, useRef } from 'react';
import { evaluateCandidateAnswers } from '../services/openaiService';
import html2canvas from 'html2canvas';
import ShareModal from './ShareModal';

const ResultPage = ({ questions, answer, onBackToStart }) => {
  const [evaluation, setEvaluation] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showScreenshot, setShowScreenshot] = useState(false);
  const [screenshot, setScreenshot] = useState(null);
  const resultRef = useRef();
  const screenshotRef = useRef(); // 新增用于截图的ref

  useEffect(() => {
    evaluateAnswers();
  }, []);

  // 模拟评分过程
  const evaluateAnswers = async () => {
    try {
      setIsLoading(true);
      
      // 调用大模型进行评分
      const evaluationData = await evaluateCandidateAnswers(questions, answer);
      
      setEvaluation(evaluationData);
      setError(null);
      setIsLoading(false);
    } catch (err) {
      console.error('评分过程中发生错误:', err);
      setError('评分过程中发生错误，请稍后重试');
      setIsLoading(false);
    }
  };

  const handleShare = async () => {
    if (!screenshotRef.current) return;
    
    try {
      const canvas = await html2canvas(screenshotRef.current, {
        useCORS: true,
        allowTaint: true,
        scale: 2 // 提高图片质量
      });
      
      const imgData = canvas.toDataURL('image/png');
      setScreenshot(imgData);
      setShowScreenshot(true);
    } catch (err) {
      console.error('截图过程中发生错误:', err);
      setError('截图过程中发生错误，请稍后重试');
    }
  };


  return (
    <div className="max-w-4xl w-full bg-white rounded-2xl shadow-xl overflow-hidden">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 py-6 px-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white">面试结果与评分</h1>
          <div className="flex space-x-2">
            <button
              onClick={handleShare}
              className="text-white hover:text-blue-200 transition-colors"
            >
              分享
            </button>
            <button
              onClick={onBackToStart}
              className="text-white hover:text-blue-200 transition-colors"
            >
              返回主页
            </button>
          </div>
        </div>
      </div>

      <ShareModal 
        isOpen={showScreenshot}
        onClose={() => setShowScreenshot(false)}
        screenshot={screenshot}
      />

      <div className="p-6">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-gray-600">正在分析您的回答并生成评分...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-700 font-medium">{error}</p>
            <button
              onClick={evaluateAnswers}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            >
              重新尝试
            </button>
          </div>
        ) : (
          <div ref={resultRef}>
            {/* 截图区域开始 */}
            <div ref={screenshotRef}>
              {/* 总体评分 */}
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6 mb-8 text-center">
                <h2 className="text-xl font-semibold text-gray-800 mb-2">总体评分</h2>
                <div className="text-5xl font-bold text-green-600 mb-2">{evaluation?.overallScore || 0}</div>
                <p className="text-gray-600">满分100分</p>
              </div>

              {/* 评价详情 */}
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-gray-800 border-b pb-2">综合评价</h3>
                
                <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                      <h5 className="font-medium text-green-800 mb-2 flex items-center">
                        <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        优点
                      </h5>
                      <ul className="list-disc list-inside text-green-700 space-y-1">
                        {evaluation?.strengths && evaluation.strengths.map((strength, i) => (
                          <li key={i}>{strength}</li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
                      <h5 className="font-medium text-amber-800 mb-2 flex items-center">
                        <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                        改进建议
                      </h5>
                      <ul className="list-disc list-inside text-amber-700 space-y-1">
                        {evaluation?.improvements && evaluation.improvements.map((improvement, i) => (
                          <li key={i}>{improvement}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                    <h5 className="font-medium text-blue-800 mb-2">综合评语</h5>
                    <p className="text-blue-700 whitespace-pre-wrap">{evaluation?.feedback}</p>
                  </div>
                </div>
                              
                {/* 统一展示所有问题和答案 */}
                <div className="space-y-6">
                  <h3 className="text-xl font-semibold text-gray-800 border-b pb-2">问题与回答</h3>
                  
                  <div className="border border-gray-200 rounded-lg p-6">
                    <div className="space-y-3 mb-6">
                      {questions.map((question, index) => (
                        <div key={question.id} className="flex">
                          <span className="mr-2 text-gray-500">{index + 1}.</span>
                          <span className="text-gray-800">{question.text}</span>
                        </div>
                      ))}
                    </div>
                    
                    <h4 className="font-medium text-gray-700 mb-4">您的回答：</h4>
                    <div className="bg-gray-50 p-4 rounded-lg border">
                      <p className="text-gray-700 whitespace-pre-wrap">{answer || '未提供回答'}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            {/* 截图区域结束 */}

            {/* 操作按钮 */}
            <div className="flex justify-center mt-8 space-x-4">
              <button
                onClick={handleShare}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
              >
                分享
              </button>
              <button
                onClick={onBackToStart}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                完成
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultPage;