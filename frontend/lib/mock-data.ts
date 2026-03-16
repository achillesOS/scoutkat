import type { Signal, Token } from "@/lib/types";

export const tokens: Token[] = [
  { id: "btc", symbol: "BTC", name: "Bitcoin", market_type: "perp", is_active: true },
  { id: "eth", symbol: "ETH", name: "Ethereum", market_type: "perp", is_active: true },
  { id: "sol", symbol: "SOL", name: "Solana", market_type: "perp", is_active: true },
];

export const signals: Signal[] = [
  {
    id: "sig_btc_hidden_1",
    token_id: "btc",
    token_symbol: "BTC",
    triggered_at: new Date().toISOString(),
    signal_type: "hidden_accumulation",
    signal_score: 78,
    confidence: 0.81,
    status: "active",
    explanation: {
      why_now:
        "Structure is holding up while public attention is still behind the move and perp positioning remains relatively calm.",
      risks: ["Funding can heat up fast", "A failed breakout would weaken the read"],
      suggested_action:
        "Keep BTC on the watchlist for continuation if structure stays strong and attention begins catching up.",
      invalidation_conditions: [
        "Structure loses efficiency on the next rotation",
        "Funding z-score jumps into crowded territory",
      ],
      evidence: ["Absorption remains firm", "Attention still lags structure"],
    },
    invalidation_json: {},
  },
  {
    id: "sig_sol_narrative_1",
    token_id: "sol",
    token_symbol: "SOL",
    triggered_at: new Date().toISOString(),
    signal_type: "narrative_ignition",
    signal_score: 84,
    confidence: 0.77,
    status: "active",
    explanation: {
      why_now:
        "Social attention and structure are accelerating together, suggesting a fresh narrative move before positioning becomes fully crowded.",
      risks: ["Momentum could overshoot", "Chasing can be punished if OI expands too quickly"],
      suggested_action:
        "Treat SOL as an emerging trend candidate and look for confirmation rather than immediate size.",
      invalidation_conditions: [
        "Mention acceleration stalls",
        "Trade imbalance flips against the move",
      ],
      evidence: ["Rising social breadth", "Structure confirms the narrative"],
    },
    invalidation_json: {},
  },
];

