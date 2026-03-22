const API_BASE = import.meta.env.VITE_API_URL ?? "";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      credentials: "include", // Include session cookie
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail ?? `API Error: ${res.status}`);
    }
    return res.json();
  }

  // Health
  health() {
    return this.request<{ status: string; version: string }>("/api/health");
  }

  // Auth
  connect(accessKey: string, secretKey: string) {
    return this.request<{ success: boolean; message: string; balance_count: number }>(
      "/api/trades/connect",
      { method: "POST", body: JSON.stringify({ access_key: accessKey, secret_key: secretKey }) }
    );
  }

  disconnect() {
    return this.request("/api/trades/disconnect", { method: "POST" });
  }

  // Trades
  syncTrades() {
    return this.request<{ synced: number; skipped: number; total: number; market_orders_enriched: number }>(
      "/api/trades/sync",
      { method: "POST" }
    );
  }

  getTrades(params?: Record<string, string>) {
    const qs = params ? `?${new URLSearchParams(params)}` : "";
    return this.request<import("@/types").Trade[]>(`/api/trades${qs}`);
  }

  getStatistics() {
    return this.request<import("@/types").TradeStats>("/api/trades/statistics");
  }

  uploadCsv(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return fetch(`${this.baseUrl}/api/trades/upload-csv`, {
      method: "POST",
      credentials: "include",
      body: formData,
    }).then(async (res) => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail ?? "Upload failed");
      }
      return res.json();
    });
  }

  // Paste (browser console script output)
  pasteTrades(text: string) {
    return this.request<{ synced: number; skipped: number; total_parsed: number }>(
      "/api/trades/paste",
      { method: "POST", body: JSON.stringify({ text }) }
    );
  }

  // Analysis
  getFullAnalysis() {
    return this.request("/api/analysis/full");
  }

  getAnalysisByCoin() {
    return this.request("/api/analysis/by-coin");
  }

  getAnalysisByTime() {
    return this.request("/api/analysis/by-time");
  }

  // Coaching
  generateReport(start?: string, end?: string) {
    return this.request("/api/coaching/generate", {
      method: "POST",
      body: JSON.stringify({ start, end }),
    });
  }
}

export const api = new ApiClient(API_BASE);
