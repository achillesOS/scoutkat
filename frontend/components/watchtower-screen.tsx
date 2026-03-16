import Link from "next/link";
import type { ReactNode } from "react";

import { HeroSignalCard } from "@/components/hero-signal-card";
import { Shell } from "@/components/shell";
import { StatusBar } from "@/components/status-bar";
import { WatchlistTokenCard } from "@/components/watchlist-token-card";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { Token, WatchtowerOverview } from "@/lib/types";

export async function WatchtowerScreen({
  title,
  eyebrow,
  description,
  overview,
  universeTokens,
  listTitle,
  listBody,
  actions,
}: {
  title: string;
  eyebrow: string;
  description: string;
  overview: WatchtowerOverview;
  universeTokens: Token[];
  listTitle: string;
  listBody: string;
  actions?: ReactNode;
}) {
  const explore = universeTokens.filter(
    (token) => !overview.assets.some((asset) => asset.symbol === token.symbol),
  );

  return (
    <Shell title={title} eyebrow={eyebrow} description={description} actions={actions}>
      <section>
        <StatusBar
          lastRefresh={overview.last_refresh}
          monitoredAssets={overview.tracked_assets_count}
          activeSignals={overview.active_signals_count}
          recentlyChanged={overview.recently_changed_count}
        />
      </section>

      <section className="mt-6 grid gap-4 xl:grid-cols-3">
        {overview.hero_cards.map((hero) => (
          <HeroSignalCard key={`${hero.title}-${hero.token_symbol}`} hero={hero} />
        ))}
      </section>

      <section className="mt-8">
        <div className="mb-4 flex items-end justify-between gap-4">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-foreground/45">
              Live board
            </p>
            <h2 className="mt-2 text-2xl font-black tracking-tight">{listTitle}</h2>
          </div>
          <p className="max-w-xl text-sm text-foreground/62">{listBody}</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
          {overview.assets.map((token) => (
            <WatchlistTokenCard key={token.id} token={token} />
          ))}
        </div>
      </section>

      <section className="mt-8">
        <Card className="rounded-[1.5rem] bg-white/55 p-4">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-foreground/45">
                Universe
              </p>
              <h2 className="mt-1 text-lg font-black tracking-tight">Tracked universe</h2>
            </div>
            <p className="max-w-xl text-sm text-foreground/58">
              Browse major Hyperliquid names and inspect how attention, structure, and positioning compare.
            </p>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {explore.map((token) => (
              <Button key={token.id} asChild variant="ghost" className="border border-border/60 bg-white/60">
                <Link href={`/tokens/${token.symbol}`}>{token.symbol}</Link>
              </Button>
            ))}
          </div>
        </Card>
      </section>
    </Shell>
  );
}
