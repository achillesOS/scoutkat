import Link from "next/link";

import { Card } from "@/components/ui/card";
import type { WatchtowerToken } from "@/lib/types";
import { formatPercent, formatPrice, signalLabel, signalTone } from "@/lib/watchtower";

function changeTone(value: number) {
  return value >= 0 ? "text-primary" : "text-rose-700";
}

export function HeroSignalCard({
  title,
  token,
}: {
  title: string;
  token: WatchtowerToken;
}) {
  return (
    <Card className="flex h-full flex-col justify-between rounded-[1.75rem] border-primary/10 bg-white/80 p-5">
      <div className="space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-foreground/45">
              {title}
            </p>
            <div className="mt-3 flex items-end gap-3">
              <p className="text-3xl font-black tracking-tight">{token.symbol}</p>
              <span
                className={`rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] ${signalTone(token.signal_type)}`}
              >
                {signalLabel(token.signal_type)}
              </span>
            </div>
          </div>
          <div className="text-right">
            <p className="text-[11px] uppercase tracking-[0.22em] text-foreground/40">Score</p>
            <p className="mt-2 text-2xl font-black">{token.signal_score ?? "—"}</p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="rounded-2xl bg-muted/65 px-4 py-3">
            <p className="text-[11px] uppercase tracking-[0.2em] text-foreground/42">Confidence</p>
            <p className="mt-2 text-lg font-bold">
              {token.confidence !== null ? `${Math.round(token.confidence * 100)}%` : "—"}
            </p>
          </div>
          <div className="rounded-2xl bg-muted/65 px-4 py-3">
            <p className="text-[11px] uppercase tracking-[0.2em] text-foreground/42">Price</p>
            <p className="mt-2 text-lg font-bold">{formatPrice(token.current_price)}</p>
          </div>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <span className={`font-semibold ${changeTone(token.change_24h)}`}>
            {formatPercent(token.change_24h)} 24h
          </span>
          <span className="text-foreground/45">why now</span>
        </div>
        <p className="text-sm leading-6 text-foreground/72">{token.why_now}</p>
      </div>
      <div className="mt-5">
        <Link href={`/tokens/${token.symbol}`} className="text-sm font-semibold text-primary">
          Open token
        </Link>
      </div>
    </Card>
  );
}
