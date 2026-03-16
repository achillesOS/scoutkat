import { notFound } from "next/navigation";

import { toggleTrackedAsset } from "@/app/actions";
import { DivergenceChart } from "@/components/divergence-chart";
import { Shell } from "@/components/shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { getViewerState } from "@/lib/auth";
import { getTokenContext } from "@/lib/api";
import { formatPercent, formatPrice, formatRelativeTime, signalLabel, signalTone } from "@/lib/watchtower";

function changeTone(value: number) {
  if (value > 0) {
    return "text-primary";
  }
  if (value < 0) {
    return "text-rose-700";
  }
  return "text-foreground/60";
}

export default async function TokenPage({
  params,
}: {
  params: Promise<{ symbol: string }>;
}) {
  const { symbol } = await params;
  const [context, viewer] = await Promise.all([
    getTokenContext(symbol.toUpperCase()),
    getViewerState(),
  ]);

  if (!context) {
    notFound();
  }

  const isTracked = viewer.onboarding?.trackedSymbols.includes(context.header.symbol) ?? false;

  return (
    <Shell
      title={context.header.symbol}
      eyebrow={context.header.name}
      description="Scoutkat compares X attention, Hyperliquid structure, and perp positioning to explain the token state right now."
    >
      <section className="grid gap-4 xl:grid-cols-[minmax(0,1.4fr)_minmax(320px,0.8fr)]">
        <Card className="rounded-[1.75rem] p-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="flex items-center gap-3">
                <p className="text-4xl font-black tracking-tight">{context.header.symbol}</p>
                <Badge variant="muted">{context.header.market_type}</Badge>
              </div>
              <p className="mt-2 text-sm text-foreground/60">{context.header.name}</p>
            </div>
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-foreground/45">
                Last updated
              </p>
              <p className="mt-2 text-sm font-semibold text-foreground/68">
                {formatRelativeTime(context.header.last_updated)}
              </p>
            </div>
          </div>

          <div className="mt-6 grid gap-3 md:grid-cols-4">
            <div className="rounded-2xl bg-muted/65 px-4 py-3 md:col-span-2">
              <p className="text-[11px] uppercase tracking-[0.18em] text-foreground/42">Current price</p>
              <p className="mt-2 text-3xl font-black">{formatPrice(context.header.current_price)}</p>
            </div>
            <div className="rounded-2xl bg-muted/65 px-4 py-3">
              <p className="text-[11px] uppercase tracking-[0.18em] text-foreground/42">1h</p>
              <p className={`mt-2 text-lg font-bold ${changeTone(context.header.change_1h)}`}>
                {formatPercent(context.header.change_1h)}
              </p>
            </div>
            <div className="rounded-2xl bg-muted/65 px-4 py-3">
              <p className="text-[11px] uppercase tracking-[0.18em] text-foreground/42">4h</p>
              <p className={`mt-2 text-lg font-bold ${changeTone(context.header.change_4h)}`}>
                {formatPercent(context.header.change_4h)}
              </p>
            </div>
          </div>

          <div className="mt-3 rounded-2xl bg-muted/65 px-4 py-3">
            <p className="text-[11px] uppercase tracking-[0.18em] text-foreground/42">24h</p>
            <p className={`mt-2 text-lg font-bold ${changeTone(context.header.change_24h)}`}>
              {formatPercent(context.header.change_24h)}
            </p>
          </div>
        </Card>

        <Card className="rounded-[1.75rem] p-6">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-foreground/45">
                Current state
              </p>
              <div className="mt-3">
                <span
                  className={`rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] ${signalTone(context.current_signal_state.signal_type)}`}
                >
                  {signalLabel(context.current_signal_state.signal_type)}
                </span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-[11px] uppercase tracking-[0.18em] text-foreground/42">Score</p>
              <p className="mt-2 text-2xl font-black">{context.current_signal_state.signal_score}</p>
              <p className="text-sm text-foreground/60">
                Confidence {Math.round(context.current_signal_state.confidence * 100)}%
              </p>
            </div>
          </div>
          <div className="mt-5 space-y-4 text-sm text-foreground/72">
            <div>
              <p className="mb-1 font-semibold text-foreground">Why now</p>
              <p>{context.current_signal_state.why_now}</p>
            </div>
            <div>
              <p className="mb-1 font-semibold text-foreground">Risks</p>
              <p>{context.current_signal_state.risks.join(" · ")}</p>
            </div>
            <div>
              <p className="mb-1 font-semibold text-foreground">Invalidation</p>
              <p>{context.current_signal_state.invalidation.join(" · ")}</p>
            </div>
          </div>
          <div className="mt-5">
            {viewer.isAuthenticated && viewer.onboarding ? (
              <form action={toggleTrackedAsset}>
                <input type="hidden" name="symbol" value={context.header.symbol} />
                <input type="hidden" name="intent" value={isTracked ? "remove" : "add"} />
                <Button type="submit" className="w-full">
                  {isTracked ? "Remove from watchlist" : "Add to watchlist"}
                </Button>
              </form>
            ) : (
              <Button asChild className="w-full">
                <a href="/sign-in">Sign in to track this asset</a>
              </Button>
            )}
          </div>
        </Card>
      </section>

      <section className="mt-8 grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <Card className="rounded-[1.75rem] p-6">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-foreground/45">
                X attention
              </p>
              <p className="mt-2 text-2xl font-black tracking-tight">{context.social_summary.attention_label}</p>
            </div>
            <Badge variant={context.social_summary.snapshot_incomplete ? "muted" : "accent"}>
              {context.social_summary.snapshot_incomplete ? "Partial" : "Live summary"}
            </Badge>
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <div className="rounded-2xl bg-muted/65 px-4 py-3">
              <p className="text-[11px] uppercase tracking-[0.18em] text-foreground/42">Discussion</p>
              <p className="mt-2 text-sm font-bold capitalize">
                {context.social_summary.discussion_type.replaceAll("_", " ")}
              </p>
            </div>
            <div className="rounded-2xl bg-muted/65 px-4 py-3">
              <p className="text-[11px] uppercase tracking-[0.18em] text-foreground/42">Signal hint</p>
              <p className="mt-2 text-sm font-bold capitalize">
                {context.social_summary.signal_hint.replaceAll("_", " ")}
              </p>
            </div>
            <div className="rounded-2xl bg-muted/65 px-4 py-3">
              <p className="text-[11px] uppercase tracking-[0.18em] text-foreground/42">LLM confidence</p>
              <p className="mt-2 text-sm font-bold">{Math.round(context.social_summary.confidence * 100)}%</p>
            </div>
          </div>
          <div className="mt-5 grid gap-4 md:grid-cols-[minmax(0,1fr)_280px]">
            <div>
              <p className="mb-2 text-sm font-semibold uppercase tracking-[0.2em] text-foreground/45">
                Social summary
              </p>
              <div className="space-y-2">
                {context.social_summary.summary_points.map((point) => (
                  <p key={point} className="text-sm leading-7 text-foreground/72">
                    {point}
                  </p>
                ))}
              </div>
            </div>
            <div>
              <p className="mb-2 text-sm font-semibold uppercase tracking-[0.2em] text-foreground/45">
                Top narratives
              </p>
              <div className="flex flex-wrap gap-2">
                {context.social_summary.top_narratives.length === 0 ? (
                  <span className="text-sm text-foreground/58">No strong narratives tagged yet.</span>
                ) : (
                  context.social_summary.top_narratives.map((item) => (
                    <Badge key={item} variant="muted">
                      {item}
                    </Badge>
                  ))
                )}
              </div>
              <div className="mt-4 space-y-2 text-sm text-foreground/68">
                <p>Expert presence {Math.round(context.social_summary.expert_presence * 100)}%</p>
                <p>Retail breadth {Math.round(context.social_summary.retail_breadth * 100)}%</p>
                <p>Narrative novelty {Math.round(context.social_summary.narrative_novelty * 100)}%</p>
              </div>
            </div>
          </div>
        </Card>
      </section>

      <section className="mt-8">
        <Card className="rounded-[1.75rem] p-6">
          <DivergenceChart
            defaultTimeframe={context.divergence_chart.default_timeframe}
            series={context.divergence_chart.series}
          />
        </Card>
      </section>

      <section className="mt-8 grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <Card className="rounded-[1.75rem] p-6">
          <p className="text-xl font-black tracking-tight">Recent state changes</p>
          <div className="mt-5 grid gap-4">
            {context.recent_state_changes.map((item) => (
              <div key={`${item.timestamp}-${item.title}`} className="rounded-2xl border border-border/70 p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-bold">{item.title}</p>
                  <span
                    className={`rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] ${signalTone(item.signal_type)}`}
                  >
                    {signalLabel(item.signal_type)}
                  </span>
                </div>
                <p className="mt-2 text-sm text-foreground/68">{item.detail}</p>
                <p className="mt-3 text-xs uppercase tracking-[0.18em] text-foreground/42">
                  {formatRelativeTime(item.timestamp)}
                </p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="rounded-[1.75rem] p-6">
          <p className="text-xl font-black tracking-tight">Recent signal history</p>
          {context.recent_signal_history.length === 0 ? (
            <p className="mt-4 text-sm text-foreground/68">
              No recent signal events for this token yet.
            </p>
          ) : (
            <div className="mt-4 grid gap-3">
              {context.recent_signal_history.map((signal) => (
                <div key={signal.id} className="rounded-2xl border border-border/70 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <span
                      className={`rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] ${signalTone(signal.signal_type)}`}
                    >
                      {signalLabel(signal.signal_type)}
                    </span>
                    <p className="text-sm font-semibold">{signal.signal_score}/100</p>
                  </div>
                  <p className="mt-3 text-sm text-foreground/68">{signal.explanation.why_now}</p>
                </div>
              ))}
            </div>
          )}
        </Card>
      </section>
    </Shell>
  );
}
