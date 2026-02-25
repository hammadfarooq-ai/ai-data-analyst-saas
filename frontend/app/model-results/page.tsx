"use client";

import { FormEvent, useState } from "react";

import { api } from "@/lib/api";
import { getStoredValue, keys, setStoredValue } from "@/lib/storage";

export default function ModelResultsPage() {
  const [target, setTarget] = useState("");
  const [trainResult, setTrainResult] = useState<any>(null);
  const [predictInput, setPredictInput] = useState("{}");
  const [predictResult, setPredictResult] = useState<any>(null);
  const [error, setError] = useState("");

  async function detectTarget() {
    const datasetId = getStoredValue(keys.datasetId);
    if (!datasetId) return setError("Upload a dataset first.");
    setError("");
    const { data } = await api.get(`/eda/detect-target/${datasetId}`);
    setTarget(data.detected_target || "");
  }

  async function trainModel(event: FormEvent) {
    event.preventDefault();
    const datasetId = getStoredValue(keys.datasetId);
    if (!datasetId) return setError("Upload a dataset first.");
    try {
      setError("");
      const { data } = await api.post("/ml/train", {
        dataset_id: datasetId,
        target_column: target || null
      });
      setTrainResult(data);
      setStoredValue(keys.modelId, data.model_id);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Training failed.");
    }
  }

  async function runPrediction(event: FormEvent) {
    event.preventDefault();
    const modelId = getStoredValue(keys.modelId);
    if (!modelId) return setError("Train a model first.");
    try {
      const record = JSON.parse(predictInput);
      const { data } = await api.post("/ml/predict", {
        model_id: modelId,
        record
      });
      setPredictResult(data);
    } catch {
      setError("Prediction failed. Ensure valid JSON record.");
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Model Results</h2>

      <div className="card space-y-3">
        <button className="button-primary" onClick={detectTarget}>
          Detect Target Column
        </button>
        <form onSubmit={trainModel} className="space-y-2">
          <input className="input" value={target} onChange={(e) => setTarget(e.target.value)} placeholder="Target column" />
          <button className="button-primary" type="submit">
            Train Best Model
          </button>
        </form>
      </div>

      {trainResult && (
        <div className="card">
          <h3 className="mb-3 text-lg font-semibold text-cyan-300">Training Output</h3>
          <pre className="max-h-[450px] overflow-auto text-sm text-slate-300">{JSON.stringify(trainResult, null, 2)}</pre>
        </div>
      )}

      <div className="card space-y-3">
        <h3 className="font-semibold">Run Prediction</h3>
        <form onSubmit={runPrediction} className="space-y-2">
          <textarea className="input min-h-36" value={predictInput} onChange={(e) => setPredictInput(e.target.value)} />
          <button className="button-primary" type="submit">
            Predict
          </button>
        </form>
        {predictResult && <pre className="text-sm text-slate-300">{JSON.stringify(predictResult, null, 2)}</pre>}
      </div>

      {error && <p className="text-sm text-rose-400">{error}</p>}
    </div>
  );
}
