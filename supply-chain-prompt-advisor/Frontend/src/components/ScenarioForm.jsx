import { useEffect, useMemo, useState } from 'react';
import LLMConfig, { FALLBACK_PROVIDERS, getProviderDefaults } from './LLMConfig';

const DOMAIN_OPTIONS = [
  {
    value: 'procurement',
    label: 'Procurement & Sourcing',
    icon: '📦',
    accentClass: 'domain-procurement',
    placeholder:
      'Example: We need to evaluate suppliers for a direct materials RFQ while balancing cost, delivery lead times, and sustainability goals across two regions.',
  },
  {
    value: 'inventory',
    label: 'Inventory & Warehouse',
    icon: '🏭',
    accentClass: 'domain-inventory',
    placeholder:
      'Example: Our regional DC is overstocked on slow movers while priority SKUs are frequently out of stock. Recommend prompts for rebalancing inventory and warehouse capacity.',
  },
  {
    value: 'demand-forecasting',
    label: 'Demand Forecasting',
    icon: '📈',
    accentClass: 'domain-demand',
    placeholder:
      'Example: A seasonal promotion and competitor launch are impacting weekly demand signals. Recommend prompts to improve forecast assumptions and scenario planning.',
  },
  {
    value: 'logistics',
    label: 'Logistics & Transportation',
    icon: '🚚',
    accentClass: 'domain-logistics',
    placeholder:
      'Example: Port delays and rising spot freight costs are threatening service levels. Recommend prompts for rerouting, mode selection, and ETA risk analysis.',
  },
  {
    value: 'supplier-risk',
    label: 'Supplier Risk & Compliance',
    icon: '🛡️',
    accentClass: 'domain-risk',
    placeholder:
      'Example: A tier-2 supplier in a high-risk region may disrupt critical parts supply. Recommend prompts for mitigation planning, alternate sourcing, and compliance review.',
  },
];

const MIN_SCENARIO_LENGTH = 20;

function normalizeProvider(provider) {
  const defaults = getProviderDefaults(provider.id);

  return {
    ...provider,
    defaultModel: provider.defaultModel || defaults.model,
    requiresEndpoint: Boolean(provider.requiresEndpoint),
  };
}

export default function ScenarioForm({ providers, onSubmit, loading }) {
  const availableProviders = useMemo(() => {
    const source = providers?.length ? providers : FALLBACK_PROVIDERS;
    return source.map(normalizeProvider);
  }, [providers]);

  const [formState, setFormState] = useState({
    domain: DOMAIN_OPTIONS[0].value,
    scenario: '',
    context: '',
    llmProvider: availableProviders[0]?.id ?? FALLBACK_PROVIDERS[0].id,
    llmConfig: {
      apiKey: '',
      endpoint: '',
      model: '',
    },
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (!availableProviders.some((provider) => provider.id === formState.llmProvider)) {
      setFormState((current) => ({
        ...current,
        llmProvider: availableProviders[0]?.id ?? FALLBACK_PROVIDERS[0].id,
      }));
    }
  }, [availableProviders, formState.llmProvider]);

  const selectedDomain = DOMAIN_OPTIONS.find((domain) => domain.value === formState.domain) ?? DOMAIN_OPTIONS[0];
  const selectedProvider =
    availableProviders.find((provider) => provider.id === formState.llmProvider) ?? availableProviders[0];

  const handleFieldChange = (field, value) => {
    setFormState((current) => ({ ...current, [field]: value }));
    setErrors((current) => ({ ...current, [field]: '' }));
  };

  const handleConfigChange = (field, value) => {
    setFormState((current) => ({
      ...current,
      llmConfig: {
        ...current.llmConfig,
        [field]: value,
      },
    }));
    setErrors((current) => ({ ...current, [field]: '' }));
  };

  const validate = () => {
    const nextErrors = {};

    if (!formState.scenario.trim()) {
      nextErrors.scenario = 'Please describe the supply chain scenario.';
    } else if (formState.scenario.trim().length < MIN_SCENARIO_LENGTH) {
      nextErrors.scenario = `Scenario must be at least ${MIN_SCENARIO_LENGTH} characters.`;
    }

    if (!formState.llmConfig.apiKey.trim()) {
      nextErrors.apiKey = 'API key is required for this request.';
    }

    if (selectedProvider?.requiresEndpoint && !formState.llmConfig.endpoint.trim()) {
      nextErrors.endpoint = 'Endpoint is required for Azure OpenAI requests.';
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!validate()) {
      return;
    }

    const providerDefaults = getProviderDefaults(formState.llmProvider);

    await onSubmit({
      domain: formState.domain,
      scenario: formState.scenario.trim(),
      context: formState.context.trim(),
      llmProvider: formState.llmProvider,
      llmConfig: {
        apiKey: formState.llmConfig.apiKey.trim(),
        endpoint: formState.llmConfig.endpoint.trim(),
        model: formState.llmConfig.model.trim() || selectedProvider?.defaultModel || providerDefaults.model,
      },
    });
  };

  return (
    <form className="panel scenario-panel" onSubmit={handleSubmit}>
      <div className="section-heading">
        <div>
          <p className="eyebrow">Scenario definition</p>
          <h2>Build supply chain prompt recommendations</h2>
        </div>
        <span className={`domain-chip ${selectedDomain.accentClass}`}>
          <span>{selectedDomain.icon}</span>
          {selectedDomain.label}
        </span>
      </div>

      <div className="field-group">
        <label htmlFor="domain">Domain</label>
        <select
          id="domain"
          value={formState.domain}
          onChange={(event) => handleFieldChange('domain', event.target.value)}
        >
          {DOMAIN_OPTIONS.map((domain) => (
            <option key={domain.value} value={domain.value}>
              {domain.label}
            </option>
          ))}
        </select>
      </div>

      <div className="field-group">
        <label htmlFor="scenario">Scenario</label>
        <textarea
          id="scenario"
          rows="6"
          value={formState.scenario}
          onChange={(event) => handleFieldChange('scenario', event.target.value)}
          placeholder={selectedDomain.placeholder}
        />
        <div className="field-meta">
          <span className="field-help">Describe objectives, constraints, risks, and expected outcome.</span>
          <span className="character-count">{formState.scenario.trim().length} characters</span>
        </div>
        {errors.scenario ? <span className="field-error">{errors.scenario}</span> : null}
      </div>

      <div className="field-group">
        <label htmlFor="context">Additional context</label>
        <textarea
          id="context"
          rows="4"
          value={formState.context}
          onChange={(event) => handleFieldChange('context', event.target.value)}
          placeholder="Any additional context such as ERP data limitations, geography, supplier constraints, or customer service targets..."
        />
      </div>

      <div className="field-group">
        <label htmlFor="llmProvider">LLM provider</label>
        <select
          id="llmProvider"
          value={formState.llmProvider}
          onChange={(event) => handleFieldChange('llmProvider', event.target.value)}
        >
          {availableProviders.map((provider) => (
            <option key={provider.id} value={provider.id}>
              {provider.name}
            </option>
          ))}
        </select>
      </div>

      <LLMConfig
        provider={selectedProvider}
        config={formState.llmConfig}
        onChange={handleConfigChange}
        errors={errors}
      />

      <button className="primary-button" type="submit" disabled={loading}>
        {loading ? (
          <>
            <span className="button-spinner" aria-hidden="true" />
            Generating recommendations...
          </>
        ) : (
          'Generate top prompts'
        )}
      </button>
    </form>
  );
}
