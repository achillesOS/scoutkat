import Link from "next/link";

import { removeFromWatchlist } from "@/app/actions";
import { Shell } from "@/components/shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { getTokens, getWatchlist } from "@/lib/api";

export default async function WatchlistPage() {
  const watchlist = await getWatchlist();
  const allTokens = await getTokens();
  const watchlistIds = new Set(watchlist.items.map((token) => token.id));
  const availableTokens = allTokens.filter((token) => !watchlistIds.has(token.id)).slice(0, 6);

  return (
    <Shell title="Watchlist" eyebrow="Scoutkat / 哨鼬">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {watchlist.items.length === 0 ? (
          <Card className="md:col-span-2 xl:col-span-3">
            <p className="text-xl font-black">No watchlist yet</p>
            <p className="mt-3 max-w-xl text-sm leading-7 text-foreground/72">
              Your backend is live and connected to real data. Add tokens to the watchlist next so Scoutkat can prioritize social refresh and personalized signal tracking.
            </p>
          </Card>
        ) : null}
        {watchlist.items.map((token) => (
          <Card key={token.id}>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-2xl font-black">{token.symbol}</p>
                <p className="text-sm text-foreground/65">{token.name}</p>
              </div>
              <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                {token.market_type}
              </span>
            </div>
            <p className="mt-4 text-sm text-foreground/70">
              Fast access to signal context, structure shifts, and candidate narrative changes.
            </p>
            <div className="mt-5 flex items-center justify-between gap-3">
              <Link href={`/tokens/${token.symbol}`} className="text-sm font-semibold text-primary">
                Open token
              </Link>
              <form action={removeFromWatchlist}>
                <input type="hidden" name="token_id" value={token.id} />
                <input type="hidden" name="symbol" value={token.symbol} />
                <Button variant="ghost" type="submit" className="px-0 text-sm text-foreground/65">
                  Remove
                </Button>
              </form>
            </div>
          </Card>
        ))}
      </section>
      <section className="mt-8">
        <Card>
          <p className="text-xl font-black">Explore universe</p>
          <p className="mt-3 text-sm leading-7 text-foreground/72">
            Add major Hyperliquid names to your watchlist so Scoutkat prioritizes social refresh and signal tracking.
          </p>
          <div className="mt-5 flex flex-wrap gap-2">
            {availableTokens.map((token) => (
              <Link
                key={token.id}
                href={`/tokens/${token.symbol}`}
                className="rounded-full border border-border/70 px-3 py-2 text-sm font-semibold text-foreground/75 transition hover:bg-muted"
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
