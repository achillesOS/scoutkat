import { Shell } from "@/components/shell";
import { Card } from "@/components/ui/card";

const pillars = [
  {
    title: "Attention",
    body: "Tracks whether X attention is early, broad, retail-heavy, or genuinely novel.",
  },
  {
    title: "Structure",
    body: "Checks if Hyperliquid price, volume, trade flow, and absorption confirm the social move.",
  },
  {
    title: "Positioning",
    body: "Measures whether perp crowding is still healthy or already overheating.",
  },
];

export default function MyEdgePage() {
  return (
    <Shell title="My Edge" eyebrow="Signal framework">
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
