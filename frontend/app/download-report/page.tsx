"use client";

import { useEffect, useState } from "react";

import { getStoredValue, keys } from "@/lib/storage";

export default function DownloadReportPage() {
  const [modelId, setModelId] = useState("");

  useEffect(() => {
    setModelId(getStoredValue(keys.modelId));
  }, []);

  const reportUrl = modelId ? `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/report/download-report/${modelId}` : "";

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Download Report</h2>
      <div className="card space-y-2">
        <p className="text-sm text-slate-300">
          Train a model first. Then download a generated PDF report containing dataset summary, EDA highlights, model metrics, and
          explainability insights.
        </p>
        {modelId ? (
          <a href={reportUrl} target="_blank" className="button-primary inline-block" rel="noreferrer">
            Download PDF Report
          </a>
        ) : (
          <p className="text-sm text-amber-300">No model found in local storage.</p>
        )}
      </div>
    </div>
  );
}
