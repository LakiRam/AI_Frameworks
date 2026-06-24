const PROVIDER_DEFAULTS = {
  openai: {
    model: 'gpt-4o',
    apiKeyLabel: 'OpenAI API Key',
    endpointLabel: null,
  },
  'azure-openai': {
    model: 'gpt-4o',
    apiKeyLabel: 'Azure OpenAI API Key',
    endpointLabel: 'Azure OpenAI Endpoint',
  },
  anthropic: {
    model: 'claude-3-5-sonnet-20241022',
    apiKeyLabel: 'Anthropic API Key',
    endpointLabel: null,
  },
  gemini: {
    model: 'gemini-1.5-pro',
    apiKeyLabel: 'Gemini API Key',
    endpointLabel: null,
  },
};

export const FALLBACK_PROVIDERS = [
  {
    id: 'openai',
    name: 'OpenAI',
    requiresEndpoint: false,
    defaultModel: 'gpt-4o',
    description: 'Balanced performance for scenario framing and prompt drafting.',
  },
  {
    id: 'azure-openai',
    name: 'Azure OpenAI',
    requiresEndpoint: true,
    defaultModel: 'gpt-4o',
    description: 'Enterprise-grade hosting for regulated supply chain environments.',
  },
  {
    id: 'anthropic',
    name: 'Anthropic',
    requiresEndpoint: false,
    defaultModel: 'claude-3-5-sonnet-20241022',
    description: 'Strong at nuanced reasoning for multi-step planning prompts.',
  },
  {
    id: 'gemini',
    name: 'Gemini',
    requiresEndpoint: false,
    defaultModel: 'gemini-1.5-pro',
    description: 'Useful for broad contextual analysis across operational signals.',
  },
];

export function getProviderDefaults(providerId) {
  return PROVIDER_DEFAULTS[providerId] ?? PROVIDER_DEFAULTS.openai;
}

export default function LLMConfig({ provider, config, onChange, errors }) {
  const defaults = getProviderDefaults(provider?.id);
  const requiresEndpoint = provider?.requiresEndpoint ?? false;
  const modelPlaceholder = provider?.defaultModel || defaults.model;

  return (
    <div className="config-card">
      <div className="section-heading compact">
        <div>
          <p className="eyebrow">Provider configuration</p>
          <h3>{provider?.name ?? 'LLM settings'}</h3>
        </div>
      </div>
      <p className="field-help provider-description">
        {provider?.description ?? 'Enter credentials for this request only. Nothing is stored after submission.'}
      </p>
      <div className="field-group">
        <label htmlFor="apiKey">{defaults.apiKeyLabel}</label>
        <input
          id="apiKey"
          type="password"
          value={config.apiKey}
          onChange={(event) => onChange('apiKey', event.target.value)}
          placeholder="Paste API key"
        />
        {errors.apiKey ? <span className="field-error">{errors.apiKey}</span> : null}
      </div>

      {requiresEndpoint ? (
        <div className="field-group">
          <label htmlFor="endpoint">{defaults.endpointLabel}</label>
          <input
            id="endpoint"
            type="url"
            value={config.endpoint}
            onChange={(event) => onChange('endpoint', event.target.value)}
            placeholder="https://your-resource.openai.azure.com"
          />
          {errors.endpoint ? <span className="field-error">{errors.endpoint}</span> : null}
        </div>
      ) : null}

      <div className="field-group">
        <label htmlFor="model">Model (optional)</label>
        <input
          id="model"
          type="text"
          value={config.model}
          onChange={(event) => onChange('model', event.target.value)}
          placeholder={modelPlaceholder}
        />
        <span className="field-help">Leave blank to use {modelPlaceholder}.</span>
      </div>
    </div>
  );
}
