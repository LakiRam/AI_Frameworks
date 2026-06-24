const openaiProvider = require('./openai');
const azureOpenAIProvider = require('./azure-openai');
const anthropicProvider = require('./anthropic');
const geminiProvider = require('./gemini');
const { SUPPORTED_PROVIDERS, buildUserPrompt } = require('./common');

const providerMap = {
  openai: openaiProvider,
  'azure-openai': azureOpenAIProvider,
  anthropic: anthropicProvider,
  gemini: geminiProvider
};

const getProvider = (providerId) => {
  const provider = providerMap[providerId];

  if (!provider) {
    const error = new Error(`Unsupported LLM provider: ${providerId}`);
    error.statusCode = 400;
    throw error;
  }

  return provider;
};

const generateRecommendations = async ({ llmProvider, llmConfig, domain, scenario, context, domainMetadata }) => {
  const provider = getProvider(llmProvider);

  return provider({
    llmConfig,
    userPrompt: buildUserPrompt({
      domain,
      scenario,
      context,
      domainMetadata
    })
  });
};

module.exports = {
  SUPPORTED_PROVIDERS,
  getProvider,
  generateRecommendations
};
