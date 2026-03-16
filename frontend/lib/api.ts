import type { Signal, Token } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function fetchJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function getTokens() {
  return (await fetchJson<Token[]>("/tokens")) ?? [];
}

export async function getToken(symbol: string) {
  return await fetchJson<Token & { recent_signals?: Signal[] }>(`/tokens/${symbol}`);
}

export async function getSignals() {
  return (await fetchJson<Signal[]>("/signals")) ?? [];
}

export async function getSignal(id: string) {
  return await fetchJson<Signal>(`/signals/${id}`);
}

export async function getWatchlist() {
  const data = await fetchJson<{ items: Token[] }>("/watchlist");
  return data ?? { items: [] };
}

export async function getWatchlistTokenIds() {
  const watchlist = await getWatchlist();
  return new Set(watchlist.items.map((token) => token.id));
}
