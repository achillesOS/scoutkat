import type { Token, TokenContext, WatchtowerOverview } from "@/lib/types";

const STARTER_TOKENS = [
  ["btc-fallback", "BTC", "Bitcoin"],
  ["eth-fallback", "ETH", "Ethereum"],
  ["sol-fallback", "SOL", "Solana"],
  ["xrp-fallback", "XRP", "XRP"],
  ["doge-fallback", "DOGE", "Dogecoin"],
] as const;

export const fallbackWorkspaceTokens: Token[] = STARTER_TOKENS.map(([id, symbol, name]) => ({
  id,
  symbol,
  name,
  market_type: "perp",
  is_active: true,
}));

export function buildFallbackTokenContext(symbol: string, tokens: Token[]): TokenContext {
  const token = tokens.find((item) => item.symbol === symbol) ?? tokens[0] ?? fallbackWorkspaceTokens[0];

  return {
    header: {
      id: token.id,
      symbol: token.symbol,
      name: token.name,
      market_type: token.market_type,
      current_price: 0,
      change_1h: 0,
      change_4h: 0,
      change_24h: 0,
      last_updated: new Date().toISOString(),
    },
    current_signal_state: {
      signal_type: "neutral",
      signal_score: 0,
      confidence: 0,
      why_now: "Live backend data is temporarily unavailable, so Scoutkat cannot compute the current divergence state yet.",
      risks: ["The live backend is unavailable, so this view is a degraded shell."],
      invalidation: ["Reconnect the live backend before acting on this placeholder state."],
    },
    social_summary: {
      snapshot_incomplete: true,
      attention_label: "Unavailable",
      discussion_type: "unclear",
      signal_hint: "unclear",
      confidence: 0,
      summary_points: ["Social summary is temporarily unavailable while the live backend reconnects."],
      top_narratives: [],
      expert_presence: 0,
      retail_breadth: 0,
      narrative_novelty: 0,
    },
    divergence_chart: {
      default_timeframe: "72h",
      series: {
        "24h": [],
        "72h": [],
        "7d": [],
      },
    },
    recent_state_changes: [],
    recent_signal_history: [],
  };
}

export function buildFallbackOverview(tokens: Token[], trackedSymbols: string[]): WatchtowerOverview {
  const symbols = trackedSymbols.length > 0 ? trackedSymbols : tokens.slice(0, 3).map((token) => token.symbol);

  return {
    last_refresh: new Date().toISOString(),
    tracked_assets_count: trackedSymbols.length,
    active_signals_count: 0,
    recently_changed_count: 0,
    hero_cards: [],
    assets: tokens
      .filter((token) => symbols.includes(token.symbol))
      .map((token) => ({
        ...token,
        current_price: 0,
        change_1h: 0,
        change_24h: 0,
        signal_type: "neutral" as const,
        signal_score: 0,
        confidence: 0,
        last_updated: new Date().toISOString(),
        why_now: "Live workspace data is temporarily unavailable.",
      })),
  };
}
