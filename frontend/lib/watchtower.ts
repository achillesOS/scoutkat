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
      return "border border-white/16 bg-white/[0.05] text-white";
    case "narrative_ignition":
      return "border border-amber-200/22 bg-amber-200/10 text-amber-100";
    case "retail_trap":
      return "border border-rose-200/18 bg-rose-200/10 text-rose-100";
    default:
      return "border border-white/12 bg-transparent text-white/60";
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
