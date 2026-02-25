export const keys = {
  datasetId: "ai_dataset_id",
  modelId: "ai_model_id"
};

export function setStoredValue(key: string, value: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem(key, value);
  }
}

export function getStoredValue(key: string): string {
  if (typeof window === "undefined") {
    return "";
  }
  return localStorage.getItem(key) || "";
}
