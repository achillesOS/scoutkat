import { notFound } from "next/navigation";

import { addToWatchlist, removeFromWatchlist } from "@/app/actions";
import { SignalCard } from "@/components/signal-card";
import { Shell } from "@/components/shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { getToken, getWatchlistTokenIds } from "@/lib/api";

export default async function TokenPage({
  params,
}: {
  params: Promise<{ symbol: string }>;
}) {
  const { symbol } = await params;
  const token = await getToken(symbol.toUpperCase());
  const watchlistIds = await getWatchlistTokenIds();
  if (!token) {
    notFound();
  }
  const isWatching = watchlistIds.has(token.id);

  return (
    <Shell title={token.symbol} eyebrow={token.name}>
      <section className="grid gap-4 xl:grid-cols-[320px_minmax(0,1fr)]">
        <Card className="space-y-4">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-foreground/45">Token</p>
            <p className="mt-2 text-3xl font-black">{token.symbol}</p>
            <p className="text-foreground/65">{token.name}</p>
          </div>
          <p className="text-sm leading-7 text-foreground/72">
            Token detail page will grow into the main context screen for market structure, positioning, and narrative state.
          </p>
          {isWatching ? (
            <form action={removeFromWatchlist}>
              <input type="hidden" name="token_id" value={token.id} />
              <input type="hidden" name="symbol" value={token.symbol} />
              <Button type="submit" variant="ghost" className="w-full">
                Remove from watchlist
              </Button>
            </form>
          ) : (
            <form action={addToWatchlist}>
              <input type="hidden" name="token_id" value={token.id} />
              <input type="hidden" name="symbol" value={token.symbol} />
              <Button type="submit" className="w-full">
                Add to watchlist
              </Button>
            </form>
          )}
        </Card>
        <div className="grid gap-4">
          {(token.recent_signals || []).length === 0 ? (
            <Card>
              <p className="text-lg font-black">No recent signals</p>
              <p className="mt-3 text-sm leading-7 text-foreground/72">
                This token exists in the live token universe, but Scoutkat has not produced a recent signal event for it yet.
              </p>
            </Card>
          ) : null}
          {(token.recent_signals || []).map((signal) => (
            <SignalCard key={signal.id} signal={signal} />
          ))}
        </div>
      </section>
    </Shell>
  );
}
