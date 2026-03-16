export type SignalType =
  | "hidden_accumulation"
  | "narrative_ignition"
  | "retail_trap"
  | "neutral";

export interface Token {
  id: string;
  symbol: string;
  name: string;
  market_type: string;
  is_active: boolean;
}

export interface Explanation {
  why_now: string;
  risks: string[];
  suggested_action: string;
  invalidation_conditions: string[];
  evidence: string[];
}

export interface Signal {
  id: string;
  token_id: string;
  token_symbol: string;
  triggered_at: string;
  signal_type: SignalType;
  signal_score: number;
  confidence: number;
  status: string;
  explanation: Explanation;
  invalidation_json: Record<string, unknown>;
}

