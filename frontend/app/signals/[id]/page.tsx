import { notFound } from "next/navigation";

import { Shell } from "@/components/shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { getSignal } from "@/lib/api";

export default async function SignalDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const signal = await getSignal(id);
  if (!signal) {
    notFound();
  }

  return (
    <Shell title={`${signal.token_symbol} Signal`} eyebrow="Signal detail">
      <Card className="space-y-6">
        <div className="flex flex-wrap items-center gap-3">
          <Badge>{signal.signal_type.replaceAll("_", " ")}</Badge>
          <Badge variant="accent">Score {signal.signal_score}</Badge>
          <Badge variant="muted">Confidence {Math.round(signal.confidence * 100)}%</Badge>
        </div>
        <div className="grid gap-5 md:grid-cols-2">
          <div>
            <p className="mb-2 text-sm font-semibold uppercase tracking-[0.2em] text-foreground/45">
              Why now
            </p>
            <p className="text-base leading-7">{signal.explanation.why_now}</p>
          </div>
          <div>
            <p className="mb-2 text-sm font-semibold uppercase tracking-[0.2em] text-foreground/45">
              Suggested action
            </p>
            <p className="text-base leading-7">{signal.explanation.suggested_action}</p>
          </div>
          <div>
            <p className="mb-2 text-sm font-semibold uppercase tracking-[0.2em] text-foreground/45">
              Risks
            </p>
            <div className="space-y-2">
              {signal.explanation.risks.map((risk) => (
                <p key={risk} className="text-base leading-7">
                  {risk}
                </p>
              ))}
            </div>
          </div>
          <div>
            <p className="mb-2 text-sm font-semibold uppercase tracking-[0.2em] text-foreground/45">
              Invalidation
            </p>
            <div className="space-y-2">
              {signal.explanation.invalidation_conditions.map((condition) => (
                <p key={condition} className="text-base leading-7">
                  {condition}
                </p>
              ))}
            </div>
          </div>
        </div>
      </Card>
    </Shell>
  );
}

