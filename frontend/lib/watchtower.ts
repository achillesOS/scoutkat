import {
  signals as mockSignals,
  tokens as mockTokens,
  watchtowerTokens,
  watchtowerWatchlistIds,
} from "@/lib/mock-data";
import type { Signal, SignalType, Token, WatchtowerToken } from "@/lib/types";

export interface WatchtowerHero {
  title: string;
  token: WatchtowerToken;
}

export interface WatchtowerViewModel {
  lastRefresh: string;
  monitoredAssets: number;
  activeSignals: number;
  recentlyChanged: number;
  heroCards: WatchtowerHero[];
  watchlist: WatchtowerToken[];
  explore: WatchtowerToken[];
}

export function signalLabel(signalType: SignalType | null) {
  switch (signalType) {
    case "hidden_accumulation":
      return "Hidden Accumulation";
    case "narrative_ignition":
      return "Narrative Ignition";
    case "retail_trap":
      return "Retail Trap";
    default:
      return "No active signal";
  }
}

export function signalTone(signalType: SignalType | null) {
  switch (signalType) {
    case "hidden_accumulation":
      return "bg-primary/12 text-primary ring-1 ring-primary/20";
    case "narrative_ignition":
      return "bg-amber-500/14 text-amber-900 ring-1 ring-amber-600/20";
    case "retail_trap":
      return "bg-rose-500/12 text-rose-800 ring-1 ring-rose-600/20";
    default:
      return "bg-muted text-foreground/70 ring-1 ring-border/70";
  }
}

export function formatPrice(value: number) {
  const digits = value >= 1000 ? 0 : value >= 100 ? 2 : value >= 1 ? 2 : 4;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  }).format(value);
}

export function formatPercent(value: number) {
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${value.toFixed(1)}%`;
}

export function formatRelativeTime(timestamp: string) {
  const diffMs = Date.now() - new Date(timestamp).getTime();
  const minutes = Math.max(1, Math.round(diffMs / 60000));

  if (minutes < 60) {
    return `${minutes}m ago`;
  }

  const hours = Math.round(minutes / 60);
  return `${hours}h ago`;
}

export function buildWatchtowerViewModel({
  watchlistItems,
  allTokens,
  signals,
}: {
  watchlistItems: Token[];
  allTokens: Token[];
  signals: Signal[];
}): WatchtowerViewModel {
  const effectiveSignals = signals.length > 0 ? signals : mockSignals;
  const signalMap = new Map(
    effectiveSignals
      .filter((signal) => signal.status === "active")
      .sort((a, b) => b.triggered_at.localeCompare(a.triggered_at))
      .map((signal) => [signal.token_id, signal]),
  );
  const mockMap = new Map(watchtowerTokens.map((token) => [token.id, token]));

  const universe = dedupeTokens([...(allTokens.length > 0 ? allTokens : mockTokens), ...watchtowerTokens]);
  const fallbackWatchlist = watchtowerTokens.filter((token) => watchtowerWatchlistIds.includes(token.id));
  const sourceWatchlist = watchlistItems.length > 0 ? watchlistItems : fallbackWatchlist;

  const watchlist = sourceWatchlist.map((token) => enrichToken(token, mockMap, signalMap));
  const watchlistIds = new Set(watchlist.map((token) => token.id));
  const explore = universe
    .filter((token) => !watchlistIds.has(token.id))
    .map((token) => enrichToken(token, mockMap, signalMap))
    .slice(0, 6);

  const activeWatchlistSignals = watchlist.filter((token) => token.signal_type !== null);
  const recentChangeCandidates = [...watchlist].sort(
    (a, b) =>
      Number(b.recently_changed) - Number(a.recently_changed) ||
      new Date(b.last_updated).getTime() - new Date(a.last_updated).getTime(),
  );

  const topSignal =
    activeWatchlistSignals
      .filter((token) => token.signal_type !== "retail_trap")
      .sort((a, b) => (b.signal_score ?? 0) - (a.signal_score ?? 0))[0] ?? watchlist[0];
  const topTrap =
    activeWatchlistSignals
      .filter((token) => token.signal_type === "retail_trap")
      .sort((a, b) => (b.signal_score ?? 0) - (a.signal_score ?? 0))[0] ?? watchlist[0];
  const justChanged = recentChangeCandidates[0] ?? watchlist[0];

  const latestTimestamp = [...watchlist, ...explore]
    .map((token) => token.last_updated)
    .sort((a, b) => b.localeCompare(a))[0] ?? new Date().toISOString();

  return {
    lastRefresh: latestTimestamp,
    monitoredAssets: watchlist.length,
    activeSignals: activeWatchlistSignals.length,
    recentlyChanged: watchlist.filter((token) => token.recently_changed).length,
    heroCards: [
      { title: "Top Signal Now", token: topSignal },
      { title: "Top Trap Now", token: topTrap },
      { title: "Just Changed", token: justChanged },
    ],
    watchlist,
    explore,
  };
}

function dedupeTokens(tokens: Token[]) {
  return Array.from(new Map(tokens.map((token) => [token.id, token])).values());
}

function enrichToken(
  token: Token,
  mockMap: Map<string, WatchtowerToken>,
  signalMap: Map<string, Signal>,
): WatchtowerToken {
  const mockToken = mockMap.get(token.id);
  const signal = signalMap.get(token.id);

  return {
    ...token,
    current_price: mockToken?.current_price ?? 0,
    change_1h: mockToken?.change_1h ?? 0,
    change_24h: mockToken?.change_24h ?? 0,
    signal_type: signal?.signal_type ?? mockToken?.signal_type ?? null,
    signal_score: signal?.signal_score ?? mockToken?.signal_score ?? null,
    confidence: signal?.confidence ?? mockToken?.confidence ?? null,
    last_updated: signal?.triggered_at ?? mockToken?.last_updated ?? new Date().toISOString(),
    why_now:
      signal?.explanation.why_now ??
      mockToken?.why_now ??
      "Scoutkat is watching this perp, but no fresh divergence has been promoted yet.",
    recently_changed: mockToken?.recently_changed ?? false,
  };
}
