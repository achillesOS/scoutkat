"use client";

import { useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { DivergencePoint, DivergenceTimeframe } from "@/lib/types";

const timeframeOptions: DivergenceTimeframe[] = ["24h", "72h", "7d"];

export function DivergenceChart({
  defaultTimeframe,
  series,
}: {
  defaultTimeframe: DivergenceTimeframe;
  series: Record<DivergenceTimeframe, DivergencePoint[]>;
}) {
  const [timeframe, setTimeframe] = useState<DivergenceTimeframe>(defaultTimeframe);
  const activeSeries = series[timeframe];

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xl font-black tracking-tight">Signal Divergence</p>
          <p className="mt-1 text-sm text-foreground/62">
            Scoutkat compares X attention, Hyperliquid structure, and perp positioning in one view.
          </p>
        </div>
        <div className="flex gap-2">
          {timeframeOptions.map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => setTimeframe(option)}
              className={`rounded-full px-3 py-2 text-sm font-semibold transition ${
                option === timeframe
                  ? "bg-primary text-white"
                  : "border border-border/70 bg-white text-foreground/70 hover:bg-muted"
              }`}
            >
              {option}
            </button>
          ))}
        </div>
      </div>

      <div className="h-[320px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={activeSeries} margin={{ top: 10, right: 10, left: -12, bottom: 0 }}>
            <CartesianGrid stroke="rgba(78, 77, 65, 0.12)" strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              stroke="rgba(30, 54, 57, 0.5)"
              tickFormatter={(value: string) =>
                new Date(value).toLocaleString("en-US", {
                  month: "short",
                  day: "numeric",
                  hour: "numeric",
                })
              }
              minTickGap={36}
            />
            <YAxis domain={[0, 100]} stroke="rgba(30, 54, 57, 0.5)" />
            <Tooltip
              contentStyle={{
                borderRadius: 16,
                border: "1px solid rgba(78,77,65,0.14)",
                backgroundColor: "rgba(255,255,255,0.96)",
              }}
              labelFormatter={(value) =>
                new Date(String(value)).toLocaleString("en-US", {
                  month: "short",
                  day: "numeric",
                  hour: "numeric",
                  minute: "2-digit",
                })
              }
            />
            <Line
              type="monotone"
              dataKey="attention_score"
              stroke="#d97706"
              strokeWidth={3}
              dot={false}
              name="Attention Score"
            />
            <Line
              type="monotone"
              dataKey="structure_score"
              stroke="#0f766e"
              strokeWidth={3}
              dot={false}
              name="Structure Score"
            />
            <Line
              type="monotone"
              dataKey="positioning_score"
              stroke="#dc2626"
              strokeWidth={3}
              dot={false}
              name="Positioning Score"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
