import { signals as fallbackSignals, tokens as fallbackTokens } from "@/lib/mock-data";
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
  return (await fetchJson<Token[]>("/tokens")) ?? fallbackTokens;
}

export async function getToken(symbol: string) {
  const fallback = fallbackTokens.find((token) => token.symbol === symbol);
  return (
    (await fetchJson<Token & { recent_signals?: Signal[] }>(`/tokens/${symbol}`)) ??
    (fallback
      ? {
          ...fallback,
          recent_signals: fallbackSignals.filter((signal) => signal.token_symbol === symbol),
        }
      : null)
  );
}

export async function getSignals() {
  return (await fetchJson<Signal[]>("/signals")) ?? fallbackSignals;
}

export async function getSignal(id: string) {
  return (
    (await fetchJson<Signal>(`/signals/${id}`)) ??
    fallbackSignals.find((signal) => signal.id === id) ??
    null
  );
}

export async function getWatchlist() {
  const data = await fetchJson<{ items: Token[] }>("/watchlist");
  return data ?? { items: [] };
}

export async function getWatchlistTokenIds() {
  const watchlist = await getWatchlist();
  return new Set(watchlist.items.map((token) => token.id));
}
