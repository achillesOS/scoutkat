import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { WatchtowerToken } from "@/lib/types";
import {
  formatPercent,
  formatPrice,
  formatRelativeTime,
  signalLabel,
  signalTone,
} from "@/lib/watchtower";

function changeTone(value: number) {
  if (value > 0) {
    return "text-primary";
  }

  if (value < 0) {
    return "text-rose-700";
  }

  return "text-foreground/60";
}

export function WatchlistTokenCard({ token }: { token: WatchtowerToken }) {
  return (
    <Card className="flex h-full flex-col justify-between rounded-[1.5rem] p-5">
      <div className="space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <p className="text-2xl font-black tracking-tight">{token.symbol}</p>
              <span className="rounded-full border border-border/70 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-foreground/55">
                {token.market_type}
              </span>
            </div>
            <p className="mt-1 text-sm text-foreground/62">{token.name}</p>
          </div>
          <span
            className={`rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] ${signalTone(token.signal_type)}`}
          >
            {signalLabel(token.signal_type)}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-2xl bg-muted/65 px-4 py-3">
            <p className="text-[11px] uppercase tracking-[0.2em] text-foreground/42">Current price</p>
            <p className="mt-2 text-lg font-bold">{formatPrice(token.current_price)}</p>
          </div>
          <div className="rounded-2xl bg-muted/65 px-4 py-3">
            <p className="text-[11px] uppercase tracking-[0.2em] text-foreground/42">Signal state</p>
            <p className="mt-2 text-lg font-bold">
              {token.signal_score !== null ? `${token.signal_score}/100` : "Watching"}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm">
          <span className={changeTone(token.change_1h)}>{formatPercent(token.change_1h)} 1h</span>
          <span className={changeTone(token.change_24h)}>{formatPercent(token.change_24h)} 24h</span>
          <span className="text-foreground/52">Updated {formatRelativeTime(token.last_updated)}</span>
        </div>
      </div>

      <div className="mt-5">
        <Button asChild>
          <Link href={`/tokens/${token.symbol}`}>Open token</Link>
        </Button>
      </div>
    </Card>
  );
}
