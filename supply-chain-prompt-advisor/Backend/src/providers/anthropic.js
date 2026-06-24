const Anthropic = require('@anthropic-ai/sdk');
const { SYSTEM_PROMPT, parseRecommendations } = require('./common');

module.exports = async ({ userPrompt, llmConfig }) => {
  const client = new Anthropic({
    apiKey: llmConfig.apiKey
  });

  const response = await client.messages.create({
    model: llmConfig.model || 'claude-3-5-sonnet-latest',
    max_tokens: 1200,
    temperature: 0.7,
    system: SYSTEM_PROMPT,
    messages: [
      {
        role: 'user',
        content: userPrompt
      }
    ]
  });

  const content = Array.isArray(response?.content)
    ? response.content
        .filter((block) => block.type === 'text')
        .map((block) => block.text)
        .join('')
    : '';

  return parseRecommendations(content);
};
