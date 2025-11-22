import React from 'react';

const StartPage = ({ onStartInterview }) => {
  return (
    <div className="max-w-md w-full bg-white rounded-2xl shadow-xl overflow-hidden">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 py-8 px-6 text-center">
        <h1 className="text-3xl font-bold text-white mb-2">公务员结构化面试系统</h1>
        <p className="text-blue-100">请选择练习模式开始您的面试准备</p>
      </div>
      
      <div className="p-8">
        <div className="space-y-6">
          <div className="group relative">
            <button 
              onClick={() => onStartInterview('real')}
              className="w-full bg-white border-2 border-blue-500 rounded-xl py-5 px-6 text-left hover:bg-blue-50 transition-all duration-300 shadow-sm hover:shadow-md"
            >
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-xl font-bold text-gray-800">全真模拟</h2>
                  <p className="text-gray-600 mt-1">真实考试环境体验</p>
                </div>
                <div className="bg-blue-100 rounded-full p-3">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
              </div>
            </button>
            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-3 w-64 px-4 py-2 bg-gray-800 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
              <p>考试过程中不显示剩余时间，仅在最后一分钟时闪烁提醒</p>
              <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-gray-800"></div>
            </div>
          </div>
          
          <div className="group relative">
            <button 
              onClick={() => onStartInterview('practice')}
              className="w-full bg-white border-2 border-green-500 rounded-xl py-5 px-6 text-left hover:bg-green-50 transition-all duration-300 shadow-sm hover:shadow-md"
            >
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-xl font-bold text-gray-800">练习模式</h2>
                  <p className="text-gray-600 mt-1">学习与练习环境</p>
                </div>
                <div className="bg-green-100 rounded-full p-3">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path>
                  </svg>
                </div>
              </div>
            </button>
            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-3 w-64 px-4 py-2 bg-gray-800 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
              <p>实时显示倒计时，帮助您掌握答题节奏</p>
              <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-gray-800"></div>
            </div>
          </div>
        </div>
        
        <div className="mt-10 text-center">
          <p className="text-gray-500 text-sm">
            根据公务员结构化面试标准设计，助您顺利通过考试
          </p>
        </div>
      </div>
    </div>
  );
};

export default StartPage;