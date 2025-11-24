import React from 'react';

const ShareModal = ({ isOpen, onClose, screenshot }) => {
  if (!isOpen) return null;

  const handleDownload = () => {
    if (!screenshot) return;
    
    const link = document.createElement('a');
    link.download = 'interview-result.png';
    link.href = screenshot;
    link.click();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-800">分享面试结果</h2>
            <button 
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          
          <div className="flex justify-center mb-6">
            <img 
              src={screenshot} 
              alt="面试结果截图" 
              className="max-w-full h-auto rounded-lg shadow-lg max-h-96 w-auto"
            />
          </div>
          
          <div className="flex justify-center space-x-4">
            <button
              onClick={handleDownload}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
            >
              下载图片
            </button>
            <button
              onClick={onClose}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShareModal;