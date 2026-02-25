export default function HomePage() {
  return (
    <div className="space-y-6">
      <section className="card">
        <h2 className="mb-2 text-3xl font-bold">AI Data Analyst - Auto EDA + ML Predictor</h2>
        <p className="text-slate-300">
          Upload CSV datasets, generate automatic EDA, train ML models, get SHAP explainability, chat with your data, and
          download production-ready reports.
        </p>
      </section>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="card">
          <h3 className="font-semibold text-cyan-300">Automated EDA</h3>
          <p className="mt-2 text-sm text-slate-300">Missing values, correlation, outliers, skewness, and chart payloads.</p>
        </div>
        <div className="card">
          <h3 className="font-semibold text-cyan-300">Auto Model Selection</h3>
          <p className="mt-2 text-sm text-slate-300">Classification/regression pipeline with cross-validation and best model pick.</p>
        </div>
        <div className="card">
          <h3 className="font-semibold text-cyan-300">Explain + Report</h3>
          <p className="mt-2 text-sm text-slate-300">Feature importance, SHAP summary, chatbot Q&A, and downloadable PDF report.</p>
        </div>
      </section>
    </div>
  );
}
