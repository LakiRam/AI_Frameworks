const { OpenAIClient, AzureKeyCredential } = require('@azure/openai');
const { SYSTEM_PROMPT, parseRecommendations } = require('./common');

module.exports = async ({ userPrompt, llmConfig }) => {
  if (!llmConfig.endpoint) {
    throw new Error('Azure OpenAI requires an endpoint in llmConfig.endpoint.');
  }

  const client = new OpenAIClient(llmConfig.endpoint, new AzureKeyCredential(llmConfig.apiKey));
  const deploymentName = llmConfig.model || 'gpt-4o';

  const response = await client.getChatCompletions(deploymentName, [
    {
      role: 'system',
      content: SYSTEM_PROMPT
    },
    {
      role: 'user',
      content: userPrompt
    }
  ], {
    temperature: 0.7
  });

  const content = response?.choices?.[0]?.message?.content;
  return parseRecommendations(content);
};
