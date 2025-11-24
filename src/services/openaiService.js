// src/services/openaiService.js
import { ChatOpenAI } from "@langchain/openai";

/**
 * Service to interact with OpenAI compatible models via LangChain
 */

/**
 * Get API token from localStorage
 * @returns {string|null} - The API token or null if not found
 */
export const getModelConfig = () => {
  const savedModelConfig = localStorage.getItem('modelConfig');
  if (savedModelConfig) {
    try {
      const modelConfig = JSON.parse(savedModelConfig);
      return modelConfig
    } catch (error) {
      console.error("Error parsing model config:", error);
      return null;
    }
  }
  return null;
};

// Initialize OpenAI compatible model
// Note: Supports various OpenAI-compatible APIs including DeepSeek
const initializeOpenAIModel = () => {
  // In a real implementation, you would get the API key from environment variables
  // const apiKey = process.env.REACT_APP_DEEPSEEK_API_KEY;
  const config = getModelConfig();
  // For demo purposes, we're initializing without actual API key
  // In production, uncomment the apiKey line and provide your key
  const model = new ChatOpenAI({
    modelName: config.modelName,
    // openAIApiKey: token || "dummy-key", // Replace with process.env.REACT_APP_DEEPSEEK_API_KEY
    configuration: {
      baseURL: config.baseURL,
      apiKey: config.apiToken,
    },
    temperature: 0.7,
  });

  return model;
};

/**
 * Generate a single interview question using OpenAI compatible model
 * @param {number} questionCount - The number of questions to generate
 * @param {Object} options - Additional options for question generation
 * @param {string} options.difficulty - Difficulty level (easy, medium, hard)
 * @param {string} options.questionLength - Length of questions (short, medium, long)
 * @returns {Promise<Array>} - Generated questions array
 */
export const generateInterviewQuestions = async (questionCount, options = {}) => {
  try {
    const model = initializeOpenAIModel();
    
    // Extract options with defaults
    const { difficulty = 'medium', questionLength = 'medium' } = options;
    
    // Map difficulty levels to descriptive text
    const difficultyMap = {
      easy: '较为简单，适合初学者',
      medium: '中等难度，有一定挑战性',
      hard: '较难，需要深入思考和丰富经验'
    };
    
    // Map question length to descriptive text
    const lengthMap = {
      short: '简短精练（约20-30字）',
      medium: '中等长度（约30-50字）',
      long: '较长详细（约50-80字）'
    };
    
    const prompt = `# Role
    你是一位中国公务员结构化面试的命题专家，熟悉国考、省考及事业单位面试的题型规律。你擅长设计考察考生综合素质、应变能力和政治素养的高质量面试题。

    # Task
    请根据用户指定的【题型】、【难度】和【数量】，生成相应数量的面试题目。
    用户指定了需要生成 ${questionCount} 道题目。
    题目难度: ${difficulty} - ${difficultyMap[difficulty]}
    题目长度: ${questionLength} - ${lengthMap[questionLength]}

    # Question Types Definition (题型定义)
    1. **综合分析**: 考察社会现象、政策理解、名言警句等。要求题目具有辩证性，能引发深层思考。
    2. **计划组织**: 考察活动策划、调研、会议组织等。要求场景具体，有明确的任务目标和限制条件。
    3. **人际关系**: 考察与领导、同事、群众的沟通协调。要求设定具体的矛盾冲突点（如误解、利益冲突）。
    4. **应急应变**: 考察突发事件处理。要求情境紧迫，压力感强（如群众闹事、设备故障、时间冲突）。
    5. **岗位匹配**: 考察求职动机、职业规划与岗位认知的匹配度。

    # Constraints
    1. **真实感**: 题目必须贴近实际公务员工作场景，避免过于科幻或脱离实际。
    2. **多样性**: 如果生成多道题，请确保题材不重复（例如不要两道题都是关于环保的）。
    3. **JSON Format**: 必须严格输出标准的 JSON 格式，不要包含 Markdown 标记。
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

/**
 * Evaluate candidate answers using OpenAI compatible model with overall scoring
 * @param {Array} questions - Array of questions with their details
 * @param {String} answer - Array of candidate answers
 * @returns {Promise<Object>} - Overall evaluation result
 */
export const evaluateCandidateAnswers = async (questions, answer) => {
  try {
    const model = initializeOpenAIModel();
    
    const prompt = `# Role
    你是一位专业的公务员面试考官，具有丰富的面试评分经验。你的任务是对考生的所有面试回答进行整体专业评分和详细点评。

    # Scoring Criteria (评分标准)
    1. **观点明确** (20分): 回答是否有明确的观点和立场
    2. **逻辑清晰** (20分): 回答是否条理清晰，逻辑性强
    3. **内容充实** (20分): 是否有充分的事实、例子或理论支撑
    4. **政策理解** (20分): 对相关政策的理解和应用能力
    5. **语言表达** (20分): 语言是否流畅、准确、得体

    # Input Data
    请根据以下题目和考生回答进行整体评分：
    
    ${questions.map((q, i) => `
    题目${i+1} (${q.type}题):
    ${q.text}
    
    考生回答:
    ${answer}`)}

    # Constraints
    1. **JSON Format**: 必须严格输出标准的 JSON 格式，不要包含 Markdown 标记。

    # Output JSON Structure

    {
      "overallScore": 85, // 总分 (0-100)
      "feedback": "整体表现良好，观点明确，逻辑清晰。但在政策理解方面还可以进一步加强...",
      "strengths": ["观点明确", "逻辑性强"], // 优点列表
      "improvements": ["加强政策理解", "增加实例支撑"], // 改进建议
      "questionEvaluations": [  // 各题简要评价
        {
          "questionId": 1,
          "score": 80,
          "briefFeedback": "回答较为全面，但可以增加一些实际案例..."
        }
      ]
    }`;
    
    const response = await model.invoke(prompt);
    
    // Try to parse the response content as JSON
    try {
      const jsonResponse = JSON.parse(response.content);
      return jsonResponse;
    } catch (parseError) {
      console.warn("Failed to parse evaluation response as JSON:", response.content);
      throw new Error("评分结果格式错误");
    }
  } catch (error) {
    console.error("Error evaluating answers:", error);
    throw error;
  }
};