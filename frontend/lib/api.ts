import type { Signal, Token, TokenContext, WatchtowerOverview } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      cache: "no-store",
      ...options,
    });
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

export async function getSignals() {
  return (await fetchJson<Signal[]>("/signals")) ?? [];
}

export async function getSignal(id: string) {
  return await fetchJson<Signal>(`/signals/${id}`);
}

export async function getWatchtowerOverview(symbols?: string[], userEmail?: string) {
  const query = symbols && symbols.length > 0 ? `?symbols=${symbols.join(",")}` : "";
  return await fetchJson<WatchtowerOverview>(`/watchtower${query}`, {
    headers: userEmail ? { "x-user-email": userEmail } : undefined,
  });
}

export async function getTokenContext(symbol: string) {
  return await fetchJson<TokenContext>(`/tokens/${symbol}/context`);
}
