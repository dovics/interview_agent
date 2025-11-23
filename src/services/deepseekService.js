// src/services/deepseekService.js
import { ChatOpenAI } from "@langchain/openai";

/**
 * Service to interact with DeepSeek models via LangChain
 */

/**
 * Get API token from localStorage
 * @returns {string|null} - The API token or null if not found
 */
export const getApiToken = () => {
  const savedModelConfig = localStorage.getItem('modelConfig');
  if (savedModelConfig) {
    try {
      const modelConfig = JSON.parse(savedModelConfig);
      return modelConfig.apiToken || null;
    } catch (error) {
      console.error("Error parsing model config:", error);
      return null;
    }
  }
  return null;
};

// Initialize DeepSeek model
// Note: DeepSeek provides OpenAI-compatible API
const initializeDeepSeekModel = (token) => {
  // In a real implementation, you would get the API key from environment variables
  // const apiKey = process.env.REACT_APP_DEEPSEEK_API_KEY;
  
  // For demo purposes, we're initializing without actual API key
  // In production, uncomment the apiKey line and provide your key
  const model = new ChatOpenAI({
    modelName: "deepseek-chat",
    // openAIApiKey: token || "dummy-key", // Replace with process.env.REACT_APP_DEEPSEEK_API_KEY
    configuration: {
      baseURL: "https://api.deepseek.com/v1",
      apiKey: token,
    },
    temperature: 0.7,
  });

  return model;
};

/**
 * Generate a single interview question using DeepSeek model
 * @param {number} questionCount - The number of questions to generate
 * @returns {Promise<Array>} - Generated questions array
 */
export const generateInterviewQuestions = async (questionCount) => {
  try {
    // In a real implementation, we would actually call the model
    const token = getApiToken();
    const model = initializeDeepSeekModel(token);
    
    const prompt = `# Role
    你是一位中国公务员结构化面试的命题专家，熟悉国考、省考及事业单位面试的题型规律。你擅长设计考察考生综合素质、应变能力和政治素养的高质量面试题。

    # Task
    请根据用户指定的【题型】、【难度】和【数量】，生成相应数量的面试题目。
    用户指定了需要生成 ${questionCount} 道题目。

    # Question Types Definition (题型定义)
    1. **综合分析**: 考察社会现象、政策理解、名言警句等。要求题目具有辩证性，能引发深层思考。
    2. **计划组织**: 考察活动策划、调研、会议组织等。要求场景具体，有明确的任务目标和限制条件。
    3. **人际关系**: 考察与领导、同事、群众的沟通协调。要求设定具体的矛盾冲突点（如误解、利益冲突）。
    4. **应急应变**: 考察突发事件处理。要求情境紧迫，压力感强（如群众闹事、设备故障、时间冲突）。
    5. **岗位匹配**: 考察求职动机、职业规划与岗位认知的匹配度。

    # Constraints
    1. **真实感**: 题目必须贴近实际公务员工作场景，避免过于科幻或脱离实际。
    2. **多样性**: 如果生成多道题，请确保题材不重复（例如不要两道题都是关于环保的）。
    3. **JSON格式**: 必须严格输出标准的 JSON 格式，不要包含 Markdown 标记。
    4. **数量要求**: 必须生成 exactly ${questionCount} 道题目，不多不少。

    # Output JSON Structure
    [
      {
        "id": 1, // 序号
        "type": "综合分析", // 题型
        "text": "题目具体内容...", // 题目文本，长度适中（20-50字）
        "analysis_points": ["点1", "点2"] // (可选) 给后端的简单提示，用于辅助评分（不展示给考生）
      }
    ]`;
    
    const response = await model.invoke(prompt);
    
    // Try to parse the response content as JSON
    try {
      const jsonResponse = JSON.parse(response.content);
      return jsonResponse;
    } catch (parseError) {
      console.warn("Failed to parse response as JSON, returning raw content:", response.content);
      // If parsing fails, return the raw content in the same structure
      return response.content;
    }
  } catch (error) {
    console.error("Error generating question:", error);
    throw error;
  }
};