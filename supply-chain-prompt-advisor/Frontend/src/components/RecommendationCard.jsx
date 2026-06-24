import { useState } from 'react';

const USE_CASE_CLASSES = {
  procurement: 'domain-procurement',
  inventory: 'domain-inventory',
  'demand-forecasting': 'domain-demand',
  logistics: 'domain-logistics',
  'supplier-risk': 'domain-risk',
};

export default function RecommendationCard({ recommendation, domain }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(recommendation.prompt);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      setCopied(false);
    }
  };

  return (
    <article className="recommendation-card reveal-up">
      <div className="recommendation-header">
        <span className="rank-badge">#{recommendation.rank}</span>
        <span className={`use-case-tag ${USE_CASE_CLASSES[domain] ?? 'domain-procurement'}`}>
          {recommendation.useCase || 'Recommended use case'}
        </span>
      </div>

      <div className="prompt-box">
        <div className="prompt-box-header">
          <h3>Suggested prompt</h3>
          <button className="secondary-button copy-button" type="button" onClick={handleCopy}>
            {copied ? 'Copied!' : 'Copy'}
          </button>
        </div>
        <p>{recommendation.prompt}</p>
      </div>

      <div className="recommendation-content">
        <div>
          <h4>Why it fits</h4>
          <p>{recommendation.explanation}</p>
        </div>
      </div>
    </article>
  );
}
