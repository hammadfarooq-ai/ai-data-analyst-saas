"use client";

import { useState } from "react";

import { api } from "@/lib/api";
import { getStoredValue, keys } from "@/lib/storage";

export default function ExplainabilityPage() {
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  async function loadExplainability() {
    const modelId = getStoredValue(keys.modelId);
    if (!modelId) return setError("No trained model found.");
    try {
      const { data } = await api.get(`/ml/explain/${modelId}`);
      setResult(data);
      setError("");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Explainability fetch failed.");
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Explainability</h2>
      <div className="card">
        <button className="button-primary" onClick={loadExplainability}>
          Load Feature Importance + SHAP
        </button>
      </div>
      {error && <p className="text-sm text-rose-400">{error}</p>}
      {result && (
        <div className="card">
          <pre className="max-h-[500px] overflow-auto text-sm text-slate-300">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
