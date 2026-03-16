import type { SignalType } from "@/lib/types";

export function signalLabel(signalType: SignalType) {
  switch (signalType) {
    case "hidden_accumulation":
      return "Hidden Accumulation";
    case "narrative_ignition":
      return "Narrative Ignition";
    case "retail_trap":
      return "Retail Trap";
    default:
      return "No active signal";
  }
}

export function signalTone(signalType: SignalType) {
  switch (signalType) {
    case "hidden_accumulation":
      return "bg-primary/12 text-primary ring-1 ring-primary/20";
    case "narrative_ignition":
      return "bg-amber-500/14 text-amber-900 ring-1 ring-amber-600/20";
    case "retail_trap":
      return "bg-rose-500/12 text-rose-800 ring-1 ring-rose-600/20";
    default:
      return "bg-muted text-foreground/70 ring-1 ring-border/70";
  }
}

export function formatPrice(value: number) {
  const digits = value >= 1000 ? 0 : value >= 100 ? 2 : value >= 1 ? 2 : 4;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  }).format(value);
}

export function formatPercent(value: number) {
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${value.toFixed(1)}%`;
}

export function formatRelativeTime(timestamp: string) {
  const diffMs = Date.now() - new Date(timestamp).getTime();
  const minutes = Math.max(1, Math.round(diffMs / 60000));

  if (minutes < 60) {
    return `${minutes}m ago`;
  }

  const hours = Math.round(minutes / 60);
  return `${hours}h ago`;
}
