const SYSTEM_PROMPT = 'You are an expert supply chain consultant and prompt engineering specialist. Generate exactly 3 high-quality prompts for the given supply chain scenario. Each prompt should be actionable, specific, and optimized for AI systems. Return ONLY valid JSON in this exact format: { "recommendations": [ { "rank": 1, "prompt": "...", "explanation": "...", "useCase": "..." }, ... ] }';

const SUPPORTED_PROVIDERS = [
  {
    id: 'openai',
    name: 'OpenAI',
    requiresEndpoint: false,
    defaultModel: 'gpt-4o-mini',
    description: 'OpenAI Chat Completions API for prompt recommendation generation.'
  },
  {
    id: 'azure-openai',
    name: 'Azure OpenAI',
    requiresEndpoint: true,
    defaultModel: 'gpt-4o',
    description: 'Azure-hosted OpenAI deployment for enterprise-grade prompt recommendations.'
  },
  {
    id: 'anthropic',
    name: 'Anthropic',
    requiresEndpoint: false,
    defaultModel: 'claude-3-5-sonnet-latest',
    description: 'Anthropic Claude models for structured supply chain recommendations.'
  },
  {
    id: 'gemini',
    name: 'Google Gemini',
    requiresEndpoint: false,
    defaultModel: 'gemini-1.5-pro',
    description: 'Google Gemini models for generating prompt recommendations.'
  }
];

const buildUserPrompt = ({ domain, scenario, context, domainMetadata }) => {
  const exampleScenarios = domainMetadata?.exampleScenarios?.join('; ') || 'N/A';
  const keywords = domainMetadata?.keywords?.join(', ') || 'N/A';

  return [
    `Supply chain domain: ${domain}`,
    `Domain description: ${domainMetadata?.description || 'N/A'}`,
    `Example scenarios: ${exampleScenarios}`,
    `Domain keywords: ${keywords}`,
    `User scenario: ${scenario}`,
    `Additional context: ${context || 'None provided.'}`,
    'Generate exactly 3 ranked recommendations tailored to this scenario.'
  ].join('\n');
};

const extractJsonString = (text) => {
  if (!text || typeof text !== 'string') {
    throw new Error('LLM response did not include any text content.');
  }

  const fencedMatch = text.match(/```(?:json)?\s*([\s\S]*?)```/i);

  if (fencedMatch?.[1]) {
    return fencedMatch[1].trim();
  }

  const firstBrace = text.indexOf('{');
  const lastBrace = text.lastIndexOf('}');

  if (firstBrace === -1 || lastBrace === -1 || lastBrace <= firstBrace) {
    throw new Error('LLM response did not contain valid JSON.');
  }

  return text.slice(firstBrace, lastBrace + 1).trim();
};

const normalizeRecommendations = (payload) => {
  if (!payload || !Array.isArray(payload.recommendations)) {
    throw new Error('LLM response JSON is missing the recommendations array.');
  }

  if (payload.recommendations.length < 3) {
    throw new Error('LLM response did not return exactly 3 recommendations.');
  }

  return payload.recommendations.slice(0, 3).map((item, index) => ({
    rank: index + 1,
    prompt: item?.prompt || '',
    explanation: item?.explanation || '',
    useCase: item?.useCase || ''
  }));
};

const parseRecommendations = (text) => {
  let parsed;

  try {
    parsed = JSON.parse(extractJsonString(text));
  } catch (error) {
    throw new Error(`Unable to parse LLM response JSON: ${error.message}`);
  }

  return normalizeRecommendations(parsed);
};

module.exports = {
  SYSTEM_PROMPT,
  SUPPORTED_PROVIDERS,
  buildUserPrompt,
  parseRecommendations
};
