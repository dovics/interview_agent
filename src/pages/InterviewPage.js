import React, { useState, useRef, useEffect } from 'react';

const InterviewPage = ({ mode, config, draftNotes, questions, onBack, onFinishInterview }) => {
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [countdown, setCountdown] = useState(config.answeringTime);
  const [isWarning, setIsWarning] = useState(false);
  const [isFlashing, setIsFlashing] = useState(false);
  const [speechError, setSpeechError] = useState(null);
  const [micPermissionRequested, setMicPermissionRequested] = useState(false); // New state to track mic permission
  const recognitionRef = useRef(null);
  const intervalRef = useRef(null);
  const flashTimeoutRef = useRef(null);

  // Request microphone permission on component mount
  useEffect(() => {
    requestMicrophonePermission();
  }, []);

  // Auto start speech recognition after mic permission is granted
  useEffect(() => {
    if (micPermissionRequested) {
      startSpeechRecognition();
    }
  }, [micPermissionRequested]);

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

  const requestMicrophonePermission = async () => {
    try {
      // First check if mediaDevices API is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('浏览器不支持麦克风访问功能，请使用最新版Chrome、Edge或Firefox浏览器');
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // Stop all tracks to release the microphone after getting permission
      stream.getTracks().forEach(track => track.stop());
      setMicPermissionRequested(true);
      setSpeechError(null); // Clear any previous errors
    } catch (error) {
      console.error('Error accessing microphone:', error);
      
      let errorMessage = '无法访问麦克风，请检查权限设置';
      
      // Handle specific error types
      if (error.name === 'NotFoundError' || error.name === 'OverconstrainedError') {
        errorMessage = '未找到可用的麦克风设备，请检查设备连接或系统设置';
      } else if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        errorMessage = '麦克风权限被拒绝，请确保已授予麦克风权限并刷新页面重试';
      } else if (error.name === 'NotReadableError') {
        errorMessage = '麦克风设备正被其他应用占用，请关闭其他应用后重试';
      } else if (error.name === 'AbortError') {
        errorMessage = '设备访问被中断，请重试';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setSpeechError(errorMessage);
    }
  };

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

  const startSpeechRecognition = () => {
    // 如果是全真模式并且已经停止过语音识别，则不允许重新开始
    if (mode === 'real' && !recognitionRef.current) {
      setSpeechError('全真模拟模式下，语音识别已停止，不允许重新开始');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setSpeechError('您的浏览器不支持语音识别功能，请使用Chrome或Edge浏览器');
      return;
    }
    console.log('SpeechRecognition', SpeechRecognition);
    // 如果已有识别器实例，先清理掉
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'zh-CN';

    recognition.onresult = (event) => {
      setSpeechError(null); // 清除之前的错误
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcript;
        } else {
          interim += transcript;
        }
      }

      if (final) {
        setTranscript(prev => prev + final);
      }
      
      setInterimTranscript(interim);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error', event.error);
      setSpeechError(`语音识别发生错误: ${event.error}`);
      
      // 特别处理not-allowed错误
      if (event.error === 'not-allowed') {
        setSpeechError('语音识别权限被拒绝，请确保已授予麦克风权限并刷新页面重试');
      } else if (event.error === 'no-speech') {
        // Continue listening
        try {
          recognition.start();
        } catch (err) {
          console.error('Failed to restart recognition', err);
        }
      }
    };

    recognition.onend = () => {
      if (recording) {
        // If recording is still active, restart recognition
        try {
          recognition.start();
        } catch (err) {
          console.error('Failed to restart recognition', err);
          setSpeechError('语音识别意外停止，请尝试重新开始');
        }
      }
    };

    try {
      recognition.start();
      recognitionRef.current = recognition;
      setRecording(true);
      setSpeechError(null); // 清除之前的错误
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      if (error.name === 'NotAllowedError') {
        setSpeechError('语音识别权限被拒绝，请确保已授予麦克风权限并刷新页面重试');
      } else {
        setSpeechError('无法启动语音识别，请检查麦克风权限设置');
      }
    }
  };

  const stopSpeechRecognition = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setRecording(false);
    }
  };

  const handleFinishInterview = () => {
    if (recording) {
      stopSpeechRecognition();
    }
    
    // In a real app, you would upload the transcript to a server here
    console.log('Interview transcript:', transcript);
    // Upload logic would go here
    
    if (onFinishInterview) {
      onFinishInterview(transcript);
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

        {/* Speech Recognition Controls */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">语音回答</h2>
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <div className="flex flex-col items-center">
              <div className="flex space-x-4 mb-4">
                {/* 在全真模式下，如果语音识别已经停止则不显示开始按钮 */}
                {mode === 'real' && !recognitionRef.current ? (
                  <div className="text-red-600 font-medium">
                    全真模拟模式下，语音识别已停止，不允许重新开始
                  </div>
                ) : !micPermissionRequested && !speechError ? (
                  <div className="text-blue-600 font-medium">
                    正在请求麦克风权限...
                  </div>
                ) : !recording && !speechError ? (
                  <button
                    onClick={startSpeechRecognition}
                    className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium flex items-center"
                  >
                    <span className="w-3 h-3 bg-white rounded-full mr-2"></span>
                    开始语音识别
                  </button>
                ) : recording ? (
                  <button
                    onClick={stopSpeechRecognition}
                    className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium flex items-center"
                  >
                    <span className="w-3 h-3 bg-white mr-2"></span>
                    停止语音识别
                  </button>
                ) : null}
                
                {recording && (
                  <div className="flex items-center text-red-600">
                    <span className="flex h-3 w-3 relative mr-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                    </span>
                    语音识别中...
                  </div>
                )}
              </div>
              
              {/* 错误信息显示 */}
              {speechError && (
                <div className="w-full mb-4 p-3 bg-red-100 border border-red-300 rounded text-red-700">
                  {speechError}
                  <div className="mt-2 text-sm">
                    <p>请尝试以下解决方案:</p>
                    <ul className="list-disc pl-5 mt-1">
                      <li>检查麦克风是否正确连接</li>
                      <li>确认浏览器有麦克风访问权限</li>
                      <li>检查系统设置中是否禁用了麦克风</li>
                      <li>尝试刷新页面或重启浏览器</li>
                    </ul>
                  </div>
                </div>
              )}
              
              {/* Transcript display */}
              <div className="w-full mb-4">
                <div className="bg-white p-4 rounded border border-gray-300 min-h-[100px] max-h-[200px] overflow-y-auto">
                  <p className="text-gray-800">{transcript}</p>
                  {interimTranscript && (
                    <p className="text-gray-500 italic">{interimTranscript}</p>
                  )}
                  {!transcript && !interimTranscript && !speechError && (
                    <p className="text-gray-400">语音识别内容将在此显示...</p>
                  )}
                </div>
              </div>
            </div>
            
            <p className="text-sm text-blue-700 mt-2">
              {mode === 'real' 
                ? '全真模拟模式：进入页面后自动开始语音识别，停止后不能重新开始' 
                : '点击"开始语音识别"按钮开始语音识别，回答完毕后点击"停止语音识别"。'}
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