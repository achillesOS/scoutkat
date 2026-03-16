import Link from "next/link";

import { HeroSignalCard } from "@/components/hero-signal-card";
import { Shell } from "@/components/shell";
import { StatusBar } from "@/components/status-bar";
import { Card } from "@/components/ui/card";
import { WatchlistTokenCard } from "@/components/watchlist-token-card";
import { getSignals, getTokens, getWatchlist } from "@/lib/api";
import { buildWatchtowerViewModel } from "@/lib/watchtower";

export default async function WatchlistPage() {
  const [watchlist, allTokens, signals] = await Promise.all([
    getWatchlist(),
    getTokens(),
    getSignals(),
  ]);
  const watchtower = buildWatchtowerViewModel({
    watchlistItems: watchlist.items,
    allTokens,
    signals,
  });

  return (
    <Shell
      title="Watchtower"
      eyebrow="Scoutkat / 哨鼬"
      description="Scoutkat watches X attention against Hyperliquid structure."
    >
      <section>
        <StatusBar
          lastRefresh={watchtower.lastRefresh}
          monitoredAssets={watchtower.monitoredAssets}
          activeSignals={watchtower.activeSignals}
          recentlyChanged={watchtower.recentlyChanged}
        />
      </section>

      <section className="mt-6 grid gap-4 xl:grid-cols-3">
        {watchtower.heroCards.map((hero) => (
          <HeroSignalCard key={hero.title} title={hero.title} token={hero.token} />
        ))}
      </section>

      <section className="mt-8">
        <div className="mb-4 flex items-end justify-between gap-4">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-foreground/45">
              Live board
            </p>
            <h2 className="mt-2 text-2xl font-black tracking-tight">Watchlist</h2>
          </div>
          <p className="max-w-xl text-sm text-foreground/62">
            The assets Scoutkat is actively monitoring for structure, attention, and signal-state changes.
          </p>
        </div>

        {watchtower.watchlist.length === 0 ? (
          <Card>
            <p className="text-xl font-black">No watchlist yet</p>
            <p className="mt-3 max-w-xl text-sm leading-7 text-foreground/72">
              Add a few perps to start a live board. Scoutkat will begin prioritizing refreshes and surfacing changes here.
            </p>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
            {watchtower.watchlist.map((token) => (
              <WatchlistTokenCard key={token.id} token={token} />
            ))}
          </div>
        )}
      </section>

      <section className="mt-8">
        <Card className="rounded-[1.5rem] bg-white/55 p-4">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-foreground/45">
                Universe
              </p>
              <h2 className="mt-1 text-lg font-black tracking-tight">Explore universe</h2>
            </div>
            <p className="max-w-xl text-sm text-foreground/58">
              Add more Hyperliquid perps to widen Scoutkat coverage.
            </p>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {watchtower.explore.map((token) => (
              <Link
                key={token.id}
                href={`/tokens/${token.symbol}`}
                className="rounded-full border border-border/60 bg-white/60 px-3 py-2 text-sm font-semibold text-foreground/72 transition hover:bg-white"
              >
                {token.symbol}
              </Link>
            ))}
          </div>
        </Card>
      </section>
    </Shell>
  );
}
