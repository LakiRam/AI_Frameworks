import RecommendationCard from './RecommendationCard';

export default function ResultsPanel({ loading, recommendations, error, domain }) {
  return (
    <section className="panel results-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Prompt recommendations</p>
          <h2>Top 3 results</h2>
        </div>
      </div>

      {error ? <div className="banner banner-error">{error}</div> : null}

      {loading ? (
        <div className="results-state loading-state">
          <div className="spinner" aria-hidden="true" />
          <div>
            <h3>Generating recommendation set</h3>
            <p>Analyzing supply chain scenario, provider settings, and prompt opportunities.</p>
          </div>
        </div>
      ) : null}

      {!loading && recommendations.length === 0 && !error ? (
        <div className="results-state empty-state">
          <h3>Ready for your scenario</h3>
          <p>
            Submit a scenario to receive ranked prompts tailored for supply chain planning, execution,
            and risk analysis.
          </p>
        </div>
      ) : null}

      {!loading && recommendations.length > 0 ? (
        <div className="recommendation-grid">
          {recommendations.slice(0, 3).map((recommendation) => (
            <RecommendationCard
              key={`${recommendation.rank}-${recommendation.useCase}`}
              recommendation={recommendation}
              domain={domain}
            />
          ))}
        </div>
      ) : null}
    </section>
  );
}
