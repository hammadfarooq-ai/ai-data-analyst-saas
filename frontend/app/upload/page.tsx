"use client";

import { FormEvent, useState } from "react";

import { api } from "@/lib/api";
import { keys, setStoredValue } from "@/lib/storage";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleUpload(event: FormEvent) {
    event.preventDefault();
    if (!file) return;

    try {
      setLoading(true);
      setError("");
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await api.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setResponse(data);
      setStoredValue(keys.datasetId, data.dataset_id);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Upload failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Upload Dataset</h2>
      <form className="card space-y-3" onSubmit={handleUpload}>
        <input className="input" type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button type="submit" className="button-primary" disabled={loading}>
          {loading ? "Uploading..." : "Upload CSV"}
        </button>
        {error && <p className="text-sm text-rose-400">{error}</p>}
      </form>

      {response && (
        <div className="card">
          <h3 className="mb-3 text-lg font-semibold text-cyan-300">Dataset Summary</h3>
          <pre className="overflow-auto text-sm text-slate-300">{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
