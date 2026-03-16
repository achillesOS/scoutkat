import { Card } from "@/components/ui/card";
import { formatRelativeTime } from "@/lib/watchtower";

export function StatusBar({
  lastRefresh,
  monitoredAssets,
  activeSignals,
  recentlyChanged,
}: {
  lastRefresh: string;
  monitoredAssets: number;
  activeSignals: number;
  recentlyChanged: number;
}) {
  const items = [
    { label: "Last refresh", value: formatRelativeTime(lastRefresh) },
    { label: "Monitored assets", value: monitoredAssets.toString() },
    { label: "Active signals", value: activeSignals.toString() },
    { label: "Recently changed", value: recentlyChanged.toString() },
  ];

  return (
    <Card className="grid gap-4 rounded-[1.75rem] border-primary/10 bg-white/75 p-4 md:grid-cols-4 md:gap-0 md:p-0">
      {items.map((item, index) => (
        <div
          key={item.label}
          className={`px-5 py-4 ${index < items.length - 1 ? "md:border-r md:border-border/60" : ""}`}
        >
          <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-foreground/45">
            {item.label}
          </p>
          <p className="mt-2 text-2xl font-black tracking-tight">{item.value}</p>
        </div>
      ))}
    </Card>
  );
}
