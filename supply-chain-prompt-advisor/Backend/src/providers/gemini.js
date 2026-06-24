const { GoogleGenerativeAI } = require('@google/generative-ai');
const { SYSTEM_PROMPT, parseRecommendations } = require('./common');

module.exports = async ({ userPrompt, llmConfig }) => {
  const client = new GoogleGenerativeAI(llmConfig.apiKey);
  const model = client.getGenerativeModel({
    model: llmConfig.model || 'gemini-1.5-pro'
  });

  const result = await model.generateContent(`${SYSTEM_PROMPT}\n\n${userPrompt}`);
  const response = await result.response;
  const content = response.text();

  return parseRecommendations(content);
};
