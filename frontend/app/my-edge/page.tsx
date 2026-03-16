import Link from "next/link";

import { Shell } from "@/components/shell";
import { Card } from "@/components/ui/card";

const pillars = [
  {
    title: "Attention",
    body: "Scoutkat estimates how strong X discussion is, how fast it is accelerating, and whether the flow looks like broad retail hype or tighter expert attention.",
  },
  {
    title: "Structure",
    body: "Scoutkat checks whether Hyperliquid price structure is actually confirming the narrative through returns, efficiency, and order-book proxies.",
  },
  {
    title: "Positioning",
    body: "Scoutkat tracks funding, open interest, and crowding pressure to avoid buying narratives that are already over-owned.",
  },
];

export default function MyEdgePage() {
  return (
    <Shell
      title="My Edge"
      eyebrow="How Scoutkat works"
      description="Scoutkat is built to find divergence, not just momentum. It compares social attention with real market structure and perp positioning."
      actions={
        <Link href="/signals" className="rounded-full border border-border/70 px-4 py-2 text-sm font-medium text-foreground/80 transition hover:bg-white">
          Browse live signals
        </Link>
      }
    >
      <section className="grid gap-4 md:grid-cols-3">
        {pillars.map((pillar) => (
          <Card key={pillar.title}>
            <p className="text-xl font-black">{pillar.title}</p>
            <p className="mt-3 text-sm leading-7 text-foreground/72">{pillar.body}</p>
          </Card>
        ))}
      </section>
    </Shell>
  );
}
