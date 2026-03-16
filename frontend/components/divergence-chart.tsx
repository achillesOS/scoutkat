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
          <p className="display text-3xl text-white">Signal divergence</p>
          <p className="mt-2 text-sm text-white/56">
            A single view across attention, structure, and positioning.
          </p>
        </div>
        <div className="flex gap-2">
          {timeframeOptions.map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => setTimeframe(option)}
              className={`border px-3 py-2 text-xs uppercase tracking-[0.2em] transition ${
                option === timeframe
                  ? "border-white bg-white text-black"
                  : "border-white/12 bg-transparent text-white/60 hover:bg-white/[0.04] hover:text-white"
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
            <CartesianGrid stroke="rgba(255, 255, 255, 0.09)" strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              stroke="rgba(255, 255, 255, 0.4)"
              tickFormatter={(value: string) =>
                new Date(value).toLocaleString("en-US", {
                  month: "short",
                  day: "numeric",
                  hour: "numeric",
                })
              }
              minTickGap={36}
            />
            <YAxis domain={[0, 100]} stroke="rgba(255, 255, 255, 0.4)" />
            <Tooltip
              contentStyle={{
                borderRadius: 0,
                border: "1px solid rgba(255,255,255,0.14)",
                backgroundColor: "rgba(8,8,8,0.96)",
                color: "white",
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
              stroke="#f1dca7"
              strokeWidth={2.5}
              dot={false}
              name="Attention Score"
            />
            <Line
              type="monotone"
              dataKey="structure_score"
              stroke="#ffffff"
              strokeWidth={2.5}
              dot={false}
              name="Structure Score"
            />
            <Line
              type="monotone"
              dataKey="positioning_score"
              stroke="#ff8d8d"
              strokeWidth={2.5}
              dot={false}
              name="Positioning Score"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
