export type SignalType =
  | "hidden_accumulation"
  | "narrative_ignition"
  | "retail_trap"
  | "neutral";

export type AlertPreference = "early_setups" | "risk_alerts" | "balanced";
export type DivergenceTimeframe = "24h" | "72h" | "7d";

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

export interface WatchtowerToken extends Token {
  current_price: number;
  change_1h: number;
  change_24h: number;
  signal_type: SignalType;
  signal_score: number;
  confidence: number;
  last_updated: string;
  why_now: string;
}

export interface WatchtowerHeroCard {
  title: string;
  token_symbol: string;
  signal_type: SignalType;
  signal_score: number;
  confidence: number;
  current_price: number;
  change_24h: number;
  why_now: string;
}

export interface WatchtowerOverview {
  last_refresh: string;
  tracked_assets_count: number;
  active_signals_count: number;
  recently_changed_count: number;
  hero_cards: WatchtowerHeroCard[];
  assets: WatchtowerToken[];
}

export interface DivergencePoint {
  timestamp: string;
  attention_score: number;
  structure_score: number;
  positioning_score: number;
}

export interface TokenHeader {
  id: string;
  symbol: string;
  name: string;
  market_type: string;
  current_price: number;
  change_1h: number;
  change_4h: number;
  change_24h: number;
  last_updated: string;
}

export interface CurrentSignalState {
  signal_type: SignalType;
  signal_score: number;
  confidence: number;
  why_now: string;
  risks: string[];
  invalidation: string[];
}

export interface SocialSummary {
  snapshot_incomplete: boolean;
  attention_label: string;
  discussion_type: string;
  signal_hint: string;
  confidence: number;
  summary_points: string[];
  top_narratives: string[];
  expert_presence: number;
  retail_breadth: number;
  narrative_novelty: number;
}

export interface RecentStateChange {
  timestamp: string;
  title: string;
  detail: string;
  signal_type: SignalType;
}

export interface TokenContext {
  header: TokenHeader;
  current_signal_state: CurrentSignalState;
  social_summary: SocialSummary;
  divergence_chart: {
    default_timeframe: DivergenceTimeframe;
    series: Record<DivergenceTimeframe, DivergencePoint[]>;
  };
  recent_state_changes: RecentStateChange[];
  recent_signal_history: Signal[];
}

export interface UserOnboardingProfile {
  trackedSymbols: string[];
  alertPreference: AlertPreference;
  completedAt: string;
}

export interface ViewerState {
  isAuthenticated: boolean;
  email: string | null;
  hasSupabaseAuth: boolean;
  onboarding: UserOnboardingProfile | null;
}
