import { SignalCard } from "@/components/signal-card";
import { Shell } from "@/components/shell";
import { getSignals } from "@/lib/api";

export default async function SignalsPage() {
  const signals = await getSignals();

  return (
    <Shell
      title="Signals"
      eyebrow="Live board"
      description="Scoutkat compares X attention, Hyperliquid structure, and positioning to surface active divergence states."
    >
      <section className="grid gap-4 lg:grid-cols-2">
        {signals.map((signal) => (
          <SignalCard key={signal.id} signal={signal} />
        ))}
      </section>
    </Shell>
  );
}
