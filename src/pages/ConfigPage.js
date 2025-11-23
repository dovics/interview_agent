import React, { useState } from 'react';

const ConfigPage = ({ onClose, onSave }) => {
  const [activeTab, setActiveTab] = useState('interview'); // 'interview' or 'model'
  const [interviewConfig, setInterviewConfig] = useState(() => {
    // Load interview config from localStorage or use defaults
    const savedInterviewConfig = localStorage.getItem('interviewConfig');
    return savedInterviewConfig ? JSON.parse(savedInterviewConfig) : {
      questionCount: 3,
      thinkingTime: 300, // 5 minutes in seconds
      answeringTime: 600, // 10 minutes in seconds
      difficulty: 'medium', // 题目难度: easy, medium, hard
      questionLength: 'medium' // 题目长度: short, medium, long
    };
  });
  
  const [modelConfig, setModelConfig] = useState(() => {
    // Load model config from localStorage or use defaults
    const savedModelConfig = localStorage.getItem('modelConfig');
    return savedModelConfig ? JSON.parse(savedModelConfig) : {
      apiToken: '',
      model: 'deepseek'
    };
  });

  const handleInterviewConfigChange = (field, value) => {
    setInterviewConfig({
      ...interviewConfig,
      [field]: value
    });
  };

  const handleModelConfigChange = (field, value) => {
    setModelConfig({
      ...modelConfig,
      [field]: value
    });
  };

  const handleSave = () => {
    // Save configs to localStorage
    localStorage.setItem('interviewConfig', JSON.stringify(interviewConfig));
    localStorage.setItem('modelConfig', JSON.stringify(modelConfig));
    
    // Pass the configs to the parent component
    onSave({
      interviewConfig,
      modelConfig
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800">配置选项</h2>
            <button 
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-gray-200 mb-6">
            <button
              className={`py-2 px-4 font-medium text-sm ${activeTab === 'interview' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
              onClick={() => setActiveTab('interview')}
            >
              面试配置
            </button>
            <button
              className={`py-2 px-4 font-medium text-sm ${activeTab === 'model' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
              onClick={() => setActiveTab('model')}
            >
              大模型配置
            </button>
          </div>

          {/* Tab Content */}
          <div className="mb-8">
            {/* Interview Configuration Tab */}
            {activeTab === 'interview' && (
              <div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      题目数量
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="20"
                      value={interviewConfig.questionCount}
                      onChange={(e) => handleInterviewConfigChange('questionCount', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">设置面试题目总数 (1-20)</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      思考时间 (秒)
                    </label>
                    <input
                      type="number"
                      min="30"
                      max="3600"
                      value={interviewConfig.thinkingTime}
                      onChange={(e) => handleInterviewConfigChange('thinkingTime', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">每道题的思考时间 (30-3600 秒)</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      答题时间 (秒)
                    </label>
                    <input
                      type="number"
                      min="60"
                      max="7200"
                      value={interviewConfig.answeringTime}
                      onChange={(e) => handleInterviewConfigChange('answeringTime', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">每道题的答题时间 (60-7200 秒)</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      题目难度
                    </label>
                    <select
                      value={interviewConfig.difficulty}
                      onChange={(e) => handleInterviewConfigChange('difficulty', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="easy">简单</option>
                      <option value="medium">中等</option>
                      <option value="hard">困难</option>
                    </select>
                    <p className="text-xs text-gray-500 mt-1">设置题目的难度等级</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      题目长度
                    </label>
                    <select
                      value={interviewConfig.questionLength}
                      onChange={(e) => handleInterviewConfigChange('questionLength', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="short">短</option>
                      <option value="medium">中等</option>
                      <option value="long">长</option>
                    </select>
                    <p className="text-xs text-gray-500 mt-1">设置题目的长度</p>
                  </div>
                </div>
              </div>
            )}

            {/* Model Configuration Tab */}
            {activeTab === 'model' && (
              <div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      API Token
                    </label>
                    <input
                      type="password"
                      value={modelConfig.apiToken}
                      onChange={(e) => handleModelConfigChange('apiToken', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="输入您的 API Token"
                    />
                    <p className="text-xs text-gray-500 mt-1">请输入用于访问大模型 API 的令牌</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      大模型选择
                    </label>
                    <select
                      value={modelConfig.model}
                      onChange={(e) => handleModelConfigChange('model', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      disabled // Currently only supporting DeepSeek
                    >
                      <option value="deepseek">DeepSeek</option>
                    </select>
                    <p className="text-xs text-gray-500 mt-1">目前仅支持 DeepSeek 模型</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="flex justify-end space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md transition duration-300"
            >
              取消
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-md transition duration-300"
            >
              保存配置
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfigPage;