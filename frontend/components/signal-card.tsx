import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { Signal } from "@/lib/types";

function labelForType(type: Signal["signal_type"]) {
  switch (type) {
    case "hidden_accumulation":
      return "Hidden Accumulation";
    case "narrative_ignition":
      return "Narrative Ignition";
    case "retail_trap":
      return "Retail Trap";
    default:
      return "Neutral";
  }
}

export function SignalCard({ signal }: { signal: Signal }) {
  return (
    <Card className="flex h-full flex-col justify-between">
      <div className="space-y-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-2xl font-black">{signal.token_symbol}</p>
            <p className="text-sm text-foreground/60">{labelForType(signal.signal_type)}</p>
          </div>
          <Badge variant={signal.signal_score >= 80 ? "accent" : "default"}>
            {signal.signal_score}/100
          </Badge>
        </div>
        <div className="grid gap-3 text-sm text-foreground/78">
          <div>
            <p className="mb-1 font-semibold text-foreground">Why now</p>
            <p>{signal.explanation.why_now}</p>
          </div>
          <div>
            <p className="mb-1 font-semibold text-foreground">Risks</p>
            <p>{signal.explanation.risks.join(" · ")}</p>
          </div>
          <div>
            <p className="mb-1 font-semibold text-foreground">Suggested action</p>
            <p>{signal.explanation.suggested_action}</p>
          </div>
          <div>
            <p className="mb-1 font-semibold text-foreground">Invalidation</p>
            <p>{signal.explanation.invalidation_conditions.join(" · ")}</p>
          </div>
        </div>
      </div>
      <div className="mt-5 flex items-center justify-between">
        <span className="text-xs uppercase tracking-[0.18em] text-foreground/45">
          Confidence {Math.round(signal.confidence * 100)}%
        </span>
        <Link href={`/signals/${signal.id}`} className="text-sm font-semibold text-primary">
          Open signal
        </Link>
      </div>
    </Card>
  );
}

