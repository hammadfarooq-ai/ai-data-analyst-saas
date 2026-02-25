"use client";

import { useState } from "react";

import { api } from "@/lib/api";
import { getStoredValue, keys } from "@/lib/storage";

export default function DashboardPage() {
  const [payload, setPayload] = useState<any>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function runEDA() {
    const datasetId = getStoredValue(keys.datasetId);
    if (!datasetId) {
      setError("No dataset found. Upload a CSV first.");
      return;
    }
    try {
      setLoading(true);
      setError("");
      const { data } = await api.get(`/eda/${datasetId}`);
      setPayload(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to fetch EDA.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Dashboard</h2>
      <div className="card">
        <button className="button-primary" onClick={runEDA} disabled={loading}>
          {loading ? "Generating..." : "Generate Auto EDA"}
        </button>
        {error && <p className="mt-2 text-sm text-rose-400">{error}</p>}
      </div>
      {payload && (
        <div className="card">
          <h3 className="mb-3 text-lg font-semibold text-cyan-300">EDA JSON Response</h3>
          <pre className="max-h-[500px] overflow-auto text-sm text-slate-300">{JSON.stringify(payload, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
