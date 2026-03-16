import type { WatchtowerOverview } from "@/lib/types";

export const emptyWatchtowerOverview: WatchtowerOverview = {
  last_refresh: new Date(0).toISOString(),
  tracked_assets_count: 0,
  active_signals_count: 0,
  recently_changed_count: 0,
  hero_cards: [],
  assets: [],
};
