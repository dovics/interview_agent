import React, { useState, useRef, useEffect } from 'react';

const InterviewPage = ({ mode, config, draftNotes, questions, onBack, onFinishInterview }) => {
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [countdown, setCountdown] = useState(config.answeringTime);
  const [isWarning, setIsWarning] = useState(false);
  const [isFlashing, setIsFlashing] = useState(false);
  const [recordingStopped, setRecordingStopped] = useState(false); // 新增状态，跟踪录音是否已停止
  const intervalRef = useRef(null);
  const flashTimeoutRef = useRef(null);

  // 自动开始录音
  useEffect(() => {
    startRecording();
  }, []);

  // Countdown effect
  useEffect(() => {
    intervalRef.current = setInterval(() => {
      setCountdown(prev => {
        // Check if we're entering the last minute
        if (prev === 60 && !isWarning) {
          setIsWarning(true);
          startFlashing();
        }

        // If countdown finishes, finish interview
        if (prev <= 1) {
          clearInterval(intervalRef.current);
          if (flashTimeoutRef.current) {
            clearTimeout(flashTimeoutRef.current);
          }
          handleFinishInterview();
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
  }, [isWarning, questions]);

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

  const startRecording = async () => {
    // 如果是全真模式并且已经停止过录音，则不允许重新开始
    if (mode === 'real' && recordingStopped) {
      alert('全真模拟模式下，录音已停止，不允许重新开始录音');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          setRecordedChunks(prev => [...prev, event.data]);
        }
      };
      recorder.start();
      setMediaRecorder(recorder);
      setRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('无法访问麦克风，请检查权限设置');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
      setRecording(false);
      setRecordingStopped(true); // 标记录音已停止
    }
  };

  const handleFinishInterview = () => {
    if (recording) {
      stopRecording();
    }
    
    // Create blob from recorded chunks
    if (recordedChunks.length > 0) {
      const blob = new Blob(recordedChunks, { type: 'audio/webm' });
      // In a real app, you would upload the blob to a server here
      console.log('Recorded audio blob:', blob);
      // Upload logic would go here
    }
    
    if (onFinishInterview) {
      onFinishInterview();
    }
  };


  return (
    <div className={`max-w-4xl w-full bg-white rounded-2xl shadow-xl overflow-hidden ${isFlashing ? 'bg-red-500 bg-opacity-30' : ''}`}>
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 py-6 px-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white">结构化面试答题</h1>
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
        {mode !== 'real' && (
          <div className={`mb-6 p-4 rounded-lg text-center ${isWarning ? 'bg-yellow-100 border border-yellow-300' : 'bg-blue-50'}`}>
            <p className="text-gray-600 mb-2">答题时间倒计时</p>
            <p className={`text-3xl font-bold ${isWarning ? 'text-yellow-600 font-extrabold' : 'text-blue-700'}`}>
              {formatTime(countdown)}
            </p>
          </div>
        )}

        {/* All Questions */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">所有面试题目</h2>
          <div className="space-y-4">
            {questions.map((question, index) => (
              <div 
                key={question.id} 
                className="bg-gray-50 p-6 rounded-lg border border-gray-200"
              >
                <div className="flex items-start">
                  <span className="flex-shrink-0 flex items-center justify-center h-8 w-8 rounded-full bg-blue-500 text-white font-medium mr-3">
                    {index + 1}
                  </span>
                  <p className="text-gray-700">{question.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Draft Notes Section (Read-only) */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">草稿区</h2>
          <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
            <div className="w-full h-40 p-3 border border-yellow-300 rounded-md bg-gray-50 overflow-y-auto">
              {draftNotes || <span className="text-gray-400">无草稿内容</span>}
            </div>
            <p className="text-sm text-yellow-700 mt-2">
              这是在准备阶段编写的草稿内容，仅用于参考。
            </p>
          </div>
        </div>

        {/* Recording Controls */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">语音回答</h2>
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <div className="flex flex-col items-center">
              <div className="flex space-x-4 mb-4">
                {/* 在全真模式下，如果录音已经停止则不显示开始录音按钮 */}
                {mode === 'real' && recordingStopped ? (
                  <div className="text-red-600 font-medium">
                    全真模拟模式下，录音已停止，不允许重新开始录音
                  </div>
                ) : !recording ? (
                  <button
                    onClick={startRecording}
                    className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium flex items-center"
                  >
                    <span className="w-3 h-3 bg-white rounded-full mr-2"></span>
                    开始录音
                  </button>
                ) : (
                  <button
                    onClick={stopRecording}
                    className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium flex items-center"
                  >
                    <span className="w-3 h-3 bg-white mr-2"></span>
                    停止录音
                  </button>
                )}
                
                {recording && (
                  <div className="flex items-center text-red-600">
                    <span className="flex h-3 w-3 relative mr-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                    </span>
                    录音中...
                  </div>
                )}
              </div>
              
              {recordedChunks.length > 0 && !recording && (
                <div className="mt-2 text-green-600">
                  已录制 {Math.round(recordedChunks.reduce((acc, chunk) => acc + chunk.size, 0) / 1024)} KB 音频数据
                </div>
              )}
            </div>
            
            <p className="text-sm text-blue-700 mt-2">
              {mode === 'real' 
                ? '全真模拟模式：进入页面后自动开始录音，录音停止后不能重新开始' 
                : '点击"开始录音"按钮开始录制您的回答，回答完毕后点击"停止录音"。'}
            </p>
          </div>
        </div>

        {/* Finish Button */}
        <div className="flex justify-center">
          <button
            onClick={handleFinishInterview}
            className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
          >
            结束答题并上传
          </button>
        </div>
      </div>
    </div>
  );
};

export default InterviewPage;