import Link from "next/link";
import { notFound } from "next/navigation";

import { toggleTrackedAsset } from "@/app/actions";
import { DivergenceChart } from "@/components/divergence-chart";
import { Shell } from "@/components/shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { requireOnboardedViewer } from "@/lib/auth";
import { getTokenContext, getTokens, getWatchtowerOverview } from "@/lib/api";
import type { SignalType, Token, TokenContext, WatchtowerOverview } from "@/lib/types";
import { formatPercent, formatPrice, formatRelativeTime, signalLabel, signalTone } from "@/lib/watchtower";

type Category = "default" | "watchlist";

function changeTone(value: number) {
  if (value > 0) {
    return "text-emerald-300";
  }
  if (value < 0) {
    return "text-rose-300";
  }
  return "text-white/60";
}

async function resolveTokenContext(candidates: string[]) {
  for (const symbol of candidates) {
    const context = await getTokenContext(symbol);
    if (context) {
      return context;
    }
  }
  return null;
}

function buildTokenUniverse(tokens: Token[], trackedSymbols: string[], category: Category) {
  const defaultSymbols = tokens.slice(0, 8).map((token) => token.symbol);
  const activeSymbols =
    category === "watchlist" && trackedSymbols.length > 0 ? trackedSymbols : defaultSymbols;

  return {
    defaultSymbols,
    activeSymbols,
    visibleTokens: tokens.filter((token) => activeSymbols.includes(token.symbol)),
  };
}

function metrics(overview: WatchtowerOverview, trackedSymbols: string[]) {
  return [
    { label: "Tracked assets", value: trackedSymbols.length.toString() },
    { label: "Active signals", value: overview.active_signals_count.toString() },
    { label: "Last refresh", value: formatRelativeTime(overview.last_refresh) },
    { label: "Recent changes", value: overview.recently_changed_count.toString() },
  ];
}

function RecentStateTone({ signalType }: { signalType: SignalType }) {
  return (
    <span className={`inline-flex px-2 py-1 text-[10px] uppercase tracking-[0.18em] ${signalTone(signalType)}`}>
      {signalLabel(signalType)}
    </span>
  );
}

function summaryPoints(context: TokenContext) {
  if (context.social_summary.summary_points.length > 0) {
    return context.social_summary.summary_points;
  }
  return ["Social summary is still being built from the latest valid snapshot."];
}

export default async function AppPage({
  searchParams,
}: {
  searchParams: Promise<{ category?: string; symbol?: string }>;
}) {
  const viewer = await requireOnboardedViewer();
  const tokens = await getTokens();

  if (tokens.length === 0) {
    notFound();
  }

  const params = await searchParams;
  const category: Category = params.category === "watchlist" ? "watchlist" : "default";
  const trackedSymbols = viewer.onboarding?.trackedSymbols ?? [];
  const tokenUniverse = buildTokenUniverse(tokens, trackedSymbols, category);
  const selectedSymbolCandidate = (params.symbol ?? tokenUniverse.activeSymbols[0] ?? tokens[0]?.symbol ?? "BTC").toUpperCase();

  const context = await resolveTokenContext([
    selectedSymbolCandidate,
    ...tokenUniverse.activeSymbols.filter((symbol) => symbol !== selectedSymbolCandidate),
    ...tokens.map((token) => token.symbol).filter((symbol) => symbol !== selectedSymbolCandidate),
  ]);

  if (!context) {
    notFound();
  }

  const activeOverview =
    category === "watchlist" && viewer.email
      ? await getWatchtowerOverview(undefined, viewer.email)
      : await getWatchtowerOverview(tokenUniverse.defaultSymbols);

  const overview = activeOverview ?? {
    last_refresh: new Date().toISOString(),
    tracked_assets_count: 0,
    active_signals_count: 0,
    recently_changed_count: 0,
    hero_cards: [],
    assets: [],
  };

  const isTracked = trackedSymbols.includes(context.header.symbol);

  return (
    <Shell
      title="Workspace"
      eyebrow="Private signal terminal"
      description="Search any supported asset, star it into your watchlist, and inspect the live divergence state without leaving the workspace."
      actions={
        <Button asChild variant="ghost">
          <Link href="/account">Open account</Link>
        </Button>
      }
    >
      <section className="grid border border-white/12 md:grid-cols-4">
        {metrics(overview, trackedSymbols).map((item, index, items) => (
          <div
            key={item.label}
            className={`px-5 py-5 ${index < items.length - 1 ? "border-b border-white/12 md:border-b-0 md:border-r" : ""}`}
          >
            <p className="text-[10px] uppercase tracking-[0.28em] text-white/34">{item.label}</p>
            <p className="mt-3 text-2xl text-white">{item.value}</p>
          </div>
        ))}
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-[360px_minmax(0,1fr)]">
        <div className="space-y-6">
          <Card className="border border-white/12 bg-white/[0.02] p-0">
            <div className="border-b border-white/12 px-5 py-4">
              <p className="text-[10px] uppercase tracking-[0.32em] text-white/34">Asset registry</p>
            </div>
            <div className="space-y-5 p-5">
              <form action="/app" className="space-y-3">
                <input type="hidden" name="category" value={category} />
                <label htmlFor="symbol" className="text-[10px] uppercase tracking-[0.24em] text-white/40">
                  Search asset
                </label>
                <div className="flex gap-2">
                  <input
                    id="symbol"
                    name="symbol"
                    list="token-registry"
                    defaultValue={context.header.symbol}
                    className="w-full border border-white/14 bg-transparent px-3 py-3 text-sm text-white outline-none placeholder:text-white/24"
                    placeholder="BTC"
                  />
                  <Button type="submit" variant="secondary">
                    Load
                  </Button>
                </div>
                <datalist id="token-registry">
                  {tokens.map((token) => (
                    <option key={token.id} value={token.symbol}>
                      {token.name}
                    </option>
                  ))}
                </datalist>
              </form>

              <div className="flex gap-2">
                <Button asChild variant={category === "default" ? "default" : "ghost"}>
                  <Link href="/app?category=default">Default</Link>
                </Button>
                <Button asChild variant={category === "watchlist" ? "default" : "ghost"}>
                  <Link href="/app?category=watchlist">Watchlist</Link>
                </Button>
              </div>

              <form action={toggleTrackedAsset}>
                <input type="hidden" name="symbol" value={context.header.symbol} />
                <input type="hidden" name="intent" value={isTracked ? "remove" : "add"} />
                <Button type="submit" className="w-full">
                  {isTracked ? "Remove star" : "Add star"}
                </Button>
              </form>
            </div>
          </Card>

          <Card className="border border-white/12 bg-white/[0.02] p-0">
            <div className="border-b border-white/12 px-5 py-4">
              <p className="text-[10px] uppercase tracking-[0.32em] text-white/34">
                {category === "watchlist" ? "Watchlist assets" : "Default coverage"}
              </p>
            </div>
            <div className="grid">
              {tokenUniverse.visibleTokens.map((token, index) => {
                const active = token.symbol === context.header.symbol;
                const tracked = trackedSymbols.includes(token.symbol);

                return (
                  <Link
                    key={token.id}
                    href={`/app?category=${category}&symbol=${token.symbol}`}
                    className={`flex items-center justify-between px-5 py-4 transition ${
                      index < tokenUniverse.visibleTokens.length - 1 ? "border-b border-white/12" : ""
                    } ${active ? "bg-white/[0.06]" : "hover:bg-white/[0.03]"}`}
                  >
                    <div>
                      <p className="text-sm text-white">{token.symbol}</p>
                      <p className="mt-1 text-[10px] uppercase tracking-[0.2em] text-white/38">{token.name}</p>
                    </div>
                    <span className="text-xs text-white/46">{tracked ? "STARRED" : "LIVE"}</span>
                  </Link>
                );
              })}
            </div>
          </Card>

          <Card className="border border-white/12 bg-white/[0.02]">
            <p className="text-[10px] uppercase tracking-[0.32em] text-white/34">Live board</p>
            <div className="mt-5 space-y-4">
              {overview.assets.map((asset) => (
                <Link
                  key={asset.id}
                  href={`/app?category=${category}&symbol=${asset.symbol}`}
                  className="block border border-white/12 px-4 py-4 transition hover:bg-white/[0.03]"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-lg text-white">{asset.symbol}</p>
                      <p className="mt-1 text-[10px] uppercase tracking-[0.22em] text-white/38">
                        Updated {formatRelativeTime(asset.last_updated)}
                      </p>
                    </div>
                    <span className={`px-2 py-1 text-[10px] uppercase tracking-[0.18em] ${signalTone(asset.signal_type)}`}>
                      {signalLabel(asset.signal_type)}
                    </span>
                  </div>
                  <div className="mt-3 flex items-center justify-between gap-3 text-sm">
                    <span className="text-white">{formatPrice(asset.current_price)}</span>
                    <span className={changeTone(asset.change_24h)}>{formatPercent(asset.change_24h)} 24h</span>
                  </div>
                </Link>
              ))}
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="border border-white/12 bg-white/[0.02] p-0">
            <div className="grid border-b border-white/12 lg:grid-cols-[minmax(0,1.15fr)_340px]">
              <div className="p-5 md:p-6">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-[10px] uppercase tracking-[0.32em] text-white/34">Selected asset</p>
                    <h2 className="display mt-4 text-5xl text-white">{context.header.symbol}</h2>
                    <p className="mt-3 text-xs uppercase tracking-[0.2em] text-white/42">{context.header.name}</p>
                  </div>
                  <Badge variant="muted">{context.header.market_type}</Badge>
                </div>

                <div className="mt-8 grid gap-3 md:grid-cols-4">
                  <div className="border border-white/12 px-4 py-4 md:col-span-2">
                    <p className="text-[10px] uppercase tracking-[0.24em] text-white/34">Price</p>
                    <p className="mt-3 text-3xl text-white">{formatPrice(context.header.current_price)}</p>
                  </div>
                  <div className="border border-white/12 px-4 py-4">
                    <p className="text-[10px] uppercase tracking-[0.24em] text-white/34">1h</p>
                    <p className={`mt-3 text-lg ${changeTone(context.header.change_1h)}`}>
                      {formatPercent(context.header.change_1h)}
                    </p>
                  </div>
                  <div className="border border-white/12 px-4 py-4">
                    <p className="text-[10px] uppercase tracking-[0.24em] text-white/34">24h</p>
                    <p className={`mt-3 text-lg ${changeTone(context.header.change_24h)}`}>
                      {formatPercent(context.header.change_24h)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="border-t border-white/12 p-5 md:p-6 lg:border-l lg:border-t-0">
                <p className="text-[10px] uppercase tracking-[0.32em] text-white/34">Current signal</p>
                <div className="mt-4">
                  <span className={`inline-flex px-2 py-1 text-[10px] uppercase tracking-[0.18em] ${signalTone(context.current_signal_state.signal_type)}`}>
                    {signalLabel(context.current_signal_state.signal_type)}
                  </span>
                </div>
                <p className="mt-5 text-4xl text-white">{Math.round(context.current_signal_state.signal_score)}</p>
                <p className="mt-2 text-xs uppercase tracking-[0.2em] text-white/44">
                  Confidence {Math.round(context.current_signal_state.confidence * 100)}%
                </p>
                <div className="mt-6 space-y-4 text-sm leading-7 text-white/62">
                  <div>
                    <p className="mb-1 text-[10px] uppercase tracking-[0.24em] text-white/34">Why now</p>
                    <p>{context.current_signal_state.why_now}</p>
                  </div>
                  <div>
                    <p className="mb-1 text-[10px] uppercase tracking-[0.24em] text-white/34">Risks</p>
                    <p>{context.current_signal_state.risks.join(" · ")}</p>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          <div className="grid gap-6 xl:grid-cols-[minmax(0,1.15fr)_360px]">
            <Card className="border border-white/12 bg-white/[0.02] p-6">
              <DivergenceChart
                defaultTimeframe={context.divergence_chart.default_timeframe}
                series={context.divergence_chart.series}
              />
            </Card>

            <Card className="border border-white/12 bg-white/[0.02]">
              <p className="text-[10px] uppercase tracking-[0.32em] text-white/34">Social summary</p>
              <div className="mt-5 flex flex-wrap gap-2">
                <Badge variant={context.social_summary.snapshot_incomplete ? "muted" : "accent"}>
                  {context.social_summary.snapshot_incomplete ? "Partial snapshot" : "Live snapshot"}
                </Badge>
                <Badge variant="muted">{context.social_summary.attention_label}</Badge>
              </div>
              <div className="mt-5 space-y-3">
                {summaryPoints(context).map((point) => (
                  <p key={point} className="text-sm leading-7 text-white/62">
                    {point}
                  </p>
                ))}
              </div>
              <div className="mt-5 border-t border-white/12 pt-5 text-xs uppercase tracking-[0.2em] text-white/42">
                <p>{context.social_summary.discussion_type.replaceAll("_", " ")}</p>
                <p className="mt-2">{context.social_summary.signal_hint.replaceAll("_", " ")}</p>
                <p className="mt-2">Novelty {Math.round(context.social_summary.narrative_novelty * 100)}%</p>
              </div>
            </Card>
          </div>

          <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
            <Card className="border border-white/12 bg-white/[0.02]">
              <p className="text-[10px] uppercase tracking-[0.32em] text-white/34">Recent state changes</p>
              <div className="mt-5 space-y-4">
                {context.recent_state_changes.map((item) => (
                  <div key={`${item.timestamp}-${item.title}`} className="border border-white/12 px-4 py-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm text-white">{item.title}</p>
                        <p className="mt-2 text-sm leading-7 text-white/56">{item.detail}</p>
                      </div>
                      <RecentStateTone signalType={item.signal_type} />
                    </div>
                    <p className="mt-3 text-[10px] uppercase tracking-[0.24em] text-white/34">
                      {formatRelativeTime(item.timestamp)}
                    </p>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="border border-white/12 bg-white/[0.02]">
              <p className="text-[10px] uppercase tracking-[0.32em] text-white/34">Signal archive</p>
              {context.recent_signal_history.length === 0 ? (
                <p className="mt-5 text-sm leading-7 text-white/56">No archived signal events for this asset yet.</p>
              ) : (
                <div className="mt-5 space-y-4">
                  {context.recent_signal_history.map((signal) => (
                    <div key={signal.id} className="border border-white/12 px-4 py-4">
                      <div className="flex items-center justify-between gap-3">
                        <RecentStateTone signalType={signal.signal_type} />
                        <p className="text-sm text-white">{Math.round(signal.signal_score)}</p>
                      </div>
                      <p className="mt-3 text-sm leading-7 text-white/56">{signal.explanation.why_now}</p>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        </div>
      </section>
    </Shell>
  );
}
