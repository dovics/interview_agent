/**
 * Internationalization utility for the interview assistant application
 */

// Define translations for both Chinese and English
const translations = {
  en: {
    interviewAssistant: "Interview Assistant",
    chooseFile: "Please choose a file",
    uploadResume: "Upload Resume",
    uploading: "Uploading...",
    uploadFailed: "Upload failed. Please try again.",
    networkError: "Network error. Please check your connection.",
    selectedFile: "Selected file:",
    back: "Back",
    typeAnswer: "Type your answer...",
    send: "Send",
    typing: "Typing...",
    fetchQuestionFailed: "Failed to fetch question",
    loading: "Loading...",
    adaptiveQuestioning: "Enable Adaptive Questioning"
  },
  zh: {
    interviewAssistant: "面试助手",
    chooseFile: "请选择文件",
    uploadResume: "上传简历",
    uploading: "上传中...",
    uploadFailed: "上传失败，请重试。",
    networkError: "网络错误，请检查您的连接。",
    selectedFile: "已选择文件:",
    back: "返回",
    typeAnswer: "请输入您的回答...",
    send: "发送",
    typing: "正在输入...",
    fetchQuestionFailed: "获取问题失败",
    loading: "加载中...",
    adaptiveQuestioning: "开启自适应问题"
  }
};

/**
 * Get translations for the specified language
 * @param {string} language - The language code ('en' or 'zh')
 * @returns {Object} - The translations object for the specified language
 */
export const getTranslations = (language) => {
  return translations[language] || translations.en;
};