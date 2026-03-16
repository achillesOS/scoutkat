import { SignalCard } from "@/components/signal-card";
import { Shell } from "@/components/shell";
import { getSignals } from "@/lib/api";

export default async function SignalsPage() {
  const signals = await getSignals();

  return (
    <Shell title="Signals" eyebrow="Live signal cards">
      <section className="grid gap-4 lg:grid-cols-2">
        {signals.length === 0 ? (
          <div className="rounded-2xl border border-border/70 bg-white/70 p-6 text-sm text-foreground/72">
            No signals yet. Run another ingestion cycle or widen tracked coverage to let the first live signals appear.
          </div>
        ) : null}
        {signals.map((signal) => (
          <SignalCard key={signal.id} signal={signal} />
        ))}
      </section>
    </Shell>
  );
}
