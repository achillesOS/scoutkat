import Link from "next/link";
import { redirect } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { getViewerState } from "@/lib/auth";
import { getTokenContext, getWatchtowerOverview } from "@/lib/api";
import type { SignalType, TokenContext, WatchtowerToken } from "@/lib/types";
import { formatPercent, formatPrice, signalLabel, signalTone } from "@/lib/watchtower";

type PublicSample = {
  symbol: string;
  name: string;
  price: number;
  change1h: number;
  change24h: number;
  signalType: SignalType;
  performanceSummary: string;
};

function buildPerformanceSummary(context: TokenContext | null, asset: WatchtowerToken | null) {
  if (context && context.recent_signal_history.length > 0) {
    return `${context.recent_signal_history.length} live signal events archived`;
  }
  if (context && context.recent_state_changes.length > 0) {
    return `${context.recent_state_changes.length} state transitions logged`;
  }
  if (asset) {
    return `Current state confidence ${Math.round(asset.confidence * 100)}%`;
  }
  return "Live record building";
}

async function loadPublicSample(symbol: string): Promise<PublicSample | null> {
  const [context, overview] = await Promise.all([
    getTokenContext(symbol),
    getWatchtowerOverview([symbol]),
  ]);

  const asset = overview?.assets.find((item) => item.symbol === symbol) ?? null;

  if (context) {
    return {
      symbol: context.header.symbol,
      name: context.header.name,
      price: context.header.current_price,
      change1h: context.header.change_1h,
      change24h: context.header.change_24h,
      signalType: context.current_signal_state.signal_type,
      performanceSummary: buildPerformanceSummary(context, asset),
    };
  }

  if (asset) {
    return {
      symbol: asset.symbol,
      name: asset.name,
      price: asset.current_price,
      change1h: asset.change_1h,
      change24h: asset.change_24h,
      signalType: asset.signal_type,
      performanceSummary: buildPerformanceSummary(null, asset),
    };
  }

  return null;
}

function changeTone(value: number) {
  if (value > 0) {
    return "text-emerald-300";
  }
  if (value < 0) {
    return "text-rose-300";
  }
  return "text-white/60";
}

const signalModules = [
  {
    title: "Hidden Accumulation",
    body: "Structure leads attention. Price and positioning stay cleaner than the crowd expects.",
  },
  {
    title: "Narrative Ignition",
    body: "Attention and structure accelerate together. A dormant story starts to convert into movement.",
  },
  {
    title: "Retail Trap",
    body: "Attention runs hot while positioning overheats. The setup looks crowded before it looks safe.",
  },
];

export default async function HomePage() {
  const viewer = await getViewerState();

  if (viewer.isAuthenticated && viewer.onboarding) {
    redirect("/app");
  }

  const samples = (await Promise.all([loadPublicSample("BTC"), loadPublicSample("ETH")])).filter(
    (sample): sample is PublicSample => sample !== null,
  );

  return (
    <main className="grain min-h-screen bg-background px-4 py-4 md:px-6">
      <div className="mx-auto max-w-[1500px]">
        <header className="grid border border-white/12 md:grid-cols-[380px_minmax(0,1fr)_220px]">
          <div className="flex min-h-[72px] items-center border-b border-white/12 px-5 md:border-b-0 md:border-r">
            <div>
              <p className="display text-[2rem] font-semibold leading-none text-white">Scoutkat</p>
              <p className="mt-2 text-[10px] uppercase tracking-[0.34em] text-white/42">Signal system v1</p>
            </div>
          </div>
          <div className="flex min-h-[72px] items-center justify-center border-b border-white/12 px-5 md:border-b-0">
            <p className="text-[10px] uppercase tracking-[0.34em] text-white/42">
              Public preview / BTC + ETH only
            </p>
          </div>
          <div className="flex min-h-[72px] items-center justify-end px-5">
            <Button asChild variant="ghost">
              <Link href="/sign-in">Login</Link>
            </Button>
          </div>
        </header>

        <section className="grid border-x border-b border-white/12 lg:grid-cols-[minmax(0,1.15fr)_minmax(420px,0.85fr)]">
          <div className="flex flex-col justify-between p-6 md:p-10">
            <div>
              <p className="text-[10px] uppercase tracking-[0.34em] text-white/35">Attention / Structure / Positioning</p>
              <h1 className="display mt-8 max-w-4xl text-5xl leading-[0.94] text-white md:text-7xl">
                Scoutkat finds divergence before it becomes obvious.
              </h1>
              <p className="mt-8 max-w-xl text-sm leading-8 text-white/62">
                Read two public sample assets for free. Start a 7-day Pro trial to unlock the full workspace,
                custom watchlists, Telegram alerts, and agent access.
              </p>
            </div>

            <div className="mt-12 flex flex-wrap gap-3">
              <Button asChild>
                <Link href="/sign-in">Start 7-day Pro trial</Link>
              </Button>
              <Button asChild variant="secondary">
                <Link href="/sign-in">Unlock more assets</Link>
              </Button>
            </div>
          </div>

          <div className="halftone-panel min-h-[420px] border-t border-white/12 md:min-h-[520px] lg:border-l lg:border-t-0" />
        </section>

        <section className="border-x border-b border-white/12 px-5 py-10 md:px-8">
          <div className="mb-6 flex items-end justify-between gap-4">
            <div>
              <p className="text-[10px] uppercase tracking-[0.34em] text-white/35">Free sample assets</p>
              <h2 className="display mt-3 text-3xl text-white md:text-4xl">Read the system on BTC and ETH.</h2>
            </div>
            <p className="max-w-md text-xs uppercase tracking-[0.2em] text-white/40">
              Public cards stay concise on purpose. Full detail lives inside the private workspace.
            </p>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            {samples.map((sample) => (
              <Card key={sample.symbol} className="border border-white/12 bg-white/[0.02] p-0">
                <div className="grid grid-cols-[1.2fr_1fr_1fr_1fr] border-b border-white/12 text-[10px] uppercase tracking-[0.28em] text-white/34">
                  <div className="px-5 py-4">Asset</div>
                  <div className="px-5 py-4">Price</div>
                  <div className="px-5 py-4">Change</div>
                  <div className="px-5 py-4">Signal</div>
                </div>
                <div className="grid grid-cols-[1.2fr_1fr_1fr_1fr]">
                  <div className="border-r border-white/12 px-5 py-5">
                    <p className="display text-3xl text-white">{sample.symbol}</p>
                    <p className="mt-2 text-xs uppercase tracking-[0.22em] text-white/42">{sample.name}</p>
                  </div>
                  <div className="border-r border-white/12 px-5 py-5">
                    <p className="text-[10px] uppercase tracking-[0.24em] text-white/34">Spot</p>
                    <p className="mt-3 text-xl text-white">{formatPrice(sample.price)}</p>
                  </div>
                  <div className="border-r border-white/12 px-5 py-5">
                    <p className={`text-sm ${changeTone(sample.change1h)}`}>{formatPercent(sample.change1h)} 1h</p>
                    <p className={`mt-2 text-sm ${changeTone(sample.change24h)}`}>{formatPercent(sample.change24h)} 24h</p>
                  </div>
                  <div className="px-5 py-5">
                    <span className={`inline-flex px-2 py-1 text-[10px] uppercase tracking-[0.18em] ${signalTone(sample.signalType)}`}>
                      {signalLabel(sample.signalType)}
                    </span>
                    <p className="mt-4 text-xs leading-6 text-white/56">{sample.performanceSummary}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </section>

        <section className="border-x border-b border-white/12 px-5 py-10 md:px-8">
          <p className="text-[10px] uppercase tracking-[0.34em] text-white/35">Signal modules</p>
          <div className="mt-4 grid border border-white/12 md:grid-cols-3">
            {signalModules.map((module, index) => (
              <div
                key={module.title}
                className={`p-5 ${index < signalModules.length - 1 ? "border-b border-white/12 md:border-b-0 md:border-r" : ""}`}
              >
                <p className="display text-2xl text-white">{module.title}</p>
                <p className="mt-4 text-sm leading-7 text-white/58">{module.body}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
