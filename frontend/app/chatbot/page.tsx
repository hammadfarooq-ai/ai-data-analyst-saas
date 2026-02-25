"use client";

import { FormEvent, useState } from "react";

import { api } from "@/lib/api";
import { getStoredValue, keys } from "@/lib/storage";

export default function ChatbotPage() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<any>(null);
  const [error, setError] = useState("");

  async function askQuestion(event: FormEvent) {
    event.preventDefault();
    const datasetId = getStoredValue(keys.datasetId);
    if (!datasetId) return setError("Upload a dataset first.");
    try {
      const { data } = await api.post("/chatbot", {
        dataset_id: datasetId,
        question
      });
      setResponse(data);
      setError("");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Chat request failed.");
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Dataset Chatbot</h2>
      <form onSubmit={askQuestion} className="card space-y-3">
        <input
          className="input"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask: What is the average salary?"
        />
        <button className="button-primary" type="submit">
          Ask
        </button>
      </form>
      {error && <p className="text-sm text-rose-400">{error}</p>}
      {response && (
        <div className="card">
          <pre className="text-sm text-slate-300">{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
