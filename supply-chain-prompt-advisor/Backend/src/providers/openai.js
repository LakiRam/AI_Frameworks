const { OpenAI } = require('openai');
const { SYSTEM_PROMPT, parseRecommendations } = require('./common');

module.exports = async ({ userPrompt, llmConfig }) => {
  const client = new OpenAI({
    apiKey: llmConfig.apiKey
  });

  const response = await client.chat.completions.create({
    model: llmConfig.model || 'gpt-4o-mini',
    temperature: 0.7,
    response_format: { type: 'json_object' },
    messages: [
      {
        role: 'system',
        content: SYSTEM_PROMPT
      },
      {
        role: 'user',
        content: userPrompt
      }
    ]
  });

  const content = response?.choices?.[0]?.message?.content;
  return parseRecommendations(content);
};
